import os
from pathlib import Path
from kivy.metrics import dp

class MyColor:
    NEON = (204 / 255.0, 1.0, 0.0, 1.0)
    BLACK = (0, 0, 0, 1)
    GREY = (0.08, 0.08, 0.08, 1)
    WHITE = (255, 255, 255, 1)
    #TODO: Change the name
    stepProgressColor = (1,1,1,0.12)

class FontSizes:
    VERY_SMALL = dp(16)
    KEYBOARD = dp(24)

class AssetPath:
    ASSETS = Path.cwd().joinpath('Assets')
    #Images
    #-----------------------------------------------------------------
    DISCO = str(ASSETS.joinpath("Disko.png"))
    LOGO = str(ASSETS.joinpath("saegewerk_logo.png"))
    FOTOBOOTH = str(ASSETS.joinpath("Fotobooth.png"))
    STARTEN = str(ASSETS.joinpath("Starten.png"))
    SMILEY = str(ASSETS.joinpath('smiley.png'))
    TEMPLATE = str(ASSETS.joinpath('Template.png'))

    #Folders
    #------------------------------------------------------------------
    FOTOSTRIPS = str(Path.cwd().joinpath('FotoStrips'))
    os.makedirs(FOTOSTRIPS, exist_ok=True)
    PHOTOS = str(Path.cwd().joinpath('Photos'))
    os.makedirs(PHOTOS, exist_ok=True)

    DATENSCHUTZERKLAERUNG = str(ASSETS.joinpath('DATENSCHUTZINFORMATIONEN_FÜR_KUNDEN_Khisdapaze.txt'))
    ROC_GROTESK_REGULAR = str(ASSETS.joinpath('Roc_Grotesk_Regular.otf'))
    CSV_PATH = str(Path.cwd().joinpath('email_strip.csv'))


class VideoParameters:
    HEIGHT = 600
    WIDTH = 600

class ScreenNames:
    START = 'start'
    TYPE_EMAIL = 'type_email'
    CONFIRM_EMAIL = 'confirm_email'
    DATENSCHUTZ_READER = 'datenschutz_reader'
    FOTOBOX = 'fotobox'
    FOTO_STRIP = 'foto_strip'

class Session:
    fotostrip_paths = []
    photo_paths = []
    emailTyped = True
    email = ''
    bestaetigt = False
    datenschutz_bestaetigt = False
    datenschutz_gelesen = False
    @staticmethod
    def reset_photo_paths():
        Session.photo_paths.clear()

    @staticmethod
    def reset_session():
        Session.fotostrip_paths = []
        Session.photo_paths = []
        Session.emailTyped = True
        Session.email = ''
        Session.bestaetigt = False
        Session.datenschutz_bestaetigt = False

#Session related variables
class Email:
 pass
