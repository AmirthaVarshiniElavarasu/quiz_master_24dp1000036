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
    if(submit && cancel ){
    submit.addEventListener("click", function () {
        popupoverlay.style.display = "block";
        popupbox.style.display = "block";
    })
    cancel.addEventListener("click", function (event) {
        event.preventDefault();
        popupoverlay.style.display = "none";
        popupbox.style.display = "none";

    })}

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
        .catch (error => console.error("Error submitting quiz:", error));
}

function Description(ID) {
    let element = document.querySelectorAll('.' + ID);

    element.forEach(element => {
        element.style.display = (element.style.display === "none" || element.style.display === "") ? "block" : "none";
    });


}

function search(){
    let query = document.getElementById("searchInput").value.trim();

    if(query === ""){
        document.getElementById('results').innerHTML="<p style='color:red;'>Please enter a search term.</p>"
        return;
    }

    fetch(`/search?q=${query}`)
        .then(response => response.json())
        .then(data => {
            let resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML='';


            if (data.Users.length>0){
                resultsDiv.innerHTML+="<h3>Users</h3>";
                data.Users.forEach(user => {
                    resultsDiv.innerHTML += `<p> Id:${user.Id} - Username:${user.Username} - Email:${user.Email} - Qualification:${user.Qualification} - Gender:${user.Gender} - Date of Birth:${user.Date_of_Birth}</p>`
                });
            }

            if(data.Quizzes.length>0){
                resultsDiv.innerHTML+="<h3>Quzzies</h3>";
                data.Quizzes.forEach(quiz =>{
                    resultsDiv.innerHTML+= `<p> Quiz Id:${quiz.Quiz_Id} - Quiz Title:${quiz.Quiz_Title} - Quiz Chapter Id:${quiz.Quiz_Chapter_Id} - Quiz Start Date: ${quiz.Quiz_Start_Date} - Quiz_Duration:${quiz.Quiz_Duration}</p>`
                });
            }

            if(data.Subjects.length>0){
                resultsDiv.innerHTML+="<h3>Subjects</h3>";
                data.Subjects.forEach(subject =>{
                    resultsDiv.innerHTML += `<p> Subject Id:${subject.Subject_Id} - Subject_Name:${subject.Subject_Name}</p>`
                });
            }
            
            if(data.Chapters.length>0){
                resultsDiv.innerHTML+="<h3>Chapters</h3>";
                data.Chapters.forEach(chapter =>{
                    resultsDiv.innerHTML +=`<p> Chapter Id:${chapter.Chapter_Id} - Chapter Title:${chapter.Chapter_Title} </p>`
                });

            }
        })
        .catch(error =>{
            console.error("Search error",error);
            document.getElementById("results").innerHTML="<p style='color=red;'>Something went wrong. Try again.</p>"
        });
}