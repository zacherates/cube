var pick_order_list = (function () {
	var ctx = {};


	return  {
		init: function () {
			ctx.$info = $("<div id='info' class='header'>")
				.appendTo(document.body);

			ctx.$message = $("<span class='message'>")
				.text("Pick overrated cards")
				.appendTo(ctx.$info);

			ctx.$done = $("<button>done</button>")
				.appendTo(ctx.$info);

			$('body').on('click', '.card', function (event) {
				console.log($(this).data('multiverseid'));	
			})
		}
	};
}());
