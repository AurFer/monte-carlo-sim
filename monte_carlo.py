import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta

st.set_page_config(layout="wide")
st.title("Simulation Monte Carlo – Prévision de Livraison Agile")

# --- Fonction de chargement ---
def charger_donnees(fichier):
    ext = fichier.name.split('.')[-1].lower()
    if ext == "csv":
        return pd.read_csv(fichier, sep=None, engine='python', parse_dates=['Activation', 'Clôture'])
    elif ext in ["xls", "xlsx"]:
        return pd.read_excel(fichier, parse_dates=['Activation', 'Clôture'])
    else:
        st.error("Format de fichier non supporté. Utilise un .csv ou un .xlsx")
        return None

# --- Fonction de simulation ---
def monte_carlo_cycle_times(cycle_times, num_simulations, num_items):
    simulations = []
    for _ in range(num_simulations):
        samples = np.random.choice(cycle_times, size=num_items, replace=True)
        simulations.append(np.cumsum(samples))
    return np.array(simulations)

# --- Interface ---
uploaded_file = st.file_uploader("Charge un fichier .csv ou .xls(x) avec les colonnes 'Title', 'Activation' et 'Clôture'", type=["csv", "xls", "xlsx"])

if uploaded_file:
    df = charger_donnees(uploaded_file)
    if df is not None:
        df['Durée'] = (df['Clôture'] - df['Activation']).dt.days
        cycle_times = df['Durée'].values

        st.write("Aperçu des données :", df.head())

        choix = st.radio("Souhaites-tu prévoir...", ["...un nombre d'items à livrer", "...ce que je peux livrer avant une date cible"])

        num_simulations = st.slider("Nombre de simulations Monte Carlo", 100, 5000, 1000)

        if choix == "...un nombre d'items à livrer":
            nb_items = st.number_input("Nombre d'items à livrer", min_value=1, step=1)
            if st.button("Lancer la simulation"):
                sims = monte_carlo_cycle_times(cycle_times, num_simulations, nb_items)
                today = pd.to_datetime("today")
                dates_simulees = today + pd.to_timedelta(sims, unit='D')

                dernieres_dates = dates_simulees[:, -1]  # Date de livraison du dernier item
                hist = pd.Series(dernieres_dates).dt.floor('D').value_counts(normalize=True).sort_index()

                fig, ax = plt.subplots(figsize=(10,4))
                cmap = sns.light_palette("green", as_cmap=True)
                sns.heatmap([hist.values], ax=ax, cmap=cmap, cbar=True, xticklabels=hist.index.strftime('%Y-%m-%d'), yticklabels=["Probabilité"])
                plt.xticks(rotation=45, ha="right")
                st.pyplot(fig)

        else:
            date_cible = st.date_input("Date cible de livraison")
            if st.button("Lancer la simulation"):
                horizon = (pd.to_datetime(date_cible) - pd.to_datetime("today")).days
                max_items = 100
                probas = []
                for n in range(1, max_items+1):
                    sims = monte_carlo_cycle_times(cycle_times, num_simulations, n)
                    pourcentage_livres = (sims[:, -1] <= horizon).mean()
                    probas.append((n, pourcentage_livres))
                df_probas = pd.DataFrame(probas, columns=["Nombre d'items", "Probabilité de livraison"])
                st.line_chart(df_probas.set_index("Nombre d'items"))
                meilleur_estimate = df_probas[df_probas["Probabilité de livraison"] >= 0.85].head(1)
                if not meilleur_estimate.empty:
                    st.success(f"Tu as 85% de chances de livrer **{int(meilleur_estimate['Nombre d'items'].values[0])} items** ou plus d'ici {date_cible}.")
                else:
                    st.warning("Aucun nombre d'items n'atteint 85% de chances d'être livré à cette date.")
