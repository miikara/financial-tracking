from db import db

def get_income_user_id(income_id):
    sql = """SELECT users.user_id FROM users 
            LEFT JOIN incomes ON users.user_id = incomes.user_id 
            WHERE income_id=:income_id"""
    try:
        result = db.session.execute(sql,{"income_id":income_id})
        id = result.fetchone()[0]
    except:
        id = -1
    return id

def add_income(amount,income_date,category,user_id,note):
    sql = """INSERT INTO incomes (income_date,amount,category,user_id, note) 
            VALUES (:income_date,:amount,:category,:user_id,:note)"""
    db.session.execute(sql,{"income_date":income_date,"amount":amount,"category":category,"user_id":user_id,"note":note})
    db.session.commit()

def delete_income(income_id,session_user_id):
    income_user_id = get_income_user_id(income_id)
    if income_user_id == session_user_id:
        sql = """DELETE FROM incomes WHERE income_id=:income_id"""
        db.session.execute(sql,{"income_id":income_id})
        db.session.commit()
        return "Income deleted"
    else:
        return "Id not found"