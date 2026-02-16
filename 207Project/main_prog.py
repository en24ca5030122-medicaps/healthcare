from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql

app = Flask(__name__)   # no need to mention template folder now


# ================== HOME PAGE ==================
@app.route('/')
def main_page():
    return render_template('main_page.html')


# ================== SHOW LOGIN PAGE ==================
@app.route('/existing_user')
def existing_user():
    return render_template("input.html")


# ================== SHOW REGISTER PAGE ==================
@app.route('/new_user')
def new_user():
    return render_template("new_user.html")


# ================== LOGIN LOGIC ==================
@app.route('/result', methods=['POST'])
def result():
    conn = None
    try:
        conn = sql.connect('db_1.0.db')
        cur = conn.cursor()

        username = request.form['uname'].strip()
        password = request.form['psw']

        cur.execute("SELECT * FROM login")
        rows = cur.fetchall()

        for row in rows:
            # row[0]=health_id, row[1]=username(name), row[2]=password — login with either Health ID or Name
            if (row[0] == username or row[1] == username) and row[2] == password:
                role = (row[0][0] if row[0] and len(str(row[0])) > 0 else '').lower()

                if role == 'p':
                    return render_template("patient.html", result=row)
                elif role == 'd':
                    return render_template("doctor.html", result=row)
                elif role == 'i':
                    return render_template("insurance.html", result=row)
                elif role == 'a':
                    return render_template("admin.html", result=row)

        return render_template("input.html", msg="Invalid Username or Password")

    except Exception as e:
        return render_template("input.html", msg="Database Error. Please try again.")

    finally:
        if conn:
            conn.close()


# ================== REGISTER USER ==================
@app.route('/insert_patient_data', methods=['POST'])
def insert_patient_data():
    conn = None
    try:
        conn = sql.connect('db_1.0.db')
        cur = conn.cursor()

        p_id = request.form['id_of_user']
        ssn = request.form['ssn_of_user']
        password = request.form['psw_of_user']
        name = request.form['name_of_user']
        email_id = request.form['email_of_user']

        cur.execute("INSERT INTO patient (p_id,p_password,p_name,p_email,p_ssn) VALUES (?,?,?,?,?)",
                    (p_id, password, name, email_id, ssn))

        cur.execute("INSERT INTO login (health_id,username,password) VALUES (?,?,?)",
                    (p_id, name, password))

        conn.commit()

        return render_template('new_user_success.html',
                               msg="Registration Successful!")

    except Exception as e:
        if conn:
            conn.rollback()
        return render_template('new_user_success.html',
                               msg="Error in Registration")

    finally:
        if conn:
            conn.close()


# ================== CHECK INSURANCE ==================
def _ensure_insurance_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS insurance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            i_company_name TEXT,
            i_p_id TEXT
        )
    """)


@app.route('/check_insurance')
def check_insurance():
    return render_template("check_insurance.html")


@app.route('/check_insurance_result', methods=['POST'])
def check_insurance_result():
    conn = None
    try:
        conn = sql.connect('db_1.0.db')
        cur = conn.cursor()
        _ensure_insurance_table(cur)

        i_name = request.form.get('insurance_comp_name', '').strip()

        cur.execute("""
            SELECT patient.p_name
            FROM patient, insurance
            WHERE insurance.i_company_name = ?
            AND insurance.i_p_id = patient.p_id
        """, (i_name,))

        rows = cur.fetchall()
        return render_template("check_insurance_result.html", result=rows)

    except Exception as e:
        return render_template("check_insurance_result.html", result=[], error="Database Error")

    finally:
        if conn:
            conn.close()


# ================== UPDATE EMAIL ==================
@app.route('/update_patient_email')
def update_patient_email():
    return render_template('update_patient_email.html')


@app.route('/update_patient_email_success', methods=['POST'])
def update_patient_email_success():
    conn = None
    try:
        conn = sql.connect('db_1.0.db')
        cur = conn.cursor()

        p_id = request.form["id_of_user"]
        email = request.form["email_of_user"]

        cur.execute("UPDATE patient SET p_email = ? WHERE p_id = ?", (email, p_id))
        conn.commit()

        return render_template("scan_report_success.html",
                               msg="Email Updated Successfully")

    except Exception as e:
        return render_template("scan_report_success.html",
                               msg="Error Updating Email")

    finally:
        if conn:
            conn.close()


# ================== APPOINTMENTS & SCAN ==================
def _ensure_appointments_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            health_id TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            doctor TEXT,
            status TEXT DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


@app.route('/book_appointment')
def book_appointment():
    conn = None
    doctors = []
    try:
        conn = sql.connect('db_1.0.db')
        cur = conn.cursor()
        cur.execute("SELECT health_id, username FROM login WHERE health_id LIKE 'd%' OR health_id LIKE 'D%' ORDER BY username")
        doctors = cur.fetchall()
    except Exception:
        pass
    finally:
        if conn:
            conn.close()
    return render_template('appointment_date_fix.html', result=doctors)


@app.route('/book_appointment_success', methods=['POST'])
def book_appointment_success():
    conn = None
    try:
        health_id = request.form.get('health_id', '').strip()
        appointment_date = request.form.get('appointment_date', '')
        doctor = request.form.get('doctor', '')
        if not health_id or not appointment_date:
            return render_template('book_appointment_success.html', msg="Missing Health ID or date.")
        conn = sql.connect('db_1.0.db')
        cur = conn.cursor()
        _ensure_appointments_table(cur)
        cur.execute(
            "INSERT INTO appointments (health_id, appointment_date, doctor, status) VALUES (?, ?, ?, 'scheduled')",
            (health_id, appointment_date, doctor)
        )
        conn.commit()
        return render_template('book_appointment_success.html')
    except Exception as e:
        if conn:
            conn.rollback()
        return render_template('book_appointment_success.html', msg="Error saving appointment. Try again.")
    finally:
        if conn:
            conn.close()


@app.route('/cancel_appointment')
def cancel_appointment():
    return render_template('cancel_appointment.html')


@app.route('/cancel_appointment_success', methods=['POST'])
def cancel_appointment_success():
    conn = None
    try:
        health_id = request.form.get('health_id', '').strip()
        appointment_date = request.form.get('appointment_date', '')
        if not health_id or not appointment_date:
            return render_template('scan_report_success.html', msg="Please enter Health ID and appointment date.")
        conn = sql.connect('db_1.0.db')
        cur = conn.cursor()
        _ensure_appointments_table(cur)
        cur.execute(
            "DELETE FROM appointments WHERE health_id = ? AND appointment_date = ? AND status = 'scheduled'",
            (health_id, appointment_date)
        )
        conn.commit()
        deleted = cur.rowcount
        msg = "Appointment cancelled successfully." if deleted else "No matching appointment found. Check Health ID and date."
        return render_template('scan_report_success.html', msg=msg)
    except Exception as e:
        if conn:
            conn.rollback()
        return render_template('scan_report_success.html', msg="Error cancelling appointment.")
    finally:
        if conn:
            conn.close()


@app.route('/scan_report')
def scan_report():
    return render_template('uploadFile.html')


@app.route('/uploadFile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('uploadFile.html')
    return render_template('scan_report_success.html', msg="File upload received. (Save to DB in your code.)")


@app.route('/view_appointment')
def view_appointment():
    conn = None
    health_id_filter = request.args.get('health_id', '').strip()
    try:
        conn = sql.connect('db_1.0.db')
        cur = conn.cursor()
        _ensure_appointments_table(cur)
        if health_id_filter:
            cur.execute(
                "SELECT id, health_id, appointment_date, doctor, status, created_at FROM appointments WHERE health_id = ? ORDER BY appointment_date DESC",
                (health_id_filter,)
            )
        else:
            cur.execute(
                "SELECT id, health_id, appointment_date, doctor, status, created_at FROM appointments ORDER BY appointment_date DESC"
            )
        rows = cur.fetchall()
        return render_template('view_appointment.html', appointments=rows, health_id_filter=health_id_filter)
    except Exception as e:
        return render_template('view_appointment.html', appointments=[], error=str(e), health_id_filter=health_id_filter)
    finally:
        if conn:
            conn.close()


# ================== VIEW DATABASE (for your reference) ==================
@app.route('/view_db')
def view_db():
    """View login, patient and appointments table data in browser."""
    conn = None
    login_rows, login_cols = [], []
    patient_rows, patient_cols = [], []
    appointment_rows, appointment_cols = [], []
    try:
        conn = sql.connect('db_1.0.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM login")
        login_rows = cur.fetchall()
        login_cols = [d[0] for d in cur.description] if cur.description else []

        cur.execute("SELECT * FROM patient")
        patient_rows = cur.fetchall()
        patient_cols = [d[0] for d in cur.description] if cur.description else []

        _ensure_appointments_table(cur)
        cur.execute("SELECT id, health_id, appointment_date, doctor, status, created_at FROM appointments ORDER BY appointment_date DESC")
        appointment_rows = cur.fetchall()
        appointment_cols = ['id', 'health_id', 'appointment_date', 'doctor', 'status', 'created_at']

        return render_template('view_db.html',
                              login_rows=login_rows, login_cols=login_cols,
                              patient_rows=patient_rows, patient_cols=patient_cols,
                              appointment_rows=appointment_rows, appointment_cols=appointment_cols)
    except Exception as e:
        return render_template('view_db.html', error=str(e),
                              login_rows=login_rows, login_cols=login_cols,
                              patient_rows=patient_rows, patient_cols=patient_cols,
                              appointment_rows=[], appointment_cols=[])
    finally:
        if conn:
            conn.close()


# ================== RUN SERVER ==================
if __name__ == '__main__':
    app.run(debug=True)
