from db import db

def add_expense(amount,expense_date,category,user_id,note):
    sql = "INSERT INTO expenses (amount,expense_date,category,user_id, note) VALUES (:amount,:expense_date,:category,:user_id,:note)"
    db.session.execute(sql, {"amount":amount, "expense_date":expense_date, "category":category, "user_id":user_id, "note":note})
    db.session.commit()
    return True