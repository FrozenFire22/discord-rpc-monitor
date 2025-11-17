# Discord RPC Universal Monitor

Display your YouTube playback, Discord channel, and desktop activity as a Rich Presence status in Discord.

---

## 🚀 Quick Start

Download the latest release from the [Releases page](https://github.com/XamDaniel-AA/discord-rpc-monitor/releases) and extract the ZIP file. Then follow the Installation section below.

---

## Features

**Website Monitoring** (Browser-based)

YouTube Integration provides real-time playback tracking with automatic chapter detection.

- Real-time playback timestamps: Shows exactly where you are in a video
- Automatic chapter detection: If a video has chapters/sections, it displays which one you're watching
- Cross-tab tracking: Your YouTube activity continues updating even when you switch to other browser tabs
- Homepage detection: When you finish watching or navigate to YouTube homepage, shows "Browsing YouTube"
- Channel attribution: Shows the creator's name alongside the video
- Smart title cleanup: If the channel name appears in the video title, it's automatically removed to avoid redundancy

Discord Web support monitors discord.com and instantly detects channel switches.

- Instant channel updates: Switches to a new channel and RPC updates within milliseconds
- Server awareness: Displays which server you're on when switching between multiple Discord servers
- Simultaneous monitoring: Works alongside Discord Desktop app without conflicts

Website blocklist functionality prevents sensitive websites from appearing in your RPC. Automatically blocks Facebook, Instagram, Twitter, Reddit and others. Add your own websites that shouldn't appear in your status. When you visit a blocked site, your previous RPC stays displayed instead of updating.

**Discord Desktop App Monitoring** (Native window detection)

Discord Desktop app detection reads your application window title for instant channel information. No browser extension needed - works directly from the Discord Desktop app. Updates appear within milliseconds of switching channels.

Discord app blocklist hides activity in specific channels and servers. Use flexible substring matching where a single entry blocks any channel or server containing those words. You can also use `#` prefix to block specific channels only (not servers). For example, `'#announcements'` blocks the channel #announcements but not a server named "announcements". When you enter a blocked channel, your RPC immediately clears.

**PC Application Monitoring**

Desktop application monitoring shows what programs you're actively using. When you switch to VS Code, Spotify, OBS, or other apps, the RPC can show what you're using. Only the currently focused application is displayed.

Application blocklist prevents specific desktop programs from appearing in your RPC. Hide sensitive tools by listing applications by their executable filename. When these apps are active, they won't appear in your status.

**Privacy & Customization**

Channel and server blocklist prevents RPC from revealing activity in specific Discord locations. Use substring matching or prefix with `#` for channel-specific blocking. The blocklist works across both Discord Web and Desktop app simultaneously.

Auto-updating Discord bio adds a live timestamp to your Discord profile. Updates every minute showing current time. Customize the message by modifying the code.

---

## RPC Display Examples

**When Watching YouTube (Without Chapters)**

Your Discord profile shows:

```
Discord Status Display:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶️  RPC
    Song Title - Album Name
    Channel Name · YouTube (3:45/7:23)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**When Watching YouTube (With Chapters)**

Your Discord profile shows:

```
Discord Status Display:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶️  RPC
    Chapter Name - Song Title
    Channel Name · YouTube (2:15/5:30)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Note: When chapters are detected, the format is "Chapter Name - Song Title - Album Name". If the channel name appears in the title, it's automatically removed to prevent redundancy.

**When In Discord Desktop App**

Your Discord profile shows:

```
Discord Status Display:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬  RPC
    In #music
    On Discord
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

When viewing a server instead of a specific channel:

```
Discord Status Display:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬  RPC
    In My Server Name
    On Discord
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**When Using Desktop Applications**

Your Discord profile shows:

```
Discord Status Display:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥️  RPC
    main.py - My Project
    Using VisualStudioCode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**When Visiting a Website**

Your Discord profile shows:

```
Discord Status Display:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐  RPC
    awesome-project - Your awesome repo
    GitHub Browsing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Discord Bio Example**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nov 3 - 10:49 AM ( <t:1730607000:t> )
If the clock stops, I'm probably touching grass or sleeping.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
---

## Requirements

- **Windows PC** (uses win32gui for window monitoring)
- **Python 3.8+**
- **Discord Desktop app** (must be running in background while using this)
- **Web browser** (Chrome, Edge, Brave, or Firefox) with Tampermonkey

---

## Installation

### 1. Extract ZIP File

Download from [Releases](https://github.com/XamDaniel-AA/discord-rpc-monitor/releases) and extract to your desired location.

### 2. Install Python Dependencies

Open command prompt in the extracted folder and run:
```bash
pip install pypresence
pip install flask
pip install flask-cors
pip install requests
pip install pypiwin32
pip install psutil
```

This installs all required packages: pypresence (Discord RPC), Flask (web server), requests (API calls), and others.

### 3. Get Your Discord Token

Open Discord Web → Press `F12` → Go to **Network** tab → Refresh page → Find request to `api.discord.com` → Check **Authorization** header → Copy the token value.

⚠️ **Keep this token secret!** Anyone with it can access your Discord account.

### 4. Configure Token

Open `discord-rpc-universal.py` and find:
```python
DISCORD_TOKEN = "YOUR_TOKEN_HERE"
```

Replace with your actual token.

### 5. Load Browser Extension

**Chrome/Edge:** `chrome://extensions` → Developer Mode ON → Load unpacked → Select `extension/` folder

**Firefox:** `about:debugging` → Load Temporary Add-on → Select `manifest.json`

### 6. Install Tampermonkey Script

1. Install [Tampermonkey](https://www.tampermonkey.net/)
2. Click Tampermonkey icon → Create new script
3. Paste contents of `youtube-chapter-rpc.js`
4. Save

### 7. Start Discord Desktop App

Make sure the Discord Desktop application is running and fully loaded. Keep it open in the background while running the Python server.

### 8. Run Python Server

Open command prompt and run (or simply just double click on the python script file):
```bash
python discord-rpc-universal.py
```

You should see:
```
[Discord RPC] ✅ Connected!
✅ Ready - All features enabled
```

**Keep this command prompt window open continuously.** Closing it stops all RPC updates.

---

## Configuration

### Discord Blocklist

Edit `discord-rpc-universal.py` in the `BLOCKED_DISCORD` section:

```python
BLOCKED_DISCORD = [
    'general',
    'random',
    '#announcements',
    'staff',
]
```

How matching works:

- `'general'` blocks any channel/server containing "general" (e.g., #general, #general-chat, "General Server")
- `'#announcements'` blocks only the channel named #announcements, not a server named "announcements"
- `'staff'` blocks any channel/server with "staff" in the name (#staff, #staff-only, "staff-server")
- Matching is case-insensitive (blocks "Staff", "STAFF", "staff" all the same way)

### Application Blocklist

Edit the `BLOCKED_APPS` section:

```python
BLOCKED_APPS = [
    'Telegram.exe',
    'WhatsApp.exe',
    'notepad.exe',
]
```

When these applications are your active window (foreground), they won't appear in your RPC. The RPC will stay frozen on whatever you were doing previously. List the executable filenames exactly as they appear in your system.

### Website Blocklist

Edit the `BLOCKED_SITES` section:

```python
BLOCKED_SITES = [
    'facebook.com',
    'instagram.com',
    'reddit.com',
    'bankofamerica.com',
]
```

When you visit these websites, they won't update your RPC. Your previous status remains displayed instead. Add any websites you want to keep private from your Discord status.

### Customize Discord Bio Message

Find the `note` variable in the code:

```python
note = "If the clock stops, I'm probably touching grass or sleeping."
```

Replace the text between the quotes with your custom message:

```python
note = "Always learning • Open for collaborations"
```

or

```python
note = "Gaming | Music | Code\nHit me up!"
```

The `\n` creates a line break in your bio. Don't modify the rest of the function.

### Polling Speed (How Often RPC Updates)

Find the `monitor_loop()` function and locate the `time.sleep()` line:

```python
def monitor_loop(self):
    while True:
        try:
            self.update_rpc()
        except Exception as e:
            pass
        time.sleep(0.1)   # <-- Change this number
```

To change the polling speed, simply replace the number with one of these values:

```python
time.sleep(0.1)   # 100ms - FASTEST (10 updates per second)
time.sleep(0.25)  # 250ms - FAST (4 updates per second)
time.sleep(0.5)   # 500ms - MEDIUM (2 updates per second)
time.sleep(1.0)   # 1000ms - SLOW (1 update per second)
```

**Just replace the `0.1` with your desired value. Don't comment anything out or remove other lines.** For example, to use 500ms speed, change:

```python
# Before:
time.sleep(0.1)

# After:
time.sleep(0.5)
```

Then save the file and restart the Python server for the change to take effect.

**What each speed means:**

- **0.1 (100ms)**: Updates 10 times per second. Nearly instant when switching channels or videos. Default and recommended. Uses ~1-2% CPU.

- **0.25 (250ms)**: Updates 4 times per second. Still feels instant. Better for laptops. Uses ~1% CPU.

- **0.5 (500ms)**: Updates 2 times per second. Slight delay when switching. Noticeable but not annoying. Uses ~0.5% CPU.

- **1.0 (1000ms)**: Updates once per second. Slowest option. Only use on very old computers. Feels slightly laggy.

---

## Troubleshooting

**Server won't connect to Discord**

Make sure the Discord Desktop application is running before starting the Python server. The Discord app must be fully loaded and in the system tray. Check that you're not already running another RPC application on the same port.

**YouTube not tracking**

Refresh the YouTube page with F5. Verify the browser extension is enabled in your extensions menu. Check that Tampermonkey is installed and the youtube-chapter-rpc.js script is active. If still not working, restart the Python server.

**Discord channels not showing**

Restart the Python server. For Desktop app, make sure Discord window is visible and has been focused at least once since starting the server. For Discord Web, reload discord.com.

**Chapters not displaying**

Not all YouTube videos contain chapter information. Test with a video known to have chapters. Verify Tampermonkey is installed and the script is active. Check the Python console output for errors.

**CPU usage too high**

Increase the polling interval by changing `time.sleep(0.1)` to `time.sleep(0.5)` or higher. This reduces how often the system checks for changes. Alternatively, disable auto-bio updates by commenting out the `server.start_bio_updater()` line.

---

## FAQ

**Q: Is my token safe?**
A: Your token stays local on your PC. Never share it or commit it to repositories.

**Q: Does Discord ban people for this?**
A: User account automation violates Discord's Terms of Service. Use at your own risk.

**Q: Can I use this on Mac or Linux?**
A: No, this requires Windows-specific APIs that don't exist on other operating systems.

**Q: Do I need to keep the Discord app open?**
A: Yes, Discord must be running for RPC to display your status. The RPC server communicates with Discord through the Desktop app.

**Q: Why is the app name always the same?**
A: The RPC system uses a custom Discord bot that I created. Because of this bot setup, the app name in the RPC cannot be changed. This doesn't affect any functionality.

---
## Acknowledgements

This project utilizes the following open-source libraries and services:

- **[pypresence](https://github.com/qwertyquerty/pypresence)** - Discord Rich Presence library for Python
- **[Flask](https://flask.palletsprojects.com/)** - Lightweight web framework for the local server
- **[Flask-CORS](https://flask-cors.readthedocs.io/)** - Cross-Origin Resource Sharing for Flask
- **[Requests](https://requests.readthedocs.io/)** - HTTP library for API communication
- **[pywin32](https://github.com/pywin32/pywin32)** - Windows API access for window monitoring
- **[psutil](https://github.com/giampaolo/psutil)** - System and process utilities
- **[Tampermonkey](https://www.tampermonkey.net/)** - Userscript manager for browser automation
- **[Discord API](https://discord.com/developers)** - Rich Presence and user profile endpoints

---

## License

MIT License - See LICENSE file for details

---

⭐ If this helped, consider leaving a star on GitHub!
