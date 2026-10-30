[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/airpad?style=flat-square)](https://github.com/YOUR_USERNAME/airpad/stargazers)
[![Downloads](https://img.shields.io/github/downloads/YOUR_USERNAME/airpad/total?style=flat-square)](https://github.com/YOUR_USERNAME/airpad/releases)

# AirPad

**Control your laptop from your phone. Wireless. Private. Open source.**

Your phone becomes a real wireless touchpad, keyboard and remote for your laptop—with haptics, momentum scroll, live screen view and file transfers. Scan a QR code, that's it. No cloud, no account, no app to install on the phone.

🚀 **Fast**: talks directly over your WiFi, no cloud in between  
🔒 **Private**: Everything stays on your network  
📱 **Works everywhere**: Windows, Mac, Linux. iPhone, Android, tablet  
🆓 **Truly free**: MIT open source, no ads, no premium  

[Download (Windows)](https://github.com/YOUR_USERNAME/airpad/releases/latest) · [Website](https://YOUR_USERNAME.github.io/airpad) · [Features](#-features) · [FAQ](#-faq)

---

## ⚡ Quick Start

**Windows:**
1. Download `AirPad.exe` from [Releases](https://github.com/YOUR_USERNAME/airpad/releases/latest)
2. Run it, click **Allow** on the Firewall prompt (private networks)
3. A pairing page opens. Scan the QR with your phone camera (same WiFi)
4. Done. Your phone controls your laptop

**Mac / Linux:**
```bash
pip install -r requirements.txt
python server.py
```

---

## 🎮 Features

### Real Touchpad
- **Tap** to click, **drag** to select, **momentum scroll** that feels natural
- **Two-finger tap** for right-click, **three-finger swipe** to switch apps
- **Haptic feedback**: feel the click, every interaction

### Live Screen + Tap to Click
- See your laptop on your phone in real time
- Tap the screen to click, hold for right-click, swipe to move
- Turn your phone into a presentation remote

### Type from Your Phone
- Phone keyboard sends text to your laptop
- Media keys, shortcuts (Ctrl+C, Alt+Tab), function keys, hold-to-repeat arrows
- Your own shortcuts and text snippets, and an "open an app by name" box
- Presenter mode: Previous, Next, Black screen

### AirDrop-Style Files
- **Drag photos from your phone** → they land in a Received folder on your laptop
- **Put files in a Shared folder on your laptop** → they show up on your phone, swipe to save
- Real-time file list, upload progress, atomic writes (no partial files)

### Clipboard Sync
- Copy text on your phone, paste on your laptop
- Uses the clipboard, so non-English text such as Urdu should paste correctly

### Power Controls
- Lock, sleep, restart or shut down with a safe press-and-hold
- 5-second countdown before restart/shutdown (you can cancel)

### Responsive & Offline
- Works on any screen size: phone, tablet, landscape mode
- No internet needed—just WiFi between your phone and laptop

---

## 🔒 Security

- **6-digit PIN**: required to pair. 5 wrong attempts = 1 minute lockout per device
- **Local network only**: requests from public internet are rejected
- **Session tokens**: file transfers use random tokens, never the PIN
- **Host & Origin checks**: blocks DNS rebinding and other website spoofing
- **No telemetry**: nothing is logged, nothing leaves your network

**Read more:** [SECURITY.md](SECURITY.md)

---

## ❓ FAQ

### Does it need internet?
No. Your laptop and phone only need to be on the same WiFi. Phone hotspot works too.

### Why no cloud?
Because your keystrokes and screen shouldn't be in someone else's database. Local also means no internet round trip.

### My phone cannot open the pairing page
1. Open `http://LAPTOP-IP:8765/health` on your phone. It should say "AirPad is running"
2. Try each address on the pairing page (they're listed live)
3. Turn off VPNs and phone mobile data
4. **Guest WiFi blocks this**: use your phone hotspot instead, connect your laptop to it

### Is it fast?
The delay depends on your WiFi quality. The phone app shows your live delay in milliseconds at the top.

### Can I use it over the internet?
No. AirPad rejects public internet addresses for security. If you need internet access, we recommend using Microsoft Remote Desktop or TeamViewer instead.

### Mac / Linux support?
**Mac**: should work from source (see Quick Start) but is not tested yet. Needs Accessibility permission.  
**Linux**: X11 only (Wayland not supported due to input injection limitations).  
**Windows**: the main tested platform.

### How do I change the PIN?
Edit `config.json`:
- **Windows**: `%APPDATA%\AirPad\config.json`
- **Mac**: `~/Library/Application Support/AirPad/config.json`
- **Linux**: `~/.config/AirPad/config.json`

Change `"pin"` value, restart AirPad.

---

## 📊 What's New (2.5.0)

- 🎯 **AirDrop-style file transfer**: send from phone, pick up files from laptop
- 🛡️ **Tighter security**: session tokens, Host/Origin checks, security headers
- 📱 **Add to home screen prompt**: install as app on your phone
- 🔴 **Live device list**: pairing page shows connected phones in real time
- ❌ **Removed pinch zoom** (two-finger scroll only, simpler and more reliable)

[Full changelog](CHANGELOG.md)

---

## 🛠️ Built With

- **Backend**: Python, aiohttp (async web framework)
- **Frontend**: Vanilla JavaScript (no frameworks, no nonsense)
- **Desktop app**: PyInstaller (Windows exe), native tray icon
- **Mobile UI**: Responsive HTML/CSS, PWA (add to home screen)
- **Testing**: Manual on real phones and laptops

---

## 🤝 Contributing

Bug reports and pull requests welcome.

**To test:**
1. Run `python server.py`
2. Open the pairing page on a real phone (not a simulator)
3. Report what you see

**Guidelines:** Keep server.py and index.html in one file each so the project stays readable. Describe what changed and which phone/OS you tested on.

[CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 💭 Why I Built This

Other phone-remote apps I tried were slow to respond and kept the good features behind a paywall. AirPad is my answer: free, open source, runs on your own laptop and designed to feel smooth.

---

**Questions?** Open an [issue](https://github.com/YOUR_USERNAME/airpad/issues) or check [SECURITY.md](SECURITY.md) for vulnerability reports.

**Like it?** Star the repo ⭐ and [share it](https://github.com/YOUR_USERNAME/airpad) with someone who presents, codes or just moves their laptop around a lot.

