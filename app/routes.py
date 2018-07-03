from flask import render_template, flash, url_for, redirect
from app import app
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


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		flash('Login user {}, remember me {}'.format(form.username.data, form.remember_me.data))
		return redirect(url_for('index'))

	return render_template('login.html', title='Sign In', form=form)
