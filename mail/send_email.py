import sys, os, datetime
# import httplib2, json, sys, os, datetime, re, copy, pytz, calendar

# from apiclient import discovery
# from oauth2client import client
# from sqlalchemy import and_, func

from flask_mail import Message

# add system directory to pull in app & models

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, mail, app


def send_mail():

    users = models.User.query.all()

    for user in users:

        query = """select company.name, card.name, lookup.active_date, b.days_for_spend, b.minimum_spend
                    from card
                    inner join user_card_lookup lookup on lookup.card_id = card.id
                    inner join company on company.id = company_id
                    inner join signup_bonus b on b.card_id = card.id and lookup.active_date between b.from_date and b.to_date
                    where lookup.user_id = {}
                    and lookup.status = 'active';""".format(user.id)

        cards = db.session.execute(query)

        recipient = [user.email]

        with app.app_context():
            with mail.connect() as conn:

                for card in cards:
                    if card[4] == 0:
                        continue

                    subject = 'Hit the Minimum Spend on {}'.format(card[1])
                    body = """Hello {},

                    Make sure you hit the minimum spend of ${:,} by {}""".format(user.username, card[4], (card[2] + datetime.timedelta(days=card[3])).strftime('%B %d, %Y'))

                    msg = Message(recipients=recipient,
                                  subject=subject,
                                  body=body,
                                  )
                    # print(msg)

                    conn.send(msg)


send_mail()
