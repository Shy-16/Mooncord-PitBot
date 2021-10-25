document.addEventListener("DOMContentLoaded", function(event) {

	let strikes_data = document.getElementById('strikes-chart-data').value;
	strikes_data = JSON.parse(strikes_data);

	let strikeCtx = document.getElementById('strikes-chart').getContext('2d');
	let strikeChart = new Chart(strikeCtx, {
	    type: 'bar',
	    data: strikes_data,
	    options: {
	    	locale: 'en-US',
	    	responsive: true,
	    	maintainAspectRatio: false,
	        scales: {
	            y: {
	                beginAtZero: true
	            }
	        }
	    }
	});

	let aggregated_data = document.getElementById('aggregated-chart-data').value;
	aggregated_data = JSON.parse(aggregated_data);

	let aggregatedCtx = document.getElementById('aggregated-chart').getContext('2d');
	let aggregatedChart = new Chart(aggregatedCtx, {
	    type: 'bar',
	    data: aggregated_data,
	    options: {
	    	locale: 'en-US',
	    	responsive: true,
	    	maintainAspectRatio: false,
	        scales: {
	            y: {
	                beginAtZero: true
	            }
	        }
	    }
	});

	
	Array.from(document.getElementsByClassName('strike-item')).forEach((el, i) => {
	    el.onclick = function(ev) {
	    	el.querySelector('.strike-list').classList.toggle('d-none');
	    }
	});

	Array.from(document.querySelectorAll('.user-id')).forEach((el, i) => {
		el.onclick = function(ev) {
			ev.preventDefault();
			ev.stopPropagation();

			var input = document.createElement('input');
		    input.setAttribute('value', el.dataset.id);
		    document.body.appendChild(input);
		    input.select();
		    var result = document.execCommand('copy');
		    document.body.removeChild(input);
			add_notif('User\'s discord ID copied to clipboard.', 'success');
		}
	});

	Array.from(document.querySelectorAll('.strike-id')).forEach((el, i) => {
		el.onclick = function(ev) {
			ev.preventDefault();
			ev.stopPropagation();

			var input = document.createElement('input');
		    input.setAttribute('value', el.dataset.id);
		    document.body.appendChild(input);
		    input.select();
		    var result = document.execCommand('copy');
		    document.body.removeChild(input);
			add_notif('Strike ID copied to clipboard.', 'success');
		}
	});

});