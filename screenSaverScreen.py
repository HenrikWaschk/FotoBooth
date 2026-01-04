from __future__ import annotations

from pathlib import Path
import random
import math

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.animation import Animation

from global_variables import ScreenNames,AssetPath

#from fotobox import try_send_unsent_strips

# Farben / Pfade
BLACK = (0, 0, 0, 1)
BASE_DIR = Path(__file__).resolve().parent
ASSETS = BASE_DIR / "Assets"

EPS = 1e-6  # numerische Stabilität


def asset(*parts: str) -> str:
    return str((ASSETS.joinpath(*parts)).resolve())


# --- Image mit Mipmaps/Filtern + Pixel-Snapping (gegen Flimmern) ---
class SmoothImage(Image):
    def __init__(self, source: str = "", snap: bool = True, **kwargs):
        # Standard: nicht vom Layout steuern lassen, außer explizit angegeben
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("fit_mode", "contain")
        self._snap_enabled = snap
        super().__init__(**kwargs)

        if source:
            tex = CoreImage(source, mipmap=True).texture
            tex.min_filter = "linear_mipmap_linear"
            tex.mag_filter = "linear"
            tex.wrap = "clamp_to_edge"
            self.texture = tex

        if self._snap_enabled:
            self.bind(pos=self._snap, size=self._snap)
            Clock.schedule_once(lambda *_: self._snap(), 0)

    def _managed_by_layout(self) -> bool:
        # Layout-managed, wenn pos_hint gesetzt ODER irgendein size_hint aktiv ist
        sh = self.size_hint
        size_hint_active = (
            sh is not None and sh != (None, None)
        ) or (getattr(self, "size_hint_x", None) is not None) or (getattr(self, "size_hint_y", None) is not None)
        return bool(self.pos_hint) or size_hint_active

    def _snap(self, *args):
        if not self._snap_enabled or self._managed_by_layout():
            return
        xi, yi = int(round(self.x)), int(round(self.y))
        wi, hi = int(round(self.width)), int(round(self.height))
        if (xi, yi, wi, hi) == (self.x, self.y, self.width, self.height):
            return  # nichts zu tun → kein erneutes Event
        # kurz entbinden, um Re-Dispatch-Kaskaden zu vermeiden
        self.unbind(pos=self._snap, size=self._snap)
        try:
            self.pos = (xi, yi)
            self.size = (wi, hi)
        finally:
            self.bind(pos=self._snap, size=self._snap)


# ----------------- Zentrale Marke (wie vorher) -----------------
class CentralBrand(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        layout = FloatLayout(size=Window.size, size_hint=(None, None))

        logo_path = asset("saegewerk_logo.png")
        fotobooth_path = asset("Fotobooth.png")
        starten_path = asset("Starten.png")

        # Logo oben (engerer Abstand)
        self.logo = SmoothImage(source=AssetPath.LOGO, size=(400, 180), snap=False)
        self.logo.pos_hint = {'center_x': 0.5, 'center_y': 0.62}
        layout.add_widget(self.logo)

        # Fotobooth näher ans Logo
        self.fotobooth = SmoothImage(source=AssetPath.FOTOBOOTH, size=(600, 180), snap=False)
        self.fotobooth.pos_hint = {'center_x': 0.5, 'center_y': 0.50}
        layout.add_widget(self.fotobooth)

        # Starten-Button (pulsierend — exakt wie am Anfang: Größe + Opacity)
        self.starten = SmoothImage(source=AssetPath.STARTEN, size=(500, 180), snap=False)
        self.starten.pos_hint = {'center_x': 0.5, 'center_y': 0.32}
        layout.add_widget(self.starten)
        Clock.schedule_once(lambda dt: self._pulse(), 0)

        self.add_widget(layout)
        Window.bind(size=lambda *_: setattr(layout, "size", Window.size))

    def _pulse(self):
        # GENAU wie am Anfang:
        #   - anim_in:  size (500, 180), opacity 1.0, duration 1.0
        #   - anim_out: size (400, 150), opacity 0.3, duration 1.0
        anim_in = Animation(opacity=1, size=(500, 180), duration=1.0)
        anim_out = Animation(opacity=0.3, size=(400, 150), duration=1.0)
        seq = anim_in + anim_out
        seq.repeat = True
        seq.start(self.starten)

    # Rechtecke der zentralen Elemente (für Kollisionen)
    @staticmethod
    def _rect_from_widget(w: Image):
        x = w.center_x - w.width / 2.0
        y = w.center_y - w.height / 2.0
        return (x, y, w.width, w.height)

    def get_rects(self):
        # kombiniertes AABB für Logo + Fotobooth
        lx, ly, lw, lh = self._rect_from_widget(self.logo)
        fx, fy, fw, fh = self._rect_from_widget(self.fotobooth)
        min_x = min(lx, fx)
        max_x = max(lx + lw, fx + fw)
        min_y = min(ly, fy)
        max_y = max(ly + lh, fy + fh)
        combined = (min_x, min_y, max_x - min_x, max_y - min_y)
        # Starten separat
        starten_rect = self._rect_from_widget(self.starten)
        return [combined, starten_rect]


# ----------------- Bewegte Sprites (wie vorher, aber „smooth“) -----------------
class BouncingSprite(Widget):
    def __init__(self, central_ref, img_path, size,
                 spawn_rect=None, exclude_rects=None, spawn_margin=0,
                 others_for_spawn_check=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.sprite_size = size
        self.central_ref = central_ref
        self.radius = min(size) * 0.5  # Kreis-Kollision

        # statt Image → SmoothImage (Mipmaps/Filter/Snapping)
        self.widget = SmoothImage(source=img_path, size=self.sprite_size)
        self.add_widget(self.widget)

        if exclude_rects is None:
            exclude_rects = []
        if others_for_spawn_check is None:
            others_for_spawn_check = []

        # Default Spawn-Areal: gesamter Screen (x0, y0, x1, y1)
        if spawn_rect is None:
            spawn_rect = (0, 0, Window.width, Window.height)

        # zentrale Flächen NICHT als Spawn erlauben
        exclude_rects = list(exclude_rects) + self.central_ref.get_rects()

        # Spawn ohne Überlappung
        self.pos = self._random_pos_nonoverlap(spawn_rect, self.sprite_size, exclude_rects,
                                               spawn_margin, others_for_spawn_check)
        self.widget.pos = self.pos

        # zufällige Geschwindigkeit — GENAU wie vorher: 3.0–7.0 px/Frame (ohne dt)
        speed = random.uniform(3.0, 7.0)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)

        # Takt: pro Frame (wie vorher). Pixel-Snap beim Setzen.
        Clock.schedule_interval(self._tick, 0)

    # ---------- Geometrie-Helpers ----------
    @staticmethod
    def _rects_collide(r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return not (x1 + w1 <= x2 or x1 >= x2 + w2 or y1 + h1 <= y2 or y1 >= y2 + h2)

    @staticmethod
    def _circle_circle_overlap(c1, r1, c2, r2):
        dx = c2[0] - c1[0]
        dy = c2[1] - c1[1]
        dist2 = dx * dx + dy * dy
        rad = r1 + r2
        return dist2 < (rad * rad)

    # ---------- Spawn ohne Overlap ----------
    def _random_pos_nonoverlap(self, rect, size, exclude_rects, margin, others, max_tries=800):
        x0, y0, x1, y1 = rect  # x1/y1 sind Grenzen (keine Breite/Höhe)
        w, h = size
        xmin = int(x0 + margin)
        ymin = int(y0 + margin)
        xmax = int(x1 - margin - w)
        ymax = int(y1 - margin - h)
        if xmax < xmin: xmax = xmin
        if ymax < ymin: ymax = ymin

        for _ in range(max_tries):
            x = random.randint(xmin, xmax) if xmax >= xmin else xmin
            y = random.randint(ymin, ymax) if ymax >= ymin else ymin
            candidate_rect = (x, y, w, h)

            # nicht in verbotenen Rechtecken
            if any(self._rects_collide(candidate_rect, r) for r in exclude_rects):
                continue

            # nicht überlappen mit bereits existierenden Sprites (kreisförmig)
            center = (x + w * 0.5, y + h * 0.5)
            ok = True
            for other in others:
                ocx = other.pos[0] + other.sprite_size[0] * 0.5
                ocy = other.pos[1] + other.sprite_size[1] * 0.5
                if self._circle_circle_overlap(center, self.radius,
                                               (ocx, ocy), other.radius):
                    ok = False
                    break
            if ok:
                return (x, y)
        # Fallback: Ecke
        return (xmin, ymin)

    # ---------- Runtime-Tick (wie vorher, aber mit Pixel-Snap) ----------
    def _tick(self, dt):
        x, y = self.pos
        x += self.vx
        y += self.vy

        # Randkollision + Clamping
        if x <= 0:
            self.vx = abs(self.vx); x = 0 + EPS
        elif x + self.sprite_size[0] >= Window.width:
            self.vx = -abs(self.vx); x = Window.width - self.sprite_size[0] - EPS

        if y <= 0:
            self.vy = abs(self.vy); y = 0 + EPS
        elif y + self.sprite_size[1] >= Window.height:
            self.vy = -abs(self.vy); y = Window.height - self.sprite_size[1] - EPS

        # Bounce an zentralen Flächen
        for (cx, cy, cw, ch) in self.central_ref.get_rects():
            if self._rects_collide((x, y, *self.sprite_size), (cx, cy, cw, ch)):
                overlap_left = abs((x + self.sprite_size[0]) - cx)
                overlap_right = abs(x - (cx + cw))
                overlap_top = abs((y + self.sprite_size[1]) - cy)
                overlap_bottom = abs(y - (cy + ch))
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                if min_overlap == overlap_left:
                    self.vx = -abs(self.vx); x = cx - self.sprite_size[0] - EPS
                elif min_overlap == overlap_right:
                    self.vx = abs(self.vx);  x = cx + cw + EPS
                elif min_overlap == overlap_top:
                    self.vy = -abs(self.vy); y = cy - self.sprite_size[1] - EPS
                else:
                    self.vy = abs(self.vy);  y = cy + ch + EPS

        # Pixel-Snap bei Zuweisung (verhindert Subpixel-Flimmern)
        xi, yi = round(x), round(y)
        self.pos = (xi, yi)
        self.widget.pos = self.pos

    # Kreisdaten für Kollisionen
    def circle(self):
        cx = self.pos[0] + self.sprite_size[0] * 0.5
        cy = self.pos[1] + self.sprite_size[1] * 0.5
        return (cx, cy, self.radius)


# ----------------- Screen -----------------
class StartScreen(Screen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self._idle_retry_event = None
        layout = FloatLayout()

        # Zentrale Markenfläche
        self.central = CentralBrand()
        layout.add_widget(self.central)

        # Oberes Drittel als Spawn-Areal, in links/rechts aufgeteilt
        top_y0 = int(Window.height * 2 / 3)
        left_top_third  = (0, top_y0, int(Window.width * 0.5), Window.height)
        right_top_third = (int(Window.width * 0.5), top_y0, Window.width, Window.height)

        # Smileys (Hälfte links, Hälfte rechts)
        smiley_path = AssetPath.SMILEY
        self.smileys = []
        total_smileys = 10
        left_count = total_smileys // 2     # 5
        right_count = total_smileys - left_count  # 5

        for _ in range(left_count):
            s = BouncingSprite(self.central, AssetPath.SMILEY, (80, 80),
                               spawn_rect=left_top_third, spawn_margin=10,
                               others_for_spawn_check=self.smileys)
            self.smileys.append(s)
            layout.add_widget(s)

        for _ in range(right_count):
            s = BouncingSprite(self.central, AssetPath.SMILEY, (80, 80),
                               spawn_rect=right_top_third, spawn_margin=10,
                               others_for_spawn_check=self.smileys)
            self.smileys.append(s)
            layout.add_widget(s)

        # Disco-Kugeln (Hälfte links, Hälfte rechts)
        disco_path = AssetPath.DISCO  # ändere zu 'Disco.png' falls nötig
        self.discos = []
        total_discos = 5
        left_d = total_discos // 2          # 2
        right_d = total_discos - left_d     # 3

        # links
        for _ in range(left_d):
            others = self.smileys + self.discos
            d = BouncingSprite(self.central, AssetPath.DISCO, (80, 80),
                               spawn_rect=left_top_third, spawn_margin=10,
                               others_for_spawn_check=others)
            self.discos.append(d)
            layout.add_widget(d)

        # rechts
        for _ in range(right_d):
            others = self.smileys + self.discos
            d = BouncingSprite(self.central, AssetPath.DISCO, (80, 80),
                               spawn_rect=right_top_third, spawn_margin=10,
                               others_for_spawn_check=others)
            self.discos.append(d)
            layout.add_widget(d)

        # Liste aller bewegten Sprites
        self._all_sprites = self.smileys + self.discos

        # Kreisbasierte Kollisionsverarbeitung zwischen allen Sprites (wie vorher)
        Clock.schedule_interval(self._handle_circle_collisions, 0)

        self.add_widget(layout)
        Window.clearcolor = BLACK

    def on_pre_enter(self, *args):
        # Nur planen, wenn noch nichts läuft (verhindert Doppeltimer)
        if not self._idle_retry_event:
            self._idle_retry_event = Clock.schedule_once(self._attempt_unsent_once, 5 * 60)

    # --- NEU: beim Verlassen immer abbrechen → „durchgängig“ garantiert ---
    def on_leave(self, *args):
        if self._idle_retry_event is not None:
            try:
                Clock.unschedule(self._idle_retry_event)
            except Exception:
                pass
            self._idle_retry_event = None

    # --- NEU: einmaliger Versandversuch + ggf. erneutes Planen ---
    def _attempt_unsent_once(self, dt):
        # Nur, wenn wir *immer noch* im Screensaver sind
        if not self.manager or self.manager.current != 'start':
            self._idle_retry_event = None
            return


        try:
            #try_send_unsent_strips(csv_path, photo_dir)
            pass
        except Exception:
            # im Screensaver bewusst still – keine UI-Meldung
            print("Fehler beim Senden der ungesendeten Streifen. In start")
            pass

        # Weiterhin im Screensaver? → nächsten 15-Minuten-Slot planen
        if self.manager and self.manager.current == 'start':
            self._idle_retry_event = Clock.schedule_once(self._attempt_unsent_once, 5 * 60)
        else:
            self._idle_retry_event = None

    def _handle_circle_collisions(self, dt):
        sprites = self._all_sprites
        n = len(sprites)
        for i in range(n):
            c1x, c1y, r1 = sprites[i].circle()
            for j in range(i + 1, n):
                c2x, c2y, r2 = sprites[j].circle()

                dx = c2x - c1x
                dy = c2y - c1y
                dist2 = dx * dx + dy * dy
                min_dist = r1 + r2

                if dist2 < (min_dist * min_dist):
                    dist = math.sqrt(dist2) if dist2 > EPS else min_dist

                    # Normale
                    nx = dx / (dist if dist > EPS else min_dist)
                    ny = dy / (dist if dist > EPS else min_dist)

                    # Penetration (Überlappung)
                    penetration = min_dist - dist
                    if penetration < 0:
                        continue

                    # Positionen entlang der Normal auseinander schieben (je 50%)
                    correction = (penetration / 2.0) + 0.5  # +0.5 px safety
                    sprites[i].pos = (sprites[i].pos[0] - nx * correction,
                                      sprites[i].pos[1] - ny * correction)
                    sprites[j].pos = (sprites[j].pos[0] + nx * correction,
                                      sprites[j].pos[1] + ny * correction)

                    # Widget-Positionen updaten (Pixel-Snap)
                    sprites[i].pos = (round(sprites[i].pos[0]), round(sprites[i].pos[1]))
                    sprites[j].pos = (round(sprites[j].pos[0]), round(sprites[j].pos[1]))
                    sprites[i].widget.pos = sprites[i].pos
                    sprites[j].widget.pos = sprites[j].pos

                    # Geschwindigkeiten elastisch entlang der Normal tauschen (gleiche Masse)
                    rvx = sprites[j].vx - sprites[i].vx
                    rvy = sprites[j].vy - sprites[i].vy
                    vel_along_normal = rvx * nx + rvy * ny
                    if vel_along_normal > 0:
                        continue  # bewegen sich bereits auseinander

                    e = 1.0
                    j_impulse = -(1 + e) * vel_along_normal / 2.0

                    ix = j_impulse * nx
                    iy = j_impulse * ny

                    sprites[i].vx -= ix
                    sprites[i].vy -= iy
                    sprites[j].vx += ix
                    sprites[j].vy += iy

    def on_touch_down(self, touch):
        self.manager.transition.direction = 'left'
        self.manager.current = ScreenNames.TYPE_EMAIL
        return True