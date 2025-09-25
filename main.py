from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

#Importing Global constants here
from global_variables import MyColor

from fotoScreen import FotoBoxScreen

class FotoBoxApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(FotoBoxScreen(name='fotobox'))

        return sm

if __name__ == '__main__':
    FotoBoxApp().run()