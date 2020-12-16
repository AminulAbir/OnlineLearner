from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_mysqldb import MySQL
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "mndkfjkdsfj"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mycountry'
app.config['MYSQL_DB'] = 'webapp'

mysql = MySQL(app)
user = 6


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

        if len(name)==0 or len(name)>50:
            abort(404, description="Enter Valid Name")

        intPlace = int(place)

        if isinstance(intPlace, int)==False or intPlace>100:
            abort(404, description="Enter Valid number of free place")

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

    cur.execute("select * from (select st2.number, st2.name, st2.sid, sb.submission_text, st2.nr, st2.user from (select st1.number, t.name, st1.sid, st1.nr, st1.user from (select st.number, nr, sid, user from (select * from tasks left join (select sid, tid, user from submit where cid = %s and user = %s) as s1 on number=s1.tid) as st  where st.nr= %s) as st1 join tasks t on st1.number=t.number) as st2 left join submission sb on st2.sid = sb.id) as st3 left join avgGrade as ag on st3.sid=ag.submission", (cid, user, cid))
    stInfo = cur.fetchall()

    cur.close()

    return render_template("view_course_detail.html", value=value, user=user, infos=infos, idInfos=idInfos, stInfo=stInfo)


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


@app.route('/new_assignment/<int:tid>', methods=['GET', 'POST'])
def new_assignment(tid):
    cur = mysql.connection.cursor()
    cur.execute("select * from submit_task where number = %s", (tid,))
    obj = cur.fetchall()
    cur.close()
    if request.method == "POST":
        text = request.form["txt"]
        cur = mysql.connection.cursor()

        cur.execute("select * from submit")
        asub = cur.fetchall()
        for sub in asub:
            if (sub[2] == tid and sub[1] == obj[0][4] and sub[3] == user):
                abort(404, description="You can not submit for this task")

        cur.execute("insert into submission(submission_text) values(%s)", (text,))
        mysql.connection.commit()
        cur.execute("select id from submission where submission_text = %s", (text,))
        id = cur.fetchall()
        cur.execute("insert into submit values(%s, %s, %s, %s)", (id, obj[0][4], tid, user))
        mysql.connection.commit()

        cur.close()

        flash("Task Submitted successfully", "success")
        return redirect(url_for("view_course_detail", cid=obj[0][4]))
    return render_template("new_assignment.html", obj=obj)


@app.route('/assess/<int:cid>', methods=['GET', 'POST'])
def assess(cid):
    arrayAssess = []
    arrayAssess2 = []

# for randomly display of tasks in rating option
    cur = mysql.connection.cursor()
    cur.execute(
        "select ssb.tid, ssb.sid, t.name, t.description, ssb.submission_text from (SELECT * FROM submit s join submission sb on s.sid=sb.id where cid = %s) as ssb join tasks t on ssb.tid=t.number", (cid,))
    objAssess = cur.fetchall()

    for obj in objAssess:
        arrayAssess.append(obj)

    objRandom = random.choice(arrayAssess)

    cur.execute("select submission, user from canrate")
    subUser = cur.fetchall()

    cur.execute("select sid, user from submit where cid = %s", (cid,))
    sidUser = cur.fetchall()


# inorder to avoid the rate option for the tasks which is done by user self.
    if (objRandom[1], user) in sidUser:
        cur.execute(
            "select ssb.tid, ssb.sid, t.name, t.description, ssb.submission_text from (SELECT * FROM submit s join submission sb on s.sid=sb.id where cid = %s and sid != %s and user != %s) as ssb join tasks t on ssb.tid=t.number",
            (cid, objRandom[1], user))
        objAssess = cur.fetchall()
        for obj in objAssess:
            arrayAssess2.append(obj)
        objRandom = random.choice(arrayAssess2)

    cur.close()

    if request.method == "POST":

        grade = int(request.form.get("gd"))
        comment = request.form["cmt"]
        subId = int(request.form["sb"])

        if (subId, user) in subUser:
            abort(404, description="You have already rated for the course")

        cur = mysql.connection.cursor()
        cur.execute("insert into canrate values(%s, %s, %s, %s)", (grade, comment, subId, user))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("view_course_detail", cid=cid))

    return render_template("assess.html", objRandom=objRandom)


if __name__ == '__main__':
    app.run()
