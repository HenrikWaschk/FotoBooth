from enum import Enum
from pathlib import Path

from kivy.metrics import dp

class MyColor():
    NEON = (204 / 255.0, 1.0, 0.0, 1.0)
    BLACK = (0, 0, 0, 1)
    GREY = (0.08, 0.08, 0.08, 1)
    WHITE = (255, 255, 255, 1)
    #TODO: Change the name
    stepProgressColor = (1,1,1,0.12)

class FontSizes():
    VERY_SMALL = dp(16)

class AssetPath():
    DATENSCHUTZERKLAERUNG = str(Path.cwd().joinpath('Assets').joinpath('DATENSCHUTZINFORMATIONEN_FÜR_KUNDEN_Khisdapaze.txt'))
    SMILEY = str(Path.cwd().joinpath('Assets').joinpath('smiley.png'))
    ROC_GROTESK_REGULAR = str(Path.cwd().joinpath('Assets').joinpath('Roc_Grotesk_Regular.otf'))

class VideoParameters():
    HEIGHT = 600
    WIDTH = 600