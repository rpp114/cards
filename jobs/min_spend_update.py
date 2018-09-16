import sys, os, datetime

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, mail, app

from mail.send_email import send_mail


def get_min_spend_users():

    get_users_query = """select user.id, user.email, user.username, company.name, card.name, date(l.active_date + interval s.days_for_spend day) as min_spend_date, datediff(l.active_date + interval s.days_for_spend day, now()) as days_left, s.minimum_spend, s.bonus_points, pp.name

from user_card_lookup l
inner join user on user_id = user.id
inner join card on card.id = l.card_id
inner join points_program pp on pp.id = card.points_program_id
inner join company on company.id = card.company_id
inner join signup_bonus s on s.card_id = card.id and l.active_date between s.from_date and s.to_date and s.minimum_spend > 0

where user.active = 1
and card.active = 1
and l.active = 1
and l.status = 'active'
and now() between l.active_date and l.active_date + interval s.days_for_spend day
and mod(datediff(now(),l.active_date), 30) = 0;
    """

    users = db.session.execute(get_users_query)

    return users



def send_min_spend_email():

    users = get_min_spend_users()

    messages = []

    for user in users:

        user_obj = {'username': user[2],
                    'company_name': user[3],
                    'card_name':user[4],
                    'min_spend_date': user[5],
                    'days_left': user[6],
                    'min_spend':'${:,}'.format(user[7]),
                    'bonus_points': '{:,}'.format(user[8]),
                    'points_program': user[9]}

        subject = "Reach the min spend on your {} card!".format(user[4])

        body = """Hey {u[username]},

This is CrdTrckr just reminding you that you have {u[days_left]} days left to hit the minimum spend on your {u[company_name]} {u[card_name]}.

You need to spend {u[min_spend]} in order to get the {u[bonus_points]} {u[points_program]} points.

Thanks

- CrdTrckr""".format(u=user_obj)


        msg = {'recipient':[user[1]],
                      'subject':subject,
                      'body':body}

        messages.append(msg)
    print(messages)
    send_mail(messages)

# send_min_spend_email()
