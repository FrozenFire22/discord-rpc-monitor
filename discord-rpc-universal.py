from flask import Flask, request, jsonify
from flask_cors import CORS
from pypresence import Presence
import time
import re
import threading
from datetime import datetime
import requests
import win32gui
import win32process
import psutil

CLIENT_ID = "1431599716050931954"
DISCORD_TOKEN = "YOUR_TOKEN_HERE"

flask_app = Flask(__name__)
CORS(flask_app)

BLOCKED_SITES = [
    'facebook.com', 'instagram.com', 'twitter.com', 'x.com',
    'tiktok.com', 'reddit.com', 'snapchat.com', 'linkedin.com',
    'whatsapp.com', 'telegram.org', 'pinterest.com', 'tumblr.com',
    'threads.net', 'mastodon.social', 'bluesky.app',
    'perplexity.com', 'perplexity.ai'
]

BLOCKED_APPS = [
    'Telegram.exe', 'WhatsApp.exe', 'Signal.exe',
    'notepad.exe', 'explorer.exe',
]

BLOCKED_DISCORD = [
    'idk',
    'random',
    'spam',
    '#nsfw',
]


class DiscordRPCServer:
    def __init__(self):
        self.rpc = None
        self.start_time = int(time.time())
        self.last_rpc_state = None
        self.bio_updater_running = False
        self.window_monitor_running = False
        self.browser_data = None
        self.browser_timestamp = 0
        self.active_window_data = None
        self.active_window_timestamp = 0

    def connect_rpc(self):
        try:
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            print("[Discord RPC] ✅ Connected!")
            return True
        except Exception as e:
            print(f"[Discord RPC] ❌ Failed: {e}")
            return False

    def make_bio(self):
        now = datetime.now()
        months_short = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        date_part = f"{months_short[now.month-1]} {now.day}"
        
        hours = now.hour
        mins = str(now.minute).zfill(2)
        ampm = 'PM' if hours >= 12 else 'AM'
        hours = hours % 12 or 12
        your_time = f"{hours}:{mins} {ampm}"
        
        unix_now = int(time.time())
        discord_timestamp = f"<t:{unix_now}:t>"
        
        note = "If the clock stops, I'm probably touching grass or sleeping.\nBefore we talk, my personality is INTP-A."
        
        bio = f"{date_part} • {your_time} ( {discord_timestamp} )\n{note}"
        return bio[:190]

    def update_bio(self):
        try:
            bio = self.make_bio()
            requests.patch(
                'https://discord.com/api/v9/users/@me/profile',
                headers={'Authorization': DISCORD_TOKEN, 'Content-Type': 'application/json'},
                json={'bio': bio}
            )
        except:
            pass

    def bio_updater_loop(self):
        self.update_bio()
        while True:
            now = datetime.now()
            time.sleep(60 - now.second)
            self.update_bio()

    def start_bio_updater(self):
        if not self.bio_updater_running:
            self.bio_updater_running = True
            threading.Thread(target=self.bio_updater_loop, daemon=True).start()

    def get_active_window_info(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            exe_name = psutil.Process(pid).name()
            return title, exe_name
        except:
            return None, None

    def get_all_discord_windows(self):
        """Find ALL Discord windows and their titles"""
        discord_windows = []
        
        def enum_windows(hwnd, ctx):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    exe_name = psutil.Process(pid).name()
                    
                    if exe_name.lower() == 'discord.exe' and title:
                        discord_windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'exe': exe_name
                        })
            except:
                pass
        
        win32gui.EnumWindows(enum_windows, None)
        return discord_windows

    def get_active_discord_context(self):
        """Get channel/server from Discord PC window title"""
        try:
            discord_wins = self.get_all_discord_windows()
            
            if not discord_wins:
                return None
            
            for win in discord_wins:
                title = win['title']
                
                if '—' in title:
                    parts = title.split('—')
                    if len(parts) >= 2:
                        context = parts[0].strip()
                        if context and context.lower() != 'discord':
                            return context
                
                context = title.replace(' — Discord', '').replace('Discord', '').strip()
                if context:
                    return context
            
            return None
        except Exception as e:
            return None

    def is_blocked_app(self, exe_name):
        return exe_name.lower() in [a.lower() for a in BLOCKED_APPS]

    def is_blocked_site(self, hostname):
        return any(blocked in hostname for blocked in BLOCKED_SITES)

    def is_browser_window(self, exe_name):
        browsers = ['chrome.exe', 'msedge.exe', 'brave.exe', 'firefox.exe', 'opera.exe', 'vivaldi.exe', 'comet.exe']
        return exe_name.lower() in browsers

    def is_blocked_discord_context(self, context):
        if not context:
            return False
        context_lower = context.lower()
        for blocked in BLOCKED_DISCORD:
            if blocked.lower() in context_lower:
                return True
        return False

    def clean(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    def strip_parens(self, text):
        return re.sub(r'\s*\([^)]*\)', '', text).strip()

    def remove_channel_from_title(self, title, channel):
        if not channel or not title:
            return title
        title = re.sub(re.escape(channel), '', title, flags=re.IGNORECASE).strip()
        return title.strip(' -').strip()

    def build_activity_from_window(self, window_title, exe_name):
        if not window_title or not exe_name or self.is_blocked_app(exe_name):
            return None
        if self.is_browser_window(exe_name):
            return None

        if exe_name.lower() == 'discord.exe':
            discord_context = self.get_active_discord_context()
            
            if discord_context and self.is_blocked_discord_context(discord_context):
                print(f"[Discord PC] Blocked: {discord_context}")
                return None
            
            context_text = discord_context or 'Discord'
            return {
                'name': 'Discord',
                'details': f'In {context_text}',
                'state': 'On Discord',
                'large_image': 'desktop',
                'large_text': 'On Discord'
            }

        app_name = exe_name.replace('.exe', '')
        clean_title = self.clean(window_title)[:128]

        return {
            'name': app_name,
            'details': clean_title,
            'state': f'Using {app_name}',
            'large_image': 'desktop',
            'large_text': f"Using {app_name}"
        }

    def build_activity_browser(self, title, url, chapter='', channel='', currentTime='0:00', duration='0:00'):
        hostname = url.split('://')[1].split('/')[0] if '://' in url else ''
        if self.is_blocked_site(hostname):
            return None

        raw = self.clean(title.replace('\n', ' '))

        if 'youtube.com' in hostname:
            if 'watch' in url and currentTime != '0:00':
                raw = raw.replace(' - YouTube', '').strip()
                raw = self.strip_parens(raw)
                raw = self.remove_channel_from_title(raw, channel)
                
                details = raw[:128]
                if chapter:
                    details = f"{chapter} — {raw}"[:128]
                
                if channel:
                    state = f"({channel}) · YouTube ({currentTime}/{duration})"
                else:
                    state = f"YouTube ({currentTime}/{duration})"
                
                return {
                    'name': 'YouTube',
                    'details': details,
                    'state': state,
                    'large_image': 'web_browser',
                    'large_text': 'Watching YouTube'
                }
            else:
                return {
                    'name': 'YouTube',
                    'details': 'Browsing',
                    'state': 'YouTube',
                    'large_image': 'web_browser',
                    'large_text': 'On YouTube'
                }

        elif 'music.youtube.com' in hostname:
            if currentTime != '0:00':
                raw = raw.replace(' - YouTube Music', '').strip()
                raw = self.strip_parens(raw)
                raw = self.remove_channel_from_title(raw, channel)
                
                details = raw[:128]
                if chapter:
                    details = f"{chapter} — {raw}"[:128]
                
                if channel:
                    state = f"({channel}) · YouTube Music ({currentTime}/{duration})"
                else:
                    state = f"YouTube Music ({currentTime}/{duration})"
                
                return {
                    'name': 'YouTube Music',
                    'details': details,
                    'state': state,
                    'large_image': 'web_browser',
                    'large_text': 'Listening to YouTube Music'
                }
            else:
                return {
                    'name': 'YouTube Music',
                    'details': 'Browsing',
                    'state': 'YouTube Music',
                    'large_image': 'web_browser',
                    'large_text': 'On YouTube Music'
                }

        elif 'discord.com' in hostname:
            t = raw.replace('[discord.com]', '').replace('Discord |', '').replace('|', ' — ')
            t = t.replace('— Discord', '').replace(' - Discord', '').strip()
            
            channel_info = self.clean(t[:100])
            
            return {
                'name': 'Discord Web',
                'details': f'In {channel_info}',
                'state': 'On Discord',
                'large_image': 'web_browser',
                'large_text': 'On Discord Web'
            }

        elif 'spotify.com' in hostname:
            t = self.strip_parens(raw)
            return {
                'name': 'Spotify',
                'details': self.clean(t)[:128],
                'state': f'Listening ({currentTime}/{duration})',
                'large_image': 'web_browser',
                'large_text': 'Listening to Spotify'
            }

        else:
            site_name = hostname.split('.')[0].capitalize()
            t = raw.replace(f' - {site_name}', '')
            t = self.strip_parens(t)
            return {
                'name': site_name,
                'details': self.clean(t)[:128],
                'state': 'Browsing',
                'large_image': 'web_browser',
                'large_text': f'On {site_name}'
            }

    def store_browser_data(self, title, url, chapter='', channel='', currentTime='0:00', duration='0:00'):
        activity = self.build_activity_browser(title, url, chapter, channel, currentTime, duration)
        self.browser_data = activity
        self.browser_timestamp = time.time()

    def get_active_activity(self):
        current_time = time.time()
        
        window_title, exe_name = self.get_active_window_info()
        if window_title and exe_name and not self.is_browser_window(exe_name):
            window_activity = self.build_activity_from_window(window_title, exe_name)
            if window_activity:
                self.active_window_data = window_activity
                self.active_window_timestamp = current_time
                return window_activity
        
        if self.browser_data and (current_time - self.browser_timestamp) < 10:
            return self.browser_data
        
        if self.active_window_data and (current_time - self.active_window_timestamp) < 10:
            return self.active_window_data

        return None

    def update_rpc(self):
        if not self.rpc:
            return

        activity = self.get_active_activity()

        if activity is None:
            if self.last_rpc_state is not None:
                self.rpc.clear()
                self.last_rpc_state = None
            return

        if activity['name'] in ['YouTube', 'YouTube Music']:
            self.start_time = int(time.time())
            rpc_data = {
                'details': activity['details'],
                'state': activity['state'],
                'large_image': activity.get('large_image', 'desktop'),
                'large_text': activity.get('large_text', 'Activity'),
                'start': self.start_time
            }
            try:
                self.rpc.update(**rpc_data)
                print(f"✅ {activity['name']} | {activity['state']}")
            except Exception as e:
                print(f"❌ Error: {e}")
            return
        
        if activity['name'] in ['Discord', 'Discord Web']:
            self.start_time = int(time.time())
            rpc_data = {
                'details': activity['details'],
                'state': activity['state'],
                'large_image': activity.get('large_image', 'desktop'),
                'large_text': activity.get('large_text', 'Activity'),
                'start': self.start_time
            }
            try:
                self.rpc.update(**rpc_data)
                print(f"✅ {activity['name']} | {activity['details']}")
            except Exception as e:
                print(f"❌ Error: {e}")
            return
        
        current_state = f"{activity['state']}"
        if current_state == self.last_rpc_state:
            return
        
        self.last_rpc_state = current_state
        self.start_time = int(time.time())

        rpc_data = {
            'details': activity['details'],
            'state': activity['state'],
            'large_image': activity.get('large_image', 'desktop'),
            'large_text': activity.get('large_text', 'Activity'),
            'start': self.start_time
        }

        try:
            self.rpc.update(**rpc_data)
            print(f"✅ {activity['name']} | {activity['state']}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def monitor_loop(self):
        while True:
            try:
                self.update_rpc()
            except Exception as e:
                pass
            time.sleep(0.1)

    def start_monitor(self):
        if not self.window_monitor_running:
            self.window_monitor_running = True
            threading.Thread(target=self.monitor_loop, daemon=True).start()


server = DiscordRPCServer()


@flask_app.route('/update', methods=['POST'])
def update_activity():
    try:
        data = request.json
        title = data.get('title', '')
        url = data.get('url', '')
        chapter = data.get('chapter', '')
        channel = data.get('channel', '')
        currentTime = data.get('currentTime', '0:00')
        duration = data.get('duration', '0:00')

        if not title or not url:
            return jsonify({'success': False}), 400

        server.store_browser_data(title, url, chapter, channel, currentTime, duration)
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False}), 500


@flask_app.route('/status', methods=['GET'])
def status():
    return jsonify({'success': True, 'connected': server.rpc is not None})


def main():
    print("=" * 60)
    print("Discord RPC - Universal Monitor")
    print("=" * 60)
    print()

    if not server.connect_rpc():
        print("Start Discord Desktop first!")
        input("Press Enter to exit...")
        return

    server.start_bio_updater()
    server.start_monitor()

    print("✅ Ready - All features enabled")
    print(f"✅ Discord blocklist: {BLOCKED_DISCORD}")
    print("✅ Discord PC + Web channel updates")
    print()

    flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
