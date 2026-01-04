from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

from global_variables import MyColor,AssetPath,ScreenNames,Session

class Normal_Button(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = MyColor.BLACK
        self.color = MyColor.NEON
        self.border = (0,0,0,0)
        with self.canvas.before:
            Color(*MyColor.NEON)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

class DatenschutzReader(Screen):
    def __init__(self, **kwargs):
        super(DatenschutzReader, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical')
        with open(AssetPath.DATENSCHUTZERKLAERUNG, 'r', encoding='utf-8') as f:
            text = f.read()
        self.text_input = TextInput(readonly=True,
                                    font_size=dp(24),
                                    scroll_from_swipe=True,
                                    background_color=MyColor.BLACK,
                                    foreground_color=MyColor.NEON,
                                    text = text)

        layout.add_widget(self.text_input)

        zurueck_button = Normal_Button(
            text="Zurück",
            size_hint=(1, None),
            height=dp(192),
            pos_hint={'center_x': 0.5, 'y': 0.1},
            font_size = dp(96),
            font_name=AssetPath.ROC_GROTESK_REGULAR,
        )
        zurueck_button.bind(on_press=self.goto_confirmemail)
        layout.add_widget(zurueck_button)

        self.add_widget(layout)

    def goto_confirmemail(self, instance):
        Session.datenschutz_gelesen = True
        self.manager.transition.direction = 'up'
        self.manager.current = ScreenNames.CONFIRM_EMAIL