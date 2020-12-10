from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
app = Flask(__name__)
app.secret_key = "mndkfjkdsfj"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'anindo'
app.config['MYSQL_DB'] = 'lab3'

mysql = MySQL(app)
user = 110

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
        cur.execute("INSERT INTO course(name, description, enrollmentkey, free_places, creator) VALUES(%s, %s, %s, %s, %s)", (name, text, key, place, user))
        mysql.connection.commit()
        cur.close()
        flash("Course created successfully", "success")
        return redirect(url_for("view_main"))

    return render_template("new_course.html")

@app.route('/view_course')
def view_course():

    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM course")
    if res>0:
        value = cur.fetchall()
    cur.close()

    return render_template("view_course.html", value=value)

if __name__ == '__main__':
    app.run()
