from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql

app = Flask(__name__, template_folder='templates')


@app.route('/')
def student():
    print("entered here")
    return render_template('input.html')


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        conn = None
        try:
            conn = sql.connect('db_1.0.db')
            print("Opened database successfully")
            username = request.form['uname']
            print("Username is: %s" % username)
            password = request.form['psw']
            print("password is: %s" % password)
            dict_login = {'username': username, 'password': password}
            print("created the dictionary")
            cur = conn.cursor()
            print("created the cursor")
            cur.execute("SELECT * FROM login")
            print("executed the query")
            rows = cur.fetchall()
            print("the type of rows is", type(rows))
            print(rows)
            for row in rows:
                print("the row in consideration is", row)
                if row[0] == username and row[2] == password:
                    print("username present in the database")
                    if row[0][0] == 'p':
                        return render_template("patient.html", result=row)
                    elif row[0][0] == 'd':
                        return render_template("doctor.html", result=row)
                    elif row[0][0] == 'i':
                        return render_template("insurance.html", result=row)
                    elif row[0][0] == 'a':
                        return render_template("admin.html", result=row)
            print("Username incorrect")
            return redirect(url_for('student'))
        except Exception as e:
            print("error in database connection or access:", e)
            return redirect(url_for('student'))
        finally:
            if conn:
                print("closing database connection")
                conn.close()
    return render_template('input.html')


@app.route('/scan_report', methods=['POST', 'GET'])
def scan_report():
    if request.method == 'POST':
        print("Python code to send an email should go here")
        return redirect(url_for('student'))
    return render_template('uploadFile.html')


@app.route('/check_insurance', methods=['POST', 'GET'])
def check_insurance():
    print("Entered the check insurance flask function")
    if request.method == 'POST':
        return render_template("check_insurance.html")
    return render_template("check_insurance.html")


@app.route('/check_insurance_result', methods=['POST', 'GET'])
def check_insurance_result():
    print("Entered the check insurance result flask function")
    if request.method == 'POST':
        conn = None
        try:
            conn = sql.connect('db_1.0.db')
            print("Opened database successfully")
            i_name = request.form['insurance_comp_name']
            print("company name received is", i_name)
            cur = conn.cursor()
            cur.execute(
                "SELECT patient.p_name FROM patient, insurance WHERE insurance.i_company_name = ? AND insurance.i_p_id = patient.p_id",
                (i_name,)
            )
            print("executed the function successfully")
            rows = cur.fetchall()
            print("fetched all rows")
            print("length of rows is", len(rows))
            print("type of rows is", type(rows))
            return render_template("check_insurance_result.html", result=rows)
        except Exception as e:
            print("error in database connection or access:", e)
            return render_template("check_insurance_result.html", result=[], error="Error in database access")
        finally:
            if conn:
                print("closing database connection")
                conn.close()
    return render_template("check_insurance.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
