from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from neonbutton import NeonButton

from VirtualKeyboard import VirtualKeyboard
from global_variables import ScreenNames,MyColor,AssetPath,Email
from stepProgress import StepProgress

typed_email = ""  # Global variable to store the email

#Title,Textbox,Keyboard,Weiter Button,Email Warning Label
#old_List_Y = (0.72,0.58,0.02,0.44,0.37)
List_Y = (0.8,0.675,0.2,0.1,0.605)

KEYBOARD_HEIGHT = 0.4

#old_List_X = (0.5,0.5,0,O.5)
List_X = (0.5,0.5,0,0.8)

class TypeEmail(Screen):
    def __init__(self, **kwargs):
        super(TypeEmail, self).__init__(**kwargs)
        self.build_ui()

    def on_pre_enter(self, *args):
        """Beim Betreten: Textfeld aus globalem State setzen (nach Reset = leer)."""
        global typed_email
        self._reset_warning()
        try:
            self.text_input.text = typed_email or ""
        except Exception:
            pass

    def build_ui(self):
        layout = FloatLayout()

        # Progress oben
        layout.add_widget(StepProgress(current_step=1))

        # Label
        info = Label(
            text="Wohin sollen wir deinen Fotostreifen schicken?",
            font_size=dp(64),
            font_name=AssetPath.ROC_GROTESK_REGULAR,
            color=(MyColor.NEON),
            size_hint=(0.9, None), height=dp(60),
            pos_hint={'center_x':List_X[0], 'y':List_Y[0]}
        )
        layout.add_widget(info)

        # TextInput mit moderner Karte
        self.text_input = TextInput(
            font_size=dp(48),
            size_hint=(0.86, None),
            height=dp(100),
            pos_hint={'center_x': List_X[1], 'y': List_Y[1]},
            multiline=False,
            halign='center',
            foreground_color=(1,1,1,1),
            cursor_color=MyColor.NEON,
            background_color=(0,0,0,0),
        )
        with self.text_input.canvas.before:
            Color(*MyColor.GREY)
            self._ti_bg = RoundedRectangle(pos=self.text_input.pos, size=self.text_input.size, radius=[dp(20)])
            Color(*MyColor.NEON)
            self._ti_border = Line(rounded_rectangle=[self.text_input.x, self.text_input.y, self.text_input.width, self.text_input.height, dp(20)], width=1.2)
        self.text_input.bind(pos=self._update_ti, size=self._update_ti, text=self._keep_vertical_center)
        # Start mit vertikal zentriertem Padding
        self.text_input.bind(text=self._on_email_changed)
        self._keep_vertical_center(self.text_input, self.text_input.text)

        layout.add_widget(self.text_input)

        # Weiter Button
        weiter_button = NeonButton(
            text="Weiter -->",
            font_size=dp(48),
            font_name = AssetPath.ROC_GROTESK_REGULAR,
            size_hint=(0.32, None),
            height=dp(96),
            pos_hint={'center_x': List_X[3], 'center_y': List_Y[3]}
        )
        weiter_button.bind(on_press=self.goto_fotobox)
        layout.add_widget(weiter_button)

        self.warning_label = Label(
            text="",
            font_size=dp(32),  # größer
            font_name=AssetPath.ROC_GROTESK_REGULAR,
            color=(1, 0.2, 0.2, 1),  # Rot
            size_hint=(0.9, None),
            height=dp(40),
            pos_hint={'center_x': 0.5, 'y': List_Y[4]},
            opacity=0  # unsichtbar bis zur ersten Warnung
        )
        layout.add_widget(self.warning_label)

        # Merker für ersten/zweiten Klick ohne Email
        self.warning_shown_once = False

        # Virtuelle Tastatur
        vk = VirtualKeyboard(
            target_input=self.text_input,
            size_hint=(1, KEYBOARD_HEIGHT),
            pos_hint={'x': List_X[2], 'y': List_Y[2]}
        )
        layout.add_widget(vk)

        self.add_widget(layout)

    def _reset_warning(self):
        self.warning_label.text = ""
        self.warning_label.opacity = 0
        self.warning_shown_once = False

    def _on_email_changed(self, instance, value):
        # Sobald etwas eingegeben wird -> Warnung ausblenden
        if value.strip():
            self._reset_warning()

    def _keep_vertical_center(self, instance, value):
        # Text vertikal stabil mittig halten (ganzzahlige Padding-Werte verhindern "Springen")
        lh = instance.line_height
        h = instance.height
        pad_y = int(max(0, (h - lh) / 2.0))
        instance.padding = (20, pad_y)

    def goto_fotobox(self, instance):
        global typed_email
        typed_email = self.text_input.text.strip()
        if not typed_email:
            if not self.warning_shown_once:
                # Beim ersten Klick nur Warnung anzeigen
                self.warning_label.text = "Leere Email-Adresse - Foto wird nach dem Anzeigen gelöscht. Trotzdem weiter?"
                self.warning_label.opacity = 1  # sichtbar machen
                self.warning_shown_once = True
                return
            # Beim zweiten Klick trotzdem weitergehen + Flag setzen
            Email.EmailTyped = True
        else:
            # E-Mail vorhanden -> Flag sicherheitshalber zurücksetzen
            Email.EmailTyped = False
        self.manager.transition.direction = 'left'
        self.manager.current = ScreenNames.CONFIRM_EMAIL

    def _update_ti(self, *args):
        self._ti_bg.pos = self.text_input.pos
        self._ti_bg.size = self.text_input.size
        self._ti_border.rounded_rectangle = [self.text_input.x, self.text_input.y, self.text_input.width, self.text_input.height, dp(20)]
        # Padding ggf. neu berechnen
        self._keep_vertical_center(self.text_input, self.text_input.text)