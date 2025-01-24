from flask import Flask,render_template,url_for,redirect,request

application=Flask(__name__)

@application.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        return render_template('registration.html')
    return render_template('index.html')

@application.route('/registration',methods=['GET','POST'])
def registration():
    
    return render_template('registration.html')

@application.route('/Login')
def Login():
    return render_template('loginpage.html')

# @application.route('/admindashboard')
# def admindb():
#     return render_template('Admin_Dashboard.html')

# @application.route('/userdashboard')
# def admindb():
#     return render_template('User_Dashboard.html')





if __name__=='__main__':
    application.run(debug=True)

