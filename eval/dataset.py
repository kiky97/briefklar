"""Synthetic evaluation letters with hand-written gold labels.

All senders, people, addresses and reference numbers are fictional. The letters imitate
the style of real Swiss administrative mail (DE/FR/IT) but contain no real personal data.

Gold fields:
  type            expected letter_type
  dates           every calendar date that matters (ISO)
  deadlines       subset of `dates` that are deadlines for the recipient
  amounts         every money amount that matters
  actions         list of action groups; a group counts as found if ANY of its keywords
                  appears (case-insensitive) in the model's English action list
"""

LETTERS = [
    {
        "id": "de_tax_invoice",
        "lang": "de",
        "type": "tax",
        "dates": ["2026-11-30", "2026-11-12"],
        "deadlines": ["2026-11-30", "2026-11-12"],
        "amounts": [2486.40],
        "actions": [["pay", "transfer"], ["objection", "object", "appeal", "einsprache", "contest", "dispute"]],
        "text": """Kantonales Steueramt
Abteilung Bezug

Herr Daniel Beispiel
Rosenweg 12
8400 Musterstadt

Musterstadt, 12. Oktober 2026

Steuerrechnung Staats- und Gemeindesteuern 2025
Referenz-Nr.: 2025-448-71203

Sehr geehrter Herr Beispiel

Gestützt auf die definitive Veranlagung stellen wir Ihnen folgenden Betrag in Rechnung:

Staats- und Gemeindesteuern 2025: CHF 2'486.40

Der Betrag ist bis spätestens 30.11.2026 mit dem beiliegenden QR-Einzahlungsschein zu überweisen. Bei verspäteter Zahlung wird ein Verzugszins erhoben.

Gegen die Veranlagung kann bis am 12. November 2026 schriftlich Einsprache erhoben werden. Die Einsprache ist zu begründen.

Freundliche Grüsse
Kantonales Steueramt""",
    },
    {
        "id": "de_parking_fine",
        "lang": "de",
        "type": "fine",
        "dates": ["2026-09-28", "2026-10-31"],
        "deadlines": ["2026-10-31"],
        "amounts": [120.00],
        "actions": [["pay"]],
        "text": """Stadtpolizei Musterstadt
Ordnungsbussen

Frau Amina Testperson
Lindenstrasse 3
3000 Musterstadt

Ordnungsbusse Nr. OB-2026-55102

Sehr geehrte Frau Testperson

Am 28.09.2026 um 14:35 Uhr wurde Ihr Fahrzeug (Kontrollschild XX 123456) an der Bahnhofstrasse im Parkverbot abgestellt.

Gemäss Ordnungsbussengesetz wird dafür eine Busse von CHF 120.00 erhoben.

Bitte bezahlen Sie den Betrag bis zum 31.10.2026. Wird die Busse nicht fristgerecht bezahlt, wird ein ordentliches Strafverfahren eingeleitet, wodurch zusätzliche Kosten entstehen.

Stadtpolizei Musterstadt""",
    },
    {
        "id": "de_permit_renewal",
        "lang": "de",
        "type": "residence_permit",
        "dates": ["2027-01-15", "2026-12-01"],
        "deadlines": ["2026-12-01"],
        "amounts": [95.00],
        "actions": [["form", "application", "submit", "send"], ["passport"], ["contract", "employment"], ["pay", "fee"]],
        "text": """Migrationsamt des Kantons
Sektion Aufenthalt

Herr Bereket Muster
Feldweg 8
6000 Musterstadt

Verlängerung der Aufenthaltsbewilligung B
Dossier-Nr.: MA-883-2041

Sehr geehrter Herr Muster

Ihre Aufenthaltsbewilligung B läuft am 15.01.2027 ab. Damit wir die Verlängerung prüfen können, senden Sie uns bitte bis spätestens 01.12.2026 folgende Unterlagen:

- das ausgefüllte Gesuchsformular (beiliegend)
- eine Kopie Ihres gültigen Reisepasses
- eine Kopie Ihres aktuellen Arbeitsvertrags

Die Gebühr für die Verlängerung beträgt CHF 95.00 und wird nach Eingang des Gesuchs in Rechnung gestellt.

Reichen Sie die Unterlagen nicht fristgerecht ein, kann dies Folgen für Ihren Aufenthalt haben.

Freundliche Grüsse
Migrationsamt""",
    },
    {
        "id": "de_insurance_reminder",
        "lang": "de",
        "type": "health_insurance",
        "dates": ["2026-10-20"],
        "deadlines": ["2026-10-20"],
        "amounts": [387.20, 30.00],
        "actions": [["pay"]],
        "text": """Gesundheitskasse Muster AG
Inkasso

Frau Olena Beispiel
Bergstrasse 21
9000 Musterstadt

1. Mahnung – Versicherten-Nr. 756.0000.0000.01

Sehr geehrte Frau Beispiel

Trotz unserer Rechnung ist die Prämie für den Monat September 2026 noch offen:

Offener Betrag: CHF 387.20

Bitte begleichen Sie diesen Betrag bis zum 20.10.2026. Erfolgt bis dann keine Zahlung, müssen wir eine Mahngebühr von CHF 30.00 erheben und die Betreibung einleiten.

Falls Sie den Betrag bereits bezahlt haben, betrachten Sie dieses Schreiben als gegenstandslos.

Freundliche Grüsse
Gesundheitskasse Muster AG""",
    },
    {
        "id": "de_debt_collection_no_date",
        "lang": "de",
        "type": "debt_collection",
        "dates": [],
        "deadlines": [],
        "amounts": [1150.00, 73.30],
        "actions": [["pay"], ["rechtsvorschlag", "object", "dispute", "contest", "oppose"]],
        "text": """Betreibungsamt Musterstadt

Zahlungsbefehl
Betreibung Nr. 26-08814

Schuldner: Herr Mehmet Testmann, Seeweg 5, 4000 Musterstadt
Gläubiger: Elektro Muster GmbH, Industriestrasse 1, 4000 Musterstadt

Forderung: CHF 1'150.00 nebst Zins zu 5 % seit Fälligkeit
Kosten des Zahlungsbefehls: CHF 73.30
Forderungsgrund: Rechnung für Elektroinstallation

Der Schuldner wird aufgefordert, den Gläubiger für die angegebene Forderung samt Betreibungskosten binnen 20 Tagen zu befriedigen.

Will der Schuldner die Forderung oder einen Teil davon bestreiten, so hat er dies innert 10 Tagen nach Zustellung dieses Zahlungsbefehls dem Betreibungsamt mündlich oder schriftlich zu erklären (Rechtsvorschlag zu erheben).

Betreibungsamt Musterstadt""",
    },
    {
        "id": "de_rav_appointment",
        "lang": "de",
        "type": "employment",
        "dates": ["2026-10-21"],
        "deadlines": [],
        "amounts": [],
        "actions": [["appointment", "attend", "meeting", "go to", "come"], ["job search", "proof", "applications", "arbeitsbemühungen", "form"]],
        "text": """Regionales Arbeitsvermittlungszentrum (RAV) Musterstadt

Frau Lucía Probe
Hauptgasse 7
5000 Musterstadt

Einladung zum Beratungsgespräch

Sehr geehrte Frau Probe

Wir laden Sie zu einem Beratungsgespräch ein:

Datum: Mittwoch, 21.10.2026
Zeit: 09:30 Uhr
Ort: RAV Musterstadt, Büro 2.14

Bitte bringen Sie das ausgefüllte Formular «Nachweis der persönlichen Arbeitsbemühungen» für den Monat September mit.

Bitte beachten Sie: Wenn Sie ohne entschuldbaren Grund nicht erscheinen, kann Ihr Anspruch auf Arbeitslosenentschädigung für einige Tage eingestellt werden. Bei Verhinderung melden Sie sich bitte vorgängig telefonisch.

Freundliche Grüsse
Ihre Personalberaterin""",
    },
    {
        "id": "de_tax_return_reminder",
        "lang": "de",
        "type": "tax",
        "dates": ["2026-11-16"],
        "deadlines": ["2026-11-16"],
        "amounts": [1000.00],
        "actions": [["tax return", "submit", "file", "steuererklärung"]],
        "text": """Gemeindesteueramt Musterwil

Herr Arben Exempel
Dorfstrasse 2
8500 Musterwil

Mahnung: Steuererklärung 2025

Sehr geehrter Herr Exempel

Ihre Steuererklärung 2025 ist bei uns noch nicht eingegangen. Wir fordern Sie auf, die vollständig ausgefüllte Steuererklärung bis zum 16. November 2026 einzureichen.

Wird die Steuererklärung nicht fristgerecht eingereicht, erfolgt eine Veranlagung nach pflichtgemässem Ermessen. Zudem kann eine Ordnungsbusse von bis zu CHF 1'000.00 ausgesprochen werden.

Freundliche Grüsse
Gemeindesteueramt Musterwil""",
    },
    {
        "id": "fr_tax_documents",
        "lang": "fr",
        "type": "tax",
        "dates": ["2026-11-20"],
        "deadlines": ["2026-11-20"],
        "amounts": [],
        "actions": [["send", "provide", "submit", "documents", "certificate"]],
        "text": """Administration fiscale cantonale
Service de taxation

Madame Yasmin Exemple
Chemin des Lilas 9
1000 Villemodèle

Demande de renseignements – Période fiscale 2025
N° de contribuable : 41.552.903

Madame,

Afin de pouvoir procéder à votre taxation, nous vous prions de nous faire parvenir d'ici au 20 novembre 2026 les documents suivants :

- l'attestation de salaire de votre employeur pour l'année 2025
- les justificatifs de vos frais de garde d'enfants

Sans réponse de votre part dans ce délai, nous procéderons à une taxation d'office.

Veuillez agréer, Madame, nos salutations distinguées.

Administration fiscale cantonale""",
    },
    {
        "id": "fr_school_camp",
        "lang": "fr",
        "type": "school",
        "dates": ["2026-11-05", "2026-10-28", "2026-11-15"],
        "deadlines": ["2026-10-28", "2026-11-15"],
        "amounts": [180.00],
        "actions": [["confirm", "reply", "register", "attendance"], ["pay"]],
        "text": """Établissement scolaire de Villemodèle

Aux parents de l'élève Noah Exemple, classe 7P

Villemodèle, le 2 octobre 2026

Chers parents,

Nous avons le plaisir de vous inviter à une séance d'information sur le camp de ski qui aura lieu le jeudi 5 novembre 2026 à 18h00, à l'aula du collège.

Merci de nous confirmer votre présence au plus tard le 28 octobre 2026 au moyen du coupon-réponse ci-joint.

La participation financière des parents au camp s'élève à CHF 180.00. Le montant est à verser d'ici au 15 novembre 2026. Si cette somme représente une difficulté pour votre famille, n'hésitez pas à contacter la direction en toute confidentialité.

Avec nos meilleures salutations,
La direction""",
    },
    {
        "id": "fr_rent_increase",
        "lang": "fr",
        "type": "housing",
        "dates": ["2027-01-01"],
        "deadlines": [],
        "amounts": [1640.00, 1715.00],
        "actions": [["contest", "challenge", "dispute", "conciliation", "object"]],
        "text": """Régie Immobilière Modèle SA

Monsieur Tran Exemple
Avenue du Lac 15
1200 Villemodèle

Notification de hausse de loyer – Appartement 3.5 pièces, 2e étage
Bail n° RM-7781

Monsieur,

Conformément à l'art. 269d CO, nous vous notifions sur formule officielle une adaptation de votre loyer à partir du 1er janvier 2027.

Loyer net actuel : CHF 1'640.00 par mois
Nouveau loyer net : CHF 1'715.00 par mois
Motif : hausse du taux hypothécaire de référence

Si vous estimez cette hausse abusive, vous pouvez la contester devant la Commission de conciliation en matière de baux et loyers dans les 30 jours suivant sa réception.

Nous vous prions d'agréer, Monsieur, nos salutations distinguées.

Régie Immobilière Modèle SA""",
    },
    {
        "id": "it_premium_reduction",
        "lang": "it",
        "type": "social_services",
        "dates": ["2026-11-15"],
        "deadlines": ["2026-11-15"],
        "amounts": [],
        "actions": [["send", "submit", "documents", "provide"]],
        "text": """Istituto delle assicurazioni sociali
Ufficio della riduzione dei premi

Signora Fatima Esempio
Via Centrale 4
6500 Cittàmodello

Riduzione dei premi dell'assicurazione malattia 2027 – documenti mancanti
Pratica n. RIPAM-2027-30418

Gentile Signora Esempio,

per poter esaminare la sua domanda di riduzione dei premi le chiediamo di inviarci entro il 15 novembre 2026 i seguenti documenti:

- copia della decisione di tassazione 2025
- copia della polizza della cassa malati per il 2027

Se i documenti non ci perverranno entro tale termine, la domanda sarà considerata ritirata.

Distinti saluti
Istituto delle assicurazioni sociali""",
    },
    {
        "id": "it_speeding_fine",
        "lang": "it",
        "type": "fine",
        "dates": ["2026-09-14", "2026-11-10"],
        "deadlines": ["2026-11-10"],
        "amounts": [250.00],
        "actions": [["pay"], ["opposition", "object", "contest", "dispute", "opposizione"]],
        "text": """Polizia cantonale
Servizio contravvenzioni

Signor Giorgi Prova
Via del Sole 11
6900 Cittàmodello

Multa disciplinare n. MD-26-77310

Egregio Signor Prova,

il 14.09.2026 alle ore 07:52 il veicolo immatricolato a suo nome è stato rilevato a 71 km/h in una zona con limite di 50 km/h (via Stazione).

Per questa infrazione le viene inflitta una multa di CHF 250.00, da pagare entro il 10.11.2026.

Se non era lei alla guida o contesta l'infrazione, può presentare opposizione per iscritto entro lo stesso termine. In caso di mancato pagamento verrà avviata una procedura penale ordinaria.

Distinti saluti
Polizia cantonale""",
    },
]
