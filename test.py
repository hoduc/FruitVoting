####TODO#####
## OAuth ##

from flask import Flask
app = Flask("FruitVoting")
app.config['DEBUG'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

users = ["Sam","John"]
items = ["Apple", "Orange", "Banana", "Pineapple"]

users_items = [(0,0,5),(0,3,3),(1,0,5),(1,1,2)] #vote


@app.route("/items")
def get_items():
    its = []
    for i,item in enumerate(items):
        item_vote_count = 0
        for user_item in users_items:
            if user_item[1] == i:
                item_vote_count += user_item[2]
        its.append((i,item,item_vote_count))
    return "<br>".join([ str(it) for it in its])

def validate_item(item_id):
    return item_id > 0 and item_id < len(items)

@app.route("/items/<int:item_id>/votes", methods=['POST'])
def post_vote(item_id):
    if validate_item(item_id):
        return "not yet"
    return "Invalidate item id:" + item_id


def get_user(user_id):
    for (i,name) in enumerate(users):
        if i == user_id:
            return users[i]
    return None    

def get_items_given_user(user_id, user):
    return [str((user_id, user,items[ui[1]], ui[2])) for ui  in users_items if ui[0] == user_id]

@app.route("/users/<int:user_id>/votes")
def get_voted_items(user_id):
    user = get_user(user_id)
    if user:
        return "<br>".join(get_items_given_user(user_id, user))
    return "No user with id : " + str(user_id)

@app.route("/users")
def create_user():
    return "This is create_user site"


if __name__ == "__main__":
    app.run()
