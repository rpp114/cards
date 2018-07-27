import sys, os
# import httplib2, json, sys, os, datetime, re, copy, pytz, calendar

# from apiclient import discovery
# from oauth2client import client
# from sqlalchemy import and_, func

from flask_mail import Message

# add system directory to pull in app & models

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, mail, app


def send_mail():

    with app.app_context():
        msg = Message(subject='Hello', sender=('Card Tracker', app.config['MAIL_USERNAME']))

        msg.recipients = ['rpputt@hotmail.com']

        msg.body = 'testing email'

        mail.send(msg)


send_mail()
