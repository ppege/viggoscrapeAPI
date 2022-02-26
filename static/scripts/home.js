$("#gotoDemo").click(function() {
    $("#demoHero").load("./demo.html");
    $([document.documentElement, document.body]).animate({
        scrollTop: $("#demoHero").offset().top
    }, 500);
});