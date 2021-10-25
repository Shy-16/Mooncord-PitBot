document.addEventListener("DOMContentLoaded", function(event) {

	Array.from(document.querySelectorAll('.area-chart')).forEach((el, i) => {
		let chartData = el.dataset.data;
		chartData = JSON.parse(chartData);

		let areaCtx = el.getContext('2d');
		let areaChart = new Chart(areaCtx, {
		    type: 'line',
		    data: chartData,
		    options: {
		    	locale: 'en-US',
		    	responsive: true,
		    	maintainAspectRatio: false,
		        plugins: {
		        	filler: {
		        		propagate: false
		        	},
		        	title:{
		        		display: false
		        	},
		        	legend: {
		        		display: false
		        	}
		        },
		        interaction: {
		        	intersect: false
		        }
		    }
		});
	});

	Array.from(document.querySelectorAll('.list-recent-strikes')).forEach((el, i) => {
		el.onclick = function(ev) {
			el.parentNode.querySelector('.user-recent-strikes').classList.toggle('d-none');
			el.parentNode.querySelector('.user-all-strikes').classList.add('d-none');
		}
	});

	Array.from(document.querySelectorAll('.list-all-strikes')).forEach((el, i) => {
		el.onclick = function(ev) {
			el.parentNode.querySelector('.user-all-strikes').classList.toggle('d-none');
			el.parentNode.querySelector('.user-recent-strikes').classList.add('d-none');
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