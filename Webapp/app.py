from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mndkfjkdsfj"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'anindo'
app.config['MYSQL_DB'] = 'lab3'

mysql = MySQL(app)
user = 113

@app.route('/')
@app.route('/view_main')
def view_main():
    return render_template("view_main.html")

@app.route('/new_course', methods=['GET', 'POST'])
def new_course():
    if request.method == 'POST':
        name = request.form["nm"]
        key = request.form["ek"]
        place = request.form["fp"]
        text = request.form["des"]

        cur = mysql.connection.cursor()
        if key:
            cur.execute("INSERT INTO course(name, description, enrollmentkey, free_places, creator) VALUES(%s, %s, %s, %s, %s)", (name, text, key, place, user))
            mysql.connection.commit()
        else:
            cur.execute(
                "INSERT INTO course(name, description, free_places, creator) VALUES(%s, %s, %s, %s)",
                (name, text, place, user))
            mysql.connection.commit()
        cur.close()
        flash("Course created successfully", "success")
        return redirect(url_for("view_main"))

    return render_template("new_course.html")

@app.route('/view_course')
def view_course():

    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM view_course WHERE user = %s", (user,))
    if res>0:
        value = cur.fetchall()

    cur.execute("select * from view_course where ID not in (SELECT ID FROM view_course WHERE user = %s)", (user,))

    values = cur.fetchall()

    cur.close()

    return render_template("view_course.html", value=value, values=values)

@app.route('/view_course/<int:cid>')
def view_course_detail(cid):
    infos = [] # list of course id from enroll
    cur = mysql.connection.cursor()
    res = cur.execute("select * from course_detail where ID = %s", (cid,))
    if res>0:
        value = cur.fetchall()

    cur.execute("select * from enroll where user = %s", (user,))
    info = cur.fetchall()
    cur.close()

    for i in info:
        infos.append(int(i[1]))

    return render_template("view_course_detail.html", value=value, infos=infos)

@app.route('/new_enroll/<int:cid>', methods=['GET', 'POST'])
def new_enroll(cid):
    cur = mysql.connection.cursor()
    cur.execute("select name, enrollmentkey from course where ID = %s", (cid,))
    info = cur.fetchall()
    name = info[0][0]
    key = info[0][1]

    cur.execute("select count(*) from enroll group by course having course = %s", (cid,))
    booked = int(cur.fetchall())
    cur.execute("select free_places from course where ID = %s", (cid,))
    free = int(cur.fetchall())

    if request.method == 'POST':
        if key != None:
            ekey = request.form["ek"]
            if key == ekey:
                cur.execute(
                    "INSERT INTO enroll(user, course, date_of_entry) VALUES(%s, %s, %s)",
                    (user, cid, datetime.today().strftime('%Y-%m-%d')))
                mysql.connection.commit()
                flash("Welcome to the course!!!", "success")
                return redirect(url_for("view_course"))
            else:
                flash("Wrong enrollment key", "danger")
        else:
            cur.execute(
                "INSERT INTO enroll(user, course, date_of_entry) VALUES(%s, %s, %s)",
                (user, cid, datetime.today().strftime('%Y-%m-%d')))
            mysql.connection.commit()
            flash("Welcome to the course!!!", "success")
            return redirect(url_for("view_course"))
    cur.close()

    return render_template("new_enroll.html", name=name, key=key, free=free, booked=booked)


if __name__ == '__main__':
    app.run()
