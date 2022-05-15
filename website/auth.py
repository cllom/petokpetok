from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Board, User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')

		user = User.query.filter_by(email=email).first()
		if user:
			if check_password_hash(user.password, password):
				flash("Logged in successfully", category='success')
				login_user(user, remember=True)
				return redirect(url_for('views.home'))
			else:
				flash("Incorrect password, try again", category='error')
		else:
			flash("Email does not exist", category='error')
	# data = request.form
	# print(data) # Debug
	return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
	# return "<p>Logout</p>"
	logout_user()
	return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
	if request.method == 'POST':
		email = request.form.get('email')
		firstName = request.form.get('firstName')
		password1 = request.form.get('password1')
		password2 = request.form.get('password1')

		user = User.query.filter_by(email=email).first()

		if user:
			flash("This email already exists", category='error')
		elif len(email) < 4:
			flash("Email must be greater than 3 characters.", category='error')
		elif len(firstName) < 2:
			flash("First name must be greater than 2 characters.", category='error')
		elif password1 != password2:
			flash("Passwords do not match.", category='error')
		elif len(password1) < 6:
			flash("Passwords need to be atleast 6 characters long.", category='error')
		else:
			new_user = User(email=email, firstName=firstName, password=generate_password_hash(password1, method='sha256'))
			db.session.add(new_user)
			db.session.commit()
			
			new_board = Board(userID=new_user.id, url=new_user.firstName.lower())
			db.session.add(new_board)
			db.session.commit()
			# upload2s3()
			flash("Account created!", category='success')
			return redirect(url_for('auth.login'))

	return render_template("signup.html", user=current_user)

