class ClassPage {
    constructor () {
        this.examData = {};
        this.examIdToName = {};
        this.examInfoBySemester = {};
        this.semesterIdToName = {};
        this.semesterIdToName = {};
        this.classListByExamId = {};
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

    async doGetClassAnalysis(examId, classId) {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/analysis/by_class/${classId}/exam/${examId}`);
        let data = await response.json();
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
            });
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

    getClassAnalysis(examId, classId) {
        this.doGetClassAnalysis(examId, classId).then((data) => {
            if (data["code"] === 200) {

            }
            else {
                // TODO: Show error message if request failed?
            }
        });
    }


    initEventListeners() {
        this.getExamInfo();

        const classSelection = document.querySelector("#class-selection");

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

if (!("classPage" in window)) {
    window["classPage"] = new ClassPage();
    window.classPage.initEventListeners();
}
