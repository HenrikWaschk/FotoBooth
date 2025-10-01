from pathlib import Path
from kivy.graphics import Line, Color
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from global_variables import MyColor,AssetPath


class My_CheckBox(Widget):
    active = BooleanProperty(False)

    def __init__(self, outline_color=MyColor.NEON, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (96, 96)
        self.layout = FloatLayout(size=self.size, size_hint=(None, None))

        with self.canvas.after:
            self.outline_color = Color(*outline_color)
            self.outline = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

        # Smiley als hochauflösende Textur mit Mipmaps laden
        tex = CoreImage(AssetPath.SMILEY, mipmap=True).texture
        tex.min_filter = "linear_mipmap_linear"  # trilinear beim Verkleinern
        tex.mag_filter = "linear"                # bilinear beim Vergrößern
        tex.wrap = "clamp_to_edge"

        self.smiley_image = Image(
            texture=tex,
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.layout.add_widget(self.smiley_image)

        self.bind(pos=self.layout.setter('pos'))
        self.bind(pos=self.update_outline, size=self.update_outline)
        self.bind(size=self._resize_smiley)
        Clock.schedule_once(lambda *_: self._resize_smiley(), 0)

        self.bind(active=self.on_active_change)

        self.add_widget(self.layout)
        self.on_active_change(self, self.active)

    def _resize_smiley(self, *args):
        # 90% der Checkbox-Größe, auf ganze Pixel runden
        target = int(round(min(self.width, self.height) * 0.9))
        self.smiley_image.size = (target, target)
        self.smiley_image.pos = (
            int(round(self.center_x - target / 2)),
            int(round(self.center_y - target / 2))
        )

    def update_outline(self, *args):
        self.outline.rectangle = (self.x, self.y, self.width, self.height)

    def set_outline_color(self, rgba):
        self.outline_color.rgba = rgba

    def on_active_change(self, instance, value):
        self.smiley_image.opacity = 1 if value else 0

    def switch(self, instance=None):
        self.active = not self.active