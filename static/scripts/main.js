$("#showModal").click(function() {
    $(".modal").addClass("is-active");  
});
$("#toggle").click(function() {
    let hero = $(".hero");
    let style = hero.css();
    console.log(style);
    let toggle = document.getElementById("toggle");
    if (toggle.checked === true) {
        style.color = "#FFFFFF";
        style.background = "url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyBAMAAADsEZWCAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAVUExURWdnaAoKCh0dHQcHBzo6OiEhIRwcHClcoyIAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAoSURBVDjLY2BUwg4UGUxCsYMQhlQcMqGjMqMyozKjMkNCBkf5FhoCACEOnKmd1d8pAAAAAElFTkSuQmCC') repeat 0 0";
    } else {
        style.color = "#363636";
        style.background = "url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAIAAACRXR/mAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABnSURBVHja7M5RDYAwDEXRDgmvEocnlrQS2SwUFST9uEfBGWs9c97nbGtDcquqiKhOImLs/UpuzVzWEi1atGjRokWLFi1atGjRokWLFi1atGjRokWLFi1af7Ukz8xWp8z8AAAA//8DAJ4LoEAAlL1nAAAAAElFTkSuQmCC') repeat 0 0";
    }
})