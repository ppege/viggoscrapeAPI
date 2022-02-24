function replaceClass(id, oldClass, newClass) {
    var elem = $(`#${id}`);
    if (elem.hasClass(oldClass)) {
        elem.removeClass(oldClass);
    }
    elem.addClass(newClass);
}

$(".modal-close-right").click(function() {
    $(".modal").removeClass("is-active");
});
$("#copyButton").click(function() {
    let output = document.getElementById("urlInput");
    output.select();
    navigator.clipboard.writeText(output.value);
})
$("#hideShowURL").click(function() {
    let button = document.getElementById("hideShowURL")
    let field = document.getElementById("urlInput")
    if (field.type === "password"){
        field.type = "text";
        button.textContent = "Hide URL";
        replaceClass("hideShowURL", "is-danger", "is-success");
    } else {
        field.type = "password";
        button.textContent = "Show URL";
        replaceClass("hideShowURL", "is-success", "is-danger");
    }
})

$("#versionSelect").change(function() {
    let select = document.getElementById("versionSelect")
    let grouping = document.getElementById("groupingSelect")
    if (select.value === "API v1") {
        grouping.disabled = true;
    } else {
        grouping.disabled = false;
    }
})

$("#scrapeButton").click(function() {
    $(".progress").removeClass("is-hidden");
    let subdomain = document.getElementById("subdomainInput").value;
    let username = document.getElementById("usernameInput").value;
    let password = document.getElementById("passwordInput").value;
    let date = document.getElementById("dateInput").value;
    let version = document.getElementById("versionSelect").value.split(' ')[1];
    let grouping = document.getElementById("groupingSelect").value;
    let bool = + (grouping === "Group by assignment");
    let urlInput = document.getElementById("urlInput");
    let fetchUrl = "/api/" + version + "/scrape?subdomain=" + subdomain + "&username=" + username +  "&date=" + date + "&groupByAssignment=" + bool + "&password=" + password;
    urlInput.value = window.location.host + fetchUrl;
    fetch(fetchUrl)
        .then(response => response.text())
        .then(data => {
            $(".progress").addClass("is-hidden");
            let node = document.getElementById("output");
            node.innerHTML = data;
        });
});
