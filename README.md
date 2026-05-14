# tsv_blog_notifications

Odoo 18 Addon für den TSV Schwerin. Sendet automatisch eine E-Mail an alle aktiven
Vereinsmitglieder, wenn ein neuer Blogbeitrag veröffentlicht wird. Jede Benachrichtigung
enthält zwei Abmelde-Links, über die Empfänger sich gezielt von einem Blog oder von allen
Blog-Benachrichtigungen abmelden können.

---

## Voraussetzungen

- Odoo 18
- Modul `website_blog` installiert (Website → Blog)
- Modul `tsv_membership_form` installiert
- Ausgehender Mailserver konfiguriert (*Einstellungen → Technisch → E-Mail → Ausgehende
  Mailserver*)

---

## Installation

```bash
docker compose exec web odoo -d tsv_18 \
  --db_host=db --db_user=odoo --db_password=odoo \
  -i tsv_blog_notifications --stop-after-init
```

---

## Funktionsweise

### Versand

Sobald ein Blogbeitrag von **unveröffentlicht → veröffentlicht** wechselt (Feld
`is_published`), ruft Odoo automatisch `_notify_members()` auf.

Empfänger sind alle `res.partner`-Einträge, auf die alle drei Bedingungen zutreffen:

| Bedingung | Bedeutung |
|---|---|
| `tsv_membership_state = 'member'` | Aktives Vereinsmitglied |
| `blog_notification_optout = False` | Nicht global abgemeldet |
| Blog **nicht** in `blog_optout_blog_ids` | Nicht von diesem Blog abgemeldet |
| `email` vorhanden | E-Mail-Adresse bekannt |

Für jeden Empfänger wird eine individuelle E-Mail mit zwei personalisierten
Abmelde-Links erstellt und über die Odoo-Mail-Queue (`mail.mail`) versendet.

### Abmelde-Token

Beim ersten Versand an einen Partner wird einmalig ein kryptografisch sicherer Token
generiert (`secrets.token_urlsafe(32)`) und in `blog_optout_token` gespeichert. Der
Token ist dauerhaft gültig und wird **nicht** nach Verwendung ungültig gemacht — er
dient als stabiler Identifikator für alle künftigen Abmelde-Links dieses Partners.

### Abmelde-Links in der E-Mail

Jede Benachrichtigungs-E-Mail enthält im Footer zwei Links:

| Link | Effekt |
|---|---|
| *Nur von diesem Blog abmelden* | `/blog/abmelden/<token>/<blog_id>` → Blog wird in `blog_optout_blog_ids` eingetragen |
| *Von allen Blog-Benachrichtigungen abmelden* | `/blog/abmelden/<token>` → `blog_notification_optout` wird auf `True` gesetzt |

Die Abmeldeseite ist öffentlich erreichbar (`auth='public'`) — kein Login erforderlich.

---

## Neue Felder auf `res.partner`

| Feld | Typ | Bedeutung |
|---|---|---|
| `blog_notification_optout` | Boolean | Globale Abmeldung von allen Blog-Benachrichtigungen |
| `blog_optout_blog_ids` | Many2many → `blog.blog` | Einzelne Blogs, von denen sich der Partner abgemeldet hat |
| `blog_optout_token` | Char | Stabiler Token für Abmelde-Links (wird nicht kopiert) |

---

## Konfiguration

### Ausgehender Mailserver

Das Modul nutzt Odoos Standard-Mail-Queue (`mail.mail`). Es muss mindestens ein
ausgehender Mailserver konfiguriert sein:

*Einstellungen → Technisch → E-Mail → Ausgehende Mailserver*

### E-Mail-Absender

Der Absendername und die Absenderadresse richten sich nach den globalen Odoo-Einstellungen
(*Einstellungen → Allgemein → E-Mail-Adresse für ausgehende E-Mails*).

### E-Mail-Template anpassen

Das HTML-Layout der Benachrichtigungs-E-Mail ist in `views/templates.xml` als
QWeb-Template (`tsv_blog_notifications.blog_notification_email_body`) definiert. Änderungen
am Erscheinungsbild können dort direkt vorgenommen werden.

### Abmeldestatus im Backend verwalten

Im Partner-Formular gibt es eine Seite **Blog-Benachrichtigungen** (sichtbar für Nutzer
der Gruppe *Technisch* / `base.group_no_one`). Dort lassen sich Opt-outs manuell einsehen
und korrigieren, z. B. um einen Partner auf Wunsch wieder anzumelden.

Um die Seite für normale Administratoren sichtbar zu machen, das `groups`-Attribut in
`views/res_partner_views.xml` auf `base.group_system` ändern oder ganz entfernen.

---

## Einschränkungen

- Das Modul versendet **keine** Benachrichtigungen für Beiträge, die beim ersten
  Speichern direkt als veröffentlicht angelegt werden, ohne vorher den Entwurfszustand
  durchlaufen zu haben — dies ist in der Standard-Odoo-Redaktion jedoch der Regelfall.
- Bei sehr großen Mitgliederzahlen (> 1.000) empfiehlt sich eine asynchrone Verarbeitung
  über einen Cron-Job statt des direkten Versands im `write()`-Aufruf.
