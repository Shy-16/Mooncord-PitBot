'use strict';

document.addEventListener("DOMContentLoaded", function(event) {

	// Delete ticket Modal
	document.querySelector('#filter-input').onchange = function(ev) {
		this.form.submit();
	};

});