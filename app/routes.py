import datetime, os, json
from flask import render_template, flash, url_for, redirect, request
from app import app, db, models
from app.forms import LoginForm, CardForm, SignupForm, CompanyForm, SignupBonusForm,PointsProgramForm, RewardCategoryForm, RewardProgramForm,SpendingCategoryForm,\
	CardSpendingCategoryForm,UserCardForm, PasswordChangeForm, PreferenceForm
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.utils import secure_filename

from algos.optimize import suggest_cards, get_wallet


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
@app.route('/index')
def index():
	if current_user.is_authenticated:
		return redirect(url_for('user_wallet'))

	title = 'Travel Hacker'

	return render_template('index.html', title=title)

@app.route('/how_it_works')
def how_it_works():

	return render_template('how_it_works.html')

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('user_wallet'))

	form = SignupForm()

	if form.validate_on_submit():
		user = models.User(username=form.username.data, email=form.email.data, active=1)
		user.set_password(form.password.data)
		user.set_session_token()
		user.first_login = 0

		db.session.add(user)
		db.session.commit()

		login_user(user, remember=form.remember_me.data)

		return redirect(url_for('user_preferences'))

	return render_template('signup.html', form=form)


@app.route('/user/password', methods=['GET', 'POST'])
def change_password():
	form = PasswordChangeForm()

	# Need to display error for not matching passwords.
	# for field, errors in form.errors:
	# 	print(field, errors)

	if form.validate_on_submit():
		user = current_user
		user.set_password(form.password.data)
		user.set_session_token()
		db.session.add(user)
		db.session.commit()

		login_user(user)

		flash('Password Changed!')

		return redirect(url_for('user_wallet'))

	return render_template('password_change.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('user_wallet'))

	form = LoginForm()

	if form.validate_on_submit():
		user = models.User.query.filter_by(username = form.username.data).first()

		if user is None or not user.check_password(form.password.data):
			flash('bad login')
			return redirect(url_for('login'))

		login_user(user, remember = form.remember_me.data)

		return redirect(url_for('user_wallet'))

	return render_template('login.html', title='Sign In', form=form)



##############################################################
# Users Views
##############################################################

@app.route('/user/preferences', methods=['GET', 'POST'])
@login_required
def user_preferences():

	prefs_list = current_user.preferences.order_by(models.UserPreference.to_date).all()
	if len(prefs_list) > 0:
		prefs=prefs_list[-1]
		form = PreferenceForm(obj=prefs)
	else:
		prefs = None
		form = PreferenceForm()

	if request.method == 'POST':
		data = request.form

		if prefs:
			now = datetime.datetime.now()
			prefs.active = 0
			prefs.to_date = now
			db.session.add(prefs)
			new_prefs = models.UserPreference(from_date = now)
		else:
			new_prefs = models.UserPreference()


		new_prefs.own_company = 1 if data.get('own_company', '') == 'y' else 0
		new_prefs.user_id = current_user.id

		for x in range(1,4):
			cat = 'reward_category_' + str(x)
			comp = 'reward_company_' + str(x)
			setattr(new_prefs, cat, data.get(cat, 'None'))
			setattr(new_prefs, comp, data.get(comp, 'None'))

		db.session.add(new_prefs)
		db.session.commit()

		flash('Updated Reward Preferences')

		return redirect(url_for('user_wallet'))


	reward_categories = models.RewardProgram.query.filter_by(active=True).order_by(models.RewardProgram.category_name, models.RewardProgram.company_name).all()

	categories = {}
	companies = []

	for c in reward_categories:
		categories[c.category_name] = categories.get(c.category_name, [])
		categories[c.category_name].append(c.company_name)
		companies.append((c.company_name, c.company_name))


	form.reward_category_1.choices = [('None', 'None')] + [(c,c) for c in categories.keys()]
	form.reward_category_2.choices = [('None', 'None')] + [(c,c) for c in categories.keys()]
	form.reward_category_3.choices = [('None', 'None')] + [(c,c) for c in categories.keys()]

	if prefs:
		form.reward_company_1.choices = [('All', 'All')] + [(c,c) for c in categories[prefs.reward_category_1]]
		form.reward_company_2.choices = [('All', 'All')] + [(c,c) for c in categories[prefs.reward_category_2]]
		form.reward_company_3.choices = [('All', 'All')] + [(c,c) for c in categories[prefs.reward_category_3]]
	else:
		form.reward_company_1.choices = [('All', 'All')]
		form.reward_company_2.choices = [('All', 'All')]
		form.reward_company_3.choices = [('All', 'All')]


	return render_template('user_preferences.html', form=form, categories=categories)


@app.route('/user/wallet', methods=['GET', 'POST'])
@login_required
def user_wallet():

	if request.method == 'POST':
		# print(request.form)

		if request.form.get('remove'):
			card_id = request.form.get('remove')
			user_card_lookup = models.UserCardLookup.query.filter_by(card_id = card_id, user_id = current_user.id).first()
			user_card_lookup.active = 0
			user_card_lookup.status = 'inactive'
			user_card_lookup.cancel_date = datetime.datetime.now()

			message = 'Removed {} from your wallet.'

		elif request.form.get('add'):
			card_id = request.form.get('add')
			user_card_lookup = models.UserCardLookup.query.filter_by(card_id=card_id, user_id = current_user.id).first()
			if not user_card_lookup:
				user_card_lookup = models.UserCardLookup(card_id=card_id, user_id=current_user.id)
			user_card_lookup.active = 1
			user_card_lookup.active_date = datetime.datetime.strptime(request.form.get('activation_date'),'%m/%d/%Y')
			user_card_lookup.expiration_date = datetime.datetime.strptime(request.form.get('expiration_date'),'%m/%d/%Y')
			user_card_lookup.status = 'active'

			message = 'Added {} to your wallet.'

		elif request.form.get('apply'):
			card_id = request.form.get('apply')
			user_card_lookup = models.UserCardLookup.query.filter_by(card_id=card_id, user_id = current_user.id).first()
			if not user_card_lookup:
				user_card_lookup = models.UserCardLookup(card_id=card_id, user_id=current_user.id)
			user_card_lookup.active = 1
			user_card_lookup.status = 'applied'

			message = 'Applied for {}.'

		card = models.Card.query.get(card_id)

		flash(message.format(card.name))

		db.session.add(user_card_lookup)
		db.session.commit()

	user_cards = models.Card.query\
			.join(models.UserCardLookup, models.Company)\
			.add_columns(models.Company.name, models.UserCardLookup.active, models.UserCardLookup.status)\
			.filter(models.UserCardLookup.user_id == current_user.id, models.Card.active == 1, models.Company.active == 1)\
			.order_by(models.Company.name, models.Card.name).all()

	cards = {}
	for user_card in user_cards:
		cards[user_card[3]] = cards.get(user_card[3], [])
		cards[user_card[3]].append(user_card[0])

	cards['suggested'] = [models.Card.query.get(id) for id in suggest_cards(current_user)]

	wallet = get_wallet(current_user)

	return render_template('user_wallet.html',
		user=current_user,
		cards=cards,
		wallet=wallet)

@app.route('/user/card', methods=['GET', 'POST'])
@login_required
def user_card():
	card_id = request.args.get('card_id', '')

	user_card_lookup = models.UserCardLookup.query.filter_by(card_id=card_id, user_id=current_user.id).first()

	form = UserCardForm() if user_card_lookup == None else UserCardForm(obj=user_card_lookup)

	if request.method == 'POST':
		user_card_lookup.active_date = form.active_date.data
		print(form.cancel_date.data)
		# print(datetime.datetime.strptime(form.active_date.data,'%Y-%m-%d'))

	return render_template('user_card.html',
							form=form,
							user_card=user_card_lookup)

@app.route('/user/profile')
@login_required
def user_profile():

	return render_template('user_profile.html')

@app.route('/search/cards', methods=['GET', 'POST'])
@login_required
def search_cards():

	if request.method == 'POST':

		user_card = models.UserCardLookup(user_id=current_user.id,
										  card_id=request.form.get('card_id'))
		if request.form.get('activation_date', None):
			user_card.active_date = datetime.datetime.strptime(request.form.get('activation_date'),'%m/%d/%Y')
		if request.form.get('expiration_date', None):
			user_card.expiration_date = datetime.datetime.strptime(request.form.get('expiration_date'),'%m/%d/%Y')
		db.session.add(user_card)
		db.session.commit()
		card = user_card.cards
		flash('Added {} to your wallet'.format(card.name))

	all_cards = models.Card.query.join(models.SignupBonus).join(models.Company)\
	.with_entities(models.Company.name.label('company_name'), models.Card.id, models.Card.card_type, models.Card.name, models.SignupBonus.bonus_points, models.SignupBonus.minimum_spend)\
	.filter(models.SignupBonus.active == 1, models.Card.active == 1, models.Card.company.has(active=1))\
	.order_by(models.Company.name, models.SignupBonus.bonus_points.desc(),models.SignupBonus.minimum_spend, models.Card.name).all()

	cards = {'companies': []}

	for card in all_cards:
		if card in current_user.cards:
			continue
		if card.company_name not in cards['companies']:
			cards['companies'].append(card.company_name)
		cards[card.company_name] = cards.get(card.company_name, {'business':[],'personal':[]})
		cards[card.company_name][card.card_type].append(card)

	cards['companies'] = sorted(cards['companies'], key=lambda x:x.lower())

	return render_template('cards.html', cards=cards)

@app.route('/search/points_programs', methods=['GET', 'POST'])
@login_required
def search_points():
	if request.method == 'POST':
		print('posted')


	all_points = models.PointsProgram.query.filter(models.PointsProgram.active == 1).order_by(models.PointsProgram.name).all()

	programs = {'programs': []}

	for program in all_points:
		if program.name not in programs['programs']:
			programs['programs'].append(program.name)
		programs[program.name] = programs.get(program.name, {'rewards':[], 'cards':[]})

		programs[program.name]['cards'] = program.cards.join(models.SignupBonus).with_entities(models.Card.id, models.Card.name, models.SignupBonus.bonus_points, models.SignupBonus.minimum_spend).filter(models.SignupBonus.active == 1, models.Card.active == 1).order_by(models.SignupBonus.bonus_points.desc()).all()
		programs[program.name]['rewards'] = program.reward_programs.order_by(models.RewardProgram.program_name).all()


	return render_template('points_programs.html', programs = programs)

##############################################################
# Card Views
##############################################################

@app.route('/card/profile')
@login_required
def card_profile():
	card_id = request.args.get('card_id')

	card = models.Card.query.get(card_id)

	spending_categories = card.spending_categories.join(models.SpendingCategoryLookup)\
		.with_entities(models.SpendingCategory.name, models.SpendingCategoryLookup.company_name, models.SpendingCategoryLookup.earning_percent)\
		.filter(models.SpendingCategory.active == 1, models.SpendingCategoryLookup.active == 1)\
		.order_by(models.SpendingCategory.name, models.SpendingCategoryLookup.company_name).all()

	reward = card.signup_bonuses.filter_by(active=1).first()

	return render_template('card_page.html',card=card, reward=reward, spending_categories = spending_categories)


##############################################################
# Admin Views
##############################################################

@app.route('/admin')
@login_required
def admin():
	if not current_user.admin:
		return redirect(url_for('index'))

	return render_template('admin.html')

######################################################################
#  Views for Admin of Users
######################################################################

@app.route('/admin/users')
@login_required
def admin_users():
	if not current_user.admin:
		return redirect(url_for('index'))
	users = models.User.query.all()

	return render_template('admin_users.html', users=users)

@app.route('/admin/adjust_user')
@login_required
def adjust_user():
	if not current_user.admin:
		return redirect(url_for('index'))
	user_id = request.args.get('user_id')
	action = request.args.get('action')

	user = models.User.query.get(user_id)

	if action == 'admin':
		user.admin = not user.admin

	if action == 'status':
		user.active = not user.active

	db.session.commit()
	return redirect(url_for('admin_users'))

######################################################################
#  Views for Admin of Cards
######################################################################

@app.route('/admin/cards')
@login_required
def admin_cards():
	if not current_user.admin:
		return redirect(url_for('index'))

	company_id = request.args.get('company_id', None)
	company = None

	if company_id:
		company = models.Company.query.get(company_id)
		cards = company.cards.filter_by(active=1).order_by(models.Card.name).all()
	else:
		cards = models.Card.query.filter_by(active=1).order_by(models.Card.name).all()

	return render_template('admin_cards.html', company=company, cards=cards)


@app.route('/admin/card', methods=['GET','POST'])
@login_required
def admin_card():
	if not current_user.admin:
		return redirect(url_for('index'))

	card_id = request.args.get('card_id')
	company_id = request.args.get('company_id')

	card = None
	form = CardForm()

	if card_id:
		card = models.Card.query.get(card_id)
		form = CardForm(obj=card)
		company = card.company

	if company_id and not card_id:
		company = models.Company.query.get(company_id)
		form.company_id.data = company_id

	if request.method == 'POST':

		data = request.form
		new= False
		if not card:
			new = True

		card = models.Card() if not card else card
		card.points_program_id = data.get('points_program_id')
		card.company_id = data.get('company_id')
		card.name = data.get('name')
		card.card_type = data.get('card_type')
		card.apply_link_url = data.get('apply_link_url')
		card.terms_link_url = data.get('terms_link_url')
		card.ulu = current_user.username

		db.session.add(card)
		db.session.commit()

		file = request.files.get('image_file')
		if file and allowed_file(file.filename):
			file_type = '.' + file.filename.rsplit('.',1)[1].lower()
			image_filename = 'card_' + str(card.id) + file_type
			filename = secure_filename(image_filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			card.image_file = image_filename
		elif file and not allowed_file(file.filename):
			flash('File not approved file type. Please try again.')

		db.session.add(card)
		db.session.commit()

		if new:
			flash('Added {} to {}.'.format(card.name, card.company.name))
			return redirect(url_for('admin_card', card_id=card.id))

		flash('Updated {} {}.'.format(card.company.name, card.name))
		return redirect(url_for('admin_cards', company_id=card.company_id))

	form.points_program_id.choices = [(pp.id, pp.name) for pp in models.PointsProgram.query.filter_by(active=1).order_by(models.PointsProgram.name).all()]

	spending_categories = []
	signup_bonus = None

	if card:
		spending_categories = models.SpendingCategory.query\
			.join(models.SpendingCategoryLookup,models.SpendingCategory.id==models.SpendingCategoryLookup.spending_category_id)\
			.add_columns(models.SpendingCategoryLookup.id, models.SpendingCategory.name, models.SpendingCategoryLookup.company_name, models.SpendingCategoryLookup.earning_percent)\
			.filter(models.SpendingCategoryLookup.card_id == card.id, models.SpendingCategory.active == 1, models.SpendingCategoryLookup.active == 1)\
			.order_by(models.SpendingCategory.name, models.SpendingCategoryLookup.earning_percent.desc()).all()

		signup_bonus = card.signup_bonuses.filter_by(active=1).first()

	# for i in range(len(card.spending_categories)):
	# 	spending_categories.append((card.spending_categories[i].name, card.card_spending_categories[0].earning_percent))


	return render_template('admin_card.html', form=form, card=card, spending_categories = spending_categories, company=company, signup_bonus=signup_bonus)


@app.route('/admin/card/spending_category', methods=['GET', 'POST'])
@login_required
def admin_card_spending_category():
	if not current_user.admin:
		return redirect(url_for('index'))

	card_id = request.args.get('card_id')
	card_category_id = request.args.get('card_category_id')

	card = models.Card.query.get(card_id)

	spending_category_lookup = None
	form = CardSpendingCategoryForm(card_id=card_id)

	if card_category_id:
		spending_category_lookup = models.SpendingCategoryLookup.query.get(card_category_id)
		form = CardSpendingCategoryForm(obj=spending_category_lookup)

	if request.method == 'POST':

		spending_category_lookup = models.SpendingCategoryLookup() if not spending_category_lookup else spending_category_lookup

		spending_category_lookup.card_id = request.form.get('card_id')
		spending_category_lookup.spending_category_id = request.form.get('spending_category_id')
		if request.form.get('company_name', '') != '':
			spending_category_lookup.company_name = request.form.get('company_name')
		spending_category_lookup.earning_percent = request.form.get('earning_percent')
		spending_category_lookup.ulu = current_user.username

		db.session.add(spending_category_lookup)
		db.session.commit()

		# flash(message.format(spending_category.name))

		return redirect(url_for('admin_card', card_id=card_id))

	form.spending_category_id.choices = [(sc.id, sc.name) for sc in models.SpendingCategory.query.filter_by(active=1).order_by(models.SpendingCategory.name).all()]

	return render_template('admin_card_spending_category.html', form=form, lookup=spending_category_lookup, card=card)


@app.route('/admin/spending_categories', methods=['GET','POST'])
@login_required
def admin_spending_categories():
	if not current_user.admin:
		return redirect(url_for('index'))

	categories = models.SpendingCategory.query.filter_by(active=1).order_by(models.SpendingCategory.name).all()

	return render_template('admin_spending_categories.html', categories=categories)

@app.route('/admin/spending_category', methods=['GET', 'POST'])
@login_required
def admin_spending_category():
	if not current_user.admin:
		return redirect(url_for('index'))

	spending_category_id = request.args.get('spending_category_id')

	spending_category = None
	form = SpendingCategoryForm()

	if spending_category_id:
		spending_category = models.SpendingCategory.query.get(spending_category_id)
		form = SpendingCategoryForm(obj=spending_category)

	if request.method == 'POST':
		if spending_category == None:
			message = 'Added New Spending Category {}'
		else:
			message = 'Updated Spending Category {}'

		spending_category = models.SpendingCategory() if not spending_category else spending_category
		spending_category.name = request.form.get('name')
		spending_category.ulu = current_user.username

		db.session.add(spending_category)
		db.session.commit()

		return redirect(url_for('admin_spending_categories'))

	return render_template('admin_spending_category.html', form=form, spending_category=spending_category)


######################################################################
#  Views for Admin of Sign UP Bonuses
######################################################################

@app.route('/admin/card/signup_bonuses', methods=['GET','POST'])
@login_required
def admin_signup_bonuses():
	if not current_user.admin:
		return redirect(url_for('index'))

	card_id = request.args.get('card_id')
	card = models.Card.query.get(card_id)

	if request.method == 'POST':
		data = request.form
		new_bonus = models.SignupBonus()

		active_bonus = card.signup_bonuses.filter_by(active=1).first()

		if active_bonus:
			now = datetime.datetime.now()
			active_bonus.to_date = now
			active_bonus.active = 0
			new_bonus.from_date = now
			db.session.add(active_bonus)

		new_bonus.card_id = data.get('card_id')
		new_bonus.days_for_spend = data.get('days_for_spend')
		new_bonus.minimum_spend = data.get('minimum_spend')
		new_bonus.annual_fee = data.get('annual_fee')
		new_bonus.annual_fee_waived = int(data.get('annual_fee_waived'))
		new_bonus.bonus_points = data.get('bonus_points')
		new_bonus.ulu = current_user.username

		db.session.add(new_bonus)

		db.session.commit()

		flash('Added new Sign Up Bonus to {}'.format(card.name))

		return redirect(url_for('admin_card', card_id=card.id))

	signup_bonus = card.signup_bonuses.filter_by(active=1).first()

	if signup_bonus == None:
		signup_bonus = models.SignupBonus(card_id=card.id)

	form = SignupBonusForm(obj=signup_bonus)


	return render_template('admin_signup_bonuses.html', card=card, signup_bonus=signup_bonus, form=form)

@app.route('/admin/reward_programs', methods=['GET','POST'])
@login_required
def admin_reward_programs():
	if not current_user.admin:
		return redirect(url_for('index'))

	reward_programs = models.RewardProgram.query.filter_by(active=1).order_by(models.RewardProgram.category_name, models.RewardProgram.program_name).all()

	programs = {'categories': []}

	for rp in reward_programs:
		if rp.category_name not in programs['categories']:
			programs['categories'].append(rp.category_name)
		programs[rp.category_name] = programs.get(rp.category_name, [])
		programs[rp.category_name].append(rp)


	return render_template('admin_reward_programs.html', programs=programs)

@app.route('/admin/reward_program', methods=['GET', 'POST'])
@login_required
def admin_reward_program():
	if not current_user.admin:
		return redirect(url_for('index'))

	reward_program_id = request.args.get('reward_program_id')

	reward_program = None
	form = RewardProgramForm()

	if reward_program_id:
		reward_program = models.RewardProgram.query.get(reward_program_id)
		form = RewardProgramForm(obj=reward_program)

	if request.method == 'POST':
		if reward_program == None:
			message = 'Added New Reward Program {}'
		else:
			message = 'Updated Reward Program {}'

		reward_program = models.RewardProgram() if not reward_program else reward_program

		new_cat = request.form.get('new_category_name', '')

		if new_cat != '':
			reward_program.category_name = new_cat
		else:
			reward_program.category_name = request.form.get('category_name')
		reward_program.program_name = request.form.get('program_name')
		reward_program.company_name = request.form.get('company_name')
		reward_program.redeem_value = request.form.get('redeem_value')

		reward_program.ulu = current_user.username

		db.session.add(reward_program)
		db.session.commit()

		flash(message.format(reward_program.program_name))

		return redirect(url_for('admin_reward_programs'))

	categories  = db.session.query(models.RewardProgram.category_name).distinct().order_by(models.RewardProgram.category_name).all()

	form.category_name.choices = [(c[0], c[0]) for c in categories]

	return render_template('admin_reward_program.html', form=form, reward_program=reward_program)

######################################################################
#  Views for Admin of Companies
######################################################################

@app.route('/admin/companies', methods=['GET', 'POST'])
@login_required
def admin_companies():
	if not current_user.admin:
		return redirect(url_for('index'))

	companies = models.Company.query.filter_by(active=1).order_by(models.Company.name).all()

	return render_template('admin_companies.html', companies=companies)

@app.route('/admin/company', methods=['GET', 'POST'])
@login_required
def admin_company():
	if not current_user.admin:
		return redirect(url_for('index'))

	company_id = request.args.get('company_id')

	company = None
	form = CompanyForm()

	if company_id:
		company = models.Company.query.get(company_id)
		form = CompanyForm(obj=company)

	if request.method == 'POST':
		if company == None:
			message = 'Added New Copmany {}'
		else:
			message = 'Updated Company {}'

		company = models.Company() if not company else company
		company.name = request.form.get('name')
		company.ulu = current_user.username

		db.session.add(company)
		db.session.commit()

		flash(message.format(company.name))

		return redirect(url_for('admin_companies'))

	return render_template('admin_company.html', form=form, company=company)


######################################################################
#  Views for Admin of Points Programs
######################################################################

@app.route('/admin/points_programs')
@login_required
def admin_points_programs():
	if not current_user.admin:
		return redirect(url_for('index'))

	programs = models.PointsProgram.query.filter_by(active=1).order_by(models.PointsProgram.name).all()

	return render_template('admin_points_programs.html', programs=programs)

@app.route('/admin/points_program', methods=['GET', 'POST'])
@login_required
def admin_points_program():
	if not current_user.admin:
		return redirect(url_for('index'))

	program_id = request.args.get('program_id')

	program = None
	form = PointsProgramForm()

	if program_id:
		program = models.PointsProgram.query.get(program_id)
		form = PointsProgramForm(obj=program)

	if request.method == 'POST':

		if program == None:
			message = 'Added New Program {}'
			new = True
		else:
			message = 'Updated Program {}'
			new = False

		program = models.PointsProgram() if not program else program
		program.name = request.form.get('name')
		program.ulu = current_user.username

		db.session.add(program)
		db.session.commit()

		message = message.format(program.name)

		add_reward_program_id = request.form.get('add_reward_program_id', '')
		delete_reward_program_id = request.form.get('delete_reward_program_id', '')

		print(request.form)

		if add_reward_program_id != '':
			reward_program = models.RewardProgram.query.get(add_reward_program_id)
			program.reward_programs.append(reward_program)
			message = 'Added {} to {}'.format(reward_program.program_name, program.name)

		if delete_reward_program_id != '':
			reward_program = models.RewardProgram.query.get(delete_reward_program_id)
			program.reward_programs.remove(reward_program)
			message = 'Removed {} from {}'.format(reward_program.program_name, program.name)

		db.session.add(program)
		db.session.commit()

		flash(message)

	reward_programs = models.RewardProgram.query.order_by(models.RewardProgram.program_name).all()

	return render_template('admin_points_program.html', form=form, program=program, reward_programs=reward_programs)
