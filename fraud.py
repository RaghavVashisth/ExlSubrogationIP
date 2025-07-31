import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import streamlit.components.v1 as components


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
    # selected_screen = st.radio("📁 Navigation", ["📊 Dashboard", "📈 Subrogation KPIs"])
    selected_screen = st.radio("📁 Navigation", ["📊 Claim Dashboard", "📈 Subrogation KPIs", "📊 Monitoring Dashboard"])


# -------------------- Load Data --------------------
data_path = 'claims_data.csv'

@st.cache_data(ttl=0)
def load_data():
    df = pd.read_csv(data_path)
    df['Prediction'] = pd.to_numeric(df['Prediction'], errors='coerce').fillna(0).astype(int)
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

# -------------------- 📊 Dashboard Screen --------------------
if selected_screen == "📊 Claim Dashboard":
    st.title("🚨 Subrogation Propensity Claims Review Dashboard")

    st.markdown("### 🔎 Filter Claims")
    filter_cols = st.columns(3)

    with filter_cols[0]:
        state_filter = st.selectbox('STATE', df['STATE_GROUP'].unique(), key='state_filter')

    with filter_cols[1]:
        peril_filter = st.selectbox("MAJOR PERIL", df['MAJ_PERIL_CD'].unique(), key='peril_filter')

    with filter_cols[2]:
        sub_det = st.selectbox("LOB SUB-LOB", df['SUB_DTL_DESC'].unique(), key='sub_det_filter')

    filtered_df = df[
        (df['STATE_GROUP'] == state_filter) &
        (df['MAJ_PERIL_CD'] == peril_filter) &
        (df['SUB_DTL_DESC'] == sub_det)
    ]

    suspicious_df = filtered_df[filtered_df['Prediction'] == 1].copy()

    if suspicious_df.empty:
        st.info("No suspected fraudulent claims found with current filters.")
    else:
        st.subheader("📋 Review and Act on Each Suspected Claim")

        for idx, row in suspicious_df.iterrows():
            st.markdown("---")
            cols = st.columns([1.5, 1.2, 1.2, 1.2, 1, 1.2, 1.2, 1.2, 1, 2, 1.2])

            with cols[0]: st.markdown(f"**Claim:** {row['Claim_Number']}")
            with cols[1]: st.markdown(f"**Peril:** {row['MAJ_PERIL_CD']}")
            with cols[2]: st.markdown(f"**State:** {row['FTR_JRSDTN_ST']}")
            with cols[3]: st.markdown(f"**Paid:** ${row['PAID_FINAL']:.2f}")
            with cols[4]: st.markdown(f"**Age:** {row['CLMNT_AGE_AT_TM_OF_LOSS']}")
            with cols[5]: st.markdown(f"**Injury:** {row['INJRY_TYPE_DESC']}")
            with cols[6]: st.markdown(f"**Loss Party:** {row['LOSS_PARTY']}")
            with cols[7]: st.markdown(f"**Severity:** {row['CLM_LOSS_SEVERITY_CD']}")
            with cols[8]: st.markdown(f"**ML Score:** {row['Probability']}")

            with cols[9]:
                selected_action = st.selectbox(
                    "Action",
                    ["", "ASSIGNED", "NOT ASSIGNED", "No Action"],
                    key=f"action_{idx}",
                    index=["", "ASSIGNED", "NOT ASSIGNED", "No Action"].index(row['User_Action']) if row['User_Action'] in ["", "ASSIGNED", "NOT ASSIGNED", "No Action"] else 0
                )

            with cols[10]:
                if st.button("💾 Save", key=f"save_{idx}"):
                    df_all = pd.read_csv(data_path)
                    df_all.at[idx, 'User_Action'] = selected_action
                    df_all.to_csv(data_path, index=False)
                    st.success(f"✅ Action saved for Claim {row['Claim_Number']}")

# # -------------------- 📈 KPI Screen --------------------
elif selected_screen == "📈 Subrogation KPIs":
    st.title("📈 Subrogation Business KPIs")

#     # KPIs
#     total_paid = df["PAID_FINAL"].sum()
#     potential_subro = df["Target_Subro"].sum()
#     num_claims = df["Claim_Number"].nunique()

#     col1, col2, col3 = st.columns(3)
#     col1.metric("Total Paid Final", f"${total_paid:,.0f}")
#     col2.metric("Target Subrogation", f"${potential_subro:,.0f}")
#     col3.metric("Unique Claims", f"{num_claims:,}")

#     st.markdown("### 📊 Paid vs. Target Subrogation by Claim")
#     fig1 = px.bar(df.sort_values("PAID_FINAL", ascending=False).head(30),
#                   x="Claim_Number", y=["PAID_FINAL", "Target_Subro"],
#                   barmode="group", title="Top 30 Claims - Paid vs Subrogation")
#     st.plotly_chart(fig1, use_container_width=True)

#     st.markdown("### 🌍 Subrogation Potential by State")
#     df_state = df.groupby("ACDNT_ST_DESC")[["PAID_FINAL", "Target_Subro"]].sum().reset_index()
#     fig2 = px.bar(df_state.sort_values("Target_Subro", ascending=False),
#                   x="ACDNT_ST_DESC", y="Target_Subro", title="Target Subrogation by State")
#     st.plotly_chart(fig2, use_container_width=True)


    st.set_page_config(page_title="Subrogation KPI Dashboard", layout="wide")

    # Title
    st.title("🚨 Subrogation Propensity Claims Review Dashboard")

    # Load your data
    # df = pd.read_csv("data/sample_data.csv")

    # Convert numeric fields
    # Aggregated KPIs
    total_claims = df["Claim_Number"].nunique()
    total_paid = df["PAID_FINAL"].sum()
    total_target_subro = df["Target_Subro"].sum()
    avg_paid = df["PAID_FINAL"].mean()
    avg_target_subro = df["Target_Subro"].mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🧾 Total Claims", f"{total_claims}")
    col2.metric("💰 Total Paid", f"${total_paid:,.0f}")
    col3.metric("🎯 Total Target Subro", f"{total_target_subro:,.0f}")
    col4.metric("📉 Avg Paid / Claim", f"${avg_paid:,.0f}")
    # col5.metric("📈 Avg Target Subro / Claim", f"${avg_target_subro:,.0f}")

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
