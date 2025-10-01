from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line
from global_variables import FontSizes

NEON = (204 / 255.0, 1.0, 0.0, 1.0)
INK = (0, 0, 0, 1)
GREY = (0.1, 0.1, 0.1, 1)


class NeonKey(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        # self.background_color = NEON
        self.color = INK
        self.font_size = FontSizes.KEYBOARD
        with self.canvas.before:
            Color(*NEON)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        # Schwarzer Rand um jede Taste
        with self.canvas.after:
            Color(0, 0, 0, 1)
            self._border = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, dp(14)], width=2)
        self.bind(pos=self._update_shapes, size=self._update_shapes)

    def _update_shapes(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = [self.x, self.y, self.width, self.height, dp(14)]

class VirtualKeyboard(FloatLayout):
    def __init__(self, target_input: TextInput, **kwargs):
        super().__init__(**kwargs)
        self.target_input = target_input

        keys = [
            list('1234567890'),
            list('QWERTZUIOP'),
            list('ASDFGHJKL'),
            ['Y', 'X', 'C', 'V', 'B', 'N', 'M', '@', '.', '-', '_'],
            ['@GMAIL.COM', '@WEB.DE', '<--']
        ]

        key_height = 1 / len(keys)
        y = 1 - key_height

        for row in keys:
            x = 0.02
            key_width = 0.96 / len(row)
            for key in row:
                btn = NeonKey(
                    text=key,
                    size_hint=(key_width, key_height),
                    pos_hint={'x': x, 'y': y}
                )
                btn.bind(on_press=self.on_key_press)
                self.add_widget(btn)
                x += key_width
            y -= key_height

    def on_key_press(self, instance: Button):
        key = instance.text
        ti = self.target_input

        if key == '<--':
            if ti.selection_text:
                ti.delete_selection()
            else:
                if ti.cursor_index() > 0:
                    ti.do_backspace()
            return

        ti.insert_text(key)