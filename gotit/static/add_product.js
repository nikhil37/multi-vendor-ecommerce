document.addEventListener('DOMContentLoaded', () => {
	var new_detail_btn = document.getElementById('add_detail');
	new_detail_btn.addEventListener('click', () => {
		var div_details = document.getElementById('details');
		var c = document.getElementsByClassName('details').length;
		document.getElementById('no_of_details').value = c+1;
		div_details.innerHTML += '											<div class="input-group d-flex flex-row align-items-center mb-4 details">\
											  <input type="text" class="input-group-text form-control" placeholder="Detail title" name="detail_title_'+c.toString()+'"/>\
											  <input class="form-control" placeholder="Detail" name="detail_'+c.toString()+'" />\
											</div>\
';
	})
})