function deleteNote(noteID) {
	fetch('/delete-note', {
		method: 'POST',
		body: JSON.stringify({ noteID: noteID}),
	}).then((_res) => {
		window.location.href = '/edit';
	});
}

function deleteBoardNote(noteID, board) {
	fetch('/delete-note', {
		method: 'POST',
		body: JSON.stringify({ noteID: noteID}),
	}).then((_res) => {
		window.location.href = `/${board}/edit`;
	});
}

function readURL(input) {
	if (input.files && input.files[0]) {
			var reader = new FileReader();

			reader.onload = function (e) {
					$('#img-preview')
							.attr('src', e.target.result);
			};
			var preview = document.getElementById("img-preview");
    	// preview.src = src;
    	// preview.style.display = "flex";
    	preview.style.width = "100px";
    	preview.style.visibility = "visible";

			reader.readAsDataURL(input.files[0]);
	}
}