function insertGist(url) {
    $.get(url, function(data) {
        marked.setOptions({
            highlight: function(code) {
            return hljs.highlightAuto(code).value;
            }
        });
        $("#description").html(marked.parse(data));
    });
}