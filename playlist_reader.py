#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JoCkEeRe Playlist Reader
Supports: M3U file, M3U URL, Xtream API, MAC Stalker (STB)
"""

import re
import requests
import json
import warnings
warnings.filterwarnings('ignore')

session = requests.Session()
session.verify = False


# ═══════════════════════════════════════════
# 1. M3U FILE / URL READER
# ═══════════════════════════════════════════

def parse_m3u_content(content):
    """Parse raw M3U text and return list of channels."""
    channels = []
    lines = content.strip().splitlines()
    current = {}
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF'):
            current = {}
            # Extract name
            name_match = re.search(r',(.+)$', line)
            if name_match:
                current['name'] = name_match.group(1).strip()
            # Extract attributes
            for attr in ['tvg-id', 'tvg-name', 'tvg-logo', 'group-title']:
                m = re.search(rf'{attr}="([^"]*)"', line, re.IGNORECASE)
                if m:
                    current[attr] = m.group(1)
        elif line and not line.startswith('#') and current:
            current['url'] = line
            channels.append(current)
            current = {}
    return channels


def read_m3u_file(filepath):
    """Read M3U from local file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        channels = parse_m3u_content(content)
        print(f"[M3U FILE] Found {len(channels)} channels from: {filepath}")
        return channels
    except Exception as e:
        print(f"[M3U FILE] Error: {e}")
        return []


def read_m3u_url(url, timeout=15):
    """Read M3U from URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 VLC/3.0.0'}
        resp = session.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        channels = parse_m3u_content(resp.text)
        print(f"[M3U URL] Found {len(channels)} channels from: {url}")
        return channels
    except Exception as e:
        print(f"[M3U URL] Error: {e}")
        return []


# ═══════════════════════════════════════════
# 2. XTREAM CODES API READER
# ═══════════════════════════════════════════

def read_xtream(host, username, password, timeout=15):
    """
    Connect to Xtream Codes API and return account info + streams.
    host: full URL like http://example.com:8080
    """
    result = {
        'info': {},
        'live': [],
        'vod': [],
        'series': [],
        'error': None
    }

    host = host.rstrip('/')

    # --- Account Info ---
    try:
        info_url = f"{host}/player_api.php?username={username}&password={password}"
        resp = session.get(info_url, timeout=timeout)
        data = resp.json()

        ui = data.get('user_info', {})
        si = data.get('server_info', {})

        import datetime
        exp_raw = ui.get('exp_date')
        if exp_raw and exp_raw != 'null' and exp_raw is not None:
            try:
                exp_date = datetime.datetime.fromtimestamp(int(exp_raw)).strftime('%Y-%m-%d')
            except:
                exp_date = str(exp_raw)
        else:
            exp_date = 'Unlimited'

        result['info'] = {
            'username'    : ui.get('username', username),
            'password'    : ui.get('password', password),
            'status'      : ui.get('status', '?'),
            'exp_date'    : exp_date,
            'active_cons' : ui.get('active_connections', '?'),
            'max_cons'    : ui.get('max_connections', '?'),
            'server_url'  : si.get('url', host),
            'port'        : si.get('port', '?'),
            'timezone'    : si.get('timezone', '?'),
        }

        print(f"[XTREAM] Status: {result['info']['status']} | Exp: {result['info']['exp_date']}")

    except Exception as e:
        result['error'] = f"Info error: {e}"
        print(f"[XTREAM] Error fetching info: {e}")
        return result

    # --- Live Streams ---
    try:
        live_url = f"{host}/player_api.php?username={username}&password={password}&action=get_live_streams"
        resp = session.get(live_url, timeout=timeout)
        streams = resp.json()
        result['live'] = [
            {
                'name'       : s.get('name', ''),
                'stream_id'  : s.get('stream_id', ''),
                'category_id': s.get('category_id', ''),
                'url'        : f"{host}/live/{username}/{password}/{s.get('stream_id', '')}.m3u8"
            }
            for s in streams
        ]
        print(f"[XTREAM] Live streams: {len(result['live'])}")
    except Exception as e:
        print(f"[XTREAM] Live streams error: {e}")

    # --- VOD ---
    try:
        vod_url = f"{host}/player_api.php?username={username}&password={password}&action=get_vod_streams"
        resp = session.get(vod_url, timeout=timeout)
        vods = resp.json()
        result['vod'] = [
            {
                'name'      : v.get('name', ''),
                'stream_id' : v.get('stream_id', ''),
                'url'       : f"{host}/movie/{username}/{password}/{v.get('stream_id', '')}.mp4"
            }
            for v in vods
        ]
        print(f"[XTREAM] VOD: {len(result['vod'])}")
    except Exception as e:
        print(f"[XTREAM] VOD error: {e}")

    return result


# ═══════════════════════════════════════════
# 3. MAC STALKER / STB READER
# ═══════════════════════════════════════════

def stb_headers(mac, token=None, panel=None, useragent="Mozilla/5.0"):
    h = {
        "User-Agent"    : useragent,
        "Accept"        : "application/json, application/javascript, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Cookie"        : f"mac={mac}; stb_lang=en; timezone=Europe%2FLondon;",
        "X-User-Agent"  : "Model: MAG254; Link: Ethernet",
        "Connection"    : "keep-alive",
    }
    if panel:
        h["Referer"] = f"http://{panel}/c/"
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def stb_get_token(panel, mac, timeout=10):
    """Get authentication token from STB portal."""
    try:
        url = (f"http://{panel}/portal.php?type=stb"
               f"&action=handshake&token=&JsHttpRequest=1-xml")
        resp = session.get(url, headers=stb_headers(mac, panel=panel), timeout=timeout)
        data = resp.json()
        token = data.get('js', {}).get('token', '')
        if token:
            print(f"[STB] Token obtained: {token[:20]}...")
            return token
    except Exception as e:
        print(f"[STB] Token error: {e}")
    return None


def stb_get_account_info(panel, mac, token, timeout=10):
    """Get account info from STB portal."""
    try:
        url = (f"http://{panel}/portal.php?type=account_info"
               f"&action=get_main_info&JsHttpRequest=1-xml")
        resp = session.get(url, headers=stb_headers(mac, token, panel), timeout=timeout)
        data = resp.json()
        js   = data.get('js', {})

        phone    = js.get('phone', '')
        fname    = js.get('fname', '')
        exp_raw  = js.get('end_date', '')

        return {
            'mac'     : mac,
            'fname'   : fname,
            'phone'   : phone,
            'exp_date': exp_raw,
            'token'   : token,
        }
    except Exception as e:
        print(f"[STB] Account info error: {e}")
        return {}


def stb_get_profile(panel, mac, token, timeout=10):
    """Get full profile including expiry from STB."""
    try:
        url = (f"http://{panel}/portal.php?type=stb"
               f"&action=get_profile&hd=1&ver=ImageDescription:0.2.18-r23-pub"
               f"&num_banks=2&sn=00000000000000&stb_type=MAG254"
               f"&device_id=000000000000&device_id2=000000000000"
               f"&signature=000000000000000000000000000000000000000000000000000000000000"
               f"&JsHttpRequest=1-xml")
        resp = session.get(url, headers=stb_headers(mac, token, panel), timeout=timeout)
        data = resp.json()
        js   = data.get('js', {})

        exp_raw  = js.get('end_date', '')
        status   = js.get('status', '')
        tariff   = js.get('tariff_expired_date', '')

        return {
            'status'  : status,
            'exp_date': exp_raw or tariff,
            'raw'     : js,
        }
    except Exception as e:
        print(f"[STB] Profile error: {e}")
        return {}


def stb_get_channels(panel, mac, token, timeout=15):
    """Get all channels from STB portal."""
    channels = []
    try:
        # Get all genres first
        genre_url = (f"http://{panel}/portal.php?type=itv"
                     f"&action=get_genres&JsHttpRequest=1-xml")
        resp  = session.get(genre_url, headers=stb_headers(mac, token, panel), timeout=timeout)
        genres = resp.json().get('js', [])

        for genre in genres:
            gid   = genre.get('id', '*')
            gname = genre.get('title', 'Unknown')

            ch_url = (f"http://{panel}/portal.php?type=itv"
                      f"&action=get_ordered_list&genre={gid}"
                      f"&force_ch_link_check=&fav=0&sortby=number"
                      f"&hd=0&p=1&JsHttpRequest=1-xml")
            try:
                r    = session.get(ch_url, headers=stb_headers(mac, token, panel), timeout=timeout)
                data = r.json().get('js', {})
                for ch in data.get('data', []):
                    cid  = ch.get('id', '')
                    cmd  = ch.get('cmd', '').replace('ffmpeg ', '')
                    name = ch.get('name', '')
                    channels.append({
                        'id'      : cid,
                        'name'    : name,
                        'group'   : gname,
                        'cmd'     : cmd,
                    })
            except:
                pass

        print(f"[STB] Channels found: {len(channels)}")
    except Exception as e:
        print(f"[STB] Channels error: {e}")

    return channels


def read_mac_stalker(panel, mac, timeout=10):
    """
    Full MAC Stalker scan.
    panel: host:port like example.com:8080
    mac: MAC address like 00:1A:79:xx:xx:xx
    """
    result = {
        'panel'   : panel,
        'mac'     : mac,
        'token'   : None,
        'info'    : {},
        'profile' : {},
        'channels': [],
        'error'   : None,
    }

    # Step 1: Get token
    token = stb_get_token(panel, mac, timeout)
    if not token:
        result['error'] = 'Failed to get token'
        return result
    result['token'] = token

    # Step 2: Get account info
    result['info'] = stb_get_account_info(panel, mac, token, timeout)

    # Step 3: Get profile
    result['profile'] = stb_get_profile(panel, mac, token, timeout)

    # Step 4: Get channels
    result['channels'] = stb_get_channels(panel, mac, token, timeout)

    return result


# ═══════════════════════════════════════════
# 4. AUTO DETECT & READ ANY FORMAT
# ═══════════════════════════════════════════

def auto_read(source):
    """
    Auto-detect format and read playlist.
    source can be:
      - Local file path (.m3u or .m3u8)
      - M3U URL (http://.../*.m3u or ?type=m3u...)
      - Xtream dict: {'type':'xtream','host':...,'user':...,'pass':...}
      - STB dict:    {'type':'stalker','panel':...,'mac':...}
    """
    if isinstance(source, dict):
        t = source.get('type', '').lower()
        if t == 'xtream':
            return read_xtream(source['host'], source['user'], source['pass'])
        elif t == 'stalker':
            return read_mac_stalker(source['panel'], source['mac'])
        else:
            return {'error': 'Unknown dict type'}

    if isinstance(source, str):
        # Local file
        if source.endswith('.m3u') or source.endswith('.m3u8') or source.startswith('/') or '\\' in source:
            return read_m3u_file(source)

        # URL
        if source.startswith('http'):
            # Xtream get.php format
            if 'get.php' in source or 'type=m3u' in source:
                return read_m3u_url(source)
            # Xtream player_api
            if 'player_api' in source:
                # Extract from URL
                m = re.search(r'username=([^&]+)&password=([^&]+)', source)
                host = source.split('/player_api')[0]
                if m:
                    return read_xtream(host, m.group(1), m.group(2))
            # Default: treat as M3U URL
            return read_m3u_url(source)

    return {'error': 'Unrecognized source format'}


# ═══════════════════════════════════════════
# 5. DEMO / TEST
# ═══════════════════════════════════════════

if __name__ == '__main__':

    print("=" * 50)
    print("  JoCkEeRe Playlist Reader - TEST MODE")
    print("=" * 50)

    # --- Test M3U URL ---
    # channels = read_m3u_url("http://example.com/playlist.m3u")
    # print(channels[:3])

    # --- Test Xtream ---
    # result = read_xtream("http://example.com:8080", "user", "pass")
    # print(result['info'])
    # print(f"Live: {len(result['live'])}")

    # --- Test MAC Stalker ---
    # result = read_mac_stalker("example.com:8080", "00:1A:79:AA:BB:CC")
    # print(result['info'])
    # print(f"Channels: {len(result['channels'])}")

    # --- Auto detect ---
    # result = auto_read({'type':'xtream','host':'http://example.com:8080','user':'test','pass':'test'})
    # result = auto_read({'type':'stalker','panel':'example.com:8080','mac':'00:1A:79:AA:BB:CC'})
    # result = auto_read("http://example.com/list.m3u")

    print("\nAll functions loaded successfully!")
    print("Use auto_read() for automatic format detection.")
