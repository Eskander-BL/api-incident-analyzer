"""Lecture des mails d'alerte et extraction des signalements d'API."""

import re
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from pathlib import Path

import pandas as pd

# Un mail peut contenir plusieurs signalements :
# "Signalement ... de NOM-API ... URL concernée https://..."
PATTERN = re.compile(
    r"Signalement.*?de ([A-Z0-9\-_]+).*?URL concernée\s+(https?://\S+)",
    re.DOTALL,
)

COLONNES = ["date", "signalement", "url"]


def extraire_signalements(texte, date_mail):
    """Retourne une ligne par signalement trouvé dans le corps du mail."""
    return [
        {"date": date_mail, "signalement": api, "url": url}
        for api, url in PATTERN.findall(texte)
    ]


def lire_eml(contenu):
    """Mail au format standard .eml -> (date d'envoi, corps texte)."""
    msg = BytesParser(policy=policy.default).parsebytes(contenu)
    date_mail = parsedate_to_datetime(msg["Date"])
    corps = msg.get_body(preferencelist=("plain",)).get_content()
    return date_mail, corps


def lire_msg(contenu):
    """Mail Outlook .msg -> (date d'envoi, corps texte)."""
    import extract_msg  # dépendance optionnelle, seulement pour Outlook

    msg = extract_msg.Message(contenu)
    return pd.to_datetime(msg.date), msg.body


def lire_fichier(nom, contenu):
    """Lit un fichier .eml ou .msg et retourne ses signalements."""
    extension = Path(nom).suffix.lower()

    if extension == ".eml":
        date_mail, corps = lire_eml(contenu)
    elif extension == ".msg":
        date_mail, corps = lire_msg(contenu)
    else:
        raise ValueError(f"Format non pris en charge : {extension}")

    return extraire_signalements(corps, date_mail)


def lire_dossier(dossier):
    """Lit tous les mails d'un dossier et retourne un DataFrame dédoublonné."""
    lignes = []

    for fichier in sorted(Path(dossier).iterdir()):
        if fichier.suffix.lower() in (".eml", ".msg"):
            lignes.extend(lire_fichier(fichier.name, fichier.read_bytes()))

    df = pd.DataFrame(lignes, columns=COLONNES)
    return df.drop_duplicates(subset=COLONNES, ignore_index=True)
