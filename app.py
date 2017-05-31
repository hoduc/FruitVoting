from flask import Flask, abort, request, jsonify, g, url_for, render_template, flash, redirect
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import TextField, PasswordField
from wtforms.validators import Required, Email
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import Fruit, User, Vote, VoteUI, HistoryUI, db


#### CONFIG ############################
app = Flask(__name__)
app.config.from_pyfile('config.cfg')

#cross site forgery protect
csrf = CSRFProtect()
csrf.init_app(app)

#db
db.init_app(app)
#login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
#### CONFIG ############################

@app.route('/')
def index():
    vote_uis = sorted([VoteUI(fruit) for fruit in Fruit.query.all()], key=lambda x : x.vote_count, reverse=True)
    return render_template('index.html', fruit_votes=vote_uis)


@login_manager.user_loader
def get_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    username = request.form['username'].encode('utf-8')
    password = request.form['password'].encode('utf-8')
    #check if user exist
    user_db = User.query.filter_by(username=username).first()
    if user_db:
        flash("User already existed!!!")
        return render_template("signup.html")
    
    user = User(username, password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    #flash('Done register!!!')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
@login_required
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
@login_required
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
