class DataPage {
    constructor () {
        this.uniqueIdLst = [];
        this.examInfoBySemester = {};
        this.examData = {};
        this.semesterIdToName = {};
        this.examIdToName = {};
    }

    async doGetExamInfo() {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/basic_info/exam`);
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
        const downloadBtn = document.querySelector("#download-submit");
        downloadBtn.disabled = false;
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
            } else {
                // TODO: Show error message if request failed?
            }

        });
    }

    async doTriggerCsvLoad(uniqueId) {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/data/loadcsv/${uniqueId}`);
        let data = await response.json();
        return data;
    }

    async loadCsv() {
        let loadedCount = 0;
        for (const uniqueId of this.uniqueIdLst) {
            const data = await this.doTriggerCsvLoad(uniqueId);
            if (data["code"] === 200) {
                loadedCount ++;
            } else {
                // TODO: Show error message if request failed?
            }
        }
        const resultDiv = document.querySelector(".file-uploader-result");
        resultDiv.hidden = false;
        setTimeout(() => {
            location.reload();
        }, 3000);
    }

    async doDownloadData(exam_id) {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/data/downloadcsv/${exam_id}`);
        return response.text();
    }

    async doGetSavedName(exam_id) {
        let response = await fetch(`${protocolPrefix}${host}/api/scores/basic_info/saved_name/${exam_id}`);
        let data = await response.json();
        return data;
    }

    async downloadData(exam_id) {
        let data = await this.doDownloadData(exam_id);
        let savedNameData = await this.doGetSavedName(exam_id);
        if (savedNameData["code"] === 200) {
            let savedName = savedNameData["data"]["savedName"];
            download(data, `${exam_id}${savedName}.csv`, "text/csv");
        }
        else {
            // TODO: Show error message if request failed?
        }
        
    }

    initEventListeners() {
        this.getExamInfo();
        FilePond.registerPlugin(FilePondPluginFileValidateSize);
        const fileUploader = document.querySelector("#file-uploader");
        const loadBtn = document.querySelector("#load-data-btn");
        loadBtn.addEventListener("click", () => {
            this.loadCsv();
        });
        const pond = FilePond.create(fileUploader);
        pond.allowMultiple = true;
        pond.chunkUploads = false;
        pond.allowRevert = false;
        pond.maxFileSize = "1MB";
        pond.setOptions({
            server: {
                process: {
                    url: '/api/scores/data/upload',
                    onload: (uniqueId) => {
                        this.uniqueIdLst.push(uniqueId);
                        const countSpan = document.querySelector(".file-uploader-counts");
                        countSpan.textContent = this.uniqueIdLst.length;
                        loadBtn.disabled = false;
                    }
                },
                revert: null,
                fetch: null
            }
        });
        const gradeSelection = document.querySelector("#grade-selection");
        gradeSelection.addEventListener("change", (event) => {
            this.updateExamList(event.target.value);
        });
        const downloadBtn = document.querySelector("#download-submit");
        downloadBtn.addEventListener("click", () => {
            downloadBtn.disabled = true;
            downloadBtn.textContent = "Loading...";
            const examSelection = document.querySelector("#exam-selection");
            this.downloadData(examSelection.value).then(() => {
                downloadBtn.textContent = "下载";
                downloadBtn.disabled = false;
            });
            
        });
    }
}

// Create the instance manually when user directly open person page.
if (!("dataPage" in window)) {
    window["dataPage"] = new DataPage();
    window.dataPage.initEventListeners();
}