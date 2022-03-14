from flask import Flask
from flask_restful import Api


from resources.user import Forgot, Login, Otpvalidation, Reset, UpdatePassword, UpdateUserDetails, UserRegister

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sunil'
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

api.add_resource(UserRegister, '/register')
api.add_resource(UpdatePassword, '/updatepassword')
api.add_resource(Login, '/login')
api.add_resource(Otpvalidation, '/otpvalidation')
api.add_resource(Forgot, '/forgotpassword')
api.add_resource(Reset, '/resetpassword')
api.add_resource(UpdateUserDetails, '/UpdateUserDetails')

if(__name__ == '__main__'):
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)