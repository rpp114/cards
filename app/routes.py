from flask import render_template, flash, url_for, redirect, request
from app import app, db, models
from app.forms import LoginForm, CardForm, SignupForm, CompanyForm, SignupBonusForm,PointsProgramForm, RewardCategoryForm, ProgramRewardCategoryForm,SpendingCategoryForm,CardSpendingCategoryForm
from flask_login import current_user, login_user, login_required, logout_user
import datetime

@app.route('/')
@app.route('/index')
def index():
	if current_user.is_authenticated:
		return redirect(url_for('user_cards'))

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
		return redirect(url_for('user_cards'))

	form = SignupForm()

	if form.validate_on_submit():
		user = models.User(username=form.username.data, email=form.email.data, active=1)
		user.set_password(form.password.data)
		user.set_session_token()

		db.session.add(user)
		db.session.commit()

		login_user(user, remember=form.remember_me.data)

		return redirect(url_for('user_wallet'))

	return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('user_cards'))

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

@app.route('/user/wallet')
@login_required
def user_wallet():

	return render_template('user_wallet.html',user=current_user)

@app.route('/user/profile')
@login_required
def user_profile():

	return render_template('user_profile.html')

@app.route('/user/cards', methods=['GET', 'POST'])
@login_required
def user_cards():

	if request.method == 'POST':

		user_card = models.UserCardLookup(user_id=current_user.id,
										  card_id=request.form.get('card_id'))
		if request.form.get('activation_date', None):
			user_card.active_date = datetime.datetime.strptime(request.form.get('activation_date'),'%m/%d/%Y')
		if request.form.get('expiration_date', None):
			user_card.expiration_date = datetime.datetime.strptime(request.form.get('expiration_date'),'%m/%d/%Y')
		db.session.add(user_card)
		db.session.commit()
		card = models.Card.query.get(request.form.get('card_id'))
		flash('Added {} to your wallet'.format(card.name))

	cards = models.Card.query.all()


	# Needs Algo to Suggest Card
	suggested_card = models.Card.query.get(1)

	return render_template('user_cards.html', cards=cards, suggested_card = suggested_card, user_cards = current_user.cards)


##############################################################
# Card Views
##############################################################

@app.route('/card')
@login_required
def card_profile():
	card_id = request.args.get('card_id')

	card = models.Card.query.get(card_id)

	spending_categories = []

	for i in range(len(card.spending_categories)):
		spending_categories.append((card.spending_categories[i].name, card.card_spending_categories[0].earning_percent))

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

		db.session.add(card)
		db.session.commit()

		flash('Added {} to {}.'.format(card.name, card.company.name))

		if new:
			return redirect(url_for('admin_card', card_id=card.id))

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

		db.session.add(new_bonus)

		db.session.commit()

		flash('Added new Sign Up Bonus to {}'.format(card.name))

		return redirect(url_for('admin_card', card_id=card.id))

	signup_bonus = card.signup_bonuses.filter_by(active=1).first()

	if signup_bonus == None:
		signup_bonus = models.SignupBonus(card_id=card.id)

	form = SignupBonusForm(obj=signup_bonus)


	return render_template('admin_signup_bonuses.html', card=card, signup_bonus=signup_bonus, form=form)

@app.route('/admin/reward_categories', methods=['GET','POST'])
@login_required
def admin_reward_categories():
	if not current_user.admin:
		return redirect(url_for('index'))

	categories = models.RewardCategory.query.filter_by(active=1).order_by(models.RewardCategory.name).all()

	return render_template('admin_reward_categories.html', categories=categories)

@app.route('/admin/reward_category', methods=['GET', 'POST'])
@login_required
def admin_reward_category():
	if not current_user.admin:
		return redirect(url_for('index'))

	reward_category_id = request.args.get('reward_category_id')

	reward_category = None
	form = RewardCategoryForm()

	if reward_category_id:
		reward_category = models.RewardCategory.query.get(reward_category_id)
		form = RewardCategoryForm(obj=reward_category)

	if request.method == 'POST':
		if reward_category == None:
			message = 'Added New Reward Category {}'
		else:
			message = 'Updated Reward Category {}'

		reward_category = models.RewardCategory() if not reward_category else reward_category
		reward_category.name = request.form.get('name')

		db.session.add(reward_category)
		db.session.commit()

		flash(message.format(reward_category.name))

		return redirect(url_for('admin_reward_categories'))

	return render_template('admin_reward_category.html', form=form, reward_category=reward_category)

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

		db.session.add(program)
		db.session.commit()

		flash(message.format(program.name))

		if new:
			return redirect(url_for('admin_points_program', program_id=program.id))

		return redirect(url_for('admin_points_programs'))

	reward_categories = []

	if program:
		reward_categories = models.RewardCategory.query\
			.join(models.RewardCategoryLookup,models.RewardCategory.id==models.RewardCategoryLookup.reward_category_id)\
			.add_columns(models.RewardCategoryLookup.id, models.RewardCategory.name, models.RewardCategoryLookup.company_name, models.RewardCategoryLookup.redeem_value)\
			.filter(models.RewardCategoryLookup.points_program_id == program.id, models.RewardCategory.active == 1, models.RewardCategoryLookup.active == 1)\
			.order_by(models.RewardCategory.name, models.RewardCategoryLookup.redeem_value.desc()).all()

	print('reward_category:', reward_categories)

	return render_template('admin_points_program.html', form=form, program=program, reward_categories=reward_categories)

@app.route('/admin/points_program/reward_category', methods=['GET', 'POST'])
@login_required
def admin_program_reward_category():
	if not current_user.admin:
		return redirect(url_for('index'))

	program_id = request.args.get('program_id')
	program_category_id = request.args.get('program_category_id')

	program = models.PointsProgram.query.get(program_id)

	reward_category_lookup = None
	form = ProgramRewardCategoryForm(points_program_id=program_id)

	if program_category_id:
		reward_category_lookup = models.RewardCategoryLookup.query.get(program_category_id)
		form = ProgramRewardCategoryForm(obj=reward_category_lookup)

	if request.method == 'POST':

		reward_category_lookup = models.RewardCategoryLookup() if not reward_category_lookup else reward_category_lookup
		print(request.form)
		reward_category_lookup.points_program_id = request.form.get('points_program_id')
		reward_category_lookup.reward_category_id = request.form.get('reward_category_id')
		if request.form.get('company_name', '') != '':
			reward_category_lookup.company_name = request.form.get('company_name')
		reward_category_lookup.redeem_value = request.form.get('redeem_value')

		db.session.add(reward_category_lookup)
		db.session.commit()

		print('lookup:',reward_category_lookup)

		# flash(message.format(spending_category.name))

		return redirect(url_for('admin_points_program', program_id=program_id))

	form.reward_category_id.choices = [(rc.id, rc.name) for rc in models.RewardCategory.query.filter_by(active=1).order_by(models.RewardCategory.name).all()]

	form.points_program_id.data = program_id

	return render_template('admin_program_reward_category.html', form=form, lookup=reward_category_lookup, program=program)
