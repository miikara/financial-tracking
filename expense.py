from db import db

def get_expense_user_id(expense_id):
    sql = """SELECT users.user_id FROM users 
            LEFT JOIN expenses ON users.user_id = expenses.user_id 
            WHERE expense_id=:expense_id"""
    try:
        result = db.session.execute(sql,{"expense_id":expense_id})
        id = result.fetchone()[0]
    except:
        id = -1
    return id

def add_expense(amount,expense_date,category,user_id,note):
    sql = """INSERT INTO expenses (amount,expense_date,category,user_id, note) 
            VALUES (:amount,:expense_date,:category,:user_id,:note)"""
    db.session.execute(sql,{"amount":amount,"expense_date":expense_date,"category":category,"user_id":user_id,"note":note})
    db.session.commit()

def delete_expense(expense_id,session_user_id):
    expense_user_id = get_expense_user_id(expense_id)
    if expense_user_id == session_user_id:
        sql = """DELETE FROM expenses WHERE expense_id=:expense_id"""
        db.session.execute(sql,{"expense_id":expense_id})
        db.session.commit()
        return "Expense deleted"
    else:
        return "Id not found"

    

