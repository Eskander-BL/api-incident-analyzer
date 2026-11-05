# Analyse des incidents API

Un dashboard Python qui transforme des mails d'alerte de supervision en indicateurs exploitables : API les plus instables, évolution des incidents et disponibilité globale.

> Version publique d'un outil que j'ai conçu pendant mon alternance. Cette version est réécrite et fonctionne uniquement sur des **données fictives** : aucune donnée, aucun nom d'API ni aucune URL d'entreprise.

<!-- <img width="1889" height="564" alt="image" src="https://github.com/user-attachments/assets/13349867-9afc-47d6-a2a6-b386fc5e2efc" />
 -->

## Le besoin

Une équipe de production reçoit des centaines de mails d'alerte, chacun signalant une ou plusieurs API en défaut. Les analyser à la main dans Excel prenait du temps et ne donnait aucune vue d'ensemble : quelles API sont les plus instables ? Les incidents augmentent-ils ? Quelle est la disponibilité réelle du service ?

## Ce que fait l'outil

1. **Lecture des mails** : `.eml` (format standard) ou `.msg` (Outlook), déposés par glisser-déposer.
2. **Extraction** de chaque signalement : date, API concernée, URL. Un mail peut contenir plusieurs signalements.
3. **Dédoublonnage** : un même mail déposé deux fois n'est compté qu'une fois.
4. **Indicateurs** : incidents, API impactées, API stables, jours ouvrés, disponibilité.
5. **Graphiques** : incidents par mois, top des API instables, répartition des incidents.

## Comment la disponibilité est calculée

```
Temps théorique = jours ouvrés de la période × nombre d'API × heures de service par jour
Temps de panne  = nombre d'incidents × durée moyenne d'un incident
Disponibilité   = 1 − temps de panne / temps théorique
```

Hypothèses par défaut, modifiables dans la barre latérale : 12 h de service par jour, 4 h par incident, jours ouvrés uniquement (lundi-vendredi).

## Données

Toutes les données du repo sont **inventées** par le script `scripts/generate_sample_data.py` : 15 API fictives (API-COMMANDES, API-FACTURATION…), un domaine d'exemple (`api.exemple.com`) et 180 mails d'alerte générés aléatoirement. L'outil fonctionne de la même façon avec de vrais mails d'alerte, qui ne sont jamais publiés.

## Lancer le projet

```bash
pip install -r requirements.txt
python scripts/generate_sample_data.py   # crée 180 mails fictifs dans data/sample_emails
streamlit run app.py
```

Dans l'application, clique sur **« Charger les données d'exemple »**.

## Tests

```bash
pytest
```

Les tests vérifient l'extraction de plusieurs signalements dans un même mail, l'exclusion des week-ends, le calcul des jours ouvrés, la disponibilité et l'ordre chronologique des mois.

## Structure

```
app.py                         Dashboard Streamlit
incidents/parser.py            Lecture des mails et extraction des signalements
incidents/metrics.py           Calcul des indicateurs
scripts/generate_sample_data.py  Génération des données fictives
tests/                         Tests unitaires
```

## Outils

Python · Pandas · Streamlit · Plotly · extract-msg · pytest

---

Réalisé par **Eskander Bellarbi** · [LinkedIn](https://www.linkedin.com/in/eskander-bellarbi-8963aa18a/)
