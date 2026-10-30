# Security

AirPad lets a paired phone control your laptop's mouse, keyboard and screen. Treat the PIN like a password.

- Local network only: requests from public internet addresses are rejected. Never port-forward AirPad.
- 6 digit PIN, 5 wrong attempts lock that device for a minute. Traffic is plain HTTP, so avoid public or shared WiFi (cafes, hostels). Use your phone hotspot there.
- Change the PIN in `config.json` (Windows: `%APPDATA%\AirPad`) if you think it leaked.

Report vulnerabilities privately via the repository's Security tab (Report a vulnerability), not in public issues.

## How requests are protected
- Sign in with the PIN once, the server then issues a random session token used for file transfers.
- Every request needs a local Host header and a matching Origin, which blocks other websites and DNS rebinding.
- Responses carry nosniff, no-frame and Content-Security-Policy headers.
