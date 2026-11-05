import pandas as pd

from incidents.metrics import calculer_kpi, incidents_par_mois, jours_ouvres, preparer
from incidents.parser import extraire_signalements

DATE = pd.Timestamp("2026-03-02 09:00")


def test_un_mail_avec_plusieurs_signalements():
    texte = (
        "Signalement d'incident de API-STOCKS en production.\n"
        "URL concernée https://api.exemple.com/v1/stocks\n\n"
        "Signalement d'incident de API-AUTH en production.\n"
        "URL concernée https://api.exemple.com/v1/auth\n"
    )
    lignes = extraire_signalements(texte, DATE)
    assert [l["signalement"] for l in lignes] == ["API-STOCKS", "API-AUTH"]


def test_mail_sans_signalement():
    assert extraire_signalements("Bonjour, rien à signaler.", DATE) == []


def test_jours_ouvres_exclut_le_week_end():
    # du lundi 2 au dimanche 8 mars 2026 : 5 jours ouvrés
    assert jours_ouvres("2026-03-02", "2026-03-08") == 5


def test_deux_mails_le_meme_jour_ne_comptent_pas_deux_jours():
    df = preparer(pd.DataFrame({
        "date": ["2026-03-02 09:00", "2026-03-02 15:00"],
        "signalement": ["API-A", "API-B"],
        "url": ["u1", "u2"],
    }))
    kpi = calculer_kpi(df, nb_api_total=10, heures_par_jour=12, duree_incident=4)
    assert kpi["jours_ouvres"] == 1
    # 1 - (2 x 4h) / (1 jour x 10 API x 12h)
    assert abs(kpi["disponibilite"] - (1 - 8 / 120)) < 1e-9


def test_les_week_ends_sont_ignores():
    df = preparer(pd.DataFrame({
        "date": ["2026-03-07 10:00"],  # samedi
        "signalement": ["API-A"],
        "url": ["u1"],
    }))
    assert df.empty


def test_mois_dans_l_ordre_chronologique():
    df = preparer(pd.DataFrame({
        "date": ["2026-04-01", "2026-01-05", "2026-02-02"],
        "signalement": ["A", "B", "C"],
        "url": ["u", "u", "u"],
    }))
    assert list(incidents_par_mois(df)["mois"]) == ["Janv. 2026", "Févr. 2026", "Avr. 2026"]
