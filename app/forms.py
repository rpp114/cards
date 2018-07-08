from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CardProfileForm(FlaskForm):
    company_name = SelectField('Company Name')
    card_name = StringField('Card Name', validators=[DataRequired()])
    points_program = SelectField('Points Program')
    points = StringField('Points')
    point_value = StringField('Point Value')
    min_spend = StringField('Minimum Spend')
    days_to_spend = StringField('Days to Spend')
