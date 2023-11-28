
let examData = null;

let semesterIdToName = {};
let examInfoBySemester = {};
let classListByExamId = {};
let studentListByClassIdByExamId = {};
let studentNameToId = {};
let validExamList = [];

async function doGetExamInfo() {
    let response = await fetch(`${protocolPrefix}${host}/api/scores/basic_info/exam`);
    let data = await response.json();
    if (data["code"] == 200) {
        return data["data"];
    }
    else {
        // TODO: Show error message if request failed?
    }
}

async function doGetClassListByExamId(examId) {
    let response = await fetch(`${protocolPrefix}${host}/api/scores/basic_info/class/${examId}`);
    let data = await response.json();
    if (data["code"] == 200) {
        return data["data"]["classes"];
    }
    else {
        // TODO: Show error message if request failed?
    }
}

function getExamInfo() {
    doGetExamInfo().then((data) => {
        examData = data;
        examInfoBySemester = data["exams"];
        for (const [semesterId, examInfoListOfSemester] of Object.entries(examInfoBySemester)) {
            if (examInfoListOfSemester.length > 0) {
                thisId = examInfoListOfSemester[0]["semesterId"]
                thisName = examInfoListOfSemester[0]["semesterName"];
                semesterIdToName[thisId] = thisName;
            }
        }

        const gradeSelection = document.querySelector("#grade-selection");
        while (gradeSelection.firstChild) {
            gradeSelection.removeChild(gradeSelection.firstChild);
        }

        for (const [semesterId, semesterName] of Object.entries(semesterIdToName)) {
            const optionChild = document.createElement("option");
            optionChild.value = semesterId;
            optionChild.textContent = semesterName;
            gradeSelection.appendChild(optionChild);
        }

        updateExamList(gradeSelection.value);
        const examSelection = document.querySelector("#exam-selection");
        updateClassList(examSelection.value);

    });
}

async function doGetPersonData(studentId, examId) {
    let response = await fetch(`${protocolPrefix}${host}/api/scores/data/by_person/${studentId}/exam/${examId}`);
    let data = await response.json();
    const studentSelection = document.querySelector("#student-selection");
    await updateValidExamList(studentNameToId[studentSelection.value]);
    return data;
}

function updateExamList(semesterId) {
    const examSelection = document.querySelector("#exam-selection");
    while (examSelection.firstChild) {
        examSelection.removeChild(examSelection.firstChild);
    }
    let temp = examInfoBySemester[semesterId]
    for (const examInfoOfSemester of temp) {
        const optionChild = document.createElement("option");
        optionChild.value = examInfoOfSemester["examId"];
        optionChild.textContent = examInfoOfSemester["examName"];
        examSelection.appendChild(optionChild);
    }
}

function updateClassList(examId) {
    const classSelection = document.querySelector("#class-selection");
    if (examId in classListByExamId) {
        while (classSelection.firstChild) {
            classSelection.removeChild(classSelection.firstChild);
        }
        for (const classId of classListByExamId[examId]) {
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
        doGetClassListByExamId(examId).then((classList) => {
            while (classSelection.firstChild) {
                classSelection.removeChild(classSelection.firstChild);
            }
            classListByExamId[examId] = classList;
            for (const classId of classListByExamId[examId]) {
                const optionChild = document.createElement("option");
                optionChild.value = classId;
                optionChild.textContent = classId;
                classSelection.appendChild(optionChild);
            }
            updateStudentList(classSelection.value, examSelection.value);
        });
    }
}

async function doGetClassInfo(classId, examId) {
    let response = await fetch(`${protocolPrefix}${host}/api/scores/data/by_class/${classId}/exam/${examId}`);
    let data = await response.json();
    return data;
}

function updateStudentList(classId, examId) {
    const studentSelectionData = document.querySelector("#student-list");
    if (examId in studentListByClassIdByExamId) {
        studentListByClassId = studentListByClassIdByExamId[examId];
        if (classId in studentListByClassId) {
            while (studentSelectionData.firstChild) {
                studentSelectionData.removeChild(studentSelectionData.firstChild);
            }
            for (const studentName of studentListByClassIdByExamId[examId][classId]) {
                const optionChild = document.createElement("option");
                optionChild.value = studentName;
                optionChild.textContent = studentName;
                studentSelectionData.appendChild(optionChild);
            }
        } else {
            doGetClassInfo(classId, examId).then((data) => {
                if (data["code"] === 200) {
                    studentListByClassIdByExamId[examId][classId] = [];
                    for (const scoreObject of data["data"]["scores"]) {
                        studentListByClassIdByExamId[examId][classId].push(scoreObject["name"]);
                        studentNameToId[scoreObject["name"]] = scoreObject["id"];
                    }
                    while (studentSelectionData.firstChild) {
                        studentSelectionData.removeChild(studentSelectionData.firstChild);
                    }
                    for (const studentName of studentListByClassIdByExamId[examId][classId]) {
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
        doGetClassInfo(classId, examId).then((data) => {
            if (data["code"] === 200) {
                studentListByClassIdByExamId[examId] = {};
                studentListByClassIdByExamId[examId][classId] = [];
                for (const scoreObject of data["data"]["scores"]) {
                    studentListByClassIdByExamId[examId][classId].push(scoreObject["name"]);
                    studentNameToId[scoreObject["name"]] = scoreObject["id"];
                }
                while (studentSelectionData.firstChild) {
                    studentSelectionData.removeChild(studentSelectionData.firstChild);
                }
                for (const studentName of studentListByClassIdByExamId[examId][classId]) {
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

function updateStudentScoreTable(studentId, examId) {
    doGetPersonData(studentId, examId).then((data) => {
        if (data["code"] === 200) {
            const scoreTbody = document.querySelector(".student-score-table tbody");
            while (scoreTbody.firstChild) {
                scoreTbody.removeChild(scoreTbody.firstChild);
            }
            scoresList = data["data"]["scores"];
            lastExamId = getLastValidExamId(examId);

            // TODO: get rank from last exam

            for (const [subjectId, subjectName] of Object.entries(subjectIdToName)) {
                if (subjectId in scoresList)
                {
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

async function doGetExamListByPerson(studentId) {
    let response = await fetch(`${protocolPrefix}${host}/api/scores/data/by_person/${studentId}/exam`);
    let data = await response.json();
    return data;
}

async function updateValidExamList(studentId) {
    data = await doGetExamListByPerson(studentId);
    if (data["code"] === 200) {
        validExamList = data["data"]["exams"];
    } else {
        // TODO: Show error message if request failed?
    }

}

function getLastValidExamId(examId) {
    if (validExamList.length > 0) {
        let temp = -1;
        for (const id of validExamList) {
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

getExamInfo();

const studentSelection = document.querySelector("#student-selection");
studentSelection.addEventListener("input", (event) => {
    if (event.target.value.trim() != "") {
        const submitButton = document.querySelector("#student-submit");
        submitButton.disabled = false;
    }
});

const submitButton = document.querySelector("#student-submit");
submitButton.addEventListener("click", () => {
    updateStudentScoreTable(studentNameToId[studentSelection.value], examSelection.value);
})

const gradeSelection = document.querySelector("#grade-selection");
gradeSelection.addEventListener("change", (event) => {
    studentSelection.value = "";
    submitButton.disabled = true;
    updateExamList(event.target.value);
});

const examSelection = document.querySelector("#exam-selection");
examSelection.addEventListener("change", (event) => {
    studentSelection.value = "";
    submitButton.disabled = true;
    updateClassList(event.target.value);
});

const classSelection = document.querySelector("#class-selection");
classSelection.addEventListener("change", (event) => {
    studentSelection.value = "";
    submitButton.disabled = true;
    updateStudentList(event.target.value, examSelection.value);
});



