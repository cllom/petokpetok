from base64 import b64encode
import io
from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import login_required, current_user
from .models import Note
from . import db, upload2s3
import json
from PIL import Image


views = Blueprint('views', __name__)

ROWS_PER_PAGE = 5

@views.route('/')
def home():
	# Set the pagination configuration
	page = request.args.get('page', 1, type=int)
	#query = Note.query.order_by(db.desc(Note.date)).all()
	query = Note.query.order_by(db.desc(Note.date)).paginate(page=page, per_page=ROWS_PER_PAGE)
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
				resized_width = 1200
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
			upload2s3()

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
			upload2s3()
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