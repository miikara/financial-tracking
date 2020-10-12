from db import db

def add_income(amount,income_date,category,user_id,note):
    sql = "INSERT INTO incomes (income_date,amount,category,user_id, note) VALUES (:income_date,:amount,:category,:user_id,:note)"
    db.session.execute(sql, {"income_date":income_date,"amount":amount,"category":category,"user_id":user_id,"note":note})
    db.session.commit()