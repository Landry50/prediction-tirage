
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Fonction de prédiction (simplifiée ici pour exemple)
def predire_numeros(series_row):
    chiffres = []
    for col in ['Matrice', 'Clavier', 'Cerveau']:
        nums = str(series_row[col]).split(',')
        for n in nums:
            if len(n.strip()) == 3:
                chiffres.extend([int(n.strip()[0]), int(n.strip()[1]), int(n.strip()[2])])
    chiffres = list(set([n for n in chiffres if 0 <= n <= 99]))
    return sorted(chiffres[:5])

# Charger les données
fichier_excel = 'Donnees_Tirage.xlsx'
df_series = pd.read_excel(fichier_excel, sheet_name="Series_Journalieres")
df_resultats = pd.read_excel(fichier_excel, sheet_name="Resultats")

# ✅ Harmonise les dates dans Series_Journalieres
df_series['Date'] = pd.to_datetime(df_series['Date']).dt.strftime('%Y-%m-%d')

# ✅ Récupérer la date du jour au bon format
today = datetime.today().strftime('%Y-%m-%d')

st.title("Prédiction du Tirage 19h")

# Trouver la ligne du jour
row_today = df_series[df_series['Date'] == today]

if row_today.empty:
    st.warning("Aucune série disponible pour aujourd’hui. Veuillez saisir manuellement.")
else:
    row_today = row_today.iloc[0]
    prediction = predire_numeros(row_today)
    st.success(f"🔮 Prédiction pour le {today} : {prediction}")

    # Enregistrement dans une feuille "Predictions"
    prediction_df = pd.DataFrame([[today] + prediction], columns=['Date'] + [f'Num{i+1}' for i in range(5)])
    
    try:
        with pd.ExcelWriter(fichier_excel, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            prediction_df.to_excel(writer, sheet_name='Predictions', index=False, header=not 'Predictions' in writer.sheets)
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement de la prédiction : {e}")
