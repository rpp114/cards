from app import db, login, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeSerializer
import datetime

login_serializer = URLSafeSerializer(app.config['SECRET_KEY'])

@login.user_loader
def load_user(session_token):
    return User.query.filter_by(session_token=session_token).first()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(256), index=True, unique=True)
    email = db.Column(db.VARCHAR(256), index=True, unique=True)
    password = db.Column(db.VARCHAR(256))
    session_token = db.Column(db.VARCHAR(256))
    status = db.Column(db.VARCHAR(15), default='active')
    first_login = db.Column(db.SMALLINT())
    admin = db.Column(db.SMALLINT(), default=0)
    cards = db.relationship('Card', secondary='user_card_lookup')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_id(self):
        return str(self.session_token)

    def set_session_token(self):
        self.session_token = login_serializer.dumps([self.username,self.password,self.status])

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def adjust_admin(self):
        self.admin = not self.admin

####################################################
#  Card and Company Definitions -- User Join to Cards
####################################################

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(256), unique=True)
    cards = db.relationship('Card', backref='company', lazy='dynamic')

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points_program_id = db.Column(db.Integer, db.ForeignKey('points_program.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    name = db.Column(db.VARCHAR(256))
    card_type = db.Column(db.VARCHAR(15))
    apply_link_url = db.Column(db.TEXT)
    image_link_url = db.Column(db.TEXT)
    users = db.relationship('User', backref='card', secondary='user_card_lookup')
    signup_bonuses = db.relationship('SignupBonus', backref='card', lazy='dynamic')
    spending_categories = db.relationship('SpendingCategory', backref='card', secondary='spending_category_lookup')
    reward_categories = db.relationship('RewardCategory', backref='card', secondary='reward_category_lookup')

class UserCardLookup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    active_date = db.Column(db.DATETIME, default = datetime.datetime.now())
    expiration_date = db.Column(db.DATETIME)
    cancel_date = db.Column(db.DATETIME)
    status = db.Column(db.VARCHAR(15), default='active')
    user_cards = db.relationship('Card', backref=db.backref('user_cards', cascade='all, delete-orphan'))
    card_users = db.relationship('User', backref=db.backref('card_users', cascade='all, delete-orphan'))

####################################################
#  Points Programs and Sign Up Bonuses
####################################################

class PointsProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(256), unique=True)
    value = db.Column(db.Float)
    cards = db.relationship('Card', backref='points_program', lazy='dynamic')

class SignupBonus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    days_for_spend = db.Column(db.Integer)
    minimum_spend = db.Column(db.Integer)
    annual_fee = db.Column(db.Integer)
    annual_fee_waived = db.Column(db.VARCHAR(10))
    bonus_points = db.Column(db.Integer)
    from_date = db.Column(db.DATETIME, default=datetime.datetime.min)
    to_date = db.Column(db.DATETIME, default=datetime.datetime.max)
    status = db.Column(db.VARCHAR(15), default='active')

####################################################
#  Spending and Reward Category Info
####################################################

class RewardCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(256), unique=True)
    cards = db.relationship('Card', backref = 'reward_category', secondary='reward_category_lookup')

class RewardCategoryLookup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    reward_category_id = db.Column(db.Integer, db.ForeignKey('reward_category.id'))
    company_name = db.Column(db.VARCHAR(255))
    redeem_value = db.Column(db.Float)
    cards = db.relationship('Card', backref=db.backref('card_reward_categories', cascade='all, delete-orphan'))
    reward_categories = db.relationship('RewardCategory', backref=db.backref('reward_category_cards', cascade='all, delete-orphan'))

class SpendingCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(255), unique=True)
    cards = db.relationship('Card', backref = 'spending_category', secondary='spending_category_lookup')

class SpendingCategoryLookup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    spending_category_id = db.Column(db.Integer, db.ForeignKey('spending_category.id'))
    company_name = db.Column(db.VARCHAR(255))
    earning_percent = db.Column(db.Float)
    cards = db.relationship('Card', backref=db.backref('card_spending_categories', cascade='all, delete-orphan'))
    spending_categories = db.relationship('SpendingCategory', backref=db.backref('spending_category_cards', cascade='all, delete-orphan'))
