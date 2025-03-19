var questions = [];
var currentQuestionIndex = 0;
var userAnswers = {};

document.addEventListener("DOMContentLoaded", function () {
    let selectElement = document.getElementById("quiz_chap_name");
    let inputElement = document.getElementById("quiz_chap_id");

    if (selectElement && inputElement) {
        selectElement.addEventListener("change", function () {
            let selectOption = selectElement.options[selectElement.selectedIndex];
            inputElement.value = selectOption.value;
        });
    }

    if (document.getElementById("user_start_quiz")) {
        totalTime = parseInt(document.getElementById("time").textContent) * 60;
        loadQuestions();
        showQuestions();
        if (questions.length != 0) {
            startTimer();
        }
    }

    let popupoverlay = document.querySelector(".popup-overlay");
    let popupbox = document.querySelector(".popup-box");
    let submit = document.getElementById("Submit");
    let cancel = document.getElementById("Cancel");

    if (submit && cancel) {
        submit.addEventListener("click", function () {
            popupoverlay.style.display = "block";
            popupbox.style.display = "block";
        })
        cancel.addEventListener("click", function (event) {
            event.preventDefault();
            popupoverlay.style.display = "none";
            popupbox.style.display = "none";

        })
    }

    // Handle Admin Chart Data
    let chartData = document.getElementById("chartData");

    if (chartData) {
        console.log("admin chart found");
        console.log("Raw dataset values:", chartData.dataset);
        try {
            let barXSubjects = JSON.parse(chartData.dataset.barXSubjects || "[]");
            let barYScores = JSON.parse(chartData.dataset.barYScores || "[]");
            let barColors = JSON.parse(chartData.dataset.barColors || "[]");

            let pieXSubjects = JSON.parse(chartData.dataset.pieXSubjects || "[]");
            let pieYScores = JSON.parse(chartData.dataset.pieYScores || "[]");
            let pieColors = JSON.parse(chartData.dataset.pieColors || "[]");



            new Chart("barChart", {
                type: "bar",
                data: {
                    labels: barXSubjects,
                    datasets: [{
                        backgroundColor: barColors,
                        data: barYScores
                    }]
                },
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: "Subject wise top scores"
                        }, legend: { display: false }
                    },
                    responsive: true,
                    maintainAspectRatio: false
                }
            });


            new Chart("pieChart", {
                type: "doughnut",
                data: {
                    labels: pieXSubjects,
                    datasets: [{
                        backgroundColor: pieColors,
                        data: pieYScores
                    }]
                },

                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: "Subject wise user attempts"
                        },
                        legend: { display: false }
                    }, 
                    responsive: true, 
                    maintainAspectRatio: false
                }
            });
        } catch (error) {
            console.error("Error parsing Admin ChartData:", error);
        }
    } else {
        console.warn("Admin chartData not found. Skipping admin charts.");
    }




    // Handle User Chart Data
    let User_ChartData = document.getElementById("UserChartData");

    if (User_ChartData) {
        console.log("User ChartData found");
        console.log("Raw dataset values:", User_ChartData.dataset);

        try {
            let user_barXSubjects = JSON.parse(User_ChartData.dataset.barXSubjects || "[]");
            let user_barYScores = JSON.parse(User_ChartData.dataset.barYAttemps || "[]");
            let user_barColors = JSON.parse(User_ChartData.dataset.barColors || "[]");

            let user_pieXSubjects = JSON.parse(User_ChartData.dataset.pieXMonth || "[]");
            let user_pieYScores = JSON.parse(User_ChartData.dataset.pieYUserAtt || "[]");
            let user_pieColors = JSON.parse(User_ChartData.dataset.pieColors || "[]");

            new Chart("UserBarChart", {
                type: "bar",
                data: {
                    labels: user_barXSubjects,
                    datasets: [{
                        backgroundColor: user_barColors,
                        data: user_barYScores
                    }]
                },
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: "Subject wise no. of quizzes attempted"
                        }, legend: { display: false }
                    },

                    responsive: true,
                    maintainAspectRatio: false
                }
            });

            new Chart("UserPieChart", {
                type: "doughnut",
                data: {
                    labels: user_pieXSubjects,
                    datasets: [{
                        backgroundColor: user_pieColors,
                        data: user_pieYScores
                    }]
                },
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: "Month wise no. of quizzes attempted"
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false

                }
            });

        } catch (error) {
            console.error("Error parsing User ChartData:", error);

        }

    } else {
        console.warn("User chartData not found. Skipping user charts.");
    }




});

function loadQuestions() {
    document.querySelectorAll(".question-data").forEach(q => {
        questions.push({
            id: q.getAttribute("data-id"),
            text: q.getAttribute("data-question"),
            options: q.getAttribute("data-options").split(",")
        });
    });
}
function showQuestions() {
    if (questions.length === 0) {
        document.querySelector("table").innerHTML = "<h2>No Questions Available!</h2>";
        return;
    }

    if (currentQuestionIndex >= questions.length) {
        document.querySelector("table").innerHTML = "<h2>Quiz Finished!</h2>";
        return;
    }

    let question = questions[currentQuestionIndex];

    let questionNumber = document.getElementById("question_number");
    let questionStatement = document.getElementById("question_statement");
    let optionsContainer = document.getElementById("options_container");
    let selectedOption = document.getElementById("selected-option");


    if (!questionNumber || !questionStatement || !optionsContainer) return;
    questionNumber.textContent = currentQuestionIndex + 1;
    questionStatement.textContent = question.text;
    optionsContainer.innerHTML = "";


    question.options.forEach((option, index) => {
        let opt = document.createElement("input");

        opt.value = option;
        opt.name = `question_${question.id}`;
        opt.type = "radio";
        opt.id = `option_${question.id}_${index}`;




        if (userAnswers[question.id] === option) {
            opt.checked = true;
        }


        opt.addEventListener("change", () => {
            userAnswers[question.id] = option;
            selectedOption.textContent = option;
        });

        let label = document.createElement("label");
        label.htmlFor = opt.id;
        label.textContent = option;


        optionsContainer.appendChild(opt);
        optionsContainer.appendChild(label);
        optionsContainer.appendChild(document.createElement("br"));
    });
    selectedOption.textContent = userAnswers[question.id] || "None";
    selectedOption.setAttribute("name", question.id || "None");

}

function prevQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        showQuestions();
    }
}

function nextQuestion() {
    if (currentQuestionIndex < questions.length - 1) {
        currentQuestionIndex++;
        showQuestions();
    }
}

function startTimer() {
    let timerDisplay = document.getElementById("time");


    let countdown = setInterval(function () {
        if (totalTime <= 0) {
            clearInterval(countdown);
            document.querySelector("#quiz-container").innerHTML = "<h2>Time Over!</h2>";
            return;
        }



        let minutes = Math.floor(totalTime / 60);
        let seconds = totalTime % 60;
        timerDisplay.textContent = `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;

        totalTime--;
    }, 1000);
}


function submitQuiz(quiz_id) {

    fetch(`/userdb/user_start_quiz/${quiz_id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(userAnswers),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`)

            }
            return response.json();
        })
        .then(data => {
            console.log("Response from API:", data);
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        })
        .catch(error => console.error("Error submitting quiz:", error));
}

function Description(ID) {
    let element = document.querySelectorAll('.' + ID);

    element.forEach(element => {
        element.style.display = (element.style.display === "none" || element.style.display === "") ? "block" : "none";
    });


}

function search() {
    let query;
    let pageSource = document.getElementById("search").getAttribute("data-source")
    if (pageSource === "user-navbar.html") {
        query = document.getElementById("user-search").value;
    }
    else if (pageSource === "admin-navbar.html") {
        query = document.getElementById("admin-search").value;

    }

    if (query === "") {
        document.getElementById("results").innerHTML = "<p style='color:red;'>Please enter a search term.</p>";
        return;
    }

    fetch(`/search?q=${query}&source=${pageSource}`)
        .then(response => response.json())
        .then(data => {
            let resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = '';

            if (data.Users && data.Users.length > 0) {
                resultsDiv.innerHTML += "<h3>Users</h3>";
                data.Users.forEach(user => {
                    resultsDiv.innerHTML += `<p> Id: ${user.Id} - Username: ${user.Username} - Email: ${user.Email} - Qualification: ${user.Qualification} - Gender: ${user.Gender} - Date of Birth: ${user.Date_of_Birth}</p>`;
                });
            }

            if (data.Quizzes && data.Quizzes.length > 0) {
                resultsDiv.innerHTML += "<h3>Quizzes</h3>";
                data.Quizzes.forEach(quiz => {
                    resultsDiv.innerHTML += `<p> Quiz Id: ${quiz.Quiz_Id} - Quiz Title: ${quiz.Quiz_Title} - Quiz Chapter Id: ${quiz.Quiz_Chapter_Id} - Quiz Start Date: ${quiz.Quiz_Start_Date} - Quiz Duration: ${quiz.Quiz_Duration}</p>`;
                });
            }

            if (data.Subjects && data.Subjects.length > 0) {
                resultsDiv.innerHTML += "<h3>Subjects</h3>";
                data.Subjects.forEach(subject => {
                    resultsDiv.innerHTML += `<p> Subject Id: ${subject.Subject_Id} - Subject Name: ${subject.Subject_Name}</p>`;
                });
            }

            if (data.Chapters && data.Chapters.length > 0) {
                resultsDiv.innerHTML += "<h3>Chapters</h3>";
                data.Chapters.forEach(chapter => {
                    resultsDiv.innerHTML += `<p> Chapter Id: ${chapter.Chapter_Id} - Chapter Title: ${chapter.Chapter_Title}</p>`;
                });
            }
            if (data.Scores && data.Scores.length > 0) {
                resultsDiv.innerHTML += "<h3>Scores</h3>";
                data.Scores.forEach(score => {
                    resultsDiv.innerHTML += `<p> Scores Id: ${score.score_id} - Quiz_Id: ${score.quiz_score_id} -  Total Score: ${score.Total_Score}</p>`;
                });
            }
        })
        .catch(error => {
            console.error("Search error", error);
            document.getElementById("results").innerHTML = "<p style='color:red;'>Something went wrong. Try again.</p>";
        });
}
