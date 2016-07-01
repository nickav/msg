function init() {
	// force all non-anchor links to open in a new window 
	var links = document.getElementsByTagName('a');
	for (var i=0,n=links.length; i<n; i++) {
		if (links[i].getAttribute('href')[0] != '#') {
			links[i].target = "_blank";
		}
	}
}

window.addEventListener('load', init, false);
