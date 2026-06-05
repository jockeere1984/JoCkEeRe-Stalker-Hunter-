[app]
title = JoCkEeRe IPTV
package.name = jockiptvplayer
package.domain = org.jockeere
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,requests,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30
android.build_tools = 30.0.3
android.accept_sdk_license = True
android.archs = arm64-v8a
android.gradle_dependencies = 'androidx.recyclerview:recyclerview:1.2.1'

[buildozer]
log_level = 2
warn_on_root = 1
