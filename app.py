from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
import numpy as np
import pandas as pd
import plotly as pt
import plotly.express as px
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
engine_name = db.get_engine(app=app)

@app.route("/",methods=['GET','POST'])
def index():
    return render_template("index.html") 

@app.route("/profile",methods=['GET','POST'])
def profile():
    username = session["username"]
    # Return table of expenses as dataframe
    df = pd.read_sql_query("SELECT expense_date,amount,category,note FROM expenses JOIN users ON expenses.user_id = users.user_id WHERE users.username=%(u)s ORDER BY expense_date DESC",engine_name, params={"u":username})
    expenses_count = len(df.index)
    df['expense_date'] = pd.to_datetime(df['expense_date']) 
    df['year'] = df['expense_date'].dt.year.astype(int)
    df['month'] = df['expense_date'].dt.month.astype(int)
    current_year = pd.datetime.now().year
    # Create monthly expenses vs ly
    df_two_years = df.where(df['year'] >= (current_year-1))
    df_two_years['year'] = df_two_years['year'].astype(str)
    df_bar = df_two_years.groupby(['category','year','month'], as_index=False).agg({"amount": "sum"})
    bar = px.bar(data_frame=df_bar,x='month',y='amount',color='year',orientation='v',barmode='group',title='Total monthly expenses vs LY',width=500,height=500)
    bar = pt.offline.plot(bar,output_type='div')
    # Create pie chart of expense category % for past 12 months (from 1st of starting month till last of current month)
    start_date = datetime.today().replace(day=1) + relativedelta(months=-11)
    end_date = datetime.today().replace(day=1) + relativedelta(months=+1)
    mask = (df['expense_date'] >= start_date) & (df['expense_date'] < end_date)
    df_12m = df.loc[mask]
    df_pie = df_12m.groupby('category', as_index=False).agg({"amount": "sum"})
    expense_pie = px.pie(data_frame=df_pie,values='amount',names='category',color='category',title='Category shares of expenses for last 12 months',width=500,height=500)
    expense_pie = pt.offline.plot(expense_pie,output_type='div')
    # Create stacked bar chart of expense category % per month
    df_12m['yearmonth'] = pd.to_datetime(df_12m['expense_date']).dt.to_period('M')
    df_12m['yearmonth'] = df_12m['yearmonth'].astype(str)
    df_bar_two = df_12m.groupby(['category','yearmonth'], as_index=False).agg({"amount": "sum"})
    df_bar_two['category%'] = df_bar_two['amount'] / df_bar_two.groupby('yearmonth')['amount'].transform('sum')
    bar_two = px.bar(data_frame=df_bar_two,x='yearmonth',y='category%',color='category',orientation='v',barmode='relative',title='Category shares of expenses per month',width=500,height=500)
    bar_two = pt.offline.plot(bar_two,output_type='div')
    # Create income vs expenses
    df_incomes = pd.read_sql_query("SELECT income_date,amount,category,note FROM incomes JOIN users ON incomes.user_id = users.user_id WHERE users.username=%(u)s ORDER BY income_date DESC",engine_name, params={"u":username})
    incomes_count = len(df_incomes.index)
    df_incomes['income_date'] = pd.to_datetime(df_incomes['income_date']) 
    mask = (df_incomes['income_date'] >= start_date) & (df_incomes['income_date'] < end_date)
    df_incomes_12m = df_incomes.loc[mask]
    df_incomes_12m['yearmonth'] = pd.to_datetime(df_incomes_12m['income_date']).dt.to_period('M')
    df_incomes_12m['yearmonth'] = df_incomes_12m['yearmonth'].astype(str)
    df_grouped_incomes = df_incomes_12m.groupby(['yearmonth'], as_index=False).agg({"amount": "sum"})
    df_grouped_incomes = df_grouped_incomes.assign(type='income')
    df_grouped_expenses = df_12m.groupby(['yearmonth'], as_index=False).agg({"amount": "sum"})
    df_grouped_expenses = df_grouped_expenses.assign(type='expense')
    df_concat = pd.concat([df_grouped_expenses,df_grouped_incomes])
    bar_three = px.bar(data_frame=df_concat,x='yearmonth',y='amount',color='type',orientation='v',barmode='group',title='Total monthly expenses vs income',width=500,height=500)
    bar_three = pt.offline.plot(bar_three,output_type='div')
    return render_template("profile.html",expense_count=expenses_count,incomes_count=incomes_count,pie=expense_pie,bar_one=bar,bar_two=bar_two,bar_three=bar_three,tables=[df_concat.to_html(classes='data',header="true",justify="center",max_rows=10,index=False)]) 

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
    sql = "SELECT username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    username_db = result.fetchone() 
    if username_db:
        return redirect("/duplicate-username")
    else:
        sql = "INSERT INTO users (username, first_name, last_name, email, password, registration_time) VALUES (:username,:first_name,:last_name,:email,:password, NOW())"    
        db.session.execute(sql, {"username":username,"first_name":first_name,"last_name":last_name,"password":hash_value,"email":email})
        db.session.commit()
        return redirect("/")

@app.route("/duplicate-username")
def duplicate_username():
    return render_template("duplicate_username.html") 

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