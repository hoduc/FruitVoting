from app2 import db
from app2 import User
from app2 import Fruit
from app2 import Vote



def insert_data(db, l):
    for e in l:
        db.session.add(e)

if __name__ == '__main__':
    db.create_all()
    #db.session.commit()

    sam = User("Sam", "123", False)
    alex = User("Alex", "456", False)
    apple = Fruit("Apple")
    pineApple = Fruit("PineApple")
    banana = Fruit("Banana")
    
    sam_vote_apple = Vote(sam, apple, 5)
    alex_vote_apple = Vote(alex, apple, 2)
    alex_vote_pineApple = Vote(alex, pineApple, 10)
    insert_data(db, [sam,alex]) #user
    insert_data(db, [apple, pineApple, banana]) #fruit
    insert_data(db, [sam_vote_apple, alex_vote_apple, alex_vote_pineApple]) #vote
    db.session.commit()
    db.session.close()
        
