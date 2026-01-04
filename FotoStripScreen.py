from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


from global_variables import MyColor,AssetPath,Session
from neonbutton import NeonButton
from foto_strip_handler import FotoStripHandler

medium_fontsize = dp(48)
big_button_fontsize = dp(48)
big_button_height = dp(96)

class FotoStripUI(FloatLayout):

    def __init__(self,**kwargs):
        super(FotoStripUI, self).__init__(**kwargs)

        Clock.schedule_interval(self.update, 1.0 / 60)  # 60 FPS

        self.container = BoxLayout(
            orientation='horizontal',
            spacing=dp(24),
            padding=(dp(40), dp(24), dp(40), dp(24)),
            size_hint=(1, 1)
        )

        self.left_col = FloatLayout(size_hint=(0.5, 1))

        if Session.bestaetigt:
            msg_text = "Genieß deinen Fotostreifen das erste und letzte mal! :)"
        else:
            msg_text = "Dein Fotostreifen ist bereit!\n"
            # "Versenden kann etwas dauern."

        # Message at y ≈ 0.75
        self.msg_label = Label(
            text=msg_text,
            font_size=dp(64),
            font_name=AssetPath.ROC_GROTESK_REGULAR if Path(AssetPath.ROC_GROTESK_REGULAR).exists() else None,
            color=MyColor.NEON,
            size_hint=(1, None),  # allow explicit height; needed so pos_hint works vertically
            halign='center', valign='middle',
            pos_hint={'center_x': 0.5, 'center_y': 0.67}
        )
        self.msg_label.bind(width=lambda i, w: setattr(i, 'text_size', (w, None)))
        self.msg_label.bind(texture_size=lambda i, s: setattr(i, 'height', s[1] + dp(12)))
        self._msg_label_ref = self.msg_label
        self.left_col.add_widget(self.msg_label)

        if not Session.bestaetigt:
            # E-Mail Label at y ≈ 0.6
            self.versenden_label = Label(
                text="Versand kann je nach Internet \n etwas dauern",
                font_size=medium_fontsize,
                font_name=AssetPath.ROC_GROTESK_REGULAR if Path(AssetPath.ROC_GROTESK_REGULAR).exists() else None,
                color=MyColor.NEON,
                size_hint=(1, None),  # allow explicit height; needed so pos_hint works vertically
                halign='center', valign='middle',
                pos_hint={'center_x': 0.5, 'center_y': 0.62}
            )
            self.versenden_label.bind(width=lambda i, w: setattr(i, 'text_size', (w, None)))
            self.versenden_label.bind(texture_size=lambda i, s: setattr(i, 'height', s[1] + dp(12)))
            self.left_col.add_widget(self.versenden_label)

        if not Session.bestaetigt:
            # Buttons grouped at y ≈ 0.5
            spacing_y = dp(16)
            self.btn_box = BoxLayout(
                orientation='vertical',
                spacing=spacing_y,
                size_hint=(0.9, None),
                pos_hint={'center_x': 0.5, 'center_y': 0.4}
            )

            # set explicit height: 3 buttons + 2 gaps
            self.btn_box.height = 3 * big_button_height + 2 * spacing_y

            self.btn_send = NeonButton(
                text="Versenden",
                size_hint=(1, None),
                font_size=big_button_fontsize,
                height=big_button_height
            )
            #TODO:
            #btn_send.bind(on_press=self._on_press_send)

            self.btn_second = NeonButton(
                text="weiteren Fotostreifen aufnehmen",
                size_hint=(1, None),
                font_size=big_button_fontsize,
                height=big_button_height
            )

            #TODO:
            #btn_second.bind(on_press=self._on_press_second)

            self.btn_discard = NeonButton(
                text="Fotostreifen verwerfen",
                size_hint=(1, None),
                font_size=big_button_fontsize,
                height=big_button_height
            )
            #TODO:
            #btn_discard.bind(on_press=self._on_press_discard)

            self.btn_box.add_widget(self.btn_send)
            self.btn_box.add_widget(self.btn_second)
            self.btn_box.add_widget(self.btn_discard)

            self.left_col.add_widget(self.btn_box)
        else:
            # mit Timer zurück, wenn Versand deaktiviert
            Clock.schedule_once(self._back_to_start, 20)

            # === RECHTE HÄLFTE: Fotostreifen (volle Höhe) ===

        self.right_col = BoxLayout(orientation='vertical', size_hint=(0.5, 1), padding=(0, 0, 0, 0))
        self.photostrip_widget = Image(
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.right_col.add_widget(self.photostrip_widget)
        self.container.add_widget(self.left_col)
        self.container.add_widget(self.right_col)
        self.add_widget(self.container)

    def update(self,dt):
        if len(Session.fotostrip_paths) > 0:
            self.photostrip_widget.source = Session.fotostrip_paths[-1]

class FotoStripScreen(Screen):
    def __init__(self, **kwargs):
        super(FotoStripScreen, self).__init__(**kwargs)
        self.fotostrip_ui = FotoStripUI()
        self.add_widget(self.fotostrip_ui)

    '''def _on_press_send(self, *_):
        if not self._last_strip_path or not self._last_strip_name:
            # Beim Navigieren auch E-Mail resetten
            try:
                import typeemail as _te
                _te.typed_email = ""
            except Exception:
                pass
            try:
                import global_variables as _gv
                _gv.email_bestaetigt = False
            except Exception:
                pass
            self._last_recipient = None
            self._go_to_screensaver()
            return

        recipient = self._last_recipient or Session.email

        ok = False
        if recipient:
            ok = FotoStripHandler.send_strip_via_email(self._last_strip_path, recipient, self._last_strip_name)
            csv_path = str(Path.cwd().joinpath('email_strip.csv'))
            photo_dir = Session.FOTOSTRIPS
            if ok:
                try:
                    CSV_Handler.mark_sent_in_csv(csv_path, self._last_strip_name, recipient)
                    FotoStripHandler.try_send_unsent_strips(csv_path, photo_dir)
                except Exception:
                    pass

        # <<< HIER: nach dem Sendeversuch immer zurücksetzen >>>
        try:
            import typeemail as _te
            _te.typed_email = ""
        except Exception:
            pass
        try:
            Session.bestaetigt= False
            Session.datenschutz_bestaetigt = False
        except Exception:
            pass
        self._last_recipient = None

        # zurück in den Screensaver/Start
        self._go_to_screensaver()
        '''

    '''def _on_press_second(self, *_):
        """
        E-Mail wird NICHT zurückgesetzt.
        Wir springen direkt in den Fotobox-Countdown und erzeugen nach Abschluss
        wieder automatisch einen CSV-Eintrag mit derselben E-Mail.
        """
        self._restart_for_next_strip()
        self.start_photobox()'''

    '''def _on_press_discard(self, *_):
        # CSV: Eintrag auf 'discard' setzen
        try:
            csv_path = str(Path.cwd().joinpath('email_strip.csv'))
            recipient = self._last_recipient or Session.email
            if recipient and self._last_strip_name:
                CSV_Handler.mark_discard_in_csv(csv_path, self._last_strip_name, recipient)
        except Exception as e:
            print(f"Fehler beim Discard-Markieren: {e}")

        # Datei optional löschen
        try:
            if self._last_strip_path and os.path.exists(self._last_strip_path):
                os.remove(self._last_strip_path)
        except Exception:
            pass

        # zurück zum Start (oder Screensaver – je nach gewünschtem Flow)
        self._back_to_start(None)
    '''
