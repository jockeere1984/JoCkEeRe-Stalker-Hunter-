[app]

title = JoCkEeRe Ultra Scanner
package.name = jockeere
package.domain = org.jockeere

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 2.0

requirements = python3,kivy==2.3.0,requests,urllib3,certifi,charset-normalizer,idna,plyer

orientation = portrait

android.minapi = 21
android.api = 33
android.build_tools_version = 33.0.2
android.ndk = 25b
android.sdk = 33
android.build_tools_version = 33.0.2

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,VIBRATE,ACCESS_NETWORK_STATE

android.archs = armeabi-v7a

android.release_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
