import sys, os, datetime

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, app


def get_wallet(user):

    all_cards = user.cards.join(models.SpendingCategoryLookup).join(models.SpendingCategory)\
          .with_entities(models.SpendingCategory.name, models.SpendingCategoryLookup.company_name, models.Card.id.label('card_id'), models.Card.name, models.SpendingCategoryLookup.earning_percent)\
          .filter(models.SpendingCategory.name == 'All', models.SpendingCategory.active == 1, models.SpendingCategoryLookup.active == 1)\
          .order_by(models.SpendingCategoryLookup.earning_percent.desc()).all()

    all_card_max = 0.0
    all_cards_list = []

    if all_cards:
        all_card_max = all_cards[0][4]
        all_cards_list += [card[2] for card in all_cards if card[4] == all_card_max]

    get_cards_query = """
    select sc.name, scl.company_name, card.id, card.name, scl.earning_percent

from spending_category sc
inner join spending_category_lookup scl on scl.spending_category_id = sc.id and sc.active = 1 and scl.active = 1
inner join card on scl.card_id = card.id and card.active = 1
inner join user_card_lookup ucl on ucl.card_id = card.id and ucl.user_id = {}

where sc.name != 'all'

order by 1, 4 desc""".format(user.id)

    user_cards = db.session.execute(get_cards_query).fetchall()

    wallet = {}

    used_cards = {}

    current_category = ''
    skip_category = False
    first_all = True
    all_percent = 0.0

    for card in user_cards:

        if card[0] != current_category:
            current_category = card[0]
            first_all = True

        add_card = False

        if card[4] >= all_card_max:
            if card[1] == 'All':
                if first_all:
                    all_percent = card[4]
                    first_all = False
                if card[4] == all_percent:
                    add_card = True
            elif card[1] != 'All' and card[4] >= all_percent:
                add_card = True

        if add_card:
            wallet[card[0]] = wallet.get(card[0], [])
            wallet[card[0]].append(card)
            used_cards[card[2]] = used_cards.get(card[2],0) + 1

    used_cards_sorted = sorted(used_cards.items(), key=lambda item:(item[1],item[0]), reverse=True)

    for used_card in used_cards_sorted:
        if used_card[0] in all_cards_list:
            wallet['All Else'] = [all_cards[all_cards_list.index(used_card[0])]]

    if not wallet.get('All Else', None) and all_cards:
        wallet['All Else'] = [all_cards[0]]

    return wallet


def suggest_cards(user):

    ###########################################################################
    # Needs to add 5/24 logic to the cards
    ###########################################################################

    prefs = user.preferences.filter(models.UserPreference.active == 1).first()

    current_card_ids = [c.id for c in user.cards.join(models.UserCardLookup).filter(models.UserCardLookup.status == 'active').all()]

    ####
    #  build SQL Query to find cards
    ####
    wheres = {'company' : "" if prefs.own_company else " and card.card_type = 'personal'",
              'cat_1': "" if not prefs.reward_category_1 else "and rp.category_name = '%s'" % prefs.reward_category_1,
              'cat_2': "" if not prefs.reward_category_2 else "and rp.category_name = '%s'" % prefs.reward_category_2,
              'cat_3': "" if not prefs.reward_category_3 else "and rp.category_name = '%s'" % prefs.reward_category_3

    }

    query = """
select id, max(potential)
from (
select card.id, max(bonus.bonus_points * rp.redeem_value * 3) as potential

from company
inner join card on card.company_id = company.id and card.active = 1 and company.active = 1
inner join signup_bonus bonus on bonus.card_id = card.id and bonus.active = 1
inner join points_program pp on pp.id = card.points_program_id and pp.active = 1
inner join reward_program_lookup rpl on rpl.points_program_id = pp.id and rpl.active = 1
inner join reward_program rp on rp.id = rpl.reward_program_id and rp.active = 1

where  1 = 1 {w[company]} {w[cat_1]}
group by 1

union

select card.id, max(bonus.bonus_points * rp.redeem_value * 2) as potential

from company
inner join card on card.company_id = company.id and card.active = 1 and company.active = 1
inner join signup_bonus bonus on bonus.card_id = card.id and bonus.active = 1
inner join points_program pp on pp.id = card.points_program_id and pp.active = 1
inner join reward_program_lookup rpl on rpl.points_program_id = pp.id and rpl.active = 1
inner join reward_program rp on rp.id = rpl.reward_program_id and rp.active = 1

where  1 = 1 {w[company]} {w[cat_2]}
group by 1

union

select card.id, max(bonus.bonus_points * rp.redeem_value * 1) as potential

from company
inner join card on card.company_id = company.id and card.active = 1 and company.active = 1
inner join signup_bonus bonus on bonus.card_id = card.id and bonus.active = 1
inner join points_program pp on pp.id = card.points_program_id and pp.active = 1
inner join reward_program_lookup rpl on rpl.points_program_id = pp.id and rpl.active = 1
inner join reward_program rp on rp.id = rpl.reward_program_id and rp.active = 1

where  1 = 1 {w[company]} {w[cat_3]}
group by 1) cards

group by 1

order by 2 desc""".format(w=wheres)

    prioritized_cards = db.session.execute(query).fetchall()

    suggested_cards = []
    counter = 0

    for card in prioritized_cards:
        if counter == 4:
            break
        if card[0] not in current_card_ids:
            suggested_cards.append(card[0])
            counter += 1

    return suggested_cards
