"""Calcul des indicateurs de stabilité et de disponibilité des API."""

import pandas as pd

MOIS_FR = {
    1: "Janv.", 2: "Févr.", 3: "Mars", 4: "Avr.", 5: "Mai", 6: "Juin",
    7: "Juil.", 8: "Août", 9: "Sept.", 10: "Oct.", 11: "Nov.", 12: "Déc.",
}


def preparer(df):
    """Normalise les dates et ne garde que les jours ouvrés (lundi-vendredi)."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], utc=True).dt.tz_convert(None)
    df = df[df["date"].dt.weekday < 5]
    df["jour"] = df["date"].dt.normalize()
    return df


def jours_ouvres(debut, fin):
    """Nombre de jours ouvrés entre deux dates incluses."""
    return len(pd.bdate_range(debut, fin))


def calculer_kpi(df, nb_api_total, heures_par_jour=12, duree_incident=4):
    """
    Indicateurs de la période couverte par les incidents.

    Disponibilité = 1 - temps de panne / temps théorique, avec :
    - temps théorique = jours ouvrés de la période x nombre d'API x heures par jour
    - temps de panne  = nombre d'incidents x durée moyenne d'un incident
    """
    nb_incidents = len(df)
    api_impactees = df["signalement"].nunique()

    if nb_incidents == 0:
        jours = 0
    else:
        jours = jours_ouvres(df["jour"].min(), df["jour"].max())

    temps_total = jours * nb_api_total * heures_par_jour
    temps_panne = nb_incidents * duree_incident

    if temps_total > 0:
        disponibilite = min(max(1 - temps_panne / temps_total, 0), 1)
    else:
        disponibilite = 1.0

    return {
        "incidents": nb_incidents,
        "api_impactees": api_impactees,
        "api_stables": max(nb_api_total - api_impactees, 0),
        "jours_ouvres": jours,
        "disponibilite": disponibilite,
    }


def incidents_par_mois(df):
    """Nombre d'incidents par mois, dans l'ordre chronologique."""
    par_mois = (
        df.groupby(df["date"].dt.to_period("M"))
        .size()
        .reset_index(name="incidents")
        .sort_values("date")
    )
    par_mois["mois"] = par_mois["date"].apply(
        lambda p: f"{MOIS_FR[p.month]} {p.year}"
    )
    return par_mois[["mois", "incidents"]]


def top_api(df, n=10):
    """Les n API qui génèrent le plus d'incidents."""
    return (
        df.groupby("signalement")
        .size()
        .reset_index(name="incidents")
        .sort_values("incidents", ascending=False)
        .head(n)
    )
