from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from datetime import datetime, date
from flask_mail import Mail, Message

app = Flask(__name__)

DB_URL = "postgresql://postgres:2021239018@localhost:5432/amsdb4"
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.app_context().push()
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hariniks0618@gmail.com'
app.config['MAIL_PASSWORD'] = 'gfah xgwu uohv oxbw' # app pwd made in gacc
app.config['MAIL_DEFAULT_SENDER'] = 'hariniks0618@gmail.com'
mail = Mail(app)

if __name__ == '__main__':
   app.run(debug=True)

class student_details(db.Model):
    user_id = Column(String, primary_key=True)
    user_name = Column(String, nullable=False)
    email_id = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Integer, default=0)
    otp = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class staff_details(db.Model):
    user_id = Column(String, primary_key=True)
    user_name = Column(String, nullable=False)
    email_id = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)
    advisor_class = Column(Integer,default=0)
    is_active = Column(Integer, default=0)
    otp = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class course(db.Model):
    course_code=Column(String,primary_key=True)
    course_name=Column(String, nullable=False)
    course_type=Column(String, nullable=False)
    total_credits=Column(Integer, nullable=False)
    semester_in=Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # attend = relationship("attendance.course_code")

class attendance(db.Model):
    attendnace_id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String, ForeignKey(course.course_code))
    class_date = Column(Date, nullable=False, default=date.today())
    class_hour = Column(Integer, nullable=False)
    user_id = Column(String,ForeignKey(student_details.user_id), nullable=False)
    status = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class student_enrolled(db.Model):
    enroll_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String,ForeignKey(student_details.user_id), nullable=False)
    course_code = Column(String,ForeignKey(course.course_code), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class teacher_assigned(db.Model):
    assigned_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String,ForeignKey(staff_details.user_id), nullable=False)
    course_code = Column(String,ForeignKey(course.course_code), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class absence_intimation(db.Model):
    absent_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String,ForeignKey(student_details.user_id), nullable=False)
    course_code = Column(String,ForeignKey(course.course_code), nullable=False)
    absent_date = Column(Date, nullable=False)
    absent_hour = Column(Integer, nullable=False)
    absent_reason = Column(String(500), nullable=False)
    status = Column(Integer, default=-1)        # if status = 0=> rejected... if 1=>then accepted... if -1=> not responded
    created_at = Column(DateTime, default=datetime.utcnow)

db.create_all()