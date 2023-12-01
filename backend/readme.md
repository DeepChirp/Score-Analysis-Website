# Backend Daemon V0.10.1

- Fix bug in /data/chart_data where total score analysis was mistakenly placed into examId.

# API V0.10.0

## V0.10.0改动
- 新增：/data/chart_data/by_subject/<int:subject_id>/by_class/<int:class_id>

SubjectId与科目名称对照表：
|SubjectId|SubjectName|
|  ----  | ----  |
|1|语文|
|2|数学|
|3|外语|
|4|物理|
|5|化学|
|6|生物|
|7|政治|
|8|历史|
|9|地理|
|255|六科总分|

## `/scores`
### GET `/basic_info/exam`
Input: None

Output:
HTTP 状态码始终为200，应根据返回的JSON判断：
ret:
|Item|Value|Description|
|  ----  | ----  | ---- |
|code|int，API状态码|若查询成功，则为200；若没有一次考试，则为404（正常情况下不会出现）|
|msg|String，（错误）信息|-|
|data|dict/Object，查询的数据|详见下|

data:
|Item|Value|Description|
|  ----  | ----  | ---- |
|exams|dict/Object，ExamInfoBySemester|详见下|

ExamInfoBySemester：
|Item|Value|Description|
|  ----  | ----  | ---- |
|1|List，ExamInfoListOfSemester|详见下|
|2|List，ExamInfoListOfSemester|详见下|
|...(semester_id)...|List，ExamInfoListOfSemester|-|

ExamInfoListOfSemester：
内含对应学期的考试
|Index|Value|Description|
|  ----  | ----  | ---- |
|0|dict/Object，ExamInfo|详见下|
|1|dict/Object，ExamInfo|详见下|
|2|dict/Object，ExamInfo|详见下|
|...|dict/Object，ExamInfo|-|

ExamInfo：
|Item|Value|Description|
|  ----  | ----  | ---- |
|examId|Int，本次考试的id|-|
|semesterId|Int，本学期的id|-|
|semesterName|String，本学期的名称|e.g高一上，高一下|
|examName|String，本次考试的名称|不含学期前缀，e.g期中，期末|

### GET `/basic_info/class/<int:exam_id>`
此API用于：在页面上选择要分析的考试后，可接下来选择要分析的班级
Input: 
- <int:exam_id>：欲查询的考试id

Output:
HTTP 状态码始终为200，应根据返回的JSON判断：
ret:
|Item|Value|Description|
|  ----  | ----  | ---- |
|code|int，API状态码|若查询成功，则为200；若考试id不存在，则为404|
|msg|String，（错误）信息|-|
|data|dict/Object，查询的数据|详见下|

data:
|Item|Value|Description|
|  ----  | ----  | ---- |
|classes|List，参考的班级|每个元素为一个参考的班级的id，保证按升序排列|


### GET `/basic_info/subject_overall_data/exam/<int:exam_id>`
Input:
- <int:exam_id>：欲查询的考试的id

Output:
HTTP 状态码始终为200，应根据返回的JSON判断：
ret:
|Item|Value|Description|
|  ----  | ----  | ---- |
|code|int，API状态码|若exam_id不存在，则为404；若查询成功，则为200|
|msg|String，（错误）信息|-|
|data|dict/Object，查询的数据|详见下|

data:
|Item|Value|Description|
|  ----  | ----  | ---- |
|overallData|overallDataBySubject(Object/dict)|详见下|

overallDataBySubject：
|Item|Value|Description|
|  ----  | ----  | ---- |
|1|overallData(Object/dict)，语文学科的总体数据|详见下|
|2|overallData(Object/dict)，数学学科的总体数据|详见下|
|3|overallData(Object/dict)，外语学科的总体数据|详见下|
|4|overallData(Object/dict)，物理学科的总体数据|详见下|
|5|overallData(Object/dict)，化学学科的总体数据|详见下|
|6|overallData(Object/dict)，生物学科的总体数据|详见下|
|7|overallData(Object/dict)，政治学科的总体数据|详见下|
|8|overallData(Object/dict)，历史学科的总体数据|详见下|
|9|overallData(Object/dict)，地理学科的总体数据|详见下|
|255|overallData(Object/dict)，总分的总体数据|详见下|

overallData：
|Item|Value|Description|
|  ----  | ----  | ---- |
|validNum|Int，全年级参加该科目考试的有效人数|-|
|gradeAvgScore|Double，全年级该科目平均分|-|
|gradeMaxScore|Double，全年级该科目最高分|-|


### GET `/basic_info/by_class/<int:class_id>/exam/<int:exam_id>`
Input:
- <int:class_id>：欲求班级
- <int:exam_id>：欲查询的考试的id

Output:
HTTP 状态码始终为200，应根据返回的JSON判断：
ret:
|Item|Value|Description|
|  ----  | ----  | ---- |
|code|int，API状态码|若class_id不存在，或exam_id不存在，则为404；若查询成功，则为200|
|msg|String，（错误）信息|-|
|data|dict/Object，查询的数据|详见下|

data:
|Item|Value|Description|
|  ----  | ----  | ---- |
|validNum|int，本次考试有效人数|有效人数指参加了全部科目考试的人数|

### GET `/data/chart_data/by_subject/<int:subject_id>/by_class/<int:class_id>`

Input:
- <int:exam_id>：欲查询的科目id
- <int:class_id>：欲求班级

Output:
HTTP 状态码始终为200，应根据返回的JSON判断：

ret:
|Item|Value|Description|
|  ----  | ----  | ---- |
|code|int，API状态码|若exam_id不存在，或class_id不存在，则为404；若查询成功，则为200|
|msg|String，（错误）信息|-|
|data|dict/Object，查询的数据|详见下|

data：
|Item|Value|Description|
|  ----  | ----  | ---- |
|chartData|ChartDataBySubject(Object/dict)，查询的科目成绩数据|详见下|

ChartDataBySubject：
|Item|Value|Description|
|  ----  | ----  | ---- |
|1|ChartData(Object/dict)，查询的科目对应考试的成绩数据|详见下|
|2|ChartData(Object/dict)，查询的科目对应考试的成绩数据|详见下|
|3|ChartData(Object/dict)，查询的科目对应考试的成绩数据|详见下|
|...(examId)...|ChartData(Object/dict)，查询的科目对应考试的成绩数据|详见下|

ChartData：
|Item|Value|Description|
|  ----  | ----  | ---- |
|gradeAvgScore|Double，全年级平均分|-|
|avgScore|Double，全班平均分|-|
|avgScoreRank|Int，全班平均分的年级排名|-|
|std|Double，该科目全班平均分的标准差|-|
|first10AvgScore|Double，该科目班级前十平均分|-|
|first10AvgScoreRank|Int，该科目班级前十平均分的年级排名|-|
|first10std|Double，该科目班级前十平均分的标准差|-|
|last10AvgScore|Double，该科目班级后十平均分|-|
|last10AvgScoreRank|Int，该科目班级后十平均分的年级排名|-|
|last10std|Double，该科目班级后十平均分的标准差|-|

### GET `/data/by_class/<int:class_id>/exam/<int:exam_id>`
Input:
- <int:class_id>：欲求班级
- <int:exam_id>：欲查询的考试的id

Output:
HTTP 状态码始终为200，应根据返回的JSON判断：

ret:
|Item|Value|Description|
|  ----  | ----  | ---- |
|code|int，API状态码|若class_id不存在，或exam_id不存在，则为404；若查询成功，则为200|
|msg|String，（错误）信息|-|
|data|dict/Object，查询的数据|详见下|

data：
|Item|Value|Description|
|  ----  | ----  | ---- |
|scores|List，查询的成绩数据|其中每个元素为ScoreObject(dict)详见下|

ScoreObject：
|Item|Value|Description|
|  ----  | ----  | ---- |
|name|String，学生姓名|-|
|id|Int，学生id|-|
|scores|List，该学生的成绩数据(ScoresList)|详见下|

ScoresList：
当学生未选考该科目时，该科目成绩为0
|Index|Value|Description|
|  ----  | ----  | ---- |
|0|Double, 0.0|预留|
|1|Double, 语文成绩|-|
|2|Double, 数学成绩|-|
|3|Double, 外语成绩|-|
|4|Double, 物理成绩|-|
|5|Double, 化学成绩|-|
|6|Double, 生物成绩|-|
|7|Double, 政治成绩|-|
|8|Double, 历史成绩|-|
|9|Double, 地理成绩|-|

### GET `/analysis/by_class/<int:class_id>/exam/<int:exam_id>`
Input:
- <int:student_id>：欲查询的班级
- <int:exam_id>：欲查询的考试的id

Output:
HTTP 状态码始终为200，应根据返回的JSON判断：

ret:
|Item|Value|Description|
|  ----  | ----  | ---- |
|code|int，API状态码|若class_id不存在，或exam_id不存在，则为404；若查询成功，则为200|
|msg|String，（错误）信息|-|
|data|AnalysisResultObject(dict/Object)，查询的数据|详见下|

AnalysisResultObject：
|Item|Value|Description|
|  ----  | ----  | ---- |
|1|SubjectAnalysisResultObject(dict/Object)，语文科目的统计数据|详见下|
|2|SubjectAnalysisResultObject(dict/Object)，数学科目的统计数据|详见下|
|...(SubjectId)...|SubjectAnalysisResultObjectt(dict/Object)|详见SubjectId与科目名称对照表|
|9|SubjectAnalysisResultObject(dict/Object)，地理科目的统计数据|详见下|
|255|SubjectAnalysisResultObject(dict/Object)，六科总分的统计数据|详见下|

注：当该班级无人选考对应SubjectId的科目时，AnalysisResultObject不存在对应的属性。

SubjectAnalysisResultObject:
|Item|Value|Description|
|  ----  | ----  | ---- |
|first10ScoreList|StudentScoreInfoListForAnalysis(List)，该科目班级前十的信息|详见下|
|first10AvgScore|Double，该科目班级前十的平均分|-|
|first10AvgRank|Int，该科目班级前十的平均分的年级排名|-|
|first10Std|Double，该科目班级前十分数的标准差|-|
|firstId|Int，该科目班级第一的学生的id|-|
|firstName|String，该科目班级第一的学生的姓名|-|
|firstScore|Double，该科目班级第一的学生的分数|-|
|firstRank|Int，该科目班级第一的学生的该科目分数的年级排名|-|
|last10ScoreList|StudentScoreInfoListForAnalysis(List)，该科目班级后十的信息|详见下|
|last10AvgScore|Double，该科目班级后十的平均分|-|
|last10AvgRank|Int，该科目班级后十的平均分的年级排名|-|
|last10Std|Double，该科目班级后十分数的标准差|-|
|classAvgScore|Double，该科目全班的平均分|-|
|classStd|Double，该科目全班的标准差|-|
|classAvgRank|Int，该科目全班的平均分的年级排名|-|
|lastId|Int，该科目班级后一的学生的id|-|
|lastName|String，该科目班级后一的学生的姓名|-|
|lastScore|Double，该科目班级后一的学生的分数|-|
|lastRank|Int，该科目班级后一的学生的该科目分数的年级排名|-|

StudentScoreInfoListForAnalysis：
|Index|Value|Description|
|  ----  | ----  | ---- |
|0|StudentScoreInfoForAnalysis(dict/Object)，该科目班级排名第一的学生成绩信息|详见下|
|1|StudentScoreInfoForAnalysis(dict/Object)，该科目班级排名第二的学生成绩信息|详见下|
|...|...|...|
|9|StudentScoreInfoForAnalysis(dict/Object)，该科目班级排名第十的学生成绩信息|详见下|

注：事实上，当多个学生成绩相同时，将被算作**多个**，因此该列表的最后一名不一定是真正意义上的第十（~~因为我偷了个懒~~）

StudentScoreInfoForAnalysis：
|Item|Value|Description|
|  ----  | ----  | ---- |
|id|Int，学生id|-|
|name|String，学生姓名|-|
|Score|Double，学生该科目成绩|-|
|gradeRank|Int，学生该科目年级排名|-|

### GET `/data/by_person/<int:student_id>/exam/<int:exam_id>`
Input:
- <int:student_id>：欲查询的学生id
- <int:exam_id>：欲查询的考试的id

Output:
HTTP 状态码始终为200，应根据返回的JSON判断：

ret:    
|Item|Value|Description|
|  ----  | ----  | ---- |
|code|int，API状态码|若student_id不存在，或exam_id不存在，则为404；若查询成功，则为200|
|msg|String，（错误）信息|-|
|data|dict/Object，查询的数据|详见下|

data：
|Item|Value|Description|
|  ----  | ----  | ---- |
|scores|ScoresBySubject(Object/dict)，查询的成绩数据|其中每个元素为StudentScoreInfoList(List)详见下|

ScoresBySubject:
当学生未选考该科目时，该科目将不出现在ScoresBySubject中
|Item|Value|Description|
|  ----  | ----  | ---- |
|0|StudentScoreList, [0.0, 0, 0]|预留|
|1|StudentScoreList, 语文成绩信息|-|
|2|StudentScoreList, 数学成绩信息|-|
|3|StudentScoreList, 外语成绩信息|-|
|4|StudentScoreList, 物理成绩信息|-|
|5|StudentScoreList, 化学成绩信息|-|
|6|StudentScoreList, 生物成绩信息|-|
|7|StudentScoreList, 政治成绩信息|-|
|8|StudentScoreList, 历史成绩信息|-|
|9|StudentScoreList, 地理成绩信息|-|
|255|StudentScoreList, 总分成绩信息|-|

StudentScoreInfoList：
|Index|Value|Description|
|  ----  | ----  | ---- |
|0|Double, 该科目成绩|-|
|1|Int, 该科目班级排名|-|
|2|Int, 该科目年级排名|-|

### GET `/data/by_person/<int:student_id>/exam`
查询该学生的有效考试（参加全部科目的考试）
Input:
- <int:student_id>：欲查询的学生id

Output:
HTTP 状态码始终为200，应根据返回的JSON判断：

ret:    
|Item|Value|Description|
|  ----  | ----  | ---- |
|code|int，API状态码|若student_id不存在，或该学生没有一次有效考试，则为404；若查询成功，则为200|
|msg|String，（错误）信息|-|
|data|dict/Object，查询的数据|详见下|

data：
|Item|Value|Description|
|  ----  | ----  | ---- |
|exams|List，有效考试的id|-|

### GET `/data/by_person/<int:student_id>/exam_detail`
查询该学生的有效考试（参加全部科目的考试）
Input:
- <int:student_id>：欲查询的学生id

Output:
HTTP 状态码始终为200，应根据返回的JSON判断：

ret:    
|Item|Value|Description|
|  ----  | ----  | ---- |
|code|int，API状态码|若student_id不存在，或该学生没有一次考试，则为404；若查询成功，则为200|
|msg|String，（错误）信息|-|
|data|dict/Object，查询的数据|详见下|

data：
|Item|Value|Description|
|  ----  | ----  | ---- |
|examDetails|dict/Object，每个元素的键为考试id，值为ScoresBySubject|ScoresBySubject详见上|
