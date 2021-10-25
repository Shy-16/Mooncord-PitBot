let floating_notifs = [];


function add_notif(msg, type) {
	let index = floating_notifs.length;
	template = '<div class="floating-notification floating-notification--enter ' + type + ' + floating-' + index + '">\
					' + msg + '\
					<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>\
		    	</div>';

	document.getElementById('floating-container').insertAdjacentHTML( 'beforeend', template );
	floating_notifs.push(template);

	setTimeout(() => {
		document.querySelector('.floating-' + index).classList.remove('floating-notification--enter');
	}, 500);

	setTimeout(() => {
		document.querySelector('.floating-' + index).classList.add('floating-notification--leave');
	}, 3000);

	setTimeout(() => {
		document.querySelector('.floating-' + index).remove();
	}, 3500);
}