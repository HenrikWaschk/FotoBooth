from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from global_variables import ScreenNames

from screenSaverScreen import StartScreen
from typeemail import TypeEmail
from confirmemail import ConfirmEmail
from datenschutz_reader import DatenschutzReader
from fotoScreen import FotoBoxScreen
from FotoStripScreen import FotoStripScreen

class FotoBoxApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name=ScreenNames.START))
        sm.add_widget(TypeEmail(name=ScreenNames.TYPE_EMAIL))
        sm.add_widget(ConfirmEmail(name=ScreenNames.CONFIRM_EMAIL))
        sm.add_widget(DatenschutzReader(name=ScreenNames.DATENSCHUTZ_READER))
        sm.add_widget(FotoBoxScreen(name=ScreenNames.FOTOBOX))
        sm.add_widget(FotoStripScreen(name=ScreenNames.FOTO_STRIP))
        sm.current = ScreenNames.FOTOBOX
        return sm

if __name__ == '__main__':
    FotoBoxApp().run()