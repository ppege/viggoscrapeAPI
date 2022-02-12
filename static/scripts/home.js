$("#gotoDemo").click(function() {
    console.log("blalba");
    $("#demoHero").load("_demo.html");
    $([document.documentElement, document.body]).animate({
        scrollTop: $("#demoHero").offset().top
    }, 500);
});
function changeBackground(theme) {
    if (theme === 'light') {
      VANTA.NET({
        el: "#page",
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 200.00,
        minWidth: 200.00,
        scale: 1.00,
        scaleMobile: 1.00,
        points: 20.00,
        maxDistance: 28.00,
        spacing: 20.00,
        showDots: false,
        backgroundColor: 0xffffff
      })
    } else {
      VANTA.NET({
        el: "#page",
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 200.00,
        minWidth: 200.00,
        scale: 1.00,
        scaleMobile: 1.00,
        points: 12.00,
        maxDistance: 28.00,
        spacing: 20.00,
        showDots: false,
        backgroundColor: 0x17181C
      })
    }
  }
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    changeBackground('dark')
  } else {
    changeBackground('light')
  }
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
    const newColorScheme = event.matches ? "dark" : "light";
    if (newColorScheme === 'dark') {
      changeBackground('dark');
    } else {
      changeBackground('light');
    }
  });