
import streamlit as st
import pandas as pd
import datetime
import random
import os

FICHIER_EXCEL = "Donnees_Tirage.xlsx"

# Charger les données
def charger_donnees():
    if not os.path.exists(FICHIER_EXCEL):
        st.error("Fichier Excel non trouvé.")
        return None, None, None
    try:
        historiques = pd.read_excel(FICHIER_EXCEL, sheet_name="Historique_Gagnants")
        series = pd.read_excel(FICHIER_EXCEL, sheet_name="Series_Journalieres")
        predictions = pd.read_excel(FICHIER_EXCEL, sheet_name="Predictions")
        return historiques, series, predictions
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return None, None, None

# Sauvegarder les données
def sauvegarder_donnees(df_gagnants, df_series, df_predictions):
    with pd.ExcelWriter(FICHIER_EXCEL, engine="openpyxl", mode="w") as writer:
        df_gagnants.to_excel(writer, sheet_name="Historique_Gagnants", index=False)
        df_series.to_excel(writer, sheet_name="Series_Journalieres", index=False)
        df_predictions.to_excel(writer, sheet_name="Predictions", index=False)

# Générer une prédiction simple basée sur des numéros aléatoires
def generer_prediction():
    return sorted(random.sample(range(1, 100), 5))

# Interface utilisateur
st.title("🔮 Prédiction Tirage 19h")

aujourdhui = datetime.date.today()
hist, series, preds = charger_donnees()

if hist is not None and series is not None and preds is not None:
    with st.form("formulaire_prediction"):
        st.subheader("📩 Entrer les séries du jour")
        matrice = st.text_input("Matrice")
        clavier = st.text_input("Clavier")
        cerveau = st.text_input("Cerveau")
        code = st.text_input("Code")
        event = st.text_input("Event")
        submit = st.form_submit_button("Générer la prédiction")
        if submit:
            prediction = generer_prediction()
            st.success(f"🎯 Prédiction : {prediction}")
            nouvelle_serie = pd.DataFrame([{
                "Date": aujourdhui,
                "Matrice": matrice,
                "Clavier": clavier,
                "Cerveau": cerveau,
                "Code": code,
                "Event": event
            }])
            series = pd.concat([series, nouvelle_serie], ignore_index=True)
            nouvelle_pred = pd.DataFrame([{
                "Date": aujourdhui,
                "Pred1": prediction[0],
                "Pred2": prediction[1],
                "Pred3": prediction[2],
                "Pred4": prediction[3],
                "Pred5": prediction[4],
            }])
            preds = pd.concat([preds, nouvelle_pred], ignore_index=True)
            sauvegarder_donnees(hist, series, preds)

    with st.form("formulaire_resultat"):
        st.subheader("📊 Entrer les résultats du tirage 19h")
        n1 = st.number_input("Numéro 1", min_value=1, max_value=99)
        n2 = st.number_input("Numéro 2", min_value=1, max_value=99)
        n3 = st.number_input("Numéro 3", min_value=1, max_value=99)
        n4 = st.number_input("Numéro 4", min_value=1, max_value=99)
        n5 = st.number_input("Numéro 5", min_value=1, max_value=99)
        submit_result = st.form_submit_button("Enregistrer les résultats")
        if submit_result:
            nouveau_resultat = pd.DataFrame([{
                "Date": aujourdhui,
                "Num1": n1,
                "Num2": n2,
                "Num3": n3,
                "Num4": n4,
                "Num5": n5,
            }])
            hist = pd.concat([hist, nouveau_resultat], ignore_index=True)
            sauvegarder_donnees(hist, series, preds)
            st.success("Résultats enregistrés avec succès.")
