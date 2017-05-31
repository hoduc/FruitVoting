from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt
db = SQLAlchemy()
############ MODELS ##########################

class Fruit(db.Model):
    __tablename__ = 'fruits'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), unique=True)
    
    def __init__(self, name):
        self.name = name
    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128), unique=True)
    is_admin = db.Column(db.Boolean, unique=False, default=False) 

    def __init__(self, username, password, is_admin = False):
        self.username = username
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())
        self.is_admin = is_admin

    #overide methods for flask-login
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return unicode(self.id)
    def __repr__(self):
        return '[User : %r]' % (self.username)


class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('votes', lazy='dynamic'))
    fruit_id = db.Column(db.Integer, db.ForeignKey('fruits.id'))
    fruit = db.relationship('Fruit', backref=db.backref('votes', lazy='dynamic'))
    vote_count = db.Column(db.Integer, nullable=False)

    def __init__(self, user, fruit, vote_count = 0):
        self.user = user
        self.fruit = fruit
        self.vote_count = vote_count

    def __repr__(self):
        return '[User : %r / Fruit : %r / Vote_count : %r]' % (self.user, self.fruit, self.vote_count)

class VoteUI:
    def __init__(self, fruit):
        print("fruit_name:" + fruit.name)
        for vote in fruit.votes:
            print("vc:" + str(vote.vote_count))
        self.name = fruit.name
        self.vote_count = sum([vote.vote_count for vote in fruit.votes])

class HistoryUI:
    def __init__(self, vote):
       self.fruit_name = vote.fruit.name
       self.vote_count = vote.vote_count
       
       
############ END MODELS ##########################
