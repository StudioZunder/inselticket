// Menü auf dem Smartphone auf- und zuklappen
(function () {
  var knopf = document.querySelector('.kopf__menueknopf');
  var navs = document.getElementById('navigation');
  if (!knopf || !navs) return;
  knopf.addEventListener('click', function () {
    var offen = navs.classList.toggle('offen');
    knopf.setAttribute('aria-expanded', offen ? 'true' : 'false');
  });
})();
