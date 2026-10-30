import asyncio, hmac, html, io, ipaddress, json, logging, logging.handlers, mimetypes, traceback, re, secrets, shutil, urllib.parse, os, random, socket, subprocess, sys, importlib, threading, time, webbrowser

if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")
FROZEN = getattr(sys, "frozen", False)

def need(mod, pkg):
    if FROZEN: return
    try:
        importlib.import_module(mod)
    except ImportError:
        print(f"Installing {pkg} (sirf pehli baar)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

need("aiohttp", "aiohttp"); need("pynput", "pynput")
def opt(m, p):
    try: need(m, p); return True
    except Exception as e: print(f"(optional) {p} could not be installed: {e}"); return False
HAS_SCREEN = opt("mss", "mss") and opt("PIL", "Pillow")
HAS_QR = opt("qrcode", "qrcode")
HAS_CLIP = opt("pyperclip", "pyperclip")
opt("psutil", "psutil")
if sys.platform.startswith("win"): opt("pystray", "pystray")
try:
    import ctypes; ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

from aiohttp import web, WSMsgType
from pynput.mouse import Controller as Mouse, Button
from pynput.keyboard import Controller as Keyboard, Key
try:
    import mss; from PIL import Image; MSS = getattr(mss, "MSS", None) or mss.mss
except Exception: HAS_SCREEN = False
try: import qrcode
except Exception: HAS_QR = False
try: import pyperclip
except Exception: HAS_CLIP = False
try: import psutil
except Exception: pass

HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(os.environ.get("APPDATA") or (os.path.expanduser("~/Library/Application Support") if sys.platform == "darwin" else os.path.expanduser("~/.config")), "AirPad")
os.makedirs(DATA, exist_ok=True)
LOG = os.path.join(DATA, "airpad.log")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", handlers=[logging.handlers.RotatingFileHandler(LOG, maxBytes=300000, backupCount=1, encoding="utf-8")])
log = logging.getLogger("airpad")
CFG = os.path.join(DATA, "config.json")
if not os.path.exists(CFG):
    json.dump({"pin": str(random.randint(100000, 999999)), "port": 8765}, open(CFG, "w"))
cfg = json.load(open(CFG))
PIN, PORT = str(cfg["pin"]), int(cfg.get("port", 8765))

mouse, kb = Mouse(), Keyboard()
MON = None
if HAS_SCREEN:
    try:
        with MSS() as _s: MON = _s.monitors[1]
    except Exception as e: print("Screen capture unavailable:", e); HAS_SCREEN = False
URL, IPS = "", []
B = {"l": Button.left, "r": Button.right, "m": Button.middle}
K = {"ctrl": Key.ctrl, "alt": Key.alt, "shift": Key.shift, "win": Key.cmd, "esc": Key.esc,
     "tab": Key.tab, "enter": Key.enter, "bksp": Key.backspace, "del": Key.delete,
     "home": Key.home, "end": Key.end, "pgup": Key.page_up, "pgdn": Key.page_down,
     "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right, "space": Key.space,
     "mute": Key.media_volume_mute, "vup": Key.media_volume_up, "vdn": Key.media_volume_down,
     "play": Key.media_play_pause, "next": Key.media_next, "prev": Key.media_previous}
for i in range(1, 13):
    K[f"f{i}"] = getattr(Key, f"f{i}")

def frame():
    with MSS() as s:
        g = s.grab(MON)
    im = Image.frombytes("RGB", g.size, g.bgra, "raw", "BGRX")
    im.thumbnail((1100, 1100))
    b = io.BytesIO(); im.save(b, "JPEG", quality=60)
    return b.getvalue()

async def stream(ws):
    loop = asyncio.get_running_loop()
    try:
        while not ws.closed:
            t = time.time()
            await ws.send_bytes(await loop.run_in_executor(None, frame))
            await asyncio.sleep(max(0, 0.08 - (time.time() - t)))
    except Exception:
        pass

FAILS, CLIENTS, TOK = {}, {}, {}
def locked(ip):
    n, t = FAILS.get(ip, (0, 0)); return n >= 5 and time.time() - t < 60
def fail(ip):
    n, t = FAILS.get(ip, (0, 0)); FAILS[ip] = ((n + 1) if time.time() - t < 60 else 1, time.time())

def new_token():
    now = time.time()
    for k in [k for k, v in TOK.items() if v < now]: del TOK[k]
    t = secrets.token_urlsafe(24); TOK[t] = now + 604800; return t
def need_auth(r):
    if locked(r.remote) or TOK.get(r.headers.get("X-Token") or r.query.get("t", ""), 0) < time.time():
        fail(r.remote); raise web.HTTPForbidden(text="Not signed in")
def devname(ua):
    m = re.search(r"Android[^;)]*;\s*([^;)]+)", ua)
    if m: n = m.group(1).replace("Build", "").strip(); n = n if len(n) > 2 else "Android phone"
    else: n = "iPhone" if "iPhone" in ua else "iPad" if "iPad" in ua else "Phone"
    return re.sub(r"[^\w .\-]", "", n)[:30] or "Phone"

def batt():
    try:
        b = psutil.sensors_battery()
        return f"{int(b.percent)}%" + (" \u26a1" if b.power_plugged else "") if b else ""
    except Exception: return ""

ROOT = os.path.join(os.path.expanduser("~"), "Downloads", "AirPad")
INBOX, SHARED = os.path.join(ROOT, "Received"), os.path.join(ROOT, "Shared")

def open_inbox():
    for d in (INBOX, SHARED): os.makedirs(d, exist_ok=True)
    if sys.platform.startswith("win"): os.startfile(ROOT)
    else: subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", ROOT])

def power(a):
    w, m = sys.platform.startswith("win"), sys.platform == "darwin"
    cmds = {"lock": "rundll32.exe user32.dll,LockWorkStation" if w else "pmset displaysleepnow" if m else "loginctl lock-session",
            "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0" if w else "pmset sleepnow" if m else "systemctl suspend",
            "restart": "shutdown /r /t 5" if w else "shutdown -r now",
            "shutdown": "shutdown /s /t 5" if w else "shutdown -h now",
            "cancel": "shutdown /a" if w else "shutdown -c"}
    if a in cmds: subprocess.Popen(cmds[a], shell=True)

RESERVED = {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}
def clean(name):
    name = os.path.basename(name.replace("\\", "/")).strip().strip(".")
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)[:150] or "file"
    return "_" + name if name.split(".")[0].upper() in RESERVED else name

def listing(d):
    out = []
    try:
        for e in os.scandir(d):
            if e.is_file() and not e.name.endswith(".part"):
                st = e.stat(); out.append({"n": e.name, "s": st.st_size, "m": int(st.st_mtime)})
    except OSError: pass
    return sorted(out, key=lambda x: -x["m"])[:100]

def reveal(kind, name):
    d = {"in": INBOX, "sh": SHARED}.get(kind); p = os.path.join(d or "", os.path.basename(name))
    if not d or not os.path.isfile(p): return
    if sys.platform.startswith("win"): subprocess.Popen(f'explorer /select,"{p}"')
    elif sys.platform == "darwin": subprocess.Popen(["open", "-R", p])
    else: subprocess.Popen(["xdg-open", d])

async def upload(r):
    need_auth(r)
    os.makedirs(INBOX, exist_ok=True)
    size = int(r.headers.get("Content-Length") or 0)
    if size and shutil.disk_usage(INBOX).free < size + (200 << 20): raise web.HTTPInsufficientStorage(text="Not enough disk space on the laptop")
    base = clean(r.query.get("name", "file")); stem, ext = os.path.splitext(base); path = os.path.join(INBOX, base); n = 1
    while os.path.exists(path) or os.path.exists(path + ".part"): path = os.path.join(INBOX, f"{stem} ({n}){ext}"); n += 1
    part, loop, got = path + ".part", asyncio.get_running_loop(), 0
    try:
        with open(part, "wb") as f:
            async for c in r.content.iter_chunked(1 << 20):
                await loop.run_in_executor(None, f.write, c); got += len(c)
        if size and got != size: raise web.HTTPBadRequest(text="Upload was cut off, try again")
        os.replace(part, path)
    except BaseException:
        try: os.remove(part)
        except OSError: pass
        raise
    return web.json_response({"name": os.path.basename(path), "size": got})

async def files(r):
    need_auth(r)
    for d in (INBOX, SHARED): os.makedirs(d, exist_ok=True)
    return web.json_response({"in": listing(INBOX), "sh": listing(SHARED), "root": ROOT})

async def dl(r):
    need_auth(r)
    d = {"in": INBOX, "sh": SHARED}.get(r.match_info["k"]); p = os.path.join(d or "", os.path.basename(r.match_info["n"]))
    if not d or not os.path.isfile(p): raise web.HTTPNotFound()
    return web.FileResponse(p, headers={"Content-Disposition": "attachment; filename*=UTF-8''" + urllib.parse.quote(os.path.basename(p))})

def combo(keys):
    ks = [k if len(k) == 1 else K[k] for k in keys]
    for k in ks: kb.press(k)
    for k in reversed(ks): kb.release(k)

async def ws_handler(req):
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=262144)
    await ws.prepare(req)
    ok, sy, zy, held, task = False, 0.0, 0.0, set(), None
    try:
        async for m in ws:
            if m.type != WSMsgType.TEXT: continue
            try: d = json.loads(m.data)
            except Exception: continue
            if not isinstance(d, dict): continue
            t = d.get("t")
            if not ok:
                if locked(req.remote): await ws.send_json({"t": "locked"})
                elif t == "auth" and hmac.compare_digest(str(d.get("pin")).encode(), PIN.encode()):
                    FAILS.pop(req.remote, None); CLIENTS[id(ws)] = {"name": devname(req.headers.get("User-Agent", "")), "via": (req.host or "").rsplit(":", 1)[0], "ip": req.remote}; ok = True; await ws.send_json({"t": "ok", "n": socket.gethostname(), "tok": new_token()})
                else:
                    fail(req.remote); await asyncio.sleep(1); await ws.send_json({"t": "bad"})
                continue
            try:
                if t == "m": mouse.move(int(d["x"]), int(d["y"]))
                elif t == "s":
                    sy += float(d["y"]); n = int(sy)
                    if n: mouse.scroll(0, n); sy -= n
                elif t == "c": mouse.click(B[d["b"]], int(d.get("n", 1)))
                elif t == "d":
                    if d["s"]: mouse.press(B[d["b"]]); held.add(d["b"])
                    else: mouse.release(B[d["b"]]); held.discard(d["b"])
                elif t == "k": combo(d["keys"])
                elif t == "txt": kb.type(d["s"])
                elif t == "a": mouse.position = (MON["left"] + int(d["x"] * MON["width"]), MON["top"] + int(d["y"] * MON["height"]))
                elif t == "scr":
                    if task: task.cancel(); task = None
                    if d.get("on"):
                        if HAS_SCREEN: task = asyncio.create_task(stream(ws))
                        else: await ws.send_json({"t": "noscr"})
                elif t == "clip" and HAS_CLIP:
                    pyperclip.copy(str(d.get("s", ""))[:100000])
                    if d.get("paste"): combo(["ctrl", "v"])
                elif t == "clipget" and HAS_CLIP: await ws.send_json({"t": "clip", "s": pyperclip.paste()[:20000]})
                elif t == "url":
                    u = str(d.get("u", "")).strip()
                    if u and (u.startswith(("http://", "https://")) or "://" not in u): webbrowser.open(u if "://" in u else "https://" + u)
                elif t == "reveal": reveal(d.get("k"), str(d.get("n", "")))
                elif t == "run":
                    q = str(d.get("s", ""))[:60]
                    if q and not sys.platform.startswith("linux"):
                        combo(["win", "space"] if sys.platform == "darwin" else ["win"])
                        await asyncio.sleep(0.6); kb.type(q); await asyncio.sleep(0.5); combo(["enter"])
                elif t == "inbox": open_inbox()
                elif t == "pow": power(d.get("a"))
                elif t == "p": await ws.send_json({"t": "p", "ts": d["ts"], "b": batt()})
            except Exception as e:
                print("Action error:", e)
    finally:
        CLIENTS.pop(id(ws), None)
        if task: task.cancel()
        for b in held: mouse.release(B[b])
    return ws

LOCAL = ("127.0.0.1", "::1")
PAIR = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>AirPad</title>
<body style="margin:0;min-height:100vh;display:grid;place-items:center;background:radial-gradient(80% 50% at 50% 0,rgba(94,92,230,.4),#06070b 70%);color:#f5f5f7;font:500 16px -apple-system,Segoe UI,system-ui,sans-serif">
<div style="text-align:center;padding:40px 48px;border-radius:36px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);max-width:460px">
<img src=/icon-192.png width=72 style="border-radius:19px"><h1 style="margin:12px 0 2px;letter-spacing:-.6px">AirPad</h1>
<p style="color:#8e8e93;margin:0 0 20px">Scan with your phone camera</p>
<img id=qq width=220 height=220 alt="QR unavailable. Type the address below." style="border-radius:18px;background:#fff;padding:12px">
<p id=uu style="font-size:21px;margin:20px 0 6px"></p>
<p style="color:#8e8e93;margin:0 0 14px">PIN <b style="color:#f5f5f7;letter-spacing:5px">__PIN__</b></p>
<div id=dv style="margin:0 0 16px;font-weight:600"></div>
<p style="color:#8e8e93;font-size:13px;margin:0 0 8px">Addresses found on this laptop, updated live. A check mark means a phone connected through it:</p>
<div id=bs style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap"></div></div>
<script>let I=[],sel='',P=__PORT__;
function draw(){bs.innerHTML=I.map(x=>`<button onclick="pick('${x.ip}')" style="border:0;color:#fff;padding:9px 14px;border-radius:12px;font:inherit;font-size:14px;cursor:pointer;background:${x.ip===sel?'#0a84ff':'rgba(255,255,255,.1)'}">${x.ip}${x.ok?' \\u2713':''}</button>`).join('')}
function pick(i){sel=i;qq.src='/qr.png?ip='+i+'&v='+Date.now();uu.textContent='http://'+i+':'+P;draw()}
async function tick(){try{const j=await(await fetch('/info')).json();P=j.port;const same=JSON.stringify(j.ips)===JSON.stringify(I.map(x=>x.ip));
I=j.ips.map(ip=>({ip,ok:j.devices.some(d=>d.via===ip)}));if(!same||!j.ips.includes(sel))pick(j.ips.includes(sel)?sel:j.ips[0]);else draw();
dv.innerHTML=j.devices.length?j.devices.map(d=>`<div style="color:#30d158">\\u25CF ${d.name} connected</div>`).join(''):'<div style="color:#8e8e93;font-weight:500">Waiting for a phone...</div>'}catch(e){dv.textContent='AirPad is not running'}}
tick();setInterval(tick,2000)</script>"""

def local(h):
    async def w(r):
        if r.remote not in LOCAL: raise web.HTTPForbidden()
        return await h(r)
    return w
def static(name):
    async def h(_):
        p = os.path.join(HERE, name)
        with open(p, "rb") as f: body = f.read()
        return web.Response(body=body, content_type=mimetypes.guess_type(p)[0] or "application/octet-stream", headers={"Cache-Control": "no-cache"})
    return h
SEC = {"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer",
       "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' ws: wss:; frame-ancestors 'none'"}

@web.middleware
async def errors(request, handler):
    r, h = request, handler
    try: return await h(r)
    except (web.HTTPException, asyncio.CancelledError): raise
    except Exception as e:
        log.error("ERROR %s %s\n%s", r.method, r.path_qs, traceback.format_exc())
        msg = f"{type(e).__name__}: {e}" if r.remote in LOCAL else "Internal error"
        if "text/html" in r.headers.get("Accept", ""):
            return web.Response(status=500, content_type="text/html", text="<meta charset=utf-8><body style='font:16px system-ui;background:#06070b;color:#f5f5f7;padding:40px'><h2>AirPad hit a problem</h2><p>%s</p><p style='color:#8e8e93'>Details are saved in %s. Send that file to the developer.</p></body>" % (html.escape(msg), html.escape(LOG)))
        return web.json_response({"error": msg}, status=500)

@web.middleware
async def guard(request, handler):
    r, h = request, handler
    try:
        ip = ipaddress.ip_address(r.remote or "127.0.0.1")
        ip = getattr(ip, "ipv4_mapped", None) or ip
        if ip.is_global: raise web.HTTPForbidden()
    except ValueError: pass
    host = (r.host or "").rsplit(":", 1)[0].strip("[]").lower()
    try: ipaddress.ip_address(host)
    except ValueError:
        if host not in ("localhost", socket.gethostname().lower()) and not host.endswith(".local"): raise web.HTTPForbidden(text="Bad host")
    o = r.headers.get("Origin")
    if o:
        try: onet = urllib.parse.urlparse(o).netloc.lower()
        except ValueError: onet = ""
        if onet != (r.host or "").lower(): raise web.HTTPForbidden(text="Bad origin")
    resp = await h(r)
    if not isinstance(resp, web.WebSocketResponse):
        try: resp.headers.update(SEC)
        except Exception: pass
    return resp
async def health(_): return web.Response(text="AirPad is running")
async def info(_): return web.json_response({"ips": lan_ips(), "port": PORT, "devices": list(CLIENTS.values())})
async def pair(_):
    return web.Response(text=PAIR.replace("__PIN__", PIN).replace("__PORT__", str(PORT)), content_type="text/html")
async def qr(r):
    ips = lan_ips(); ip = r.query.get("ip") or ips[0]
    if not HAS_QR or ip not in ips: raise web.HTTPNotFound()
    b = io.BytesIO(); qrcode.make(f"http://{ip}:{PORT}/#p={PIN}").save(b, "PNG")
    return web.Response(body=b.getvalue(), content_type="image/png")
async def manifest(_):
    ic = [{"src": f"/icon-{n}.png", "sizes": f"{n}x{n}", "type": "image/png", "purpose": "any maskable"} for n in (192, 512)]
    return web.json_response({"name": "AirPad", "short_name": "AirPad", "start_url": "/", "display": "standalone",
        "background_color": "#06070b", "theme_color": "#06070b", "icons": ic})

async def showlog(_):
    try: txt = open(LOG, encoding="utf-8").read()[-20000:]
    except OSError: txt = "No log yet"
    return web.Response(text=txt, content_type="text/plain")

def selfcheck():
    import urllib.request, urllib.error
    bad = []
    for p in ("/health", "/", "/pair", "/info", "/manifest.json", "/icon-192.png") + (("/qr.png",) if HAS_QR else ()):
        try: urllib.request.urlopen(f"http://127.0.0.1:{PORT}{p}", timeout=5).read()
        except urllib.error.HTTPError as e: bad.append(f"{p} -> HTTP {e.code} {e.read()[:150]!r}")
        except Exception as e: bad.append(f"{p} -> {e}")
    log.info("Self-check %s", "passed" if not bad else "FAILED: " + "; ".join(bad))
    print("  Self-check:", "all pages OK" if not bad else "PROBLEM: " + "; ".join(bad))
    if bad:
        try: print("\n  --- last log lines (send a screenshot of this) ---\n" + open(LOG, encoding="utf-8").read()[-1800:])
        except OSError: pass

def lan_ips():
    ok = lambda i: not i.startswith(("127.", "169.254.", "0."))
    primary = None
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(("8.8.8.8", 80)); primary = s.getsockname()[0]
    except Exception: pass
    finally: s.close()
    ips = set()
    try: ips |= {a[4][0] for a in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)}
    except Exception: pass
    rank = lambda i: (0 if i.startswith("192.168.") else 1 if i.startswith("10.") else 2, i)
    rest = sorted((i for i in ips if ok(i) and i != primary), key=rank)
    return ([primary] if primary and ok(primary) else []) + rest or ["127.0.0.1"]

def free(p):
    s = socket.socket()
    try: s.bind(("0.0.0.0", p)); return True
    except OSError: return False
    finally: s.close()

def autostart(on=None):
    import winreg
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
    if on is None:
        try: winreg.QueryValueEx(k, "AirPad"); return True
        except OSError: return False
    exe = sys.executable.replace("python.exe", "pythonw.exe")
    cmd = f'"{exe}" --quiet' if FROZEN else f'"{exe}" "{os.path.abspath(__file__)}" --quiet'
    if on: winreg.SetValueEx(k, "AirPad", 0, winreg.REG_SZ, cmd)
    else:
        try: winreg.DeleteValue(k, "AirPad")
        except OSError: pass

def tray():
    try:
        import pystray; from PIL import Image
        M = pystray.MenuItem
        menu = pystray.Menu(M("Pair a phone", lambda: webbrowser.open(f"http://localhost:{PORT}/pair"), default=True),
            M("Open received files", lambda: open_inbox()),
            M("Start with Windows", lambda: autostart(not autostart()), checked=lambda item: autostart()),
            M("Quit AirPad", lambda icon, item: (icon.stop(), os._exit(0))))
        pystray.Icon("AirPad", Image.open(os.path.join(HERE, "icon-192.png")), "AirPad", menu).run()
    except Exception as e: print("Tray unavailable:", e)

if __name__ == "__main__":
    try:
        import urllib.request
        if b"AirPad" in urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=1).read():
            if "--quiet" not in sys.argv: webbrowser.open(f"http://localhost:{PORT}/pair")
            sys.exit(0)
    except Exception: pass
    for p in range(PORT, PORT + 11):
        if free(p): PORT = p; break
    IPS = lan_ips(); URL = f"http://{IPS[0]}:{PORT}"
    print("\n  AirPad is running. PIN:", PIN)
    print("  Open on your phone (same WiFi), try these in order:")
    for i in IPS: print(f"    http://{i}:{PORT}")
    print(f"  Test page (phone): http://{IPS[0]}:{PORT}/health\n")
    if not HAS_SCREEN: print("  Note: Screen tab is disabled (mss/Pillow missing). Everything else works.\n")
    app = web.Application(middlewares=[errors, guard])
    app.add_routes([web.get("/", static("index.html")), web.get("/ws", ws_handler), web.get("/health", health), web.post("/upload", upload), web.get("/files", files), web.get("/dl/{k}/{n}", dl), web.get("/manifest.json", manifest),
        web.get("/icon-192.png", static("icon-192.png")), web.get("/icon-512.png", static("icon-512.png")),
        web.get("/apple-touch-icon.png", static("apple-touch-icon.png")),
        web.get("/pair", local(pair)), web.get("/log", local(showlog)), web.get("/info", local(info)), web.get("/qr.png", local(qr))])
    if "--quiet" not in sys.argv: threading.Timer(1.5, webbrowser.open, [f"http://localhost:{PORT}/pair"]).start()
    if sys.platform.startswith("win"): threading.Thread(target=tray, daemon=True).start()
    log.info("AirPad starting on port %s, addresses %s", PORT, IPS)
    threading.Timer(2.5, selfcheck).start()
    web.run_app(app, host="0.0.0.0", port=PORT, print=None, access_log=None)
