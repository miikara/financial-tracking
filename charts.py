from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly as pt
import plotly.express as px
from db import db
from app import app

# Assign engine name to work with pandas queries
engine_name = db.get_engine(app=app)

def recorded_counts(user):
    df_expenses = pd.read_sql_query("SELECT expense_id FROM expenses JOIN users ON expenses.user_id = users.user_id WHERE users.username=%(u)s",engine_name, params={"u":user})
    expenses_count = len(df_expenses.index)
    df_incomes = pd.read_sql_query("SELECT income_id FROM incomes JOIN users ON incomes.user_id = users.user_id WHERE users.username=%(u)s",engine_name, params={"u":user})
    incomes_count = len(df_incomes.index)
    return (expenses_count,incomes_count)

def expense_table(user):
    df = pd.read_sql_query("SELECT expense_date,amount,category,note FROM expenses JOIN users ON expenses.user_id = users.user_id WHERE users.username=%(u)s ORDER BY expense_date DESC",engine_name, params={"u":user})
    return df

def chart_monthly_expenses(user):
    df = pd.read_sql_query("SELECT expense_date,amount,category,note FROM expenses JOIN users ON expenses.user_id = users.user_id WHERE users.username=%(u)s ORDER BY expense_date DESC",engine_name, params={"u":user})
    df['expense_date'] = pd.to_datetime(df['expense_date']) 
    df['year'] = df['expense_date'].dt.year.astype(int)
    df['month'] = df['expense_date'].dt.month.astype(int)
    current_year = pd.datetime.now().year
    df_filtered = df.where(df['year'] >= (current_year-1))
    df_filtered['year'] = df_filtered['year'].astype(str)
    df_grouped = df_filtered.groupby(['category','year','month'], as_index=False).agg({"amount": "sum"})
    chart = px.bar(data_frame=df_grouped,x='month',y='amount',color='year',orientation='v',barmode='group',title='Total monthly expenses vs LY',width=500,height=500)
    return pt.offline.plot(chart,output_type='div')

def chart_expense_categories(user):
    df = pd.read_sql_query("SELECT expense_date,amount,category,note FROM expenses JOIN users ON expenses.user_id = users.user_id WHERE users.username=%(u)s ORDER BY expense_date DESC",engine_name, params={"u":user})
    df['expense_date'] = pd.to_datetime(df['expense_date']) 
    start_date = datetime.today().replace(day=1) + relativedelta(months=-11)
    end_date = datetime.today().replace(day=1) + relativedelta(months=+1)
    mask = (df['expense_date'] >= start_date) & (df['expense_date'] < end_date)
    df_filtered = df.loc[mask]
    df_grouped = df_filtered.groupby('category', as_index=False).agg({"amount": "sum"})
    chart = px.pie(data_frame=df_grouped,values='amount',names='category',color='category',title='Category shares of expenses for last 12 months',width=500,height=500)
    return pt.offline.plot(chart,output_type='div')

def chart_monthly_expense_categories(user):
    df = pd.read_sql_query("SELECT expense_date,amount,category,note FROM expenses JOIN users ON expenses.user_id = users.user_id WHERE users.username=%(u)s ORDER BY expense_date DESC",engine_name, params={"u":user})
    df['expense_date'] = pd.to_datetime(df['expense_date']) 
    start_date = datetime.today().replace(day=1) + relativedelta(months=-11)
    end_date = datetime.today().replace(day=1) + relativedelta(months=+1)
    mask = (df['expense_date'] >= start_date) & (df['expense_date'] < end_date)
    df_filtered = df.loc[mask]
    df_filtered['yearmonth'] = pd.to_datetime(df_filtered['expense_date']).dt.to_period('M')
    df_filtered['yearmonth'] = df_filtered['yearmonth'].astype(str)
    df_grouped = df_filtered.groupby(['category','yearmonth'], as_index=False).agg({"amount": "sum"})
    df_grouped['category%'] = df_grouped['amount'] / df_grouped.groupby('yearmonth')['amount'].transform('sum')
    chart = px.bar(data_frame=df_grouped,x='yearmonth',y='category%',color='category',orientation='v',barmode='relative',title='Category shares of expenses per month',width=500,height=500)
    return pt.offline.plot(chart,output_type='div')


def chart_monthly_expenses_vs_incomes(user):
    start_date = datetime.today().replace(day=1) + relativedelta(months=-11)
    end_date = datetime.today().replace(day=1) + relativedelta(months=+1)
    # Income
    df_incomes = pd.read_sql_query("SELECT income_date,amount,category,note FROM incomes JOIN users ON incomes.user_id = users.user_id WHERE users.username=%(u)s ORDER BY income_date DESC",engine_name, params={"u":user})
    df_incomes['income_date'] = pd.to_datetime(df_incomes['income_date']) 
    mask = (df_incomes['income_date'] >= start_date) & (df_incomes['income_date'] < end_date)
    df_incomes_filtered = df_incomes.loc[mask]
    df_incomes_filtered['yearmonth'] = pd.to_datetime(df_incomes_filtered['income_date']).dt.to_period('M')
    df_incomes_filtered['yearmonth'] = df_incomes_filtered['yearmonth'].astype(str)
    df_incomes_grouped = df_incomes_filtered.groupby(['yearmonth'], as_index=False).agg({"amount": "sum"})
    df_incomes_grouped = df_incomes_grouped.assign(type='income')
    # Expenses
    df_expenses = pd.read_sql_query("SELECT expense_date,amount,category,note FROM expenses JOIN users ON expenses.user_id = users.user_id WHERE users.username=%(u)s ORDER BY expense_date DESC",engine_name, params={"u":user})
    df_expenses['expense_date'] = pd.to_datetime(df_expenses['expense_date']) 
    mask = (df_expenses['expense_date'] >= start_date) & (df_expenses['expense_date'] < end_date)
    df_expenses_filtered = df_expenses.loc[mask]
    df_expenses_filtered['yearmonth'] = pd.to_datetime(df_expenses_filtered['expense_date']).dt.to_period('M')
    df_expenses_filtered['yearmonth'] = df_expenses_filtered['yearmonth'].astype(str)
    df_expenses_grouped = df_expenses_filtered.groupby(['yearmonth'], as_index=False).agg({"amount": "sum"})
    df_expenses_grouped = df_expenses_grouped.assign(type='expense')
    # Combined
    df_concat = pd.concat([df_expenses_grouped,df_incomes_grouped])
    chart = px.bar(data_frame=df_concat,x='yearmonth',y='amount',color='type',orientation='v',barmode='group',title='Total monthly expenses vs income',width=500,height=500)
    return pt.offline.plot(chart,output_type='div')