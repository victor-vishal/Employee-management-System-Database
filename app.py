from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'employee_db'
}


def get_db_connection():
    return mysql.connector.connect(**db_config)


@app.route('/')
def index():
    search_query = request.args.get('search')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search_query:
        # Filtered View
        sql = """
            SELECT employees.*, departments.dept_name 
            FROM employees 
            LEFT JOIN departments ON employees.dept_id = departments.dept_id
            WHERE employees.name LIKE %s
        """
        cursor.execute(sql, (f"%{search_query}%",))
    else:
        # Standard View
        cursor.execute("""
            SELECT employees.*, departments.dept_name 
            FROM employees 
            LEFT JOIN departments ON employees.dept_id = departments.dept_id
        """)

    employees = cursor.fetchall()
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', employees=employees, departments=departments)


@app.route('/insert', methods=['POST'])
def insert():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    dept_id = request.form.get('dept_id')

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO employees (name, email, phone, dept_id) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, email, phone, dept_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        cursor.execute("UPDATE employees SET name=%s, email=%s, phone=%s WHERE id=%s", (name, email, phone, id))
        conn.commit()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
    employee = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit.html', employee=employee)


@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)