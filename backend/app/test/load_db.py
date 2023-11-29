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

# 创建科目名称和科目ID的字典
subjects = {
    "chinese": 1,
    "math": 2,
    "english": 3,
    "physics": 4,
    "chemistry": 5,
    "biology": 6,
    "politic": 7,
    "history": 8,
    "geography": 9
}

# 处理学生数据
student_data = []
with open("../data/old_student_class", "r") as f:
    old_student_class = json.loads(f.read())
    for name, class_id in old_student_class.items():
        student_data.append((class_id, 0, grades_name_to_id["本高2023届"], name))

with open("../data/new_student_class", "r") as f:
    new_student_class = json.loads(f.read())
    for name, class_id in new_student_class.items():
        student_data.append((class_id, 1, grades_name_to_id["本高2023届"], name))

# 批量插入学生数据
student_sql = "INSERT INTO students (class, class_divide, grade_id, name) VALUES (?, ?, ?, ?)"
cur.executemany(student_sql, student_data)

# 处理科目数据
subject_data = []
for subject_name, subject_info in subjects_to_id.items():
    subject_data.append((subject_info[1], subject_name))

# 批量插入科目数据
subject_sql = "INSERT INTO subjects (full_score, name) VALUES (?, ?)"
cur.executemany(subject_sql, subject_data)

# 处理学期数据
semester_data = []
for semester_name, semester_id in semester_to_id.items():
    class_divide = 0 if semester_id <= 4 else 1
    semester_data.append((semester_name, class_divide))

# 批量插入学期数据
semester_sql = "INSERT INTO semesters (name, class_divide) VALUES (?, ?)"
cur.executemany(semester_sql, semester_data)

conn.commit()
filename_list = os.listdir("../data/csv")
filename_list = sorted(filename_list, key=lambda x: int(x[:2]))
for filename in filename_list:
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

            exam_saved_name = "{}_{}".format(semester_name, exam_name)
            if exam_saved_name in exams_to_id:
                exam_id = exams_to_id[exam_saved_name]
            else:
                exams_sql = "INSERT INTO exams (name) VALUES (?)"
                cur.execute(exams_sql, (exam_saved_name, ))
                conn.commit()
                exams_id_sql = "SELECT id FROM exams WHERE name = ?"
                cur.execute(exams_id_sql, (exam_saved_name, ))
                exam_id = list(cur)[0][0]
                exams_to_id[exam_saved_name] = exam_id

            print("{}_{}: {}".format(semester_name, exam_name, exam_id))
            semester_id = semester_to_id[semester_name]
            # 遍历字典，对每个科目执行相同的操作
            for subject_name, subject_id in subjects.items():
                subject_score = locals()[subject_name]
                if subject_score.strip() != "/":
                    score_sql = "INSERT INTO scores (student_id, exam_id, subject_id, semester_id, value) VALUES (?, ?, ?, ?, ?)"
                    cur.execute(score_sql, (student_id, exam_id, subject_id, semester_id, float(subject_score)))

conn.commit()
