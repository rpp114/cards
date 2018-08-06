from flask import render_template, flash, url_for, redirect, request
from app import app, db, models
from app.forms import LoginForm, CardProfileForm, SignupForm
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
		user = models.User(username=form.username.data, email=form.email.data, status='active')
		user.set_password(form.password.data)
		user.set_session_token()

		db.session.add(user)
		db.session.commit()

		login_user(user, remember=form.remember_me.data)

		return redirect(url_for('wallet'))

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

		flash('Logged in user: {}'.format(current_user.username))
		return redirect(url_for('wallet'))

	return render_template('login.html', title='Sign In', form=form)



##############################################################
# Users Views
##############################################################

@app.route('/user/wallet')
@login_required
def wallet():

	return render_template('wallet.html',user=current_user)

@app.route('/user/profile')
@login_required
def user_profile():

	return render_template('user_profile.html')

@app.route('/user/cards', methods=['GET', 'POST'])
@login_required
def user_cards():

	if request.method == 'POST':
		curr_time = datetime.datetime.now()
		card = models.Card.query.get(request.form.get('card_id'))

		user = current_user
		user.cards.append(card)
		db.session.add(user)
		db.session.commit()
		flash('Added {} to your wallet'.format(card.name))

	companies = models.Company.query.order_by(models.Company.name).all()


	# Needs Algo to Suggest Card
	suggested_card = models.Card.query.get(1)

	return render_template('user_cards.html', companies=companies, suggested_card = suggested_card, user_cards = current_user.cards)


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

	reward = card.signup_bonuses.filter_by(status='active').first()

	return render_template('card_page.html',card=card, reward=reward, spending_categories = spending_categories)


##############################################################
# Admin Views
##############################################################

@app.route('/admin/card')
@login_required
def admin_card_profile():
	card_id = request.args.get('card_id')

	spending_categories = []

	for i in range(len(card.spending_categories)):
		spending_categories.append((card.spending_categories[i].name, card.card_spending_categories[0].earning_percent))

	reward = card.signup_bonuses.filter_by(status='active').first()

	return render_template('admin_card_page.html',card=card, reward=reward, spending_categories = spending_categories)
