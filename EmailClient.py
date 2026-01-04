from server import Email_Server
class EmailClient:
    @staticmethod
    # TODO: Add the Email server Data
    def send_strips_via_email(strip_paths, recipient, strip_name):
        import re, ssl, smtplib
        from email.message import EmailMessage
        SMTP_SERVER = Email_Server.SMTP_SERVER
        SMTP_PORT = Email_Server.SMTP_PORT
        SMTP_USER = Email_Server.SMTP_USER
        SMTP_PASS = Email_Server.SMTP_PASS
        SENDER_EMAIL = Email_Server.SENDER_EMAIL

        subject = "Sägewerk FOTO BOOTH - Dein Fotostreifen"
        body = (
            "Liebe:r Besucher:in,\n\n"
            "im Anhang findest du deinen Fotostreifen von der Sägewerk FOTO BOOTH!\n\n"
            "Viel Spaß damit!\n\n"
        )

        if not recipient or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", recipient):
            print(f"Fehler beim Mailversand: ungültiger Empfänger '{recipient}'")
            return False

        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = f"Fotobox <{SENDER_EMAIL}>"
            msg["To"] = recipient
            msg.set_content(body)
            for strip_path in strip_paths:
                with open(strip_path, "rb") as f:
                    img_data = f.read()
                msg.add_attachment(img_data, maintype="image", subtype="png", filename=strip_name)

            context = ssl.create_default_context()
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg, from_addr=SENDER_EMAIL, to_addrs=[recipient])

            return True

        except Exception as e:
            print(f"Fehler beim Mailversand: {e}")
            return False