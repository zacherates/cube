console.log("Hello cube");

$(function () {
	$(".header").on("click", "a", function (){
		var type = $(this).attr("id");
		$(".gallery").toggleClass("no-" + type + "s");
	});
});
