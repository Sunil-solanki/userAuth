from db import db

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80))
    mobile_number = db.Column(db.String(10))
    email_id = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))
    OTP = db.Column(db.String(6))
    token_gen_time = db.Column(db.String(80))
    token_exp_time = db.Column(db.String(80))

    def __init__(self, username, password, full_name, mobile_number, email_id):
        self.username = username
        self.password = password
        self.full_name = full_name
        self.mobile_number = mobile_number
        self.email_id = email_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_mobile_number(cls, mobile_number):
        return cls.query.filter_by(mobile_number=mobile_number).first()

    @classmethod
    def find_by_email_id(cls, email_id):
        return cls.query.filter_by(email_id=email_id).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()