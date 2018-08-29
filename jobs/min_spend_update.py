import sys, os, datetime

from flask_mail import Message

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, mail, app

from mail import send_email


def get_min_spend_users():

    get_users_query = """select user.id, user.email, user.username, company.name, card.name, date(l.active_date + interval s.days_for_spend day) as min_spend_date, datediff(l.active_date + interval s.days_for_spend day, now()) as days_left, s.minimum_spend

from user_card_lookup l
inner join user on user_id = user.id
inner join card on card.id = l.card_id
inner join company on company.id = card.company_id
inner join signup_bonus s on s.card_id = card.id and l.active_date between s.from_date and s.to_date and s.minimum_spend > 0

where user.active = 1
and card.active = 1
and l.active = 1
and l.status = 'active'
and now() between l.active_date and l.active_date + interval s.days_for_spend day;
and mod(datediff(now(),l.active_date), 30) = 0;
    """

    users = db.session.execute(get_users_query)

    return users



def send_min_spend_email():

    users = get_min_spend_users()

    messages = []

    for user in users:

        subject = "Make sure you reach the min spend on your {} card".format(user[4])

        body = """Hey {},

        

        """

        msg = Message(recipients=[user[1]]
                      subject=subject,
                      body=body)

        messages.append(msg)

    send_email(messages)

# get_min_spend_users()
