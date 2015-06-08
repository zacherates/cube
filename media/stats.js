$(function(){
	$(".inlinesparkline").sparkline("html", {
		disableInteraction: true,
		lineColor: '#777',
		fillColor: false,
		chartRangeMin: 0,
		chartRangeMax: 25,
		spotColor: false,
		minSpotColor: false,
		maxSpotColor: false,
	});
});
