from flask import Flask,render_template,url_for,redirect,request,session,flash,jsonify
from models import data,User,Subject,Chapter,Quiz,Questions,Option,Scores,Admin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timezone
from flask_bcrypt import Bcrypt
import random,calendar



application=Flask(__name__)
application.secret_key = "your_secret_key" 
bcrypt = Bcrypt(application)

application.config['SQLALCHEMY_DATABASE_URI']='sqlite:///quiz.sqlite'
application.config['SECRET_KEY'] = 'your_secret_key'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

data.init_app(application)


def setup_database():
    data.create_all()

    if not Admin.query.first():
        admin_username='admin_amirtha'
        admin_password='admin@new'
        admin_email='admin@mail.com'
        admin_role='Website Administrator'

        hashed_pw=bcrypt.generate_password_hash(admin_password).decode('utf-8')

        new_admin=Admin(admin_username=admin_username,admin_email=admin_email,admin_password=hashed_pw,admin_role=admin_role)
        
        data.session.add(new_admin)
        data.session.commit()


def generate_color():
    return "#{:06x}".format(random.randint(0,0XFFFFFF))

def get_user_attempts_by_subject():
    user_attempts = (
        data.session.query(
            Subject.sub_name,
            data.func.count(data.func.distinct(Scores.user_score_id)).label("user_attempts")  # Unique users per subject
        )
        .join(Chapter, Subject.sub_id == Chapter.sub_id)
        .join(Quiz, Chapter.chap_id == Quiz.chap_id)
        .join(Scores, Quiz.quiz_id == Scores.quiz_score_id)
        .group_by(Subject.sub_name)
        .all()
    )
    return user_attempts

def get_total_scores_by_subject():
    total_scores = (
        data.session.query(Subject.sub_name,data.func.max(Scores.score_total).label("total_score"))
        .join(Chapter, Subject.sub_id == Chapter.sub_id)
        .join(Quiz, Chapter.chap_id == Quiz.chap_id)
        .join(Scores, Quiz.quiz_id == Scores.quiz_score_id)
        .group_by(Subject.sub_name)
        .all()
    )
    return total_scores

def get_no_of_subject_by_quiz(user_id):
    Quiz_subjects=(
        data.session.query(
            Subject.sub_name,
            data.func.count(data.func.distinct(Scores.quiz_score_id)).label("no_of_quiz")  # Unique quiz per subject
        )
        .join(Chapter, Subject.sub_id == Chapter.sub_id)
        .join(Quiz, Chapter.chap_id == Quiz.chap_id)
        .join(Scores, Quiz.quiz_id == Scores.quiz_score_id)
        .filter(Scores.user_score_id ==user_id)
        .group_by(Subject.sub_name)
        .all())
    return Quiz_subjects

def get_no_of_attempts_by_month(user_id):
    quiz_attempt=(
        data.session.query(
            data.func.extract('year',Scores.score_time_stamp).label('year'),
            data.func.extract('month',Scores.score_time_stamp).label('month'),
            data.func.count(data.func.distinct(Scores.quiz_score_id)).label("no_of_quiz"))
            .filter(Scores.user_score_id==user_id)
            .group_by('year', 'month')
            .order_by('year', 'month')
            .all())
    return quiz_attempt


@application.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        if 'user' in session:
            return render_template("User_Dashboard.html",username=session['name'])
        return render_template('registration.html')
    return render_template('index.html')

@application.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        qualification = request.form.get('qualification')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        dob_1=datetime.strptime(dob, '%Y-%m-%d').date()
        hased_password=bcrypt.generate_password_hash(password).decode('utf-8')

        if User.query.filter_by(email=email).first():
            flash("User already exists!", "error") 
            return redirect(url_for('registration'))
        else:
            new_user=User(email=email,password=hased_password,username=username,qualification=qualification,gender=gender,dob=dob_1)
            data.session.add(new_user)
            data.session.commit()
            # Process the data
            # Store it in the database
            flash('Registration successful!')
            return redirect(url_for('Login'))

    return render_template('registration.html',request_path=request.path)

@application.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(request.path)

        user = User.query.filter_by(email=email).first()
       
        if not user:
            
            flash('User not found.')
            return render_template('loginpage.html',request_path=request.path)

        if bcrypt.check_password_hash(user.password, password):
            session['user'] = user.id
            session['name'] = user.username
            flash('Login successful.')
            return redirect(url_for('userdb'))
        else:
            print("Password mismatch")
            flash('Invalid email or password.')
            
    return render_template('loginpage.html',request_path=request.path)

@application.route('/Logout')
def Logout():
    session.pop('user',None)
    flash('you have been logged out.')
    return redirect(url_for('Login',request_path=request.path))

@application.route('/Admin_Login', methods=['GET', 'POST'])
def Admin_Login():
    if request.method == 'POST':
        admin_email = request.form.get('admin_email')
        admin_password = request.form.get('admin_password')
        
        user_admin = Admin.query.filter_by(admin_email=admin_email).first()
        
        if not user_admin:
            flash('User not found.')
            return render_template('admin_login_page.html')

        if bcrypt.check_password_hash(user_admin.admin_password, admin_password):
            session['admin'] = user_admin.admin_id
            flash('Admin Login successful.')
            return redirect(url_for('admindb'))
        else:
            print("Password mismatch")
            flash('Invalid email or password.')
    return render_template('admin_login_page.html',request_path=request.path)

@application.route('/Admin_Logout',methods=['GET'])
def Admin_Logout():
    session.pop('admin',None)
    flash('you have been logged out.')
    return redirect(url_for('Admin_Login',request_path=request.path))

@application.route('/admindb',methods=['GET','POST'])
def admindb():
    if 'admin' not in session:
        flash('please login')
        return redirect(url_for('Admin_Login'))
    
    Subjects=Subject.query.all()
    Chapters=Chapter.query.all()
    Quizzes=Quiz.query.all()

    return render_template('Admin_Dashboard.html',Subjects=Subjects,Chapters=Chapters,quiz=Quizzes,user="Admin",request_path=request.path)

@application.route('/admindb/quiz_dashboard/')
def quiz_dashboard():
    if 'admin' not in session:
        flash('please login')
        return redirect(url_for('Admin_Login'))
    
    Quizzes=Quiz.query.all()
    Question=Questions.query.all()

    return render_template('quiz_dashboard.html',quizzes=Quizzes,Question=Question,user="Admin",request_path=request.path)


   
@application.route('/admindb/summary_dashboard')
def summary_dashboard():
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect("url_for('Admin_Login')")
    
    users=User.query.all()
    Total_score=Scores.query.all()
    
    subject_scores=get_total_scores_by_subject()
    subject_attempt=get_user_attempts_by_subject()

    bar_color=[generate_color() for _ in range(len(subject_scores))]
    pie_color=[generate_color() for _ in range(len(subject_scores))]

    bar_x_values,bar_y_values,pie_x_values,pie_y_values=[],[],[],[]
    
    for subjects,scores in subject_scores:
        bar_x_values.append(subjects)
        bar_y_values.append(scores)

    for subjects,user_att in subject_attempt:
        pie_x_values.append(subjects)
        pie_y_values.append(user_att)
    

    return render_template('summary.html',user="Admin",users=users,total_score=Total_score,bar_X_subjects=bar_x_values, bar_y_scores=bar_y_values, bar_Colors=bar_color,
        pie_X_subjects=pie_x_values, pie_y_scores=pie_y_values, pie_Colors=pie_color,request_path=request.path)

@application.route('/userdb',methods=['GET','POST'])
def userdb():
    if 'name' not in session:
        flash('please login')
        return redirect(url_for('Login'))
    
    quiz=Quiz.query.all()
    
    return render_template('User_Dashboard.html',quiz=quiz,request_path=request.path)

@application.route('/search',methods=['GET'])
def search():
    s=request.args.get("q","").strip()
    source= request.args.get("source","").strip()
    
    User_results,quiz_results,subject_result,chapter_result,scores_result=[],[],[],[],[] #customize search
    Users,Subjects,Quizzes,Chapters,Score=[],[],[],[],[] # total search
    if session.get('admin'):  
        user_id = session['admin']
    elif session.get('user'):  
        user_id = session['user']
    else:
        return jsonify({"error": "Unauthorized"}), 401  
        

    if not s:
        return jsonify({"error":"Empty search query"}),400
    
    if "admin-navbar.html" in source:
        
        if s.lower().startswith("user"):
            Users=User.query.all()

        if s.lower().startswith("subject"):
            Subjects=Subject.query.all()

        if s.lower().startswith("quiz"):
            Quizzes=Quiz.query.all()

        if s.lower().startswith("chapter"):
            Chapters=Chapter.query.all()

        if s.lower().startswith("score"):
            Score=Scores.query.all()
        
        User_results=User.query.filter(
            User.id.like(f"%{s}%")| User.username.ilike(f"%{s}%")| 
            User.gender.ilike(f"%{s}%")|User.email.ilike(f"%{s}%")).all()
        
        quiz_results = Quiz.query.filter(
            Quiz.quiz_id.like(f"%{s}%")|Quiz.quiz_title.ilike(f"%{s}%")).all()
        
        subject_result=Subject.query.filter(
            Subject.sub_id.like(f"%{s}%")| Subject.sub_name.ilike(f"%{s}%")).all()

        chapter_result=Chapter.query.filter(
            Chapter.chap_id.like(f"%{s}%")|Chapter.chap_title.ilike(f"%{s}%")).all()

       
    elif "user-navbar.html" in source:
        
        if s.lower().startswith("subject"):
            Subjects=Subject.query.all()

        if s.lower().startswith("quiz"):
            Quizzes=Quiz.query.all()

        if s.lower().startswith("chapter"):
            Chapters=Chapter.query.all()

        if s.lower().startswith("score"):
            Score=Scores.query.filter_by(user_score_id=user_id).all()

        quiz_results = Quiz.query.filter(
            Quiz.quiz_id.like(f"%{s}%")|Quiz.quiz_title.ilike(f"%{s}%")).all()
        
        subject_result=Subject.query.filter(
            Subject.sub_id.like(f"%{s}%")| Subject.sub_name.ilike(f"%{s}%")).all()

        chapter_result=Chapter.query.filter(
            Chapter.chap_id.like(f"%{s}%")|Chapter.chap_title.ilike(f"%{s}%")).all()
        
        scores_result=Scores.query.filter(
            Scores.user_score_id==user_id,Scores.quiz_score_id.like(f"%{s}%")|Scores.score_total.like(f"%{s}%")|Scores.score_total.like(f"%{s}%"))
        

    results = {
            "Users":[{"Id":u.id,"Username":u.username,"Email":u.email,"Qualification":u.qualification,"Gender":u.gender,"Date_of_Birth":u.dob.strftime('%d-%m-%Y')}for u in Users],
            "Subjects":[{"Subject_Id":s.sub_id,"Subject_Name":s.sub_name}for s in Subjects],
            "Quizzes":[{"Quiz_Id":q.quiz_id,"Quiz_Title":q.quiz_title,"Quiz_Chapter_Id":q.chap_id,"Quiz_Start_Date":q.quiz_date,"Quiz_Duration":q.quiz_time} for q in Quizzes],
            "Chapters":[{"Chapter_Id":c.chap_id,"Chapter_Title":c.chap_title}for c in Chapters],
            "Scores":[{"User_Id":sc.user_score_id,"Quiz_Id":sc.quiz_score_id,"score_id":sc.score_id,"Total_Score":sc.score_total}for sc in Score],
            "User": [{"Id":u.id,"Username":u.username,"Email":u.email,"Qualification":u.qualification,"Gender":u.gender,"Date_of_Birth":u.dob.strftime('%d-%m-%Y')}for u in User_results],
            "Quiz":[{"Quiz_Id":q.quiz_id,"Quiz_Title":q.quiz_title,"Quiz_Chapter_Id":q.chap_id,"Quiz_Start_Date":q.quiz_date,"Quiz_Duration":q.quiz_time} for q in quiz_results],
            "Subject":[{"Subject_Id":s.sub_id,"Subject_Name":s.sub_name}for s in subject_result],
            "Chapter":[{"Chapter_Id":c.chap_id,"Chapter_Title":c.chap_title}for c in chapter_result],
            "Score":[{"Quiz_Id":sc.quiz_score_id,"score_id":sc.score_id,"Total_Score":sc.score_total}for sc in scores_result]
        }  

    return jsonify(results)  


@application.route('/scores',methods=['GET','POST'])
def scores():
    if 'name' not in session:
        flash('please login')
        return redirect(url_for('Login'))
    
    user_id=session['user']
    scores=Scores.query.filter_by(user_score_id=user_id).all()
    
    return render_template('user_scores.html',scores=scores,request_path=request.path)

@application.route('/userdb/user_summary/<int:user_id>',methods=['GET','POST'])
def user_summary(user_id):
    if 'name' not in session:
        flash('please login')
        return redirect(url_for('Login'))
    
    subject_scores=get_no_of_subject_by_quiz(user_id)
    Quiz_attempts=get_no_of_attempts_by_month(user_id)

    user_bar_color=[generate_color() for _ in range(len(subject_scores))]
    user_pie_color=[generate_color() for _ in range(len(subject_scores))]

    bar_x_values,bar_y_values,pie_x_values,pie_y_values=[],[],[],[]

    for subjects,attemps in subject_scores:
        bar_x_values.append(subjects)
        bar_y_values.append(attemps)

    for year,month,user_att in Quiz_attempts:
        year_month=f"{calendar.month_name[month]} {year}"
        
        pie_x_values.append(year_month)
        pie_y_values.append(user_att)
    
    return render_template('user_summary.html',bar_X_subjects=bar_x_values, bar_y_attemps=bar_y_values, bar_Colors=user_bar_color,
        pie_X_month=pie_x_values, pie_y_user_att=pie_y_values, pie_Colors=user_pie_color,request_path=request.path)

@application.route('/userdb/user_view_quiz/<int:quiz_id>',methods=['GET','POST'])
def user_view_quiz(quiz_id):
    if 'name' not in session:
        flash('please login')
        return redirect(url_for('Login'))
    
    quiz=Quiz.query.get_or_404(quiz_id)
    chapter=Chapter.query.filter_by(chap_id=quiz.chap_id).first()
    subject=Subject.query.filter_by(sub_id=chapter.sub_id).first()

    return render_template('user_view_quiz.html',quiz=quiz,chapter=chapter.chap_title,subject=subject.sub_name,request_path=request.path)

@application.route('/userdb/user_start_quiz/<int:quiz_id>',methods=['GET','POST'])
def user_start_quiz(quiz_id):
    if 'name' not in session:
        flash('please login')
        return redirect(url_for('Login'))
    
    quiz=Quiz.query.get_or_404(quiz_id)
    question=Questions.query.filter_by(quiz_id=quiz_id).all()
    

    correctAnswer={str(i.ques_id) : i.correct_option  for i in question }
    total=0
    
    No_of_quest=len(quiz.quiz_ques)
    
    if request.method=="POST":
        userAnswer=request.get_json()
        time=datetime.now(timezone.utc) 
       
        for ques_id, correct_ans in correctAnswer.items():
            if ques_id not in userAnswer:
                userAnswer[ques_id] = "none"  # Add missing key with "none"
            
            if userAnswer[ques_id] == correct_ans:
                total+=1
        
        
        new_score=Scores(quiz_score_id=quiz_id,user_score_id=session['user'],score_time_stamp=time,score_total=total,No_of_question=No_of_quest)
        data.session.add(new_score)
        data.session.commit()

        if not userAnswer:
            return jsonify({"error": "No data received"}), 400 
        return jsonify({"message":"Quiz submitted successfully","quiz_id":quiz_id,"data":userAnswer,"redirect_url":url_for('scores')}),200
    return render_template('user_start_quiz.html',quiz=quiz,questions=question)


@application.route('/admindb/create_subject', methods=['GET', 'POST'])
def create_subject():
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect(url_for('Admin_Login'))

    if request.method == 'POST':
        sub_name = request.form.get('new_sub_name')
        
       
        if Subject.query.filter_by(sub_name=sub_name).first():  
            flash('This subject already exists.')
            return render_template('subject.html', action="Creation")

        sub_description = request.form.get('new_sub_descrip')
        sub_quiz_descrip = request.form.get('new_sub_quiz_descrip')

     
        new_sub = Subject(sub_name=sub_name, sub_Description=sub_description, sub_quiz_descrip=sub_quiz_descrip)
        data.session.add(new_sub)
        data.session.commit()

        flash(f"{sub_name} Created Successfully")
        return redirect(url_for('admindb'))

    else:
        flash("Something went wrong")
        return render_template('subject.html', action="Creation")

    return render_template('subject.html', action="Create",request_path=request.path)


@application.route('/admindb/edit_subject/<int:sub_id>',methods=['GET','POST'])
def edit_subject(sub_id):
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect("url_for('Admin_Login')")

    subject=Subject.query.get_or_404(sub_id)
    if request.method=='POST':
        subject.sub_name=request.form.get('new_sub_name')
        subject.sub_Description=request.form.get('new_sub_descrip')
        subject.sub_quiz_descrip=request.form.get('new_sub_quiz_descrip')
        data.session.commit()
        flash(f"{ subject.sub_name } Edited Successfully")
        return redirect(url_for('admindb'))
    return render_template('subject.html',action="Edit",subject=subject,request_path=request.path)

@application.route('/admindb/delete_subject/<int:sub_id>',methods=['GET','POST'])
def delete_subject(sub_id):
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect("url_for('Admin_Login')")
    
    subject=Subject.query.get_or_404(sub_id)
    if subject.sub_chap:
        flash("please delete the chapter")
        return redirect(url_for('admindb'))
    data.session.delete(subject)
    data.session.commit()
    flash(f"{ subject.sub_name } deleted Successfully")
    
    return redirect(url_for('admindb',request_path=request.path))

@application.route('/admindb/create_chapter/<int:sub_id>',methods=['GET', 'POST'])
def create_chapter(sub_id):
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect(url_for('Admin_Login'))
    subject = Subject.query.get_or_404(sub_id) 

    if request.method == 'POST':
        chap_title = request.form.get('new_chap_name')
        chap_description = request.form.get('new_chap_descrip')

        if Chapter.query.filter_by(chap_title=chap_title).first():  
            flash('This chapter already exists.')
            return render_template('chapter.html', action="Creation",sub_id=subject.sub_id)
        
        new_chap = Chapter(chap_title=chap_title, chap_description=chap_description,sub_id=subject.sub_id)
        data.session.add(new_chap)
        data.session.commit()

        flash(f"{chap_title} Created Successfully")
        return redirect(url_for('admindb'))

    return render_template('chapter.html', action="Create",request_path=request.path)


@application.route('/admindb/edit_chapter/<int:chap_id>,<int:sub_id>',methods=['GET','POST'])
def edit_chapter(chap_id,sub_id):
    if 'admin' not in session:
        flash('Please Login to create a chapter')
        return redirect("url_for('Admin_Login')")

    chapter=Chapter.query.get_or_404(chap_id,sub_id)
    
    if request.method=='POST':
        chapter.chap_title=request.form.get('new_chap_name')
        chapter.chap_description=request.form.get('new_chap_descrip')
        chapter.sub_id=sub_id
        data.session.commit()
        flash(f"{ chapter.chap_title } Edited Successfully")
        return redirect(url_for('admindb'))
    return render_template('chapter.html',action="Edit",chapter=chapter,request_path=request.path)

@application.route('/admindb/delete_chapter/<int:chap_id>,<int:sub_id>',methods=['GET','POST'])
def delete_chapter(chap_id,sub_id):
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect("url_for('Admin_Login')")
    
    chapter=Chapter.query.get_or_404(chap_id,sub_id)
    if chapter.chap_quiz:
        flash("please delete the Quizzes")
        return redirect("url_for('admindb')")
    data.session.delete(chapter)
    data.session.commit()
    flash(f"{chapter.chap_title} deleted")
    return redirect(url_for('admindb'))

@application.route('/admindb/quiz_dashboard/create_quiz',methods=['GET','POST'])
def create_quiz():
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect(url_for('Admin_Login'))
    
    if Chapter.query.first() == None:
        flash("Please Create Chapter")
        return redirect(url_for('admindb'))
    
    chapters=Chapter.query.all()


    latest_quiz=Quiz.query.order_by(Quiz.quiz_id.desc()).first()
    
    if latest_quiz:
        next_quiz_number=latest_quiz.quiz_id +1
        quiz_title= f"Quiz {next_quiz_number}"
    else:
        quiz_title="Quiz 1"
    
    if request.method=='POST':
        quiz_chap_id=request.form.get('quiz_chap_id')
        date=request.form.get('quiz_date')
        quiz_date=datetime.strptime(date,'%Y-%m-%d').date()
        
        hours=int(request.form.get('quiz_duration_hours'))
        minutes=int(request.form.get('quiz_duration_minute'))

        quiz_duration=(hours*60)+minutes
        
        new_quiz=Quiz(quiz_title=quiz_title,chap_id=quiz_chap_id,quiz_date=quiz_date,quiz_time=quiz_duration)
        data.session.add(new_quiz)
        data.session.commit()

        flash(f"{quiz_title} Created Successfully")
        return redirect(url_for('quiz_dashboard'))
    
    return render_template('quiz_creation.html',chapters=chapters,action='Create',quiz_title=quiz_title,request_path=request.path)

@application.route('/admindb/quiz_dashboard/edit_quiz/<int:quiz_id>',methods=['GET','POST'])
def edit_quiz(quiz_id):
    if 'admin' not in session:
        flash('Please Login to create a chapter')
        return redirect("url_for('Admin_Login')")

    quiz=Quiz.query.get_or_404(quiz_id)
    chapters=Chapter.query.all()

    if request.method=='POST':
        quiz.chap_id=request.form.get('quiz_chap_id')
        
        date=request.form.get('quiz_date')
        quiz.quiz_date=datetime.strptime(date,'%Y-%m-%d').date()
        
        hours=int(request.form.get('quiz_duration_hours'))
        minutes=int(request.form.get('quiz_duration_minute'))

        quiz.quiz_time=(hours*60)+minutes
        
        data.session.commit()
        flash(f"{ quiz.quiz_title } Edited Successfully")
        return redirect(url_for('quiz_dashboard'))
    return render_template('quiz_creation.html',action="Edit",chapters=chapters,quiz_title=quiz.quiz_title,quiz=quiz,request_path=request.path)

@application.route('/admindb/quiz_dashboard/delete_quiz/<int:quiz_id>',methods=['GET','POST'])
def delete_quiz(quiz_id):
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect("url_for('Admin_Login')")
    
    quiz=Quiz.query.get_or_404(quiz_id)
    if quiz.quiz_ques:
        flash("please delete the Questions")
        return redirect(url_for('quiz_dashboard'))
    data.session.delete(quiz)
    data.session.commit()
    flash(f"{quiz.quiz_title} deleted")
    return redirect(url_for('quiz_dashboard'))

@application.route('/admindb/quiz_dashboard/create_question/<int:quiz_id>', methods=['GET','POST'])
def create_question(quiz_id):
    quiz=Quiz.query.get_or_404(quiz_id)
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect(url_for('Admin_Login'))
    
    if request.method=="POST":
        ques_title=request.form.get("ques_title")
        ques_statement=request.form.get("ques_statement")
        correct_option=request.form.get("correctoption")
        
        question=Questions(ques_title=ques_title,ques_statement=ques_statement,correct_option=correct_option,quiz_id=quiz_id)
        data.session.add(question)
        data.session.commit()
       
        optionsList = request.form.getlist("options[]")
        for option in optionsList:
            
            new_option=Option(op_statement=option,op_ques_id=question.ques_id)
            data.session.add(new_option)

        data.session.commit()
        flash(f"{ ques_title } Created Successfully")


    return render_template('question.html',action='Create',quiz=quiz,request_path=request.path)

@application.route('/admindb/quiz_dashboard/edit_question/<int:quiz_id>,<int:question_id>',methods=['GET','POST'])
def edit_question(quiz_id,question_id):
    if 'admin' not in session:
        flash('Please Login to create a chapter')
        return redirect("url_for('Admin_Login')")
    
    quiz=Quiz.query.get_or_404(quiz_id)
    question=Questions.query.get_or_404(question_id)
    
    if request.method=='POST':
        question.ques_title=request.form.get('ques_title')
        question.ques_statement=request.form.get("ques_statement")
        question.correct_option=request.form.get("correctoption")
        
        data.session.commit()

        optionsList = request.form.getlist("options[]")
        existing_options = question.options.all() 
        print(optionsList)
        print(existing_options)
        new_texts = set(optionsList)
        for opt in existing_options:
            if opt.op_statement not in new_texts: 
                data.session.delete(opt)

        existing_map = {opt.op_statement: opt for opt in existing_options}  
        for text in optionsList:
            if text in existing_map: 
                existing_map[text].op_statement = text
            else:
                
                new_option = Option(op_statement=text, op_ques_id=question.ques_id)
                data.session.add(new_option)


        data.session.commit()       
                

        flash(f"{ quiz.quiz_title } Edited Successfully")
        return redirect(url_for('quiz_dashboard'))
    return render_template('Edit_question.html',action="Edit",quiz=quiz,question=question,request_path=request.path)

@application.route('/admindb/quiz_dashboard/delete_question/<int:question_id>',methods=['GET','POST'])
def delete_question(question_id):
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect("url_for('Admin_Login')")
    
    question=Questions.query.get_or_404(question_id)
    
    data.session.delete(question)
    data.session.commit()
    flash(f"{question.ques_title} deleted")
    return redirect(url_for('quiz_dashboard'))




with application.app_context():
    setup_database()


if __name__=='__main__':
    application.run(debug=True)

