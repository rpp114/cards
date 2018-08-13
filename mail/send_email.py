import sys, os, datetime
# import httplib2, json, sys, os, datetime, re, copy, pytz, calendar

# from apiclient import discovery
# from oauth2client import client
# from sqlalchemy import and_, func

from flask_mail import Message

# add system directory to pull in app & models

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, mail, app


def send_mail(users, message):

    for user in users:

        recipient = [user.email]

        message['recipients'] = recipient

        message['subject'] = message['subject'].format(user.username)

        with app.app_context():
            with mail.connect() as conn:

                msg = Message(recipients=message['recipients'],
                              subject=message['subject'],
                              body=message['body'])

                conn.send(msg)


# send_mail()
