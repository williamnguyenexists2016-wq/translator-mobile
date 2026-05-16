# Pocket Translator — Kivy Android App
# Uses plyer for TTS (Android native)
 
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import threading
 
# ── Language data ────────────────────────────────────────────────────────────
 
LANGUAGES = {
    "English":               "en",
    "Arabic":                "ar",
    "Belarusian":            "be",
    "Bengali":               "bn",
    "Bulgarian":             "bg",
    "Catalan":               "ca",
    "Chinese (Simplified)":  "zh-CN",
    "Chinese (Traditional)": "zh-TW",
    "Croatian":              "hr",
    "Czech":                 "cs",
    "Danish":                "da",
    "Dutch":                 "nl",
    "Farsi":                 "fa",
    "Filipino":              "tl",
    "Finnish":               "fi",
    "French":                "fr",
    "German":                "de",
    "Greek":                 "el",
    "Hebrew":                "he",
    "Hindi":                 "hi",
    "Indonesian":            "id",
    "Italian":               "it",
    "Japanese":              "ja",
    "Korean":                "ko",
    "Malay":                 "ms",
    "Norwegian":             "no",
    "Polish":                "pl",
    "Portuguese":            "pt",
    "Romanian":              "ro",
    "Russian":               "ru",
    "Scottish Gaelic":       "gd",
    "Serbian":               "sr",
    "Slovak":                "sk",
    "Spanish":               "es",
    "Swahili":               "sw",
    "Swedish":               "sv",
    "Tagalog":               "tl",
    "Tamil":                 "ta",
    "Thai":                  "th",
    "Turkish":               "tr",
    "Ukrainian":             "uk",
    "Urdu":                  "ur",
    "Vietnamese":            "vi",
}
 
NO_TTS = {"be", "gd"}
LANG_NAMES = sorted(LANGUAGES.keys())
 
# ── Colours ──────────────────────────────────────────────────────────────────
 
BG      = "#0f1117"
PANEL   = "#1a1d27"
ACCENT  = "#4f8ef7"
TEXT    = "#e8eaf0"
SUBTEXT = "#7b8099"
SUCCESS = "#3ddba0"
ERROR   = "#ff5f6d"
 
Window.clearcolor = get_color_from_hex(BG)
 
# ── Helpers ──────────────────────────────────────────────────────────────────
 
def speak(text, lang_code):
    if lang_code in NO_TTS:
        return False
    try:
        from plyer import tts
        tts.speak(text)
        return True
    except Exception:
        return False
 
def do_translate(text, to_lang, from_lang="Auto Detect"):
    from deep_translator import GoogleTranslator
    to_code   = LANGUAGES[to_lang]
    from_code = "auto" if from_lang == "Auto Detect" else LANGUAGES[from_lang]
    result = GoogleTranslator(source=from_code, target=to_code).translate(text)
    return result, to_code
 
def do_listen():
    import speech_recognition as sr
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, timeout=6)
    return r.recognize_google(audio)
 
# ── App ───────────────────────────────────────────────────────────────────────
 
class TranslatorApp(App):
    def build(self):
        self.last_result = None
        self.last_code   = None
 
        root = BoxLayout(orientation="vertical", padding=16, spacing=12)
 
        root.add_widget(Label(
            text="✦ Translator",
            font_size="24sp",
            bold=True,
            color=get_color_from_hex(TEXT),
            size_hint_y=None,
            height=40,
        ))
        root.add_widget(Label(
            text="powered by Google",
            font_size="11sp",
            color=get_color_from_hex(SUBTEXT),
            size_hint_y=None,
            height=20,
        ))
 
        root.add_widget(Label(
            text="TEXT TO TRANSLATE",
            font_size="10sp",
            color=get_color_from_hex(SUBTEXT),
            size_hint_y=None,
            height=20,
        ))
 
        self.input_box = TextInput(
            hint_text="Type here...",
            multiline=True,
            size_hint_y=None,
            height=120,
            background_color=get_color_from_hex(PANEL),
            foreground_color=get_color_from_hex(TEXT),
            cursor_color=get_color_from_hex(ACCENT),
            font_size="14sp",
            padding=[12, 8],
        )
        root.add_widget(self.input_box)
 
        lang_row = BoxLayout(orientation="horizontal",
                             size_hint_y=None, height=44, spacing=8)
 
        self.from_spinner = Spinner(
            text="Auto Detect",
            values=["Auto Detect"] + LANG_NAMES,
            background_color=get_color_from_hex(PANEL),
            color=get_color_from_hex(TEXT),
            font_size="13sp",
        )
        lang_row.add_widget(self.from_spinner)
 
        lang_row.add_widget(Label(
            text="→", color=get_color_from_hex(SUBTEXT),
            size_hint_x=None, width=24,
        ))
 
        self.to_spinner = Spinner(
            text="Spanish",
            values=LANG_NAMES,
            background_color=get_color_from_hex(PANEL),
            color=get_color_from_hex(TEXT),
            font_size="13sp",
        )
        lang_row.add_widget(self.to_spinner)
        root.add_widget(lang_row)
 
        btn_row = BoxLayout(orientation="horizontal",
                            size_hint_y=None, height=48, spacing=8)
 
        self.translate_btn = Button(
            text="Translate  →",
            background_color=get_color_from_hex(ACCENT),
            color=get_color_from_hex(TEXT),
            font_size="14sp", bold=True,
        )
        self.translate_btn.bind(on_press=self.on_translate)
        btn_row.add_widget(self.translate_btn)
 
        self.mic_btn = Button(
            text="🎤 Dictate",
            background_color=get_color_from_hex(PANEL),
            color=get_color_from_hex(TEXT),
            font_size="14sp",
        )
        self.mic_btn.bind(on_press=self.on_dictate)
        btn_row.add_widget(self.mic_btn)
        root.add_widget(btn_row)
 
        out_header = BoxLayout(orientation="horizontal",
                               size_hint_y=None, height=30)
        out_header.add_widget(Label(
            text="TRANSLATION", font_size="10sp",
            color=get_color_from_hex(SUBTEXT),
        ))
        self.speak_btn = Button(
            text="🔊 Speak",
            background_color=get_color_from_hex(PANEL),
            color=get_color_from_hex(ACCENT),
            font_size="11sp", size_hint_x=None, width=90,
        )
        self.speak_btn.bind(on_press=self.on_speak)
        out_header.add_widget(self.speak_btn)
        root.add_widget(out_header)
 
        self.output_box = TextInput(
            hint_text="Translation appears here...",
            multiline=True, readonly=True,
            size_hint_y=None, height=140,
            background_color=get_color_from_hex(PANEL),
            foreground_color=get_color_from_hex(SUCCESS),
            font_size="14sp", padding=[12, 8],
        )
        root.add_widget(self.output_box)
 
        self.status_label = Label(
            text="Ready  ✦", font_size="11sp",
            color=get_color_from_hex(SUBTEXT),
            size_hint_y=None, height=24,
        )
        root.add_widget(self.status_label)
 
        return root
 
    def set_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_label, "text", text))
 
    def on_translate(self, instance):
        text = self.input_box.text.strip()
        if not text:
            self.set_status("⚠  Please enter some text first.")
            return
 
        to_lang   = self.to_spinner.text
        from_lang = self.from_spinner.text
 
        self.translate_btn.disabled = True
        self.set_status(f"Translating to {to_lang}...")
 
        def run():
            try:
                result, code = do_translate(text, to_lang, from_lang)
                self.last_result = result
                self.last_code   = code
                Clock.schedule_once(lambda dt: setattr(self.output_box, "text", result))
                Clock.schedule_once(lambda dt: setattr(
                    self.output_box, "foreground_color", get_color_from_hex(SUCCESS)))
                if code in NO_TTS:
                    self.set_status(f"✓  Translated  (TTS not available for {to_lang})")
                else:
                    self.set_status(f"✓  Translated to {to_lang}")
                    threading.Thread(target=speak, args=(result, code), daemon=True).start()
            except Exception as ex:
                Clock.schedule_once(lambda dt: setattr(self.output_box, "text", str(ex)))
                Clock.schedule_once(lambda dt: setattr(
                    self.output_box, "foreground_color", get_color_from_hex(ERROR)))
                self.set_status("✗  Translation failed.")
            finally:
                Clock.schedule_once(lambda dt: setattr(self.translate_btn, "disabled", False))
 
        threading.Thread(target=run, daemon=True).start()
 
    def on_speak(self, instance):
        if self.last_result and self.last_code not in NO_TTS:
            self.set_status("🔊 Speaking...")
            threading.Thread(target=speak,
                             args=(self.last_result, self.last_code),
                             daemon=True).start()
        elif self.last_code in NO_TTS:
            self.set_status("⚠  TTS not available for this language.")
 
    def on_dictate(self, instance):
        self.mic_btn.disabled = True
        self.mic_btn.text = "🎤 Listening..."
        self.set_status("🎤 Listening... speak now!")
 
        def run():
            try:
                text = do_listen()
                Clock.schedule_once(lambda dt: setattr(self.input_box, "text", text))
                self.set_status(f"✓  Heard: {text}")
            except Exception as ex:
                self.set_status(f"✗  Dictation failed: {ex}")
            finally:
                Clock.schedule_once(lambda dt: setattr(self.mic_btn, "disabled", False))
                Clock.schedule_once(lambda dt: setattr(self.mic_btn, "text", "🎤 Dictate"))
 
        threading.Thread(target=run, daemon=True).start()
 
 
if __name__ == "__main__":
    TranslatorApp().run()
 
