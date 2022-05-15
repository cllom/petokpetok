from base64 import b64encode
import io
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .models import Board, Note, User
from . import db
import json
from PIL import Image
from os import path

views = Blueprint('views', __name__)

@views.route('/')
def home():
	query = Note.query.filter_by(boardID=None).order_by(db.desc(Note.date)).all()
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

####################
# USER #
@views.route('/<userName>/<boardName>')
@login_required
def userBoard(userName, boardName):
	userID = User.query.filter_by(firstName=userName).first().id
	currBoard = Board.query.filter_by(url=boardName, userID=userID).first()
	print(current_user.boards, currBoard)
	if currBoard in current_user.boards:
		print("One step closer")
		query = Note.query.filter_by(boardID=currBoard.id).order_by(db.desc(Note.date)).all()
		print(query)
		return render_template("userBoard.html", user=current_user, query=query, boardName=boardName)
	else:
		flash("You do not have access to view", category="error")
		return ("OOPS! You do not have access to view!")
		# return redirect(url_for('views.home'))

	# if userName == current_user.firstName:
	# 	bDatabase = f'{current_user.firstName}_{boardName}.db'
	# 	print(bDatabase)
	# 	if path.exists('website/' + bDatabase):
	# 		print("true")
	# 		engine = create_engine(f'sqlite:///{bDatabase}')
	# 		session = Session(engine)
	# 		try:
	# 			query = session.query(Note).order_by(db.desc(Note.date)).all()
	# 		finally:
	# 			session.close
	# 		return render_template("userBoard.html", user=current_user, query=query)
	# 	else:
	# 		return ("OOPS!")
	# else:
	# 	flash("You do not have access to view", category="error")
	# 	return redirect(url_for('views.home'))

@views.route('/<userName>/<boardName>/edit', methods=['GET', 'POST'])
@login_required
def boardEdit(userName, boardName):
	userID = User.query.filter_by(firstName=userName).first().id
	currBoard = Board.query.filter_by(url=boardName, userID=userID).first()
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
					new_note = Note(data=note, userID=current_user.id, userName=current_user.firstName, boardID=currBoard.id)
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
					new_note = Note(data=note, userID=current_user.id, img=base64Img, userName=current_user.firstName, boardID=currBoard.id)
					
				db.session.add(new_note)
				db.session.commit()
				flash("Note added successfully", category='success')
				# upload2s3()
		# print(f"currBoard.id : {currBoard.id}")
		# for note in current_user.notes:
		# 	print(type(note.boardID), type(currBoard.id))
		# 	if note.boardID == currBoard.id:
		# 		print(note.data)
		return render_template("home.html", user=current_user, board=currBoard.id)

	else:
		flash(f"You do not have access to {userName}/{boardName}", category="error")
		return redirect(url_for('views.edit'))



@views.route('/create', methods=['POST'])
@login_required
def create():
	boardName = request.form.get('boardName')
	# Check if boardName already exists
	new_board = Board(userID=current_user.id, url=boardName)
	db.session.add(new_board)
	db.session.commit()
	flash("New board created!", category='success')
	# bDatabase = f'{current_user.firstName}_{boardName}.db'
	print(boardName)
	# if not path.exists('website/' + bDatabase):
	# 	engine = create_engine(f'sqlite:///website/{bDatabase}')
	# 	# engine.connect()
	# 	db.create_all(engine)
	return redirect(url_for('views.edit'))
	# return f"Cannot create with {boardName}"






@views.route('/test')
def test_all():
	return render_template("test_all.html", user=current_user)