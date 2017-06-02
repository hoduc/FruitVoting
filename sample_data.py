from models import Fruit, User, Vote, VoteUI, HistoryUI, db
from app import app

def insert_data(db, l):
    for e in l:
        db.session.add(e)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
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
        
