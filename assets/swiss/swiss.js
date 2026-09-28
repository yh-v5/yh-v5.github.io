// Grid / blueprint toggles and BibTeX copy for the neo-Swiss theme.
// The initial state is applied by an inline script in <head> to avoid a flash.
(function () {
  var root = document.documentElement;

  function store(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {}
  }

  function isDark() {
    var t = root.getAttribute("data-theme");
    if (t) return t === "dark";
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function sync() {
    document.querySelectorAll('[data-toggle="grid"]').forEach(function (b) {
      b.setAttribute("aria-pressed", root.classList.contains("grid-on") ? "true" : "false");
    });
    document.querySelectorAll('[data-toggle="theme"]').forEach(function (b) {
      b.setAttribute("aria-pressed", isDark() ? "true" : "false");
    });
  }

  function toggleGrid() {
    var on = root.classList.toggle("grid-on");
    store("yh-grid", on ? "on" : "off");
    sync();
  }

  function toggleTheme() {
    var next = isDark() ? "light" : "dark";
    root.setAttribute("data-theme", next);
    store("yh-theme", next);
    sync();
  }

  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest("[data-toggle]");
    if (btn) {
      if (btn.getAttribute("data-toggle") === "grid") toggleGrid();
      else toggleTheme();
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

  // "G" shows the grid, like a layout tool would.
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "g" && ev.key !== "G") return;
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    var t = ev.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    toggleGrid();
  });

  if (window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    if (mq.addEventListener) mq.addEventListener("change", sync);
  }

  sync();
})();
