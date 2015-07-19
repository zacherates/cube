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
			console.log("Picked " + id);
			console.log(this.message());
			console.log(this);
		}
	};

	function init($root) {
		ctx.$root = $root;

		ctx.$info = $("<div class='info'>")
			.appendTo($root);

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
			ctx.$cards.load("/sample");
			picker.reset();
		});

		picker.events.on("changed", function (){
			ctx.$info
				.removeClass("good bad")
				.addClass(picker.picking())
				.text(picker.message());
		});

		picker.reset();
	}

	return { init: init };
}());
