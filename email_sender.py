from email.message import EmailMessage
from email.headerregistry import Address
import ssl
import smtplib
from email.utils import make_msgid
from config import EMAIL_SENDER, EMAIL_PASSWORD


def send_email(email_receiver, receiver_name, password_reset_url):
    email_sender = EMAIL_SENDER
    email_password = EMAIL_PASSWORD

    subject = 'Redefinição de senha'
    body = \
        f"""
            Olá, {receiver_name}!
            
            Segue link para redefinição da sua senha:
            
            {password_reset_url}
        """

    asparagus_cid = make_msgid()

    msg = EmailMessage()
    msg['From'] = Address('Zendesk Routing', domain=email_sender)
    msg['To'] = email_receiver
    msg['Subject'] = subject
    msg.set_content(body)

    msg.add_alternative(f"""\
    <html lang="pt_BR">
        <head>
            <title>Redefinição de senha</title>
        </head>
        <body style="background-color:#040C26;padding:50px;text-align:center;font-family:Arial,Helvetica,sans-serif;font-size:14px">
            <div style="background-color:white;padding:50px;text-align:left;width:20%;margin:auto;border-radius:30px">
                <div style="text-align:center">
                    <img src="cid:{asparagus_cid[1:-1]}" />
                </div>
                <br>
                <div style="text-align:center">
                    <h2 style="color:black">Olá, {receiver_name}!</h2>
                    <br>
                    <p style="color:black">Segue o link para redefinição da sua senha 🤘</p>
                </div>
                <br>
                <div style="text-align:center;margin-top:50px">
                    <a href="{password_reset_url}" class="link"><button style="padding:20px 60px;border-radius:40px;border:none;cursor:pointer;background-color:#040C26;color:white;font-weight:bold;font-size:16px">Redefinir senha</button></a>
                </div>
            </div>
        </body>
    </html>
    """, subtype='html')

    with open("static/img/favicon.png", 'rb') as img:
        msg.get_payload()[1].add_related(img.read(), 'image', 'png', cid=asparagus_cid)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        message_status = smtp.send_message(msg)

        return message_status
