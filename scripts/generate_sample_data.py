"""
Génère des mails d'alerte fictifs (.eml) pour tester le dashboard.

Aucune donnée réelle : noms d'API et URL inventés, domaine api.exemple.com.
Usage : python scripts/generate_sample_data.py
"""

import random
from email.message import EmailMessage
from email.utils import format_datetime
from pathlib import Path

import pandas as pd

DOSSIER = Path(__file__).resolve().parent.parent / "data" / "sample_emails"

API = [
    "API-COMMANDES", "API-FACTURATION", "API-CLIENTS", "API-STOCKS",
    "API-PAIEMENTS", "API-LIVRAISONS", "API-CATALOGUE", "API-AUTH",
    "API-NOTIFICATIONS", "API-RETOURS", "API-FOURNISSEURS", "API-CONTRATS",
    "API-PLANNING", "API-DOCUMENTS", "API-REPORTING",
]

# Quelques API volontairement plus instables que les autres
POIDS = [8, 6, 5, 4, 4, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1]


def corps_alerte(signalements):
    blocs = [
        f"Signalement d'incident de {api} sur l'environnement de production.\n"
        f"URL concernée https://api.exemple.com/v1/{api.split('-', 1)[1].lower()}\n"
        for api in signalements
    ]
    return "Bonjour,\n\n" + "\n".join(blocs) + "\nCordialement,\nSupervision"


def generer(nb_mails=180, graine=42):
    random.seed(graine)
    DOSSIER.mkdir(parents=True, exist_ok=True)

    jours = pd.bdate_range("2026-01-05", "2026-06-30")

    for i in range(nb_mails):
        jour = random.choice(jours)
        envoi = jour + pd.Timedelta(hours=random.randint(7, 19), minutes=random.randint(0, 59))
        nb = random.choices([1, 2, 3], weights=[70, 22, 8])[0]
        signalements = random.choices(API, weights=POIDS, k=nb)

        msg = EmailMessage()
        msg["From"] = "supervision@exemple.com"
        msg["To"] = "equipe-run@exemple.com"
        msg["Subject"] = f"[ALERTE] {nb} signalement(s) API"
        msg["Date"] = format_datetime(envoi.to_pydatetime())
        msg.set_content(corps_alerte(signalements))

        (DOSSIER / f"alerte_{i:03d}.eml").write_bytes(bytes(msg))

    print(f"{nb_mails} mails générés dans {DOSSIER}")


if __name__ == "__main__":
    generer()
