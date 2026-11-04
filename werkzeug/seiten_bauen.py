"""Baut alle HTML-Seiten des InselTicket-Prototyps aus einer gemeinsamen Vorlage.

Aufruf (im Ordner outputs/website):  python3 werkzeug/seiten_bauen.py
Inhalte: werkzeug/inseln.json (Gutscheine je Insel) und werkzeug/quellen/*.html
(Texte der Live-Seite inselticket.de, Stand 04.11.2026, wörtlich übernommen).
"""
import html, json, re
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
QUELLEN = WEB / 'werkzeug' / 'quellen'
DATEN = json.loads((WEB / 'werkzeug' / 'inseln.json').read_text())['inseln']

INSELN = [  # Schlüssel, Name
    ('borkum', 'Borkum'), ('norderney', 'Norderney'), ('juist', 'Juist'),
    ('wangerooge', 'Wangerooge'), ('helgoland', 'Helgoland'),
]

e = html.escape

# ---------------------------------------------------------------- Rahmen

def kopf(aktiv):
    def cur(k):
        return ' aria-current="page"' if k == aktiv else ''
    unter = ''.join(
        f'<li><a href="{k}.html"{cur(k)}>InselTicket {n}</a></li>' for k, n in INSELN)
    inseln_aktiv = aktiv == 'inseln' or aktiv in dict(INSELN)
    return f'''<header class="kopf">
  <div class="kopf__innen">
    <a class="kopf__logo" href="index.html" aria-label="InselTicket Startseite">
      <img src="assets/img/inselticket-logo.png" alt="InselTicket. Gutscheine für Ihren Inselurlaub" width="1038" height="269">
    </a>

    <button class="kopf__menueknopf" type="button" aria-expanded="false" aria-controls="navigation">
      <span></span><span></span><span></span>
      <span class="sr">Menü</span>
    </button>

    <div class="kopf__navs" id="navigation">
      <nav class="metanav" aria-label="Service">
        <a class="metanav__insta" href="https://www.instagram.com/inselticket.de/" target="_blank" rel="noopener" aria-label="InselTicket auf Instagram">
          <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4.4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.6" cy="6.4" r="1.3" fill="currentColor"/></svg>
        </a>
        <a href="agb.html"{cur('agb')}>AGB</a>
        <a href="impressum.html"{cur('impressum')}>Impressum</a>
      </nav>
      <nav class="hauptnav" aria-label="Hauptmenü">
        <a href="so-funktionierts.html"{cur('function')}>So funktioniert's</a>
        <div class="hauptnav__gruppe">
          <a href="inseln.html"{' aria-current="page"' if inseln_aktiv else ''}>Inseln &amp; Anbieter</a>
          <ul class="hauptnav__unter">{unter}</ul>
        </div>
        <a class="hauptnav__korb" href="warenkorb.html"{cur('basket')}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M1 3h3.2l2.6 12.2a1 1 0 0 0 1 .8h10.4a1 1 0 0 0 1-.76L21.6 7H6.1" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9" cy="20" r="1.6" fill="currentColor"/><circle cx="17" cy="20" r="1.6" fill="currentColor"/></svg>
          Warenkorb
          <span class="korb-zaehler" data-korb-zaehler hidden></span>
        </a>
      </nav>
    </div>
  </div>
</header>'''


def seite(datei, titel, aktiv, inhalt, beschreibung='', noindex=False):
    beschreibung = beschreibung or 'Exklusiv-Gutscheine für Ihren Urlaub auf Borkum, Norderney, Juist, Wangerooge und Helgoland.'
    robots = '\n  <meta name="robots" content="noindex">' if noindex else ''
    doc = f'''<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">{robots}
  <title>{e(titel)}</title>
  <meta name="description" content="{e(beschreibung)}">
  <link rel="preload" href="assets/fonts/roboto-condensed-700.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

{kopf(aktiv)}

<main>
{inhalt}
</main>

<div class="meldung" data-meldung role="status" aria-live="polite" hidden></div>

<script src="assets/js/menue.js"></script>
<script src="assets/js/produkte.js"></script>
<script src="assets/js/warenkorb.js"></script>
</body>
</html>
'''
    (WEB / datei).write_text(doc)
    print('gebaut:', datei)


def seitenkopf(titel, bild, position='center'):
    return f'''  <section class="seitenkopf">
    <div class="seitenkopf__bild" style="background-image: url('assets/img/{bild}'); background-position: {position};" aria-hidden="true"></div>
    <h1 class="seitenkopf__titel">{titel}</h1>
  </section>'''

# ---------------------------------------------------------------- Bausteine

def kopfdaten(k):
    d = DATEN[k]['kopf']
    titel = d[0][1].split('\n')          # ['InselTicket', 'Borkum 2027']
    fakten = d[1][1].split('\n')         # Laufzeit, Gesamtersparnis
    preis = d[2][1]                       # 'Einmal kaufen, überall sparen! Einmaliger Kaufpreis: 24,50 €'
    p1, p2 = preis.split('! ', 1)
    return titel, fakten, (p1 + '!', p2)


def ticketkasten(k, n, knopf_text, knopf_ziel, ebene='h2'):
    titel, fakten, preis = kopfdaten(k)
    return f'''      <div class="ticketkasten">
        <img class="ticketkasten__bild" src="assets/img/inselticket-{k}.jpg" alt="InselTicket {e(n)} 2027" width="900" height="371">
        <div class="ticketkasten__text">
          <{ebene} class="ticketkasten__titel">{e(titel[0])}<br>{e(titel[1])}</{ebene}>
          <p class="ticketkasten__fakten">{'<br>'.join(e(f) for f in fakten)}</p>
          <p class="ticketkasten__preis">{e(preis[0])}<br>{e(preis[1])}</p>
          {knopf(knopf_text, knopf_ziel)}
        </div>
      </div>'''


def knopf(text, ziel):
    """Ziel 'ticket:borkum' ergibt einen Warenkorb-Knopf, sonst einen Link."""
    if ziel.startswith('ticket:'):
        return f'<button class="knopf" type="button" data-ticket="{ziel[7:]}">{text}</button>'
    return f'<a class="knopf" href="{ziel}">{text}</a>'


def preis_cent(k):
    """'Einmaliger Kaufpreis: 24,50 €' -> 2450"""
    m = re.search(r'(\d+),(\d{2})\s*€', kopfdaten(k)[2][1])
    return int(m.group(1)) * 100 + int(m.group(2))


def produkte_js():
    produkte = {}
    for k, n in INSELN:
        titel, fakten, _ = kopfdaten(k)
        produkte[k] = {
            'id': int(DATEN[k]['kaufen']),
            'name': f'InselTicket {n}',
            'titel': titel[1],
            'preis': preis_cent(k),
            'laufzeit': fakten[0],
            'bild': f'assets/img/inselticket-{k}.jpg',
            'seite': f'{k}.html',
        }
    js = ('// Automatisch erzeugt von werkzeug/seiten_bauen.py aus werkzeug/inseln.json\n'
          'window.INSELTICKET_PRODUKTE = ' + json.dumps(produkte, ensure_ascii=False, indent=2) + ';\n')
    (WEB / 'assets' / 'js' / 'produkte.js').write_text(js)
    print('gebaut: assets/js/produkte.js')


def ticketliste():
    li = ''.join(f'\n    <li>\n{ticketkasten(k, n, "Zum Ticket", k + ".html")}\n    </li>' for k, n in INSELN)
    return f'''  <section class="inseln" id="inseln" aria-label="Die Inseln">
    <ul class="inseln__liste">{li}
    </ul>
  </section>'''


def inselwahl(aktiv):
    cur = ' aria-current="page"'
    links = ''.join(
        f'<a href="{k}.html"{cur if k == aktiv else ""}>{n}</a>' for k, n in INSELN)
    return f'''  <nav class="inselwahl" aria-label="Weitere Inseln">
    <span class="inselwahl__titel">Weitere InselTickets:</span>
    {links}
  </nav>'''

# ---------------------------------------------------------------- Rechtstexte bereinigen

ERLAUBT = {'strong', 'br', 'h4', 'a', 'p'}

def rechtstext(roh):
    t = re.sub(r'(?s)<!--.*?-->', '', roh)
    t = t.replace('Ãœ', 'Ü')                       # Zeichensatzfehler der Live-Seite
    t = re.sub(r'(?is)<(script|style).*?</\1>', '', t)
    t = re.sub(r'(?i)<b>', '<strong>', t); t = re.sub(r'(?i)</b>', '</strong>', t)

    def tag(m):
        name = m.group(2).lower()
        if name not in ERLAUBT:
            return ''
        if name == 'a':
            if m.group(1):
                return '</a>'
            href = re.search(r'href="([^"]*)"', m.group(0))
            return f'<a href="{href.group(1)}">' if href else '<a>'
        if name == 'br':
            return '<br>'
        return f'<{m.group(1)}{name}>'
    t = re.sub(r'<(/?)([a-zA-Z0-9]+)[^>]*>', tag, t)
    t = html.unescape(t).replace('\xa0', ' ')
    t = re.sub(r'[ \t\r\n]+', ' ', t)
    t = t.replace('<h4>', '<h2>').replace('</h4>', '</h2>')
    t = re.sub(r'(\s*<br>\s*){2,}', '</p><p>', t)
    t = re.sub(r'\s*<br>\s*', '<br>', t)
    t = re.sub(r'<p>\s*(<br>)*\s*', '<p>', t)
    t = '<p>' + t.strip() + '</p>'
    t = re.sub(r'<p>\s*(<h2>.*?</h2>)', r'\1<p>', t)
    t = re.sub(r'(</h2>)\s*(<br>)+', r'\1', t)
    t = re.sub(r'<p>\s*</p>', '', t)
    t = re.sub(r'<p>\s*<br>', '<p>', t)
    # fette Zwischentitel mitten im Absatz werden eigene Überschriften
    t = re.sub(r'<br><strong>([^<]{3,120})</strong><br>', r'</p><h3>\1</h3><p>', t)
    # offene Absätze vor Überschriften schließen
    t = re.sub(r'(<p>(?:(?!</p>).)*?)\s*(<h2>)', r'\1</p>\2', t)
    t = re.sub(r'(</h2>)\s*(?!<p>)', r'\1<p>', t)
    t = re.sub(r'<p>\s+', '<p>', t)
    t = re.sub(r'(<br>)*</p>(\s*<br>)*\s*</p>', '</p>', t)
    t = re.sub(r'<br>\s*</p>', '</p>', t)
    t = re.sub(r'<p>\s*</p>', '', t)
    t = t.replace('<h3>', '\n      <h3>')
    return t.replace('</p><p>', '</p>\n      <p>').replace('<h2>', '\n      <h2>')

# ---------------------------------------------------------------- Seiten

def startseite():
    inhalt = f'''  <section class="held">
    <div class="held__bild" aria-hidden="true"></div>
    <h1 class="held__titel">Exklusiv-Gutscheine<br>für Ihren Urlaub.</h1>
  </section>

{ticketliste()}

  <section class="botschaft">
    <p>Keine Vorkasse, der Versand erfolgt mit beiliegender Rechnung.<br>
    Wir wünschen Ihnen im Jahr 2024 einen sonnigen und wunderschönen Urlaub<br>
    auf ihrer Lieblingsinsel!</p>
    <p>P.S.: Fahren Sie als Gruppe, Verein oder Club auf die Inseln?<br>
    Dann lohnt sich für Sie eine Sammelbestellung, denn ab einem Einkaufswert<br>
    von 50.- Euro gibt`s 10%, ab 100.- Euro satte 20% Rabatt!</p>
  </section>

  <section class="app" id="app">
    <div class="app__text">
      <h2 class="app__titel">Für Alle, die lieber mit dem<br>Smartphone sparen</h2>
      <p>Unser InselTicket gibt es auch als App:</p>
      <div class="app__badges">
        <a href="#app"><img src="assets/img/badge-app-store.png" alt="Get it on App Store" width="438" height="156"></a>
        <a href="#app"><img src="assets/img/badge-google-play.png" alt="Get it on Google Play" width="444" height="158"></a>
      </div>
      <p>Zur Vorschau: <a href="https://app.inselticket.de" target="_blank" rel="noopener">app.inselticket.de</a></p>
    </div>
  </section>'''
    seite('index.html', 'InselTicket · Gutscheine für Ihren Inselurlaub', 'start', inhalt)


def inselseite(k, n):
    d = DATEN[k]
    karten = []
    for g in d['gutscheine']:
        name = e(g['name'])
        if g['link']:
            name = f'<a href="{e(g["link"])}" target="_blank" rel="noopener">{name}</a>'
        zusatz = f'<span class="gutschein__zusatz">{e(g["zusatz"])}</span>' if g['zusatz'] else ''
        zeit = f'<span class="gutschein__zeit">{e(g["zeit"])}</span>' if g['zeit'] else ''
        karten.append(f'''      <li class="gutschein">
        <h3 class="gutschein__name">{name}</h3>{zusatz}
        <p class="gutschein__angebot">{e(g["angebot"])}{zeit}</p>
        <p class="gutschein__ersparnis">{e(g["ersparnis"])}</p>
      </li>''')
    titel, fakten, preis = kopfdaten(k)
    inhalt = f'''{seitenkopf(f"InselTicket {e(n)}", f"kopf-{k}.jpg")}

  <section class="inselkopf">
{ticketkasten(k, n, "In den Warenkorb", f"ticket:{k}", ebene='h2')}
  </section>

  <section class="gutscheine">
    <h2 class="gutscheine__titel">{e(d['ueberblick'])}</h2>
    <ul class="gutscheine__liste">
{chr(10).join(karten)}
    </ul>
    <p class="gutscheine__summe">{e(fakten[1])}</p>
    <p class="gutscheine__summe-knopf">{knopf("In den Warenkorb", f"ticket:{k}")}</p>
  </section>

{inselwahl(k)}'''
    seite(f'{k}.html', f'InselTicket {n} 2027 · Alle Gutscheine', k, inhalt,
          f'InselTicket {n} 2027: alle Gutscheine im Überblick. {preis[1]}')


def inseluebersicht():
    inhalt = f'''{seitenkopf("Die Inseln &amp; ihre Anbieter", "kopf-duenen.jpg", "center 60%")}

{ticketliste().replace('class="inseln"', 'class="inseln inseln--seite"')}'''
    seite('inseln.html', 'Die Inseln & ihre Anbieter · InselTicket', 'inseln', inhalt)


def so_funktionierts():
    # Sätze im Wortlaut der Live-Seite, als einzelne Kästen angeordnet.
    # Die kurzen Stichworte über den Kästen sind eine gestalterische Ergänzung von STUDIO ZUNDER.
    def ico(pfad):
        return f'<svg class="info__symbol" viewBox="0 0 32 32" aria-hidden="true">{pfad}</svg>'
    S = 'fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'
    symbole = {
        'heft': ico(f'<rect x="5" y="8" width="22" height="16" rx="2" {S}/><path d="M12 8v16" {S} stroke-dasharray="2 2.5"/><path d="M16 14h7M16 18h5" {S}/>'),
        'exklusiv': ico(f'<path d="M16 4l3.6 7.4 8.1 1.2-5.9 5.7 1.4 8.1L16 22.6l-7.2 3.8 1.4-8.1-5.9-5.7 8.1-1.2z" {S}/>'),
        'sparen': ico(f'<circle cx="16" cy="16" r="11" {S}/><path d="M20.5 11.5a5.5 5.5 0 1 0 0 9M9.5 14.5h8M9.5 17.5h8" {S}/>'),
        'vorlegen': ico(f'<rect x="9" y="4" width="14" height="24" rx="2.5" {S}/><path d="M13 9h6M13 13h6M13 17h4" {S}/>'),
        'zwei': '<span class="info__zahl" aria-hidden="true">2:1</span>',
        'rabatt': ico(f'<path d="M8 24L24 8" {S}/><circle cx="10" cy="10" r="3" {S}/><circle cx="22" cy="22" r="3" {S}/>'),
        'alle': ico(f'<path d="M6 9l3 3 5-6M6 18l3 3 5-6M18 9h8M18 18h8M18 26h8" {S}/>'),
    }
    kaesten = [
        ('heft', 'Das Heft',
         '<p>Das InselTicket ist ein kleines Gutscheinheft, in dem exklusive Gutscheine für Sie enthalten sind.</p>', ''),
        ('exklusiv', 'Exklusiv',
         '<p><strong>Diese Gutscheine erhalten Sie nur mit dem InselTicket!</strong></p>'
         '<p>Alle Angebote finden Sie unter der Rubrik <a href="inseln.html">"Die Insel &amp; Ihre Anbieter"</a>.</p>', ''),
        ('sparen', 'Sparen &amp; entdecken',
         '<p>Mit Ihrem Ticket können Sie mit Rabatt- und "2 für 1"-Gutscheinen auf der Insel Ihrer Wahl immer viel Geld sparen und Neues entdecken.</p>', ''),
        ('vorlegen', 'Einfach vorlegen',
         '<p>Bei der Nutzung legen Sie dann einfach das Ticket vor.</p>', ''),
        ('zwei', '2 für 1',
         '<p>Bei einem "2 für 1" - Angebot wird die jeweils günstigere oder preisgleiche Position nicht berechnet und ist somit für Sie kostenlos.</p>'
         '<p><strong>Sie zahlen also nur für eine Person - für die zweite Person ist es immer gratis!</strong></p>', ' info--betont'),
        ('rabatt', 'Rabatte',
         '<p>Und die Rabattgutscheine lösen Sie einfach beim jeweiligen Teilnehmer ein.</p>', ''),
        ('alle', 'Alle Angebote nutzen',
         '<p>P.S. Natürlich können Sie nicht nur ein, sondern alle Angebote Ihres InselTickets nutzen!</p>', ''),
    ]
    liste = '\n'.join(f'''      <li class="info{extra}">
        <div class="info__kopf">{symbole[k]}<span class="info__stichwort">{stich}</span></div>
        {text}
      </li>''' for k, stich, text, extra in kaesten)
    inhalt = f'''{seitenkopf("So funktioniert's", "kopf-duenen.jpg", "center 60%")}

  <article class="funktion">
    <h2 class="funktion__aufmacher">Maximale Freizeitgestaltung bei minimalen Kosten!</h2>
    <ul class="info-liste">
{liste}
    </ul>
    <div class="funktion__abschluss">
      <p>Das InselTicket ist streng limitiert.<br>Also gleich bestellen!</p>
      <a class="knopf" href="inseln.html">Zu den InselTickets</a>
    </div>
  </article>'''
    seite('so-funktionierts.html', "So funktioniert's · InselTicket", 'function', inhalt)


VORSCHAU = '<p class="shop__hinweis">Vorschau-Shop: In dieser Fassung wird keine Bestellung verschickt.</p>'

LEER = '''    <div class="textseite textseite--mittig" data-korb-leer>
      <p class="textseite__abschluss">Der Warenkorb ist leer.</p>
      <p>Bitte wählen Sie unter <a href="inseln.html">"Die Insel &amp; Ihre Anbieter"</a> Ihre gewünschten Tickets aus.</p>
      <p><a class="knopf" href="inseln.html">Zu den InselTickets</a></p>
    </div>'''


def summenkasten(knopf_html):
    return f'''      <aside class="summe" aria-label="Summe">
        <h2 class="summe__titel">Ihre Bestellung</h2>
        <dl class="summe__zeilen">
          <div><dt>Zwischensumme</dt><dd data-summe-zwischen></dd></div>
          <div data-summe-rabatt-zeile hidden><dt data-summe-rabatt-text>Sammelrabatt</dt><dd data-summe-rabatt></dd></div>
          <div class="summe__gesamt"><dt>Gesamt</dt><dd data-summe-gesamt></dd></div>
        </dl>
        <p class="summe__stufe" data-rabatt-hinweis></p>
        <p class="summe__rechnung">Keine Vorkasse, der Versand erfolgt mit beiliegender Rechnung.</p>
        {knopf_html}
      </aside>'''


def warenkorb():
    inhalt = f'''{seitenkopf("Warenkorb", "kopf-duenen.jpg", "center 60%")}

  <section class="shop" data-shop="warenkorb">
    {VORSCHAU}
{LEER}
    <div class="korb" data-korb-voll hidden>
      <ul class="korb__liste" data-korb-liste></ul>
{summenkasten('<a class="knopf" href="kasse.html">Zur Kasse</a>')}
    </div>
    <p class="shop__sammel">P.S.: Fahren Sie als Gruppe, Verein oder Club auf die Inseln? Dann lohnt sich für Sie eine Sammelbestellung, denn ab einem Einkaufswert von 50.- Euro gibt`s 10%, ab 100.- Euro satte 20% Rabatt!</p>
  </section>'''
    seite('warenkorb.html', 'Warenkorb · InselTicket', 'basket', inhalt, noindex=True)


def kasse():
    feld = lambda name, label, typ='text', pflicht=True, auto='', breit=False: (
        f'<label class="feld{" feld--breit" if breit else ""}"><span>{label}{" *" if pflicht else ""}</span>'
        f'<input name="{name}" type="{typ}"{" required" if pflicht else ""}{f" autocomplete={chr(34)}{auto}{chr(34)}" if auto else ""}></label>')
    inhalt = f'''{seitenkopf("Kasse", "kopf-duenen.jpg", "center 60%")}

  <section class="shop" data-shop="kasse">
    {VORSCHAU}
{LEER}
    <div class="korb" data-korb-voll hidden>
      <form class="kasse" data-kasse novalidate>
        <h2 class="kasse__titel">Rechnungs- und Lieferadresse</h2>
        <div class="kasse__felder">
          {feld('vorname', 'Vorname', auto='given-name')}
          {feld('nachname', 'Nachname', auto='family-name')}
          {feld('firma', 'Firma, Verein oder Club', pflicht=False, auto='organization', breit=True)}
          {feld('strasse', 'Straße und Hausnummer', auto='street-address', breit=True)}
          {feld('plz', 'PLZ', auto='postal-code')}
          {feld('ort', 'Ort', auto='address-level2')}
          {feld('email', 'E-Mail', typ='email', auto='email')}
          {feld('telefon', 'Telefon', typ='tel', pflicht=False, auto='tel')}
          <label class="feld feld--breit"><span>Anmerkung</span><textarea name="anmerkung" rows="3"></textarea></label>
        </div>

        <h2 class="kasse__titel">Zahlart</h2>
        <p class="kasse__zahlart"><span class="kasse__punkt" aria-hidden="true"></span>Kauf auf Rechnung</p>

        <label class="kasse__agb"><input type="checkbox" name="agb" required> <span>Ich habe die <a href="agb.html" target="_blank">AGB und die Widerrufsbelehrung</a> gelesen. *</span></label>
        <p class="kasse__fehler" data-kasse-fehler hidden>Bitte füllen Sie alle Pflichtfelder aus und bestätigen Sie die AGB.</p>
        <p class="kasse__pflicht">* Pflichtfeld</p>
      </form>
      <div class="kasse__seite">
        <ul class="korb__liste korb__liste--kurz" data-korb-liste data-nur-lesen></ul>
{summenkasten('<button class="knopf knopf--gross" type="submit" form="kasse-formular" data-bestellen>Zahlungspflichtig bestellen</button>')}
      </div>
    </div>

    <div class="danke" data-danke hidden>
      <h2 class="danke__titel">Vielen Dank für Ihre Bestellung!</h2>
      <p>Vorschau: In dieser Fassung wird keine Bestellung verschickt.</p>
      <div class="danke__uebersicht" data-danke-uebersicht></div>
      <p><a class="knopf" href="index.html">Zur Startseite</a></p>
    </div>
  </section>'''
    inhalt = inhalt.replace('<form class="kasse" data-kasse novalidate>', '<form class="kasse" id="kasse-formular" data-kasse novalidate>')
    seite('kasse.html', 'Kasse · InselTicket', 'basket', inhalt, noindex=True)


def rechtsseite(datei, quelle, titel, aktiv):
    roh = (QUELLEN / quelle).read_text()
    text = rechtstext(roh)
    # Überschrift der Quelle (erste fette Zeile) wird zum Seitentitel
    text = re.sub(r'^<p><strong>[^<]*</strong>(<br>)*', '<p>', text, count=1)
    text = re.sub(r'^<p>\s*</p>\s*', '', text)
    inhalt = f'''{seitenkopf(titel, "kopf-duenen.jpg", "center 60%")}

  <article class="textseite textseite--recht">
      {text}
  </article>'''
    seite(datei, f'{titel} · InselTicket', aktiv, inhalt)


if __name__ == '__main__':
    startseite()
    inseluebersicht()
    so_funktionierts()
    for k, n in INSELN:
        inselseite(k, n)
    warenkorb()
    kasse()
    produkte_js()
    rechtsseite('agb.html', 'agb.html', 'AGB / Widerruf', 'agb')
    rechtsseite('impressum.html', 'impressum.html', 'Impressum', 'impressum')
