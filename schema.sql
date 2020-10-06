CREATE TABLE users (user_id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE, first_name VARCHAR(50), last_name VARCHAR(50), password VARCHAR, registration_time TIMESTAMP, email VARCHAR);
CREATE TABLE expenses (expense_id SERIAL PRIMARY KEY, expense_date DATE, amount NUMERIC, category VARCHAR(50), user_id INTEGER REFERENCES users ON DELETE CASCADE, note VARCHAR);
CREATE TABLE incomes (income_id SERIAL PRIMARY KEY, income_date DATE, amount NUMERIC, category VARCHAR(50), user_id INTEGER REFERENCES users ON DELETE CASCADE, note VARCHAR);
