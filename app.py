import streamlit as st
import pandas as pd
import gspread
import os
import altair as alt 
from datetime import datetime 

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Suivi RDV", layout="wide")

# --- SECURITE : FONCTION LOGIN ---
def check_password():
    """Retourne True si l'utilisateur a le bon mot de passe."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔒 Veuillez entrer le mot de passe", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 Veuillez entrer le mot de passe", type="password", on_change=password_entered, key="password")
        st.error("⛔ Mot de passe incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

st.title("Dashboard RDV LeadGen")

# --- 1. CONNEXION GOOGLE SHEETS ---
if os.path.exists("credentials.json"):
    gc = gspread.service_account(filename="credentials.json")
else:
    credentials_dict = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(credentials_dict)

SHEET_ID = "1oThuV40f0y5rKAMlmyiLVviZ-ITNAQAl0zMevO4fjlg"

try:
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.worksheet("RDV/jour")
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# --- 2. TRAITEMENT DES DONNÉES ---
data = worksheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])

# Nettoyage
df.columns = df.columns.str.strip()
if 'DATE' in df.columns:
    df['DATE'] = df['DATE'].replace('', pd.NA).ffill()
else:
    st.error("Erreur : La colonne 'DATE' est introuvable.")
    st.stop()

# Colonnes à tracer
cols_to_plot = ['NOMBRE DE RDV PRIS', 'NOMBRE DE RDV PLANIFIÉ']

# --- FONCTION D'AFFICHAGE OPTIMISÉE ---
def afficher_graphique_interactif(dataframe, couleurs=["#3366cc", "#dc3912"]):
    # 1. Préparation des courbes
    df_melted = dataframe.melt('DATE', value_vars=cols_to_plot, var_name='Type', value_name='Nombre')
    
    # Création de l'interactivité (Click sur légende)
    selection = alt.selection_point(fields=['Type'], bind='legend')
    
    # Graphique de base (Les courbes)
    base = alt.Chart(df_melted).mark_line(point=True).encode(
        x=alt.X('DATE:T', axis=alt.Axis(format="%d/%m", title="Date")), 
        y='Nombre',
        color=alt.Color('Type', scale=alt.Scale(domain=cols_to_plot, range=couleurs)),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
        order='DATE:T',
        tooltip=[alt.Tooltip('DATE:T', format='%d/%m/%Y'), 'Type', 'Nombre']
    ).add_params(
        selection
    )

    # 2. Création de la ligne "Aujourd'hui"
    today_date = pd.to_datetime(datetime.now().date())
    today_df = pd.DataFrame({'DATE': [today_date]})

    # Ligne rouge pointillée
    rule = alt.Chart(today_df).mark_rule(color='red', strokeDash=[5, 5]).encode(
        x='DATE:T'
    )

    # 3. Combinaison des deux
    final_chart = alt.layer(base, rule).interactive()
    
    # CORRECTION ICI : Remplacement de use_container_width=True par width="stretch"
    st.altair_chart(final_chart, width="stretch")

# --- 3. GRAPHIQUE : PLAISIRS ET PAPILLES ---
st.header("📈 Campagne : Plaisirs et Papilles")
df_pp = df[df['CAMPAGNES'] == 'Plaisirs et Papilles'].copy()

# Traitement
df_pp['DATE'] = pd.to_datetime(df_pp['DATE'], dayfirst=True, errors='coerce')
df_pp = df_pp.dropna(subset=['DATE']) 
df_pp = df_pp.sort_values('DATE')

for col in cols_to_plot:
    df_pp[col] = pd.to_numeric(df_pp[col], errors='coerce').fillna(0)

if not df_pp.empty:
    afficher_graphique_interactif(df_pp)
    with st.expander("Voir les données brutes"):
        st.dataframe(df_pp)
else:
    st.warning("Aucune donnée trouvée.")

# --- 4. GRAPHIQUE : PORTRAITS FÉMININS ---
st.markdown("---")
st.header("📈 Campagne : Portraits Féminins")
df_pf = df[df['CAMPAGNES'] == 'Portraits Féminins'].copy()

# Traitement
df_pf['DATE'] = pd.to_datetime(df_pf['DATE'], dayfirst=True, errors='coerce')
df_pf = df_pf.dropna(subset=['DATE'])
df_pf = df_pf.sort_values('DATE')

for col in cols_to_plot:
    df_pf[col] = pd.to_numeric(df_pf[col], errors='coerce').fillna(0)

if not df_pf.empty:
    afficher_graphique_interactif(df_pf)
    with st.expander("Voir les données Portraits Féminins"):
        st.dataframe(df_pf)
else:
    st.warning("Aucune donnée trouvée pour 'Portraits Féminins'.")

# --- 5. GRAPHIQUE : REGARDS D'EXPERTS ---
st.markdown("---")
st.header("📈 Campagne : Regards d'Experts")
df_re = df[df['CAMPAGNES'] == "Regards d'Experts"].copy()

# Traitement
df_re['DATE'] = pd.to_datetime(df_re['DATE'], dayfirst=True, errors='coerce')
df_re = df_re.dropna(subset=['DATE'])
df_re = df_re.sort_values('DATE')

for col in cols_to_plot:
    df_re[col] = pd.to_numeric(df_re[col], errors='coerce').fillna(0)

if not df_re.empty:
    afficher_graphique_interactif(df_re)
    with st.expander("Voir les données Regards d'Experts"):
        st.dataframe(df_re)
else:
    st.warning("Aucune donnée trouvée pour 'Regards d'Experts'.")

# --- 6. GRAPHIQUE : L'OEIL DES EXPERTS ---
st.markdown("---")
st.header("📈 Campagne : L'oeil des Experts")
df_oe = df[df['CAMPAGNES'] == "L'oeil des Experts"].copy()

# Traitement
df_oe['DATE'] = pd.to_datetime(df_oe['DATE'], dayfirst=True, errors='coerce')
df_oe = df_oe.dropna(subset=['DATE'])
df_oe = df_oe.sort_values('DATE')

for col in cols_to_plot:
    df_oe[col] = pd.to_numeric(df_oe[col], errors='coerce').fillna(0)

if not df_oe.empty:
    afficher_graphique_interactif(df_oe)
    with st.expander("Voir les données L'oeil des Experts"):
        st.dataframe(df_oe)
else:
    st.warning("Aucune donnée trouvée pour 'L'oeil des Experts'.")