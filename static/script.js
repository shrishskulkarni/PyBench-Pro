document.addEventListener("DOMContentLoaded", function () {
    var tabs = document.querySelectorAll("[data-tabs] .tab-button");
    var panels = document.querySelectorAll(".tab-panel");
    tabs.forEach(function (tab) {
        tab.addEventListener("click", function () {
            var target = tab.getAttribute("data-tab");
            tabs.forEach(function (t) {
                t.classList.toggle("active", t === tab);
            });
            panels.forEach(function (panel) {
                panel.classList.toggle(
                    "active",
                    panel.getAttribute("data-panel") === target
                );
            });
        });
    });
    var form = document.getElementById("code-form");
    var overlay = document.getElementById("loading-overlay");
    if (form && overlay) {
        form.addEventListener("submit", function () {
            overlay.classList.add("visible");
        });
    }
});

