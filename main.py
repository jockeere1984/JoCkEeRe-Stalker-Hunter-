# -*- coding: utf-8 -*-
# JoCkEeRe IPTV Player - نسخة Android (بدون متصفح، فقط مشغل فيديو)
import requests
import threading
import os
import re
import time
import random
import string
import datetime
from urllib.parse import urlparse, parse_qs
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# ========== الألوان ==========
COLORS = {
    'bg_main': get_color_from_hex('#0a0f1c'),
    'bg_spinner': get_color_from_hex('#2c3e66'),
    'bg_card': get_color_from_hex('#1e2740'),
    'bg_input': get_color_from_hex('#0f1422'),
    'bg_popup': get_color_from_hex('#1a1f2e'),
    'text_light': get_color_from_hex('#ffffff'),
    'text_muted': get_color_from_hex('#9aa8c5'),
    'accent': get_color_from_hex('#00d4ff'),
    'accent2': get_color_from_hex('#9d4edd'),
    'success': get_color_from_hex('#06d6a0'),
    'warning': get_color_from_hex('#ffb703'),
    'danger': get_color_from_hex('#ef476f'),
}

Window.clearcolor = COLORS['bg_main']

# ========== التحقق من توفر jnius على Android ==========
try:
    from jnius import autoclass
    JNIUS_AVAILABLE = True
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
    except:
        PythonActivity = None
except ImportError:
    JNIUS_AVAILABLE = False
    autoclass = None
    PythonActivity = None

def rand_str(n=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

class IPTVPlayer(App):
    def build(self):
        self.channels = []
        self.categories = []
        self.current_channels = []
        self.current_title = ""
        self.selected_file_path = None
        self.current_view = 'categories'

        layout = BoxLayout(orientation='vertical', padding=[15, 35, 15, 15], spacing=12)

        title = Label(text='JoCkEeRe IPTV Player', font_size='22sp', color=COLORS['accent'], size_hint_y=None, height=55)
        layout.add_widget(title)

        self.source_spinner = Spinner(text='Select source', values=('M3U URL', 'Local .m3u file', 'Xtream Codes', 'Stalker Portal (MAC)'), size_hint=(1, None), height=70, background_normal='', background_color=COLORS['bg_spinner'], color=COLORS['text_light'], font_size='16sp')
        self.source_spinner.bind(text=self.on_source_change)
        layout.add_widget(self.source_spinner)

        self.input_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        self.input_container.bind(minimum_height=self.input_container.setter('height'))
        layout.add_widget(self.input_container)

        self.url_input = None
        self.load_btn = None
        self.xtream_url = None
        self.xtream_user = None
        self.xtream_pass = None
        self.xtream_btn = None
        self.select_file_btn = None
        self.load_local_btn = None
        self.file_info_label = None
        self.stalker_portal_input = None
        self.stalker_mac_input = None
        self.stalker_connect_btn = None

        search_box = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.back_button = Button(text='◀ Back', size_hint_x=0.2, background_normal='', background_color=COLORS['bg_card'], color=COLORS['text_light'], font_size='16sp', disabled=True)
        self.back_button.bind(on_press=self.go_back)
        self.search_input = TextInput(text='', hint_text='Search channel...', multiline=False, font_size='16sp', background_color=COLORS['bg_input'], foreground_color=COLORS['text_light'], cursor_color=COLORS['accent'])
        self.search_btn = Button(text='Search', size_hint_x=0.25, disabled=True, font_size='16sp', background_normal='', background_color=COLORS['success'], color=COLORS['text_light'])
        self.search_btn.bind(on_press=self.search_channels)
        search_box.add_widget(self.back_button)
        search_box.add_widget(self.search_input)
        search_box.add_widget(self.search_btn)
        layout.add_widget(search_box)

        header_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.header_label = Label(text='Categories', font_size='18sp', color=COLORS['accent'], bold=True, size_hint_x=0.8)
        self.save_btn = Button(text='💾 Save M3U', size_hint_x=0.2, background_normal='', background_color=COLORS['success'], color=COLORS['text_light'], font_size='14sp', disabled=True)
        self.save_btn.bind(on_press=self.save_channels_to_m3u)
        header_box.add_widget(self.header_label)
        header_box.add_widget(self.save_btn)
        layout.add_widget(header_box)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)

        self.status = Label(text='Ready', size_hint_y=None, height=40, font_size='12sp', color=COLORS['text_muted'])
        layout.add_widget(self.status)

        if JNIUS_AVAILABLE and PythonActivity:
            self.request_permissions()

        return layout

    def request_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        except Exception as e:
            print("Permissions error:", e)

    def update_save_button_state(self):
        self.save_btn.disabled = len(self.channels) == 0

    def save_channels_to_m3u(self, instance):
        if not self.channels:
            self.update_status("No channels to save")
            return
        portal_url = ""
        source_text = self.source_spinner.text
        if source_text == 'Stalker Portal (MAC)':
            portal_url = self.stalker_portal_input.text.strip()
        elif source_text == 'Xtream Codes':
            portal_url = self.xtream_url.text.strip()
        elif source_text == 'M3U URL':
            portal_url = self.url_input.text.strip()
        url_part = "playlist"
        if portal_url:
            parsed = urlparse(portal_url)
            netloc = parsed.netloc or portal_url.split('/')[0]
            safe_netloc = netloc.replace(':', '-').replace('.', '_').replace('/', '_')
            url_part = safe_netloc
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"{url_part}_{date_str}.m3u"
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        filename_input = TextInput(text=default_filename, multiline=False, font_size='16sp', background_color=COLORS['bg_input'], foreground_color=COLORS['text_light'])
        content.add_widget(Label(text='Enter filename:', color=COLORS['text_light'], size_hint_y=None, height=30))
        content.add_widget(filename_input)
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text='Cancel', background_normal='', background_color=COLORS['danger'], color=COLORS['text_light'])
        save_btn = Button(text='Save', background_normal='', background_color=COLORS['success'], color=COLORS['text_light'])
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        content.add_widget(btn_layout)
        popup = Popup(title='Save M3U File', content=content, size_hint=(0.8, 0.4), background_color=COLORS['bg_popup'])
        def do_save(btn):
            filename = filename_input.text.strip()
            if not filename.endswith('.m3u'):
                filename += '.m3u'
            popup.dismiss()
            self.save_file_to_downloads(filename)
        def do_cancel(btn):
            popup.dismiss()
        save_btn.bind(on_press=do_save)
        cancel_btn.bind(on_press=do_cancel)
        popup.open()

    def save_file_to_downloads(self, filename):
        try:
            alt_dir = os.path.join(self.user_data_dir, "IPTV_Playlists")
            os.makedirs(alt_dir, exist_ok=True)
            full_path = os.path.join(alt_dir, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(self.generate_m3u_content())
            self.update_status(f"Saved to {full_path}")
        except Exception as e:
            self.update_status(f"Error saving: {e}")

    def generate_m3u_content(self):
        m3u_content = "#EXTM3U\n"
        for idx, ch in enumerate(self.channels, start=1):
            name = ch.get('name', f'Channel {idx}')
            url = ch.get('url', '')
            m3u_content += f'#EXTINF:-1,{name}\n{url}\n'
        return m3u_content

    def go_back(self, instance):
        if self.current_view != 'categories':
            self.show_categories()
            self.current_view = 'categories'
            self.back_button.disabled = True
            self.search_btn.disabled = False if self.channels else True

    def on_source_change(self, spinner, text):
        self.input_container.clear_widgets()
        if text == 'M3U URL':
            self.url_input = TextInput(text='', hint_text='Enter M3U playlist URL...', multiline=False, font_size='16sp', size_hint_y=None, height=60, background_color=COLORS['bg_input'], foreground_color=COLORS['text_light'], cursor_color=COLORS['accent'])
            self.load_btn = Button(text='Load Channels', size_hint_y=None, height=60, font_size='16sp', background_normal='', background_color=COLORS['warning'], color=COLORS['text_light'])
            self.load_btn.bind(on_press=self.start_load_from_url)
            self.input_container.add_widget(self.url_input)
            self.input_container.add_widget(self.load_btn)
        elif text == 'Local .m3u file':
            self.select_file_btn = Button(text='📂 Choose M3U File', size_hint_y=None, height=60, background_normal='', background_color=COLORS['warning'], color=COLORS['text_light'])
            self.select_file_btn.bind(on_press=self.open_file_chooser)
            self.file_info_label = Label(text='No file selected', size_hint_y=None, height=50, color=COLORS['text_muted'], font_size='14sp')
            self.load_local_btn = Button(text='Load Selected File', size_hint_y=None, height=80, disabled=True, background_normal='', background_color=COLORS['warning'], color=COLORS['text_light'])
            self.load_local_btn.bind(on_press=self.load_selected_file)
            self.input_container.add_widget(self.select_file_btn)
            self.input_container.add_widget(self.file_info_label)
            self.input_container.add_widget(self.load_local_btn)
        elif text == 'Xtream Codes':
            xtream_layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
            xtream_layout.bind(minimum_height=xtream_layout.setter('height'))
            self.xtream_url = TextInput(text='', hint_text='Portal URL (e.g. http://example.com:8080)', multiline=False, font_size='16sp', size_hint_y=None, height=55, background_color=COLORS['bg_input'], foreground_color=COLORS['text_light'], cursor_color=COLORS['accent'])
            xtream_layout.add_widget(self.xtream_url)
            self.xtream_user = TextInput(text='', hint_text='Username', multiline=False, font_size='16sp', size_hint_y=None, height=55, background_color=COLORS['bg_input'], foreground_color=COLORS['text_light'], cursor_color=COLORS['accent'])
            xtream_layout.add_widget(self.xtream_user)
            self.xtream_pass = TextInput(text='', hint_text='Password', multiline=False, password=True, font_size='16sp', size_hint_y=None, height=55, background_color=COLORS['bg_input'], foreground_color=COLORS['text_light'], cursor_color=COLORS['accent'])
            xtream_layout.add_widget(self.xtream_pass)
            self.xtream_btn = Button(text='Load Channels', size_hint_y=None, height=80, background_normal='', background_color=COLORS['warning'], color=COLORS['text_light'])
            self.xtream_btn.bind(on_press=self.start_load_xtream)
            xtream_layout.add_widget(self.xtream_btn)
            xtream_layout.padding = [0, 0, 0, 20]
            self.input_container.add_widget(xtream_layout)
        elif text == 'Stalker Portal (MAC)':
            stalker_layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
            stalker_layout.bind(minimum_height=stalker_layout.setter('height'))
            self.stalker_portal_input = TextInput(text='', hint_text='Portal URL (e.g. http://exemple.me:80)', multiline=False, font_size='16sp', size_hint_y=None, height=55, background_color=COLORS['bg_input'], foreground_color=COLORS['text_light'], cursor_color=COLORS['accent'])
            stalker_layout.add_widget(self.stalker_portal_input)
            self.stalker_mac_input = TextInput(text='', hint_text='MAC Address (XX:XX:XX:XX:XX:XX)', multiline=False, font_size='16sp', size_hint_y=None, height=55, background_color=COLORS['bg_input'], foreground_color=COLORS['text_light'], cursor_color=COLORS['accent'])
            stalker_layout.add_widget(self.stalker_mac_input)
            self.stalker_connect_btn = Button(text='Connect & Load Channels', size_hint_y=None, height=80, background_normal='', background_color=COLORS['warning'], color=COLORS['text_light'])
            self.stalker_connect_btn.bind(on_press=self.start_load_stalker)
            stalker_layout.add_widget(self.stalker_connect_btn)
            stalker_layout.padding = [0, 0, 0, 20]
            self.input_container.add_widget(stalker_layout)

    def start_load_stalker(self, instance):
        portal = self.stalker_portal_input.text.strip()
        portal = portal.rstrip('/')
        if portal.endswith('/c'):
            portal = portal[:-2]
        elif portal.endswith('/c/'):
            portal = portal[:-3]
        if not portal.startswith('http'):
            portal = 'http://' + portal
        mac = self.stalker_mac_input.text.strip().upper()
        if ':' not in mac and len(mac) == 12:
            mac = ':'.join(mac[i:i+2] for i in range(0,12,2))
        if not re.match(r'^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$', mac):
            self.update_status('Invalid MAC format. Use XX:XX:XX:XX:XX:XX')
            return
        if not portal:
            self.update_status('Please enter Portal URL')
            return
        self.stalker_portal_input.text = portal
        self.stalker_mac_input.text = mac
        self.stalker_connect_btn.disabled = True
        self.search_btn.disabled = True
        self.update_status(f'Connecting to {portal} with MAC {mac}...')
        threading.Thread(target=self.fetch_stalker_data, args=(portal, mac)).start()

    def fetch_stalker_data(self, portal, mac):
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) MAG200'})
        sn = rand_str(10)
        device_id = rand_str(8)
        possible_paths = [f"{portal}/c/server/load.php", f"{portal}/server/load.php", f"{portal}/stalker_portal/server/load.php", f"{portal}/load.php"]
        token = None
        used_url = None
        for base_url in possible_paths:
            try:
                params = {'type': 'stb', 'action': 'handshake', 'mac': mac, 'sn': sn, 'device_id': device_id}
                r = session.get(base_url, params=params, timeout=10)
                if r.status_code == 200 and 'token' in r.text:
                    match = re.search(r'"token":"([^"]+)"', r.text)
                    if match:
                        token = match.group(1)
                        used_url = base_url
                        break
            except:
                continue
        if not token:
            self.update_status('Handshake failed: no working portal path. Check URL and MAC.')
            self.enable_buttons()
            return
        self.update_status(f'Connected. Fetching channels...')
        try:
            params = {'type': 'itv', 'action': 'get_all_channels', 'mac': mac, 'token': token, 'sn': sn, 'device_id': device_id}
            r = session.get(used_url, params=params, timeout=30)
            if r.status_code == 429:
                time.sleep(3)
                r = session.get(used_url, params=params, timeout=30)
            try:
                data = r.json()
            except:
                raw_preview = r.text[:200]
                self.update_status(f"Response not JSON: {raw_preview}")
                return
            channels_list = []
            if isinstance(data, list):
                channels_list = data
            elif isinstance(data, dict):
                channels_list = data.get('js', {}).get('data', [])
                if not channels_list:
                    channels_list = data.get('data', [])
                if not channels_list:
                    channels_list = data.get('js', [])
                if not channels_list:
                    js_data = data.get('js', {})
                    if isinstance(js_data, dict):
                        for k, v in js_data.items():
                            if isinstance(v, list) and len(v) > 0:
                                channels_list = v
                                break
            if not channels_list:
                self.update_status("No channels array found in response")
                return
            genre_map = {}
            try:
                params_genre = {'type': 'itv', 'action': 'get_genres', 'mac': mac, 'token': token, 'sn': sn, 'device_id': device_id}
                r_genre = session.get(used_url, params=params_genre, timeout=10)
                if r_genre.status_code == 200:
                    genre_data = r_genre.json()
                    if isinstance(genre_data, list):
                        genre_list = genre_data
                    elif isinstance(genre_data, dict):
                        genre_list = genre_data.get('js', [])
                    else:
                        genre_list = []
                    for g in genre_list:
                        if isinstance(g, dict):
                            gid = str(g.get('id', ''))
                            name = g.get('title') or g.get('name')
                            if gid and name:
                                genre_map[gid] = name
            except:
                pass
            self.channels = []
            seen_cats = set()
            self.categories = []
            for ch in channels_list:
                if not isinstance(ch, dict):
                    continue
                name = ch.get('name', 'No name')
                url = ch.get('cmd', '')
                if url.startswith('ffmpeg '):
                    url = url[7:]
                url = url.replace('\\/', '/')
                genre_id = str(ch.get('tv_genre_id', ''))
                genre_name = genre_map.get(genre_id, ch.get('tv_genre', f'Genre {genre_id}' if genre_id else 'Uncategorized'))
                self.channels.append({'name': name, 'url': url, 'category': genre_id if genre_id else 'uncat', 'category_name': genre_name})
                if genre_id and genre_id not in seen_cats:
                    self.categories.append({'id': genre_id, 'title': genre_name})
                    seen_cats.add(genre_id)
                elif not genre_id and 'uncat' not in seen_cats:
                    self.categories.append({'id': 'uncat', 'title': 'Uncategorized'})
                    seen_cats.add('uncat')
            if not self.channels:
                self.update_status("No valid channels extracted from response")
                return
            self.categories.sort(key=lambda x: x['title'])
            self.categories.insert(0, {'id': 'all', 'title': '📺 All Channels'})
            self.update_status(f'Loaded {len(self.channels)} channels, {len(self.categories)-1} categories (Stalker)')
            Clock.schedule_once(lambda dt: self.show_categories(), 0)
            Clock.schedule_once(lambda dt: self.enable_buttons(), 0)
            Clock.schedule_once(lambda dt: self.update_save_button_state(), 0)
        except Exception as e:
            self.update_status(f'Channels error: {e}')
            self.enable_buttons()

    def is_xtream_m3u_url(self, url):
        if 'get.php' not in url:
            return False
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if 'username' in query and 'password' in query:
            return True
        return 'username=' in url and 'password=' in url

    def extract_xtream_params(self, url):
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        query = parse_qs(parsed.query)
        username = query.get('username', [None])[0]
        password = query.get('password', [None])[0]
        if username and password:
            return base, username, password
        match = re.search(r'username=([^&]+)&password=([^&]+)', url)
        if match:
            return base, match.group(1), match.group(2)
        return None, None, None

    def load_xtream_api(self, portal, username, password, source_desc=""):
        try:
            cat_url = f"{portal}/player_api.php?username={username}&password={password}&action=get_live_categories"
            r_cat = requests.get(cat_url, timeout=15)
            categories = []
            if r_cat.status_code == 200:
                try:
                    cats = r_cat.json()
                    for cat in cats:
                        categories.append({'category_id': str(cat.get('category_id')), 'category_name': cat.get('category_name')})
                except:
                    pass
            streams_url = f"{portal}/player_api.php?username={username}&password={password}&action=get_live_streams"
            r_str = requests.get(streams_url, timeout=30)
            channels = []
            if r_str.status_code == 200:
                try:
                    streams = r_str.json()
                    for stream in streams:
                        channels.append({'name': stream.get('name'), 'stream_id': stream.get('stream_id'), 'category_id': str(stream.get('category_id'))})
                except:
                    pass
            if not channels:
                self.update_status('API returned no channels, trying M3U fallback...')
                m3u_url = f"{portal}/get.php?username={username}&password={password}&type=m3u_plus&output=ts"
                self.load_m3u_raw(m3u_url)
                return
            self.categories = [{'id': 'all', 'title': '📺 All Channels'}]
            for cat in categories:
                self.categories.append({'id': cat['category_id'], 'title': cat['category_name']})
            self.channels = []
            for ch in channels:
                self.channels.append({'name': ch['name'], 'url': f"{portal}/live/{username}/{password}/{ch['stream_id']}.ts", 'category': ch['category_id']})
            self.update_status(f'Loaded {len(self.channels)} channels, {len(self.categories)-1} categories {source_desc}')
            Clock.schedule_once(lambda dt: self.show_categories(), 0)
            Clock.schedule_once(lambda dt: self.enable_buttons(), 0)
            Clock.schedule_once(lambda dt: self.update_save_button_state(), 0)
        except Exception as e:
            self.update_status(f'API error: {e}, falling back to M3U...')
            m3u_url = f"{portal}/get.php?username={username}&password={password}&type=m3u_plus&output=ts"
            self.load_m3u_raw(m3u_url)

    def load_m3u_raw(self, url):
        try:
            r = requests.get(url, timeout=15)
            r.encoding = 'utf-8'
            self.process_m3u_content(r.text, url)
        except Exception as e:
            self.update_status(f'Error: {e}')
        finally:
            Clock.schedule_once(lambda dt: self.enable_buttons(), 0)

    def process_m3u_content(self, content, source):
        lines = content.splitlines()
        categories_dict = {}
        channels = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('#EXTINF:'):
                category = 'Uncategorized'
                match = re.search(r'group-title="([^"]+)"', line)
                if match:
                    category = match.group(1).strip()
                if ',' in line:
                    name = line.split(',', 1)[1].strip()
                else:
                    name = 'Unnamed'
                if i + 1 < len(lines):
                    url_line = lines[i + 1].strip()
                    if url_line and not url_line.startswith('#'):
                        channels.append({'name': name, 'url': url_line, 'category': category})
                        if category not in categories_dict:
                            categories_dict[category] = True
                        i += 1
            i += 1
        self.categories = [{'id': 'all', 'title': '📺 All Channels'}]
        for cat in sorted(categories_dict.keys()):
            self.categories.append({'id': cat, 'title': cat})
        self.channels = channels
        if not self.channels:
            self.update_status('No channels found')
        else:
            self.update_status(f'Loaded {len(self.channels)} channels, {len(self.categories)-1} categories from {source}')
            Clock.schedule_once(lambda dt: self.show_categories(), 0)
            Clock.schedule_once(lambda dt: self.update_save_button_state(), 0)

    def start_load_from_url(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.update_status('Please enter a valid URL')
            return
        self.load_btn.disabled = True
        self.search_btn.disabled = True
        self.update_status('Checking URL type...')
        if self.is_xtream_m3u_url(url):
            portal, user, pwd = self.extract_xtream_params(url)
            if portal and user and pwd:
                self.update_status('Xtream M3U URL detected, switching to API mode...')
                threading.Thread(target=self.load_xtream_api, args=(portal, user, pwd, '(from M3U URL)')).start()
                return
        threading.Thread(target=self.load_m3u_raw, args=(url,)).start()

    def start_load_xtream(self, instance):
        url = self.xtream_url.text.strip()
        user = self.xtream_user.text.strip()
        pwd = self.xtream_pass.text.strip()
        if not url or not user or not pwd:
            self.update_status('All fields required')
            return
        self.xtream_btn.disabled = True
        self.search_btn.disabled = True
        self.update_status('Loading Xtream channels via API...')
        threading.Thread(target=self.load_xtream_api, args=(url, user, pwd, '')).start()

    def show_categories(self):
        self.grid.clear_widgets()
        self.header_label.text = '📁 Select Category:'
        self.header_label.color = COLORS['accent']
        for cat in self.categories:
            btn = Button(text=cat['title'], size_hint_y=None, height=55, font_size='16sp', background_normal='', background_color=COLORS['bg_card'], color=COLORS['text_light'])
            btn.cat_id = cat['id']
            btn.bind(on_press=self.show_channels)
            self.grid.add_widget(btn)
        self.current_view = 'categories'
        self.back_button.disabled = True
        self.update_save_button_state()

    def show_channels(self, btn):
        cat_id = btn.cat_id
        if cat_id == 'all':
            self.current_channels = self.channels[:]
            title = '📺 All Channels'
        else:
            self.current_channels = [ch for ch in self.channels if str(ch.get('category', '')) == cat_id]
            cat_title = next((c['title'] for c in self.categories if c['id'] == cat_id), cat_id)
            title = cat_title
        self.current_title = title
        self.display_channels(self.current_channels, title)
        self.current_view = 'channels'
        self.back_button.disabled = False
        self.update_save_button_state()

    def display_channels(self, channels_list, title):
        self.grid.clear_widgets()
        self.header_label.text = f'{title} (click to play):'
        self.header_label.color = COLORS['success']
        for ch in channels_list[:200]:
            name = ch.get('name', 'No name')
            url = ch.get('url', '')
            if url.startswith('ffmpeg '):
                url = url[7:]
            url = url.replace('\\/', '/')
            btn = Button(text=name, size_hint_y=None, height=55, font_size='15sp', background_normal='', background_color=COLORS['bg_card'], color=COLORS['text_light'])
            btn.stream_url = url
            btn.bind(on_press=self.play_channel_external)
            self.grid.add_widget(btn)
        if len(channels_list) > 200:
            more = Label(text=f'... and {len(channels_list)-200} more', size_hint_y=None, height=40, color=COLORS['text_muted'])
            self.grid.add_widget(more)
        back_btn = Button(text='<< Back to Categories', size_hint_y=None, height=50, font_size='15sp', background_normal='', background_color=COLORS['accent2'], color=COLORS['text_light'])
        back_btn.bind(on_press=lambda x: self.show_categories())
        self.grid.add_widget(back_btn)
        self.update_save_button_state()

    def search_channels(self, instance):
        query = self.search_input.text.strip().lower()
        if not query:
            self.display_channels(self.current_channels, self.current_title)
            return
        filtered = [ch for ch in self.current_channels if query in ch.get('name', '').lower()]
        if filtered:
            self.display_channels(filtered, f'🔍 "{query}" ({len(filtered)} found)')
            self.update_status(f'Found {len(filtered)} channels')
        else:
            self.grid.clear_widgets()
            self.header_label.text = f'❌ No results for "{query}"'
            self.header_label.color = COLORS['danger']
            self.update_status('No results')
            back_btn = Button(text='<< Back to Categories', size_hint_y=None, height=50, background_normal='', background_color=COLORS['accent2'], color=COLORS['text_light'])
            back_btn.bind(on_press=lambda x: self.show_categories())
            self.grid.add_widget(back_btn)
        self.update_save_button_state()

    # ========== دالة التشغيل النهائية (بدون متصفح) ==========
    def play_channel_external(self, btn):
        url = btn.stream_url
        if not url:
            self.update_status('No stream URL')
            return

        if not JNIUS_AVAILABLE or PythonActivity is None:
            self.update_status('Cannot play: Android intent not available')
            return

        try:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            intent = Intent(Intent.ACTION_VIEW)
            uri = Uri.parse(url)
            # تحديد نوع MIME كفيديو يمنع المتصفحات من الظهور (لأن معظم المتصفحات لا تعلن دعمها لهذا النوع)
            intent.setDataAndType(uri, "video/*")
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            PythonActivity.mActivity.startActivity(intent)
            self.update_status(f'Opening "{btn.text}" with video player...')
        except Exception as e:
            self.update_status(f'Failed to open: {e}')

    def open_file_chooser(self, instance):
        start_path = '/storage/emulated/0'
        if not os.path.exists(start_path):
            start_path = '/sdcard'
        if not os.path.exists(start_path):
            start_path = '.'
        file_chooser = FileChooserListView(path=start_path, filters=['*.m3u', '*.m3u8'], size_hint=(1, 1))
        file_chooser.background_color = COLORS['bg_input']
        select_btn = Button(text='✔ Select This File', size_hint_y=None, height=50, background_normal='', background_color=COLORS['success'], color=COLORS['text_light'])
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_layout.add_widget(file_chooser)
        popup_layout.add_widget(select_btn)
        popup = Popup(title='Choose M3U File', title_color=COLORS['accent'], content=popup_layout, size_hint=(0.9, 0.9), background_color=COLORS['bg_popup'])
        def on_select(btn):
            if file_chooser.selection:
                self.selected_file_path = file_chooser.selection[0]
                self.file_info_label.text = f'Selected: {os.path.basename(self.selected_file_path)}'
                self.load_local_btn.disabled = False
                self.update_status(f'File selected: {os.path.basename(self.selected_file_path)}')
                popup.dismiss()
            else:
                self.update_status('No file selected')
        select_btn.bind(on_press=on_select)
        popup.open()

    def load_selected_file(self, instance):
        if self.selected_file_path and os.path.exists(self.selected_file_path):
            self.update_status(f'Loading {self.selected_file_path}...')
            try:
                with open(self.selected_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.process_m3u_content(content, self.selected_file_path)
            except Exception as e:
                self.update_status(f'Error: {e}')
        else:
            self.update_status('Please select a file first')

    def enable_buttons(self):
        if self.load_btn:
            self.load_btn.disabled = False
        if self.xtream_btn:
            self.xtream_btn.disabled = False
        if self.stalker_connect_btn:
            self.stalker_connect_btn.disabled = False
        self.search_btn.disabled = False

    def update_status(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.status, 'text', msg), 0)

if __name__ == '__main__':
    IPTVPlayer().run()