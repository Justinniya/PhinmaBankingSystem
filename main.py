import mysql.connector
import pyttsx3
import pyaudio
import qrcode
import speech_recognition
from flask import Flask, render_template, redirect, url_for, session, request
en = pyttsx3.init()
app = Flask(__name__)
app.config['SECRET_KEY'] = "hahaha"
db = mysql.connector.connect(
    #key='minihacks',
    host='localhost',
    user='root',
    password='',
    database='minihackathon'

)
cursor = db.cursor()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        cursor = db.cursor()
        studentid = request.form['studentid']
        password = request.form['password']
        cursor.execute("SELECT * FROM usersinfo WHERE Studentid = %s AND Password = %s", (studentid, password,))
        success = cursor.fetchone()
        #db.commit()
        if success:
            cursor.execute(
                f"UPDATE usersinfo SET teller_number =  teller_number + 1 WHERE studentid = '{studentid}'")
            db.commit()
            session['studentid'] = studentid
            print(success[1])
            db.commit()
            return redirect(url_for('home',success=success))
        else:
            return "Incorrect Account"

    return render_template("index.html")


@app.route('/home')
def home():
    studentid = session.get('studentid')

    cursor.execute("SELECT * FROM usersinfo WHERE Studentid = %s", (studentid,))
    number = cursor.fetchone()
    cursor.execute(f"SELECT * FROM account_balance WHERE studentid = '{studentid}'")
    cashins = cursor.fetchone()
    haha = cashins[2]+cashins[3]

    return render_template("getnum.html", cashins=cashins,haha=haha,number=number)


@app.route('/regis', methods=["POST", "GET"])
def regis():
    if request.method == "POST":
        # print(cursor)
        tuition = 20000
        studentid = request.form['studentid']
        fname = request.form['firstname']
        mname = request.form['middlename']
        lname = request.form['lastname']
        age = request.form['age']
        sex = request.form['sex']
        location = request.form['location']
        phone = request.form['phone']
        course = request.form['course']
        yearlevel = request.form['yearlevel']
        scholarship = request.form['scholarship']
        phinmaed = request.form['phinmaed']
        password = request.form['password']
        cursor.execute(
            'INSERT INTO usersinfo (Studentid,Firstname,Middlename,Lastname,Age,Sex,Location,Phonenumber,Course,'
            f'Yearlevel,Phinmaemail,Password,teller_number) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,{75})'
            , ( studentid, fname, mname, lname, age, sex, location, phone, course, yearlevel, phinmaed, password,))
        #print(studentid, fname, mname, lname, age, sex, location, phone, course, yearlevel, phinmaed, password)
        cursor.execute(f'INSERT INTO account_balance (Studentid,1st_Sem,2nd_Sem) Values ( %s, {tuition},{tuition} )',(studentid,))
        db.commit()
        return redirect(url_for('login'))
    return render_template("index.html")


@app.route('/transaction', methods=["POST", "GET"])
def transaction():
    cursor = db.cursor()
    studentid = session.get('studentid')
    cursor.execute(
        f"SELECT * FROM transaction WHERE Studentid = '{studentid}' ORDER BY orasnaoras DESC")
    data = cursor.fetchall()

    transaction_list = []
    for row in data:
        transaction = {
            'date': str(row[4]),
            'time': str(row[5]),
            'description': row[1],
            'amount': row[3],
            'balance': row[2],
            # Add other fields as needed
        }
        transaction_list.append(transaction)
    cursor.close()

    return render_template("transaction.html", transaction=transaction_list)

    """"
    transaction = "1"
    haha = None
    reconnizer = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print("Lets try.......")
        audio = reconnizer.listen(source)
        haha = reconnizer.recognize_google(audio)
        pyttsx3.speak(haha)
    return render_template("transaction.html",transaction=transaction)"""

@app.route('/cashout', methods=["POST", "GET"])
def cashout():
    type = 'Cash Out'
    if request.method == 'POST':
        studentid = session.get('studentid')
        amount = request.form.get('cash')
        amount = int(amount)
        cursor.execute(
            f"UPDATE account_balance SET student_balance =  student_balance - {amount} WHERE studentid = '{studentid}'")
        db.commit()
        cursor.execute(f"SELECT * FROM account_balance WHERE studentid = '{studentid}'")
        cashins = cursor.fetchone()
        db.commit()
        cursor.execute(
            f"INSERT INTO transaction (studentid, amount, trans_bal, type) VALUES ({studentid},'{str(cashins[1])}','-{str(amount)}', '{type}')")

        db.commit()
        print(cashins)
        session['cashamount'] = amount
        session['studentid'] = studentid

        return redirect(url_for('home'))
    return render_template('getnum.html')

@app.route("/cashin", methods =['GET', 'POST'])
def cashin():
    cursor = db.cursor()
    type = 'Cash In'
    if request.method == 'POST':
        studentid = session.get('studentid')
        amount = request.form.get('cash')
        amount = int(amount)
        cursor.execute(f"UPDATE account_balance SET student_balance =  student_balance + {amount} WHERE studentid = '{studentid}'")
        db.commit()
        cursor.execute(f"SELECT * FROM account_balance WHERE studentid = '{studentid}'")
        cashins = cursor.fetchone()
        db.commit()
        justin = cursor.execute(
            f"INSERT INTO transaction (studentid, amount, trans_bal, type) VALUES ({studentid},'{str(cashins[1])}','+{str(amount)}', '{type}')")

        db.commit()
        print(cashins)
        session['cashamount'] = amount
        print(justin)
        session['studentid'] = studentid

        
        return redirect(url_for('home'))
    return render_template('getnum.html')





@app.route('/onlinepayment')
def onlinepayment():
    cursor = db.cursor()
    studentid = session.get('studentid')
    cursor.execute(f"SELECT * FROM usersinfo WHERE studentid = '{studentid}'")
    profile = cursor.fetchone()
    fullname =f"{str(profile[2])} , {str(profile[1])}  {str(profile[3])} "
    cursor.execute(f"SELECT * FROM account_balance WHERE studentid = '{studentid}'")
    amount = cursor.fetchone()
    return render_template('landing.html', profile=profile,amount=amount,fullname= fullname)

@app.route("/paymentt" , methods=["POST","GET"])
def payment():
    cursor = db.cursor()
    type = 'Tuition Fee'
    if request.method == "POST":
        student = request.form['studentnumber']
        payment = request.form['payment']
        tuition = request.form['tuition']
        cursor.execute(
            f"UPDATE account_balance SET student_balance =  student_balance - {payment}, {tuition} = {tuition} - {payment} WHERE studentid = {student}")
        db.commit()
        cursor.execute(f"SELECT * FROM account_balance WHERE studentid = '{student}'")
        cashins = cursor.fetchone()
        db.commit()
        cursor.execute(
            f"INSERT INTO transaction (studentid, amount, trans_bal, type) VALUES ({student},'{str(cashins[1])}','-{str(payment)}', '{type}/{tuition}')")
        return redirect(url_for('home'))

@app.route('/admin')
def admin():
    cursor.execute(f"SELECT * FROM usersinfo")
    cashins = cursor.fetchall()
    return render_template("orders.html",cashins=cashins)

@app.route('/delete/<string:id>' ,methods=["GET"])
def delete(id):
    print(id)
    cursor.execute(f"DELETE FROM usersinfo WHERE Studentid = '{id}'")
    db.commit()
    return redirect(url_for("admin"))


def speech():
    haha = None
    reconnizer = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print("Lets try.......")
        text = "Welcome user"
        #engine.say(text)
        audio = reconnizer.listen(source)
        haha = reconnizer.recognize_sphinx(audio)
        #engine.say(haha)
        print(haha)

        #engine.runAndWait()
if __name__ == '__main__':
    app.run(debug=True)
    # Speech()
    # print(mysql)
