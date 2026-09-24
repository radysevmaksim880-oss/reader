import os
import threading
import time
from gtts import gTTS
import pygame

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

Window.clearcolor = (0.1, 0.1, 0.12, 1)

class ReaderApp(App):
    def build(self):
        self.title = "Аудио-Читалка"
        
        pygame.mixer.init()
        self.lines = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False

        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        self.lbl_title = Label(
            text="Аудио-Читалка книг",
            font_size='22sp',
            bold=True,
            size_hint_y=0.1
        )
        main_layout.add_widget(self.lbl_title)

        self.lbl_status = Label(
            text="Нажмите 'Загрузить book.txt'",
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.1
        )
        main_layout.add_widget(self.lbl_status)

        self.txt_display = TextInput(
            text="Здесь будет отображаться читаемый текст...",
            font_size='18sp',
            readonly=True,
            background_color=(0.18, 0.18, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            size_hint_y=0.5
        )
        main_layout.add_widget(self.txt_display)

        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.15)

        self.btn_load = Button(text="📁 Файл", background_color=(0.2, 0.6, 0.8, 1))
        self.btn_load.bind(on_press=self.load_file)
        btn_layout.add_widget(self.btn_load)

        self.btn_play = Button(text="▶ Старт", background_color=(0.2, 0.8, 0.3, 1))
        self.btn_play.bind(on_press=self.start_reading)
        btn_layout.add_widget(self.btn_play)

        self.btn_pause = Button(text="⏸ Пауза", background_color=(0.9, 0.6, 0.1, 1))
        self.btn_pause.bind(on_press=self.pause_reading)
        btn_layout.add_widget(self.btn_pause)

        self.btn_stop = Button(text="⏹ Стоп", background_color=(0.8, 0.2, 0.2, 1))
        self.btn_stop.bind(on_press=self.stop_reading)
        btn_layout.add_widget(self.btn_stop)

        main_layout.add_widget(btn_layout)

        return main_layout

    def load_file(self, instance):
        filename = "book.txt"
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write("Это первая строка твоей книги.\nА это вторая строка для проверки чтения!")

        with open(filename, "r", encoding="utf-8") as f:
            self.lines = [line.strip() for line in f.readlines() if line.strip()]

        self.current_index = 0
        self.lbl_status.text = f"Загружен book.txt ({len(self.lines)} строк)"

    def start_reading(self, instance):
        if not self.lines:
            self.load_file(None)

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.lbl_status.text = "Продолжаем чтение"
            return

        if not self.is_playing:
            self.is_playing = True
            threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        while self.current_index < len(self.lines) and self.is_playing:
            line = self.lines[self.current_index]
            self.txt_display.text = line
            self.lbl_status.text = f"Строка {self.current_index + 1} из {len(self.lines)}"

            try:
                tts = gTTS(text=line, lang="ru")
                audio_file = "temp_kivy_voice.mp3"
                tts.save(audio_file)

                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy() or self.is_paused:
                    if not self.is_playing:
                        break
                    time.sleep(0.1)

                pygame.mixer.music.unload()
            except Exception as e:
                print(f"Ошибка: {e}")

            if self.is_playing and not self.is_paused:
                self.current_index += 1

        if self.current_index >= len(self.lines):
            self.lbl_status.text = "Книга прочитана!"
            self.is_playing = False

    def pause_reading(self, instance):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.lbl_status.text = "На паузе"

    def stop_reading(self, instance):
        self.is_playing = False
        self.is_paused = False
        pygame.mixer.music.stop()
        self.current_index = 0
        self.txt_display.text = "Остановлено"
        self.lbl_status.text = "Готов к запуску"

if __name__ == "__main__":
    ReaderApp().run()
