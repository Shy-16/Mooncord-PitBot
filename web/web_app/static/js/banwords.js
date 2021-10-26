'use strict';

document.addEventListener("DOMContentLoaded", function(event) {

	const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
	const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
		return new bootstrap.Tooltip(tooltipTriggerEl)
	});

	const createModalInstance = bootstrap.Modal.getOrCreateInstance(document.querySelector("#create-banword-modal"));
	const editModalInstance = bootstrap.Modal.getOrCreateInstance(document.querySelector("#edit-banword-modal"));
	let deleteConfirm = false;

	const createSlider = document.getElementById("create-range");
	const editSlider = document.getElementById("edit-range");

	// Update the current slider value (each time you drag the slider handle)
	createSlider.oninput = function() {
		document.querySelector("#create-range-value").innerHTML = this.value;
	};

	editSlider.oninput = function() {
		document.querySelector("#edit-range-value").innerHTML = this.value;
	};

	function onClickEditButton(ev){
		ev.preventDefault();

		const banword_id = this.dataset.id;

		fetch(`/banwords/${banword_id}`, {
		  headers: {
		    'Accept': 'application/json'
		  },
		  method: 'GET'
		})
		.then(response => response.json())
		.then(result => {
			editModalInstance.show();

			document.querySelector("#edit-banword-id").value = result['_id'];
			document.querySelector("#edit-banword-word").value = result['word'];
			let {duration, type} = secondsToFormData(result['duration']);
			document.querySelector("#edit-banword-time").value = duration;
			document.querySelector("#edit-banword-duration").value = type;
			document.querySelector("#edit-range-value").innerHTML = result['strength'];
			document.querySelector("#edit-range").value = result['strength'];
			
			document.querySelector("#edit-temporary").checked = result['temporary_ban'];
			document.querySelector("#edit-permanent").checked = result['permanent_ban'];
			document.querySelector("#edit-delete").checked = result['delete_message'];
			document.querySelector("#edit-variable").checked = result['variable_time'];
			document.querySelector("#edit-include").checked = result['include_link'];
		})
		.catch(error => {
			console.error('Error:', error);
			add_notif('There was an error fetching the banword.', 'danger');
		});
	};

	function onStatusChange(ev){
		const banword_id = this.dataset.id;

		fetch(`/banwords/${banword_id}`, {
		  headers: {
		    'Accept': 'application/json',
		    'Content-Type': 'application/json'
		  },
		  method: 'PUT',
		  body: JSON.stringify({'active': this.checked})
		})
		.then(response => response.json())
		.then(result => {
			add_notif('Status updated successfully.', 'success');
		})
		.catch(error => {
			console.error('Error:', error);
			add_notif('There was an error updating the banword status.', 'danger');
		});
	}

	document.querySelector("#create-banword-button").onclick = function(ev){
		ev.preventDefault();

		const button = this;
		button.disabled = true;
		button.classList.add("disabled");
		button.innerHTML = '<div class="spinner-border spinner-border-sm text-white" role="status"></div> Creating';

		const form_data = new FormData(document.querySelector("#create-banword-form"));
		const banword = new Object();

		for (var [key, value] of form_data.entries()) {
			banword[key] = value;
		}

		document.querySelector("#create-banword-form").querySelectorAll("input[type='checkbox']").forEach((el, i) => {
			banword[el.name] = el.checked;
		});

		if(!banword.word || banword.word == ''){
			document.querySelector("#create-banword-word").classList.add("is-invalid");
			button.disabled = false;
			button.classList.remove("disabled");
			button.innerHTML = 'Create';
			return;
		}
		document.querySelector("#create-banword-word").classList.remove("is-invalid");

		if(!banword.time || banword.time == ''){
			document.querySelector("#create-banword-time").classList.add("is-invalid");
			button.disabled = false;
			button.classList.remove("disabled");
			button.innerHTML = 'Create';
			return;
		}
		document.querySelector("#create-banword-time").classList.remove("is-invalid");

		banword['user_id'] = document.querySelector("#session_id").value;
		let duration = 0;
		const time = parseInt(banword['time']);

		switch(banword['duration']){
			case 'seconds':
				duration = time;
				break;
			case 'minutes':
				duration = time * 60;
				break;
			case 'hours':
				duration = time * 3600;
				break;
			case 'days':
				duration = time * 86400;
				break;
			default:
				duration = time * 3600;
				break;
		}

		delete banword.time;
		banword.duration = duration;
		banword.strength = parseInt(banword.strength);

		fetch(`/banwords`, {
		  headers: {
		    'Accept': 'application/json',
		    'Content-Type': 'application/json'
		  },
		  method: 'POST',
		  body: JSON.stringify(banword)
		})
		.then(response => response.json())
		.then(result => {
			createBanword(result);
			document.querySelector(`button[data-id='${result['_id']}']`).onclick = onClickEditButton;
			document.querySelector(`input[data-id='${result['_id']}']`).onclick = onStatusChange;

			button.disabled = false;
			button.classList.remove("disabled");
			button.innerHTML = 'Create';
			createModalInstance.hide();
			document.querySelector("#create-banword-form").reset();
			add_notif('Banword created successfully.', 'success');
		})
		.catch(error => {
			console.error('Error:', error);
			button.disabled = false;
			button.classList.remove("disabled");
			button.innerHTML = 'Create';
			createModalInstance.hide();
			add_notif('There was an error creating the banword.', 'danger');
		});
	};

	document.querySelectorAll(".edit-banword").forEach(item => {
		item.onclick = onClickEditButton
	});

	document.querySelector("#edit-banword-button").onclick = function(ev){
		ev.preventDefault();

		const button = this;
		button.disabled = true;
		button.classList.add("disabled");
		button.innerHTML = '<div class="spinner-border spinner-border-sm text-white" role="status"></div> Saving';

		const banword_id = document.querySelector("#edit-banword-id").value;

		const form_data = new FormData(document.querySelector("#edit-banword-form"));
		const banword = new Object();

		for (var [key, value] of form_data.entries()) {
			banword[key] = value;
		}

		document.querySelector("#edit-banword-form").querySelectorAll("input[type='checkbox']").forEach((el, i) => {
			banword[el.name] = el.checked;
		});

		if(!banword.word || banword.word == ''){
			document.querySelector("#edit-banword-word").classList.add("is-invalid");
			button.disabled = false;
			button.classList.remove("disabled");
			button.innerHTML = 'Create';
			return;
		}
		document.querySelector("#edit-banword-word").classList.remove("is-invalid");

		if(!banword.time || banword.time == ''){
			document.querySelector("#edit-banword-time").classList.add("is-invalid");
			button.disabled = false;
			button.classList.remove("disabled");
			button.innerHTML = 'Create';
			return;
		}
		document.querySelector("#edit-banword-time").classList.remove("is-invalid");

		let duration = 0;
		const time = parseInt(banword['time']);

		switch(banword['duration']){
			case 'seconds':
				duration = time;
				break;
			case 'minutes':
				duration = time * 60;
				break;
			case 'hours':
				duration = time * 3600;
				break;
			case 'days':
				duration = time * 86400;
				break;
			default:
				duration = time * 3600;
				break;
		}

		delete banword.time;
		banword.duration = duration;
		banword.strength = parseInt(banword.strength);

		fetch(`/banwords/${banword_id}`, {
		  headers: {
		    'Accept': 'application/json',
		    'Content-Type': 'application/json'
		  },
		  method: 'PUT',
		  body: JSON.stringify(banword)
		})
		.then(response => response.json())
		.then(result => {
			updateBanword(result);
			document.querySelector(`button[data-id='${result['_id']}']`).onclick = onClickEditButton;
			document.querySelector(`input[data-id='${result['_id']}']`).onclick = onStatusChange;

			button.disabled = false;
			button.classList.remove("disabled");
			button.innerHTML = 'Save';
			editModalInstance.hide();
			document.querySelector("#edit-banword-form").reset();
			add_notif('Banword updated successfully.', 'success');
		})
		.catch(error => {
			console.error('Error:', error);
			button.disabled = false;
			button.classList.remove("disabled");
			button.innerHTML = 'Save';
			editModalInstance.hide();
			add_notif('There was an error creating the banword.', 'danger');
		});
	};

	document.querySelectorAll("input[name='status']").forEach(item => {
		item.onclick = onStatusChange
	});

	document.querySelector("#delete-banword-button").onclick = function(ev){
		ev.preventDefault();

		const button = this;

		if(!deleteConfirm){
			button.innerHTML = 'Are you sure?';
			deleteConfirm = true;
			return;
		}

		const banword_id = document.querySelector("#edit-banword-id").value;
		button.innerHTML = '<div class="spinner-border spinner-border-sm text-white" role="status"></div> Deleting';
		deleteConfirm = false;

		fetch(`/banwords/${banword_id}`, {
		  headers: {
		    'Accept': 'application/json'
		  },
		  method: 'DELETE'
		})
		.then(response => response.json())
		.then(result => {
			document.querySelector(`button[data-id='${banword_id}']`).parentElement.parentElement.remove();
			button.innerHTML = 'Delete';
			editModalInstance.hide();
			add_notif('Banword deleted successfully.', 'success');
		})
		.catch(error => {
			console.error('Error:', error);
			editModalInstance.hide();
			button.innerHTML = 'Delete';
			add_notif('There was an error deleting the banword.', 'danger');
		});
	};

	document.querySelector("input[name='status']").change = onStatusChange;

});

function secondsToHms(t) {
    t = Number(t);

    var d = Math.floor(t / 86400);
    var h = Math.floor(t / 3600);
    var m = Math.floor(t % 3600 / 60);
    var s = Math.floor(t % 3600 % 60);

    var dDisplay = d > 0 ? d + (d == 1 ? " day" : " days") : "";
    var hDisplay = (h > 0 && h < 24) ? h + (h == 1 ? " hour" : " hours") : "";
    var mDisplay = m > 0 ? m + (m == 1 ? " minute" : " minutes") : "";
    var sDisplay = s > 0 ? s + (s == 1 ? " second" : " seconds") : "";
    return dDisplay + hDisplay + mDisplay + sDisplay; 
}

function secondsToFormData(t) {
    t = Number(t);

    var d = Math.floor(t / 86400);
    var h = Math.floor(t / 3600);
    var m = Math.floor(t % 3600 / 60);
    var s = Math.floor(t % 3600 % 60);

    if(d > 0) return {duration: d, type: 'days'};
    if(h > 0) return {duration: h, type: 'hours'};
    if(m > 0) return {duration: m, type: 'minutes'};
    return {duration: s, type: 'seconds'};
}

function createBanword(data){

	const duration = secondsToHms(data['duration']);

	let template = `<div class="col-3 banword">
			<div class="banword-title-row">
				<h4>${data["word"]}</h4>

				<label class="switch-small ml-auto">
					<input type="checkbox" name="status" checked data-id="${data['_id']}" />
					<span class="slider round"></span>
				</label>

				<label class="timeout-info">${duration} timeout</label>
				<label class="strictness">${data['strength']}% strict</label>
			</div>

			<div class="banword-options-row mt-3">
				<i class="bi bi-link-45deg ${data['include_link'] == true ? "text-primary" : "text-muted"}" data-bs-toggle="tooltip" data-bs-placement="top" title="Include links"></i>&emsp;
				<i class="bi bi-trash ${data['delete_message'] == true ? "text-success" : "text-muted"}" data-bs-toggle="tooltip" data-bs-placement="top" title="Delete message"></i>&emsp;
				<i class="bi bi-clock ${data['variable_time'] == true ? "text-success" : "text-muted"}" data-bs-toggle="tooltip" data-bs-placement="top" title="Variable time"></i>&emsp;
				<i class="bi bi-calendar3 ${data['temporary_ban'] == true ? "text-success" : "text-muted"}" data-bs-toggle="tooltip" data-bs-placement="top" title="Temporary ban"></i>&emsp;
				<i class="bi bi-calendar2-x ${data['permanent_ban'] == true ? "text-success" : "text-muted"}" data-bs-toggle="tooltip" data-bs-placement="top" title="Permanent ban"></i>
			

				<button type="button" class="btn btn-link btn-sm float-end py-0 edit-banword" data-bs-toggle="tooltip" data-bs-placement="top" title="Edit" data-id="${data['_id']}">
					<i class="bi bi-pencil-fill"></i>
				</button>
			</div>
		</div>`;

	document.querySelector("#banwords-container").insertAdjacentHTML("beforeend", template);
};

function updateBanword(data){

	const duration = secondsToHms(data['duration']);

	let template = `<div class="col-3 banword">
			<div class="banword-title-row">
				<h4>${data["word"]}</h4>

				<label class="switch-small ml-auto">
					<input type="checkbox" name="status" checked data-id="${data['_id']}" />
					<span class="slider round"></span>
				</label>

				<label class="timeout-info">${duration} timeout</label>
				<label class="strictness">${data['strength']}% strict</label>
			</div>

			<div class="banword-options-row mt-3">
				<i class="bi bi-link-45deg ${data['include_link'] == true ? "text-primary" : "text-muted"}" data-bs-toggle="tooltip" data-bs-placement="top" title="Include links"></i>&emsp;
				<i class="bi bi-trash ${data['delete_message'] == true ? "text-success" : "text-muted"}" data-bs-toggle="tooltip" data-bs-placement="top" title="Delete message"></i>&emsp;
				<i class="bi bi-clock ${data['variable_time'] == true ? "text-success" : "text-muted"}" data-bs-toggle="tooltip" data-bs-placement="top" title="Variable time"></i>&emsp;
				<i class="bi bi-calendar3 ${data['temporary_ban'] == true ? "text-success" : "text-muted"}" data-bs-toggle="tooltip" data-bs-placement="top" title="Temporary ban"></i>&emsp;
				<i class="bi bi-calendar2-x ${data['permanent_ban'] == true ? "text-success" : "text-muted"}" data-bs-toggle="tooltip" data-bs-placement="top" title="Permanent ban"></i>				

				<button type="button" class="btn btn-link btn-sm float-end py-0 edit-banword" data-bs-toggle="tooltip" data-bs-placement="top" title="Edit" data-id="${data['_id']}">
					<i class="bi bi-pencil-fill"></i>
				</button>
			</div>
		</div>`;

	const parent = document.querySelector(`button[data-id='${data['_id']}']`).parentElement.parentElement;
	parent.insertAdjacentHTML("afterend", template);
	parent.remove();
};