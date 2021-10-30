$("#showModal").click(function() {
    $(".modal").addClass("is-active");  
});
$(".modal-close-right").click(function() {
    $(".modal").removeClass("is-active");
});
$("#copyButton").click(function() {
    let output = document.getElementById("urlInput");
    output.select();
    navigator.clipboard.writeText(output.value);
})
$("#scrapeButton").click(function() {
    $(".progress").removeClass("is-hidden");
    let subdomain = document.getElementById("subdomainInput").value;
    let username = document.getElementById("usernameInput").value;
    let password = document.getElementById("passwordInput").value;
    let urlInput = document.getElementById("urlInput");
    let fetchUrl = "/api/v1/scrape?subdomain=" + subdomain + "&username=" + username + "&password=" + password;
    urlInput.value = fetchUrl;
    fetch(fetchUrl)
        .then(response => response.json())
        .then(data => {
            $(".progress").addClass("is-hidden");
            let node = document.getElementById("output");
            node.innerHTML = JSON.stringify(data);
        });
});