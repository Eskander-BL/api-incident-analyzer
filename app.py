import pandas as pd
import plotly.express as px
import streamlit as st

from incidents.metrics import calculer_kpi, incidents_par_mois, preparer, top_api
from incidents.parser import COLONNES, lire_dossier, lire_fichier

DOSSIER_EXEMPLE = "data/sample_emails"

st.set_page_config(page_title="Analyse des incidents API", layout="wide")

st.title("Analyse des incidents API")
st.write(
    "Déposez des mails d'alerte (.eml ou .msg Outlook) pour obtenir "
    "les API les plus instables et la disponibilité globale."
)

# -----------------------
# PARAMÈTRES MÉTIER
# -----------------------

with st.sidebar:
    st.header("Paramètres")
    nb_api_total = st.number_input(
        "Nombre total d'API sur la période", min_value=1, value=25, step=1
    )
    heures_par_jour = st.number_input(
        "Heures de service par jour", min_value=1, max_value=24, value=12
    )
    duree_incident = st.number_input(
        "Durée moyenne d'un incident (h)", min_value=0.5, value=4.0, step=0.5
    )

# -----------------------
# DONNÉES
# -----------------------

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=COLONNES)

col_upload, col_actions = st.columns([2, 1])

with col_upload:
    fichiers = st.file_uploader(
        "Mails d'alerte", type=["eml", "msg"], accept_multiple_files=True
    )

with col_actions:
    if st.button("Charger les données d'exemple"):
        st.session_state.data = lire_dossier(DOSSIER_EXEMPLE)
    st.caption("Données d'exemple 100 % fictives, générées par script.")
    if st.button("Réinitialiser"):
        st.session_state.data = pd.DataFrame(columns=COLONNES)

if fichiers:
    lignes = []
    for fichier in fichiers:
        try:
            lignes.extend(lire_fichier(fichier.name, fichier.getvalue()))
        except Exception as erreur:
            st.warning(f"Impossible de lire {fichier.name} : {erreur}")

    if lignes:
        total = pd.concat(
            [st.session_state.data, pd.DataFrame(lignes, columns=COLONNES)],
            ignore_index=True,
        ).drop_duplicates(subset=COLONNES, ignore_index=True)
        ajoutes = len(total) - len(st.session_state.data)
        st.session_state.data = total
        st.success(f"{ajoutes} nouveaux incidents ajoutés")

if st.session_state.data.empty:
    st.info("Déposez des mails ou chargez les données d'exemple pour commencer.")
    st.stop()

df = preparer(st.session_state.data)

# -----------------------
# INDICATEURS
# -----------------------

kpi = calculer_kpi(df, nb_api_total, heures_par_jour, duree_incident)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Incidents", kpi["incidents"])
col2.metric("API impactées", kpi["api_impactees"])
col3.metric("API stables", kpi["api_stables"])
col4.metric("Jours ouvrés", kpi["jours_ouvres"])
col5.metric("Disponibilité", f"{kpi['disponibilite']:.2%}")

# -----------------------
# GRAPHIQUES
# -----------------------

st.plotly_chart(
    px.bar(incidents_par_mois(df), x="mois", y="incidents", title="Incidents par mois"),
    use_container_width=True,
)

top_n = st.slider("Nombre d'API à afficher", 3, 20, 10)
top = top_api(df, top_n)

col_gauche, col_droite = st.columns(2)

with col_gauche:
    fig_top = px.bar(
        top, x="incidents", y="signalement", orientation="h",
        title=f"Top {top_n} des API générant des incidents",
    )
    fig_top.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig_top, use_container_width=True)

with col_droite:
    st.plotly_chart(
        px.pie(top, values="incidents", names="signalement",
               title="Répartition des incidents"),
        use_container_width=True,
    )

st.subheader("Incidents")
st.dataframe(df[COLONNES], use_container_width=True)
