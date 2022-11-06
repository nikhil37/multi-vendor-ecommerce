document.addEventListener('DOMContentLoaded', () => {
	var small_imgs = document.getElementsByClassName('small_images');
	var formulaire = document.getElementsByClassName('formulaire');


	for (var i = 0; i < small_imgs.length; i++) {
	    small_imgs[i].addEventListener('click', (bt) => {
	    var l = (String)(bt.target.dataset['num']);
	    var main = document.getElementById('main_img');
	    var src = "/static/images/{{ product.product_id}}_" + l + '.' +(main.src.split('.')[main.src.split('.').length-1]);
	    console.log(src);
	    main.src=src;
	    //this.style.display ='none';
	});
	}
})