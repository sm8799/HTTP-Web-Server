
// FOR Card HOVER

$(document).ready(function(){

	$('.card').hover(
		function(){
			$(this).animate({
				marginTop: "-=1%",
			},200);
		},
		function(){
			$(this).animate({
				marginTop: "0%",
			},200);
		}

		);
});

 // FOR Directing To Register Page

var h = document.getElementById("LOGIN");
h.onclick = function () {
        location.href = "login.html";
    };

document.getElementById("SIGNUP").onclick = function () {
        location.href = "login.html";
    };
