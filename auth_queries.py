import psycopg2

def connect():
    c = psycopg2.connect("dbname=db_group_22")
    return c

def commit(query):
    c = connect()
    cur = c.cursor()
    cur.execute(query)
    c.commit()
    cur.close()
    c.close()

def fetch(query):
    c = connect()
    cur = c.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    c.close()
    return result

def new_user(username, email, password):
    commit(f"insert into users(uname,email,pass) values('{username}','{email}','{password}')")

def get_user_from_email(email):
    users = fetch(f"select * from users where email='{email}'")
    if len(users) != 1:
        return None
    return users[0]

def get_user_from_uname(uname):
    users = fetch(f"select * from users where uname='{uname}'")
    if len(users) != 1:
        return None
    return users[0]

def get_user_from_userid(userid):
    users = fetch(f"select * from users where userid='{userid}'")
    if len(users) != 1:
        return None
    return users[0]

def update_user_details(userid, uname, email):
    commit(f"update users set uname='{uname}', email='{email}' where userid={userid}")

def update_password(userid, password):
    commit(f"update users set pass='{password}' where userid={userid}")

def delete_user(userid):
    commit(f"delete from users where userid={userid}")
