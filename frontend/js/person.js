var PersonPage = function () {
    this.examData = null;
    this.semesterIdToName = {};
    this.examInfoBySemester = {};
    this.classListByExamId = {};
    this.studentListByClassIdByExamId = {};
    this.studentNameToId = {};
    this.validExamList = [];
};

PersonPage.prototype.doGetExamInfo = async function () {
    let response = await fetch(`${protocolPrefix}${host}/api/scores/basic_info/exam`);
    let data = await response.json();
    if (data["code"] == 200) {
        return data["data"];
    }
    else {
        // TODO: Show error message if request failed?
    }
};

PersonPage.prototype.doGetClassListByExamId = async function (examId) {
    let response = await fetch(`${protocolPrefix}${host}/api/scores/basic_info/class/${examId}`);
    let data = await response.json();
    if (data["code"] == 200) {
        return data["data"]["classes"];
    }
    else {
        // TODO: Show error message if request failed?
    }
};

PersonPage.prototype.getExamInfo = function () {
    this.doGetExamInfo().then((data) => {
        this.examData = data;
        this.examInfoBySemester = data["exams"];
        for (const [semesterId, examInfoListOfSemester] of Object.entries(this.examInfoBySemester)) {
            if (examInfoListOfSemester.length > 0) {
                let thisId = examInfoListOfSemester[0]["semesterId"]
                let thisName = examInfoListOfSemester[0]["semesterName"];
                this.semesterIdToName[thisId] = thisName;
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

    });
};

PersonPage.prototype.doGetPersonData = async function (studentId, examId) {
    let response = await fetch(`${protocolPrefix}${host}/api/scores/data/by_person/${studentId}/exam/${examId}`);
    let data = await response.json();
    const studentSelection = document.querySelector("#student-selection");
    await this.updateValidExamList(this.studentNameToId[studentSelection.value]);
    return data;
}

PersonPage.prototype.updateExamList = function (semesterId) {
    const examSelection = document.querySelector("#exam-selection");
    while (examSelection.firstChild) {
        examSelection.removeChild(examSelection.firstChild);
    }
    let temp = this.examInfoBySemester[semesterId]
    for (const examInfoOfSemester of temp) {
        const optionChild = document.createElement("option");
        optionChild.value = examInfoOfSemester["examId"];
        optionChild.textContent = examInfoOfSemester["examName"];
        examSelection.appendChild(optionChild);
    }
}

PersonPage.prototype.updateClassList = function (examId) {
    const classSelection = document.querySelector("#class-selection");
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

PersonPage.prototype.doGetClassInfo = async function (classId, examId) {
    let response = await fetch(`${protocolPrefix}${host}/api/scores/data/by_class/${classId}/exam/${examId}`);
    let data = await response.json();
    return data;
}

PersonPage.prototype.updateStudentList = function (classId, examId) {
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

PersonPage.prototype.updateStudentScoreTable = function (studentId, examId) {
    this.doGetPersonData(studentId, examId).then((data) => {
        if (data["code"] === 200) {
            const scoreTbody = document.querySelector(".student-score-table tbody");
            while (scoreTbody.firstChild) {
                scoreTbody.removeChild(scoreTbody.firstChild);
            }
            let scoresList = data["data"]["scores"];
            let lastExamId = this.getLastValidExamId(examId);

            // TODO: get rank from last exam

            for (const [subjectId, subjectName] of Object.entries(this.subjectIdToName)) {
                if (subjectId in scoresList) {
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
                    classRankTd.textContent = classRank;
                    thisTr.appendChild(classRankTd);
                    const gradeRankTd = document.createElement("td");
                    gradeRankTd.textContent = gradeRank;
                    thisTr.appendChild(gradeRankTd);
                    scoreTbody.appendChild(thisTr);
                }
            }
        } else {
            // TODO: Show error message if request failed?
        }
    });
}

PersonPage.prototype.doGetExamListByPerson = async function (studentId) {
    let response = await fetch(`${protocolPrefix}${host}/api/scores/data/by_person/${studentId}/exam`);
    let data = await response.json();
    return data;
}

PersonPage.prototype.updateValidExamList = async function (studentId) {
    let data = await this.doGetExamListByPerson(studentId);
    if (data["code"] === 200) {
        this.validExamList = data["data"]["exams"];
    } else {
        // TODO: Show error message if request failed?
    }
}

PersonPage.prototype.getLastValidExamId = function (examId) {
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

PersonPage.prototype.getExamInfo();

PersonPage.prototype.initEventListeners = function () {
    const studentSelection = document.querySelector("#student-selection");
    studentSelection.addEventListener("input", (event) => {
        if (event.target.value.trim() != "") {
            const submitButton = document.querySelector("#student-submit");
            submitButton.disabled = false;
        }
    });

    const submitButton = document.querySelector("#student-submit");
    submitButton.addEventListener("click", () => {
        this.updateStudentScoreTable(this.studentNameToId[studentSelection.value], examSelection.value);
    })

    const gradeSelection = document.querySelector("#grade-selection");
    gradeSelection.addEventListener("change", (event) => {
        studentSelection.value = "";
        submitButton.disabled = true;
        this.updateExamList(event.target.value);
    });

    const examSelection = document.querySelector("#exam-selection");
    examSelection.addEventListener("change", (event) => {
        studentSelection.value = "";
        submitButton.disabled = true;
        this.updateClassList(event.target.value);
    });

    const classSelection = document.querySelector("#class-selection");
    classSelection.addEventListener("change", (event) => {
        studentSelection.value = "";
        submitButton.disabled = true;
        this.updateStudentList(event.target.value, examSelection.value);
    });
}