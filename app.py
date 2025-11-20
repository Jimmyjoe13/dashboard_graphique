import streamlit as st
import pandas as pd
import gspread
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Suivi RDV", layout="wide")
st.title("Dashboard RDV LeadGen")

# --- 1. CONNEXION GOOGLE SHEETS ---
# On regarde si le fichier existe (mode local) ou si on est sur le cloud (st.secrets)
if os.path.exists("credentials.json"):
    gc = gspread.service_account(filename="credentials.json")
else:
    # Mode Cloud : on récupère les infos depuis les secrets Streamlit
    credentials_dict = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(credentials_dict)

# ID du Google Sheet
SHEET_ID = "1oThuV40f0y5rKAMlmyiLVviZ-ITNAQAl0zMevO4fjlg" # Votre ID est déjà là

try:
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.worksheet("RDV/jour")
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# --- 2. TRAITEMENT DES DONNÉES ---
# Récupération de toutes les valeurs
data = worksheet.get_all_values()

# Création du DataFrame
# On suppose que la ligne 1 (index 0) contient les entêtes
df = pd.DataFrame(data[1:], columns=data[0])

# --- DEBUG & CORRECTION ---
# 1. Afficher les colonnes brutes pour comprendre le problème
st.write("Colonnes détectées par Python :", df.columns.tolist())

# 2. Nettoyer les noms de colonnes (enlève les espaces invisibles autour)
df.columns = df.columns.str.strip()

# 3. Gérer les cellules fusionnées pour la DATE
# Maintenant que les espaces sont enlevés, "DATE" devrait être reconnu
if 'DATE' in df.columns:
    df['DATE'] = df['DATE'].replace('', pd.NA).ffill()
else:
    st.error("Erreur : La colonne 'DATE' est introuvable. Vérifiez la ligne 1 de votre Google Sheet.")
    st.stop()

# --- 3. GRAPHIQUE : PLAISIRS ET PAPILLES ---
st.header("📈 Campagne : Plaisirs et Papilles")

# Filtrer uniquement cette campagne
df_pp = df[df['CAMPAGNES'] == 'Plaisirs et Papilles'].copy()

# --- CORRECTION DATE ---
# 1. On convertit le texte "JJ/MM/AAAA" en véritable objet Date
# dayfirst=True est CRUCIAL pour dire à Python que le jour est en premier (format français)
df_pp['DATE'] = pd.to_datetime(df_pp['DATE'], dayfirst=True, errors='coerce')

# 2. On trie du plus ancien au plus récent (pour avoir une ligne fluide)
df_pp = df_pp.sort_values('DATE')

# Convertir les chiffres (comme avant)
cols_to_plot = ['NOMBRE DE RDV PRIS', 'NOMBRE DE RDV PLANIFIÉ']
for col in cols_to_plot:
    df_pp[col] = pd.to_numeric(df_pp[col], errors='coerce').fillna(0)

# Vérification et Affichage
if not df_pp.empty:
    st.line_chart(
        df_pp,
        x='DATE',
        y=cols_to_plot,
        color=["#3366cc", "#dc3912"] 
    )
    
    with st.expander("Voir les données brutes"):
        st.dataframe(df_pp)
else:
    st.warning("Aucune donnée trouvée.")

    # --- 4. GRAPHIQUE : PORTRAITS FÉMININS ---
st.markdown("---") # Une ligne de séparation esthétique
st.header("📈 Campagne : Portraits Féminins")

# 1. Filtrer pour la campagne "Portraits Féminins"
df_pf = df[df['CAMPAGNES'] == 'Portraits Féminins'].copy()

# 2. Conversion Date (Déjà fait dans 'df' global, mais on s'assure du tri)
# On utilise la même colonne 'DATE' convertie précédemment
if not pd.api.types.is_datetime64_any_dtype(df_pf['DATE']):
     df_pf['DATE'] = pd.to_datetime(df_pf['DATE'], dayfirst=True, errors='coerce')

df_pf = df_pf.sort_values('DATE')

# 3. Conversion des chiffres
for col in cols_to_plot:
    df_pf[col] = pd.to_numeric(df_pf[col], errors='coerce').fillna(0)

# 4. Affichage
if not df_pf.empty:
    st.line_chart(
        df_pf,
        x='DATE',
        y=cols_to_plot,
        color=["#3366cc", "#dc3912"] # On garde les mêmes couleurs pour la cohérence
    )
    
    with st.expander("Voir les données Portraits Féminins"):
        st.dataframe(df_pf)
else:
    st.warning("Aucune donnée trouvée pour 'Portraits Féminins'.")

# --- 5. GRAPHIQUE : REGARDS D'EXPERTS ---
st.markdown("---")
st.header("📈 Campagne : Regards d'Experts")

# 1. Filtrer pour "Regards d'Experts"
df_re = df[df['CAMPAGNES'] == "Regards d'Experts"].copy()

# --- CORRECTION MANQUANTE ---
# On force la conversion en Date ici aussi avant de trier
df_re['DATE'] = pd.to_datetime(df_re['DATE'], dayfirst=True, errors='coerce')

# 2. Tri par date (Maintenant que c'est une date, le tri sera chronologique)
df_re = df_re.sort_values('DATE')

# 3. Conversion des chiffres
cols_to_plot = ['NOMBRE DE RDV PRIS', 'NOMBRE DE RDV PLANIFIÉ']
for col in cols_to_plot:
    df_re[col] = pd.to_numeric(df_re[col], errors='coerce').fillna(0)

# 4. Affichage
if not df_re.empty:
    st.line_chart(
        df_re,
        x='DATE',
        y=cols_to_plot,
        color=["#3366cc", "#dc3912"]
    )
    
    with st.expander("Voir les données Regards d'Experts"):
        st.dataframe(df_re)
else:
    st.warning("Aucune donnée trouvée pour 'Regards d'Experts'.")

    # --- 6. GRAPHIQUE : L'OEIL DES EXPERTS ---
st.markdown("---")
st.header("📈 Campagne : L'oeil des Experts")

# 1. Filtrer pour "L'oeil des Experts"
df_oe = df[df['CAMPAGNES'] == "L'oeil des Experts"].copy()

# 2. Conversion Date et Tri
# On force la conversion date au cas où
if not pd.api.types.is_datetime64_any_dtype(df_oe['DATE']):
     df_oe['DATE'] = pd.to_datetime(df_oe['DATE'], dayfirst=True, errors='coerce')

df_oe = df_oe.sort_values('DATE')

# 3. Conversion des chiffres
for col in cols_to_plot:
    df_oe[col] = pd.to_numeric(df_oe[col], errors='coerce').fillna(0)

# 4. Affichage
if not df_oe.empty:
    st.line_chart(
        df_oe,
        x='DATE',
        y=cols_to_plot,
        color=["#3366cc", "#dc3912"]
    )
    
    with st.expander("Voir les données L'oeil des Experts"):
        st.dataframe(df_oe)
else:

    st.warning("Aucune donnée trouvée pour 'L'oeil des Experts'. (C'est normal si la date du jour est avant le 24/11/2025 et que le fichier n'est pas rempli, ou vérifiez l'orthographe exact).")
