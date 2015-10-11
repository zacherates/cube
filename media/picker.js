var picker = (function () {

	var ctx = {};

	var picker = {
		events: $("<div>"),
		picked: 0,
		good: [],
		bad: [],
		picking: function () {
			return this.picked < 3 ? "good" : "bad";
		},
		done: function () {
			this.events.trigger("done", this);
		},
		reset: function () {
			this.picked = 0;
			this.good = [];
			this.bad = [];	

			this.update();
		},
		pick: function (id) {
			var set = (this.picked++ < 3 ? this.good : this.bad);
			set.push(id)

			if (this.picked === 6) {
				this.done();
			}

			this.update(id);
		},
		message: function () {
			if (this.picked < 3) {
				return "Pick the " + (3 - this.picked) + " best cards.";
			} else {
				return "Pick the " + (6 - this.picked) + " worst cards."; 	
			}
		},
		update: function (id) {
			this.events.trigger("changed", this);
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

	function init($root) {
		ctx.$root = $root;

		ctx.$status = $("<div class='status'>")
			.appendTo($root);

		ctx.$info = $("<span class='info'>")
			.appendTo(ctx.$status);

		ctx.$progress = $("<progress>")
			.hide()
			.appendTo(ctx.$status);

		ctx.$cards = $("<div class='cards'>")
			.appendTo($root);

		ctx.$cards.load("/sample");

		ctx.$cards.on("click", ".card", function(event) {
			var id = $(this).data("multiverseid");
			$(this).addClass("picked")
				.addClass(picker.picking());

			picker.pick(id);
		});

		picker.events.on("done", function (){
			var cards = ctx.$cards.find(".card").map(function () {
				return $(this).data('multiverseid');	
			}).toArray();

			var data = {
				good: picker.good,
				bad: picker.bad,
				rest: cards,	
			};

			post("/post-picks", data, function (html) {
				picker.reset();

				var rated = $(html).data('rated'),
					total = $(html).data('total');

				ctx.$progress
					.attr('value', rated)
					.attr('max', total)
					.show();

				ctx.$cards
					.empty()
					.html(html);
			}, 'html');

		});

		picker.events.on("changed", function (){
			ctx.$status
				.removeClass("good bad")
				.addClass(picker.picking());

			ctx.$info
				.text(picker.message());
		});

		picker.reset();
	}

	return { init: init };
}());
