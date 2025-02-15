from sqlalchemy import Date
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

data=SQLAlchemy()

class User(data.Model):
    __tablename__='user'
    id=data.Column(data.Integer,primary_key=True)
    username=data.Column(data.String(50),nullable=False)
    email=data.Column(data.String(150),nullable=False,unique=True)
    password=data.Column(data.String(200),nullable=False)
    qualification=data.Column(data.String(150),nullable=False)
    gender=data.Column(data.String(6),nullable=False)
    dob=data.Column(Date,nullable=False)
    scores=data.relationship('Scores',backref='User',lazy=True)
    

class Subject(data.Model):
    __tablename__='sub'
    sub_id=data.Column(data.Integer,primary_key=True)
    sub_name=data.Column(data.String(50),nullable=False,unique=True)
    sub_Description=data.Column(data.Text,nullable=True)
    sub_quiz_descrip=data.Column(data.Text,nullable=True)
    sub_chap=data.relationship('Chapter',backref='Subject',lazy=True)
    
class Chapter(data.Model):
    __tablename__='chap'
    chap_id=data.Column(data.Integer,primary_key=True)
    chap_title=data.Column(data.String(200),nullable=False,unique=True)
    chap_description=data.Column(data.Text,nullable=False)
    chap_quiz=data.relationship('Quiz',backref='Chapter',lazy=True)
    sub_id=data.Column(data.Integer,data.ForeignKey('sub.sub_id'),nullable=False)

    

class Quiz(data.Model):
    __tablename__='quizzes'
    quiz_id=data.Column(data.Integer,primary_key=True)
    quiz_title=data.Column(data.String(200),nullable=False)
    chap_id=data.Column(data.Integer,data.ForeignKey('chap.chap_id'),nullable=False)
    quiz_date=data.Column(data.Date,nullable=False)
    quiz_time=data.Column(data.Integer,nullable=False)
    quiz_score=data.relationship('Scores',backref='Quiz',lazy=True)
    quiz_ques=data.relationship('Questions',backref='Quiz',lazy=True)
    
    @property
    def question(self):
        return len(self.quiz_ques)
    
class Questions(data.Model):
    __tablename__="question"
    ques_id=data.Column(data.Integer,primary_key=True)
    ques_title=data.Column(data.String(200),nullable=False)
    ques_statement=data.Column(data.Text,nullable=False,unique=True)
    options=data.relationship('Option',backref='question',cascade='all,delete-orphan',lazy='dynamic',foreign_keys='Option.op_ques_id')
    quiz_id=data.Column(data.Integer,data.ForeignKey('quizzes.quiz_id'),nullable=False)
    correct_option=data.Column(data.Integer,data.ForeignKey('options.op_id'),nullable=True)

    def __repr__(self):
        return f"<Question: {self.ques_statement}>"
    
class Option(data.Model):
    __tablename__="options"
    op_id=data.Column(data.Integer,primary_key=True)
    op_statement=data.Column(data.Text,nullable=False)
    op_ques_id=data.Column(data.Integer,data.ForeignKey('question.ques_id'),nullable=False)
   
    
    def __repr__(self):
        return f"<Option: {self.op_statement}>"


class Scores(data.Model):
    __tablename__="score"
    score_id=data.Column(data.Integer,primary_key=True)
    quiz_score_id=data.Column(data.Integer,data.ForeignKey('quizzes.quiz_id'),nullable=False)
    user_score_id=data.Column(data.Integer,data.ForeignKey('user.id'),nullable=False)
    score_time_stamp=data.Column(data.DateTime,nullable=False)
    score_total=data.Column(data.Integer,nullable=False)

class Admin(data.Model):
    __tablename__="admin"
    admin_id=data.Column(data.Integer,primary_key=True)
    admin_username=data.Column(data.String(50),nullable=False)
    admin_email=data.Column(data.String(150),nullable=False,unique=True)
    admin_password=data.Column(data.String(200),nullable=False)
    admin_role=data.Column(data.String(150),nullable=False)


    


