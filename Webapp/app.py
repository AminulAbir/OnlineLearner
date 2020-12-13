from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mndkfjkdsfj"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mycountry'
app.config['MYSQL_DB'] = 'webapp'

mysql = MySQL(app)
user = 101

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
    cur.execute("SELECT * FROM view_course WHERE user = %s", (user,))

    value = cur.fetchall()

    cur.execute("select distinct ID, name, description, enrollmentkey, free_places, uname from view_course where ID not in (SELECT ID FROM view_course WHERE user = %s)", (user,))

    values = cur.fetchall()

    cur.close()

    return render_template("view_course.html", value=value, values=values)

@app.route('/view_course/<int:cid>')
def view_course_detail(cid):
    infos = [] # list of course id from enroll
    idInfos = [] # list for delete function

    cur = mysql.connection.cursor()
    res = cur.execute("select * from course_detail where ID = %s", (cid,))
    if res>0:
        value = cur.fetchall()

    cur.execute("select * from enroll where user = %s", (user,))
    info = cur.fetchall()

    cur.execute("select ID from course where creator = %s", (user,))
    idInfo = cur.fetchall()

    for i in info:
        infos.append(int(i[1]))

    for j in idInfo:
        idInfos.append(j[0])

    cur.execute("select * from tasks where nr = %s order by number ASC;", (cid,))
    taskInfo = cur.fetchall()

    cur.close()

    return render_template("view_course_detail.html", value=value, infos=infos, idInfos=idInfos, taskInfo=taskInfo)

@app.route('/new_enroll/<int:cid>', methods=['GET', 'POST'])
def new_enroll(cid):
    cur = mysql.connection.cursor()
    cur.execute("select name, enrollmentkey from course where ID = %s", (cid,))
    info = cur.fetchall()
    name = info[0][0]
    key = info[0][1]

    cur.execute("select free_places from course where ID = %s", (cid,))
    free = cur.fetchall()

    if request.method == 'POST':
        if key != None :
            ekey = request.form["ek"]
            if key == ekey:
                cur.execute(
                    "INSERT INTO enroll(user, course, date_of_entry) VALUES(%s, %s, %s)",
                    (user, cid, datetime.today().strftime('%Y-%m-%d')))
                mysql.connection.commit()
                flash("Welcome to the course!!!", "success")

                red = free[0][0]-1

                cur.execute(
                    "UPDATE course SET free_places = %s where ID = %s",(red, cid))
                mysql.connection.commit()
                cur.close()

                return redirect(url_for("view_course"))
            else:
                flash("Wrong enrollment key", "danger")
        else:
            cur.execute(
                "INSERT INTO enroll(user, course, date_of_entry) VALUES(%s, %s, %s)",
                (user, cid, datetime.today().strftime('%Y-%m-%d')))
            mysql.connection.commit()
            flash("Welcome to the course!!!", "success")

            red = free[0][0]-1

            cur.execute("UPDATE course SET free_places = %s where ID = %s", (red, cid))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for("view_course"))
    cur.close()

    return render_template("new_enroll.html", name=name, key=key, free=free)

@app.route('/delete/<int:cid>')
def delete(cid):
    cur = mysql.connection.cursor()
    cur.execute("delete from course where ID = %s", (cid,))
    mysql.connection.commit()
    cur.close()
    flash("Course has been deleted successfully!!!", "success")
    return redirect(url_for("view_course"))


@app.route('/new_assignment/<int:cid>')
def new_assignment(cid):

    return "Still need to do!!!"


if __name__ == '__main__':
    app.run()
