from flask import Flask,request,jsonify,render_template
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash
from flask_basicauth import BasicAuth
#from flask_login import

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'adminpass'

#users database created by hand in pgadmin
#personal postgres password should be written in the string bellow
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:password@localhost/users'

api = Api(app)

bcrypt = Bcrypt(app)
basic_auth = BasicAuth(app)
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(50), nullable=False)
    password= db.Column(db.String(500), nullable=False)

    def __init__(self,username,password):
        self.username=username
        self.password=password

    def check_password(self, password):
        return check_password_hash(self.password, password)

#run db.create_all() only once so a users table would be created in the users db

#errors
def abort_if_user_doesnt_exist(id,user):
    if user is None:
        abort(404, message="User with id {} doesn't exist".format(id))

def abort_if_username_exists(user):
    if user:
        abort(400, message="Username {} exists".format(user.username))

def abort_if_password_is_bad(password):
    if len(password) < 6:
        abort(400, message='password is too short.')

#resource for first endpoint => function: inserting a new user in the db (registration)
#dont need to be autheticated to register
class InsertUser(Resource):

    def post(self):
        username = request.form['username']
        user= db.session.query(User).filter(User.username == username).first()
        abort_if_username_exists(user)
        password=request.form['password']
        abort_if_password_is_bad(password)
        password = generate_password_hash(password).decode('utf8')
        user = User(username,password)
        db.session.add(user)
        db.session.commit()
        id = user.id
        return {'id': str(id)}, 200

#resource for second endpoint => function: editing info for a user in the db (update)
#can be reached only by admin
class UpdateUser(Resource):

    @basic_auth.required
    def put(self,id):
        userResult = db.session.query(User).filter(User.id == id).first()
        abort_if_user_doesnt_exist(id, userResult)
        username = request.form['username']
        user = db.session.query(User).filter(User.username == username).first()
        if user:
            if userResult.id != user.id:
                abort(400, message="Username {} exists".format(user.username))
        password = request.form['password']
        abort_if_password_is_bad(password)
        password = generate_password_hash(password).decode('utf8')
        userResult.username=username
        userResult.password=password
        db.session.commit()
        return {'id': str(id)}, 200

#resource for third endpoint => function: finding info for a user with given id in the db
#can be reached only by admin
class FindUser(Resource):

    @basic_auth.required
    def get(self,id):
        userResult = db.session.query(User).filter(User.id == id).first()
        abort_if_user_doesnt_exist(id,userResult)
        username=userResult.username
        password=userResult.password
        return {'username': username, 'password': password}, 200


api.add_resource(InsertUser,"/user/signup")
api.add_resource(UpdateUser,"/user/edit/<int:id>")
api.add_resource(FindUser,"/user/<int:id>")

if __name__ == "__main__":
    app.run(debug=True)