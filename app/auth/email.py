from flask import render_template
from flask_mail import Message
from app import mail
from flask import current_app
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[EmotionApp] Reset Your Password',\
               sender=current_app.config['ADMINS'][0],\
               recipients=[user.email],\
               text_body=render_template('email/reset_password.txt', user=user, token=token),\
               html_body=render_template('email/reset_password.html', user=user, token=token))

def send_sign_up_req_email(user):
    send_email('[EmotionApp] New User Sign Up Request',\
                sender=current_app.config['ADMINS'][0],\
                recipients=current_app.config['ADMINS'],\
                text_body=render_template('email/signupreq.txt', user=user),\
                html_body=render_template('email/signupreq.html', user=user)
    )


def send_req_result_email(user, results):
    send_email('[EmotionApp] Sign Up Request Reviewed',\
                sender=current_app.config['ADMINS'][0],\
                recipients=[user.email],\
                text_body=render_template('email/req_reply.txt', user=user, results=results),\
                html_body=render_template('email/req_reply.html', user=user, results=results)
    )
