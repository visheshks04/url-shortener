from flask import Flask, render_template, session, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
import hashlib
import string
import random
import json
import os


app = Flask(__name__)
api = Api(app)

db_user = os.getenv('DB_USER', 'default_user')
db_password = os.getenv('DB_PASSWORD', 'default_password')
db_name = os.getenv('DB_NAME', 'default_db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@localhost/{db_name}'

db = SQLAlchemy(app)
migrate = Migrate(app, db)



class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)



class URL(db.Model):
    __tablename__ = 'urls'

    short_url = db.Column(db.String(50), nullable=False, primary_key=True)
    full_url = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visits = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<URL {self.short_url}>"
    
    def to_json(self):
        return {
            'short_url': self.short_url,
            'full_url': self.full_url,
            'user_id': self.user_id,
        }
    



class ShortenURL(Resource):
    def get(self, url):

        user_id = request.headers.get('user-id')

        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        hash_object = hashlib.sha1(url.encode())
        short_url = hash_object.hexdigest()[:8]

        new_url = URL(short_url=short_url, user_id=user_id, full_url = url)
        db.session.add(new_url)
        db.session.commit()

        return {'original_url': url, 'shortened_url': f'http://yourdomain/{short_url}'}

class RedirectURL(Resource):
    def get(self, short_url):
        
        url = URL.query.get(short_url)

        url.visits = url.visits+1
        db.session.commit()

        if not url:
            return {'status': 404, 'message': 'URL not found'}, 404

        return redirect(url.full_url)
        # return {'status': 200, 'url': url.full_url}, 200
    

class AllURLs(Resource):
    def get(self):

        user_id = request.headers.get('user-id')

        user = User.query.get(user_id)
        if not user:
            return {'status': 404, 'message': 'User not found'}, 404
        
        urls = URL.query.filter_by(user_id=user.id).all()

        urls = [url.to_json() for url in urls]

        return {'status': 200, 'urls': urls}, 200
        

class UserSignUp(Resource):
    def post(self):

        username = request.headers.get('username')
        password = request.headers.get('password')

        print(username)
        print(password)

        user = User.query.filter_by(username=username).all()
    
        if user:
            return {'status': 400, 'message': 'Username already exists'}, 400

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return {'status': 201, 'message': 'User registered successfully', 'user_id': new_user.id}, 201


class UserLogin(Resource):
    def post(self):
        username = request.headers.get('username')
        password = request.headers.get('password')

        print(username)
        print(password)

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            return {'status': 200, 'message': 'Login successful', 'user_id': user.id}, 200
        else:
            return {'status': 401, 'message': 'Invalid credentials'}, 401


api.add_resource(ShortenURL, '/shorten/<path:url>')
api.add_resource(UserSignUp, '/signup')
api.add_resource(UserLogin, '/login')
api.add_resource(RedirectURL, '/<path:short_url>')
api.add_resource(AllURLs, '/')



if __name__ == '__main__':
    app.run(debug=True)
