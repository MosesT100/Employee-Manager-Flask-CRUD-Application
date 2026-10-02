# app.py
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db_connection, init_db

# -- Load environment variables --
load_dotenv()

app = Flask(__name__)

# -- Configuration from .env --
app.config['SECRET_KEY']              = os.getenv('SECRET_KEY', 'fallback-dev-key')
app.config['DEBUG']                   = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
app.config['DATABASE_NAME']           = os.getenv('DATABASE_NAME', 'crud_app.db')
app.config['SESSION_COOKIE_SECURE']   = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY']  = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')


# ---------------------------------------------
# READ - List All Employees
# ---------------------------------------------
@app.route('/')
def index():
    conn = get_db_connection()
    employees = conn.execute(
        'SELECT * FROM employees ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return render_template('index.html', employees=employees)


# ---------------------------------------------
# READ - View Single Employee
# ---------------------------------------------
@app.route('/employee/<int:employee_id>')
def view(employee_id):
    conn = get_db_connection()
    employee = conn.execute(
        'SELECT * FROM employees WHERE id = ?', (employee_id,)
    ).fetchone()
    conn.close()

    if employee is None:
        flash('Employee not found!', 'error')
        return redirect(url_for('index'))

    return render_template('view.html', employee=employee)


# ---------------------------------------------
# CREATE - Add New Employee
# ---------------------------------------------
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name       = request.form['name'].strip()
        email      = request.form['email'].strip()
        department = request.form['department'].strip()
        salary     = request.form['salary'].strip()

        # -- Validation --
        errors = []
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        if not department:
            errors.append('Department is required.')
        if not salary:
            errors.append('Salary is required.')
        else:
            try:
                salary = float(salary)
                if salary < 0:
                    errors.append('Salary must be a positive number.')
            except ValueError:
                errors.append('Salary must be a valid number.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('create.html')

        # -- Insert into DB --
        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO employees (name, email, department, salary) '
                'VALUES (?, ?, ?, ?)',
                (name, email, department, salary)
            )
            conn.commit()
            conn.close()
            flash(f'Employee "{name}" created successfully!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return render_template('create.html')

    return render_template('create.html')


# ---------------------------------------------
# UPDATE - Edit Existing Employee
# ---------------------------------------------
@app.route('/edit/<int:employee_id>', methods=['GET', 'POST'])
def edit(employee_id):
    conn = get_db_connection()
    employee = conn.execute(
        'SELECT * FROM employees WHERE id = ?', (employee_id,)
    ).fetchone()

    if employee is None:
        conn.close()
        flash('Employee not found!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name       = request.form['name'].strip()
        email      = request.form['email'].strip()
        department = request.form['department'].strip()
        salary     = request.form['salary'].strip()

        # -- Validation --
        errors = []
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        if not department:
            errors.append('Department is required.')
        if not salary:
            errors.append('Salary is required.')
        else:
            try:
                salary = float(salary)
                if salary < 0:
                    errors.append('Salary must be a positive number.')
            except ValueError:
                errors.append('Salary must be a valid number.')

        if errors:
            for error in errors:
                flash(error, 'error')
            conn.close()
            return render_template('edit.html', employee=employee)

        # -- Update in DB --
        try:
            conn.execute(
                'UPDATE employees SET name=?, email=?, department=?, salary=? '
                'WHERE id=?',
                (name, email, department, salary, employee_id)
            )
            conn.commit()
            conn.close()
            flash(f'Employee "{name}" updated successfully!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            conn.close()
            flash(f'Error: {str(e)}', 'error')
            return render_template('edit.html', employee=employee)

    conn.close()
    return render_template('edit.html', employee=employee)


# ---------------------------------------------
# DELETE - Remove Employee
# ---------------------------------------------
@app.route('/delete/<int:employee_id>', methods=['POST'])
def delete(employee_id):
    conn = get_db_connection()
    employee = conn.execute(
        'SELECT * FROM employees WHERE id = ?', (employee_id,)
    ).fetchone()

    if employee is None:
        conn.close()
        flash('Employee not found!', 'error')
        return redirect(url_for('index'))

    conn.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
    conn.commit()
    conn.close()
    flash(f'Employee "{employee["name"]}" deleted successfully!', 'success')
    return redirect(url_for('index'))


# ---------------------------------------------
# SEARCH
# ---------------------------------------------
@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    conn = get_db_connection()

    if query:
        employees = conn.execute(
            'SELECT * FROM employees WHERE name LIKE ? OR email LIKE ? OR department LIKE ?',
            (f'%{query}%', f'%{query}%', f'%{query}%')
        ).fetchall()
    else:
        employees = conn.execute('SELECT * FROM employees').fetchall()

    conn.close()
    return render_template('index.html', employees=employees, search_query=query)


# ---------------------------------------------
# Run App
# ---------------------------------------------
if __name__ == '__main__':
    init_db()
    app.run(
        host  = os.getenv('FLASK_HOST', '127.0.0.1'),
        port  = int(os.getenv('FLASK_PORT', 5000)),
        debug = app.config['DEBUG']
    )