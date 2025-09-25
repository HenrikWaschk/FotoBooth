from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle


from global_variables import MyColor


class StepProgress(FloatLayout):
    def __init__(self, current_step:int=3, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.96, None)  # breiter
        self.height = dp(56)
        self.pos_hint = {'center_x': 0.5, 'top': 0.98}
        self.steps = ["Email eingeben", "Bestätigen", "Fotobox", "Versendet"]
        self.current_step = max(1, min(current_step, 4))
        with self.canvas:
            Color(*MyColor.stepProgressColor)
            self._bar = RoundedRectangle(pos=(0,0), size=(self.width, self.height), radius=[dp(16)])
        self.bind(size=self._update_bar, pos=self._update_bar)
        self.labels = []
        for i, s in enumerate(self.steps, start=1):
            lbl = Label(text=s, font_size=dp(20), color=MyColor.NEON if i<=self.current_step else (1,1,1,0.45),
                        size_hint=(0.25,1), pos_hint={'x': (i-1)*0.25, 'y': 0}, halign='center', valign='middle')
            lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
            self.add_widget(lbl)
            self.labels.append(lbl)

    def _update_bar(self, *args):
        self._bar.pos = self.pos
        self._bar.size = self.size