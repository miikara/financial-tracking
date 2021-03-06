from app import app
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash
from charts import *
from expense import *
from income import *
from user import *

@app.route("/")
def index():
    return render_template("index.html") 

@app.route("/profile",methods=['GET','POST'])
def profile():
    try:
        username = session["username"]
        expenses_count,incomes_count = recorded_counts(username)
    except:
        expenses_count,incomes_count = (0,0)
    return render_template("profile.html",expense_count=expenses_count,incomes_count=incomes_count) 

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if len(username)>200:
            return render_template("error.html",note="Username too long")
        if len(password)>200:
            return render_template("error.html",note="Password too long")
        else:
            user_id = get_user_id(username)
            session["username"] = username
            session["user_id"] = user_id
            pw = get_password(username)
            if pw == None:
                del session["username"]
                return render_template("login.html",error_note="Username doesn't exist. Please try again or signup.")
            else:
                hash_value = pw
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
        if len(username) > 200:
            return render_template("error.html",note="Username too long")
        elif len(first_name) > 200:
            return render_template("error.html",note="First name too long")
        elif len(last_name) > 200:
            return render_template("error.html",note="Last name too long")
        elif len(email) > 200:
            return render_template("error.html",note="Email too long")
        elif len(password) > 200:
            return render_template("error.html",note="Password too long")
        elif username_exists(username):
            return render_template("signup.html",error_note="Username already taken. Please select another one.")
        else:
            add_user(username,first_name,last_name,email,password)
            return redirect("/login")
    else:
        return render_template("signup.html")

@app.route("/new-expense")
def new_expense():
    return render_template("expense.html")
    
@app.route("/send-expense", methods=["POST"])
def send_expense():
    username = session["username"]
    user_id = session["user_id"]
    amount = request.form["amount"]
    expense_date = request.form["expense_date"]
    category = request.form["category"]
    note = request.form["note"]
    if len(note) > 3000:
        return render_template("error.html",note="Note text too long")
    else:    
        add_expense(amount,expense_date,category,user_id,note)
        return redirect("/new-expense")

@app.route("/new-income")
def new_income():
    return render_template("income.html")

@app.route("/send-income", methods=["POST"])
def send_income():
    username = session["username"]
    user_id = session["user_id"]
    amount = request.form["amount"]
    income_date = request.form["income_date"]
    category = request.form["category"]
    note = request.form["note"]
    if len(note) > 3000:
        return render_template("error.html",note="Note text too long")
    else:
        add_income(amount,income_date,category,user_id,note)
        return redirect("/new-income")

@app.route("/dashboard")
def dashboard():
    try:
        username = session["username"]
        bar = chart_monthly_expenses(username)
        bar_two = chart_monthly_expense_categories(username)
        bar_three = chart_monthly_expenses_vs_incomes(username)
        pie = chart_expense_categories(username)
    except:
        pie,bar,bar_two,bar_three = ("","","","")
    return render_template("dashboard.html",pie=pie,bar_one=bar,bar_two=bar_two,bar_three=bar_three)

@app.route("/search", methods=["GET","POST"])
def search():
    if request.method == "POST":
        username = session["username"]
        report = request.form["report"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        category = request.form["category"]
        note_text = request.form["note_text"]
        if report == "Expense list":
            df,total = search_expenses(username,start_date,end_date,category,note_text)
            total_str = "Total expenses for the period from "+str(start_date)+" to "+str(end_date)+" equal "+str(total)
        elif report == "Income list":
            df,total = search_incomes(username,start_date,end_date,category,note_text)
            total_str = "Total incomes for the period from "+str(start_date)+" to "+str(end_date)+" equal "+str(total)
        elif report == "Period balance calculation":
            df,total = search_net_balance(username,start_date,end_date,category,note_text)
            total_str = "Total net balance for the period from "+str(start_date)+" to "+str(end_date)+" equals "+str(total)
        return render_template("search.html",total=total_str,table=df.to_html(classes='data',header="true",justify="left",max_rows=150,index=False))
    else:
        return render_template("search.html")

@app.route("/delete",methods=["GET","POST"])
def delete():
    if request.method == "POST":
        user_id = session["user_id"]
        transaction_type = request.form["transaction_type"]
        transaction_id = request.form["transaction_id"]
        if transaction_type == "Expense":
            note = delete_expense(transaction_id,user_id)
            return render_template("delete.html",note=note)
        if transaction_type == "Income":
            note = delete_income(transaction_id,user_id)
            return render_template("delete.html",note=note)
    else:
        return render_template("delete.html")