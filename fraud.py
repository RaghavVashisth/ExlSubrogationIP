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
    # claim_notes = df[df["Claim_Number"] == selected_claim]["Claim_Notes"].values[0] if "Claim_Notes" in df.columns else ""
    claim_notes = """For claim number CLM-57398bv: From: SPRY, JANE L.   Sent: Thursday, February 3, 2022 10:22 AM  To: KRUEGER, PAULA J. <PKRUEGER@HANOVER.COM>  Subject: FW: CLM-57398bv        Hi Paula,         I have reviewed your claim and policy.     I have added vehicle 001 the 2013 Subaru Outback that was on the policy at the time of loss. You can proceed with your exposures.    Please note that this vehicle was removed from the policy effective 10/15/20.    At this time I have added UM Coverage.  If you need more coverages added please let me know.    Let me know if you need further assistance on this issue.    Thank you,  Janey    Janey Spry  Claims  Technology Group  251 Salina Meadows Pkwy  Suite 260  N Syracuse NY 13212  Phone 800-628-0250 Ext 4806  Fax 508-635-5944            From: KRUEGER, PAULA J. <PKRUEGER@HANOVER.COM>   Sent: Wednesday, February 2, 2022 1:20 PM  To: ClaimsTechSupport <HCSSUPPORT@hanover.com>  Subject: CLM-57398bv    Please add the 2013 SUBARU OUTBACK VIN: 4S4BRCLC4D3288630  for UM coverage.    Thank you.    Paula, From: KRUEGER, PAULA J.   Sent: Wednesday, February 2, 2022 10:20 AM  To: 'claimstechsupport@hanover.com' <claimstechsupport@hanover.com>  Subject: CLM-57398bv    Please add the 2013 SUBARU OUTBACK VIN: 4S4BRCLC4D3288630  for UM coverage.    Thank you.    Paula, attny is seeking UIM coverage, Recvd dec pg from tort carrier Geico verifying limits of $30K - Mehfooz Alam and Meherun Akter are both listed policyholders, If negotiations require it, consider obtaining the following:  • Virginia Pediatric Group, Dr. David R. Rubio: Post-hospital physician records up through 11/5/2020  • Virginia Spine & Sports Orthopedics, Dr. Angela Santini: post-hospital records through 11/5/2020.  • Including CN in future roundtables with medical focus and consider re-referral back to CN for further review., UIM Demand in file. demand is for $250,000  t.f. liab limits $30K    no med pay coverage, Recvd demand from insd attny, meds total $17,078.51, demand is for policy limits of $250K.  No time date.      The minor 11 YO IVP was transported from the scene to INOVA Loudoun Hospital ER, CT scans revealed insd suffered fractures to T6 & T7 and the insd was ordered to stay at the hospital overnight.  On 8/27/21 insd's pediatrician ordered ortho and PT.  Insd was give n a back brace in which he had to wear for 6 months.  Insd was in in tx through November 2021     Sent addtl evidence ltr to attny as we are still in need of the following:  RS of IVD, Pol Rpt, Geico Dec Pg, Tender Ltr,   ***I will also need to verify no addtl ins on tort or veh     I received a call from Geico, they do not have a copy of the police report for any addtl info I need to contact the adj Mr. Dakota Cheape @ 757-301-3144, dialed same & left vm for cb., Recvd signed release and request to issue pymt in amt of $100K, Under form 231-2322 0606 Personal Umbrella Liability Supplement, umbrella coverage is excluded under   7.  Any Claim for No-Fault, Uninsured Motorists, or Underinsured Motorists coverage, Requested Accurint as follows:     Carrier Discovery via tort driver/owner:  Meherun Akter  Carrier Discovery via tort vehicle:  2016 Toyota Corolla Vin 2T1BURHE6GC627772  Titled Owner tort vehicle & tags:  2016 Toyota Corolla Vin 2T1BURHE6GC627772, no license plate, I would assume the tags are VA   Assets check via tort driver name: Meherun Akter  Carrier Discovery via Injured Insured:  Meherun Akter   Carrier Discovery via Injured Insured:  RICARDO ARAUJO, Comprehensive Report/Carrier Discovery/MVR complete - uploaded in file docs., Email to attny:      Can you verify the relationship between our named insureds Richard Araujo and Alessandra Riavasi and the injured party Eduardo Ravasi Franca De Araujo?  Also please verify where Eduardo Ravasi Franca De Araujo resides., there is no medical payments coverage on this policy, Recvd pol rpt     Unit 1 Meherun Akter   Unit 2 Ricardo Franca DeAraujo     Tortfeasor Meherun Akter was traveling on Belmont Ridge Rd, intending to make a left turn onto Hay Rd, she had a green (yield) light.  IVD Ricardo Franca DeAraujo advised he was traveling SB on Belmont Ridge Rd towards the intersection of Hay Rd, he has a green light.  There was a vehicle traveling in front of him that cleared the intersection.  Tort vehicle attempted to make a left turn in between that vehicle and IV but struck the IV on the  d/s front.  Police report minor injuries.  Tortfeasor admits to not seeing IV.  Per Insd written stmt he denies be able to avid this loss.      POI tort vehicle:  P/s front   POI IV:  d/s front, Geico clm # 8688156640000001    insd's loss vehicle:  Vehicle Info: 2013 SUBARU OUTBACK          VIN: 4S4BRCLC4D3288630     Disposition: Totaled          Date of Salvage: 08/21/2020          Actual Cash Value: 12,486     Passenger           Name: RAVASI FRANCA DE ARAUJO,EDUARDO            Address: 43036 BROOKTON WAY           ASHBURN, VA 20147          DOB: XX/XX/2008          Gender: Male          Injury/Damage: BRUISES, FRACTURED SPINE          Coverage/Loss: Bodily Injury    Guardian Name: DEARAUJO,RICARDO,FRANCA                Address: 43036 BROOKTON WAY               ASHBURN, VA 20147              DOB: XX/XX/1976              Gender: Male, Completed eval and long form, email to um for auth, This letter will serve to confirm that I represent Eduardo Ravasi Franca De Araujo, a   minor, as to his bodily injuries sustained in a motor vehicle accident on August 18, 2020. His   father, Ricardo Araujo is the policy holder with your insurance. Eduardo was injured in a motor   vehicle accident caused by another driver who was insured by Geico. At the time of the   accident, Eduardo was in the vehicle with his father driving. Please communicate directly with   my office regarding this matter., From: KRUEGER, PAULA J.   Sent: Wednesday, February 2, 2022 10:03 AM  To: Soroush Dastan <attorney@ashburn-law-office.com>; FIRSTREPORT <FIRSTREPORT@hanover.com>  Subject: RE: Claim Number: CLM-57398bv    Dear Soroush Dastan,    Thank you for your email.  Can you provide a copy of the crash report so that we can complete the set up of this claim and start our investigation of coverage and liability?    Also, there is no medical payments coverage on this policy.  This claim will be reassigned to an adjuster who handles the investigation of the UM/UIM coverages. Once assigned that adjuster will reach out to you.    Sincerely,   . . ., Reviewed Accurint DOL 8/18/2020    Titled Owner tort vehicle & tags: 2016 Toyota Corolla Vin 2T1BURHE6GC627772, registered to Geico      Carrier Discovery via tort driver/owner: Meherun Akter shows Geico policy #4631290287, term dates are 2/22/22 - 8/22/22, inception is 6/15/20.  Lists tort & veh.  No other active policies at TOL     Carrier Discovery via tort vehicle: 2016 Toyota Corolla Vin 2T1BURHE6GC627772 Geico policy #4631290287, term dates are 2/22/22 - 8/22/22, inception is 6/15/20.  Lists tort & veh.  No other active policies at TOL    Carrier Discovery via Injured Insured: RICARDO ARAUJO shows AFB policy, no other active polices at TOL     Assets check via tort driver name: Meherun Akter resides at 43138 Chestwood Acres Terrace Apt 203 Broadlands, VA 20148, liens & judgements, no bankruptcies.  Owns 2013 Honda CRV.  No criminal record.  Tort does not appear to be collectable, FNOL from ATTY  Soroush Dastan will be sending LOR to firstreport@hanover.com    No details except for names/address of INSD. He believes the vehicle was totaled. OV had Geico and they have accepted liability., Reason for Referral:   Please review the medical records to determine if injuries are related to MVA of 8/18/2020.  CT scan results which indicate possible fracture and height loss of 20%, but there is an indication these may not be acute, or trauma related.        Check or list the records below if in the file:  X Ambulance  X ER   Prior Records  X PCP/PMD  X Specialists  X Imaging Reports   Other care and treatment records (i.e. PT, chiro, pain mgmt.)    What relevant records are missing, if any?  Priors   Any other non-medical records that should be reviewed? If so, please list.  Please describe the alleged mechanism of injury if relevant to your referral?  What are the alleged injuries and diagnoses?  Thoracic compression fracture at T6 and T7, Abrasion of left front wall of thorax, contusion of abdomen wall, pain in right shoulder, contact with viral communicable diseases, vomiting, abdominal trauma  Is there a history of similar symptoms or injuries or problems (yes/no)?  It is noted in the records that the insured plays multiple contact sports and is very active   Do you have a deadline by which you need the CN report?  ASAP response due 2 weeks.  Demand has not been submitted to Med Connects as it did not qualify (small demand under 200 pgs), The injured insured classifies as an insured under this policy     Minor Eduardo Ravasi Franca DeAraujo resides at home with our named insureds  Richard Araujo and Alessandra Riavasi, he is their 12 YO son.  He is not listed on the policy as he does not driver but is considered a insured as he is a family member    C. "Insured" as used in this endorsement means:  1. Your or any "family member"., Reviewed BIE Long Form and medial timeline.      Settlement authority to $100,000., Policy Information: Coverage is provided under personal auto policy A2R- A745272-05 issued by Allmerica Financial Benefit Insurance to Named Insured Richard Araujo and Alessandra Riavasi, the injured party is the NI's son, Eduardo Ravasi Franca De Araujo, he is a 12 YO minor who lives with the NI. The policy period ran from 10/15/2019 to 10/15/2020 and was in effect on the 8/18/20 loss. Ricardo Araujo is the NI and a scheduled driver on the policy, listed driver #1.  The UM/UIM Limits are $250K per person and $300K per occurrence.  There is $1 million umbrella listed under h/o policy #HNR A745273 however it is excluded form coverage.      Insuring Agreement: UIM Coverage is specifically provided under Endorsement PP1403-0105 UNINSURED MOTORIST COVERAGE - VIRGINIA    Insuring Agreement  A. We will pay, in accordance with VA. Code Ann. Section 38.2-2206, damages which an "insured" or an "insured's legal representative is legally entitled to recover from the owner or operator of an "uninsured motor vehicle" or an "underinsured motor vehicle" because of:  1. "Bodily injury" sustained by an "insured" and caused by an accident; and  2. "Property Damage" caused by an accident.  The owner's or operator's liability for these damages must arise out of the ownership, maintenance, or use of the "uninsured motor vehicle" or "underinsured motor vehicle". We will pay damages under this coverage caused by an accident with an "underinsured motor vehicle" only after the limits of liability under any applicable bodily injury liability or property damage liability bonds or policies have been exhausted by payment of judgments or settlements.    C. "Insured" as used in this endorsement means:  1. Your or any "family member".  2. Any other person "occupying" or using "your covered auto".  3. Any person for damages that person is entitled to recover because of "bodily injury" to which this coverage applies sustained by a person described in 1. or 2. above.    D. "Underinsured motor vehicle" means a land motor vehicle or trailer of any type for which the sum of:  1. The limits of liability under all liability bonds or policies; or  2. All deposits of money or securities made to comply with the Virginia Financial Responsibility Law;  that is "available for payment" is less than the sum of the limits of liability applicable to the "insured" for the Uninsured Motorist Coverage under this policy or any other policy.  "Available for Payment" as used in this Paragraph (D) means the amount of liability coverage applicable to the claim of the "insured" as reduced by the payment of any other claims arising out of the same occurrence.    Eduardo Ravasi Franca De Araujo meets the definition of "insured". He is the son the named insureds and resides in the household.  NI and listed driver #1 Richard Araujo was the driver of the IV.  He was operating a "covered auto", listed vehicle #1 2013 Subaru Outback Vin 4S4BRCLCSD3288630.      Tortfeasor is Meherun Akter; she is the owner/operating of the tort vehicle insured through Geico under policy #6025-69-65-99.  Clm # 8688156640000001 has been set up and their limits are $30K.  Geico has tendered their limits.  We have a copy of their dec pg in docs nav as well as offer letter.  Ran ISO and there were no addtl matching claims. Ran Accurint and carrier discovery and there is no addtl insurance found for the tortfeasor. Also, tort does not appear collectable.        Exclusions: There are no exclusions contained in the UM endorsement that have an impact on this loss.    Limits of Liability:  The relevant provisions contained in the Limits of Liability include:    Limit of Liability  A. The limit of Bodily Injury Liability shown in the Declarations for each person for Uninsured Motorist Coverage is our maximum limit of liability for all damages, including damages for care, loss of services or death, arising out of "bodily injury" sustained by any one person in any one accident. Subject to this limit for each person, the limit of Bodily Injury Liability shown in the Declarations for each accident for Uninsured Motorist Coverage is our maximum limit of liability for all damages for "bodily injury" resulting from any one accident.  This is the most we will pay regardless of the number of:  1. "Insured";  2. Claims made, or  3. Vehicles or premiums shown in the Declarations.  B. Any damages payable under this coverage:  1. Shall be reduced by all sums paid because of "bodily injury" or "property damage" by or on behalf of persons or organizations who may be legally responsible.    Accordingly, the UIM limits are reduced to $220K after the tort tenders.     Other Insurance: There are no other policies known to provide UIM coverage. A Carrier Discovery search reflects only Allmerica Financial policy.     Conditions: There are no conditions at this time that impact coverage., I ordered a copy of the police report through Metro, conf #10514482, In receipt of new claim reported on 2/1/22 via insd attny Soroush Dastan, Esq. Attorney at Law.  She represents minor IVP minor Eduardo Ravasi Franca De Araujo, he was a passenger in the vehicle being driven by our NI Richard Araujo, he is operating listed vehicle #1 which has now been removed due to this loss.      The tortfeasor is insd through Geico, clm #8688156640000001 has been set up under policy #6025696599, they have accepted 100% liability.  We do not yet have torts info     LOSS LOCA:  Ashburn, VA; Louden County (Liberal per US Law)      LOSS DETAILS:  Unk at this time     INVESTIGATION:  Called attny @ 703-986-3337, spoke to Soroush Dastan, advised we need police report, Geico Dec Pg, Tender Ltr, Stmt from our IVD Ricardo, attny will work on getting me required docs.  He advises the tortfeasor is Ms. Meherun Akter, her DOB is 1/1****, she was charged with failure to yield on left turn.  Attny does not have copy of police report but will try & obtain, also advised I need Yr Make Model & Vin of tort veh.        Called Geico @ 757-689-5648, left vm for Kamala Mulholland to cb refd clm #8688156640000001.    Ran ISO and found Geico clm, updated tort driver contacts and tort vehicle info      Mehfooz Alam is the policyholder and Meherun Akter is the driver   Both reside at:  43138 CHESTWOOD ACRES TER, APT 203 in BROADLANDS, VA 20148    RESERVE:  Opened at $50K as we investigate     POA:   IVD RS   Geico Dec Pg   Asset Searches - Discovery Searches - Accurint  Final Coverage Note, Received and reviewed new claim      Type of Claim/Exposure: Pending UM/IM for Exposures #1 minor Eduardo Ravasi Franca De Araujo  Location of loss:  Ashburn, VA Louden County (Liberal per US Law)   Policy Type:  Personal Auto Policy   Endorsements: PP00010105 Personal Auto Policy, PP1403-0105 UNINSURED MOTORIST COVERAGE - VIRGINIA, 23122061015 AMENDMENT OF POLICY PROVISIONS  Policy Number/Mod: A2R- A745272-05  Effective Dates: 10/15/2019 to 10/15/2020   DOL:  8/18/20, within policy period   SOL for UM/UIM:  2 Years, 8/18/22  Underwriting Company: Allmerica Financial Benefit Insurance       Negligence Laws VA:  Contributory    NI: Richard Araujo and Alessandra Riavasi   IV:  listed vehicle2013 Subaru Outback  IVD:  Richard Araujo  IVP:  minor Eduardo Ravasi Franca De Araujo   Coverage Limits: UM/UIM $250K per person $500K per occurrence, no MP    Exclusions/Conditions:   Umbrella Policy: $1 million listed under h/o policy #HNR A745273    VIRGINIA    Endorsement PP1403-0105 Uninsured Motorist Coverage - Virginia    Insuring Agreement  A. We will pay, in accordance with VA. Code Ann. Section 38.2-2206, damages which an "insured" or an "insured's legal representative is legally entitled to recover from the owner or operator of an "uninsured motor vehicle" or an "underinsured motor vehicle" because of:  1. "Bodily injury" sustained by an "insured" and caused by an accident; and  2. "Property Damage" caused by an accident.   The owner's or operator's liability for these damages must arise out of the ownership, maintenance, or use of the "uninsured motor vehicle" or "underinsured motor vehicle". We will pay damages under this coverage caused by an accident with an "underinsured motor vehicle" only after the limits of liability under any applicable bodily injury liability or property damage liability bonds or policies have been exhausted by payment of judgments or settlements.   C. "Insured" as used in this endorsement means:   1. Your or any "family member".   2. Any other person "occupying" or using "your covered auto".   3. Any person for damages that person is entitled to recover because of "bodily injury" to which this coverage applies sustained by a person described in 1. or 2. above.  D. "Underinsured motor vehicle" means a land motor vehicle or trailer of any type for which the sum of:   1. The limits of liability under all liability bonds or policies; or  2. All deposits of money or securities made to comply with the Virginia Financial Responsibility Law;  that is "available for payment" is less than the sum of the limits of liability applicable to the "insured" for the Uninsured Motorist Coverage under this policy or any other policy.   "Available for Payment" as used in this Paragraph (D) means the amount of liability coverage applicable to the claim of the "insured" as reduced by the payment of any other claims arising out of the same occurrence.     Limit of Liability   A. The limit of Bodily Injury Liability shown in the Declarations for each person for Uninsured Motorist Coverage is our maximum limit of liability for all damages, including damages for care, loss of services or death, arising out of "bodily injury" sustained by any one person in any one accident. Subject to this limit for each person, the limit of Bodily Injury Liability shown in the Declarations for each accident for Uninsured Motorist Coverage is our maximum limit of liability for all damages for "bodily injury" resulting from any one accident.   This is the most we will pay regardless of the number of:   1. "Insured";  2. Claims made, or  3. Vehicles or premiums shown in the Declarations.   B. Any damages payable under this coverage:  1. Shall be reduced by all sums paid because of "bodily injury" or "property damage" by or on behalf of persons or organizations who may be legally responsible. For claim number 85-00022106: setting 1500 res, appears clmnt treated, AWNI SAFADI : 0 MATTHEW SAFADI : 100 Liability Rationale : MI 50/50  Proximate Cause:  IV made u turn into wrong lane into path of OV. OV tried to swerve but could not and OV hit IV  Duties Owed: to yield the right of way  Duties Breached: failure to yield the right of way, found ins phone # from previous claim    called ins @ # 313-400-5490  matthew safadi  lm on vm requesting call back, PLATINUM AUTO ESSENTIAL - MI y no oem  FULL GLASS COVERAGE - MI    2007 jeep cher brd 1000 rr 30/900  MOD  03  Type  Personal Auto  Effective Date  03/17/2021  Expiration Date  03/17/2022  Cancellation Date  Legal Cancellation Date  Original Effective Date  03/17/2018  Status  In force  driver 3  3x3, sent msp letter, sent SOD to clmnt, Reviewed for potential PIP exposure for insd driver Matthew. Listed as driver 3 on policy.    ***PIP OPT OUT ON THIS POLICY***    Called Matthew to advise. Also sent Opt-out letter. He did not seek any medical tx. He does not work, he is in school and did miss school bc of mva. No WL potential.    No further action from PIP., vm from clmnt    called same @ # 586-359-9419    spoke with abigail    I took a recorded statement from abigail darmetko DOV.  I confirmed DOL, loss occured at 10:30 am.  The loss occurred on squirrel road, OV was going south on squirrel road, OV was in the right lane.  no traffic control.  Speed limit is unknown.  It was a 2 vehicle loss, IV was a some sort of jeep, driven by a male with no passengers in either vehicle.  FOL:  OV was going south on squirrel road.  IV was in turnaround to go same direction as OV, IV came in front of OV, OV couldn't stop, OV hit IV rear end, and then OV lost control and ended up in middle part of the road and hit a tree.  OV struck IV on the rear end.  IV went in the turnaboubt into the right hand lane. OV tried to swerve, hit sidewalk which pushed her back into the road.  police were notified, it was the auburn hills police, no tickets or citations to OV, DIV received a ticket.  clmnt was checked out by ambulance, she had a laceration on her forehead, hit her head pretty hard on steering wheel, and chemical burn on her wrist and ended up with 2 black eyes.  no follow up treatment..  she had xray of thumb at ER which was unremarkable.      DOV provided credible account, called clmnt @ # 586-359-9419  vm not set up  yet, vm from clmnt father    called same @ # 313-550-6684    spoke with brian  advised we need to get DOV r.s  clmnt vehicle was totaled, he is looking to pursue mini tort claim  clmnt went to hospital, ex wife drove her, laceration on forehead and chemical burn on wrist from airbag.  no additional treatment sought at all    bdarmetko77@gmail.com    emailed him directions on what we need for MT, LOSS DESCRIPTION: IV failed to yield causing OV to collide into IV and OV hit a tree      KEY PARTIES: Matthew Safadi DIV, Abigail Darmetko DOV injured party    COVERAGE:    Effective dates:  3/17/21-3/17/2022  Mod# 3  Policy in force: Y   Policy Type:  MI PAP  Neg Law: MI 50/50  Endorsements: none  Excess/Other Applicable Coverage:  none  Vehicle:  1 2007 jeep grand cherokee  Coverage:  250/500  Driver: matthew safadi unlised  Excluded drivers: none  Prior losses:  yes not related  How many vehicles/how many drivers: 3v 3d  Policy State MI  Loss Location: MI  Coverage Analysis; No Coverage Issues       LIABILITY ANALYSIS: pending    SCOPE OF DAMAGES: OV is totaled, possibly significant inj    LITIGATION: no    RESOLUTION STRATEGY: DIV r.s, p.r DOV r.s, finalize liab, ISO, MSP, MI note, Pro se, ISO on clmnt  found matching claim with State auto  PIP showing as closed, chemical burns on wrist from airbag and forearm abrasion    AU0000000660193  Dawn Carr OC  614-917-4920  straight to vm  lm on vm requesting call back, ISO on other clmnt  MSP tier 1 complete    no priors, no open PIP showing in ISO hit, called clmnt @ # 586-359-9419  went to vm  vm not set up yet, received p.r from lexis nexis    IV hazardous action for failure to yield    FOL:  OV was going south on N squirrel rd just north of cross creek parkway.  IV was going north on north squirrel road and made a u turn onto southbound N squirrel rd.  IV failed to yield and pulled in front of OV causing collision.  OV went off road and struck tree.      both drivers complained of injuries but refused transport  DIV Cited    it is worth  noting, the diagram shows the insured had completed u turn and was rear ended before clmnt lost control and hit tree.  need photos to confirm, called ins @ # 313-400-5490    spoke with matthew  DIV was injured, neck and his head was hurting, still hurting right now, low back  confirmed vehicle  damage to IV:  the bumper and the tailgate door, trunk.    vehicle is drivable    I took a recorded statement from Matthew Safadi DIV.  I confirmed DOL, loss occurred around 11am, unknown street possibly squirrel but it's near oakland university.  2 lanes each way.  Speed limit is 40 mph.  Stop sign where IV was.  it was a 2 vehicle loss, OV was a buick blue in color, female driver with no passengers.  FOL:  IV was coming out of the  university, going onto the road.  He went onto the road and was making a u turn.  He stopped at the stop sign, looked both ways, he had enough time to go, he continued his turn after he stopped, the woman who hit IV had not slowed down at all, and she impacted IV from the rear.  She then drove to the left of IV, continued for a quarter mile, drove onto the grass and crashed into a tree.  IV had completed his u turn, and was driving for about a minute, then he was impacted in the rear.  OV rear ended IV.  POI OV:  from the middle of the vehicle all the way to the right.  DOV airbags went off after she hit tree and there was blood on her head.  DIV neck and low back were injured.  police were notified, it was the auburn hills police.  DIV was issued a ticket for failing to yield.  however the insured disputes this as he had completely stopped and the driver that hit him was distracted as she should've slowed down.      DIV provided credible account, called clmnt @ # 586-359-9419  vm not set up yet, Accurint search for the SSN for Abigail Darmetko.  There were no records found with the clmt address and DOB given., lm   poa brd 1000 applies rr 30/900, need shop, THE OV IS TOTALED. Police Report:XXX-XX-XXXXf per loss date too old. SEARCH SUCCESSFUL - POLICY:D519918 - UNIT COUNT:3 Policy Prefix: A6B Policy: D519918 Policy Type: Auto Loss Date: 10/18/2021 Unable to confirm email Tow: N/C Rental: N/C Coll Ded: N/C Comp Ded: 100, ordered p.r from lexis nexis For claim number 85-00134646: Personal Auto Policy    Loss State:  TN  Confirm Policy is active for the date of loss:  yes  Confirm Driver:   n/a parked  Confirm Vehicle:   001 CHEV SLVRDO 2002  #2GCEC19XXX-XX-XXXXlimit:    100,000  Rental:   NONE ON POLICY    Endorsements:    PLATINUM AUTO ESSENTIAL    Red flags ruled out?:   no collision but possible UMPD, IBC from the insured...  Confirm email:  does not have email  Confirm DOL:   3/28/22  Confirm IV:    CHEVY SILVERADO  Confirm driver:  n/a parked  Confirm passengers:  n/a  Injuries:  n/a  FOL:  IV WAS PARKED AND UNOCCUPIED IN WALMART PARKING LOT WHEN INSURED GOT HOME THEY FOUND DAMAGE.      Damage to the IV:   SCRATCH ON THE BED FROM CAB TO THE TAIL (P/S) - MIRROR BROKEN    Police/TP info: none  POI:   p/s from cab to end of bed (scratched and creased) and mirror is broken  MOI/Appraisal/SOC: Desk  Nelson's Auto Body  Gallatin, TN  Deductible:  $200, insured is aware payable to the shop  Rental:  will let me know  DTP:   to the SHOP  Drivable/non-Drivable:  yes, AUTHORITIES WERE CONTACTED BUT THEY DID NOT COME OUT OR DO A REPORT FIRST IMPACT UNKNOWN DEFAULTED Vehicle Location: George Gudenius 170 Albright Ln  Gallatin, TN 37066 Escalation Off per loss date too old. SEARCH SUCCESSFUL - POLICY:D443543 - UNIT COUNT:2 Policy Prefix: A15  Policy: D443543 Policy Type: Auto Loss Date: 3/28/2022 Email is not the preferred method of communication Tow: N/C Rental: N/C Coll Ded: N/C Comp Ded: 500, File alerted from the Model due to George Gudenius vehicle 2GCEC19XXX-XX-XXXXeorge Gudenius was involved in a claim 55 days prior to current claim, 35 day reporting delay as well as this was a hit while parked loss    ***Background:   Policy effective:  12/05/17  Policy type: Personal auto *PLATINUM   Dol: 03/28/22  Reported: 05/02/22   Priors:  1, no SIU involvement   -03/28/22, auto, PD HWP *THIS LOSS   -06/07/18, auto, PD, IVD hit parked OV    --PUUC notes reviewed, no concerning memos located   --Billing reviewed; no non-payments located     ***Insured: George Gudenius, address: 170 Albright Ln, Gallatin, TN 37066  --Insured: Sharon Gudenius, address: 170 Albright Ln, Gallatin, TN 37066    ** Accurint   -Accurint ran on named insured;  George Gudenius; no bankruptcies located, liens or judgements located from 2011 and no criminal records located    -Accurint ran on named insured; Sharon Gudenius ;located a  bankruptcy from 2009, no liens or judgements located, and no criminal records located     **ISO   -Ran ISO on George Gudenius; using name, address, and SS#. No questionable claims located  -03/28/22, auto, PD HWP *THIS LOSS   -02/01/22, auto, PD  carrier: Hanover   -10/01/21, auto road service carrier: Hanover   -06/07/18, auto, PD, IVD hit parked OV carrier: NGM Insurance     -Ran ISO on Sharon Gudenius; using name, address, and SS#. No questionable claims located   -06/07/18, auto, PD, IVD hit parked OV carrier: NGM Insurance     -VIN check in ISO, vin# 2GCEC19V221224301, no questionable claims located   -03/28/22, auto, PD HWP *THIS LOSS   -02/01/22, auto, PD  carrier: Hanover   -10/01/21, auto road service carrier: Hanover   -06/07/18, auto, PD, IVD hit parked OV carrier: NGM Insurance     **Summary:  -Insured reports HWP  -2 veh vs 2 drivers  -Insured will obtain the appraisal     ***Recommendations:   SIU has completed a review of this file, and at this time there appears to be no need for further SIU involvement and SIU recommends the adjuster continue to handle the claim based on its own merits. SIU recommends the adjuster confirm the damages are consistent with a hit while parked. Please contact this SIU Analyst should the damages not be consistent with a hit while parked    Ashley Bouchard, SIU ext 855-4618, Adj does not handle TN territory     Re-assigning to APD WEST, Estimate rcvd from agency....attached to file.  Need photos as well., Collision incident without collision coverage on 2002 Chev Slvrdo , relevel, Name: GEORGE GUDENIUS  Phone # called:   615-336-4541    left a vm for the insured to call back to discuss claim.      POA  statement  estimate  payment (minus $200 - UMPD)  rr needed?  will pay under UMPD For claim number 85-00168769: BI/Represented - Matthew Harris    LOSS DESCRIPTION: MI policy/MI loss. Insured made a left turn from the rightmost lane impacting clmt vehicle who was in the left lane traveling straight.     KEY PARTIES:  Insured driver: Sage Tischer. Clmt is Matthew Harris and is represented by Christopher Gatza.     COVERAGE: In order. Listed driver operating 2004 Jeep Liberty listed on the policy.   BI Coverage - $250k/$500k    Effective dates: 09/10/2021-09/10/2022  Mod# 03  Policy in force: Y  Policy Type: Personal Auto  Neg Law: 50/50  Endorsements: n/a  Excess/Other Applicable Coverage: None    LIABILITY ANALYSIS: Insured is 100% at fault for improperly turning from the rightmost lane.     SCOPE OF DAMAGES: Clmt is a 52-year-old male restrained driver. No air bag deployment. B type injury on policed report. None listed for hospital/ambulance. Disabling damages to OV. PR indicates clmt c/o hand pain and was treated on scene.     ISO: Several hits  Current DOL 6/7/22 - State Farm 2235B613J PIP claim, back sprain/strain soft tissue , soreness. Also UIM claim opened.   10/19/21 - MVA no injuries   05/05/21 Comp claim no injuries   07/06/2020 collision claim totaled no injuries   11/04/2018 collision claim no injuries   06/21/2018 - unrecovered theft       RESOLUTION STRATEGY: Acknowledgement MSP sent to attny. Obtain injury details from clmt attorney., Legal Document, OBC to Sage Tischer (ULD) @ 517-996-2583 - Unable to leave message, VM full.    OBC to CHRISTINE TISCHER @ 517-604-3397 - Unable to leave message, VM not set up., OBC to Sage Tischer (ULD) @ 517-996-2583 - Unable to leave message, VM full.    """

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


                    prompt ="""  Can you summarize the provided claim notes for the following topics 
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
