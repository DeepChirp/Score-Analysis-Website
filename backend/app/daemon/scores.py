import io

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, current_app
)
import numpy
from daemon.db import get_db
import json
import random
import os
import csv

bp = Blueprint("scores", __name__, url_prefix="/scores")

grades_name_to_id = {
    "本高2023届": 1
}

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

student_to_id = {}
exams_to_id = {}

semester_to_id ={
    "高一上": 1,
    "高一下": 2,
    "高二上": 3,
    "高二下": 4,
    "高三上": 5,
    "高三下": 6
}
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
    cur.execute(sql, (exam_id,))
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


@bp.route("/basic_info/subject_overall_data/exam/<int:exam_id>", methods=("GET",))
def get_exam_basic_data(exam_id):
    # SELECT class, COUNT(student_id) FROM (SELECT DISTINCT student_id FROM scores WHERE exam_id = 46) AS t INNER JOIN students ON t.student_id = students.id GROUP BY students.class;
    db = get_db()
    cur = db.cursor()
    sql = "SELECT COUNT(*), AVG(value), MAX(value)" \
          "FROM scores " \
          "WHERE exam_id = ? " \
          "AND subject_id = ? " \
          "AND student_id IN (SELECT student_id FROM scores WHERE exam_id = 44 GROUP BY student_id HAVING COUNT(*) >= 6)"
    result_by_subject = {}
    for subject_id in range(1, 10):
        cur.execute(sql, (exam_id, subject_id))
        data = list(cur)
        if subject_id == 1 and (len(data) == 0 or data[0][0] == None):
            ret = {"code": 404, "msg": "Not Found.", "data": {}}
            return ret
        if len(data) == 0 or data[0][0] == None:
            continue
        else:
            result_by_subject[subject_id] = {"validNum": data[0][0], "gradeAvgScore": data[0][1],
                                             "gradeMaxScore": data[0][2]}
    total_sql = "SELECT COUNT(*), AVG(tvalue), MAX(tvalue)" \
                "FROM(SELECT SUM(value) AS tvalue FROM scores WHERE exam_id = ? AND student_id IN (SELECT student_id FROM scores WHERE exam_id = ? GROUP BY student_id HAVING COUNT(*) >= 6) GROUP BY student_id) AS t"
    cur.execute(total_sql, (exam_id, exam_id))
    data = list(cur)
    result_by_subject[255] = {"validNum": data[0][0], "gradeAvgScore": data[0][1], "gradeMaxScore": data[0][2]}
    ret = {"code": 200, "msg": "Ok.", "data": {"overallData": result_by_subject}}
    return ret


def get_grade_rank(cur, subject_id, exam_id, target_score):
    rank_sql = "SELECT DISTINCT r.rank " \
               "FROM (SELECT value, RANK() OVER (ORDER BY value DESC) AS rank FROM scores WHERE subject_id = ? AND exam_id = ?) AS r " \
               "WHERE value = ?"

    cur.execute(rank_sql, (subject_id, exam_id, int(target_score)))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        rank2_sql = "SELECT COUNT(*) " \
                    "FROM scores " \
                    "WHERE subject_id = ? " \
                    "AND exam_id = ? " \
                    "AND value >= ?"
        cur.execute(rank2_sql, (subject_id, exam_id, target_score))
        data = list(cur)
        return data[0][0]
    else:
        return data[0][0]


def get_grade_total_rank(cur, exam_id, target_score):
    rank_sql = "SELECT rank " \
               "FROM(SELECT SUM(value) AS tvalue, RANK() OVER (ORDER BY tvalue DESC) AS rank FROM scores  INNER JOIN students  ON scores.student_id = students.id  WHERE exam_id = ? AND student_id IN (SELECT student_id FROM scores WHERE exam_id = ? GROUP BY student_id HAVING COUNT(*) >= 6)  GROUP BY student_id) AS r " \
               "WHERE tvalue = ?"
    cur.execute(rank_sql, (exam_id, exam_id, int(target_score)))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        rank2_sql = "SELECT COUNT(*) " \
                    "FROM(SELECT SUM(value) FROM scores WHERE exam_id = ? GROUP BY student_id HAVING SUM(value) >= ?) AS v"
        cur.execute(rank2_sql, (exam_id, target_score))
        data = list(cur)
        return data[0][0]
    else:
        return data[0][0]


@bp.route("/data/chart_data/by_subject/<int:subject_id>/by_class/<int:class_id>")
# 班级平均分，班级平均分排名，班级标准差，前十平均分，前十平均分排名，前十标准差，后十平均分，后十平均分排名，后十标准差 年级平均分
def get_chart_data_by_subject(subject_id, class_id):
    db = get_db()
    cur = db.cursor()
    class_data = {}
    if subject_id != 255:
        class_avg_sql = "SELECT exam_id, AVG(value) " \
                        "FROM scores " \
                        "INNER JOIN students " \
                        "ON students.id = scores.student_id " \
                        "WHERE subject_id = ? " \
                        "AND class = ? " \
                        "GROUP BY exam_id"
        cur.execute(class_avg_sql, (subject_id, class_id))
        data = list(cur)
        if len(data) == 0 or data[0][0] is None:
            ret = {"code": 404, "msg": "Not Found.", "data": {}}
            return ret
        for exam_id, avg_score in data:
            class_data[exam_id] = {
                "avgScore": avg_score,
                "avgScoreRank": get_grade_rank(cur, subject_id, exam_id, avg_score)
            }

        for exam_id in class_data.keys():
            class_data_sql = "SELECT value " \
                             "FROM scores " \
                             "INNER JOIN students " \
                             "ON scores.student_id = students.id " \
                             "WHERE exam_id = ? " \
                             "AND subject_id = ? " \
                             "AND class = ?"
            cur.execute(class_data_sql, (exam_id, subject_id, class_id))
            data = list(cur)
            score_lst = [x[0] for x in data]
            class_data[exam_id]["std"] = numpy.std(score_lst)

        for exam_id in class_data.keys():
            first10_data_sql = "SELECT value " \
                               "FROM scores " \
                               "INNER JOIN students " \
                               "ON students.id = scores.student_id " \
                               "WHERE exam_id = ? " \
                               "AND subject_id = ? " \
                               "AND class = ? " \
                               "ORDER BY value DESC " \
                               "LIMIT 10"
            cur.execute(first10_data_sql, (exam_id, subject_id, class_id))
            score_lst = [x[0] for x in list(cur)]
            class_data[exam_id]["first10AvgScore"] = numpy.average(score_lst)
            class_data[exam_id]["first10AvgScoreRank"] = get_grade_rank(cur, subject_id, exam_id,
                                                                        class_data[exam_id]["first10AvgScore"])
            class_data[exam_id]["first10std"] = numpy.std(score_lst)

        for exam_id in class_data.keys():
            last10_data_sql = "SELECT value " \
                               "FROM scores " \
                               "INNER JOIN students " \
                               "ON students.id = scores.student_id " \
                               "WHERE exam_id = ? " \
                               "AND subject_id = ? " \
                               "AND class = ? " \
                               "ORDER BY value " \
                               "LIMIT 10"
            cur.execute(last10_data_sql, (exam_id, subject_id, class_id))
            score_lst = [x[0] for x in list(cur)]
            class_data[exam_id]["last10AvgScore"] = numpy.average(score_lst)
            class_data[exam_id]["last10AvgScoreRank"] = get_grade_rank(cur, subject_id, exam_id,
                                                                       class_data[exam_id]["last10AvgScore"])
            class_data[exam_id]["last10std"] = numpy.std(score_lst)

        grade_avg_score_sql = "SELECT exam_id, AVG(value) " \
                              "FROM scores " \
                              "WHERE subject_id = ? " \
                              "GROUP BY exam_id"
        cur.execute(grade_avg_score_sql, (subject_id,))
        data = list(cur)
        for exam_id, avg_score in data:
            class_data[exam_id]["gradeAvgScore"] = avg_score

    else:
        exam_lst_sql = "SELECT DISTINCT exam_id " \
                       "FROM scores " \
                       "INNER JOIN students " \
                       "ON students.id = scores.student_id " \
                       "WHERE class = ?"
        cur.execute(exam_lst_sql, (class_id,))
        exam_lst = [x[0] for x in list(cur)]
        for exam_id in exam_lst:
            class_total_data_sql = "SELECT SUM(value) " \
                                   "FROM scores " \
                                   "INNER JOIN students " \
                                   "ON scores.student_id = students.id " \
                                   "WHERE exam_id = ? " \
                                   "AND class = ? " \
                                   "GROUP BY student_id"
            cur.execute(class_total_data_sql, (exam_id, class_id))
            data = list(cur)
            if len(data) == 0 or data[0][0] is None:
                ret = {"code": 404, "msg": "Not Found.", "data": {}}
                return ret
            score_lst = [x[0] for x in data]
            class_data[exam_id] = {}
            class_data[exam_id]["avgScore"] = numpy.average(score_lst)
            class_data[exam_id]["avgScoreRank"] = get_grade_total_rank(cur, exam_id, class_data[exam_id]["avgScore"])
            class_data[exam_id]["std"] = numpy.std(score_lst)
            class_total_first10_data_sql = "SELECT SUM(value) " \
                                           "FROM scores " \
                                           "INNER JOIN students " \
                                           "ON scores.student_id = students.id " \
                                           "WHERE exam_id = ? " \
                                           "AND class = ? " \
                                           "GROUP BY student_id " \
                                           "ORDER BY SUM(value) DESC " \
                                           "LIMIT 10"
            cur.execute(class_total_first10_data_sql, (exam_id, class_id))
            score_lst = [x[0] for x in list(cur)]
            class_data[exam_id]["first10AvgScore"] = numpy.average(score_lst)
            class_data[exam_id]["first10AvgScoreRank"] = get_grade_total_rank(cur, exam_id, class_data[exam_id]["first10AvgScore"])
            class_data[exam_id]["first10std"] = numpy.std(score_lst)

            class_total_last10_data_sql = "SELECT SUM(value) " \
                                          "FROM scores " \
                                          "INNER JOIN students " \
                                          "ON scores.student_id = students.id " \
                                          "WHERE exam_id = ? " \
                                          "AND class = ? " \
                                          "AND student_id IN (SELECT student_id FROM scores WHERE exam_id = ? GROUP BY student_id HAVING COUNT(id) >= 6) " \
                                          "GROUP BY student_id " \
                                          "ORDER BY SUM(value) " \
                                          "LIMIT 10"
            cur.execute(class_total_last10_data_sql, (exam_id, class_id, exam_id))
            score_lst = [x[0] for x in list(cur)]
            class_data[exam_id]["last10AvgScore"] = numpy.average(score_lst)
            class_data[exam_id]["last10AvgScoreRank"] = get_grade_total_rank(cur, exam_id, class_data[exam_id]["last10AvgScore"])
            class_data[exam_id]["last10std"] = numpy.std(score_lst)

            grade_total_avg_sql = "SELECT AVG(tvalue) " \
                                  "FROM(SELECT SUM(value) AS tvalue FROM scores WHERE exam_id = ? AND student_id IN (SELECT student_id FROM scores WHERE exam_id = ? GROUP BY student_id HAVING COUNT(id) >= 6) GROUP BY student_id) AS t"
            cur.execute(grade_total_avg_sql, (exam_id, exam_id))
            class_data[exam_id]["gradeAvgScore"] = list(cur)[0][0]

    ret = {"code": 200, "msg": "Ok.", "data": {"chartData": class_data}}
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
    return json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'}


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

    class_sql = "SELECT subject_id, MAX(value), AVG(value) " \
                "FROM scores " \
                "INNER JOIN students " \
                "ON students.id = scores.student_id " \
                "WHERE class = ? " \
                "AND exam_id = ? " \
                "GROUP BY subject_id"
    cur.execute(class_sql, (class_id, exam_id))
    class_data = list(cur)

    grade_sql = "SELECT subject_id, MAX(value), AVG(value) " \
                "FROM scores " \
                "INNER JOIN students " \
                "ON students.id = scores.student_id " \
                "WHERE exam_id = ? " \
                "GROUP BY subject_id"
    cur.execute(grade_sql, (exam_id,))
    grade_data = list(cur)

    if len(data) == 0 or data[0][0] is None:
        ret = {"code": 404, "msg": "Not Found", "data": {}}
    else:
        temp = {}
        for subject_id, value, grade_rank, class_rank in data:
            temp[subject_id] = [value, class_rank, grade_rank]
        result = {}
        for key, value in temp.items():
            result[key] = value

        for subject_id, max_value, avg_value in class_data:
            if subject_id in temp:
                result[subject_id].append(max_value)
                result[subject_id].append(avg_value)
                total_count_sql = "SELECT COUNT(*) " \
                                  "FROM scores " \
                                  "INNER JOIN students " \
                                  "ON students.id = scores.student_id " \
                                  "WHERE class = ? " \
                                  "AND subject_id = ? " \
                                  "AND exam_id = ?"
                cur.execute(total_count_sql, (class_id, subject_id, exam_id))
                data = list(cur)
                result[subject_id].append(data[0][0])


        for subject_id, max_value, avg_value in grade_data:
            if subject_id in temp:
                result[subject_id].append(max_value)
                result[subject_id].append(avg_value)
                total_count_sql = "SELECT COUNT(*) " \
                                  "FROM scores " \
                                  "INNER JOIN students " \
                                  "ON students.id = scores.student_id " \
                                  "WHERE subject_id = ? " \
                                  "AND exam_id = ?"
                cur.execute(total_count_sql, (subject_id, exam_id))
                data = list(cur)
                result[subject_id].append(data[0][0])

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

        class_data_sql = "SELECT MAX(tvalue), AVG(tvalue) " \
                         "FROM (SELECT SUM(value) AS tvalue FROM scores INNER JOIN students ON students.id = scores.student_id WHERE class = ? AND exam_id = ? GROUP BY student_id) AS t"
        cur.execute(class_data_sql, (class_id, exam_id))
        class_data = list(cur)

        class_total_sql = "SELECT COUNT(*) " \
                          "FROM (SELECT student_id FROM scores INNER JOIN students ON students.id = scores.student_id WHERE exam_id = ? AND class = ? AND class_divide = 0 GROUP BY student_id HAVING COUNT(*) >= 6) AS t"
        cur.execute(class_total_sql, (exam_id, class_id))
        class_total = list(cur)

        grade_data_sql = "SELECT MAX(tvalue), AVG(tvalue) " \
                         "FROM (SELECT SUM(value) AS tvalue FROM scores INNER JOIN students ON students.id = scores.student_id WHERE exam_id = ? GROUP BY student_id) AS t"
        cur.execute(grade_data_sql, (exam_id, ))
        grade_data = list(cur)

        grade_total_sql = "SELECT COUNT(*) " \
                          "FROM (SELECT student_id FROM scores INNER JOIN students ON students.id = scores.student_id WHERE exam_id = ? AND class_divide = 0 GROUP BY student_id HAVING COUNT(*) >= 6) AS t"
        cur.execute(grade_total_sql, (exam_id,))
        grade_total = list(cur)

        result[255] = [total_score, total_class_rank, total_grade_rank, class_data[0][0], class_data[0][1], class_total[0][0], grade_data[0][0], grade_data[0][1], grade_total[0][0]]
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
    cur.execute(sql, (student_id,))
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
            ret = {"code": 404, "msg": "Not Found for exam_id: {}".format(exam_id), "data": {}}
            return ret
        else:
            temp = {}
            for subject_id, value, grade_rank, class_rank in data:
                temp[subject_id] = [value, class_rank, grade_rank]
            result = {}
            for key, value in temp.items():
                result[key] = value

            class_data_sql = "SELECT subject_id, MAX(value), AVG(value) " \
                             "FROM scores " \
                             "INNER JOIN students " \
                             "ON scores.student_id = students.id " \
                             "WHERE exam_id = ? " \
                             "AND class = ? " \
                             "GROUP BY subject_id"
            cur.execute(class_data_sql, (exam_id, class_id))
            data = list(cur)
            for subject_id, max_score, avg_score in data:
                if subject_id in result:
                    result[subject_id].append(max_score)
                    result[subject_id].append(avg_score)

            grade_data_sql = "SELECT subject_id, MAX(value), AVG(value) " \
                             "FROM scores " \
                             "INNER JOIN students " \
                             "ON scores.student_id = students.id " \
                             "WHERE exam_id = ? " \
                             "GROUP BY subject_id"
            cur.execute(grade_data_sql, (exam_id,))
            data = list(cur)
            for subject_id, max_score, avg_score in data:
                if subject_id in result:
                    result[subject_id].append(max_score)
                    result[subject_id].append(avg_score)

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

            class_total_data_sql = "SELECT MAX(tvalue), AVG(tvalue) " \
                                   "FROM (SELECT SUM(value) AS tvalue FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? AND class = ? GROUP BY student_id) AS t"
            cur.execute(class_total_data_sql, (exam_id, class_id))
            data = list(cur)

            for max_score, avg_score in data:
                result[255].append(max_score)
                result[255].append(avg_score)

            grade_total_data_sql = "SELECT MAX(tvalue), AVG(tvalue) " \
                                   "FROM (SELECT SUM(value) AS tvalue FROM scores INNER JOIN students ON scores.student_id = students.id WHERE exam_id = ? GROUP BY student_id) AS t"
            cur.execute(grade_total_data_sql, (exam_id, ))
            data = list(cur)

            for max_score, avg_score in data:
                result[255].append(max_score)
                result[255].append(avg_score)
            ret_result[exam_id] = result
    ret = {"code": 200, "msg": "Ok", "data": {"examDetails": ret_result}}
    return ret

def get_unique_id(instance_path):
    rand_directory = random.randint(0, 1000000000)
    if os.path.exists("{}/{}".format(instance_path, rand_directory)):
        return get_unique_id(instance_path)
    else:
        return rand_directory


@bp.route("data/upload", methods=("GET", "POST"))
def upload_data():
    instance_path = current_app.instance_path
    if request.method == "POST":
        unique_id = get_unique_id(instance_path)
        f = request.files["file-uploader"]
        f.save("{}/{}".format(instance_path, unique_id))
        file_sql = "INSERT INTO uploads (unique_id, filename) VALUES (?, ?)"
        db = get_db()
        cur = db.cursor()
        cur.execute(file_sql, (unique_id, f.filename))
        db.commit()
        return str(unique_id), 200, {'Content-Type': 'text/plain'}
    else:
        request.args.get("file-uploader")
        return "OK", 200, {'Content-Type': 'text/plain'}

def load_db(filename, conn, csv_reader):
    cur = conn.cursor()
    front, prefix = filename.split(".")
    if prefix == "csv":
        semester_name, exam_name = front[2:].split("_")
        for row in csv_reader:
            grade_name, class_id, student_name, chinese, math, english, physics, chemistry, biology, politic, history, geography = row

            if grade_name == "年级":
                continue

            if grade_name in grades_name_to_id:
                grade_id = grades_name_to_id[grade_name]
            else:
                grades_id_sql = "SELECT id FROM grades WHERE name = ?"
                cur.execute(grades_id_sql, (grade_name,))
                data = list(cur)
                if len(data) != 0 and data[0][0] is not None:
                    grade_id = data[0][0]
                    grades_name_to_id[grade_name] = grade_id
                else:
                    grades_sql = "INSERT INTO grades (name) VALUES (?)"
                    cur.execute(grades_sql, (grade_name,))
                    conn.commit()
                    grades_id_sql = "SELECT id FROM grades WHERE name = ?"
                    cur.execute(grades_id_sql, (grade_name,))
                    grade_id = list(cur)[0][0]
                    grades_name_to_id[grade_name] = grade_id

            if student_name in student_to_id:
                student_id = student_to_id[student_name]
            else:
                id_sql = "SELECT id FROM students WHERE name = ?"
                cur.execute(id_sql, (student_name,))
                print(student_name)
                data = list(cur)
                if len(data) != 0 and data[0][0] is not None:
                    student_id = data[0][0]
                    student_to_id[student_name] = student_id
                else:
                    isql = "INSERT INTO students (class, name, class_divide, grade_id) VALUES (?, ?, ?, ?)"
                    if class_id.strip() == "":
                        class_id = "17班"
                    cur.execute(isql, (int(class_id[:-1]), student_name, 0, grade_id))
                    conn.commit()
                    id_sql = "SELECT id FROM students WHERE name = ?"
                    cur.execute(id_sql, (student_name,))
                    data = list(cur)
                    student_id = data[0][0]

            exam_saved_name = "{}_{}".format(semester_name, exam_name)
            if exam_saved_name in exams_to_id:
                exam_id = exams_to_id[exam_saved_name]
            else:
                exams_id_sql = "SELECT id FROM exams WHERE name = ?"
                cur.execute(exams_id_sql, (exam_saved_name, ))
                data = list(cur)
                if len(data) != 0 and data[0][0] is not None:
                    exam_id = data[0][0]
                    exams_to_id[exam_saved_name] = exam_id
                else:
                    exams_sql = "INSERT INTO exams (name) VALUES (?)"
                    cur.execute(exams_sql, (exam_saved_name,))
                    conn.commit()
                    exams_id_sql = "SELECT id FROM exams WHERE name = ?"
                    cur.execute(exams_id_sql, (exam_saved_name,))
                    exam_id = list(cur)[0][0]
                    exams_to_id[exam_saved_name] = exam_id

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
@bp.route("/data/loadcsv/<int:unique_id>", methods=("GET", ))
def load_csv(unique_id):
    instance_path = current_app.instance_path
    db = get_db()
    cur = db.cursor()
    try:
        with open("{}/{}".format(instance_path, unique_id), "r") as f:
            reader = csv.reader(f)
            file_sql = "SELECT filename FROM uploads WHERE unique_id = ?"
            cur.execute(file_sql, (unique_id, ))
            filename = list(cur)[0][0]
            load_db(filename, db, reader)
            file_del_sql = "DELETE FROM uploads WHERE unique_id = ?"
            cur.execute(file_del_sql, (unique_id,))
            db.commit()
            os.remove("{}/{}".format(instance_path, unique_id))
    except FileNotFoundError:
        return {"code": 404, "msg": "File Not Found for uniqueId: {}".format(unique_id), "data": {}}
    ret = {"code": 200, "msg": "Ok", "data": {}}
    return ret

@bp.route("/basic_info/saved_name/<int:exam_id>", methods=("GET", ))
def saved_name(exam_id):
    db = get_db()
    cur = db.cursor()
    sql = "SELECT name " \
          "FROM exams " \
          "WHERE id = ?"
    cur.execute(sql, (exam_id, ))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        ret = {"code": 404, "msg": "Not found.", "data": {}}
    else:
        ret = {"code": 200, "msg": "Ok.", "data": {"savedName": data[0][0]}}
    return ret
@bp.route("/data/downloadcsv/<int:exam_id>", methods=("GET", ))
def download_csv(exam_id):
    db = get_db()
    cur = db.cursor()
    name_sql = "SELECT name " \
               "FROM exams " \
               "WHERE id = ?"
    cur.execute(name_sql, (exam_id, ))
    data = list(cur)
    if len(data) == 0 or data[0][0] is None:
        return "exam for exam_id: {} not found".format(exam_id), 404
    else:
        string_output = io.StringIO()
        writer = csv.writer(string_output)
        writer.writerow(["年级", "班级", "姓名", "语文", "数学", "外语", "物理", "化学", "生物", "政治", "历史", "地理"])
        data_sql = "SELECT students.name, class, subject_id, value " \
                   "FROM scores " \
                   "INNER JOIN students " \
                   "ON students.id = scores.student_id " \
                   "INNER JOIN subjects " \
                   "ON subjects.id = scores.subject_id " \
                   "WHERE exam_id = ?"
        cur.execute(data_sql, (exam_id, ))
        data = list(cur)
        student_data = {}
        for student_name, class_id, subject_id, value in data:
            student_lst = student_data.setdefault(student_name, ["本高2023届", "{}班".format(class_id), student_name] + ["/"] * 9)
            op_col = subject_id + 2
            student_lst[op_col] = value
        for row in student_data.values():
            writer.writerow(row)

        return string_output.getvalue(), 200, {'Content-Type': 'text/csv'}
