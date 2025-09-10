from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from model import app
from model import *
from datetime import datetime
from sqlalchemy import update
import json, random, hashlib

api = Api(app)

user_fields= {
   'user_id': fields.String,
   'user_name': fields.String,
   'email_id': fields.String,
   'password': fields.String,
   'role': fields.String
}

upPwd_fields= {
   'user_id': fields.String,
   'email_id': fields.String,
   'password': fields.String,
   'otp': fields.String
}

course_fields= {
   'course_code': fields.String,
   'course_name': fields.String,
   'course_type': fields.String,
   'total_credits':fields.Integer,
   'semester_in': fields.Integer
}

user_login = reqparse.RequestParser()
user_login.add_argument("user_id", type=int, help="user_id is required", required=True)
user_login.add_argument("password", type=str, help="password is required", required=True)
user_login.add_argument("user_name", type=str)
user_login.add_argument("email_id", type=str)
user_login.add_argument("role", type=str)

user_post = reqparse.RequestParser()
user_post.add_argument("user_id", type=int, help="user_id is required", required=True)
user_post.add_argument("password", type=str, help="password is required", required=True)
user_post.add_argument("user_name", type=str, help="user_name is required", required=True)
user_post.add_argument("email_id", type=str, help="email_id is required", required=True)
user_post.add_argument("role", type=str, help="role is required", required=True)

user_put = reqparse.RequestParser()
user_put.add_argument("user_id", type=int, help="user_id is required", required=True)
user_put.add_argument("password", type=str)  #, help="password is required", required=True
user_put.add_argument("email_id", type=str)
user_put.add_argument("otp", type=int)

course_post = reqparse.RequestParser()
course_post.add_argument("course_code", type=str, help="course_code is required", required=True)
course_post.add_argument("course_name", type=str, help="course_name is required", required=True)
course_post.add_argument("course_type", type=str, help="course_type is required", required=True)
course_post.add_argument("total_credits", type=int, help="total_credits is required", required=True)
course_post.add_argument("semester_in", type=int, help="semester_in is required", required=True)

course_get = reqparse.RequestParser()
course_get.add_argument("semester_in", type=int, help="semester_in is required", required=True)

def pwdencryption(str):
    result = hashlib.sha256(str.encode())
    encryptedpwd = result.hexdigest()
    return encryptedpwd

class userLogin(Resource):
    # to read from the database for login
    @marshal_with(user_fields)
    def post(self): 
        args = user_login.parse_args()
        user = userDetails.query.filter_by(user_id=args["user_id"]).first()
        pwd = pwdencryption(args["password"])
        if not user:
            abort(404, message="Could not find such user")
        elif user and pwd != user.password:
            abort(409, message="Incorrect password")
        args['user_name'] = user.user_name
        args['email_id'] = user.email_id 
        args['role'] = user.role
        args['password'] = ""
        return args

class userRegister(Resource):
   # to store in database for registration
    @marshal_with(user_fields)
    def post(self):
        args = user_post.parse_args()
        user = userDetails.query.filter_by(user_id=args["user_id"]).first()
        pwd = pwdencryption(args["password"])
        if user:
            abort(409, message="user id already exists")
        addUser = userDetails(user_id = args["user_id"],user_name = args["user_name"],email_id = args["email_id"],password = pwd, role = args['role'])
        db.session.add(addUser)
        db.session.commit()
        return 201
    
def send_otp_email(email, otp):
    msg = Message('Your OTP Code', recipients=[email])
    msg.body = f'Your OTP code is: {otp}'
    mail.send(msg)

class UpdatePassword(Resource):
    @marshal_with(upPwd_fields)
    def post(self):     # to get user_id to check in db and send otp for forgot password
        args = user_put.parse_args()
        user = userDetails.query.filter_by(user_id=args["user_id"]).first()
        if not user:
            abort(404, message = "Invalid id, cannot update")
        elif not user.email_id:
            abort(404, "User's mail id is not found")
        email_id = user.email_id
        global otp
        otp = random.randint(100001, 999999)
        send_otp_email(email_id, otp)
        return "otp has been sent to your registered mail...", 201

    def put(self):     # to validate otp and update password in the db
        args = user_put.parse_args()
        user = userDetails.query.filter_by(user_id=args["user_id"]).first()
        if not args["password"]:
            abort(404, message = "please enter the new password" )
        if not args["otp"]:
            abort(404, message = "please enter the OTP" )
        if args["password"] and args["otp"] == otp:
            pwd = pwdencryption(args["password"])
            user.password = pwd
        db.session.commit()
        return "Password has been updated succesfully!",201
    
class courseRegister(Resource):
    @marshal_with(course_fields)    
    def post(self):     # to store in database when a new course is registered
        args = course_post.parse_args()
        isCourse = course.query.filter_by(course_code=args["course_code"]).first()
        if isCourse:
            abort(404, message="course already exist")
        addCourse = course(course_code=args["course_code"],course_name=args["course_name"],course_type=args["course_type"],total_credits=args["total_credits"],semester_in=args["semester_in"])
        db.session.add(addCourse)
        db.session.commit()
        return "course Registered successfully",201
    
class listCourses(Resource):
    @marshal_with(course_fields)    
    def get(self,semester_in):      # to list all the courses that are in a particular sem for dropdown
        lcourses = db.session.query(course.course_code).filter(course.semester_in == semester_in)
        courseList = []
        if not lcourses:
            abort(404, message="no course registered for this sem")
        for i in lcourses:
            courseList.append({"course_code": i.course_code})
        print(courseList)
        return courseList


api.add_resource(userRegister,'/userRegister')
api.add_resource(userLogin,'/userLogin')
api.add_resource(UpdatePassword,'/upPass')
api.add_resource(courseRegister,'/courseRegister')
api.add_resource(listCourses,'/listCourses/<int:semester_in>')


if __name__ == '__main__':
   app.run(debug=True, host="0.0.0.0", port=5000)