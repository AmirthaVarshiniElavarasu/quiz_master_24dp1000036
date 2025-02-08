from flask import Flask,render_template,url_for,redirect,request,session,flash
from models import data,User,Subject,Chapter,Quiz,Questions,Option,Scores,Admin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timedelta
from flask_bcrypt import Bcrypt


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

        if User.query.filter_by(username=username).first():
            return "Username already exists!"
        else:
            new_user=User(email=email,password=hased_password,username=username,qualification=qualification,gender=gender,dob=dob_1)
            data.session.add(new_user)
            data.session.commit()
            # Process the data
            # Example: Store it in the database
            flash('Registration successful!')
            return redirect(url_for('Login'))

    return render_template('registration.html')


@application.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        

        user = User.query.filter_by(email=email).first()
        
        if not user:
            
            flash('User not found.')
            return render_template('loginpage.html')

      
        
        if check_password_hash(user.password, password):
            session['user'] = user.id
            session['name'] = user.username
            flash('Login successful.')
            return redirect(url_for('userdb'))
        else:
            print("Password mismatch")
            flash('Invalid email or password.')
    return render_template('loginpage.html')

@application.route('/Logout')
def Logout():
    session.pop('user',None)
    flash('you have been logged out.')
    return redirect(url_for('Login'))



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
    return render_template('admin_login_page.html')

@application.route('/Admin_Logout',methods=['GET'])
def Admin_Logout():
    session.pop('admin',None)
    flash('you have been logged out.')
    return redirect(url_for('Admin_Login'))

@application.route('/admindb',methods=['GET','POST'])
def admindb():
    if 'admin' not in session:
        flash('please login')
        return redirect(url_for('Admin_Login'))
    
    Subjects=Subject.query.all()
    Chapters=Chapter.query.all()

    return render_template('Admin_Dashboard.html',Subjects=Subjects,Chapters=Chapters)

@application.route('/admindb/quiz_dashboard/')
def quiz_dashboard():
    if 'admin' not in session:
        flash('please login')
        return redirect(url_for('Admin_Login'))
    
    Quizzes=Quiz.query.all()

    return render_template('quiz_dashboard.html',quizzes=Quizzes)
    
@application.route('/admindb/summary_dashboard')
def summary_dashboard():
    return render_template('summary.html')

@application.route('/userdb',methods=['GET','POST'])
def userdb():
    return render_template('User_Dashboard.html',user=session['name'])


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

    return render_template('subject.html', action="Create")


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
    return render_template('subject.html',action="Edit",subject=subject)

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
    return redirect(url_for('admindb'))

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

    return render_template('chapter.html', action="Create")


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
    return render_template('chapter.html',action="Edit",chapter=chapter)

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
    
    return render_template('quiz_creation.html',chapters=chapters,action='Create',quiz_title=quiz_title)

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
    return render_template('quiz_creation.html',action="Edit",chapters=chapters,quiz_title=quiz.quiz_title,quiz=quiz)

@application.route('/admindb/quiz_dashboard/delete_quiz/<int:quiz_id>',methods=['GET','POST'])
def delete_quiz(quiz_id):
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect("url_for('Admin_Login')")
    
    quiz=Quiz.query.get_or_404(quiz_id)
    if quiz.quiz_ques:

        flash("please delete the Questions")
        return redirect("url_for('admindb')")
    data.session.delete(quiz)
    data.session.commit()
    flash(f"{quiz.quiz_title} deleted")
    return redirect(url_for('quiz_dashboard'))

@application.route('/admindb/quiz_dashboard/create_question', methods=['GET','POST'])
def create_question():
    chapters=Chapter.query.all()
    return render_template('question.html',action='Create',chapters=chapters)

with application.app_context():
    setup_database()


if __name__=='__main__':
    application.run(debug=True)

