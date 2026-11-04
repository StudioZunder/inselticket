// InselTicket · Vorschau-Shop (Warenkorb, Sammelrabatt, Kasse)
// Speichert den Warenkorb im Browser. Es wird keine Bestellung verschickt.
(function (global) {
  'use strict';

  var SCHLUESSEL = 'inselticket-warenkorb';
  var MAX_MENGE = 99;

  // ---------- Rechnen (auch für Tests unter Node nutzbar) ----------

  // Sammelrabatt laut Kundentext: ab 50,- Euro Einkaufswert 10 %, ab 100,- Euro 20 %
  function rabattSatz(zwischenCent) {
    if (zwischenCent >= 10000) return 20;
    if (zwischenCent >= 5000) return 10;
    return 0;
  }

  function berechne(korb, produkte) {
    var zwischen = 0, anzahl = 0;
    Object.keys(korb).forEach(function (k) {
      if (!produkte[k]) return;
      zwischen += produkte[k].preis * korb[k];
      anzahl += korb[k];
    });
    var satz = rabattSatz(zwischen);
    var rabatt = Math.round(zwischen * satz / 100);
    var naechste = zwischen < 5000 ? { satz: 10, fehlt: 5000 - zwischen }
                 : zwischen < 10000 ? { satz: 20, fehlt: 10000 - zwischen } : null;
    return { anzahl: anzahl, zwischen: zwischen, satz: satz, rabatt: rabatt, gesamt: zwischen - rabatt, naechste: naechste };
  }

  function euro(cent) {
    return (cent / 100).toFixed(2).replace('.', ',') + ' €';
  }

  var api = { rabattSatz: rabattSatz, berechne: berechne, euro: euro };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; return; }

  // ---------- Browser ----------

  var produkte = global.INSELTICKET_PRODUKTE || {};
  var speicherErsatz = null;   // falls der Browser keinen Speicher erlaubt

  function laden() {
    try {
      var roh = global.localStorage.getItem(SCHLUESSEL);
      if (roh) return bereinigen(JSON.parse(roh));
    } catch (e) { /* Speicher gesperrt */ }
    return speicherErsatz ? bereinigen(speicherErsatz) : {};
  }

  function speichern(korb) {
    speicherErsatz = korb;
    try { global.localStorage.setItem(SCHLUESSEL, JSON.stringify(korb)); } catch (e) { /* Sitzung reicht */ }
    zaehlerZeigen();
  }

  function bereinigen(korb) {
    var sauber = {};
    Object.keys(korb || {}).forEach(function (k) {
      var n = parseInt(korb[k], 10);
      if (produkte[k] && n > 0) sauber[k] = Math.min(n, MAX_MENGE);
    });
    return sauber;
  }

  function setzeMenge(k, n) {
    var korb = laden();
    if (n > 0) korb[k] = Math.min(n, MAX_MENGE); else delete korb[k];
    speichern(korb);
    seiteZeichnen();
  }

  function hinzufuegen(k) {
    var korb = laden();
    korb[k] = Math.min((korb[k] || 0) + 1, MAX_MENGE);
    speichern(korb);
    melden(produkte[k].name + ' liegt im Warenkorb.', 'warenkorb.html', 'Zum Warenkorb');
    seiteZeichnen();
  }

  // ---------- Anzeige ----------

  function zaehlerZeigen() {
    var anzahl = berechne(laden(), produkte).anzahl;
    document.querySelectorAll('[data-korb-zaehler]').forEach(function (el) {
      el.textContent = anzahl;
      el.hidden = anzahl === 0;
      el.setAttribute('aria-label', anzahl + ' im Warenkorb');
    });
  }

  var meldungTimer;
  function melden(text, link, linkText) {
    var box = document.querySelector('[data-meldung]');
    if (!box) return;
    box.innerHTML = '';
    var span = document.createElement('span'); span.textContent = text; box.appendChild(span);
    if (link) {
      var a = document.createElement('a'); a.href = link; a.textContent = linkText; box.appendChild(a);
    }
    box.hidden = false;
    requestAnimationFrame(function () { box.classList.add('meldung--sichtbar'); });
    clearTimeout(meldungTimer);
    meldungTimer = setTimeout(function () {
      box.classList.remove('meldung--sichtbar');
      setTimeout(function () { box.hidden = true; }, 300);
    }, 4000);
  }

  function zeile(k, menge, nurLesen) {
    var p = produkte[k];
    var li = document.createElement('li');
    li.className = 'korbzeile';
    li.innerHTML =
      '<a class="korbzeile__bild" href="' + p.seite + '"><img src="' + p.bild + '" alt="" width="900" height="371"></a>' +
      '<div class="korbzeile__text">' +
        '<a class="korbzeile__name" href="' + p.seite + '"></a>' +
        '<span class="korbzeile__laufzeit"></span>' +
        '<span class="korbzeile__einzel"></span>' +
      '</div>' +
      (nurLesen
        ? '<span class="korbzeile__menge-lesen"></span>'
        : '<div class="menge" role="group" aria-label="Menge">' +
            '<button type="button" class="menge__knopf" data-minus aria-label="Eins weniger">−</button>' +
            '<input class="menge__zahl" type="number" min="0" max="' + MAX_MENGE + '" inputmode="numeric" aria-label="Anzahl">' +
            '<button type="button" class="menge__knopf" data-plus aria-label="Eins mehr">+</button>' +
          '</div>') +
      '<span class="korbzeile__summe"></span>' +
      (nurLesen ? '' : '<button type="button" class="korbzeile__weg" data-weg aria-label="Entfernen">×</button>');
    li.querySelector('.korbzeile__name').textContent = 'InselTicket ' + p.titel;
    li.querySelector('.korbzeile__laufzeit').textContent = p.laufzeit;
    li.querySelector('.korbzeile__einzel').textContent = 'Einzelpreis: ' + euro(p.preis);
    li.querySelector('.korbzeile__summe').textContent = euro(p.preis * menge);
    if (nurLesen) {
      li.querySelector('.korbzeile__menge-lesen').textContent = menge + ' ×';
    } else {
      var feld = li.querySelector('.menge__zahl');
      feld.value = menge;
      li.querySelector('[data-minus]').addEventListener('click', function () { setzeMenge(k, menge - 1); });
      li.querySelector('[data-plus]').addEventListener('click', function () { setzeMenge(k, menge + 1); });
      li.querySelector('[data-weg]').addEventListener('click', function () { setzeMenge(k, 0); });
      feld.addEventListener('change', function () { setzeMenge(k, parseInt(feld.value, 10) || 0); });
    }
    return li;
  }

  function summeZeigen(r) {
    var setze = function (sel, text) { document.querySelectorAll(sel).forEach(function (el) { el.textContent = text; }); };
    setze('[data-summe-zwischen]', euro(r.zwischen));
    setze('[data-summe-gesamt]', euro(r.gesamt));
    setze('[data-summe-rabatt]', '− ' + euro(r.rabatt));
    setze('[data-summe-rabatt-text]', 'Sammelrabatt ' + r.satz + ' %');
    document.querySelectorAll('[data-summe-rabatt-zeile]').forEach(function (el) { el.hidden = r.satz === 0; });
    setze('[data-rabatt-hinweis]', r.naechste
      ? 'Noch ' + euro(r.naechste.fehlt) + ' bis ' + r.naechste.satz + ' % Sammelrabatt.'
      : 'Sie erhalten den höchsten Sammelrabatt von 20 %.');
  }

  function seiteZeichnen() {
    var shop = document.querySelector('[data-shop]');
    if (!shop) return;
    var korb = laden();
    var r = berechne(korb, produkte);
    var leer = r.anzahl === 0;
    var danke = shop.querySelector('[data-danke]');
    if (danke && !danke.hidden) return;
    shop.querySelectorAll('[data-korb-leer]').forEach(function (el) { el.hidden = !leer; });
    shop.querySelectorAll('[data-korb-voll]').forEach(function (el) { el.hidden = leer; });
    shop.querySelectorAll('[data-korb-liste]').forEach(function (ul) {
      var nurLesen = ul.hasAttribute('data-nur-lesen');
      ul.innerHTML = '';
      Object.keys(produkte).forEach(function (k) { if (korb[k]) ul.appendChild(zeile(k, korb[k], nurLesen)); });
    });
    summeZeigen(r);
  }

  // ---------- Kasse ----------

  function kasseVorbereiten() {
    var form = document.querySelector('[data-kasse]');
    if (!form) return;
    var fehler = document.querySelector('[data-kasse-fehler]');
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (!form.checkValidity()) {
        fehler.hidden = false;
        form.classList.add('kasse--geprueft');
        var erstes = form.querySelector(':invalid');
        if (erstes) erstes.focus();
        return;
      }
      fehler.hidden = true;
      var korb = laden();
      var r = berechne(korb, produkte);
      var daten = new FormData(form);
      var zeilen = Object.keys(korb).map(function (k) {
        return '<li>' + korb[k] + ' × ' + produkte[k].name + ' 2027 · ' + euro(produkte[k].preis * korb[k]) + '</li>';
      }).join('');
      var esc = function (s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; };
      var adresse = [
        [daten.get('vorname'), daten.get('nachname')].join(' '),
        daten.get('firma'), daten.get('strasse'), [daten.get('plz'), daten.get('ort')].join(' '), daten.get('email')
      ].filter(function (x) { return x && x.trim(); }).map(esc).join('<br>');
      var box = document.querySelector('[data-danke-uebersicht]');
      box.innerHTML =
        '<ul class="danke__liste">' + zeilen + '</ul>' +
        (r.satz ? '<p>Sammelrabatt ' + r.satz + ' %: − ' + euro(r.rabatt) + '</p>' : '') +
        '<p class="danke__gesamt">Gesamt: ' + euro(r.gesamt) + '</p>' +
        '<p>Zahlart: Kauf auf Rechnung</p>' +
        '<p class="danke__adresse">' + adresse + '</p>';
      speichern({});
      document.querySelectorAll('[data-korb-voll],[data-korb-leer]').forEach(function (el) { el.hidden = true; });
      document.querySelector('[data-danke]').hidden = false;
      global.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ---------- Start ----------

  function start() {
    // Vorschau-Befüllung: warenkorb.html?beispiel
    if (/[?&]beispiel\b/.test(global.location.search)) {
      speichern({ borkum: 2, juist: 1, helgoland: 1 });
    }
    document.querySelectorAll('[data-ticket]').forEach(function (b) {
      b.addEventListener('click', function () { hinzufuegen(b.getAttribute('data-ticket')); });
    });
    zaehlerZeigen();
    seiteZeichnen();
    kasseVorbereiten();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})(typeof window !== 'undefined' ? window : globalThis);
