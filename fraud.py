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
    # selected_screen = st.radio("📁 Navigation", ["📊 Claim Dashboard", "📈 Subrogation KPIs", "📊 Monitoring Dashboard"])
    selected_screen = st.radio("📁 Navigation", [
    "📊 Claim Dashboard", 
    "📈 Subrogation KPIs", 
    "📊 Monitoring Dashboard", 
    "🧠 Generative AI Assistant"
    ])


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
    filter_cols = st.columns(4)

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
    # Download filtered suspicious claims
    if not suspicious_df.empty:
        # st.markdown("### 📥 Download Filtered Claims")
        download_df = suspicious_df.copy()
        download_csv = download_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=download_csv,
            file_name=f"suspicious_claims_{state_filter}_{peril_filter}_{sub_det}.csv",
            mime="text/csv"
        )



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


# -------------------- 🧠 Generative AI Assistant --------------------
elif selected_screen == "🧠 Generative AI Assistant":
    st.title("🧠 Claim Notes Assistant (Powered by Gemini)")
    st.markdown("This assistant summarizes claim notes and answers questions based on the claim context.")

    # Select claim
    selected_claim = st.selectbox("Select a Claim Number", df["Claim_Number"].unique())
    # Search box
    # from streamlit_searchbox import st_searchbox

    # def search_claims(query: str):
    #     options = df["Claim_Number"].unique()
    #     return [opt for opt in options if query.lower() in str(opt).lower()]

    # selected_claim = st_searchbox(
    #     search_function=search_claims,
    #     placeholder="Search & Select a Claim Number",
    #     key="claim_searchbox"
    # )
    # --------------------------------------------------------------------------------------
    # claim_notes = df[df["Claim_Number"] == selected_claim]["Claim_Notes"].values[0] if "Claim_Notes" in df.columns else ""
    claim_notes = """For claim number CLM-57398bv: called the attorney back @ 216-285-9991  spoke with Gloria    they sent a LOR    needing UIM opened    Tittle and Perlmuter  4106 Bridge Ave,  Cleveland, OH.  44113    FAX- 888-604-9299, We received some bills for Reginald Williams and we have no available coverage for UM based on limits. Reviewed dec page and we to have Med Pay coverage.      Transferred activity to Med Pay, Christine Perna.     Carol X5796714, Sent email asking for return call., per adj the reporting party was insd lawyer., Received email back from Nationwide in regard to my question as to whether they have $100K or greater BI limits and she responded that they have BI limits of $100K, therefore, we would have no available coverage has we have reduction of BI limits. We have UM/UIM limits of $100-300K which is the same as BI limits with Nationwide and with our reduction of limits, we would not have any available coverage.     Sent a "no coverage available" letter to attorney and closed file.     Carol X5404606, New loss received in liability  Type of Claim/Exposure:   UM/UIM Claim  Location of loss:  Leavitt Rd & State Rd 58 Lorain, OH  Policy Type:  Personal Auto Policy   Endorsements: PP0001-0698 Personal Auto Policy,  2312261-0506 Uninsured/Underinsured Motorist Coverage - Ohio    Policy Number/Mod: ANW-H861867-00  Effective Dates: 01/05/2022 to 01/05/2023  Underwriting Company: The Hanover Insurance Company    Named Insured:  Reginald Williams  Insured Vehicle: 2005 Jeep Grand vin #1J4GR48K35C516080 - Unit 001   Insured Driver:  Reginald Williams who is driver #1 on the policy    Coverage Limits: UM/UIM #100-300K  Exclusions/Conditions: None at this time  Umbrella Policy: No umbrella with Hanover and no end't on home policy    Endorsement 2312261-0506 Uninsured/Underinsured Motorist Coverage - Ohio  Part C - Uninsured Motorist Coverage   Part C is replaced by the following:   Insuring Agreement  A. We will pay compensatory damages which an "insured" is legally entitled to recover from the owner or operator of an:  1. "Uninsured Motor vehicle" or Underinsured motor vehicle because of "bodily injury":   a. Sustained by an "insured; and  b. Caused by an accident; and  The owner's or operator's liability for these damages must arise out of the ownership, maintenance or use of the "uninsured motor vehicle" or "underinsured motor vehicle". We will pay damages under this coverage caused by an accident with an "underinsured motor vehicle" only if 1. or 2. below applies:    1. The limits of liability under any applicable bodily injury liability bonds or policies have been exhausted by payments of judgments or settlements; or  2. A tentative settlement has been made between an "insured" and the insurer of the "underinsured motor vehicle" and we:         a. Have been given prompt written notice of both the tentative settlement and certification of the liability coverage limits of the owner or operator of the "underinsured motor vehicle"; and   b. Advance payment to the "insured" in an amount equal to the tentative settlement within 30 days after receipt of notification.   Any judgment for damages arising out of a suit brought without our written consent is not binding on us.   B. "Insured" as used in this Part means:  1. Your or any "family member";  2. Any person "occupying" "your covered auto";  3. Any person for damages that person is entitled to recover because of "bodily injury" to which this coverage applies sustained by a person described in 1. or 2. above.   D. "Underinsured Motor Vehicle" means a land motor vehicle or trailer of any type for which the sum of the limits of liability under all bodily injury liability bonds or policies applicable at the time of the accident is either:  1. Less than the limit of liability for this coverage; or  2. Reduced by payments to persons, other than "insureds", injured in the accident to less than the limit of liability for this coverage.   Limit of Liability  A. The limit of liability shown in the Schedule or in the Declarations for this coverage is our maximum limit of liability for all damages resulting from any one accident. This is the most we will pay regardless of the number of:  1. "Insureds";  2. Claims made;  3. Vehicles or premiums shown in the Declarations; or  4. Vehicles involved in the accident.   B. The limit of liability shall be reduced by all sums paid because of the "bodily injury" or "property damage" by or on behalf of persons or organizations who may be legally responsible. This includes all sums paid under Part A of this policy.        Carol X5404606, Called insured @ 216-285-9991  spoke with Julian  LAW OFFICE    was connected to someone needing to speak with Natalie, he then disconnected the call, Police Report: 2022-00031443 Other Carrier 1 Name-Policy No: -  Escalation Off per loss date too old. SEARCH SUCCESSFUL - POLICY:H861867 - UNIT COUNT:1 Policy Prefix: ANW Policy: H861867 Policy Type: Auto Loss Date: 9/15/2022 Copied from Reference#:22322290 Tow: N/C Rental: N/C Coll Ded: 500 Comp Ded: 250, police report received    file is already noted in regards to the PR narrative, IBC from NI re. Verification letter -- updated MSP info for file., Based on notes UIM was to be assigned not MP; assigned UIM to file, Received the following from paralegal in regard to Regional's injuries:     So far, we are aware of injuries to Mr. Williams's neck, back, shoulders, arms, and legs. We do not have more detailed information at this time. Mr. Wiliams went to an emergency department the same day of the accident and is currently being seen by a chiropractor.    Carol X5404606, Uploaded billing and supports in Medata // Success! Created record MCN: 2023022211523797CPE900, uploaded accurints-carrier for the following Carrier Discovery via Tort Name: Karen Walton  Carrier Discovery via Tort Vehicle Vin: 2018 Chev Cruze Vin #1G1BE5SM3J7169096  Titled/Registered Owner via Tort Vehicle Vin and/or License Plate: 2018 Chev Cruze Vin #1G1BE5SM3J7169096 / OH Plate DUS1925  Assets/Comprehensive report via Tort Name: Karen Walton  Carrier Discovery via Insured: Reginald Williams  all available in doc navs, Received email from Nationwide adjuster, Andrea Duffield who indicated that they are accepting 100% liability and while she cannot share her BI limits, they do have ABOVE state minimum and feel their limits are adequate to resolve his claim from the information they have to date.     Carol X5404606, Policy in force (Y/N): Y  Vehicle/Driver listed on policy (Y/N): 1: 2005 JEEP GRAND CHEROKEE/ #1 Reginald Williams  Relevant Priors: N/A    Comp/Collision (less DSA?): Collision $500  PD: 100K  Rental: 50/1500/3000    Applicable Endorsements: PLATINUM AUTO ESSENTIAL    Reg Letters Sent (Y/N): N/A    Note any coverage issues?: N/A, IBC from Mary at Firm - NI rcvd EMS bill and would like to process it through MP    Reopened MP and EMS bill only to be processed -- updated PIC Code    Atty will have EMS rebill to Hanover., IBC from insured  spoke with Reginald    he says he is receiving a lot of calls from lawyers and that the police department emailed the report to all of them    law office called him and he placed me on hold    waited and then disconnected the call, OIC is handling IV as a possible TL    closing my involvement, Contacted Nationwide, Claim #755761-GN, adjuster is Andrea Duffield @ Email: lashera@nationwide.com PH# 614-427-4243. I was unable to get this phone number to work so I sent email address to adjuster requesting BI limits.     Carol X5404606, IBC from Mary at Law Firm -- confirmed if utilizing MP will call back and let me know. MP will remain closed    Ph # 216-285-9991, Contacted Tittle & Perlmuter, atty is Katie Harris and Paralegal is Gloria Lee @ 216-285-9991. She indicated the at-fault driver is insured with Nationwide, Claim #755761-GN, adjuster is Andrea Duffield @ Email: lashera@nationwide.com PH# 614-427-4243. The attorney does not know BI limits are this time.     She will reach out to her client in setting up a recorded statement.     Reginald Williams was transported from scene to ER. He sustained injuries to include right shoulder, low back, (unknown right or left) knee, right foot and treating with several doctors for the various body parts.   He was also seeing someone else for different unrelated issues too. She will have her paralegal get back to me about more specifics on the treatment. I sent Paralegal email address to obtain additional details on the injuries and treatment.     Carol X5404606, IBC from Reginald re. MP letter sent out to him; he does not want to utilize MP cvg.    Advised to have Atty contact me if anything changes., This is a UM/UIM Claim and our limits are $100-300K. We received LOR from Tittle & Perlmuter, atty is Katie Harris and Paralegal is  Gloria Lee @ 216-285-9991 (Email: gloria@tittlelawfirm.com) and they are representing Reginald Williams for UM/UIM. They request copy of policy. Sent acknowledgement w/provisions.     APD statement with Reginald: He was alone and going to Home Depot when he was stopped at a red light on Tar Road at the intersection of Leavitt Rd. The light changed to green, insured proceeded and OV ran red light and struck the IV and then insured hit light pole. The OV struck a 3rd vehicle after hitting insured. Lorain PD to scene. He had damage to the right side and the frame was bent.     Lorain Police Report    Location: Leavitt Rd and Tower Blvd in Lorain, OH  Unit #1: Karen Walton (Owner/Driver)  Unit #2: Reginald Williams  Unit #3: Gabriella Jackson  Comments: Walton was traveling SB on Rt 58 approaching the intersection with Tower Blvd. IV was traveling WB on Tower Blvd approaching the intersection with St 58. Walton ran the red light striking IV. Insured ran off the road right, striking a light pole in front of 4130 N Leavitt Rd. Walton continued into parking lot of 4130 N Leavitte Rd (Starbucks), striking Jackson. Walton then struck a cable box and  shortly after came to rest.  It indicates both Walton and Williams taken via amb to Mercy Regional.     Carol X5404606, Requested Accurint as follows:     Carrier Discovery via Tort Name: Karen Walton  Carrier Discovery via Tort Vehicle Vin: 2018 Chev Cruze Vin #1G1BE5SM3J7169096  Titled/Registered Owner via Tort Vehicle Vin and/or License Plate:  2018 Chev Cruze Vin #1G1BE5SM3J7169096 / OH Plate DUS1925  Assets/Comprehensive report via Tort Name: Karen Walton  Carrier Discovery via Insured: Reginald Williams    Carol X5404606, Policy H861867  MOD 00  Eff Dates 1/5/22-23  UW CO The Hanover Insurance Company    Veh: 001: 2005 JEEP GRAND C  Driver 1 Reginald Williams    MP: $10K    Bill and Supports in docs // reopened claim / MP Exp and will upload bill when data transferred to Medata    Mercy Regional Medical Center  DOS: 9/15/22  Total: $13,998, Called: insured @ 443-593-2242  Spoke with Reginald    Confirm DOL: 09/15/2022    Confirm IV: 2005 Jeep Grand Cheroke    Confirm driver: Reginald Williams    Confirm passengers: none    Injuries: yes- attorney involvement   went to the hospital via ambulance    FOL: going to Home Depot, stopped at a red light, Tar Road and Leavitt Road, light change to green, IVD proceeded, OV ran the red light, hit IV and then IV hit a light pole    OV then hit another vehicle     Police/TP info: Lorain PD     POI: right side  damages- frame is bent      MOI/Appraisal/SOC:   OIC is handling the IV as a possible TL    IVD does not want a claim filed on his policy and then he started swearing at me and he hung up, Sent certified copy of policy to attorney via secure email.     Carol X5404606, Reviewed Accurint.     Carrier Discovery via Tort Name, Karen Walton shows Nationwide already documented to the file.     Carrier Discovery via Tort Vehicle, 2018 Chev Cruze shows Nationwide already documented to the file.   Several other policies listed but all cancelled prior to DOL.     ** No other policies available for BI coverage found.      Titled/Registered Owner via Tort Vehicle, 2018 Chev Cruze shows Karen Walton as the owner.     Assets/Comprehensive report via Tort Name, Karen Walton shows current address as 6595 Bluebird Lane Canal Winchester, OH. 43110 and shows 7923 Rice Rd Amherst, OH 44001.   Shows possible property owned at 1328 W 27th St Lorain, OH 44052 with Market Value of $97,200, Land Value is $25,300, Improvement Value is $71,900 and she along with Bonnie Hockman own the property jointly. No bankruptcies, liens or judgments.   She has Offense in 07/06/1995 which was a Homicide charge.   *** She appears uncollectible as the home is jointly owned.     Carrier Discovery via Insured, Reginald Williams shows this is the only policy for UM/UIM coverage on the DOL.     Carol X5404606"""


    st.markdown("### 📄 Original Claim Notes")
    st.text_area("Claim Notes", claim_notes, height=200, disabled=True)

    # Google Gemini API Setup
    from google import genai
    import os

    # Make sure API key is in your environment or replace directly here (not recommended for production)
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDqE83L2kuOcFyEh2y_P1waK300-D2HxDI"
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    # --------- Summary Section ----------
    if st.button("🔍 Generate Summary"):
        if claim_notes.strip():
            with st.spinner("Summarizing claim notes..."):
                try:
                    # prompt = f"""You are an expert insurance adjuster reviewing claim notes for potential indicators of subrogation related to the provided TOPIC. Your job is to thoroughly analyze the provided SUBROGATION LAWS and CLAIM NOTES and identify any red flags based on the provided QUESTIONS.



                    # ###INSTRUCTION

                    # - Act as an expert insurance adjuster analyzing claim notes for potential subrogation.

                    # - For each TOPIC, compile a single, concise list of all identified potential subrogation indicators based on the provided QUESTIONS and CLAIM NOTES.

                    # - If a relevant red flag for a specific question is found in the CLAIM NOTES, include that specific red flag in the list.

                    # - **Crucially, do not include the original question in the output.** Instead, directly state the identified subrogation indicator.

                    # - If no information or red flag is found for any of the questions within a TOPIC based on the CLAIM NOTES, explicitly state "No indicators found in claim notes." for that entire TOPIC.

                    # - Do not include questions that do not have relevant information or red flags.

                    # - Do not create multiple sections within the output for a single TOPIC (e.g., no separate "Analysis," "Potential Subrogation Indicators," and "Final Summary" sections). Provide only one consolidated list per TOPIC.



                    # ###RESTRICTIONS

                    # - Do not use any generic information or information outside the provided claim notes.

                    # - Avoid suggestions, recommendations, or mitigation methods.

                    # - Avoid drawing conclusions, making interpretations, or providing opinions on the likelihood of subrogation.

                    # - Do not change or manipulate any fact or information from the claim notes.

                    # - Do not use number-based formatting. Always use bullet points (•) instead.

                    # - Do not create paragraphs; only use bullet points separated by new lines.

                    # - The output for each TOPIC should begin directly with "Topic: [TOPIC NAME]" followed by the consolidated list of indicators or the "No indicators found" statement.

                    #     **Input:**

                    #     ###TOPICS & QUESTIONS : 
                    # topic_que = {{

                    # 'Accident and Fault Determination' : [

                    #         'What were the exact circumstances of the accident?',

                    #         'Who are the parties involved in the accident?',

                    #         'Is a third-party other than the insured involved in accident?',

                    #         'Who is identified as at fault in the accident?'],

                    # 'Injury at Scene' :[

                    #         'Is the injury reported on scene?',

                    #         'Is there any medical treatment received?',

                    #         'Is there an ambulance on scene?'],

                    # 'Vehicle Damage' : [

                    #         'What are the total damages and expenses incurred?',

                    #         "What is the location of the damage on the insured vehicle?",

                    #         'Is the insured vehicle totaled in the accident?',

                    #         'Was the insured vehicle rear-ended?'],

                    # 'Evidences and Witnesses' :[

                    #         'Is there a police report available and what does it say about the accident and fault?',

                    #         'What evidence is available (photos, videos, physical evidence) for the accident?',

                    #         'Are there any witness statements about the accident included in the claim notes?'],

                    # 'Insurance Coverage (Third Party)' :[

                    #         'Is the third party identified at fault?',

                    #         "What are the details of the third party's insurance coverage?",

                    #         "Are the policy limits for third party's insurance sufficient to cover the damages?",

                    #         'Is the third party uninsured ?'],

                    # "Jurisdiction" :[

                    #         "What are the subrogation laws in the state where the accident occurred?",

                    #         "Does the accident state follow no-fault insurance rules and how do these rules impact the ability to pursue subrogation?",

                    #         'Does the accident state adhere to comparative or contributory negligence principles and how does this affect fault determination?'],

                    # "Paid Loss": [

                    #   'Has any payment for losses been made by Hanover towards the claim ?'],

                    # "Subrogation Chances" : [

                    #   'Is the cause of loss eligible for subrogation?',

                    #   'Examine the subrogation chances considering your previous responses for topic Jurisdiction, Accident, Fault Determination, Vehicle Damage and Insurance Coverage (Third Party)?']

                    # }}



                    # Here are the context for the subrogation laws and claim notes:


                    # ###CLAIM_NOTES :

                    
                    # \n\n{claim_notes}"""


                    prompt =f"""Can you summarize the provided claim notes for the following topics 
                    'Jurisdiction','Accident and Fault Determination','Vehicle Damage','Injury at Scene','Evidences and Witnesses','Insurance Coverage (Third Party)','Paid Loss','Subrogation Chances'

                     # ###CLAIM_NOTES :

                    
                    # \n\n{claim_notes}

                    
                    """



                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    summary = response.text if hasattr(response, "text") else "Unable to generate summary."
                    st.markdown("### 📝 Summary of Claim Notes")
                    st.success(summary)
                except Exception as e:
                    st.error(f"Error generating summary: {e}")
        else:
            st.warning("No claim notes available to summarize.")

    # --------- Q&A Chatbot Section ----------
    st.markdown("### 💬 Ask Questions About This Claim")
    user_question = st.text_input("Type your question here:")
    if user_question.strip():
        with st.spinner("Generating answer..."):
            try:
                qa_prompt = f"""
                You are an insurance claims assistant.
                Use the following claim notes to answer the question.
                Claim Notes:
                {claim_notes}

                Question: {user_question}
                Answer based only on the claim notes.
                """
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=qa_prompt
                )
                answer = response.text if hasattr(response, "text") else "No answer generated."
                st.markdown("**Answer:**")
                st.info(answer)
            except Exception as e:
                st.error(f"Error generating answer: {e}")
