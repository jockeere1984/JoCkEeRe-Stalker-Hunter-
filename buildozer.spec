[app]
title = JoCkEeRe IPTV
package.name = iptvplayer
package.domain = org.jockeere
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,requests,jnius,android,pyjnius
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0
fullscreen = 0
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.build_tools = 33.0.2
android.archs = arm64-v8a, armeabi-v7a
android.gradle_dependencies = 'androidx.recyclerview:recyclerview:1.2.1'
android.add_src = 

[buildozer]
log_level = 2
warn_on_root = 1
