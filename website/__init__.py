from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import boto3
import botocore


db = SQLAlchemy()
DB_NAME = "tania.db"
# DB_NAME = "database_with_imgTEXT.db"

s3_resource = boto3.resource('s3')


def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'hshsh kaldklakdal12'
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
	db.init_app(app)

	from .views import views
	from .auth import auth

	app.register_blueprint(views, url_prefix='/')
	app.register_blueprint(auth, url_prefix='/')

	from .models import User, Note

	create_database(app)

	
	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(id):
		return User.query.get(int(id))
		 
	return app


def create_database(app):
	"""
	# The object does not exist.
	if not path.exists('website/' + DB_NAME):
		db.create_all(app=app)
		print("Created database")

	"""
	try:
		print("checking S3")
		s3_resource.Object('social-media-data-base', DB_NAME).load()
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Code'] == "404":
			print("caught error")
			# The object does not exist.
			if not path.exists('website/' + DB_NAME):
				db.create_all(app=app)
				print("Created database")
				upload2s3()
		#else:
			# Something else has gone wrong.
		#	raise
	else:
		# The object does exist.
		s3_resource.Object('social-media-data-base', DB_NAME).download_file(f'website/{DB_NAME}')
		print("Downloaded db from S3")
	



def upload2s3():
	s3_resource.Bucket('social-media-data-base').upload_file(Filename='website/' + DB_NAME, Key=DB_NAME)
	print("Updated db in S3")
