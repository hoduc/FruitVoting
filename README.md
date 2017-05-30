# FruitVoting
Fruit Voting -- Upvote your best fruit

# Dependencies/Installation
* Flask packages
> pip install Flask .#main package [Link](http://flask.pocoo.org)

> pip install flask-login . #manage login [Link](https://flask-login.readthedocs.io/en/latest/#installation)

> pip install Flask-WTF . #form-related [Link](http://flask-wtf.readthedocs.io/en/stable/install.html)

> pip install sqlalchemy #sql-alchemy

> pip install SQLAlchemy-Utils

> pip install Flask-SQLAlchemy #Flask SQLAlchemy binding

> pip install psycopg2 #python PostgreSQL driver

> pip install bcrypt . #Hash lib

> pip install Flask-Bcrypt . #Flask hash lib binding

* PostgreSQL 9.5.5 [LINK](https://www.postgresql.org/download/) . [More Instruction](https://github.com/hoduc/rat_lipid_map/wiki/Rat-Lipid-Map-Wiki)


# Steps to run

* Create a database, assuming default user (postgres)

> psql -U postgres

> postgres=# create database fruitvote owner postgres

* Insert sample data : Insert the following data. Row is id-auto-increment implicitly.
  * USERS
    * USERNAME | PASSWORD
      -------- | --------
      Sam | ????
      Alex | ????
  * FRUITS
    * NAME |
      ---- |
      Apple |
      PineApple |
      Banana |
   * VOTES ( User vote )
     * USER_ID | FRUIT_ID | VOTE_COUNT
       ------- | -------- | ----------
       1 | 1 | 5 # Sam vote apple 5
       2 | 1 | 2 # Alex vote apple 2
       2 | 2 | 10 # Alex vote pineApple 10
       
 ==> At index(homepage), we would expect to see the following:
 
 FRUIT | VOTES
 ----- | -----
 Apple | 7
 PineApple | 10
 Banana | 0

> python sample_data.py
 
* Once User log in, next to each votes, number dial will appear to vote. Click submit to vote. **NOTE**: Any number <= 0 will be ignored.    



# TO DO
- [ ] Automation scripts : Windows & Bash.
