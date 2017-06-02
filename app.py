from flask import Flask, abort, request, jsonify, g, url_for, render_template, flash, redirect, json,jsonify, make_response
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import TextField, PasswordField
from wtforms.validators import Required, Email
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import Fruit, User, Vote, VoteUI, HistoryUI, db


#### CONFIG ############################
app = Flask(__name__)
with app.app_context():
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


def get_sorted_fruit_votes():
    sfv = [] #sorted fruit vote
    try:
        sfv = sorted([VoteUI(fruit) for fruit in Fruit.query.all()], key=lambda x : x.vote_count, reverse=True)
    except:
        pass # some error, dismiss
    return sfv

def get_sorted_fruit_votes_json(status="success", msg="Get Votes OK"):
    json_objs = jsonify({"status": status, "message": msg,  "values" : [e.tojson() for e in get_sorted_fruit_votes()]})
    print("json:" + str(json_objs.get_data()))
    return json_objs

def get_sorted_fruit_votes_json_authenticated(status="success", msg="Get Votes OK"):
    json_objs = jsonify({ "status" : status, "message" : msg,  "values" : [e.tojson_authenticated() for e in get_sorted_fruit_votes()] })
    print("json:" + str(json_objs.get_data()))
    return json_objs

def get_votes(status="success", msg="Get Votes OK"):
     #add votes dials if user logged in
    if g.user.is_authenticated:
        return get_sorted_fruit_votes_json_authenticated(status, msg)
    return get_sorted_fruit_votes_json(status, msg)

@app.route('/get_fruit')
def get_all_votes():
   return get_votes()

@app.route('/')
def index():
    return render_template("index.html")


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
    flash('Successfully logged in', 'success')
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

@app.route('/get_history')
@login_required
def get_history():
    user_fruit_votes_uis = sorted([HistoryUI(vote) for vote in Vote.query.filter_by(user_id=g.user.id).all()], key=lambda x : x.vote_count, reverse=True) #Vote class
    return jsonify([e.tojson() for e in user_fruit_votes_uis])

@app.route('/history')
def history():
    return render_template('history.html')


#return true if commit to databse
def detect_change():
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
    #print("finished detect")
    return changed_count > 0

@app.route('/vote', methods=['POST'])
@login_required
def vote():
    #with app.app_context():
    if not detect_change():
        print("NO_CHANGE!!!")
        #flash('No Changed!!!', categories='info')
        return get_votes(status="info", msg="No Change!!!")
    print (" CHANGE!!!" )
    return get_votes()

@app.before_request
def before_request():
    #current_user = db.session.merge(current_user)
    g.user = current_user
    #g.user = db.session.merge(g.user)

if __name__ == '__main__':
    app.run(debug=True)
