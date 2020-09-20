FINANCIAL TRACKING APP
Deployed on:
https://financial-compass.herokuapp.com/

FUNCTIONALITIES
- Create your own user profile under which to track your spending 
- Adding and categorizing your expenses and income
- Creating custom categories
- Adding comments to expenses and income
- Setting money aside for savings and investments
- Visualizing your expenses, income and balance behavior under your profile

CURRENT STATE
- Structure of the web page is ready
- User authentication is in MVP state. User creation and session management is operational but the form is still missing some validations
- Inserting expenses via form to database table expenses is operational
- Insert income only has a path but no form with which to insert income to database
- Under profile there will be statistics and most likely some charts regarding your financial behavior but these are not operational yet

TESTING APPLICATION
- Application can be tested by creating your own user account and inserting expenses when logged in. Only the count of inserted expenses is displayed under the profile currently and it includes all expenses inserted by all users (no where clause for user_id yet). User can also logout of the application
