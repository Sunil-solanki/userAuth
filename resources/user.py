from flask_restful import Resource, reqparse
from models.user import UserModel
import jwt
import random
import math
from datetime import datetime, timedelta
import re


# user registration
class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('full_name',
        type=str,
        required=True,
        help="Provide your full name."
    )
    parser.add_argument('mobile_number',
        type=str,
        required=True,
        help="Provide your mobile_number."
    )
    parser.add_argument('email_id',
        type=str,
        required=True,
        help="Provide your email_id."
    )
    parser.add_argument('username',
        type=str,
        required=True,
        help="Provide your username."
    )
    parser.add_argument('password',
        type=str,
        required=True,
        help="Provide your password."
    )
    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "Username is already Registered."}, 400
        if UserModel.find_by_mobile_number(data['mobile_number']):
            return {"message": "Mobile number is already Registered."}, 400
        if UserModel.find_by_email_id(data['email_id']):
            return {"message": "Email id is already Registered."}, 400
       
        match_email = re.findall(r'[\w]+[@][\w]+[.][\w]+', data['email_id'])
        match_mobile = re.findall(r'\d{10}', data['mobile_number'])
        mobile_len = len(data['mobile_number'])
        if match_email == []:
            return {"message": "Please enter a valid email address!"}
        if match_mobile == [] or mobile_len != 10:
            return {"message": "Please enter a valid mobile number!"}
        

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully, you can login now."}, 201


# update the password
class UpdatePassword(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help="Provide your username."
    )
    parser.add_argument('current_password',
        type=str,
        required=True,
        help="Provide your current_password."
    )
    parser.add_argument('new_password',
        type=str,
        required=True,
        help="Provide your new_password."
    )

    def put(self):
        data = UpdatePassword.parser.parse_args()

        username = UserModel.find_by_username(data['username'])

        if username is None:
            return {"message": f"User with username '{data['username']}' not found!"}, 404
        elif username.password != data['current_password']:
            return {"message": "You entered wrong credentials, please enter correct credentials. If you forgot credentials reset your credentials!"}
        else:
            username.password = data['new_password']

        username.save_to_db()

        return {"message": "Password updated successfully, now you can authenticate using new password!"}, 201


# Login 
class Login(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help="Provide your username."
    )
    parser.add_argument('password',
        type=str,
        required=True,
        help="Provide your password."
    )
    
    def post(self):
        data = Login.parser.parse_args()

        username = UserModel.find_by_username(data['username'])

        if username is None:
            return {"message": f"User with username '{data['username']}' not found, please register first."}, 404

        elif username.password == data['password']:

            ## initializing a string
            random_otp = ""
            ## generating 6 digit lenght of string
            for i in range(6):
                index = math.floor(random.random() * 10)
                random_otp += str(index)
            username.OTP = random_otp

            username.save_to_db()
            return {"message": f"You have successfully logged in. Your OTP is: {username.OTP}"}, 200

        elif username.password != data['password']:
            return {"message": "You have entered wrong credentials."}, 401
        else:
            {"message": "There is some Internal Server Error!"}, 500


# validating otp     
class Otpvalidation(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help="Provide your username."
    )
    parser.add_argument('OTP',
        type=str,
        required=True,
        help="Provide OTP."
    )
    def get(self):
        data = Otpvalidation.parser.parse_args()

        username = UserModel.find_by_username(data['username'])

        if username is None:
            return {"message": "User not found!"}, 404
        elif username.OTP == data['OTP']:
            # access_token
            payload_data = {
                "username" : "username",
                "password" : "password"
            }
            token = jwt.encode (
                payload=payload_data,
                key='sunil_secret_key'
            )

            return {"message": f"'{username.full_name}', Your OTP is successfully authenticated.",
                    "Username": f"{data['username']}",
                    "Name": f"{username.full_name}",
                    "Mobile Number": f"{username.mobile_number}",
                    "Email Id": f"{username.email_id}",
                    "access_token": f"{token.decode('utf-8')}"
            }, 200
        else:
            return {"message": "Please enter correct OTP."}, 401


class Forgot(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help="Provide your username."
    )
    def post(self):
        data = Forgot.parser.parse_args()

        email = UserModel.find_by_username(data['username'])

        if email is None:
            return {"message": "User with this username id not found."}, 404

        else:
             # reset_password_token
            reset_payload_data = {
                "username" : data['username']
            }
            reset_password_token = jwt.encode (
                payload=reset_payload_data,
                key=('sunil_secret_key')
            )
            email.token_gen_time = datetime.now()
            email.save_to_db()
            return {"reset password token": f"{reset_password_token.decode('utf-8')}"}

class Reset(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('access_token',
        type=str,
        required=True,
        help="Provide your access token."
    )
    parser.add_argument('new_password',
        type=str,
        required=True,
        help="Provide new password."
    )
    parser.add_argument('confirm_new_password',
        type=str,
        required=True,
        help="Provide confirm new password."
    )
    def post(self):
        data = Reset.parser.parse_args()
        current_date = datetime.now() - timedelta(minutes=5)
        
        if data:
            token = data['access_token']
            token_data = jwt.decode(token,key='sunil_secret_key',algorithms=['HS256',])
            username = token_data['username']
        username = UserModel.find_by_username(username)
        if (str(current_date) >= username.token_gen_time):
            return {"message": "Your token has expired, please generate a new one."}
        if username is None:
            return {"message": "Invalid token!!"}, 401
        elif data['new_password'] == data['confirm_new_password']:
            username.password = data['new_password']
        else:
            return {"message": "Please enter 'new password' and 'confirm new password' same"}

        username.save_to_db()

        return {"message": "Password changed successfully, now you can authenticate using new password!"}, 201


class UpdateUserDetails(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help="Provide your username."
    )
    parser.add_argument('password',
        type=str,
        required=True,
        help="Provide your password."
    )
    parser.add_argument('full_name',
        type=str,
    )
    parser.add_argument('mobile_number',
        type=str,
    )
    parser.add_argument('email_id',
        type=str,
    )

    def put(self):
        data = UpdateUserDetails.parser.parse_args()

        username = UserModel.find_by_username(data['username'])

        if username is None:
            return {"message": f"User with username '{data['username']}' not found!"}, 404
        elif username.password != data['password']:
            return {"message": "You entered wrong credentials, please enter correct credentials. If you forgot credentials reset your credentials!"}
        else:
            if data['full_name'] is None and data['email_id'] is None and data['mobile_number'] is None:
                return {"message": "Please provide details to update!"}
            if data['full_name'] is None:
                username.full_name = username.full_name
            else:
                username.full_name = data['full_name']
            if data['mobile_number'] is None:
                username.mobile_number = username.mobile_number
            else:
                username.mobile_number = data['mobile_number']
            if data['email_id'] is None:
                username.email_id = username.email_id
            else:
                username.email_id = data['email_id']
        username.save_to_db()

        return {"message": "Your details updated successfully!"}, 201


