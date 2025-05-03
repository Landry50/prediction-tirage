import streamlit as st
import pandas as pd
import numpy as np
import datetime
import re
from collections import Counter

# Chargement des données Excel
FICHIER = "Donnees_Tirage.xlsx"

@st.cache_data

def charger_donnees():
    try:
        xls = pd.ExcelFile(FICHIER)
        histo = xls.parse("Historique_Gagnants")
        series = xls.parse("Series_Journalieres")
        preds = xls.parse("Predictions")
    except:
        st.error("Erreur lors du chargement des feuilles Excel.")
        return None, None, None
    return histo, series, preds

# Extraction des chiffres depuis les séries (par unités ou couples)
def extraire_chiffres(serie_str, mode="unite"):
    if pd.isna(serie_str): return []
    numeros = re.findall(r"\\d+", serie_str)
    resultats = []
    for num in numeros:
        if mode == "unite":
            resultats.extend([int(d) for d in num])
        elif mode == "couple":
            resultats.extend([int(num[i:i+2]) for i in range(len(num)-1)])
    return resultats

# Générer une prédiction basée sur l’analyse des séries

def generer_prediction(series_ligne):
    unite_totale = []
    couple_totale = []

    for col in ["Matrice", "Clavier", "Cerveau"]:
        unite_totale.extend(extraire_chiffres(series_ligne[col], mode="unite"))
        couple_totale.extend(extraire_chiffres(series_ligne[col], mode="couple"))

    # Ajouter Code et Event comme sources de patterns
    for col in ["Code", "Event"]:
        if not pd.isna(series_ligne[col]):
            unite_totale.extend(extraire_chiffres(str(int(series_ligne[col])), mode="unite"))
            couple_totale.extend(extraire_chiffres(str(int(series_ligne[col])), mode="couple"))

    # Compter les occurrences
    unite_freq = Counter(unite_totale)
    couple_freq = Counter(couple_totale)

    # Sélection des 5 chiffres ou couples les plus fréquents
    top_couples = [num for num, _ in couple_freq.most_common(10) if 1 <= num <= 99]
    top_unites = [num for num, _ in unite_freq.most_common(20) if 1 <= num <= 99]

    prediction = sorted(list(set(top_couples + top_unites)))[:5]
    return prediction

# Comparer prédiction et résultat réel

def evaluer_prediction(pred, reel):
    return len(set(pred).intersection(set(reel)))

# --- Interface principale Streamlit ---

st.title("🔮 Prédiction du Tirage 19h")
historique, series, predictions = charger_donnees()

if historique is None:
    st.stop()

# Sélection automatique ou manuelle de la date du jour
aujourdhui = datetime.date.today()

serie_du_jour = series[series["Date"] == pd.to_datetime(aujourdhui)]
if serie_du_jour.empty:
    st.warning("Aucune série disponible pour aujourd’hui. Veuillez saisir manuellement :")
    date = st.date_input("Date du jour", value=aujourdhui)
    matrice = st.text_input("Matrice")
    clavier = st.text_input("Clavier")
    cerveau = st.text_input("Cerveau")
    code = st.text_input("Code")
    event = st.text_input("Event")

    if st.button("Lancer la prédiction"):
        ligne = pd.Series({
            "Date": date,
            "Matrice": matrice,
            "Clavier": clavier,
            "Cerveau": cerveau,
            "Code": code,
            "Event": event
        })
        prediction = generer_prediction(ligne)
        st.success(f"🎯 Prédiction du jour: {prediction}")
else:
    ligne = serie_du_jour.iloc[0]
    prediction = generer_prediction(ligne)
    st.success(f"🎯 Prédiction automatique du {aujourdhui} : {prediction}")

# Afficher résultat réel s’il existe
resultat = historique[historique["Date"] == pd.to_datetime(aujourdhui)]
if not resultat.empty:
    nums = resultat.iloc[0][["Num1", "Num2", "Num3", "Num4", "Num5"]].dropna().astype(int).tolist()
    score = evaluer_prediction(prediction, nums)
    st.info(f"✅ Résultat réel : {nums}")
    st.info(f"🎯 Prédiction correcte sur {score}/5")

# Sauvegarde automatique dans l'onglet Predictions
if "prediction" in locals():
    nouvelles_predictions = pd.DataFrame([{"Date": aujourdhui, **{f"Pred{i+1}": prediction[i] if i < len(prediction) else None for i in range(5)}}])
    try:
        anciennes = predictions if predictions is not None else pd.DataFrame()
        maj = pd.concat([anciennes, nouvelles_predictions]).drop_duplicates("Date", keep="last")
        with pd.ExcelWriter(FICHIER, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            historique.to_excel(writer, sheet_name="Historique_Gagnants", index=False)
            series.to_excel(writer, sheet_name="Series_Journalieres", index=False)
            maj.to_excel(writer, sheet_name="Predictions", index=False)
        st.success("📝 Prédiction enregistrée dans Predictions.")
    except Exception as e:
        st.warning(f"Erreur lors de l'enregistrement: {e}")
