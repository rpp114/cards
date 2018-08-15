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
    active = db.Column(db.BOOLEAN(), default=1)
    first_login = db.Column(db.BOOLEAN(), default=1)
    admin = db.Column(db.BOOLEAN(), default=0)
    cards = db.relationship('Card', secondary='user_card_lookup')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_id(self):
        return str(self.session_token)

    def set_session_token(self):
        self.session_token = login_serializer.dumps([self.username,self.password,self.active])

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


####################################################
#  Card and Company Definitions -- User Join to Cards
####################################################

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(256), unique=True)
    active = db.Column(db.BOOLEAN(), default=1)
    ulu = db.Column(db.VARCHAR(50))
    cards = db.relationship('Card', backref='company', lazy='dynamic')

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points_program_id = db.Column(db.Integer, db.ForeignKey('points_program.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    name = db.Column(db.VARCHAR(256))
    card_type = db.Column(db.VARCHAR(15))
    apply_link_url = db.Column(db.TEXT)
    terms_link_url = db.Column(db.TEXT)
    image_file = db.Column(db.TEXT)
    active = db.Column(db.BOOLEAN(), default=1)
    ulu = db.Column(db.VARCHAR(50))
    users = db.relationship('User', backref='card', secondary='user_card_lookup')
    signup_bonuses = db.relationship('SignupBonus', backref='card', lazy='dynamic')
    spending_categories = db.relationship('SpendingCategory', backref='card', secondary='spending_category_lookup')


class UserCardLookup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    active_date = db.Column(db.DATETIME, default = datetime.datetime.now())
    expiration_date = db.Column(db.DATETIME)
    cancel_date = db.Column(db.DATETIME)
    active = db.Column(db.BOOLEAN(), default=1)
    status = db.Column(db.VARCHAR(10), default='active')
    user_cards = db.relationship('User', backref=db.backref('user_cards', cascade='all, delete-orphan'))
    card_users = db.relationship('Card', backref=db.backref('card_users', cascade='all, delete-orphan'))

####################################################
#  Points Programs and Sign Up Bonuses
####################################################

class PointsProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(256), unique=True)
    active = db.Column(db.BOOLEAN(), default=1)
    ulu = db.Column(db.VARCHAR(50))
    cards = db.relationship('Card', backref='points_program', lazy='dynamic')
    reward_categories = db.relationship('RewardCategory', backref='points_program', secondary='reward_category_lookup')


class SignupBonus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    days_for_spend = db.Column(db.Integer)
    minimum_spend = db.Column(db.Integer)
    annual_fee = db.Column(db.Integer)
    annual_fee_waived = db.Column(db.BOOLEAN(), default=0)
    bonus_points = db.Column(db.Integer)
    from_date = db.Column(db.DATETIME, default=datetime.datetime(1,1,1,0,0,0))
    to_date = db.Column(db.DATETIME, default=datetime.datetime(9999,12,31,23,59,59))
    active = db.Column(db.BOOLEAN(), default=1)
    ulu = db.Column(db.VARCHAR(50))

####################################################
#  Spending and Reward Category Info
####################################################

class RewardCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(256), unique=True)
    active = db.Column(db.BOOLEAN(), default=1)
    ulu = db.Column(db.VARCHAR(50))
    programs = db.relationship('PointsProgram', backref = 'reward_category', secondary='reward_category_lookup')

class RewardCategoryLookup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points_program_id = db.Column(db.Integer, db.ForeignKey('points_program.id'))
    reward_category_id = db.Column(db.Integer, db.ForeignKey('reward_category.id'))
    company_name = db.Column(db.VARCHAR(255), default="All")
    redeem_value = db.Column(db.Float)
    active = db.Column(db.BOOLEAN(), default=1)
    ulu = db.Column(db.VARCHAR(50))
    programs = db.relationship('PointsProgram', backref=db.backref('points_program_reward_categories', cascade='all, delete-orphan'))
    reward_categories = db.relationship('RewardCategory', backref=db.backref('reward_category_points_programs', cascade='all, delete-orphan'))

class SpendingCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(255), unique=True)
    active = db.Column(db.BOOLEAN(), default=1)
    ulu = db.Column(db.VARCHAR(50))
    cards = db.relationship('Card', backref = 'spending_category', secondary='spending_category_lookup')

class SpendingCategoryLookup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    spending_category_id = db.Column(db.Integer, db.ForeignKey('spending_category.id'))
    company_name = db.Column(db.VARCHAR(255), default="All")
    earning_percent = db.Column(db.Float)
    active = db.Column(db.BOOLEAN(), default=1)
    ulu = db.Column(db.VARCHAR(50))
    cards = db.relationship('Card', backref=db.backref('card_spending_categories', cascade='all, delete-orphan'))
    spending_categories = db.relationship('SpendingCategory', backref=db.backref('spending_category_cards', cascade='all, delete-orphan'))
