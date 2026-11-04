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
        </a>
      </nav>
    </div>
  </div>
</header>'''


def seite(datei, titel, aktiv, inhalt, beschreibung=''):
    beschreibung = beschreibung or 'Exklusiv-Gutscheine für Ihren Urlaub auf Borkum, Norderney, Juist, Wangerooge und Helgoland.'
    doc = f'''<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
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

<script src="assets/js/menue.js"></script>
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
          <a class="knopf" href="{knopf_ziel}">{knopf_text}</a>
        </div>
      </div>'''


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
{ticketkasten(k, n, "In den Warenkorb", f"warenkorb.html?ticket={d['kaufen']}", ebene='h2')}
  </section>

  <section class="gutscheine">
    <h2 class="gutscheine__titel">{e(d['ueberblick'])}</h2>
    <ul class="gutscheine__liste">
{chr(10).join(karten)}
    </ul>
    <p class="gutscheine__summe">{e(fakten[1])}</p>
    <p class="gutscheine__summe-knopf"><a class="knopf" href="warenkorb.html?ticket={d['kaufen']}">In den Warenkorb</a></p>
  </section>

{inselwahl(k)}'''
    seite(f'{k}.html', f'InselTicket {n} 2027 · Alle Gutscheine', k, inhalt,
          f'InselTicket {n} 2027: alle Gutscheine im Überblick. {preis[1]}')


def inseluebersicht():
    inhalt = f'''{seitenkopf("Die Inseln &amp; ihre Anbieter", "kopf-duenen.jpg", "center 60%")}

{ticketliste().replace('class="inseln"', 'class="inseln inseln--seite"')}'''
    seite('inseln.html', 'Die Inseln & ihre Anbieter · InselTicket', 'inseln', inhalt)


def so_funktionierts():
    # Wortlaut der Live-Seite; Zeilenumbrüche des alten Layouts entfallen, Absätze bleiben
    inhalt = f'''{seitenkopf("So funktioniert's", "kopf-duenen.jpg", "center 60%")}

  <article class="textseite textseite--mittig">
    <h2 class="textseite__aufmacher">Maximale Freizeitgestaltung bei minimalen Kosten!</h2>
    <p>Das InselTicket ist ein kleines Gutscheinheft, in dem exklusive Gutscheine für Sie enthalten sind.</p>
    <p><strong>Diese Gutscheine erhalten Sie nur mit dem InselTicket!</strong> Alle Angebote finden Sie unter der Rubrik <a href="inseln.html">"Die Insel &amp; Ihre Anbieter"</a>.</p>
    <p>Mit Ihrem Ticket können Sie mit Rabatt- und "2 für 1"-Gutscheinen auf der Insel Ihrer Wahl immer viel Geld sparen und Neues entdecken.</p>
    <p>Bei der Nutzung legen Sie dann einfach das Ticket vor.</p>
    <p>Bei einem "2 für 1" - Angebot wird die jeweils günstigere oder preisgleiche Position nicht berechnet und ist somit für Sie kostenlos.</p>
    <p>Sie zahlen also nur für eine Person - für die zweite Person ist es immer gratis!</p>
    <p>Und die Rabattgutscheine lösen Sie einfach beim jeweiligen Teilnehmer ein.</p>
    <p>P.S. Natürlich können Sie nicht nur ein, sondern alle Angebote Ihres InselTickets nutzen!</p>
    <p class="textseite__abschluss">Das InselTicket ist streng limitiert.<br>Also gleich bestellen!</p>
    <p><a class="knopf" href="inseln.html">Zu den InselTickets</a></p>
  </article>'''
    seite('so-funktionierts.html', "So funktioniert's · InselTicket", 'function', inhalt)


def warenkorb():
    inhalt = f'''{seitenkopf("Warenkorb", "kopf-duenen.jpg", "center 60%")}

  <article class="textseite textseite--mittig">
    <p class="textseite__abschluss">Der Warenkorb ist leer.</p>
    <p>Bitte wählen Sie unter <a href="inseln.html">"Die Insel &amp; Ihre Anbieter"</a> Ihre gewünschten Tickets aus.</p>
    <p><a class="knopf" href="inseln.html">Zu den InselTickets</a></p>
  </article>'''
    seite('warenkorb.html', 'Warenkorb · InselTicket', 'basket', inhalt)


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
    rechtsseite('agb.html', 'agb.html', 'AGB / Widerruf', 'agb')
    rechtsseite('impressum.html', 'impressum.html', 'Impressum', 'impressum')
