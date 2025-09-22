[app]
title = ToOpen4
package.name = toopen4
package.domain = org.toopen
source.dir = .
source.include_exts = py,kv,json,png,ttf,mp3,wav,csv
fullscreen = 1
orientation = portrait
icon.filename = assets/icon.png
requirements = python3,kivy,kivymd,androidstorage4kivy,requests,gTTS,pydub,soundfile,numpy,pandas,Pillow
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO
android.api = 34
android.minapi = 23
android.sdk = 34
android.ndk = 25b
android.archs = armeabi-v7a,arm64-v8a
presplash.filename = assets/splash.png
log_level = 2
android.manifest.intent_filters = <category android:name="android.intent.category.LAUNCHER"/>
[buildozer]
log_level = 2
warn_on_root = 0
