$("#openSource").click(function() {
    window.open("https://github.com/nangurepo/viggoscrapeapi", '_blank').focus();
});
$(".navbar-burger").click(function() {
    $(".navbar-burger").toggleClass("is-active");
    $(".navbar-menu").toggleClass("is-active");
});

function toggleColors(mode) {
    $("#darkmode").toggleClass("is-dark");
    $("#navbar-place").toggleClass("is-dark");
    $("#hero").toggleClass("is-dark");
    $("#gotoDemo").toggleClass("has-text-white");
    $("#gotoDemo").toggleClass("has-background-dark");
    $(".card").toggleClass("has-background-dark");
    $("#output").toggleClass("has-text-white");
    $("#output").toggleClass("has-background-dark");
    if (mode === "dark") {
        $("#dark-css").attr("href", "/static/styles/dark.css");
    } else {
        $("#dark-css").attr("href", "");
    }
}

$("#darkmode").click(function() {
    let button = document.getElementById("darkmode");
    if (button.textContent == "Dark mode"){
        $('link[href="static/styles/background.css"]').attr('href','static/styles/background-dark.css');
        button.textContent = "Light mode";
        toggleColors("dark");
    } else {
        $('link[href="static/styles/background-dark.css"]').attr('href','static/styles/background.css');
        button.textContent = "Dark mode";
        toggleColors("light");
    }
})

$(function() {
    $('#darkmode').click();
});