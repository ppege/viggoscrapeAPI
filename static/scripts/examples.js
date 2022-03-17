function goto(place) {
    $([document.documentElement, document.body]).animate({
        scrollTop: $(`#${place}`).offset().top
    }, 500);
}

function insertGist(url, selector) {
    fetch(url)
    .then(response => response.text())
    .then(text => {
        marked.setOptions({
            highlight: function(code) {
            return hljs.highlightAuto(code).value;
            }
        });
        $(selector).html(marked.parse(text));
    });
}

insertGist('https://gist.githubusercontent.com/NanguRepo/7bec404ae851725b3abb7bdbec9fb88f/raw/', '#pythonBody');
insertGist('https://gist.githubusercontent.com/NanguRepo/f139e748e13b497da2b84435848e0407/raw/', '#javascriptBody');
