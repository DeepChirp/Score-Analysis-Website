import mariadb
import csv
import os
import json

conn = mariadb.connect(
    host="127.0.0.1",
    user="grades",
    password="grades",
    database="grades"
)

grades_name_to_id = {}

cur = conn.cursor()

with open("../data/old_student_class", "r") as f:
    old_student_class = json.loads(f.read())
    class_sql = "INSERT INTO students (class, class_divide, grade_id, name) VALUES (?, 0, ?, ?)"
    for name, class_id in old_student_class.items():
        cur.execute(class_sql, (class_id, grades_name_to_id["本高2023届"], name))

for filename in os.listdir("../data/csv"):
    front, prefix = filename.split(".")
    if prefix == "csv":
        semester_name, exam_name = front[2:].split("_")
        csv_reader = csv.reader(open(filename, encoding="GB-18030"))
        for row in csv_reader:
            grade_name, class_id, student_name, chinese, math, english, physics, chemistry, biology, politic, history, geography = row

            if grade_name == "年级":
                continue


            if grade_name in grades_name_to_id:
                grade_id = grades_name_to_id[grade_name]
            else:
                grades_sql = "INSERT INTO grades (name) VALUES (?)"
                cur.execute(grades_sql, (grade_name, ))
                conn.commit()
                grades_id_sql = "SELECT id FROM grades WHERE name = ?"
                cur.execute(grades_id_sql, (grade_name, ))
                grade_id = list(cur)[0][0]
                grades_name_to_id[grade_name] = grade_id


