from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
import numpy as np
import pandas as pd
import plotly as pt
import plotly.express as px
import plotly.io as pio
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
engine_name = db.get_engine(app=app)

# how to pass username to pandas query
# Put result to plotly graphs

@app.route("/",methods=['GET','POST'])
def index():
    return render_template("index.html") 

@app.route("/profile",methods=['GET','POST'])
def profile():
    username = session["username"]
    # Get count of all logged expenses
    sql = "SELECT COUNT(expense_id) FROM expenses JOIN users ON expenses.user_id = users.user_id WHERE users.username=:username"
    result = db.session.execute(sql, {"username":username})
    expenses_count = result.fetchone()[0]
    # Return table of expenses as dataframe
    df = pd.read_sql_query("SELECT expense_date,amount,category,note FROM expenses JOIN users ON expenses.user_id = users.user_id WHERE users.username=%(u)s ORDER BY expense_date DESC",engine_name, params={"u":username})
    # Create pie chart of expense structure
    df_pie = df.groupby('category', as_index=False).agg({"amount": "sum"})
    expense_pie = px.pie(data_frame=df_pie,values='amount',names='category',color='category')
    expense_pie = pt.offline.plot(expense_pie,output_type='div')
    return render_template("profile.html",expense_count=expenses_count,pie=expense_pie,tables=[df.to_html(classes='data',header="true",justify="center",max_rows=10,index=False)]) 

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    # Give session the username
    session["username"] = username
    # Verify user and password
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone() 
    if user == None:
        del session["username"]
    else:
        hash_value = user[0]
        if check_password_hash(hash_value,password):
            return redirect("/profile")
        else:
            del session["username"] 
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/signup")
def signup():
    return render_template("signup.html") 

@app.route("/registration-complete", methods=["GET","POST"])
def registration_complete():
    username = request.form["username"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO users (username, first_name, last_name, email, password, registration_time) VALUES (:username,:first_name,:last_name,:email,:password, NOW())"    
    db.session.execute(sql, {"username":username,"first_name":first_name,"last_name":last_name,"password":hash_value,"email":email})
    db.session.commit()
    return redirect("/")

@app.route("/new-expense")
def new_expense():
    return render_template("expense.html")
    
@app.route("/send-expense", methods=["POST"])
def send_expense():
    amount = request.form["amount"]
    expense_date = request.form["expense_date"]
    category = request.form["category"]
    note = request.form["note"]
    # Fetch used_id
    username = session["username"]
    sql = "SELECT user_id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    sql = "INSERT INTO expenses (amount,expense_date,category,user_id, note) VALUES (:amount,:expense_date,:category,:user_id,:note)"
    db.session.execute(sql, {"amount":amount, "expense_date":expense_date, "category":category, "user_id":user_id, "note":note})
    db.session.commit()
    return redirect("/profile")

@app.route("/new-income")
def new_income():
    return render_template("income.html")

@app.route("/send-income", methods=["POST"])
def send_income():
    amount = request.form["amount"]
    income_date = request.form["income_date"]
    category = request.form["category"]
    note = request.form["note"]
    # Fetch used_id
    username = session["username"]
    sql = "SELECT user_id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    sql = "INSERT INTO incomes (income_date,amount,category,user_id, note) VALUES (:income_date,:amount,:category,:user_id,:note)"
    db.session.execute(sql, {"income_date":income_date, "amount":amount, "category":category, "user_id":user_id, "note":note})
    db.session.commit()
    return redirect("/profile")