import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def monte_carlo_simulation(data, num_simulations=1000):
    simulated_completion_times = []
    for _ in range(num_simulations):
        sampled_tasks = data.sample(frac=1, replace=True)  # Échantillon aléatoire des tâches
        sampled_tasks = sampled_tasks.copy()
        sampled_tasks['Simulated_Activation'] = sampled_tasks['Activation'].min() + pd.to_timedelta(np.random.randint(0, (sampled_tasks['Activation'].max() - sampled_tasks['Activation'].min()).days, size=len(sampled_tasks)), unit='D')
        sampled_tasks['Simulated_Clôture'] = sampled_tasks['Simulated_Activation'] + pd.to_timedelta(sampled_tasks['Durée'], unit='D')
        project_completion_time = (sampled_tasks['Simulated_Clôture'].max() - sampled_tasks['Simulated_Activation'].min()).days
        simulated_completion_times.append(project_completion_time)
    
    return simulated_completion_times

st.title("Simulation de Monte Carlo pour la Prévision de Livraison")

uploaded_file = st.file_uploader("Charge un fichier CSV avec les colonnes 'Activation' et 'Clôture' (format YYYY-MM-DD)", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file, sep=";", parse_dates=['Activation', 'Clôture'])
    data['Durée'] = (data['Clôture'] - data['Activation']).dt.days  # Ajouter une colonne de durée
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
