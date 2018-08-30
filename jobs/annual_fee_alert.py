import sys, os, datetime

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, mail, app

from mail.send_email import send_mail


def get_annual_fee_users():

    get_users_query = """select user.id, user.email, user.username, company.name, card.name, date_format(l.active_date,'%M') as active_month, s.annual_fee

from user_card_lookup l
inner join user on user_id = user.id
inner join card on card.id = l.card_id
inner join points_program pp on pp.id = card.points_program_id
inner join company on company.id = card.company_id
inner join signup_bonus s on s.card_id = card.id and l.active_date between s.from_date and s.to_date and s.annual_fee > 0

where user.active = 1
and card.active = 1
and l.active = 1
and l.status = 'active'
and month(l.active_date) = month(now() + interval 1 month);
    """

    users = db.session.execute(get_users_query)

    return users



def send_annual_fee_email():

    users = get_annual_fee_users()

    messages = []

    for user in users:

        user_obj = {'username': user[2],
                    'company_name': user[3],
                    'card_name':user[4],
                    'active_month': user[5],
                    'annual_fee':'${:,}'.format(user[6]),
                    'card_rating':'{:}%'.format(1 * 100)}

        subject = "Annual Fee coming on {} card!".format(user_obj['card_name'])

        body = """Hey {u[username]},

This is CrdTrckr just reminding you that you have and annual fee of {u[annual_fee]} on your {u[company_name]} {u[card_name]} in the month of {u[active_month]}.

According to our users, {u[card_rating]} of them feel this card is worth keeping for the annual fee.

Thanks

- CrdTrckr""".format(u=user_obj)


        msg = {'recipient':[user[1]],
                      'subject':subject,
                      'body':body}


        messages.append(msg)

    send_mail(messages)

# send_annual_fee_email()
