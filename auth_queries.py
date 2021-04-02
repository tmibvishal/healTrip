import db

def new_user(username, email, password):
    db.commit("insert into users(uname,email,pass) values(%s, %s, %s)", (username, email, password))

def get_user_from_email(email):
    users = db.fetch("select * from users where email=%s", (email, ))
    if len(users) != 1:
        return None
    return users[0]

def get_user_from_uname(uname):
    users = db.fetch("select * from users where uname=%s", (uname, ))
    if len(users) != 1:
        return None
    return users[0]

def get_user_from_userid(userid):
    users = db.fetch("select * from users where userid=%s", (userid, ))
    if len(users) != 1:
        return None
    return users[0]

def update_user_details(userid, uname, email):
    db.commit("update users set uname=%s, email=%s where userid=%s", (uname, email, userid))

def update_password(userid, password):
    db.commit("update users set pass=%s where userid=%s", (password, userid))

def delete_user(userid):
    db.commit("delete from users where userid=%s", (userid, ))

def disable_city(city):
    "hotels, airport codes"
    pass

def enable_city(city):
    pass