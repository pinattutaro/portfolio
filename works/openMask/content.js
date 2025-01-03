console.log('enter');
const url = location.href;
if(url.indexOf('Programming1-') != -1) {
	document.addEventListener('scroll',() => {
		var elements = document.getElementsByClassName('masked');
		for (var i = 0; i < elements.length; i++) {
			elements[i].className += " open";
		}
	});	
} 