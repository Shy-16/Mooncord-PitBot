'use strict';

document.addEventListener("DOMContentLoaded", function(event) {

	init_lightense();
	document.querySelector('.chat').scrollTo(0, document.querySelector('.chat').scrollHeight);

	// Delete ticket Modal
	document.querySelector('#reopen-ticket-button').onclick = function(ev) {
		this.disabled = true;
		this.classList.add("disabled");
		this.innerHTML = '<div class="spinner-border spinner-border-sm text-white" role="status"></div> Reopening';
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