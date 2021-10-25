'use strict';

document.addEventListener("DOMContentLoaded", function(event) {

	init_lightense();
	document.querySelector('.chat').scrollTo(0, document.querySelector('.chat').scrollHeight);
	document.querySelectorAll('.message-content').forEach((el, index) => {
		el.innerHTML = review_channel_link(el.innerHTML);
	});

	// Socket functionality for chat
	let ticket_id = document.querySelector('#ticket-id').value;
	let user_id = document.querySelector('#session_id').value;
	let socket = io('/feed');

	socket.on('connect', function() {
		socket.emit('connected', {'ticket_id': ticket_id});
	});

	socket.on('connected', function(data) {
		let template = '<div class="chat-notif">' + data.message + '</div>';

		document.querySelector('.chat-send-input').insertAdjacentHTML( 'beforebegin', template );
	});

	socket.on('dm_message', function(data) {
		add_chat_message(data, data.sender);
	});

	document.querySelector('#send-message-input').onkeypress = function(event) {
		if(event.key == "Enter" && !event.shiftKey){
			event.preventDefault();
			const formData = new FormData();
			const fileField = document.querySelector('input[type="file"]');

			formData.append('user_id', document.querySelector('#session_id').value);
			formData.append('channel_id', document.querySelector('#channel-id').value);
			formData.append('message', this.value);
			formData.append('attachment', document.querySelector('#message-attachment').files[0]);

			fetch(`/modmail/tickets/${ticket_id}/new_message`, {
			  method: 'POST',
			  body: formData
			})
			.then(response => response.json())
			.then(result => {
				console.log(result);
			  	add_chat_message(result.data, result.data.sender);
			})
			.catch(error => {
			  console.error('Error:', error);
			});

			this.value = '';
			document.querySelector('#message-attachment').value = '';
			while (document.querySelector('.chat-send-attachments').firstChild) {
		        document.querySelector('.chat-send-attachments').removeChild(document.querySelector('.chat-send-attachments').firstChild);
		    }
		}
	};

	document.addEventListener("keydown", function onPress(event) {
	    if (event.key === "Escape") {
	        document.querySelector('#message-attachment').value = '';
			while (document.querySelector('.chat-send-attachments').firstChild) {
		        document.querySelector('.chat-send-attachments').removeChild(document.querySelector('.chat-send-attachments').firstChild);
		    }
	    }
	});

	document.querySelector('body').ondragenter = function(ev) {
		document.querySelector('#drop_zone').classList.remove('d-none');
	};

	document.querySelector('#drop_zone').ondragleave = function(ev) {
		document.querySelector('#drop_zone').classList.add('d-none');
	};

	document.querySelector('#drop_zone').ondragover = function(ev) {
		ev.preventDefault();
	}

	document.querySelector('#drop_zone').ondrop = function(ev){
		// Prevent default behavior (Prevent file from being opened)
		ev.preventDefault();

		let file = undefined;

		// Use DataTransfer interface to access the file(s)
		document.querySelector('#message-attachment').files = ev.dataTransfer.files;
		for (var i = 0; i < ev.dataTransfer.files.length; i++) {
			file = ev.dataTransfer.files[i];
		}

		if (FileReader && file) {
	        var fr = new FileReader();
	        var sourceImage = document.createElement('img');
	        fr.onload = function () {
	            sourceImage.src = fr.result;
	        }
	        fr.readAsDataURL(file);

	        while (document.querySelector('.chat-send-attachments').firstChild) {
		        document.querySelector('.chat-send-attachments').removeChild(document.querySelector('.chat-send-attachments').firstChild);
		    }
	        document.querySelector('.chat-send-attachments').appendChild(sourceImage);
	    }

		document.querySelector('#drop_zone').classList.add('d-none');
		document.querySelector('#send-message-input').focus();
	};

	// window.addEventListener('paste', ... or
	document.onpaste = function(event){
		var items = (event.clipboardData || event.originalEvent.clipboardData).items;
		for (var index in items) {
			var item = items[index];
			if (item.kind === 'file') {
				var file = item.getAsFile();
				var fr = new FileReader();
				var sourceImage = document.createElement('img');
					fr.onload = function () {
		            sourceImage.src = fr.result;
		        }
		        fr.readAsDataURL(file);

		        while (document.querySelector('.chat-send-attachments').firstChild) {
			        document.querySelector('.chat-send-attachments').removeChild(document.querySelector('.chat-send-attachments').firstChild);
			    }
		        document.querySelector('.chat-send-attachments').appendChild(sourceImage);
			}
		}
	};

	// Close ticket Modal
	document.querySelector('#submit-close-ticket-button').onclick = function(ev) {
		ev.preventDefault();
		this.disabled = true;
		this.classList.add("disabled");
		this.innerHTML = '<div class="spinner-border spinner-border-sm text-white" role="status"></div> Closing';
		document.querySelector('#close-ticket-form').submit();
	};

	// Delete ticket Modal
	document.querySelector('#submit-delete-ticket-button').onclick = function(ev) {
		this.disabled = true;
		this.classList.add("disabled");
		this.innerHTML = '<div class="spinner-border spinner-border-sm text-white" role="status"></div> Deleting';
		document.querySelector('#delete-ticket-form').submit();
	};

});

function init_lightense() {
	// Add Ligentese on all images
	Lightense('img:not(.no-lightense),img:not(.user-avatar),.lightense', {
		beforeShow(config) {
			var sourceImage = document.createElement('img');
			sourceImage.src = config.target.src;
			sourceImage.dataset.background = config.target.dataset.background;
			document.querySelector(".lightense-backdrop").appendChild(sourceImage);
			config.target = sourceImage;
		},
		afterHide(config) {
			let sourceImage = config.target;
			setTimeout(function(){ document.querySelector(".lightense-backdrop").removeChild(sourceImage); }, 500);
		}
     });
};

function add_chat_message(data, sender){
	const user_id = data.user_id;
	const username = data.user.username;
	const handle = data.user.username_handle;
	const avatar_url = _build_avatar_url(user_id, data.user.avatar);

	let post_time = new Date(data.created_date).toLocaleString();
	let attachments = '';
	if(data.attachments.length > 0){
		attachments = '<div class="message-attachments">';
		data.attachments.forEach((el, i) => { 
			attachments += '<img src="'+ el.url + '" data-background="rgba(33, 33, 33, .7)" />';
		});
		attachments += '</div>';
	}

	let parsed_message = data.message.replaceAll("\n", "<br>");
	parsed_message = review_channel_link(parsed_message);
	

	let template = `<div class="chat-message ${sender}">\
						<div class="message-user user-id" data-id="${user_id}">\
							<img src="${avatar_url}" width="32" class="img-responsive user-avatar" />\
							${username}#${handle}\
						</div>\
						<div class="message-time">${post_time}</div>\
						<div class="message-content">${parsed_message}</div>\
						${attachments}
					</div>`;

	document.querySelector('.chat-send-input').insertAdjacentHTML( 'beforebegin', template );
	init_lightense();
}

function review_channel_link(message){
	let re = /https:\/\/discord.com\/channels\/.+/;
	let matches = message.match(re);

	if(matches){
		const matched = matches[0];
		message = message.replace(re, `<a href="discord://${matched}">${matched}</a>`)
	}

	return message;
}

function _build_avatar_url(user_id, avatar){
	return `https://cdn.discordapp.com/avatars/${user_id}/${avatar}.png?size=4096`;
}