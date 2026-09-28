// Dark / light switch and BibTeX copy for the neo-Swiss theme.
// Dark is the default; a saved "light" choice is applied by an inline script
// in <head> before first paint.
(function () {
  var root = document.documentElement;

  function current() {
    return root.getAttribute("data-theme") === "light" ? "light" : "dark";
  }

  function sync() {
    var t = current();
    document.querySelectorAll("[data-theme-set]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-theme-set") === t ? "true" : "false");
    });
  }

  function setTheme(t) {
    if (t === "light") root.setAttribute("data-theme", "light");
    else root.removeAttribute("data-theme");
    try {
      localStorage.setItem("yh-theme", t);
    } catch (e) {}
    sync();
  }

  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest("[data-theme-set]");
    if (btn) {
      setTheme(btn.getAttribute("data-theme-set"));
      return;
    }
    var copy = ev.target.closest("[data-copy]");
    if (copy) {
      var src = document.getElementById(copy.getAttribute("data-copy"));
      if (!src || !navigator.clipboard) return;
      navigator.clipboard.writeText(src.textContent.trim()).then(function () {
        var label = copy.textContent;
        copy.textContent = "Copied";
        setTimeout(function () {
          copy.textContent = label;
        }, 1400);
      });
    }
  });

  sync();
})();
