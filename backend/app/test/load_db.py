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

grades_name_to_id = {
    "本高2023届": 1
}

cur = conn.cursor()

old_student_class = None
new_student_class = None

student_to_id = {}
exams_to_id = {}
subjects_to_id = {
    "语文": [1, 150],
    "数学": [2, 150],
    "外语": [3, 150],
    "物理": [4, 100],
    "化学": [5, 100],
    "生物": [6, 100],
    "政治": [7, 100],
    "历史": [8, 100],
    "地理": [9, 100]
}

semester_to_id ={
    "高一上": 1,
    "高一下": 2,
    "高二上": 3,
    "高二下": 4,
    "高三上": 5,
    "高三下": 6
}

with open("../data/old_student_class", "r") as f:
    old_student_class = json.loads(f.read())
    class_sql = "INSERT INTO students (class, class_divide, grade_id, name) VALUES (?, 0, ?, ?)"
    for name, class_id in old_student_class.items():
        cur.execute(class_sql, (class_id, grades_name_to_id["本高2023届"], name))


with open("../data/new_student_class", "r") as f:
    new_student_class = json.loads(f.read())
    class_sql = "INSERT INTO students (class, class_divide, grade_id, name) VALUES (?, 1, ?, ?)"
    for name, class_id in new_student_class.items():
        cur.execute(class_sql, (class_id, grades_name_to_id["本高2023届"], name))

for subject_name, subject_info in subjects_to_id.items():
    subject_sql = "INSERT INTO subjects (full_score, name) VALUES (?, ?)"
    cur.execute(subject_sql, (subject_info[1], subject_name))

for semester_name, semester_id in semester_to_id.items():
    semester_sql = "INSERT INTO semesters (name, class_divide) VALUES (?, ?)"
    if semester_id <= 4:
        class_divide = 0
    else:
        class_divide = 1
    cur.execute(semester_sql, (semester_name, class_divide))

conn.commit()
for filename in os.listdir("../data/csv"):
    front, prefix = filename.split(".")
    if prefix == "csv":
        semester_name, exam_name = front[2:].split("_")
        csv_reader = csv.reader(open("../data/csv/{}".format(filename), encoding="GB18030"))
        print("../data/csv/{}".format(filename))
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

            if student_name in student_to_id:
                student_id = student_to_id[student_name]
            else:
                id_sql = "SELECT id FROM students WHERE name = ?"
                cur.execute(id_sql, (student_name, ))
                print(student_name)
                data = list(cur)
                if len(data) != 0 and data[0][0] is not None:
                    student_id = data[0][0]
                    student_to_id[student_name] = student_id

            if "{}_{}".format(semester_name, exam_name) in exams_to_id:
                exam_id = exams_to_id["{}_{}".format(semester_name, exam_name)]
            else:
                exams_sql = "INSERT INTO exams (name) VALUES (?)"
                cur.execute(exams_sql, (exam_name, ))
                conn.commit()
                exams_id_sql = "SELECT id FROM exams WHERE name = ?"
                cur.execute(exams_id_sql, (exam_name, ))
                exam_id = list(cur)[0][0]
                exams_to_id["{}_{}".format(semester_name, exam_name)] = exam_id

            semester_id = semester_to_id[semester_name]
            if chinese.strip() != "/":
                chinese_sql = "INSERT INTO scores (student_id, exam_id, subject_id, semester_id, value) VALUES (?, ?, ?, ?, ?)"
                cur.execute(chinese_sql, (student_id, exam_id, 1, semester_id, float(chinese)))
            if math.strip() != "/":
                math_sql = "INSERT INTO scores (student_id, exam_id, subject_id, semester_id, value) VALUES (?, ?, ?, ?, ?)"
                cur.execute(math_sql, (student_id, exam_id, 2, semester_id, float(math)))
            if english.strip() != "/":
                english_sql = "INSERT INTO scores (student_id, exam_id, subject_id, semester_id, value) VALUES (?, ?, ?, ?, ?)"
                cur.execute(english_sql, (student_id, exam_id, 3, semester_id, float(english)))
            if physics.strip() != "/":
                physics_sql = "INSERT INTO scores (student_id, exam_id, subject_id, semester_id, value) VALUES (?, ?, ?, ?, ?)"
                cur.execute(physics_sql, (student_id, exam_id, 4, semester_id, float(physics)))
            if chemistry.strip() != "/":
                chemistry_sql = "INSERT INTO scores (student_id, exam_id, subject_id, semester_id, value) VALUES (?, ?, ?, ?, ?)"
                cur.execute(chemistry_sql, (student_id, exam_id, 5, semester_id, float(chemistry)))
            if biology.strip() != "/":
                biology_sql = "INSERT INTO scores (student_id, exam_id, subject_id, semester_id, value) VALUES (?, ?, ?, ?, ?)"
                cur.execute(biology_sql, (student_id, exam_id, 6, semester_id, float(biology)))
            if politic.strip() != "/":
                politic_sql = "INSERT INTO scores (student_id, exam_id, subject_id, semester_id, value) VALUES (?, ?, ?, ?, ?)"
                cur.execute(politic_sql, (student_id, exam_id, 7, semester_id, float(politic)))
            if history.strip() != "/":
                history_sql = "INSERT INTO scores (student_id, exam_id, subject_id, semester_id, value) VALUES (?, ?, ?, ?, ?)"
                cur.execute(history_sql, (student_id, exam_id, 8, semester_id, float(history)))
            if geography.strip() != "/":
                geography_sql = "INSERT INTO scores (student_id, exam_id, subject_id, semester_id, value) VALUES (?, ?, ?, ?, ?)"
                cur.execute(geography_sql, (student_id, exam_id, 9, semester_id, float(geography)))

conn.commit()
