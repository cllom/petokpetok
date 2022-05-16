from base64 import b64encode
import io
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, current_user
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
from .models import Board, Note, User
from . import db
import json
from PIL import Image
# from os import path

views = Blueprint('views', __name__)

@views.route('/')
def home():
	query = Note.query.filter_by(boardName=None).order_by(db.desc(Note.date)).all()
	# print(query)
	return render_template("board.html", user=current_user, query=query)

@views.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
	if request.method == 'POST':
		note = request.form.get('note')
		img = request.files.get('image-upload')
		data = request.files['image-upload'].read()
		# print(img.filename, data) # Debug

		# Note content needs to be longer than 1 character
		if len(note) < 1:
			flash("Note too short", category='error')
		else:
		# If no image, continue
			if img.filename == '':
				new_note = Note(data=note, userID=current_user.id, userName=current_user.firstName)
			else:
				# print("adding image") # debug
				dataPIL = Image.open(io.BytesIO(data))
				w, h = dataPIL.size
				resized_width = 624
				resized_height = int((resized_width / w) *h)
				dataPIL = dataPIL.resize((resized_width, resized_height), Image.NEAREST)
				buffered = io.BytesIO()
				dataPIL.save(buffered, format="PNG")
				buffered.seek(0)

				base64Img = b64encode(buffered.read()).decode("ascii")
				new_note = Note(data=note, userID=current_user.id, img=base64Img, userName=current_user.firstName)
				
			db.session.add(new_note)
			db.session.commit()
			flash("Note added successfully", category='success')
			# upload2s3()

	return render_template("home.html", user=current_user, board=None)

@views.route('/delete-note', methods=['POST'])
def delete_note():
	data = json.loads(request.data)
	noteID = data['noteID']
	note = Note.query.get(noteID)
	if note:
		if note.userID == current_user.id:
			db.session.delete(note)
			db.session.commit()
			# upload2s3()
			return jsonify({})
	pass

@views.route('/about')
def about():
	return render_template("about.html", user=current_user)

@views.route('/services')
def services():
	return render_template("services.html", user=current_user)

@views.route('/users')
def users():
	return render_template("users.html", user=current_user)

############################################################################
# USER #

@views.route('/<string:boardName>')
@login_required
def userBoard(boardName):
	print(boardName)
	# userID = User.query.filter_by(firstName=userName).first().id
	currBoard = Board.query.filter_by(url=boardName, userID=current_user.id).first()
	# print(current_user.boards, currBoard, boardName)
	if currBoard in current_user.boards:
		print("One step closer")
		query = Note.query.filter_by(boardName=boardName).order_by(db.desc(Note.date)).all()
		print(query)
		return render_template("userBoard.html", user=current_user, query=query, boardName=boardName)
	else:
		flash("You do not have access to view", category="error")
		# return ("OOPS! You do not have access to view!")
		return redirect(url_for('views.home'))
	# 	return redirect(url_for('views.home'))

@views.route('/<boardName>/edit', methods=['GET', 'POST'])
@login_required
def boardEdit(boardName):
	# userID = User.query.filter_by(firstName=userName).first().id
	currBoard = Board.query.filter_by(url=boardName, userID=current_user.id).first()
	if currBoard in current_user.boards:
		if request.method == 'POST':
			note = request.form.get('note')
			img = request.files.get('image-upload')
			data = request.files['image-upload'].read()
			# print(img.filename, data) # Debug

			# Note content needs to be longer than 1 character
			if len(note) < 1:
				flash("Note too short", category='error')
			else:
			# If no image, continue
				if img.filename == '':
					new_note = Note(data=note, userID=current_user.id, userName=current_user.firstName, boardName=boardName)
				else:
					# print("adding image") # debug
					dataPIL = Image.open(io.BytesIO(data))
					if dataPIL.mode in ("RGBA", "P"): 
						dataPIL = dataPIL.convert("RGB")
					w, h = dataPIL.size
					resized_width = 624
					resized_height = int((resized_width / w) *h)
					dataPIL = dataPIL.resize((resized_width, resized_height), Image.NEAREST)
					buffered = io.BytesIO()
					dataPIL.save(buffered, format="JPEG")
					buffered.seek(0)

					base64Img = b64encode(buffered.read()).decode("ascii")
					new_note = Note(data=note, userID=current_user.id, img=base64Img, userName=current_user.firstName, boardName=currBoard.url)
					
				db.session.add(new_note)
				db.session.commit()
				flash("Note added successfully", category='success')
				# upload2s3()

		return render_template("home.html", user=current_user, board=currBoard.url)

	else:
		flash(f"You do not have access to {boardName}", category="error")
		return redirect(url_for('views.edit'))

@views.route('/join-board', methods=['GET', 'POST'])
@login_required
def join_board():
	if request.method == 'POST':
		boardName = request.form.get('boardName')
		# userName = request.form.get('userName')
		print(f"Received: {boardName}")
		boardExists = Board.query.filter_by(url=boardName).first()
		userinBoard = Board.query.filter_by(url=boardName, userID=current_user.id).first()
		print(userinBoard)
		if boardExists and not userinBoard:
			# print(current_user.boards.query.filter_)
			new_board = Board(userID=current_user.id, url=boardName)
			db.session.add(new_board)
			db.session.commit()
			flash(f"Successfully added you to {boardName}", category='success')
		elif userinBoard:
			flash(f"You are already signed up to this board", category='error')
			return redirect(url_for('views.userBoard', boardName=boardName))
		else:
			flash(f"{boardName} does not exist", category='error')
		

	return render_template("join_board.html", user=current_user)
	# userID = User.query.filter_by(firstName=userName).first().id
	# currBoard = Board.query.filter_by(url=boardName, userID=userID).first()
	# print(current_user.boards, currBoard)
	# if currBoard in current_user.boards:
	# 	print("Add users here")
	# 	query = User.query.filter_by(boards=currBoard).all()
	# 	print(query)
	# 	return render_template("userBoard.html", user=current_user, query=query, boardName=boardName)
	# else:
	# 	flash("You do not have access to view", category="error")
	# 	return ("OOPS! You do not have access to view!")
	# 	# return redirect(url_for('views.home'))

@views.route('/create', methods=['POST'])
@login_required
def create():
	boardName = request.form.get('boardName')
	# Check if boardName already exists
	boardExists = Board.query.filter_by(url=boardName).first()
	print(boardExists)
	if boardExists:
		flash("This board name already exists", category='error')
	else:
		new_board = Board(userID=current_user.id, url=boardName)
		db.session.add(new_board)
		db.session.commit()
		flash("New board created!", category='success')
	# bDatabase = f'{current_user.firstName}_{boardName}.db'
		return redirect(url_for('views.boardEdit', boardName=boardName))
	return redirect(url_for('views.join_board'))
	print(boardName)

	# return f"Cannot create with {boardName}"






@views.route('/test')
def test_all():
	return render_template("test_all.html", user=current_user)