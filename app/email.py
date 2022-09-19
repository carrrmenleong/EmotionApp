from flask import render_template
from flask_mail import Message
from app import app, mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[MoodTrack] Reset Your Password',\
               sender=app.config['ADMINS'][0],\
               recipients=[user.email],\
               text_body=render_template('email/reset_password.txt', user=user, token=token),\
               html_body=render_template('email/reset_password.html', user=user, token=token))

def send_sign_up_req_email(user):
    send_email('[MoodTrack] New User Sign Up Request',\
                sender=app.config['ADMINS'][0],\
                recipients=app.config['ADMINS'][0],\
                text_body=render_template('email/signupreq.txt', user=user),\
                html_body=render_template('email/signupreq.html', user=user)
    )


def send_req_result_email(user):
    send_email('[MoodTrack] Sign Up Request Reviewed',\
                sender=app.config['ADMINS'][0],\
                recipients=[user.email],\
                text_body=render_template('email/req_reply.txt', user=user),\
                html_body=render_template('email/req_reply.html', user=user)
    )