// Start page by enforcing automatic scroll to bottom.
var _manual_scroll = false;
// The cache object interacts with the log and the main div to which tweets append.
// The 'init' constructor is onLoad, the 'update' constructor runs at a configurable
// interval, set at the end of the script.
var cache = {
	tweets: "Null",
	tags: [],
	sequence: [],
	count: 0,
	init: function() {
		$.ajax({
			url: "../log/00-eclipse.txt",
			async: false,
			success: function(data){
				cache.tweets = JSON.parse(data);
				cache.count = cache.tweets.length;
				for(var i = 0; i<cache.count; i++){
					tag = makeTag(cache.tweets[i]);
					$('#console').append(tag);
					typeMe(cache.tweets[i]);
				}
			}
		});
	},
	update: function() {
		$.ajax({
			url: "../log/00-eclipse.txt",
                        async: false,
                        success: function(data){
				var updates = JSON.parse(data);
				for(var i = cache.count;i<=updates.length;i++){
					try{
						tag = makeTag(updates[i]);
						$('#console').append(tag);
						typeMe(updates[i]);
						cache.count += 1
					} catch(err) {
						console.log('No new records...');
					}
				}
			}
		});

	}
};
function makeTag(tweet){
	// Create tweet links/spans.
	console.log('Making tag...['+tweet.t_id+']');
	return "<span onclick = 'window.open(\"http://www.twitter.com/"+tweet.data.user+"/status/"+tweet.t_id+"\",\"width=320\",\"height=190\")' class = 'tweet' id = 'id" + tweet.t_id + "' title = '" + tweet.data.loc + "'></span> ";
}
function typeMe(tweet){
	// Do screen typing for each tweet, targeting individual spans rather than adding to a single-string corpus.
	// The idea was to do a kind of lazy-load for strings, but this is a choice in taste or laziness in programming
        // rather than, perhaps, good. objective code.
	var id = "#id"+tweet.t_id;
	var typed = new Typed(id,{});
	typed.strings = [filterText(tweet.data.msg)];
	typed.typeSpeed = 30;
	typed.backSpeed = 0;
	typed.onStringComplete = function() { $('.typed-cursor').remove(); };
	typed.blinkingCursor = true;
	typed.loop = false;
	$('#console').find('span.typed-cursor:not(:last)').hide();
}
function cursorAnimation() {
   //Set and animate typed.min.js cursor.
    $('#console span:last-child').html('█');
    $('#console span:last-child').animate({
        opacity: 0
    }, 'fast', 'swing').animate({
        opacity: 1
    }, 'fast', 'swing');
}
function filterText(tweet){
	// Filter whitespace, and remove urls from tweet text.
	var inc = tweet;
	inc = inc.trim();
	var a = inc.replace(/(?:https?|ftp):\/\/[\n\S]+/g, '');
	// This is also where one might put language filters. People on Twitter use bad words, sometimes.
	return a;
}
function scrollUp(){
	// Should users want to scroll to top, and free themselves from the tyranny of autoscroll.
	_manual_scroll = true;
	$('#console').animate({scrollTop: 0},800);
}
function scrollDown(){
	// Welcome to my autoscroll empire.
	if(!_manual_scroll){
		var scrollBottom = document.getElementById('console').scrollHeight;
        	$('#console').animate({scrollTop: scrollBottom},800);
	}
}
// Setting intervals for all recurring tasks.
setInterval(cache.update,10000);
setInterval(cursorAnimation,1000);
setInterval(scrollDown,1000);
