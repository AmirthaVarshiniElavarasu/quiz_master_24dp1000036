from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

data=SQLAlchemy()

class User(data.Model):
    __table__='user'
    id=data.Column(data.Integer,primary_key=True)
    username=data.Column(data.String(50),nullable=False)
    Email=data.Column(data.String(150),nullable=False,unique=True)
    password=data.Column(data.String(200),nullable=False)
    Qualification=data.Column(data.String(150),nullable=False)
    Gender=data.Column(data.String(6),nullable=False)
    dob=data.Column(data.DateTime(),nullable=False)
    

class Subject(data.Model):
    __table__='sub'
    sub_id=data.Column(data.Integer,primary_key=True)
    sub_name=data.Column(data.String(50),nullable=False,unique=False)
    sub_Description=data.Column(data.String(200),nullable=True)
    sub_post=data.Column('Chapter')
    
class Chapter(data.Model):
    __table__='chap'
    chap_id=data.Column(data.Integer,primary_key=True)
    chap_title=data.Column(data.String(200),nullable=False,unique=False)
    chap_Description=data.Column(data.String(200),nullable=False)
    user_id=data.Column(data.Integer,data.ForeignKey('user.id'),nullable=False)

class Quiz(data.Model):
    __table__='quizzes'
    _id=data.Column(data.Integer,primary_key=True)
    chap_title=data.Column(data.String(200),nullable=False,unique=False)
    chap_Description=data.Column(data.String(200),nullable=False)
    chap_id=data.Column(data.Integer,data.ForeignKey('.id'),nullable=False)
    


