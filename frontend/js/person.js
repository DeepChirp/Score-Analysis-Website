class PersonPage {
    constructor() {
        this.examData = null;
        this.semesterIdToName = {};
        this.examInfoBySemester = {};
        this.classListByExamId = {};
        this.studentListByClassIdByExamId = {};
        this.studentNameToId = {};
        this.validExamList = [];
        this.examDetailByPerson = {};
        this.examIdToName = {};
    }
    async doGetExamInfo() {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/basic_info/exam`);
        let data = await response.json();
        return data;
    }
    async doGetClassListByExamId(examId) {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/basic_info/class/${examId}`);
        let data = await response.json();
        if (data["code"] == 200) {
            return data["data"]["classes"];
        }
        else {
            // TODO: Show error message if request failed?
        }
    }
    getExamInfo() {
        this.doGetExamInfo().then((data) => {
            if (data["code"] === 200) {
                this.examData = data["data"];


                this.examInfoBySemester = this.examData["exams"];
                for (const [semesterId, examInfoListOfSemester] of Object.entries(this.examInfoBySemester)) {
                    if (examInfoListOfSemester.length > 0) {
                        let thisId = examInfoListOfSemester[0]["semesterId"];
                        let thisName = examInfoListOfSemester[0]["semesterName"];
                        this.semesterIdToName[thisId] = thisName;
                    }
                }

                for (const [semesterId, examList] of Object.entries(this.examData["exams"])) {
                    let semesterName = this.semesterIdToName[semesterId]
                    for (const exam of examList) {
                        this.examIdToName[exam["examId"]] = `${semesterName}${exam["examName"]}`;
                    }
                }

                const gradeSelection = document.querySelector("#grade-selection");
                while (gradeSelection.firstChild) {
                    gradeSelection.removeChild(gradeSelection.firstChild);
                }

                for (const [semesterId, semesterName] of Object.entries(this.semesterIdToName)) {
                    const optionChild = document.createElement("option");
                    optionChild.value = semesterId;
                    optionChild.textContent = semesterName;
                    gradeSelection.appendChild(optionChild);
                }

                this.updateExamList(gradeSelection.value);
                const examSelection = document.querySelector("#exam-selection");
                this.updateClassList(examSelection.value);
            } else {
                // TODO: Show error message if request failed?
            }

        });
    }
    async doGetPersonData(studentId, examId) {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/data/by_person/${studentId}/exam/${examId}`);
        let data = await response.json();
        const studentSelection = document.querySelector("#student-selection");
        await this.updateValidExamList(this.studentNameToId[studentSelection.value]);
        return data;
    }
    updateExamList(semesterId) {
        const examSelection = document.querySelector("#exam-selection");
        while (examSelection.firstChild) {
            examSelection.removeChild(examSelection.firstChild);
        }
        let temp = this.examInfoBySemester[semesterId];
        for (const examInfoOfSemester of temp) {
            const optionChild = document.createElement("option");
            optionChild.value = examInfoOfSemester["examId"];
            optionChild.textContent = examInfoOfSemester["examName"];
            examSelection.appendChild(optionChild);
        }
    }
    updateClassList(examId) {
        const classSelection = document.querySelector("#class-selection");
        const examSelection = document.querySelector("#exam-selection");
        if (examId in this.classListByExamId) {
            while (classSelection.firstChild) {
                classSelection.removeChild(classSelection.firstChild);
            }
            for (const classId of this.classListByExamId[examId]) {
                const optionChild = document.createElement("option");
                optionChild.value = classId;
                optionChild.textContent = classId;
                classSelection.appendChild(optionChild);
            }
        }
        else {
            while (classSelection.firstChild) {
                classSelection.removeChild(classSelection.firstChild);
            }
            const loadingChild = document.createElement("option");
            loadingChild.textContent = "Loading...";
            classSelection.appendChild(loadingChild);
            this.doGetClassListByExamId(examId).then((classList) => {
                while (classSelection.firstChild) {
                    classSelection.removeChild(classSelection.firstChild);
                }
                this.classListByExamId[examId] = classList;
                for (const classId of this.classListByExamId[examId]) {
                    const optionChild = document.createElement("option");
                    optionChild.value = classId;
                    optionChild.textContent = classId;
                    classSelection.appendChild(optionChild);
                }
                this.updateStudentList(classSelection.value, examSelection.value);
            });
        }
    }
    async doGetClassInfo(classId, examId) {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/data/by_class/${classId}/exam/${examId}`);
        let data = await response.json();
        return data;
    }
    updateStudentList(classId, examId) {
        const studentSelectionData = document.querySelector("#student-list");
        if (examId in this.studentListByClassIdByExamId) {
            let studentListByClassId = this.studentListByClassIdByExamId[examId];
            if (classId in studentListByClassId) {
                while (studentSelectionData.firstChild) {
                    studentSelectionData.removeChild(studentSelectionData.firstChild);
                }
                for (const studentName of this.studentListByClassIdByExamId[examId][classId]) {
                    const optionChild = document.createElement("option");
                    optionChild.value = studentName;
                    optionChild.textContent = studentName;
                    studentSelectionData.appendChild(optionChild);
                }
            } else {
                this.doGetClassInfo(classId, examId).then((data) => {
                    if (data["code"] === 200) {
                        this.studentListByClassIdByExamId[examId][classId] = [];
                        for (const scoreObject of data["data"]["scores"]) {
                            this.studentListByClassIdByExamId[examId][classId].push(scoreObject["name"]);
                            this.studentNameToId[scoreObject["name"]] = scoreObject["id"];
                        }
                        while (studentSelectionData.firstChild) {
                            studentSelectionData.removeChild(studentSelectionData.firstChild);
                        }
                        for (const studentName of this.studentListByClassIdByExamId[examId][classId]) {
                            const optionChild = document.createElement("option");
                            optionChild.value = studentName;
                            optionChild.textContent = studentName;
                            studentSelectionData.appendChild(optionChild);
                        }
                    } else {
                        // TODO: Show error message if request failed?
                    }
                });
            }
        } else {
            this.doGetClassInfo(classId, examId).then((data) => {
                if (data["code"] === 200) {
                    this.studentListByClassIdByExamId[examId] = {};
                    this.studentListByClassIdByExamId[examId][classId] = [];
                    for (const scoreObject of data["data"]["scores"]) {
                        this.studentListByClassIdByExamId[examId][classId].push(scoreObject["name"]);
                        this.studentNameToId[scoreObject["name"]] = scoreObject["id"];
                    }
                    while (studentSelectionData.firstChild) {
                        studentSelectionData.removeChild(studentSelectionData.firstChild);
                    }
                    for (const studentName of this.studentListByClassIdByExamId[examId][classId]) {
                        const optionChild = document.createElement("option");
                        optionChild.value = studentName;
                        optionChild.textContent = studentName;
                        studentSelectionData.appendChild(optionChild);
                    }
                } else {
                    // TODO: Show error message if request failed?
                }
            });
        }
    }
    updateStudentScoreTable(studentId, examId) {
        this.doGetPersonData(studentId, examId).then((data) => {
            if (data["code"] === 200) {
                const scoreTbody = document.querySelector(".student-score-table tbody");
                while (scoreTbody.firstChild) {
                    scoreTbody.removeChild(scoreTbody.firstChild);
                }
                let scoresList = data["data"]["scores"];
                let lastExamId = this.getLastValidExamId(examId);

                const chartSelectDiv = document.querySelector("#student-score-chart-select-div");

                // Show the chart select div
                document.getElementById('student-score-chart-container').style.display = 'block';

                while (chartSelectDiv.firstChild) {
                    chartSelectDiv.removeChild(chartSelectDiv.firstChild);
                }

                for (const [subjectId, subjectName] of Object.entries(subjectIdToName)) {
                    if (subjectId in scoresList) {
                        const thisBtn = document.createElement("button");
                        thisBtn.textContent = subjectName;
                        thisBtn.classList.add("subject-button");
                        thisBtn.addEventListener("click", () => {
                            this.drawChart(subjectId);
                        });
                        chartSelectDiv.appendChild(thisBtn);

                        let score = scoresList[subjectId][0];
                        let classRank = scoresList[subjectId][1];
                        let gradeRank = scoresList[subjectId][2];
                        const thisTr = document.createElement("tr");
                        const subjectNameTd = document.createElement("td");
                        subjectNameTd.textContent = subjectName;
                        thisTr.appendChild(subjectNameTd);
                        const scoreTd = document.createElement("td");
                        scoreTd.textContent = score;
                        thisTr.appendChild(scoreTd);
                        const classRankTd = document.createElement("td");
                        const gradeRankTd = document.createElement("td");
                        if (lastExamId != -1) {
                            let lastClassRank = this.examDetailByPerson[lastExamId][subjectId][1];
                            let lastGradeRank = this.examDetailByPerson[lastExamId][subjectId][2];
                            let deltaClassRank = lastClassRank - classRank;
                            let deltaGradeRank = lastGradeRank - gradeRank;
                            classRankTd.innerHTML = `${classRank} <span style="color: ${deltaClassRank < 0 ? 'red' : 'green'}">(${deltaClassRank >= 0 ? '+' : ''}${deltaClassRank})</span>`;
                            gradeRankTd.innerHTML = `${gradeRank} <span style="color: ${deltaGradeRank < 0 ? 'red' : 'green'}">(${deltaGradeRank >= 0 ? '+' : ''}${deltaGradeRank})</span>`;
                        }
                        else {
                            classRankTd.textContent = classRank;
                            gradeRankTd.textContent = gradeRank;
                        }
                        thisTr.appendChild(classRankTd);
                        thisTr.appendChild(gradeRankTd);
                        scoreTbody.appendChild(thisTr);
                    }
                }

                // Add selected class to the selected button
                var buttons = document.querySelectorAll('.subject-button');
                buttons.forEach(function (button) {
                    button.addEventListener('click', function () {
                        buttons.forEach(function (btn) {
                            btn.classList.remove('selected');
                        });
                        button.classList.add('selected');
                    });
                });
            } else {
                // TODO: Show error message if request failed?
            }
        });
    }
    async doGetExamListByPerson(studentId) {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/data/by_person/${studentId}/exam`);
        let data = await response.json();
        return data;
    }
    async updateValidExamList(studentId) {
        let data = await this.doGetExamListByPerson(studentId);
        if (data["code"] === 200) {
            this.validExamList = data["data"]["exams"];
        } else {
            // TODO: Show error message if request failed?
        }
    }
    getLastValidExamId(examId) {

        if (this.validExamList.length > 0) {
            let temp = -1;
            for (const id of this.validExamList) {
                if (id < examId) {
                    temp = id;
                } else {
                    break;
                }
            }
            return temp;
        } else {
            return -1;
        }
    }

    async doGetExamDetailByPerson(studentId) {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/data/by_person/${studentId}/exam_detail`);
        let data = await response.json();
        return data;
    }

    async getExamDetailByPerson(studentId) {
        let data = await this.doGetExamDetailByPerson(studentId);
        if (data["code"] === 200) {
            this.examDetailByPerson = data["data"]["examDetails"];
        } else {
            // TODO: Show error message if request failed?
        }

    }

    drawChart(subjectId) {
        const chartDiv = document.querySelector("#student-score-chart-div");
        while (chartDiv.firstChild) {
            chartDiv.removeChild(chartDiv.firstChild);
        }
        let subjectName = subjectIdToName[subjectId];

        let show = 0;
        const thisDiv = document.createElement("div");
        thisDiv.setAttribute("class", "subject-group-div");
        thisDiv.style.display = "flex";
        const scoreCanvas = document.createElement("canvas");
        const rankCanvas = document.createElement("canvas");

        const scoreContainer = document.createElement("div");
        scoreContainer.setAttribute("class", "chart-container");
        scoreContainer.style.flex = 1;
        const rankContainer = document.createElement("div");
        rankContainer.setAttribute("class", "chart-container");
        rankContainer.style.flex = 1;

        let labels = [];
        let scores = [];
        let gradeRanks = [];
        for (const [examId, examDetail] of Object.entries(this.examDetailByPerson)) {
            if (subjectId in examDetail) {
                show = 1;
                labels.push(this.examIdToName[examId]);
                scores.push(examDetail[subjectId][0]);
                gradeRanks.push(examDetail[subjectId][2]);
            }

        }


        new Chart(scoreCanvas, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "分数",
                        data: scores,
                        borderColor: "#007bff",
                        fill: false
                    }
                ]
            }
        }
        );

        new Chart(rankCanvas, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "年级排名",
                        data: gradeRanks,
                        borderColor: "#007bff",
                        fill: false
                    }
                ]
            },
            options: {
                scales: {
                    y: {
                        reverse: true
                    }
                }
            }
        }
        );

        scoreContainer.appendChild(scoreCanvas);
        rankContainer.appendChild(rankCanvas);
        thisDiv.appendChild(scoreContainer);
        thisDiv.appendChild(rankContainer);
        if (show) {
            chartDiv.appendChild(thisDiv);
        }
    }

    initEventListeners() {
        this.getExamInfo();
        const studentSelection = document.querySelector("#student-selection");
        studentSelection.addEventListener("input", (event) => {
            if (event.target.value.trim() != "") {
                const submitButton = document.querySelector("#student-submit");
                submitButton.disabled = false;
            }
        });

        const classSelection = document.querySelector("#class-selection");
        classSelection.addEventListener("change", (event) => {
            this.updateStudentList(event.target.value, examSelection.value);
        });

        const submitButton = document.querySelector("#student-submit");
        submitButton.addEventListener("click", () => {
            submitButton.disabled = true;
            submitButton.textContent = "Loading...";

            this.updateValidExamList(this.studentNameToId[studentSelection.value]).then(() => {
                this.getExamDetailByPerson(this.studentNameToId[studentSelection.value]).then(() => {
                    this.updateStudentScoreTable(this.studentNameToId[studentSelection.value], examSelection.value);
                    this.drawChart(1);
                    submitButton.disabled = false;
                    submitButton.textContent = "查询";
                });
            });
        });

        const gradeSelection = document.querySelector("#grade-selection");
        gradeSelection.addEventListener("change", (event) => {
            const classSelectionPreviousIndex = classSelection.selectedIndex;
            this.updateExamList(event.target.value);
            classSelection.selectedIndex = classSelectionPreviousIndex;

        });

        const examSelection = document.querySelector("#exam-selection");
        examSelection.addEventListener("change", (event) => {
            const classSelectionPreviousIndex = classSelection.selectedIndex;
            this.updateClassList(event.target.value);
            setTimeout(() => {
                classSelection.selectedIndex = classSelectionPreviousIndex;
            }, 50);


        });


    }
}

// Create the instance manually when user directly open person page.
if (!("personPage" in window)) {
    window["personPage"] = new PersonPage();
    window.personPage.initEventListeners();
}