from flask import render_template, request
import sqlite3 as sql


def update_patient_scan_report():
    if request.method == 'POST':
        conn = None
        msg = "error in update operation"
        try:
            conn = sql.connect('db_1.0.db')
            print("Opened database successfully")
            scan_report_name = request.form['reportName']  # have scan_report_name field as reportName in html code
            p_id = request.form['uname']                  # have username field as uname
            cur = conn.cursor()
            cur.execute("""UPDATE patient SET p_scan_report = ? WHERE p_id = ?""", (scan_report_name, p_id))

            conn.commit()
            msg = "Record successfully updated"
        except Exception as e:
            print("error in database connection or access:", e)
            if conn:
                conn.rollback()
        finally:
            if conn:
                print("closing connection")
                conn.close()
            return render_template('patient.html', msg=msg)  # go back to patient.html and render with the msg block dynamically


def delete_patient_record():
    if request.method == 'POST':
        conn = None
        msg = "error in delete operation"
        try:
            conn = sql.connect('db_1.0.db')
            print("Opened database successfully")
            p_id = request.form['uname']   # have username field as uname
            cur = conn.cursor()
            cur.execute('DELETE FROM patient WHERE p_id = ?', (p_id,))
            conn.commit()
            msg = "Your data has been successfully deleted"
        except Exception as e:
            print("error in database connection or access:", e)
            if conn:
                conn.rollback()
        finally:
            if conn:
                print("closing connection")
                conn.close()
            return render_template('input.html', msg=msg)   # go back to input.html and render with the msg block dynamically


def check_insurance_result():
    if request.method == 'POST':
        conn = None
        try:
            conn = sql.connect('db_1.0.db')
            print("Opened database successfully")
            i_name = request.form['insurance_comp_name']

            cur = conn.cursor()
            cur.execute(
                "SELECT patient.p_name FROM patient, insurance WHERE insurance.i_company_name = ? AND insurance.i_p_id = patient.p_id",
                (i_name,)
            )

            rows = cur.fetchall()
            return render_template('check_insurance_result.html', result=rows)
        except Exception as e:
            print("error in database connection or access:", e)
            return render_template('check_insurance_result.html', result=[], error="Error in database access")
        finally:
            if conn:
                print("closing database connection")
                conn.close()
