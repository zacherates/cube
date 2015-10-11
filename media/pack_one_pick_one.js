var p1p1 = (function () {
	var ENTER = 13;
	var ctx = {}

	var model = {
		events: $("<div>"),
		submit: function (data) {
			console.log(data);
			this.reset();
		},
		reset: function () {
			this.events.trigger('new_pack');	
		},
		init: function () {
			this.reset();	
		}
	};

	function post(url, data, success, dataType) {
		$.ajax({
			  url: url,
			  type: "POST",
			  data: JSON.stringify(data),
			  contentType: "application/json; charset=utf-8",
			  dataType: 'html',
			  success: success
		});
	}

	return {
		init: function ($root) {
			ctx.$root = $root;
			ctx.$cards = $("<div class='cards'>")
				.appendTo($root);

			ctx.$notes = $("<textarea autofocus id='notes'>")
				.appendTo($root);

			model.events.on('new_pack', function () {
				ctx.$cards.load("/pack");
				ctx.$notes.val('');
			});

			ctx.$notes.on('keydown', function (event) {
				if (!event.ctrlKey || event.keyCode != ENTER) {
					return;
				}

				event.preventDefault();
				var cards = ctx.$cards.find(".card").map(function () {
					return $(this).data('multiverseid');	
				}).toArray();

				var data = {
					cards: cards,
					notes: ctx.$notes.val()
				};

				post("/post-notes", data, function (html) {}, 'html');
				model.reset();
			});

			model.init();
		}
	};
}());
