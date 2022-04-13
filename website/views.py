from base64 import b64encode
import io
from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from PIL import Image


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
	# return "<h1>Hello</h1>"
	if request.method == 'POST':
		note = request.form.get('note')
		img = request.files.get('image-upload')
		data = request.files['image-upload'].read()
		# print(img.filename, data)
		if len(note) < 1:
			flash("Note too short", category='error')
		else:
			if img.filename == '':
				new_note = Note(data=note, userID=current_user.id)
			else:
				print("adding image")
				dataPIL = Image.open(io.BytesIO(data))
				w, h = dataPIL.size
				resized_width = 624
				resized_height = (resized_width / w) *h
				dataPIL = dataPIL.resize((resized_width, resized_height), Image.NEAREST)
				# data = request.files['image-upload'].read()
				buffered = io.BytesIO()
				dataPIL.save(buffered, format="PNG")
				buffered.seek(0)

				base64Img = b64encode(buffered.read()).decode("ascii")
				# print(data)
				new_note = Note(data=note, userID=current_user.id, img=base64Img)
				
			db.session.add(new_note)
			db.session.commit()
			flash("Note added successfully", category='success')

	return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
	data = json.loads(request.data)
	noteID = data['noteID']
	note = Note.query.get(noteID)
	if note:
		if note.userID == current_user.id:
			db.session.delete(note)
			db.session.commit()
			return jsonify({})
	pass

@views.route('/common-board')
def common_board():
	query = Note.query.order_by(db.desc(Note.date)).all()
	# base64_images = [b64encode(image).decode("utf-8") for each.image in query]
	# # Debug print
	# for each in query: 
	# 	print(each.img)	
		# if each.img:
		# 	# print(each.img)
		# 	each.img = b64encode(each.img).decode("ascii")
		# 	# print(each.img)
	return render_template("board.html", user=current_user, query=query)
	pass