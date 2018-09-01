from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField, RadioField, HiddenField, DateField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from app import db, models

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PasswordChangeForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2',message="Please make the passwords match!")])
    password2 = PasswordField('Password Confirm', validators=[DataRequired()])

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2',message="Please make the passwords match!")])
    password2 = PasswordField('Password Confirm', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_username(self, username):
        user = models.User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different UserName')

    def validate_email(self, email):
        user = models.User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different Email')

class CardForm(FlaskForm):
    company_id = HiddenField('Company Name')
    name = StringField('Card Name', validators=[DataRequired()])
    card_type = RadioField('Card Type', choices=[('personal', 'Personal'), ('business', 'Business')])
    points_program_id = SelectField('Points Program')
    apply_link_url = StringField('Application Link')
    terms_link_url = StringField('Terms Link')
    image_file = FileField('Image Upload')

class CompanyForm(FlaskForm):
    name = StringField('Company Name')

class SignupBonusForm(FlaskForm):
    card_id = HiddenField('Card Name')
    days_for_spend = StringField('Days to Min Spend')
    minimum_spend = StringField('Minimum Spend')
    annual_fee = StringField('Annual Fee')
    annual_fee_waived = RadioField('Annual Fee Waived', choices=[(1, 'Yes'),(0, 'No')])
    bonus_points = StringField('Bonus Points')

class PointsProgramForm(FlaskForm):
    name = StringField('Program Name')

class RewardCategoryForm(FlaskForm):
    reward_program_id = SelectField('Rewards Program Name')

class RewardProgramForm(FlaskForm):
    category_name = SelectField('Reward Category Name')
    program_name = StringField('Reward Program Name')
    company_name = StringField('Reward Company Name')
    redeem_value = StringField('Point Value ($)')

class SpendingCategoryForm(FlaskForm):
    name = StringField('Spending Category Name')

class CardSpendingCategoryForm(FlaskForm):
    card_id = HiddenField('Card Name')
    spending_category_id = SelectField('Spending Category Name')
    company_name = StringField('Spending Company Name')
    earning_percent = StringField('Earning Percent')

class UserCardForm(FlaskForm):
    card_id = HiddenField()
    user_id = HiddenField()
    active_date = DateField('Activation Date')
    expiration_date = DateField('Expiration Date')
    cancel_date = DateField('Cancel Date')
