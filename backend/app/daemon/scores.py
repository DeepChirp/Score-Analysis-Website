from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
import numpy
from daemon.db import get_db
import json

bp = Blueprint("scores", __name__, url_prefix="/scores")

@bp.route("/basic_info/exam", methods=("GET",))
def get_exam():
    db = get_db()
    cur = db.cursor()
    sql = "SELECT DISTINCT exams.id, semesters.id, semesters.name, exams.name " \
          "FROM exams " \
          "INNER JOIN scores " \
          "ON scores.exam_id = exams.id " \
          "INNER JOIN semesters " \
          "ON semesters.id = scores.semester_id"
    cur.execute(sql)
    data = list(cur)
    if len(data) == 0:
        ret = {"code": 404, "msg": "Not Found.", "data": {}}
    else:
        result = {}
        for exam_id, semester_id, semester_name, exam_name in data:
            this_semester = result.setdefault(semester_id, [])
            exam_info = {
                "examId": exam_id,
                "semesterId": semester_id,
                "semesterName": semester_name,
                "examName": exam_name.split("_")[1]
            }
            this_semester.append(exam_info)
        ret = {"code": 200, "msg": "Ok.", "data": {"exams": result}}
    return ret
@bp.route("/basic_info/class/<int:exam_id>", methods=("GET",))
def get_class(exam_id):
    db = get_db()
    cur = db.cursor()
    sql = "SELECT DISTINCT class " \
          "FROM scores " \
          "INNER JOIN students " \
          "ON scores.student_id = students.id " \
          "WHERE exam_id = ? " \
          "ORDER BY class"
    cur.execute(sql, (exam_id, ))
    data = list(cur)
    if len(data) == 0:
        ret = {"code": 404, "msg": "Not Found.", "data": {}}
    else:
        result = []
        for class_id in data:
            result.append(class_id[0])
        ret = {"code": 200, "msg": "Ok.", "data": {"classes": result}}
    return ret
@bp.route("/basic_info/by_class/<int:class_id>/exam/<int:exam_id>", methods=("GET",))
def get_basic_info_by_class(class_id, exam_id):
    # SELECT class, COUNT(student_id) FROM (SELECT DISTINCT student_id FROM scores WHERE exam_id = 46) AS t INNER JOIN students ON t.student_id = students.id GROUP BY students.class;
    db = get_db()
    cur = db.cursor()
    sql = "SELECT COUNT(*) " \
          "FROM ( " \
          "SELECT student_id " \
          "FROM scores " \
          "WHERE exam_id = ?  " \
          "GROUP BY student_id " \
          "HAVING COUNT(id) >= 6 ) " \
          "AS subquery " \
          "INNER JOIN students " \
          "ON student_id = students.id " \
          "WHERE class = ?"
    cur.execute(sql, (exam_id, class_id))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None or data[0][0] == 0:
        ret = {"code": 404, "msg": "Not Found.", "data": {}}
    else:
        ret = {"code": 200, "msg": "Ok.", "data": {"validNum": data[0][0]}}
    return ret


@bp.route("/data/by_class/<int:class_id>/exam/<int:exam_id>", methods=("GET",))
def get_data_by_class(class_id, exam_id):
    db = get_db()
    cur = db.cursor()
    sql = "SELECT name, scores.student_id, subject_id, value " \
          "FROM scores " \
          "INNER JOIN students " \
          "ON students.id = scores.student_id " \
          "WHERE exam_id = ? " \
          "AND class = ? " \
          "AND student_id IN (" \
          "SELECT student_id " \
          "FROM " \
          "(SELECT student_id FROM scores WHERE exam_id = ? GROUP BY student_id HAVING COUNT(id) >= 6) AS sub " \
          "INNER JOIN students " \
          "ON sub.student_id = students.id " \
          "WHERE class = ?)"
    cur.execute(sql, (exam_id, class_id, exam_id, class_id))
    data = list(cur)

    if len(data) == 0:
        ret = {"code": 404, "msg": "Not Found.", "data": {}}
    else:
        result = {}
        student_name_to_id = {}
        for name, student_id, subject_id, value in data:
            scores = result.setdefault(name, [0] * 10)
            scores[subject_id] = value
            student_name_to_id[name] = student_id
        result_lst = []
        for name, scores in result.items():
            result_lst.append({"name": name, "id": student_name_to_id[name], "scores": scores})
        ret = {"code": 200, "msg": "Ok.", "data": {"scores": result_lst}}

    return ret


@bp.route("/analysis/by_class/<int:class_id>/exam/<int:exam_id>", methods=("GET",))
def get_analysis_by_class(class_id, exam_id):
    db = get_db()
    cur = db.cursor()
    test_sql = "SELECT * " \
               "FROM scores " \
               "INNER JOIN students " \
               "ON scores.student_id = students.id " \
               "WHERE exam_id = ? " \
               "AND class = ?"
    cur.execute(test_sql, (exam_id, class_id))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        ret = {"code": 404, "msg": "Not Found", "data": {}}
        return ret
    subject_result = {}
    for subject_id in range(1, 10):
        first10_sql = "SELECT scores.student_id, name, subject_id, value, r.rank " \
                      "FROM scores " \
                      "INNER JOIN students " \
                      "ON scores.student_id = students.id " \
                      "INNER JOIN (SELECT student_id, RANK() OVER (ORDER BY value DESC) AS rank FROM scores WHERE exam_id = ? AND subject_id = ?) AS r " \
                      "ON scores.student_id = r.student_id " \
                      "WHERE exam_id = ? " \
                      "AND class = ? " \
                      "AND scores.student_id IN ((SELECT student_id FROM scores WHERE exam_id = ? GROUP BY student_id HAVING COUNT(id) >= 6)) " \
                      "AND subject_id = ? " \
                      "ORDER BY value DESC " \
                      "LIMIT 10"
        cur.execute(first10_sql, (exam_id, subject_id, exam_id, class_id, exam_id, subject_id))
        data = list(cur)
        if len(data) == 0 or data[0][0] is None:
            continue
        else:
            first10_ids = []
            first10_names = []
            first10_scores = []
            first10_ranks = []
            for student_id, name, subject_id, value, grade_rank in data:
                first10_ids.append(student_id)
                first10_names.append(name)
                first10_scores.append(value)
                first10_ranks.append(grade_rank)
            first10_avg_scores = numpy.average(first10_scores)
            first10_std = numpy.std(first10_scores)
            avg_rank_sql = "SELECT DISTINCT r " \
                           "FROM (SELECT value, RANK() OVER (ORDER BY value DESC) AS r FROM scores WHERE subject_id = ? AND exam_id = ?) AS ran " \
                           "WHERE ran.value = ?"
            cur.execute(avg_rank_sql, (int(first10_avg_scores), subject_id, exam_id))
            data = list(cur)
            if len(data) == 0 or data[0][0] is None:
                rank2_sql = "SELECT COUNT(student_id) " \
                            "FROM scores " \
                            "WHERE exam_id = ? " \
                            "AND subject_id = ? " \
                            "AND value >= ?"
                cur.execute(rank2_sql, (exam_id, subject_id, first10_avg_scores))
                data = list(cur)
                if data[0][0] == 0:
                    first10_avg_rank = 1
                else:
                    first10_avg_rank = data[0][0]
            else:
                first10_avg_rank = data[0][0]
            subject_info = subject_result.setdefault(subject_id, {})
            first10_info = []
            scoresLen = len(first10_scores)
            for i in range(scoresLen):
                thisInfo = {
                    "id": first10_ids[i],
                    "name": first10_names[i],
                    "score": first10_scores[i],
                    "gradeRank": first10_ranks[i]
                }
                first10_info.append(thisInfo)
            subject_info["first10ScoreList"] = first10_info
            subject_info["first10AvgScore"] = first10_avg_scores
            subject_info["first10AvgRank"] = first10_avg_rank
            subject_info["first10Std"] = first10_std

        first_sql = "SELECT scores.student_id, name, value, r.grade_rank " \
                    "FROM scores " \
                    "INNER JOIN students " \
                    "ON scores.student_id = students.id " \
                    "INNER JOIN (SELECT student_id, RANK() OVER (ORDER BY value DESC) AS grade_rank FROM scores WHERE exam_id = ? AND subject_id = ?) AS r " \
                    "ON r.student_id = scores.student_id " \
                    "WHERE exam_id = ? " \
                    "AND class = ? " \
                    "AND subject_id = ? " \
                    "ORDER BY value DESC " \
                    "LIMIT 1"
        cur.execute(first_sql, (exam_id, subject_id, exam_id, class_id, subject_id))
        data = list(cur)
        first_id, first_name, first_score, first_rank = data[0]
        subject_info["firstId"] = first_id
        subject_info["firstName"] = first_name
        subject_info["firstScore"] = first_score
        subject_info["firstRank"] = first_rank

        class_sql = "SELECT value " \
                    "FROM scores " \
                    "INNER JOIN students " \
                    "ON scores.student_id = students.id " \
                    "INNER JOIN (SELECT student_id, RANK() OVER (ORDER BY value DESC) AS rank FROM scores WHERE exam_id = ? AND subject_id = ?) AS r " \
                    "ON scores.student_id = r.student_id " \
                    "WHERE exam_id = ? " \
                    "AND class = ? " \
                    "AND scores.student_id IN ((SELECT student_id FROM scores WHERE exam_id = ? GROUP BY student_id HAVING COUNT(id) >= 6)) " \
                    "AND subject_id = ? " \
                    "ORDER BY value DESC"

        cur.execute(class_sql, (exam_id, subject_id, exam_id, class_id, exam_id, subject_id))
        data = list(cur)

        class_scores = []

        for value in data:
            class_scores.append(value[0])
        class_avg_score = numpy.average(class_scores)
        subject_info["classAvgScore"] = class_avg_score
        subject_info["classStd"] = numpy.std(class_scores)

        avg_rank_sql = "SELECT DISTINCT r " \
                       "FROM (SELECT value, RANK() OVER (ORDER BY value DESC) AS r FROM scores WHERE subject_id = ? AND exam_id = ?) AS ran " \
                       "WHERE ran.value = ?"
        cur.execute(avg_rank_sql, (int(class_avg_score), subject_id, exam_id))
        data = list(cur)
        if len(data) == 0 or data[0][0] is None:
            rank2_sql = "SELECT COUNT(student_id) " \
                        "FROM scores " \
                        "WHERE exam_id = ? " \
                        "AND subject_id = ? " \
                        "AND value >= ?"
            cur.execute(rank2_sql, (exam_id, subject_id, class_avg_score))
            data = list(cur)
            if data[0][0] == 0:
                class_avg_rank = 1
            else:
                class_avg_rank = data[0][0]
        else:
            class_avg_rank = data[0][0]

        subject_info["classAvgRank"] = class_avg_rank

        last10_sql = "SELECT scores.student_id, name, subject_id, value, r.rank " \
                     "FROM scores " \
                     "INNER JOIN students " \
                     "ON scores.student_id = students.id " \
                     "INNER JOIN (SELECT student_id, RANK() OVER (ORDER BY value DESC) AS rank FROM scores WHERE exam_id = ? AND subject_id = ?) AS r " \
                     "ON scores.student_id = r.student_id " \
                     "WHERE exam_id = ? " \
                     "AND class = ? " \
                     "AND scores.student_id IN ((SELECT student_id FROM scores WHERE exam_id = ? GROUP BY student_id HAVING COUNT(id) >= 6)) " \
                     "AND subject_id = ? " \
                     "ORDER BY value " \
                     "LIMIT 10"
        cur.execute(last10_sql, (exam_id, subject_id, exam_id, class_id, exam_id, subject_id))
        data = list(cur)
        if len(data) == 0 or data[0][0] is None:
            pass
        else:
            last10_ids = []
            last10_names = []
            last10_scores = []
            last10_ranks = []
            for student_id, name, subject_id, value, grade_rank in data:
                last10_ids.append(student_id)
                last10_names.append(name)
                last10_scores.append(value)
                last10_ranks.append(grade_rank)

            last10_avg_scores = numpy.average(last10_scores)
            last10_std = numpy.std(last10_scores)
            avg_rank_sql = "SELECT DISTINCT r " \
                           "FROM (SELECT value, RANK() OVER (ORDER BY value DESC) AS r FROM scores WHERE subject_id = ? AND exam_id = ?) AS ran " \
                           "WHERE ran.value = ?"
            cur.execute(avg_rank_sql, (int(last10_avg_scores), subject_id, exam_id))
            data = list(cur)
            if len(data) == 0 or data[0][0] is None:
                rank2_sql = "SELECT COUNT(student_id) " \
                            "FROM scores " \
                            "WHERE exam_id = ? " \
                            "AND subject_id = ? " \
                            "AND value >= ?"
                cur.execute(rank2_sql, (exam_id, subject_id, last10_avg_scores))
                data = list(cur)
                if data[0][0] == 0:
                    last10_avg_rank = 1
                else:
                    last10_avg_rank = data[0][0]
            else:
                last10_avg_rank = data[0][0]
            last10_info = []
            scoresLen = len(last10_scores)
            for i in range(scoresLen - 1, -1, -1):
                thisInfo = {
                    "id": last10_ids[i],
                    "name": last10_names[i],
                    "score": last10_scores[i],
                    "gradeRank": last10_ranks[i]
                }
                last10_info.append(thisInfo)
            subject_info["last10ScoreList"] = last10_info
            subject_info["last10AvgScore"] = last10_avg_scores
            subject_info["last10AvgRank"] = last10_avg_rank
            subject_info["last10Std"] = last10_std

        last_sql = "SELECT scores.student_id, name, value, r.grade_rank " \
                   "FROM scores " \
                   "INNER JOIN students " \
                   "ON scores.student_id = students.id " \
                   "INNER JOIN (SELECT student_id, RANK() OVER (ORDER BY value DESC) AS grade_rank FROM scores WHERE exam_id = ? AND subject_id = ?) AS r " \
                   "ON r.student_id = scores.student_id " \
                   "WHERE exam_id = ? " \
                   "AND class = ? " \
                   "AND subject_id = ? " \
                   "ORDER BY value  " \
                   "LIMIT 1"
        cur.execute(last_sql, (exam_id, subject_id, exam_id, class_id, subject_id))
        data = list(cur)
        last_id, last_name, last_score, last_rank = data[0]
        subject_info["lastId"] = last_id
        subject_info["lastName"] = last_name
        subject_info["lastScore"] = last_score
        subject_info["lastRank"] = last_rank

    first10_total_sql = "SELECT scores.student_id, name, SUM(value), r.rank " \
                        "FROM scores " \
                        "INNER JOIN students " \
                        "ON scores.student_id = students.id " \
                        "INNER JOIN (SELECT student_id, RANK() OVER (ORDER BY tvalue DESC) AS rank FROM (SELECT student_id, SUM(value) AS tvalue FROM scores WHERE exam_id = ? GROUP BY student_id) AS t) AS r " \
                        "ON r.student_id = scores.student_id " \
                        "WHERE exam_id = ? " \
                        "AND class = ? " \
                        "GROUP BY name " \
                        "ORDER BY SUM(value) DESC " \
                        "LIMIT 10"

    cur.execute(first10_total_sql, (exam_id, exam_id, class_id))
    first10_total_ids = []
    first10_total_names = []
    first10_total_scores = []
    first10_total_ranks = []
    data = list(cur)
    for student_id, name, score, grade_rank in data:
        first10_total_ids.append(student_id)
        first10_total_names.append(name)
        first10_total_scores.append(score)
        first10_total_ranks.append(grade_rank)
    first10_total_avg = numpy.average(first10_total_scores)
    first10_total_std = numpy.std(first10_total_scores)
    total_avg_rank_sql = "SELECT DISTINCT rank FROM " \
                         "((SELECT SUM(scores.value) AS s, RANK() OVER (ORDER BY SUM(scores.value) DESC) AS rank FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? GROUP BY students.name) as r) " \
                         "WHERE s = ?"
    cur.execute(total_avg_rank_sql, (exam_id, int(first10_total_avg),))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        total_avg_rank_sql2 = "SELECT COUNT(*) " \
                              "FROM (SELECT SUM(value) AS value FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? GROUP BY name ORDER BY SUM(value) DESC) AS t " \
                              "WHERE value >= ?"
        cur.execute(total_avg_rank_sql2, (exam_id, first10_total_avg,))
        data = list(cur)
        if data[0][0] == 0:
            first10_total_avg_rank = 1
        else:
            first10_total_avg_rank = data[0][0]
    else:
        first10_total_avg_rank = data[0][0]

    subject_info = subject_result.setdefault("255", {})
    first10_total_info = []
    scoresLen = len(first10_scores)
    for i in range(scoresLen):
        thisInfo = {
            "id": first10_total_ids[i],
            "name": first10_total_names[i],
            "score": first10_total_scores[i],
            "gradeRank": first10_total_ranks[i]
        }
        first10_total_info.append(thisInfo)
    subject_info["first10ScoreList"] = first10_total_info
    subject_info["first10AvgScore"] = first10_total_avg
    subject_info["first10AvgRank"] = first10_total_avg_rank
    subject_info["first10Std"] = first10_total_std

    class_total_sql = "SELECT SUM(value) " \
                      "FROM scores " \
                      "INNER JOIN students " \
                      "ON scores.student_id = students.id " \
                      "INNER JOIN (SELECT student_id, RANK() OVER (ORDER BY tvalue DESC) AS rank FROM (SELECT student_id, SUM(value) AS tvalue FROM scores WHERE exam_id = ? GROUP BY student_id) AS t) AS r " \
                      "ON r.student_id = scores.student_id " \
                      "WHERE exam_id = ? " \
                      "AND class = ? " \
                      "GROUP BY name " \
                      "ORDER BY SUM(value) DESC"

    cur.execute(class_total_sql, (exam_id, exam_id, class_id))
    data = list(cur)
    class_total_scores = []
    for value in data:
        class_total_scores.append(value[0])
    class_avg_score = numpy.average(class_total_scores)
    subject_info["classAvgScore"] = class_avg_score
    subject_info["classStd"] = numpy.std(class_total_scores)

    total_avg_rank_sql = "SELECT DISTINCT rank " \
                         "FROM (SELECT tvalue, RANK() OVER (ORDER BY tvalue DESC) AS rank FROM (SELECT student_id, name, SUM(value) AS tvalue FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? GROUP BY name ORDER BY SUM(value) DESC) AS t  ) AS r " \
                         "WHERE tvalue = ?"
    cur.execute(total_avg_rank_sql, (exam_id, int(class_avg_score),))
    data = list(cur)

    if len(data) == 0 or data[0][0] is None:
        total_avg_rank_sql2 = "SELECT COUNT(*) " \
                              "FROM (SELECT SUM(value) AS value FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? GROUP BY name ORDER BY SUM(value) DESC) AS t " \
                              "WHERE value >= ?"
        cur.execute(total_avg_rank_sql2, (exam_id, class_avg_score,))
        data = list(cur)
        if data[0][0] == 0:
            class_avg_rank = 1
        else:
            class_avg_rank = data[0][0]
    else:
        class_avg_rank = data[0][0]

    subject_info["classAvgRank"] = class_avg_rank

    first_total_sql = "SELECT scores.student_id, name, SUM(value), r.rank " \
                      "FROM scores " \
                      "INNER JOIN students " \
                      "ON scores.student_id = students.id " \
                      "INNER JOIN (SELECT student_id, RANK() OVER (ORDER BY tvalue DESC) AS rank FROM (SELECT student_id, SUM(value) AS tvalue FROM scores WHERE exam_id = ? GROUP BY student_id) AS t) AS r " \
                      "ON r.student_id = scores.student_id " \
                      "WHERE exam_id = ? " \
                      "AND class = ? " \
                      "GROUP BY name " \
                      "ORDER BY SUM(value) DESC " \
                      "LIMIT 1"
    cur.execute(first_total_sql, (exam_id, exam_id, class_id))
    data = list(cur)
    first_id, first_name, first_score, first_rank = data[0]
    subject_info["firstId"] = first_id
    subject_info["firstName"] = first_name
    subject_info["firstScore"] = first_score
    subject_info["firstRank"] = first_rank

    last10_total_sql = "SELECT scores.student_id, name, SUM(value), r.rank " \
                       "FROM scores " \
                       "INNER JOIN students " \
                       "ON scores.student_id = students.id " \
                       "INNER JOIN (SELECT student_id, RANK() OVER (ORDER BY tvalue DESC) AS rank FROM (SELECT student_id, SUM(value) AS tvalue FROM scores WHERE exam_id = ? GROUP BY student_id) AS t) AS r " \
                       "ON r.student_id = scores.student_id " \
                       "WHERE exam_id = ? " \
                       "AND class = ? " \
                       "AND scores.student_id IN (SELECT student_id FROM scores INNER JOIN students ON students.id = scores.student_id WHERE exam_id = ? AND class = ? GROUP BY name HAVING COUNT(value) >= 6)" \
                       "GROUP BY name " \
                       "ORDER BY SUM(value) " \
                       "LIMIT 10"

    cur.execute(last10_total_sql, (exam_id, exam_id, class_id, exam_id, class_id))
    last10_total_ids = []
    last10_total_names = []
    last10_total_scores = []
    last10_total_ranks = []
    data = list(cur)
    for student_id, name, score, grade_rank in data:
        last10_total_ids.append(student_id)
        last10_total_names.append(name)
        last10_total_scores.append(score)
        last10_total_ranks.append(grade_rank)
    last10_total_avg = numpy.average(last10_total_scores)
    last10_total_std = numpy.std(last10_total_scores)
    total_avg_rank_sql = "SELECT DISTINCT rank " \
                         "FROM (SELECT tvalue, RANK() OVER (ORDER BY tvalue DESC) AS rank FROM (SELECT student_id, name, SUM(value) AS tvalue FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? GROUP BY name ORDER BY SUM(value) DESC) AS t  ) " \
                         "AS r WHERE tvalue = ?"
    cur.execute(total_avg_rank_sql, (exam_id, int(last10_total_avg),))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        total_avg_rank_sql2 = "SELECT COUNT(*) " \
                              "FROM (SELECT SUM(value) AS value FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? GROUP BY name ORDER BY SUM(value) DESC) AS t " \
                              "WHERE value >= ?"
        cur.execute(total_avg_rank_sql2, (exam_id, last10_total_avg,))
        data = list(cur)
        if data[0][0] == 0:
            last10_total_avg_rank = 1
        else:
            last10_total_avg_rank = data[0][0]
    else:
        last10_total_avg_rank = data[0][0]
    last10_total_info = []
    scoresLen = len(last10_total_scores)
    for i in range(scoresLen - 1, -1, -1):
        thisInfo = {
            "id": last10_total_ids[i],
            "name": last10_total_names[i],
            "score": last10_total_scores[i],
            "gradeRank": last10_total_ranks[i]
        }
        last10_total_info.append(thisInfo)
    subject_info["last10ScoreList"] = last10_total_info
    subject_info["last10AvgScore"] = last10_total_avg
    subject_info["last10AvgRank"] = last10_total_avg_rank
    subject_info["last10Std"] = last10_total_std

    last_total_sql = "SELECT scores.student_id, name, SUM(value), r.rank " \
                     "FROM scores " \
                     "INNER JOIN students " \
                     "ON scores.student_id = students.id " \
                     "INNER JOIN (SELECT student_id, RANK() OVER (ORDER BY tvalue DESC) AS rank FROM (SELECT student_id, SUM(value) AS tvalue FROM scores WHERE exam_id = ? GROUP BY student_id) AS t) AS r " \
                     "ON r.student_id = scores.student_id " \
                     "WHERE exam_id = ? " \
                     "AND class = ? " \
                     "GROUP BY name " \
                     "ORDER BY SUM(value) " \
                     "LIMIT 1"
    cur.execute(last_total_sql, (exam_id, exam_id, class_id))
    data = list(cur)
    last_id, last_name, last_score, last_rank = data[0]
    subject_info["lastId"] = last_id
    subject_info["lastName"] = last_name
    subject_info["lastScore"] = last_score
    subject_info["lastRank"] = last_rank
    result = {"code": 200, "msg": "Ok.", "data": subject_result}
    # Flask's jsonify() seems to be broken, so I use json.dumps() instead.
    # TypeError: '<' not supported between instances of 'str' and 'int'
    return json.dumps(result), 200, {'Content-Type': 'text/css; charset=utf-8'}


@bp.route("data/by_person/<int:student_id>/exam/<int:exam_id>", methods=("GET",))
def get_data_by_person(student_id, exam_id):
    db = get_db()
    cur = db.cursor()
    class_sql = "SELECT class FROM students WHERE id = ?"
    cur.execute(class_sql, (student_id,))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        ret = {"code": 404, "msg": "student_id Not Found", "data": {}}
        return ret
    class_id = data[0][0]
    sql = "SELECT scores.subject_id, scores.value, tr.rank AS grade_rank, cr.rank AS class_rank " \
          "FROM scores " \
          "INNER JOIN students " \
          "ON scores.student_id = students.id " \
          "INNER JOIN (SELECT * FROM (SELECT student_id, subject_id, value, RANK() OVER (PARTITION BY subject_id ORDER BY value DESC) AS rank FROM scores WHERE exam_id = ?) AS sub WHERE student_id = ?) AS tr " \
          "ON scores.student_id = tr.student_id AND tr.subject_id = scores.subject_id " \
          "INNER JOIN (SELECT * FROM (SELECT student_id, subject_id, value, RANK() OVER (PARTITION BY subject_id ORDER BY value DESC) AS rank FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? AND class = ?) AS sub WHERE student_id = ?) AS cr " \
          "ON scores.student_id = cr.student_id AND cr.subject_id = scores.subject_id " \
          "WHERE scores.student_id = ? AND exam_id = ?"
    cur.execute(sql, (exam_id, student_id, exam_id, class_id, student_id, student_id, exam_id))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        ret = {"code": 404, "msg": "Not Found", "data": {}}
    else:
        temp = {}
        for subject_id, value, grade_rank, class_rank in data:
            temp[subject_id] = [value, class_rank, grade_rank]
        result = {}
        for key, value in temp.items():
            result[key] = value

        total_sql = "SELECT temp.v, temp.rank " \
                    "FROM(SELECT tvalue.student_id , v, RANK() OVER (ORDER BY tvalue.v DESC) AS rank FROM (SELECT student_id, SUM(value) AS v FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? GROUP BY name) AS tvalue) AS temp " \
                    "WHERE temp.student_id = ?"
        cur.execute(total_sql, (exam_id, student_id))
        data = list(cur)
        total_score, total_grade_rank = data[0]
        class_rank_sql = "SELECT temp2.rank " \
                         "FROM(SELECT tvalue.student_id , v, RANK() OVER (ORDER BY tvalue.v DESC) AS rank FROM (SELECT student_id, SUM(value) AS v FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? AND class = ? GROUP BY name) AS tvalue) AS temp2 " \
                         "WHERE temp2.student_id = ?"
        cur.execute(class_rank_sql, (exam_id, class_id, student_id))
        data = list(cur)
        total_class_rank = data[0][0]
        result[255] = [total_score, total_class_rank, total_grade_rank]
        ret = {"code": 200, "msg": "Ok", "data": {"scores": result}}
    return ret

@bp.route("/data/by_person/<int:student_id>/exam", methods=("GET",))
def get_exam_by_person(student_id):
    db = get_db()
    cur = db.cursor()
    sql = "SELECT exam_id " \
          "FROM scores " \
          "INNER JOIN students " \
          "ON scores.student_id = students.id " \
          "WHERE student_id = ? " \
          "GROUP BY exam_id " \
          "HAVING COUNT(*) >= 6"
    cur.execute(sql, (student_id, ))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        ret = {"code": 404, "msg": "Not Found.", "data": {}}
    else:
        result = [x[0] for x in data]
        ret = {"code": 200, "msg": "Ok.", "data": {"exams": result}}
    return ret

@bp.route("data/by_person/<int:student_id>/exam_detail", methods=("GET",))
def get_exam_detail_by_person(student_id):
    db = get_db()
    cur = db.cursor()
    class_sql = "SELECT class FROM students WHERE id = ?"
    cur.execute(class_sql, (student_id,))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        ret = {"code": 404, "msg": "student_id Not Found", "data": {}}
        return ret
    class_id = data[0][0]

    sql = "SELECT exam_id " \
          "FROM scores " \
          "INNER JOIN students " \
          "ON scores.student_id = students.id " \
          "WHERE student_id = ? " \
          "GROUP BY exam_id " \
          "HAVING COUNT(*) >= 6"
    cur.execute(sql, (student_id,))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        ret = {"code": 404, "msg": "Not Found.", "data": {}}
        return ret
    else:
        valid_exam_list = [x[0] for x in data]

    ret_result = {}

    for exam_id in valid_exam_list:
        sql = "SELECT scores.subject_id, scores.value, tr.rank AS grade_rank, cr.rank AS class_rank " \
              "FROM scores " \
              "INNER JOIN students " \
              "ON scores.student_id = students.id " \
              "INNER JOIN (SELECT * FROM (SELECT student_id, subject_id, value, RANK() OVER (PARTITION BY subject_id ORDER BY value DESC) AS rank FROM scores WHERE exam_id = ?) AS sub WHERE student_id = ?) AS tr " \
              "ON scores.student_id = tr.student_id AND tr.subject_id = scores.subject_id " \
              "INNER JOIN (SELECT * FROM (SELECT student_id, subject_id, value, RANK() OVER (PARTITION BY subject_id ORDER BY value DESC) AS rank FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? AND class = ?) AS sub WHERE student_id = ?) AS cr " \
              "ON scores.student_id = cr.student_id AND cr.subject_id = scores.subject_id " \
              "WHERE scores.student_id = ? AND exam_id = ?"
        cur.execute(sql, (exam_id, student_id, exam_id, class_id, student_id, student_id, exam_id))
        data = list(cur)
        if len(data) == 0 or data[0][0] is None:
            ret = {"code": 404, "msg": "Not Found", "data": {}}
        else:
            temp = {}
            for subject_id, value, grade_rank, class_rank in data:
                temp[subject_id] = [value, class_rank, grade_rank]
            result = {}
            for key, value in temp.items():
                result[key] = value

            total_sql = "SELECT temp.v, temp.rank " \
                        "FROM(SELECT tvalue.student_id , v, RANK() OVER (ORDER BY tvalue.v DESC) AS rank FROM (SELECT student_id, SUM(value) AS v FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? GROUP BY name) AS tvalue) AS temp " \
                        "WHERE temp.student_id = ?"
            cur.execute(total_sql, (exam_id, student_id))
            data = list(cur)
            total_score, total_grade_rank = data[0]
            class_rank_sql = "SELECT temp2.rank " \
                             "FROM(SELECT tvalue.student_id , v, RANK() OVER (ORDER BY tvalue.v DESC) AS rank FROM (SELECT student_id, SUM(value) AS v FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? AND class = ? GROUP BY name) AS tvalue) AS temp2 " \
                             "WHERE temp2.student_id = ?"
            cur.execute(class_rank_sql, (exam_id, class_id, student_id))
            data = list(cur)
            total_class_rank = data[0][0]
            result[255] = [total_score, total_class_rank, total_grade_rank]
            ret_result[exam_id] = result
    ret = {"code": 200, "msg": "Ok", "data": {"examDetails": ret_result}}
    return ret
