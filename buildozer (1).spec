[app]
title = CENAD
package.name = cenad
package.domain = org.cenad

source.dir = .
source.include_exts = py,kv,png,jpg,sqlite,db,csv,json
source.include_patterns = assets/*,assets/icons/*,data/*,screens/*,screens/__init__.py

version = 1.0.0

requirements = python3,kivy==2.3.0,sqlite3,pandas,numpy,matplotlib,pillow,reportlab

orientation = portrait

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.ndk_api = 21

android.archs = armeabi-v7a

android.release_artifact = apk

android.icon.filename = %(source.dir)s/assets/cenad_icon.png
android.presplash.filename = %(source.dir)s/assets/cenad_icon.png
android.presplash_color = #0D1640

android.wakelock = False

log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
