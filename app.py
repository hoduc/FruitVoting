from flask import Flask, abort, request, jsonify, g, url_for, render_template, flash, redirect
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import TextField, PasswordField
from wtforms.validators import Required, Email
from flask_bcrypt import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = "!jsfhahdkahskdf"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:@localhost/fruitvote"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
csrf = CSRFProtect()
csrf.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

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

    def __init__(self, username, password, is_admin):
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

@login_manager.user_loader
def get_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("login.html")
    user = User(request.form['username'], request.form['password'])
    db.session.add(user)
    db.session.commit()
    flash('Done register!!!')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username'].encode('utf-8')
    password = request.form['password'].encode('utf-8')
    user_db = User.query.filter_by(username=username).first()
    if user_db is None or bcrypt.hashpw(password, user_db.password.encode('utf-8')) != user_db.password.encode('utf-8'):
        flash('Username/Password combination is not correct', 'error')
        return redirect(url_for('login'))
    login_user(user_db)
    flash('Successfully logged in')
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create_fruit')
@login_required
def create_fruit():
    if request.method == 'POST':
        fruit = Fruit(request.form['name'])
        db.session.add(fruit)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_fruit.html')

@app.route('/history')
@login_required
def history():
    user_fruit_votes_uis = [HistoryUI(vote) for vote in Vote.query.filter_by(user_id=g.user.id).all()] #Vote class
    return render_template('history.html', user_fruit_votes=user_fruit_votes_uis)
    

@app.route('/')
def index():
    vote_uis = sorted([VoteUI(fruit) for fruit in Fruit.query.all()], key=lambda x : x.vote_count, reverse=True)
    return render_template('index.html', fruit_votes=vote_uis)

@app.route('/vote', methods=['POST'])
@login_required
def vote():
    changed_count = 0
    for (fruit_name, new_vote) in request.form.iteritems():
        if fruit_name == 'csrf_token':
            continue
        new_vote = int(new_vote.decode('utf-8'))
        if new_vote <= 0:
            continue
        is_new_fruit = True
        for v in g.user.votes:
            if v.fruit.name == fruit_name:
                print("fruit:" + fruit_name + " changed!!!")
                v.vote_count += new_vote
                db.session.add(v)
                changed_count += 1
                is_new_fruit = False
                break
        if not is_new_fruit:
            continue
        #never ever vote for this yet
        print("new fruit:" + fruit_name + "=>" + str(new_vote))
        fruit_db = Fruit.query.filter_by(name=fruit_name).first()
        nv = Vote(g.user, fruit_db, new_vote)
        db.session.add(nv)
        changed_count += 1
    if changed_count:
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()
    return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user = current_user

if __name__ == '__main__':
    app.run(debug=True)
