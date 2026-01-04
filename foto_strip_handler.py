import os
from pathlib import Path
from PIL import Image as PILImage
from datetime import datetime


from global_variables import Session, AssetPath

class CSV_Handler:
    @staticmethod
    def mark_discard_in_csv(strip_name, recipient):
        """Markiert den gegebenen Streifen in der CSV mit ,discard (anstatt ,sent)."""
        try:
            if not os.path.exists(AssetPath.CSV_PATH):
                return
            lines, updated = [], False
            with open(AssetPath.CSV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) >= 2 and parts[0] == strip_name and parts[1] == recipient:
                        # Falls bereits markiert, so lassen; sonst auf discard setzen
                        if len(parts) >= 3 and parts[2] in ("sent", "discard"):
                            lines.append(line)
                        else:
                            lines.append(f"{strip_name},{recipient},discard\n")
                            updated = True
                    else:
                        lines.append(line)
            if updated:
                with open(AssetPath.CSV_PATH, "w", encoding="utf-8") as f:
                    f.writelines(lines)
        except Exception as e:
            print(f"CSV-Update (discard) fehlgeschlagen: {e}")

        def mark_sent_in_csv(strip_name, recipient):
            """Setzt für den gegebenen Streifen in der CSV die Markierung ,sent."""
            try:
                if not os.path.exists(AssetPath.CSV_PATH):
                    return
                lines, updated = [], False
                with open(AssetPath.CSV_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split(",")
                        if len(parts) >= 2 and parts[0] == strip_name and parts[1] == recipient:
                            if len(parts) >= 3 and parts[2] == "sent":
                                lines.append(line)
                            else:
                                lines.append(f"{strip_name},{recipient},sent\n")
                                updated = True
                        else:
                            lines.append(line)
                if updated:
                    with open(AssetPath.CSV_PATH, "w", encoding="utf-8") as f:
                        f.writelines(lines)
            except Exception as e:
                print(f"CSV-Update fehlgeschlagen: {e}")



class FotoStripHandler:


    @staticmethod
    def try_send_unsent_strips(photo_dir):
        # Versuche alle Einträge ohne 'sent' zu versenden
        if not os.path.exists(AssetPath.CSV_PATH):
            return
        lines = []
        changed = False
        with open(AssetPath.CSV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2 and (len(parts) < 3 or parts[2] not in ("sent", "discard")):
                    strip_name, recipient = parts[0], parts[1]
                    strip_path = os.path.join(photo_dir, strip_name)
                    if os.path.exists(strip_path):
                        success = FotoStripHandler.send_strip_via_email(strip_path, recipient, strip_name)
                        if success:
                            lines.append(f"{strip_name},{recipient},sent\n")
                            changed = True
                        else:
                            lines.append(line)
                    else:
                        lines.append(line)
                else:
                    lines.append(line)
        if changed:
            with open(AssetPath.CSV_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines)

    @staticmethod
    def three_fotos_exist():
        return len(Session.photo_paths) == 3

    @staticmethod
    def create_photostrip():
        photos = Session.photo_paths[:3]
        if len(photos) < 3:
            raise Exception("Not enough Fotos")

        if not os.path.exists(AssetPath.TEMPLATE):
            template = PILImage.new("RGB", (850, 2400), color=(255, 255, 255))
        else:
            template = PILImage.open(AssetPath.TEMPLATE).convert("RGB")

        # Slots
        slot_w, slot_h = 600, 600
        slots = [(125, 480), (125, 1100), (125, 1720)]
        for img_path, (sx, sy) in zip(reversed(photos), slots):
            img = PILImage.open(img_path).convert("RGB")
            img = img.resize((slot_w, slot_h), PILImage.LANCZOS)
            template.paste(img, (sx, sy))

        strip_name = datetime.now().strftime("photostrip_%Y%m%d_%H%M%S.png")
        output_path = str(Path(AssetPath.FOTOSTRIPS).joinpath(strip_name))
        template.save(output_path)
        Session.fotostrip_paths.append(output_path)
        print(len(Session.fotostrip_paths))
        # E-Mail merken
        recipient = Session.email
        _last_recipient = recipient

        Session.photo_paths.clear()

        # CSV-Eintrag sofort anlegen (ohne 'sent'), falls Versand erlaubt
        if (not Session.bestaetigt) and _last_recipient:
            try:
                with open(AssetPath.CSV_PATH, "a", encoding="utf-8") as f:
                    f.write(f"{strip_name},{_last_recipient}\n")
            except Exception as e:
                print(f"Fehler beim Schreiben in CSV: {e}")




    def _on_press_send(self, *_):
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
            photo_dir = Session.FOTOSTRIPS
            if ok:
                try:
                    CSV_Handler.mark_sent_in_csv(AssetPath.CSV_PATH, self._last_strip_name, recipient)
                    FotoStripHandler.try_send_unsent_strips(AssetPath.CSV_PATH, photo_dir)
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


    def _on_press_second(self, *_):
        """
        E-Mail wird NICHT zurückgesetzt.
        Wir springen direkt in den Fotobox-Countdown und erzeugen nach Abschluss
        wieder automatisch einen CSV-Eintrag mit derselben E-Mail.
        """
        self._restart_for_next_strip()
        self.start_photobox()


    def _on_press_discard(self, *_):
        # CSV: Eintrag auf 'discard' setzen
        try:
            recipient = self._last_recipient or Session.email
            if recipient and self._last_strip_name:
                CSV_Handler.mark_discard_in_csv(AssetPath.CSV_PATH, self._last_strip_name, recipient)
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


