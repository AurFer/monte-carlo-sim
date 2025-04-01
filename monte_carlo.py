import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def monte_carlo_simulation(data, num_simulations=1000):
    durations = (data['Clôture'] - data['Activation']).dt.total_seconds() / 86400  # Convertir en jours décimaux
    simulated_durations = np.random.choice(durations, size=(num_simulations, len(durations)), replace=True)
    completion_times = simulated_durations.sum(axis=1)
    return completion_times

st.title("Simulation de Monte Carlo pour la Prévision de Livraison")

uploaded_file = st.file_uploader("Charge un fichier CSV avec les colonnes 'Activation' et 'Clôture' (format YYYY-MM-DD)", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file, sep=";", parse_dates=['Activation', 'Clôture'])
    st.write("Aperçu des données :", data.head())
    
    num_simulations = st.slider("Nombre de simulations", 100, 5000, 1000)
    
    if st.button("Lancer la simulation"):
        completion_times = monte_carlo_simulation(data, num_simulations)
        
        fig, ax = plt.subplots()
        ax.hist(completion_times, bins=30, color='blue', alpha=0.7)
        ax.set_title("Distribution des temps de complétion")
        ax.set_xlabel("Jours")
        ax.set_ylabel("Fréquence")
        
        st.pyplot(fig)
        
        percentiles = np.percentile(completion_times, [50, 85, 95])
        st.write(f"50% des projets se terminent en {percentiles[0]} jours ou moins")
        st.write(f"85% des projets se terminent en {percentiles[1]} jours ou moins")
        st.write(f"95% des projets se terminent en {percentiles[2]} jours ou moins")
