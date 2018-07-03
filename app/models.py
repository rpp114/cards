from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(256), index=True, unique=True)
    email = db.Column(db.VARCHAR(256), index=True, unique=True)
    password = db.Column(db.VARCHAR(256))
    session_token = db.Column(db.VARCHAR(256))
    rewards = db.relationship('Reward', secondary='user_reward_lookup')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_id(self):
        return str(self.session_token)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(256), unique=True)
    cards = db.relationship('Card', backref='company', lazy='dynamic')

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    name = db.Column(db.VARCHAR(256), unique=True)
    card_type = db.Column(db.VARCHAR(15))
    apply_link_url = db.Column(db.TEXT)
    image_link_url = db.Column(db.TEXT)
    rewards = db.relationship('Reward', backref='card', lazy='dynamic')

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    name = db.Column(db.VARCHAR(256), unique=True)
    days_for_spend = db.Column(db.Integer)
    minimum_spend = db>Column(db.Integer)
    annual_fee = db.Column(db.Integer)
    bonus_points = db.Column(db.Integer)
    from_date = db.Column(db.DATETIME)
    to_date = db.Column(db.DATETIME)
    status = db.Column(db.VARCHAR(50))
    points_program = db.relationship('PointsProgram', backref='reward', uselist=False)
    users = db.relationship('User', secondary='user_reward_lookup')

class PointsPrograms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'))
    name = db.Column(db.VARCHAR)
    value = db.Column(db.Decimal(10,2))

class UserRewardLookup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reward_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    rewards = db.relationship('Reward', backref=db.backref('user_rewards', cascade='all, delete-orphan'))
    users = db.relationship('Card', backref=db.backref('user_rewards', cascade='all, delete-orphan'))
    active_date = db.Column(db.DATETIME)
    cancel_date = db.Column(db.DATETIME)
    status = db.Column(db.VARCHAR(256))
