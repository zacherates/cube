console.log("Hello cube");

$(function () {
	function id(x) { return x; }

	var filters = {};

	$(".header").on("click", "a", function (){
		var attr = $(this).attr("id"),
			type = $(this).data("type");

		if (attr == "all") {
			$(".card").show();
			filters = {};
			$(".header a").removeClass("selected");
			$("#all").addClass("selected");
			return;
		}

		filters[type] = attr;
		$(".card").hide();
		$("." + ["card", filters.color, filters.type].filter(id).join(".")).show();

		$(".header a").removeClass("selected");
		[filters.color, filters.type].filter(id).forEach(function (selector) {
			$("#" + selector).addClass("selected");
		});
	});
});
