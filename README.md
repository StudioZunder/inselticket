# InselTicket · Website-Prototyp

Neuer Webauftritt für InselTicket (Gutscheinhefte für Borkum, Norderney, Juist, Wangerooge und Helgoland).
Gestaltung und Umsetzung: STUDIO ZUNDER. Stand: lokaler HTML-Prototyp, später WordPress mit WooCommerce und eigenem Theme.

## Ansehen

`index.html` im Browser öffnen.

## Seiten bauen

```
python3 werkzeug/seiten_bauen.py
```

Der Generator erzeugt alle HTML-Seiten aus einer gemeinsamen Vorlage.

- Gutscheindaten je Insel: `werkzeug/inseln.json`
- Texte der bisherigen Website (wörtlich): `werkzeug/quellen/`
- Gestaltung: `assets/css/style.css` (Blau #102D56, Orange #EE7F00, Sand #DBD6BC, Roboto Condensed)
