import sys, os, datetime

from flask_mail import Message

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, mail, app

from mail import send_email



def send_admin_email():

    users = models.User.query.filter_by(active=1).all()

    body = """Hey guys,

    Hello from CrdTrckr.  More exciting things going on.

    I just wanted to let you know that I've changed a couple things.  Now, in the admin page there is a concept of reward programs these are what get attached to every points programself.

    So for instance, the Southwest Reward Program will get connected to a southwest points program, but also to Chase Ultimate rewards since you can transfer the points to thatself.

    These points programs have a monetary value.  And a category associated with them.  This way we can find where the best redemptions areself.

    As for the emails, there are two alerts that are now officially live:

        1) Alerts you if every 30 days when you have a minimum spend active.  (I need to make it have an off switch if you hit it, but at most it's 4 emails 1 a month).
        2) Alerts for annual fees.  This will send you an alert the first of the month prior to your activation date, so you are aware an annual fee is upcomingself.

    Feel free to actually start putting things in there.  Let's see if this damn thing actually starts workingself.

    Next in the pipe will be a log in flow to start gathering categories as you sign up for what you are interested in.  So that we can start making suggestions.

    If you have any questions, please email me at rpputt@hotmail.com.

    Thanks

    -Ray
    """

    messages = []

    for user in users:
        subject = "Hello {} From to CrdTrckr".format(user.username)
        message = {'recipient':[user.email],
                   'subject':subject,
                   'body':body}
        messages.append(message)


    send_email.send_mail(messages)

send_admin_email()
