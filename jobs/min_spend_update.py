import sys, os, datetime

from flask_mail import Message

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, mail, app

from mail import send_email



def send_min_spend_email():

    users = models.User.query.filter_by(active=1, admin=1).all()

    subject = "Hello {} Welcome to CrdTrckr"

    body = """Hey guys,

    Welcome to the CrdTrckr.  Lots of exciting things going on.  You guys were the first to sign up so I've made you all admins.  You can go to www.crdtrckr.com and log in with your created user name.

    Then you'll be able to see the admin page in the upper right hand corner.  This will take you to a secret place.  A place where you can manage all the cards, signup bonuses, and all the rewards and spending categories associated with each.

    This is going to be the tricky part, is keeping this up-to-date.  In order to be able to suggest cards, we need this information.  So I'm hopefully that you guys can help me out in gathering it.

    If you have any questions, please email me at rpputt@hotmail.com.

    Thanks

    -Ray
    """

    msg = Message(subject=subject,body=body)

    send_email(users, msg)
