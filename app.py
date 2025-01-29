from flask import Flask,render_template,url_for,redirect,request,session,flash
from models import data,User,Subject,Chapter,Quiz,Questions,Option,Scores,Admin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
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

      
        
        if check_password_hash(user_admin.admin_password, admin_password):
            session['admin'] = user_admin.admin_id
            flash('Admin Login successful.')
            return redirect(url_for('admindb'))
        else:
            print("Password mismatch")
            flash('Invalid email or password.')
    return render_template('admin_login_page.html')

@application.route('/Admin_Logout',method='GET')
def Admin_Logout():
    session.pop('admin',None)
    flash('you have been logged out.')
    return redirect(url_for('Admin_Login'))

@application.route('/admindb')
def admindb():
    return render_template('Admin_Dashboard.html')

@application.route('/userdb',methods=['GET','POST'])
def userdb():
    return render_template('User_Dashboard.html',user=session['name'])


@application.route('admindb/create_subject',method=['GET','POST'])
def create_subject():

    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect(url_for('Admin_Login'))

    if request.method=='POST':
        sub_name=request.form.get('new_sub_name')
        sub_Description=request.form.get('new_sub_descrip')
        sub_quiz_descrip=request.form.get('new_sub_quiz_descrip')

        

        new_sub=Subject(sub_name=sub_name,sub_Description=sub_Description,sub_quiz_descrip=sub_quiz_descrip)
        data.session.add(new_sub)
        data.session.commit()
        flash(f"{ sub_name } Created Successfully")
        return redirect(url_for('Admin_Login'))
    return render_template('subject.html',action="Creation")

@application.route('admindb/edit_subject/<int:sub_id>',method=['GET','POST'])
def edit_subject(sub_id):
    if 'admin' not in session:
        flash('Please Login to create a subject')
        return redirect("url_for('Admin_Login')")

    subject=Subject.query.get_or_404(sub_id)
    if request.method=='POST':
        subject.sub_name=request.form.get('new_sub_name')
        subject.sub_Description=request.form.get('new_sub_descrip')
        subject.sub_quiz_descrip=request.form.get('new_sub_quiz_descrip')

        flash(f"{ subject.sub_name } Edited Successfully")
        return redirect(url_for('Admin_Login'))
    return render_template('subject.html',action="Edit")


with application.app_context():
    setup_database()


if __name__=='__main__':
    application.run(debug=True)

