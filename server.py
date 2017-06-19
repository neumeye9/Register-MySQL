from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
from flask_bcrypt import Bcrypt # or try flask.ext.bcrypt

app = Flask(__name__)
mysql = MySQLConnector(app,'registrationdb')
app.secret_key="SecretGarden"
bcrypt = Bcrypt(app)

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
Name_REGEX = re.compile(r'^[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    session['username'] = request.form['username']
    query = "SELECT * FROM users WHERE username = '{}'".format(session['username'])
    check = mysql.query_db(query)
    print check
    print check[0]['password']

    # if you are looking for a specific column value, i.e. a username, know you have to access a dictionary within a list to compare the values
    
    #YOU MAY NEED TO FLIP FLOP THESE

   
    if len(request.form['password']) < 1:
        print "1"
        flash("You must enter your password")
        return redirect('/')
    if bcrypt.check_password_hash(check[0]['password'],request.form['password']) == False :
        print "2"
        flash("Incorrect Password Entered")
        return redirect('/')
    if len(check) == 0:
        print "Failed"
        flash("The username you have entered does not exist, please try again or register below.")
        return redirect('/')
    if check[0]['username'] != session['username']:
        flash("The username you have entered does not exist, please try again or register below")
        return redirect('/')
    else:
        return render_template('main.html')
    
@app.route('/register')
def register():
        return render_template('register.html')

@app.route('/form', methods=['POST'])
def info():
    session['first'] = request.form['first']
    session['last'] = request.form['last']
    session['username'] = request.form['username']
    session['email'] = request.form['email']
    session['password'] = request.form['password']
    session['passwordconfirm'] = request.form['passwordconfirm']

    query1 = "SELECT username FROM users WHERE username = '{}'".format(session['username'])
    print query1
    check = mysql.query_db(query1)
    print check

    
   
    if 'register' in request.form and len(check) == 0: 
        validation = True
        if len(request.form['first']) < 1:
            flash("First Name cannot be empty!")
            validation = False
        if not request.form['first'].isalpha():
            flash("First Fame can only include letters")
            validation = False
        if len(request.form['last']) < 1:
            flash("Last Name cannot be empty!")
            validation = False
        if not request.form['last'].isalpha():
            flash("Last Name can only include letters")
            validation = False
        if len(request.form['email']) < 1:
            flash("Email cannot be empty")
            validation = False
        if not EMAIL_REGEX.match(request.form['email']):
            flash("Not a valid Email address")
            validation = False
        if len(request.form['password']) < 1:
            flash("Password is required.")
            validation = False
        if len(request.form['password']) < 8:
            flash("Password must be longer than 8 characters")
            validation = False
        if len(request.form['passwordconfirm']) < 1:
            flash("Password  Confirmation is required.")
            validation = False
        if not request.form['password'] == request.form['passwordconfirm']:
            flash("Password Confirmation does not enter Password")
            validation = False 
        if validation:
            pw_hash = bcrypt.generate_password_hash(session['password'])
            print pw_hash

            query2 = "INSERT INTO users(first_name,last_name,username,email,password,created_at,updated_at) VALUES( :first, :last, :username, :email, :pw_hash, NOW(), NOW())"
            print query2

            data = {
                'first': request.form['first'],
                'last': request.form['last'],
                'username': request.form['username'],
                'email': request.form['email'],
                'pw_hash': pw_hash
            
            }

            mysql.query_db(query2,data)
            return render_template('main.html')
    return redirect('/register')
    ##always redirect when submitting a form 
            
app.run(debug=True)