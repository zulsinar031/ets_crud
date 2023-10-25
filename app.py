from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib 
import json

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ets_db'

mysql = MySQL(app)

def check_user_exists(cursor, username):
    cursor.execute("""SELECT * FROM user WHERE user_name = %s""", ([username]))
    if cursor.fetchone() is None:
        return False
    else:
        return True

#@app.route('/')
@app.route('/ets_login', methods =['GET', 'POST'])
def login():
    if request.method == "POST":
        #user_id = uuid4()
        username = json.loads(request.data)["user_name"]
        password = json.loads(request.data)["user_password"]
        password = hashlib.sha256(password.encode("utf-8")).hexdigest()

        # Check if user exists
        cur = mysql.connection.cursor()
        #if check_user_exists(cur, username):
        #    return jsonify({"status": "failed", "message": "User already exists."})

        cur.execute(
            """SELECT * FROM user(user_name, user_password) VALUES (%s, %s, %s)""",
            ([username], [password]),
        )
        mysql.connection.commit()
        user = cur.fetchone()
        cur.close()
        if user :
            #session["token"] = username
            session["token"] = user[0]
            session["username"] = user[1]
            return jsonify({"status": "success", "message": "Succesfully log in"})
        else:
            return jsonify({"Credentials incorrect"})

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('user_email', None)
    return redirect(url_for('ets_login'))

@app.route('/ets_register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        #user_id = uuid4()
        username = json.loads(request.data)["user_name"]
        email = json.loads(request.data)["user_email"]
        password = json.loads(request.data)["user_password"]
        password = hashlib.sha256(password.encode("utf-8")).hexdigest()

        # Check if user exists
        cur = mysql.connection.cursor()
        if check_user_exists(cur, username):
            return jsonify({"status": "failed", "message": "User already exists."})

        cur.execute(
            """INSERT INTO users (user_name, user_email, user_password) VALUES (%s, %s, %s)""",
            ([username], [email], [password]),
        )
        mysql.connection.commit()
        cur.close()

        # Success
        return jsonify({"status": "success", "message": "Registration successful."})
    else:
        is_login = False
        if session.get("token"):
            is_login = True
        return render_template("ets_register.html", is_login=is_login)

if __name__ == '__main__':
    app.run(debug=True)
