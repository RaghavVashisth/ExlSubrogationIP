import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import streamlit.components.v1 as components
import os
import tempfile
from report_generator import generate_demand_letter_from_text, create_demand_package_final_reports, create_internal_final_reports
import base64
from llm_processing import llm
import shutil



# -------------------- Login Credential System --------------------
USER_CREDENTIALS = {
    "admin": "admin123",
    "exluser": "exl2025"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

def login():
    st.image("exl logo.png", use_container_width=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {username}!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

if not st.session_state.logged_in:
    login()
    st.stop()

# -------------------- App Config and Style --------------------
st.set_page_config(page_title="Subrogation Dashboard", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: black; }
        section[data-testid="stSidebar"] { background-color: #F5F5F5 !important; color: black !important; }
        * { color: black !important; }
        div[data-baseweb="select"], div[data-baseweb="popover"], div[data-baseweb="option"], div[data-baseweb="menu"] {
            background-color: white !important; color: black !important; border: 1px solid #ccc !important; border-radius: 5px !important;
        }
        div[data-baseweb="option"]:hover, div[data-baseweb="option"][aria-selected="true"] {
            background-color: #e6e6e6 !important;
        }
        .stButton > button {
            background-color: white !important; color: black !important; border: 1px solid #ccc !important; border-radius: 5px !important;
        }
        .stButton > button:hover {
            background-color: #e6e6e6 !important;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------- Sidebar --------------------
with st.sidebar:
    st.image("exl logo.png", use_container_width=True)
    selected_screen = st.radio("📁 Navigation", [
        "📊 Claim Dashboard", 
        "📑 Subrogation Workbench",
        "🧠 Q&A Assistant", 
        "📊 Monitoring Dashboard",
        "📈 Subrogation KPIs"
    ])


# -------------------- Load Data --------------------
# data_path = 'claims_only_Data.csv'
data_path = "syntheticsubrogationfulldataset_dummy2.csv"
Notes_path = 'Notes_Data.csv'
@st.cache_data(ttl=0)
def load_data():
    cdf = pd.read_csv(data_path)
    ndf = pd.read_csv(Notes_path,sep ='|')
    df = cdf.merge(ndf[['Claim_Number','Claims_Notes','Summary']],how='left',on= 'Claim_Number')
    # df['Prediction'] = pd.to_numeric(df['Prediction'], errors='coerce').fillna(0).astype(int)
    state_group_map = {
        "Pure": "Pure Comparative Negligence",
        "Regular": "Contributory Negligence"
        # "Michigan" is left unchanged
    }
    df["STATE_GROUP"] = df["STATE_GROUP"].replace(state_group_map)
    if 'User_Action' not in df.columns:
        df['User_Action'] = ''
    return df

df = load_data()

# Directories you want to clear
DIR1 = "processed_claims"
DIR2 = "uploaded_claims"

def clear_directory(dir_path):
    """Remove all files and subfolders inside a directory."""
    if os.path.exists(dir_path):
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                st.error(f"Error deleting {item_path}: {e}")

# Sidebar Reset Button
st.sidebar.subheader("⚙️ Settings")
if st.sidebar.button("🔄 Reset App"):
    clear_directory(DIR1)
    clear_directory(DIR2)
    st.sidebar.success("✅ All data cleared from directories!")
    st.rerun()   # refresh app after reset



# -------------------- 📊 Dashboard Screen --------------------
if selected_screen == "📊 Claim Dashboard":
    st.title("🚨 Subrogation Propensity Claims Review Dashboard")

    # Toggle filters
    enable_filters = st.checkbox("🔎 Enable Filters", value=True)

    claim_search = st.text_input("🔍 Search by Claim Number", key="claim_search")

    if enable_filters:
        st.markdown("### 🛠️ Apply Filters")
        filter_cols = st.columns(3)

        with filter_cols[0]:
            state_filter = st.selectbox('STATE', [" "] + list(df['STATE_GROUP'].unique()), key='state_filter')

        with filter_cols[1]:
            peril_filter = st.selectbox("MAJOR PERIL", [" "] + list(df['MAJ_PERIL_CD'].unique()), key='peril_filter')

        with filter_cols[2]:
            sub_det = st.selectbox("LOB SUB-LOB", [" "] + list(df['SUB_DTL_DESC'].unique()), key='sub_det_filter')

        # Apply filters
        filtered_df = df.copy()
        if state_filter != " ":
            filtered_df = filtered_df[filtered_df['STATE_GROUP'] == state_filter]
        if peril_filter != " ":
            filtered_df = filtered_df[filtered_df['MAJ_PERIL_CD'] == peril_filter]
        if sub_det != " ":
            filtered_df = filtered_df[filtered_df['SUB_DTL_DESC'] == sub_det]
    else:
        filtered_df = df.copy()

    # Apply claim number search if entered
    if claim_search.strip():
        filtered_df = filtered_df[filtered_df['Claim_Number'].astype(str).str.contains(claim_search.strip(), case=False)]

    # suspicious_df = filtered_df[filtered_df['Prediction'] == 1].copy()
    suspicious_df = filtered_df.sort_values(by=['ML_SCORE'],ascending=False)

    # Download filtered suspicious claims
    if not suspicious_df.empty:
        download_df = suspicious_df.copy()
        download_csv = download_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=download_csv,
            file_name="suspicious_claims.csv",
            mime="text/csv"
        )

    if suspicious_df.empty:
        st.info("⚠️ No suspected Subrogated claims found with current filters or search.")
    else:
        st.subheader("📋 Review and Act on Each Suspected Claim")

        for idx, row in suspicious_df.iterrows():
            st.markdown("---")
            cols = st.columns([2, 1.2, 0.8, 1.2, 0.8, 1.2, 1.2, 1.2, 1,1,2, 1.2])

            with cols[0]: st.markdown(f"**Claim:** {row['Claim_Number']}")
            with cols[1]: st.markdown(f"**Peril:** {row['MAJ_PERIL_CD']}")
            with cols[2]: st.markdown(f"**State:** {row['FTR_JRSDTN_ST']}")
            with cols[3]: st.markdown(f"**Paid:** ${row['PAID_FINAL']:.2f}")
            with cols[4]: st.markdown(f"**Age:** {row['CLMNT_AGE_AT_TM_OF_LOSS']}")
            with cols[5]: st.markdown(f"**Injury:** {row['INJRY_TYPE_DESC']}")
            with cols[6]: st.markdown(f"**Loss Party:** {row['LOSS_PARTY']}")
            with cols[7]: st.markdown(f"**Severity:** {row['CLM_LOSS_SEVERITY_CD']}")
            with cols[8]: st.markdown(f"**ML Score:** {row['ML_SCORE']}")

            # --- New Column for Notes Summary Toggle ---
            with cols[9]:
                st.markdown("**Notes**") 
                show_summary = st.toggle("", key=f"notes_toggle_{idx}")
            if show_summary:
                st.text_area(
                    "Claim Notes Summary",
                    value=row.get("Summary", "No summary available."),
                    height=500,
                    key=f"notes_area_{idx}"
                )

            with cols[10]:
                selected_action = st.selectbox(
                    "Action",
                    ["", "ASSIGNED", "NOT ASSIGNED", "No Action"],
                    key=f"action_{idx}",
                    index=["", "ASSIGNED", "NOT ASSIGNED", "No Action"].index(row['User_Action']) if row['User_Action'] in ["", "ASSIGNED", "NOT ASSIGNED", "No Action"] else 0
                )

            with cols[11]:
                if st.button("💾 Save", key=f"save_{idx}"):
                    df_all = pd.read_csv(data_path)
                    df_all.at[idx, 'User_Action'] = selected_action
                    df_all.to_csv(data_path, index=False)
                    st.success(f"✅ Action saved for Claim {row['Claim_Number']}")


# # -------------------- 📈 KPI Screen --------------------
elif selected_screen == "📈 Subrogation KPIs":
    st.title("📈 Subrogation Business KPIs")
    st.set_page_config(page_title="Subrogation KPI Dashboard", layout="wide")
    # Title
    st.title("🚨 Subrogation Propensity Claims Review Dashboard")

    # Aggregated KPIs
    total_claims = df["Claim_Number"].nunique()
    total_paid = df["PAID_FINAL"].sum()
    total_target_subro = df["Target_Subro"].sum()
    avg_paid = df["PAID_FINAL"].mean()
    avg_target_subro = df["Target_Subro"].mean()
    Total_Recovered = df['RECOVERY_AMT'].sum()
    AVG_Recovered = df['RECOVERY_AMT'].mean()

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🧾 Total Claims", f"{total_claims}")
    col2.metric("💰 Total Paid", f"${total_paid:,.0f}")
    col3.metric("🎯 Claims In Subro", f"{total_target_subro:,.0f}")
    col4.metric("📉 Avg Paid / Claim", f"${avg_paid:,.0f}")
    # col5.metric("📈 Avg Target Subro / Claim", f"${avg_target_subro:,.0f}")
    col5.metric("📈 Total Recovered", f"${Total_Recovered:,.0f}")
    col6.metric("📈 Avg Recoverd / Claim", f"${AVG_Recovered:,.0f}")


    st.markdown("---")

    # Aggregated by Accident State
    st.subheader("Subrogation KPIs by State")
    state_summary = df.groupby("STATE_GROUP").agg({
        "Claim_Number": "count",
        "PAID_FINAL": "sum",
        "Target_Subro": "sum"
    }).reset_index().rename(columns={"Claim_Number": "Total Claims"})

    fig1 = px.bar(state_summary, x="STATE_GROUP", y="Target_Subro",
                title="Target Subrogation by State", labels={"ACDNT_ST_DESC": "State Group"})
    st.plotly_chart(fig1, use_container_width=True)

    # Aggregated by Account Category
    st.subheader("Subrogation KPIs by Account Category")
    acct_summary = df.groupby("ACCT_CR_DESC").agg({
        "Claim_Number": "count",
        "PAID_FINAL": "sum",
        "Target_Subro": "sum"
    }).reset_index().rename(columns={"Claim_Number": "Total Claims"})

    fig2 = px.bar(acct_summary, x="ACCT_CR_DESC", y="Target_Subro",
                title="Target Subrogation by Account Category", labels={"ACCT_CR_DESC": "Account Category"})
    st.plotly_chart(fig2, use_container_width=True)


# -------------------- 📊 Monitoring Dashboard --------------------
elif selected_screen == "📊 Monitoring Dashboard":
    st.title("📊 Monitoring Dashboard - Power BI")

    st.markdown("#### Embedded Power BI Dashboard Below:")
    
    powerbi_embed_url = """
    <iframe title="SUBROGATION PROPENSITY MODEL MONITORING" width="1140" height="600" 
        src="https://app.powerbi.com/reportEmbed?reportId=49d274d9-37a4-4f06-ac05-dc7a98960ed9&autoAuth=true&ctid=dafe49bc-5ac3-4310-97b4-3e44a28cbf18&actionBarEnabled=true" 
        frameborder="0" allowFullScreen="true"></iframe>
    """
    components.html(powerbi_embed_url, height=650)


# -------------------- 🧠 Q&A Assistant --------------------
elif selected_screen == "🧠 Q&A Assistant":
    st.title("🧠 Q&A Assistant (Powered by OpenAI)")
    st.markdown("This assistant answers questions based on the Adjuster Claim Notes.")

    # Select claim
    ndf = df[df['Claims_Notes'].notnull()]
    selected_claim = st.selectbox("Select a Claim Number", ndf["Claim_Number"].unique())

    claim_notes = df[df["Claim_Number"] == selected_claim]["Claims_Notes"].values[0] if "Claims_Notes" in df.columns else ""


    st.markdown("### 📄 Original Claim Notes")
    st.text_area("Claim Notes", claim_notes, height=200, disabled=True)

    # --------- Q&A Chatbot Section ----------
    st.markdown("### 💬 Ask Questions About This Claim")

    # --- User Question Section ---
    user_question = st.text_input("Type your question here:")
    if user_question.strip():
        with st.spinner("Generating answer..."):
            try:
                qa_prompt = f"""
                Use the following claim notes to answer the question.
                Claim Notes:
                {claim_notes}

                Question: {user_question}
                Answer based only on the claim notes.
                """
                # response = client.models.generate_content(
                #     model="gemini-2.5-flash",
                #     contents=qa_prompt
                # )
                # answer = response.text if hasattr(response, "text") else "No answer generated."
                answer = llm(qa_prompt)

                st.markdown("**Answer:**")
                st.info(answer)
            except Exception as e:
                st.error(f"Error generating answer: {e}")

    # --- Template Questions Section ---
    st.markdown("---")
    st.markdown("### 📑 Frequently Asked Questions")

    template_questions = [
        "Mention all the key people involved in claim",
        "Mention all the key organisation involved in claim",
        "What is percentage of fault for insured?",
        "Was a third party responsible for the loss?",
        "Are there statute of limitations to consider?",
        "Is this a Comparative negligence and contributory negligence state?",
        "Is there clear documentation of how the loss occurred?",
        "What is the reason or cause of Loss?",
        "Are there any admissions of fault or liability by another party?",
        "Is the third party insured, and who is their carrier?",
        "Was a police report or official investigation conducted?",
        "What damages were paid out and to whom?",
        "Were any waivers of subrogation signed or implied?"

    ]

    for q in template_questions:
        with st.expander(q):  # Expandable answers for each template question
            with st.spinner("Fetching answer..."):
                try:
                    qa_prompt = f"""
                    You are an insurance claims assistant.
                    Use the following claim notes to answer the question.
                    Claim Notes:
                    {claim_notes}

                    Question: {q}
                    Answer based only on the claim notes.
                    """
                    answer = llm(qa_prompt)
                    st.markdown("**Answer:**")
                    st.success(answer)
                except Exception as e:
                    st.error(f"Error generating answer: {e}")

# -------------------- 📑 Actioned Claims Screen --------------------
elif selected_screen == "📑 Subrogation Workbench":
    
    # Upload & process files
    UPLOAD_BASE_DIR = "uploaded_claims"
    PROCESSED_BASE_DIR = "processed_claims"
    os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)
    os.makedirs(PROCESSED_BASE_DIR, exist_ok=True)
    LOGO_PATH = "exl_logo.png"

    def display_pdf(file_path):
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)



    # -------------------- DEMAND LETTER EDITOR SCREEN --------------------
    if "view" in st.session_state and st.session_state["view"] == "demand_package":
        claim_number = st.session_state["selected_claim"]
        claim_details = df[df["Claim_Number"] == claim_number].to_dict("records")[0]

        st.subheader(f"✍️ Edit Demand Letter for Claim {claim_number}")

        At_fault_party_insurance_carrier_name = "XYZ Insurance Company"
        Third_party_insurance_carrier_Address = "XYZ Plaza, Columbus, Ohio 43215-2220, USA"
        Insured_Name = "Reginald Williams"
        Other_Party_insured_name = "Karen Walton"
        Date_of_Loss = "09/15/2022"
        other_party_adjuster_name = "Andrea Duffield"
        Insured_adjuster_name = "Carol Bradford"

        # Default demand letter template
        default_letter = f"""
        To:
        {At_fault_party_insurance_carrier_name}
        {Third_party_insurance_carrier_Address}

        Re: Subrogation Demand - Claim No. {claim_number}
        Our Insured: {Insured_Name}
        Your Insured: {Other_Party_insured_name}
        Date of Loss: {Date_of_Loss}
        Loss Location: {claim_details['STATE_GROUP']}

        Dear {other_party_adjuster_name},

        We represent {Insured_Name}, the automobile insurance carrier for {Insured_Name}. On {Date_of_Loss},
        your insured, {Other_Party_insured_name} negligently caused a motor vehicle collision 
        at {claim_details['STATE_GROUP']}. Based on the police report and supporting evidence, your insured
        was cited for failure to stop at a red light, thereby establishing liability.

        As a result of this incident, {Insured_Name} indemnified our insured for the following damages:

        Category                Amount Paid (USD)
        ------------------------------------------------
        Vehicle Repairs             $1260
        Rental Car Expenses     $500
        Towing & Storage           $200
        Medical Payments         $3000
        ------------------------------------------------
        Total Demand            $4,960

        We hereby demand reimbursement in the amount of $4,960 within thirty (30) days
        of receipt of this letter. Enclosed please find supporting documentation, including
        proof of payment, repair invoices, photographs, and the police report.

        Should this matter remain unresolved, we reserve the right to pursue recovery
        through Arbitration Forums, Inc. or litigation as applicable under state law.

        Please direct all correspondence and payments to the undersigned.

        Sincerely,
        {Insured_adjuster_name}
        Sr. Relationship Manager
        ABC Insurance Company
        Contact: +0001321513312
        carol@ABCInsurance.com
            """

        # Let user edit letter
        edited_letter = st.text_area("📝 Edit Demand Letter", default_letter, height=600)

        # Save edited text in session
        st.session_state["edited_demand_letter"] = edited_letter

        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("⬅️ Back to Subrogation Workbench"):
                st.session_state["view"] = "subro_workbench"
                st.rerun()

        with col2:
            if st.button("✅ Generate Demand Package"):
                processed_dir = os.path.join(PROCESSED_BASE_DIR, f"{claim_number}")
                os.makedirs(processed_dir, exist_ok=True)

                OUTPUT_PDF = os.path.join(processed_dir, "Subro_Demand_exhibits_package.pdf")
                INTERNAL_PDF = os.path.join(processed_dir, "Internal_adjuster_notes_report.pdf")

                # Generate demand letter from edited text
                demand_letter_pdf = generate_demand_letter_from_text(edited_letter)

                # Merge cover + demand letter + exhibits
                exhibits = st.session_state["uploaded_docs"][claim_number]
                create_demand_package_final_reports(
                    exhibit_files=exhibits,
                    output_demand_pdf=OUTPUT_PDF,
                    claim_id=str(claim_number),
                    prepared_by="System Auto-Generated",
                    logo_path=LOGO_PATH,
                    demand_letter_pdf=demand_letter_pdf  # pass custom edited letter
                )
                exhibits_pdf = os.path.join(PROCESSED_BASE_DIR, f"{claim_number}", "Subro_Demand_exhibits_package.pdf")
                # Store path in session for preview/download
                st.session_state["final_demand_package"] = exhibits_pdf
                st.session_state["view"] = "demand_package_preview"
                st.rerun()

    # -------------------- DEMAND PACKAGE PREVIEW SCREEN --------------------
    elif "view" in st.session_state and st.session_state["view"] == "demand_package_preview":
        claim_number = st.session_state["selected_claim"]
        merged_pdf = st.session_state.get("final_demand_package")

        st.subheader(f"📦 Final Demand Package Preview - Claim {claim_number}")

        if merged_pdf and os.path.exists(merged_pdf):
            # Preview inside Streamlit
            with open(merged_pdf, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

            # Download button
            with open(merged_pdf, "rb") as f:
                st.download_button(
                    label="⬇️ Download Final Demand Package",
                    data=f,
                    file_name=f"Final_Demand_Package_{claim_number}.pdf",
                    mime="application/pdf",
                    key=f"download_final_{claim_number}"
                )

        if st.button("⬅️ Back to Edit Demand Letter"):
            st.session_state["view"] = "demand_package"
            st.rerun()


    # -------------------- Internal Notes Screen --------------------
    elif "view" in st.session_state and st.session_state["view"] == "internal_notes":
        claim_number = st.session_state["selected_claim"]
        internal_pdf = os.path.join(PROCESSED_BASE_DIR, f"{claim_number}", "Internal_adjuster_notes_report.pdf")

        st.subheader(f"📝 Internal Adjuster Report for Claim {claim_number}")

        if os.path.exists(internal_pdf):

            # Preview PDF
            display_pdf(internal_pdf)

            # Download button
            with open(internal_pdf, "rb") as f:
                st.download_button(
                    label="⬇️ Download Internal Adjuster Report",
                    data=f,
                    file_name=f"Internal_adjuster_notes_report_{claim_number}.pdf",
                    mime="application/pdf",
                    key=f"download_internal_{claim_number}"
                )

        else:
            st.warning("⚠️ Internal Adjuster Notes Report not found for this claim.")

        # Back button
        if st.button("⬅️ Back to Subrogation Workbench"):
            st.session_state["view"] = "subro_workbench"
            st.rerun()

    # -------------------- Workbench Default View --------------------
    else:
        st.title("📑 Subrogation Workbench")

        actioned_df = df[df["User_Action"].isin(["ASSIGNED"])].copy()

        if actioned_df.empty:
            st.info("⚠️ No claims have been assigned to Subrogation Workbench.")
        else:
            st.success(f"✅ Showing {len(actioned_df)} claims where actions were saved.")

            if "uploaded_docs" not in st.session_state:
                st.session_state["uploaded_docs"] = {}

            for idx, row in actioned_df.iterrows():
                with st.container(border=True):
                    col1, col2, col3, col4, col5,col6 = st.columns([1.8,3,1,2,1,1])
                    with col1:
                        st.write(f"**Claim #:** {row['Claim_Number']}")
                    with col2:
                        selected_action = st.selectbox(
                            "Action",
                            [" ","Subrogation Assignment", "A New Witness Added Onto the Claim", "Send First Demand for Subrogation Letter/ Package", "Investigation Pending", "Medical/ Police Report Status", "Close - Not Pursuing"],
                            key=f"action_{idx}",
                            index=[" ","Subrogation Assignment", "A New Witness Added Onto the Claim", "Send First Demand for Subrogation Letter/ Package", "Investigation Pending", "Medical/ Police Report Status", "Close - Not Pursuing"].index(row['Subro_User_Action']) if row['Subro_User_Action'] in [" ","Subrogation Assignment", "A New Witness Added Onto the Claim", "Send First Demand for Subrogation Letter/ Package", "Investigation Pending", "Medical/ Police Report Status", "Close - Not Pursuing"] else 0
                        )

                    with col3:
                        if st.button("💾 Save", key=f"save_{idx}"):
                            df_all = pd.read_csv(data_path)
                            df_all.at[idx, 'Subro_User_Action'] = selected_action
                            df_all.to_csv(data_path, index=False)
                            st.success(f"✅ Action saved for Claim {row['Claim_Number']}")



                    with col4:
                        uploaded_files = st.file_uploader(
                            f"📎 Upload Files (Claim {row['Claim_Number']})",
                            type=None,
                            key=f"uploader_{row['Claim_Number']}",
                            accept_multiple_files=True
                        )

                        if uploaded_files:
                            claim_dir = os.path.join(UPLOAD_BASE_DIR, f"{row['Claim_Number']}")
                            os.makedirs(claim_dir, exist_ok=True)

                            for uploaded_file in uploaded_files:
                                file_path = os.path.join(claim_dir, uploaded_file.name)
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())

                                if row['Claim_Number'] not in st.session_state["uploaded_docs"]:
                                    st.session_state["uploaded_docs"][row['Claim_Number']] = []
                                if file_path not in st.session_state["uploaded_docs"][row['Claim_Number']]:
                                    st.session_state["uploaded_docs"][row['Claim_Number']].append(file_path)

                                st.success(f"✅ {uploaded_file.name} saved in {claim_dir}")

                            # Generate reports for all exhibits
                            exhibits = st.session_state["uploaded_docs"][row['Claim_Number']]
                            processed_dir = os.path.join(PROCESSED_BASE_DIR, f"{row['Claim_Number']}")
                            os.makedirs(processed_dir, exist_ok=True)

                            OUTPUT_PDF = os.path.join(processed_dir, "Subro_Demand_exhibits_package.pdf")
                            INTERNAL_PDF = os.path.join(processed_dir, "Internal_adjuster_notes_report.pdf")
                            claim_details = df[df["Claim_Number"] == row['Claim_Number']].to_dict("records")[0]

                            create_internal_final_reports(
                                exhibit_files=exhibits,
                                output_internal_pdf=INTERNAL_PDF,
                                claim_id=str(claim_details['Claim_Number']),
                                prepared_by="System Auto-Generated",
                                logo_path=LOGO_PATH
                            )

                            st.success(f"📄 Reports generated for Claim {row['Claim_Number']}")

                    # Demand Package button
                    with col5:
                        if st.button("📄 Demand Package", key=f"demand_{row['Claim_Number']}"):
                            st.session_state["selected_claim"] = row["Claim_Number"]
                            st.session_state["view"] = "demand_package"
                            st.rerun()

                    # Internal Notes button
                    with col6:
                        if st.button("📝 Internal Report", key=f"notes_{row['Claim_Number']}"):
                            st.session_state["selected_claim"] = row["Claim_Number"]
                            st.session_state["view"] = "internal_notes"
                            st.rerun()
