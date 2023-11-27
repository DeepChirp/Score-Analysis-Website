# Backend Daemon V0.2.0

- Change API to V0.2.0
- Fix some bugs in scores API implementation (in V0.1.1).

# API V0.2.0

## V0.2.0改动
- analysis中新增classAvgScore、classAvgStd、classAvgRank

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
|scores|ScoresList(List)，查询的成绩数据|其中每个元素为StudentScoreInfoList(List)详见下|

ScoresList:
当学生未选考该科目时，该科目成绩为0
|Index|Value|Description|
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

StudentScoreInfoList：
当学生未选考该科目时，该科目成绩为0
|Index|Value|Description|
|  ----  | ----  | ---- |
|0|Double, 该科目成绩|-|
|1|Int, 该科目班级排名|-|
|2|Int, 该科目年级排名|-|