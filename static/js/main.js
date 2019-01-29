function validateForm(){
	var task = document.getElementById("task").value;
	var status = document.getElementById("status").value;
	var priority = document.getElementById("priority").value;

	if ((task == null || task == "") && (status == null || status == "") && (priority == null || priority == "")){
		alert("One or more values cannot be blank");
		return false;
	}
}