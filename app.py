from flask import Flask, request, redirect, url_for, render_template, make_response
from datetime import datetime

app = Flask(__name__)

# In-Memory Data Storage
users = {}  # Format: {'username': {'password': 'password', 'email': 'email'}}
expenses = {} # Format: {'username': [{'id': 'timestamp', 'title': 'Food', 'amount': 10, 'date': '2023-10-01'}]}

@app.route('/')
def home():
    user = request.cookies.get('user')
    if user:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        print(f" the user details are username: {username}, password: {password}, email: {email}")

        if username in users:
            return render_template('signup.html', error="User already exists")
        
        for user_data in users.values():
            if user_data['email'] == email:
                return render_template('signup.html', error="Email already registered")
        
        users[username] = {'password': password, 'email': email}
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_found = None

        # Search email inside users dictionary
        for username, data in users.items():
            if data['email'] == email:
                user_found = username
                break

        if not user_found:
            return render_template('login.html', error="Email is wrong")

        if users[user_found]['password'] != password:
            return render_template('login.html', error="Password does not match")

        resp = make_response(redirect(url_for('dashboard')))
        resp.set_cookie('user', user_found)  # store username
        return resp

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    username = request.cookies.get('user')
    if not username:
        return redirect(url_for('login'))
    
    user_expenses = expenses.get(username, [])
    total_amount = None

    if request.method == 'POST':
        # Check if it's a calculation request or adding an expense
        if 'calculate_total' in request.form:
             total_amount = sum(float(expense['amount']) for expense in user_expenses)
        else:
            title = request.form['title']
            amount = request.form['amount']
            date = request.form['date']
            
            new_expense = {
                'id': datetime.now().strftime('%Y%m%d%H%M%S'),
                'title': title,
                'amount': amount,
                'date': date
            }
            print(f" Adding expense for user '{username}': {new_expense}")
            
            if username not in expenses:
                expenses[username] = []
            expenses[username].append(new_expense)
            return redirect(url_for('dashboard'))

    return render_template('dashboard.html', expenses=user_expenses, username=username, total_amount=total_amount)

@app.route('/update/<expense_id>', methods=['GET', 'POST'])
def update_expense(expense_id):
    username = request.cookies.get('user')
    if not username:
        return redirect(url_for('login'))
    
    user_expenses = expenses.get(username, [])
    expense_to_edit = next((item for item in user_expenses if item['id'] == expense_id), None)
    
    if not expense_to_edit:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        expense_to_edit['title'] = request.form['title']
        expense_to_edit['amount'] = request.form['amount']
        expense_to_edit['date'] = request.form['date']
        return redirect(url_for('dashboard'))
    
    return render_template('edit.html', expense=expense_to_edit)

@app.route('/delete/<expense_id>')
def delete_expense(expense_id):
    username = request.cookies.get('user')
    if not username:
        return redirect(url_for('login'))
    
    if username in expenses:
        expenses[username] = [e for e in expenses[username] if e['id'] != expense_id]
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    if request.cookies.get('user'):
        resp = make_response(redirect(url_for('login')))
        resp.delete_cookie('user')
        return resp
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()

