function goto(place) {
    $([document.documentElement, document.body]).animate({
        scrollTop: $(`#${place}`).offset().top
    }, 500);
}