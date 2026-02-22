import streamlit as st
import math
import datetime
from fpdf import FPDF

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="FC ELEC - Bureau d'Études", layout="wide", initial_sidebar_state="expanded")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- CLASSE PDF PROFESSIONNELLE (Gère les sauts de page auto) ---
class FCELEC_Report(FPDF):
    def header(self):
        try: self.image("logoFCELEC.png", 10, 8, 25)
        except: pass
        self.set_font("Helvetica", "B", 14)
        self.cell(30)
        self.cell(130, 8, "DOSSIER TECHNIQUE ÉLECTRIQUE", border=0, ln=0, align="C")
        self.set_font("Helvetica", "I", 9)
        self.cell(30, 8, f"{datetime.date.today().strftime('%d/%m/%Y')}", border=0, ln=1, align="R")
        self.set_font("Helvetica", "I", 9)
        self.cell(30)
        self.cell(130, 5, "Note de calcul conforme à la norme NF C 15-100", border=0, ln=1, align="C")
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.line(10, 282, 200, 282)
        self.cell(0, 5, f"FC ELEC - Bureau d'Études | WhatsApp : +212 6 74 53 42 64 | Page {self.page_no()}", 0, 0, "C")

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
                    st.error("Accès refusé.")
        return False
    return True

if check_password():
    # --- NAVIGATION LATÉRALE ---
    st.sidebar.image("logoFCELEC.png", use_container_width=True)
    st.sidebar.markdown("## 📐 MODULES D'INGÉNIERIE")
    menu = st.sidebar.radio("Sélectionnez l'outil :", [
        "🔌 1. Carnet de Câbles (Sections)",
        "📊 2. Bilan de Puissance (TGBT)",
        "📉 3. Compensation (Cos φ)",
        "🚘 4. Infrastructure IRVE"
    ])
    st.sidebar.markdown("---")

    # ---------------------------------------------------------
    # MODULE 1 : CARNET DE CÂBLES (MULTI-CIRCUITS)
    # ---------------------------------------------------------
    if menu == "🔌 1. Carnet de Câbles (Sections)":
        st.title("🔌 Carnet de Câbles & Protections")
        st.write("Dimensionnez plusieurs lignes et générez un tableau récapitulatif (sauts de page automatiques).")
        
        col_p1, col_p2 = st.columns(2)
        nom_projet = col_p1.text_input("Nom du Projet / Client", "Chantier Résidentiel")
        nom_tableau = col_p2.text_input("Nom du Tableau", "TGBT")

        if 'cables_db' not in st.session_state: st.session_state.cables_db = []

        with st.expander("➕ Saisir une nouvelle ligne", expanded=True):
            with st.form("form_cable"):
                c1, c2, c3, c4 = st.columns(4)
                ref_c = c1.text_input("Désignation (ex: Prises)")
                tension = c2.selectbox("Réseau", ["230V", "400V"])
                p_w = c3.number_input("Puissance (W)", min_value=0, value=3500)
                longueur = c4.number_input("Longueur (m)", min_value=1, value=50)
                
                c5, c6, c7 = st.columns(3)
                nature = c5.selectbox("Métal", ["Cuivre", "Aluminium"])
                type_charge = c6.selectbox("Application", ["Éclairage (Max 3%)", "Autres (Max 5%)"])
                cos_phi = c7.slider("Cos φ", 0.7, 1.0, 0.85)

                if st.form_submit_button("Calculer et Ajouter"):
                    # Moteur de calcul
                    V = 230 if "230V" in tension else 400
                    rho = 0.0225 if "Cuivre" in nature else 0.036
                    b = 2 if "230V" in tension else 1
                    du_max_pct = 3.0 if "Éclairage" in type_charge else 5.0

                    Ib = p_w / (V * cos_phi) if b == 2 else p_w / (V * math.sqrt(3) * cos_phi)
                    
                    calibres = [10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 400, 630]
                    In = next((x for x in calibres if x >= Ib), 630)
                    
                    S_calc = (b * rho * longueur * Ib) / ((du_max_pct / 100) * V)
                    sections = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
                    S_retenue = next((s for s in sections if s >= S_calc), 300)
                    
                    du_reel_pct = (((b * rho * longueur * Ib) / S_retenue) / V) * 100

                    st.session_state.cables_db.append({
                        "Désignation": ref_c, "U": tension, "L(m)": longueur, "P(W)": p_w,
                        "Ib(A)": round(Ib, 1), "Disj(A)": In, "Section": f"{S_retenue} mm²", "dU(%)": round(du_reel_pct, 2)
                    })

        if st.session_state.cables_db:
            st.dataframe(st.session_state.cables_db, use_container_width=True)

            def generate_pdf_cables():
                pdf = FCELEC_Report()
                pdf.set_auto_page_break(auto=True, margin=15) # Gère les sauts de page si beaucoup de circuits
                pdf.add_page()
                
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(190, 10, f" CARNET DE CÂBLES - {nom_projet.upper()} ({nom_tableau.upper()})", border=1, ln=True, align="C", fill=True)
                pdf.ln(5)
                
                # En-têtes du tableau
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_fill_color(200, 200, 200)
                col_widths = [45, 15, 15, 20, 20, 20, 35, 20]
                headers = ["Désignation", "U", "L(m)", "P(W)", "Ib(A)", "Disj(A)", "Section", "dU(%)"]
                for i in range(len(headers)):
                    pdf.cell(col_widths[i], 8, headers[i], border=1, align='C', fill=True)
                pdf.ln()

                # Données du tableau
                pdf.set_font("Helvetica", "", 9)
                for row in st.session_state.cables_db:
                    pdf.cell(col_widths[0], 8, row["Désignation"][:20], border=1) # Coupe si trop long
                    pdf.cell(col_widths[1], 8, row["U"], border=1, align='C')
                    pdf.cell(col_widths[2], 8, str(row["L(m)"]), border=1, align='C')
                    pdf.cell(col_widths[3], 8, str(row["P(W)"]), border=1, align='C')
                    pdf.cell(col_widths[4], 8, str(row["Ib(A)"]), border=1, align='C')
                    
                    # Mise en évidence du disjoncteur et section
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(col_widths[5], 8, str(row["Disj(A)"]), border=1, align='C')
                    pdf.set_text_color(255, 100, 0)
                    pdf.cell(col_widths[6], 8, str(row["Section"]), border=1, align='C')
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("Helvetica", "", 9)
                    
                    pdf.cell(col_widths[7], 8, str(row["dU(%)"]), border=1, align='C', ln=True)

                pdf.ln(15)
                pdf.set_font("Helvetica", "I", 8)
                pdf.cell(190, 5, "* Le calcul des sections est basé sur la chute de tension admissible (3% éclairage, 5% autres).", ln=True)
                
                return pdf.output()

            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("📄 Éditer le Carnet de Câbles (PDF)", type="primary"):
                st.download_button("📥 Télécharger PDF", bytes(generate_pdf_cables()), f"Cables_{nom_tableau}.pdf")
            if col_btn2.button("🗑️ Vider le Carnet"):
                st.session_state.cables_db = []; st.rerun()

    # ---------------------------------------------------------
    # MODULE 2 : BILAN DE PUISSANCE TGBT
    # ---------------------------------------------------------
    elif menu == "📊 2. Bilan de Puissance (TGBT)":
        st.title("📊 Bilan de Puissance du Tableau (TGBT)")
        
        col_p1, col_p2 = st.columns(2)
        nom_projet = col_p1.text_input("Nom du Projet / Client", "Usine / Résidence")
        nom_tgbt = col_p2.text_input("Nom du Tableau", "TGBT")

        if 'bilan_pro' not in st.session_state: st.session_state.bilan_pro = []

        with st.expander("➕ Ajouter une charge", expanded=True):
            with st.form("form_bilan"):
                c1, c2, c3 = st.columns([2, 1, 1])
                nom_c = c1.text_input("Désignation")
                p_inst = c2.number_input("P. Installée (W)", min_value=0, value=1000)
                type_c = c3.selectbox("Type", ["Éclairage", "Prises", "Moteur", "Chauffage", "Divers"])
                
                ku_def = 1.0 if type_c in ["Éclairage", "Chauffage"] else 0.75 if type_c == "Moteur" else 0.5 if type_c == "Prises" else 0.8
                ku = st.slider("Facteur d'utilisation (Ku)", 0.1, 1.0, ku_def)
                
                if st.form_submit_button("Ajouter au Bilan"):
                    st.session_state.bilan_pro.append({
                        "Désignation": nom_c, "Famille": type_c, "P.Inst": p_inst, "Ku": ku, "P.Abs": int(p_inst * ku)
                    })

        if st.session_state.bilan_pro:
            st.dataframe(st.session_state.bilan_pro, use_container_width=True)
            
            p_total_inst = sum(x['P.Inst'] for x in st.session_state.bilan_pro)
            p_total_abs = sum(x['P.Abs'] for x in st.session_state.bilan_pro)
            
            ks = st.slider("Facteur de Simultanéité Global (Ks)", 0.4, 1.0, 0.8)
            p_souscription = p_total_abs * ks
            
            c_r1, c_r2, c_r3 = st.columns(3)
            c_r1.metric("Total Installé", f"{p_total_inst} W")
            c_r2.metric("Total Absorbé (Ku)", f"{p_total_abs} W")
            c_r3.metric("PUISSANCE D'APPEL (Ks)", f"{int(p_souscription)} W")

            def generate_pdf_bilan():
                pdf = FCELEC_Report()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(190, 10, f" BILAN DE PUISSANCE - {nom_projet.upper()} ({nom_tgbt.upper()})", border=1, ln=True, align="C", fill=True)
                pdf.ln(8)
                
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_fill_color(200, 200, 200)
                pdf.cell(70, 8, "Circuit", 1, 0, 'C', True)
                pdf.cell(40, 8, "Type", 1, 0, 'C', True)
                pdf.cell(30, 8, "P.Inst (W)", 1, 0, 'C', True)
                pdf.cell(20, 8, "Ku", 1, 0, 'C', True)
                pdf.cell(30, 8, "P.Abs (W)", 1, 1, 'C', True)
                
                pdf.set_font("Helvetica", "", 10)
                for c in st.session_state.bilan_pro:
                    pdf.cell(70, 8, c['Désignation'][:30], 1)
                    pdf.cell(40, 8, c['Famille'], 1, 0, 'C')
                    pdf.cell(30, 8, str(c['P.Inst']), 1, 0, 'C')
                    pdf.cell(20, 8, str(c['Ku']), 1, 0, 'C')
                    pdf.cell(30, 8, str(c['P.Abs']), 1, 1, 'C')
                
                pdf.ln(10)
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_fill_color(255, 245, 230)
                pdf.cell(190, 12, f"PUISSANCE MAXIMALE D'APPEL (Ks={ks}) : {int(p_souscription)} Watts", border=1, ln=True, align="C", fill=True)
                
                return pdf.output()

            col_b1, col_b2 = st.columns(2)
            if col_b1.button("📄 Éditer la Note de Bilan (PDF)", type="primary"):
                st.download_button("📥 Télécharger le Bilan", bytes(generate_pdf_bilan()), f"Bilan_{nom_tgbt}.pdf")
            if col_b2.button("🗑️ Réinitialiser le Bilan"):
                st.session_state.bilan_pro = []; st.rerun()

    # ---------------------------------------------------------
    # MODULE 3 & 4 (Cos Phi et IRVE inchangés - très performants)
    # ---------------------------------------------------------
    elif menu == "📉 3. Compensation (Cos φ)":
        st.title("📉 Compensation d'Énergie Réactive")
        with st.container(border=True):
            p_kw = st.number_input("Puissance Active (kW)", min_value=1.0, value=100.0)
            col1, col2 = st.columns(2)
            cos_ini = col1.number_input("Cos φ actuel", min_value=0.3, max_value=0.99, value=0.75, step=0.01)
            cos_vise = col2.number_input("Cos φ cible", min_value=0.8, max_value=1.0, value=0.95, step=0.01)
            Qc = p_kw * (math.tan(math.acos(cos_ini)) - math.tan(math.acos(cos_vise)))
            st.success(f"Puissance Batterie Condensateurs : **{math.ceil(Qc)} kVAR**")

    elif menu == "🚘 4. Infrastructure IRVE":
        st.title("🚘 Mobilité Électrique (IRVE)")
        p_borne = st.selectbox("Puissance de la borne (AC)", ["3.7 kW (16A Mono)", "7.4 kW (32A Mono)", "11 kW (16A Tri)", "22 kW (32A Tri)"])
        if "Mono" in p_borne: st.write("- **Câble** : 10 mm² | **Disjoncteur** :", "20A" if "3.7" in p_borne else "40A")
        else: st.write("- **Câble** : 5G10 mm² | **Disjoncteur** :", "20A" if "11" in p_borne else "40A")
        st.warning("- **Différentiel** : 30mA Type B obligatoire.")

    st.sidebar.markdown("---")
    if st.sidebar.button("Se déconnecter"):
        st.session_state.clear(); st.rerun()