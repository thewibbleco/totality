// Functionality for the about box. Probably didn't need its own script, but I like including stuff.
// Call it a hobby.
function aboutPopover(){
	$("#scrim").css("visibility","visible");
	$("#about-box").css("visibility","visible");
}

function aboutPopout(){
	 $("#scrim").css("visibility","hidden");
        $("#about-box").css("visibility","hidden");
}
