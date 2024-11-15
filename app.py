from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# Prevent Flask jsonify from sorting the data
app.json.sort_keys = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
db = SQLAlchemy()
db.init_app(app)


class User(db.Model):
	pk = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(80), nullable=False)
	is_active = db.Column(db.Boolean)
	created_at = db.Column(db.DateTime, default=datetime.now())
	
	def __repr__(self):
		return "<User %r>"
	
	def to_dict(self):
		return {
			'pk': self.pk,
			'name': self.name,
			'email': self.email,
			'is_active': self.is_active,
			'created_at': self.created_at
		}
	
	
with app.app_context():
	db.create_all()
	

@app.route('/')
def home():
	return render_template('home.html')


@app.get('/users/')
def get_users():
	users = User.query.all()
	users_list = [user.to_dict() for user in users]
	return jsonify(users_list)


@app.get('/users/<int:pk>')
def get_user(pk):
	user = User.query.get(pk)
	if not user:
		return jsonify({"message": "user not found"}), 404
	return jsonify(user.to_dict())


@app.post('/users/')
def create_user():
	data = request.get_json()
	payload = User(
		name=data.get('name'),
		email=data.get('email'),
		password=data.get('password'),
		is_active=data.get('is_active'))
	if not data.get('name') or not data.get('email') or not data.get('password'):
		return jsonify({"error": "all fields are required"}), 400
	db.session.add(payload)
	try:
		db.session.commit()
		return jsonify(payload.to_dict()), 201
	except IntegrityError:
		db.session.rollback()
		return {"message": "duplicate user id found"}, 409


@app.patch('/users/<int:pk>')
def update_user(pk):
	user = User.query.get(pk)
	if not user:
		return jsonify({"message": "user not found"}), 404
	data = request.get_json()
	if 'name' in data:
		user.name = data.get('name')
	if 'email' in data:
		user.email = data.get('email')
	if 'password' in data:
		user.password = data.get('password')
	if 'is_active' in data:
		user.is_active = data.get('is_active')
	db.session.commit()
	return jsonify(user.to_dict())


@app.delete('/users/<int:pk>')
def delete_user(pk):
	user = User.query.get(pk)
	if not user:
		return jsonify({"message": "user not found"}), 404
	try:
		db.session.delete(user)
		db.session.commit()
		return jsonify({"message": "user deleted successfully!"}), 204
	except Exception as e:
		return jsonify({'error': 'An error occurred: {}'.format(e)}), 500


if __name__ == '__main__':
	app.run()
