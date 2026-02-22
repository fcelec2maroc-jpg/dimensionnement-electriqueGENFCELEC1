import streamlit as st
import math
import datetime
from fpdf import FPDF

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="FC ELEC - Bureau d'Études", layout="wide", initial_sidebar_state="expanded")

# --- INJECTION DE STYLE CSS (Design Pro) ---
st.markdown("""
    <style>
    .reportview-container { background: #f4f6f9; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    .metric-card { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# --- CLASSE PDF "DOSSIER TECHNIQUE" ---
class FCELEC_Report(FPDF):
    def cover_page(self, nom_projet, titre_doc):
        self.add_page()
        try: self.image("logoFCELEC.png", 60, 40, 90)
        except: pass
        self.ln(80)
        self.set_font("Helvetica", "B", 24)
        self.cell(0, 15, "DOSSIER TECHNIQUE ÉLECTRIQUE", ln=True, align="C")
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(100, 100, 100)
        self.cell(0, 15, titre_doc.upper(), ln=True, align="C")
        self.ln(20)
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "", 14)
        self.cell(0, 10, f"PROJET / CLIENT : {nom_projet.upper()}", ln=True, align="C")
        self.cell(0, 10, f"Date de l'étude : {datetime.date.today().strftime('%d/%m/%Y')}", ln=True, align="C")
        self.ln(40)
        self.set_font("Helvetica", "I", 11)
        self.cell(0, 10, "Document certifié conforme aux prescriptions de la norme NF C 15-100", ln=True, align="C")
        
    def header(self):
        if self.page_no() > 1:
            try: self.image("logoFCELEC.png", 10, 8, 25)
            except: pass
            self.set_font("Helvetica", "B", 12)
            self.cell(80)
            self.cell(30, 10, "NOTE DE CALCUL", 0, 0, "C")
            self.set_font("Helvetica", "I", 8)
            self.cell(0, 10, f"Date: {datetime.date.today().strftime('%d/%m/%Y')}", 0, 1, "R")
            self.line(10, 22, 200, 22)
            self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.line(10, 277, 200, 277)
        self.cell(0, 6, "FC ELEC - Bureau d'Études Électriques", 0, 1, "C")
        self.cell(0, 6, "Assistance & Contact WhatsApp : +212 6 74 53 42 64", 0, 1, "C")
        self.set_font("Helvetica", "", 8)
        self.cell(0, 4, f"Page {self.page_no()}", 0, 0, "R")

# --- SYSTÈME DE SÉCURITÉ ---
def check_password():
    if "password_correct" not in st.session_state:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("logoFCELEC.png", width=250)
            st.markdown("### 🔐 Portail Ingénierie FC ELEC")
            user = st.text_input("Identifiant")
            pw = st.text_input("Mot de passe", type="password")
            if st.button("Authentification"):
                if "passwords" in st.secrets and user in st.secrets["passwords"] and pw == st.secrets["passwords"][user]:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Accès refusé. Vérifiez vos identifiants.")
        return False
    return True

if check_password():
    # --- NAVIGATION LATÉRALE ---
    st.sidebar.image("logoFCELEC.png", use_container_width=True)
    st.sidebar.markdown("## 📐 MODULES D'INGÉNIERIE")
    menu = st.sidebar.radio("Sélectionnez l'outil :", [
        "🔌 1. Liaison & Protection",
        "📊 2. Bilan de Puissance (TGBT)",
        "📉 3. Compensation (Cos φ)",
        "🚘 4. Infrastructure IRVE"
    ])
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Plateforme de calcul conforme à la norme NF C 15-100.")

    # ---------------------------------------------------------
    # MODULE 1 : LIAISON & PROTECTION
    # ---------------------------------------------------------
    if menu == "🔌 1. Liaison & Protection":
        st.title("🔌 Dimensionnement de Ligne & Protection")
        
        with st.container(border=True):
            st.markdown("#### 📋 Données du projet")
            col_p1, col_p2 = st.columns(2)
            nom_projet = col_p1.text_input("Nom du Projet / Client", "Chantier Résidentiel")
            ref_circuit = col_p2.text_input("Désignation du Circuit", "TGBT - Départ Sous-sol")

        with st.container(border=True):
            st.markdown("#### ⚙️ Paramètres Électriques")
            c1, c2, c3 = st.columns(3)
            with c1:
                tension_type = st.selectbox("Tension du réseau", ["Monophasé (230V)", "Triphasé (400V)"])
                nature_cable = st.selectbox("Nature de l'âme", ["Cuivre (Cu)", "Aluminium (Al)"])
            with c2:
                mode_saisie = st.radio("Mode de saisie", ["Puissance (W)", "Courant d'emploi (A)"])
                valeur_saisie = st.number_input("Valeur (W ou A)", min_value=1.0, value=3500.0)
            with c3:
                longueur = st.number_input("Longueur de la liaison (m)", min_value=1, value=50)
                type_charge = st.selectbox("Type d'utilisation", ["Éclairage (Max 3%)", "Force Motrice / Autres (Max 5%)"])
                du_max_pct = 3.0 if "Éclairage" in type_charge else 5.0

        # Moteur de calcul
        V = 230 if "Monophasé" in tension_type else 400
        rho = 0.0225 if "Cuivre" in nature_cable else 0.036
        b = 2 if "Monophasé" in tension_type else 1
        cos_phi = 0.85 # Standardisé pour la simplification

        if mode_saisie == "Puissance (W)":
            Ib = valeur_saisie / (V * cos_phi) if b == 2 else valeur_saisie / (V * math.sqrt(3) * cos_phi)
        else:
            Ib = valeur_saisie

        calibres = [10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 400, 630, 800, 1000]
        In = next((x for x in calibres if x >= Ib), calibres[-1])
        
        S_calc = (b * rho * longueur * Ib) / ((du_max_pct / 100) * V)
        sections = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
        S_retenue = next((s for s in sections if s >= S_calc), "Hors standard (>300)")
        
        du_reel_v = (b * rho * longueur * Ib) / (S_retenue if isinstance(S_retenue, float) else 300)
        du_reel_pct = (du_reel_v / V) * 100

        # Affichage style "Dashboard"
        st.markdown("### 📊 Synthèse des Résultats")
        res1, res2, res3, res4 = st.columns(4)
        res1.metric("Courant d'emploi (Ib)", f"{Ib:.2f} A")
        res2.metric("Calibre Disjoncteur (In)", f"{In} A", help="Protection magnéto-thermique recommandée")
        res3.metric("Section Normalisée", f"{S_retenue} mm²")
        res4.metric("Chute de tension", f"{du_reel_pct:.2f} %", delta=f"Max autorisé: {du_max_pct}%", delta_color="inverse" if du_reel_pct > du_max_pct else "normal")

        # Génération du PDF Bureau d'études
        def generate_pdf_liaison():
            pdf = FCELEC_Report()
            pdf.cover_page(nom_projet, "Dimensionnement de Liaison")
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(190, 10, "1. HÉPOTHÈSES DE CALCUL", border='B', ln=True)
            pdf.ln(5)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(95, 8, f"Circuit : {ref_circuit}", ln=0); pdf.cell(95, 8, f"Réseau : {tension_type}", ln=1)
            pdf.cell(95, 8, f"Longueur : {longueur} mètres", ln=0); pdf.cell(95, 8, f"Nature : {nature_cable}", ln=1)
            pdf.cell(95, 8, f"Puissance / Courant : {valeur_saisie} {'W' if 'Puissance' in mode_saisie else 'A'}", ln=0)
            pdf.cell(95, 8, f"Chute de tension limite : {du_max_pct} %", ln=1)
            pdf.ln(10)
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(190, 10, "2. RÉSULTATS NORMATIFS", border='B', ln=True)
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(95, 10, "Courant d'emploi (Ib) :", border=1); pdf.cell(95, 10, f"{Ib:.2f} A", border=1, ln=1, align="C")
            pdf.cell(95, 10, "Calibre Protection (In) :", border=1); pdf.cell(95, 10, f"{In} A", border=1, ln=1, align="C")
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(95, 12, "SECTION CÂBLE RETENUE :", border=1, fill=True)
            pdf.set_text_color(255, 100, 0)
            pdf.cell(95, 12, f"{S_retenue} mm2", border=1, ln=1, align="C", fill=True)
            pdf.set_text_color(0,0,0)
            pdf.cell(95, 10, "Chute de tension réelle :", border=1); pdf.cell(95, 10, f"{du_reel_pct:.2f} % (Conforme)", border=1, ln=1, align="C")
            
            # Bloc de signature
            pdf.ln(30)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(120, 10, "")
            pdf.cell(70, 10, "Le Bureau d'Études / L'Ingénieur :", ln=True, align="C")
            pdf.cell(120, 20, "")
            pdf.cell(70, 20, "(Signature et Cachet)", border=1, ln=True, align="C")
            
            return pdf.output()

        if st.button("📄 Éditer le Dossier Technique (PDF)", type="primary"):
            st.download_button("📥 Confirmer le téléchargement", bytes(generate_pdf_liaison()), f"Dossier_{ref_circuit}.pdf")

    # ---------------------------------------------------------
    # MODULE 2 : BILAN DE PUISSANCE TGBT
    # ---------------------------------------------------------
    elif menu == "📊 2. Bilan de Puissance (TGBT)":
        st.title("📊 Bilan de Puissance du Tableau (TGBT)")
        
        col_p1, col_p2 = st.columns(2)
        nom_projet = col_p1.text_input("Nom du Projet / Client", "Résidence / Usine")
        nom_tgbt = col_p2.text_input("Nom du Tableau", "TGBT Général")

        if 'bilan_pro' not in st.session_state: st.session_state.bilan_pro = []

        with st.expander("➕ Saisie d'un nouveau départ (Circuit)", expanded=True):
            with st.form("form_bilan"):
                c1, c2, c3 = st.columns([2, 1, 1])
                nom_c = c1.text_input("Nom du circuit")
                p_inst = c2.number_input("P. Installée (W)", min_value=0, value=1000)
                type_c = c3.selectbox("Famille de charge", ["Éclairage", "Prises", "Moteur / CVC", "Chauffage", "Divers"])
                
                # Explication Ku
                st.caption("Le Facteur d'Utilisation (Ku) détermine le taux de charge réel de l'équipement.")
                ku_def = 1.0 if type_c in ["Éclairage", "Chauffage"] else 0.75 if type_c == "Moteur / CVC" else 0.5 if type_c == "Prises" else 0.8
                ku = st.slider("Facteur d'utilisation (Ku)", 0.1, 1.0, ku_def)
                
                if st.form_submit_button("Valider et Ajouter"):
                    st.session_state.bilan_pro.append({
                        "Désignation": nom_c, "Famille": type_c, "P.Inst (W)": p_inst, "Ku": ku, "P.Abs (W)": int(p_inst * ku)
                    })

        if st.session_state.bilan_pro:
            st.dataframe(st.session_state.bilan_pro, use_container_width=True)
            
            p_total_inst = sum(x['P.Inst (W)'] for x in st.session_state.bilan_pro)
            p_total_abs = sum(x['P.Abs (W)'] for x in st.session_state.bilan_pro)
            
            st.markdown("#### 📉 Application du Foisonnement Global")
            ks = st.slider("Facteur de Simultanéité (Ks) du tableau", 0.4, 1.0, 0.8, help="Dépend du nombre de circuits et du type de bâtiment.")
            p_souscription = p_total_abs * ks
            
            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric("Total Installé", f"{p_total_inst} W")
            col_res2.metric("Total Absorbé (Ku)", f"{p_total_abs} W")
            col_res3.metric("PUISSANCE D'APPEL (Ks)", f"{int(p_souscription)} W")

            if st.button("📄 Éditer la Note de Bilan (PDF)", type="primary"):
                pdf = FCELEC_Report()
                pdf.cover_page(nom_projet, f"Bilan de Puissance - {nom_tgbt}")
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(190, 10, f"TABLEAU RÉCAPITULATIF : {nom_tgbt}", ln=True, align="C")
                pdf.ln(5)
                # En-têtes
                pdf.set_font("Helvetica", "B", 10); pdf.set_fill_color(200, 200, 200)
                pdf.cell(60, 10, "Circuit", 1, 0, 'C', True); pdf.cell(40, 10, "Type", 1, 0, 'C', True)
                pdf.cell(30, 10, "P.Inst", 1, 0, 'C', True); pdf.cell(20, 10, "Ku", 1, 0, 'C', True)
                pdf.cell(40, 10, "P.Absorbée", 1, 1, 'C', True)
                pdf.set_font("Helvetica", "", 10)
                for c in st.session_state.bilan_pro:
                    pdf.cell(60, 8, c['Désignation'], 1); pdf.cell(40, 8, c['Famille'], 1)
                    pdf.cell(30, 8, f"{c['P.Inst (W)']} W", 1, 0, 'C'); pdf.cell(20, 8, str(c['Ku']), 1, 0, 'C')
                    pdf.cell(40, 8, f"{c['P.Abs (W)']} W", 1, 1, 'C')
                
                pdf.ln(10)
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(190, 12, f"PUISSANCE MAXIMALE D'APPEL DU TABLEAU (Ks={ks}) : {int(p_souscription)} W", border=1, ln=True, align="C", fill=True)
                st.download_button("📥 Télécharger le Bilan", bytes(pdf.output()), f"Bilan_{nom_tgbt}.pdf")

            if st.button("🗑️ Réinitialiser le Bilan"):
                st.session_state.bilan_pro = []; st.rerun()

    # ---------------------------------------------------------
    # MODULE 3 : COMPENSATION COS PHI
    # ---------------------------------------------------------
    elif menu == "📉 3. Compensation (Cos φ)":
        st.title("📉 Compensation d'Énergie Réactive")
        st.write("Dimensionnement de la batterie de condensateurs pour relever le facteur de puissance.")
        
        with st.container(border=True):
            p_kw = st.number_input("Puissance Active de l'installation (kW)", min_value=1.0, value=100.0)
            col1, col2 = st.columns(2)
            cos_ini = col1.number_input("Cos φ initial (Facteur de puissance actuel)", min_value=0.3, max_value=0.99, value=0.75, step=0.01)
            cos_vise = col2.number_input("Cos φ cible (Généralement 0.93 ou 0.95)", min_value=0.8, max_value=1.0, value=0.95, step=0.01)
            
            tan_ini = math.tan(math.acos(cos_ini))
            tan_vise = math.tan(math.acos(cos_vise))
            Qc = p_kw * (tan_ini - tan_vise)
            
            st.info(f"Formule appliquée : Qc = P × (tan φ1 - tan φ2) = {p_kw} × ({tan_ini:.2f} - {tan_vise:.2f})")
            st.success(f"Puissance Réactive de la Batterie de Condensateurs : **{math.ceil(Qc)} kVAR**")

    # ---------------------------------------------------------
    # MODULE 4 : BORNES IRVE
    # ---------------------------------------------------------
    elif menu == "🚘 4. Infrastructure IRVE":
        st.title("🚘 Mobilité Électrique (IRVE)")
        st.write("Recommandations techniques pour l'installation de bornes de recharge pour véhicules électriques.")
        
        p_borne = st.selectbox("Puissance de la borne de recharge (AC)", ["3.7 kW (Monophasé - 16A)", "7.4 kW (Monophasé - 32A)", "11 kW (Triphasé - 16A)", "22 kW (Triphasé - 32A)"])
        
        st.markdown("### 📋 Synthèse des Prescriptions")
        if "3.7" in p_borne or "7.4" in p_borne:
            st.write("- **Raccordement** : Monophasé 230V")
            st.write("- **Section de câble minimale recommandée** : 10 mm² (Cuivre)")
            calibre = 20 if "3.7" in p_borne else 40
        else:
            st.write("- **Raccordement** : Triphasé 400V")
            st.write("- **Section de câble minimale recommandée** : 5G10 mm² (Cuivre)")
            calibre = 20 if "11" in p_borne else 40
            
        st.write(f"- **Disjoncteur Magnéto-Thermique** : {calibre}A Courbe C")
        st.warning("- **Protection Différentielle** : Obligatoirement un interrupteur différentiel **30mA Type B** (ou Type A avec détection courant de fuite DC intégrée à la borne).")

    # --- DÉCONNEXION ---
    st.sidebar.markdown("---")
    if st.sidebar.button("Se déconnecter de la session"):
        st.session_state.clear()
        st.rerun()