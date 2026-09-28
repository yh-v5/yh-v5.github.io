// Dark / light switch, BibTeX copy and story reader helpers for the neo-Swiss theme.
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

  // Stories: open the chapter list on wide screens, and show reading progress.
  if (window.matchMedia && window.matchMedia("(min-width: 981px)").matches) {
    document.querySelectorAll("details[data-open-wide]").forEach(function (d) {
      d.open = true;
    });
  }
  var bar = document.querySelector(".read-progress");
  var body = document.querySelector(".story-body");
  if (bar && body) {
    var update = function () {
      var r = body.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var p = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 1;
      bar.style.setProperty("--read", p.toFixed(4));
    };
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
  }

  sync();
})();
