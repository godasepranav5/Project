import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500
CORS(app)

# ─── DB CONFIG ─────────────────────────────────────────────
# Change 'your_password' to your actual MySQL root password
DB_CONFIG = {
    "host":     os.environ.get("MYSQLHOST", "localhost"),
    "user":     os.environ.get("MYSQLUSER", "root"),
    "password": os.environ.get("MYSQLPASSWORD", ""),
    "database": os.environ.get("MYSQLDATABASE", "college_db"),
    "port":     int(os.environ.get("MYSQLPORT", 3306))
}

def get_db():
    """Open a fresh DB connection for each request."""
    return mysql.connector.connect(**DB_CONFIG)


# ─── SERVE FRONTEND ────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ══════════════════════════════════════════════════════════
#  STUDENTS
# ══════════════════════════════════════════════════════════

@app.route("/api/students", methods=["GET"])
def get_students():
    dept = request.args.get("dept", "")
    year = request.args.get("year", "")
    q    = request.args.get("q", "")

    sql    = "SELECT * FROM students WHERE 1=1"
    params = []

    if dept:
        sql += " AND dept = %s"
        params.append(dept)
    if year:
        sql += " AND year = %s"
        params.append(year)
    if q:
        sql += " AND (name LIKE %s OR student_id LIKE %s OR email LIKE %s)"
        like = f"%{q}%"
        params.extend([like, like, like])

    db  = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close(); db.close()
    return jsonify(rows)


@app.route("/api/students", methods=["POST"])
def add_student():
    d = request.json
    required = ["student_id", "name", "email", "dept", "year", "phone"]
    if not all(d.get(k) for k in required):
        return jsonify({"error": "All fields are required"}), 400

    db  = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO students VALUES (%s,%s,%s,%s,%s,%s)",
            (d["student_id"], d["name"], d["email"], d["dept"], d["year"], d["phone"])
        )
        db.commit()
    except mysql.connector.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        cur.close(); db.close()
    return jsonify({"message": "Student added"}), 201


@app.route("/api/students/<sid>", methods=["DELETE"])
def delete_student(sid):
    db  = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM students WHERE student_id = %s", (sid,))
    db.commit()
    cur.close(); db.close()
    return jsonify({"message": "Student deleted"})


@app.route("/api/students/<sid>", methods=["PUT"])
def update_student(sid):
    d   = request.json
    db  = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE students SET name=%s, email=%s, dept=%s, year=%s, phone=%s WHERE student_id=%s",
        (d["name"], d["email"], d["dept"], d["year"], d["phone"], sid)
    )
    db.commit()
    cur.close(); db.close()
    return jsonify({"message": "Student updated"})


# ══════════════════════════════════════════════════════════
#  FACULTY
# ══════════════════════════════════════════════════════════

@app.route("/api/faculty", methods=["GET"])
def get_faculty():
    dept = request.args.get("dept", "")
    q    = request.args.get("q", "")

    sql    = "SELECT * FROM faculty WHERE 1=1"
    params = []

    if dept:
        sql += " AND dept = %s"
        params.append(dept)
    if q:
        sql += " AND (name LIKE %s OR faculty_id LIKE %s OR designation LIKE %s)"
        like = f"%{q}%"
        params.extend([like, like, like])

    db  = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close(); db.close()
    return jsonify(rows)


@app.route("/api/faculty", methods=["POST"])
def add_faculty():
    d = request.json
    required = ["faculty_id", "name", "dept", "designation", "email"]
    if not all(d.get(k) for k in required):
        return jsonify({"error": "All fields are required"}), 400

    db  = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO faculty VALUES (%s,%s,%s,%s,%s,%s)",
            (d["faculty_id"], d["name"], d["dept"], d["designation"], d["email"], 0)
        )
        db.commit()
    except mysql.connector.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        cur.close(); db.close()
    return jsonify({"message": "Faculty added"}), 201


@app.route("/api/faculty/<fid>", methods=["DELETE"])
def delete_faculty(fid):
    db  = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM faculty WHERE faculty_id = %s", (fid,))
    db.commit()
    cur.close(); db.close()
    return jsonify({"message": "Faculty deleted"})


# ══════════════════════════════════════════════════════════
#  COURSES
# ══════════════════════════════════════════════════════════

@app.route("/api/courses", methods=["GET"])
def get_courses():
    dept = request.args.get("dept", "")
    q    = request.args.get("q", "")

    sql    = "SELECT * FROM courses WHERE 1=1"
    params = []

    if dept:
        sql += " AND dept = %s"
        params.append(dept)
    if q:
        sql += " AND (name LIKE %s OR course_id LIKE %s OR faculty_name LIKE %s)"
        like = f"%{q}%"
        params.extend([like, like, like])

    db  = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close(); db.close()
    return jsonify(rows)


@app.route("/api/courses", methods=["POST"])
def add_course():
    d = request.json
    required = ["course_id", "name", "dept", "credits", "faculty_name"]
    if not all(str(d.get(k, "")) for k in required):
        return jsonify({"error": "All fields are required"}), 400

    db  = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO courses VALUES (%s,%s,%s,%s,%s,%s)",
            (d["course_id"], d["name"], d["dept"], d["credits"], d["faculty_name"], 0)
        )
        db.commit()
    except mysql.connector.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        cur.close(); db.close()
    return jsonify({"message": "Course added"}), 201


@app.route("/api/courses/<cid>", methods=["DELETE"])
def delete_course(cid):
    db  = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM courses WHERE course_id = %s", (cid,))
    db.commit()
    cur.close(); db.close()
    return jsonify({"message": "Course deleted"})


# ══════════════════════════════════════════════════════════
#  EXAM MARKS
# ══════════════════════════════════════════════════════════

@app.route("/api/marks", methods=["GET"])
def get_marks():
    course = request.args.get("course", "")
    q      = request.args.get("q", "")

    sql    = "SELECT * FROM exam_marks WHERE 1=1"
    params = []

    if course and course != "all":
        sql += " AND course = %s"
        params.append(course)
    if q:
        sql += " AND (student_name LIKE %s OR course LIKE %s OR exam_id LIKE %s)"
        like = f"%{q}%"
        params.extend([like, like, like])

    db  = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close(); db.close()
    return jsonify(rows)


@app.route("/api/marks", methods=["POST"])
def add_marks():
    d = request.json
    required = ["exam_id", "student_name", "course", "marks"]
    if not all(str(d.get(k, "")) for k in required):
        return jsonify({"error": "All fields are required"}), 400

    marks = int(d["marks"])
    if not (0 <= marks <= 100):
        return jsonify({"error": "Marks must be between 0 and 100"}), 400

    db  = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO exam_marks VALUES (%s,%s,%s,%s)",
            (d["exam_id"], d["student_name"], d["course"], marks)
        )
        db.commit()
    except mysql.connector.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        cur.close(); db.close()
    return jsonify({"message": "Marks added"}), 201


@app.route("/api/marks/<eid>", methods=["DELETE"])
def delete_marks(eid):
    db  = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM exam_marks WHERE exam_id = %s", (eid,))
    db.commit()
    cur.close(); db.close()
    return jsonify({"message": "Record deleted"})


# ══════════════════════════════════════════════════════════
#  DASHBOARD STATS
# ══════════════════════════════════════════════════════════

@app.route("/api/stats", methods=["GET"])
def get_stats():
    db  = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM faculty")
    total_faculty = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM courses")
    total_courses = cur.fetchone()["total"]

    cur.execute("SELECT AVG(marks) AS avg_marks FROM exam_marks")
    avg_marks = round(cur.fetchone()["avg_marks"] or 0, 1)

    cur.execute("SELECT dept, COUNT(*) AS count FROM students GROUP BY dept")
    dept_dist = cur.fetchall()

    cur.execute("SELECT course, AVG(marks) AS avg FROM exam_marks GROUP BY course")
    course_avg = cur.fetchall()

    cur.close(); db.close()

    return jsonify({
        "total_students": total_students,
        "total_faculty":  total_faculty,
        "total_courses":  total_courses,
        "avg_marks":      avg_marks,
        "dept_dist":      dept_dist,
        "course_avg":     course_avg
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
