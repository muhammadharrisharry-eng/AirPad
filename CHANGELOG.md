# Changelog

## 2.6.0
- Responsive layout for Pad, Keys and Shortcuts (fluid buttons, short screens, landscape, notches)
- Arrow keys as a proper cluster, hold-to-repeat for arrows, Back, Del, PgUp, PgDn and volume
- Your own shortcuts and text snippets, open an app by name, more built-in shortcuts

## 2.5.2
- Fixed every page returning HTTP 500: middleware parameters now use the names aiohttp expects (`request`, `handler`)
- Silenced the mss deprecation warning, self-check prints the log tail when something fails

## 2.5.1
- Errors are written to a log file (`airpad.log`) and shown with a clear message instead of a blank 500 page
- Startup self-check tests every page and prints the result
- Static pages served without FileResponse, safer PIN and message handling

## 2.5.0
- Removed pinch zoom, two fingers now only scroll
- Reliable file transfer: queue, progress, atomic saves, disk check, Received and Shared folders, file list
- Add to home screen prompt, live address and device list on the pairing page
- Session tokens, Origin and Host checks, security headers

## 2.4.0
- QR code signs the phone in automatically, pairing page confirms "Phone connected"
- Rejects connections from public internet addresses
- Project website (GitHub Pages) with one-click download links

## 2.3.0
- Rebuilt gesture engine: scroll and zoom lock after a short deadzone, lifting or adding a finger no longer causes jumps, momentum scroll
- Responsive navigation bar (small phones, tablets, landscape)
- Windows tray app, Start with Windows, single-instance guard
- PIN lockout after 5 wrong attempts, settings stored in the user profile folder
- GitHub Actions build for `AirPad.exe`

## 2.2.0
- Enter and Speed buttons on the pad, haptics, ripples, quick links, battery in status pill

## 2.1.0
- Clipboard, file transfer, presenter mode, power controls, pinch zoom, three-finger swipes

## 2.0.0
- Live screen view, pairing page with QR, PIN keypad, new design
