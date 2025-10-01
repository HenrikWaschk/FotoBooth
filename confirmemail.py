from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from mycheckbox import My_CheckBox
from pathlib import Path
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line

from global_variables import Email,ScreenNames,MyColor,AssetPath
from neonbutton import NeonButton
from stepProgress import StepProgress
import typeemail  # Import the global variable

# Confirm Email Title,Confirm Email test and buttom,Datenschutz Title, Datenschutz and agree button,Weiter and Zurück Button
Layers_y = (0.77, 0.635, 0.42, 0.25, 0.1)

big_button_fontsize = dp(48)
headline_fontsize = dp(64)
big_button_height = dp(96)
big_fontsize = dp(56)

class ConfirmEmail(Screen):
    def __init__(self, **kwargs):
        super(ConfirmEmail, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = FloatLayout()

        layout.add_widget(StepProgress(current_step=2))

        info_label = Label(
            text="BITTE E-MAIL BESTÄTIGEN",
            font_size=headline_fontsize,
            font_name=AssetPath.ROC_GROTESK_REGULAR,
            color=(MyColor.NEON),
            size_hint=(0.9, None),
            height=dp(80),
            pos_hint={'center_x': 0.5, 'center_y': Layers_y[0]},
            halign='center',
            valign='middle'

        )
        info_label.bind(size=lambda instance, value: setattr(instance, 'text_size', instance.size))
        layout.add_widget(info_label)

        self.email_label = Label(
            text="",
            font_size=big_fontsize,
            color=MyColor.NEON,
            size_hint=(0.5, None),
            height=dp(140),
            pos_hint={'x': 0.075, 'center_y': Layers_y[1]},
            halign='center',
            valign='center'
        )
        self.email_label.bind(size=self._update_label_text)
        layout.add_widget(self.email_label)

        self.email_checkbox = My_CheckBox(
            pos_hint={'center_x': 0.625, 'center_y': Layers_y[1]}
        )
        layout.add_widget(self.email_checkbox)

        email_bestaetigen_button = NeonButton(
            text="Bestätigen",
            size_hint=(0.25, None),
            height=big_button_height,
            pos_hint={'center_x': 0.8, 'center_y': Layers_y[1]},
            font_size=big_button_fontsize,
            font_name=AssetPath.ROC_GROTESK_REGULAR
        )
        email_bestaetigen_button.bind(on_press=self.email_bestaetigen_button)
        layout.add_widget(email_bestaetigen_button)

        datenschutz_bestätigen_label = Label(
            text="Ich habe die Datenschutzerklärung gelesen \n und stimme dieser hiermit zu:",
            font_size=headline_fontsize,
            font_name=AssetPath.ROC_GROTESK_REGULAR,
            color=(MyColor.NEON),
            size_hint=(0.7, None),
            height=dp(160),
            pos_hint={'center_x': 0.5, 'center_y': Layers_y[2]},
            halign='center',
            valign='middle'

        )
        datenschutz_bestätigen_label.bind(size=lambda instance, value: setattr(instance, 'text_size', instance.size))
        layout.add_widget(datenschutz_bestätigen_label)

        self.datenschutz_checkbox = My_CheckBox(
            pos_hint={'center_x': 0.625, 'center_y': Layers_y[3]},
        )
        layout.add_widget(self.datenschutz_checkbox)

        datenschutz_button = NeonButton(
            text=" Datenschutzerklärung",
            size_hint=(0.4, None),
            height=big_button_height,
            pos_hint={'center_x': 0.275, 'center_y': Layers_y[3]},
            font_size=big_button_fontsize,
            font_name=AssetPath.ROC_GROTESK_REGULAR,
        )
        datenschutz_button.bind(on_press=self.goto_datenschutzreader)
        layout.add_widget(datenschutz_button)

        Datenschutz_bestaetigen_button = NeonButton(
            text="Bestätigen",
            size_hint=(0.25, None),
            height=big_button_height,
            pos_hint={'center_x': 0.8, 'center_y': Layers_y[3]},
            font_size=big_button_fontsize,
            font_name=AssetPath.ROC_GROTESK_REGULAR
        )
        Datenschutz_bestaetigen_button.bind(on_press=self.datenschutz_button)
        layout.add_widget(Datenschutz_bestaetigen_button)

        zurueck_button = NeonButton(
            text=" <-- Zurück",
            size_hint=(0.25, None),
            height=big_button_height,
            pos_hint={'center_x': 0.2, 'center_y': Layers_y[4]},
            font_size=big_button_fontsize,
            font_name=AssetPath.ROC_GROTESK_REGULAR,
        )
        zurueck_button.bind(on_press=self.goto_typeemail)
        layout.add_widget(zurueck_button)

        weiter_button = NeonButton(
            text="Weiter -->",
            size_hint=(0.25, None),
            height=big_button_height,
            pos_hint={'center_x': 0.8, 'center_y': Layers_y[4]},
            font_size=big_button_fontsize,
            font_name=AssetPath.ROC_GROTESK_REGULAR,
        )
        weiter_button.bind(on_press=self.goto_fotobox)
        layout.add_widget(weiter_button)

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        Email.datenschutz_bestaetigt = False
        if (typeemail.typed_email == ""):
            Email.bestaetigt = True
        else:
            Email.bestaetigt = False
        from typeemail import typed_email  # Re-import to get the updated value
        self.email_label.text = typed_email
        self.email_checkbox.active = Email.bestaetigt
        self.datenschutz_checkbox.active = Email.datenschutz_bestaetigt

    def _update_label_text(self, instance, value):
        instance.text_size = instance.size

    def datenschutz_button(self, instance):
        Email.datenschutz_bestaetigt = not Email.datenschutz_bestaetigt
        self.datenschutz_checkbox.active = Email.datenschutz_bestaetigt

    def email_bestaetigen_button(self, instance):
        Email.bestaetigt = not Email.bestaetigt
        self.email_checkbox.active = Email.bestaetigt

    def goto_fotobox(self, instance):
        if (Email.bestaetigt & Email.datenschutz_bestaetigt):
            self.manager.transition.direction = 'left'
            self.manager.current = 'fotobox'

    def goto_typeemail(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = ScreenNames.TYPE_EMAIL

    def goto_datenschutzreader(self, instance):
        self.manager.transition.direction = 'down'
        self.manager.current = AssetPath.DATENSCHUTZERKLAERUNG

    # def on_leave(self, *args):
    # self.datenschutz_checkbox.active = False
    # self.email_checkbox.active = False