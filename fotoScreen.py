from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
import os
from camera_client import ComputerVisionCamera

from neonbutton import NeonButton
from stepProgress import StepProgress
from global_variables import MyColor


class FotoBoxUI(FloatLayout):
    def __init__(self, **kwargs):
        super(FotoBoxUI, self).__init__(**kwargs)

        # Progress über gesamte Breite oben
        self.progress = StepProgress(current_step=3)
        self.add_widget(self.progress)

        # H-Layout für Preview links, Steuerbereich rechts
        content = BoxLayout(orientation='horizontal', size_hint=(1,1), pos_hint={'x':0,'y':0})
        self.add_widget(content)

        self.image_widget = Image(
            size_hint=(0.63, 0.9),
            allow_stretch=True,
            keep_ratio=True
        )

        right_layout = FloatLayout(size_hint=(0.3, 1))

        # Zentrales Panel im rechten Bereich -> Button/Timer exakt mittig zwischen Vorschaubild und Bildschirmrand
        panel = FloatLayout(size_hint=(0.9, 0.9), pos_hint={'center_x': 0.5, 'center_y': 0.48})

        # Timer groß, mittig im rechten Bereich
        self.timer_label = Label(
            text="5",
            font_size=dp(180),
            color= MyColor.NEON,
            size_hint=(None, None),
            size=(dp(300), dp(300)),
            pos_hint={'center_x': 0.5, 'top': 0.9},
            halign='center', valign='middle'
        )
        self.timer_label.bind(size=lambda i, v: setattr(i, 'text_size', i.size))
        panel.add_widget(self.timer_label)

        # Start-Button mittig im rechten Bereich
        self.start_button = NeonButton(
            text='Fotobox starten',
            size_hint=(0.8, None),
            height=dp(80),
            pos_hint={'center_x': 0.5, 'center_y': 0.42}
        )
        self.start_button.bind(on_press=self.start_photobox)
        panel.add_widget(self.start_button)

        right_layout.add_widget(panel)

        content.add_widget(self.image_widget)
        content.add_widget(right_layout)

        try:
            self.cameraClient = ComputerVisionCamera()
            self.cameraClient.start()
        except:
            print("Couldn't open camera client")
        self.timer_running = False
        self.timer_value = 5
        self.photo_count = 0

        # VERY IMPORTANT is necessary for Kivy to call the update function later
        Clock.schedule_interval(self.update, 1.0 / 60)  # 60 FPS

    def update(self, dt):
        frame = self.cameraClient.get_frame()
        if frame is not None:
            # Konvertieren in RGB für Kivy
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.image_widget.texture = texture
        else:
            print("Error: Could not read frame from camera.")

    def start_photobox(self, instance):
        if not self.timer_running:
            self.timer_running = True
            self.photo_count = 0
            self.start_button.opacity = 0
            self.start_button.disabled = True
            self.start_countdown()

#--------------------------------------------------------------------------------------
#Start of the foto logic
#--------------------------------------------------------------------------------------

    def start_countdown(self):
        self.timer_value = 5
        self.timer_label.text = str(self.timer_value)
        Clock.schedule_interval(self.timer_tick, 1)

    def timer_tick(self, dt):
        if self.timer_value > 1:
            self.timer_value -= 1
            self.timer_label.text = str(self.timer_value)
        else:
            Clock.unschedule(self.timer_tick)
            self.timer_label.text = "Foto!"
            self.turn_light_on()
            self.photo_count += 1
            if self.photo_count < 3:
                Clock.schedule_once(lambda dt: self.start_countdown(), 1.5)
            else:
                #Clock.schedule_once(self.create_and_show_photostrip, 1.0)
                self.timer_running = False
                self.start_button.opacity = 1
                self.start_button.disabled = False
        return True

    def turn_light_on(self):
        os.system('cd /home/kdp/wiringpi/433Utils/RPi_utils/ && ./send 11111 1 1')
        Clock.schedule_once(self.take_photo_and_turn_light_off, 1)

    def take_photo_and_turn_light_off(self, dt):
        self.cameraClient.take_picture()
        os.system('cd /home/kdp/wiringpi/433Utils/RPi_utils/ && ./send 11111 1 0')

#--------------------------------------------------------------------------------------------------
#End of foto logic
#--------------------------------------------------------------------------------------------------

class FotoBoxScreen(Screen):
    def __init__(self, **kwargs):
        super(FotoBoxScreen, self).__init__(**kwargs)
        self.fotobox_ui = FotoBoxUI()
        self.add_widget(self.fotobox_ui)

    def on_pre_enter(self, *args):
        # Sicherstellen, dass die Kamera läuft, wenn man zurück in die Fotobox kommt
        try:
            self.cameraClient.start()
        except:
            pass

    def on_stop(self):
        self.fotobox_ui.on_stop()