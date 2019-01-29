function changeStatus(){
	var xhttp = new XMLHTTPRequest();
	xhttp.onreadystatechange = function{
		if (this.readyState == 4 && this.status == 304){
			document.getElementById("finished").innerHTML = this.responseText;
		}
	}
	xhttp.open("/finished/{{row.id}}");
	xhttp.send();
}