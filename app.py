from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ets_db'

mysql = MySQL(app)

@app.route('/')
@app.route('/ets_login', methods =['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            return "Please fill in all fields."

        db = mysql.connection
        cursor = db.cursor()

        cursor.execute("SELECT user_id, user_name FROM users WHERE user_email = %s AND user_password = %s",
                       (email, password))
        user = cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['user_id'] = user['user_id']
            session['user_name'] = user['user_name']
            session['user_email'] = user['user_email']
            mesage = 'Logged in successfully !'
            return render_template('user.html', mesage = mesage)
        else: 
            mesage = 'Please enter the correct email/password!'
        cursor.close()
        db.close()
    return render_template('ets_login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('user_email', None)
    return redirect(url_for('ets_login'))

@app.route('/ets_register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['user_name']
        email = request.form['user_email']
        password = request.form['user_password']

        if not name or not email or not password:
            return "Please fill in all fields."

        db = mysql.connection
        cursor = db.cursor()

        existing_user = cursor.fetchone()
        if existing_user:
            return "User with this email already exists. Please use a different email."

        try:
            cursor.execute("INSERT INTO users (user_name, user_email, user_password) VALUES (%s, %s, %s)",
                        (name, email, password))
            db.commit()
            cursor.close()
            db.close()
            mesage = "Registration sucessful"
            return render_template('ets_login.html', mesage = mesage)
        except Exception as e:
                return render_template('ets_register.html', mesage="registration failed")

    return render_template('ets_register.html')

if __name__ == '__main__':
    app.run(debug=True)
