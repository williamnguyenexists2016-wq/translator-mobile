[app]
title = Translator
package.name = translator
package.domain = org.brian
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3==3.10.12,kivy==2.3.0,Cython==0.29.33,deep-translator,gtts,plyer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, RECORD_AUDIO
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
