from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
from db import db
from charts import *

@app.route("/",methods=['GET','POST'])
def index():
    return render_template("index.html") 

@app.route("/profile",methods=['GET','POST'])
def profile():
    username = session["username"]
    df = expense_table(username)
    bar = chart_monthly_expenses(username)
    bar_two = chart_monthly_expense_categories(username)
    bar_three = chart_monthly_expenses_vs_incomes(username)
    pie = chart_expense_categories(username)
    expenses_count,incomes_count = recorded_counts(username)
    return render_template("profile.html",expense_count=expenses_count,incomes_count=incomes_count,pie=pie,bar_one=bar,bar_two=bar_two,bar_three=bar_three,tables=[df.to_html(classes='data',header="true",justify="center",max_rows=10,index=False)]) 

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        session["username"] = username
        sql = "SELECT password FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone() 
        if user == None:
            del session["username"]
            return render_template("login.html",error_note="Username doesn't exist. Please try again or signup.")
        else:
            hash_value = user[0]
            if check_password_hash(hash_value,password):
                return redirect("/profile")
            else:
                del session["username"]
                return render_template("login.html",error_note="Incorrect password. Please try again.")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        hash_value = generate_password_hash(password)
        sql = "SELECT username FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username})
        username_db = result.fetchone() 
        if username_db:
            return render_template("signup.html",error_note="Username already taken. Please select another one.")
        else:
            sql = "INSERT INTO users (username, first_name, last_name, email, password, registration_time) VALUES (:username,:first_name,:last_name,:email,:password, NOW())"    
            db.session.execute(sql, {"username":username,"first_name":first_name,"last_name":last_name,"password":hash_value,"email":email})
            db.session.commit()
            return redirect("/login")
    else:
        return render_template("signup.html")

@app.route("/new-expense")
def new_expense():
    return render_template("expense.html")
    
@app.route("/send-expense", methods=["POST"])
def send_expense():
    amount = request.form["amount"]
    expense_date = request.form["expense_date"]
    category = request.form["category"]
    note = request.form["note"]
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
    username = session["username"]
    sql = "SELECT user_id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    sql = "INSERT INTO incomes (income_date,amount,category,user_id, note) VALUES (:income_date,:amount,:category,:user_id,:note)"
    db.session.execute(sql, {"income_date":income_date, "amount":amount, "category":category, "user_id":user_id, "note":note})
    db.session.commit()
    return redirect("/profile")