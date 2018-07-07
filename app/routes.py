from flask import render_template, flash, url_for, redirect, request
from app import app, db, models
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
	title = 'Travel Hacker'

	user = {'username': 'Ray'}

	posts = [
	{'author': {'username': 'Sarah'},
	 'body': 'Nice day huh?'},
	{'author': {'username': 'Ted'},
	 'body': 'Sure is'}
	]

	return render_template('index.html', title=title, user=user, posts=posts)

@app.route('/how_it_works')
def how_it_works():

	return render_template('how_it_works.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		flash('Login user {}, remember me {}'.format(form.username.data, form.remember_me.data))
		return redirect(url_for('index'))

	return render_template('login.html', title='Sign In', form=form)

@app.route('/user/wallet')
def wallet():

	return render_template('wallet.html')

@app.route('/user/cards')
def user_cards():

	companies = models.Company.query.order_by(models.Company.name).all()

	suggested_card = models.Reward.query.filter_by(card_id=304).first()

	return render_template('user_cards.html', companies=companies, suggested_card = suggested_card)

@app.route('/card')
def card_profile():
	card_id = request.args.get('card_id')

	card = models.Card.query.get(card_id)

	reward = card.rewards.filter_by(status='active').first()

	return render_template('card_page.html', reward=reward)
