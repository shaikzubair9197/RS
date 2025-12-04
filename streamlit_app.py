import streamlit as st
import pandas as pd
import json
import re
import altair as alt


st.set_page_config(page_title="Insurance Email Dashboard", layout="wide")

# ---------------- HEADER ----------------
st.markdown("""
<h1 style="text-align:center;">Insurance Email Intelligence Dashboard</h1>
<p style="text-align:center; color:#6b7280;">
AI-powered classification & support intelligence from Gmail
</p>
<hr>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
try:
    with open("output.json", "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
except:
    st.error("No output.json found. Please run main.py first.")
    st.stop()

# ---------------- CLEAN NAME & EMAIL ----------------
def split_sender(sender):
    match = re.match(r"(.*)<(.+)>", sender)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return sender, ""

df[["Sender Name", "Sender Email"]] = df["from"].apply(
    lambda x: pd.Series(split_sender(x))
)

# ---------------- KPI CALCULATIONS ----------------
total_emails = len(df)
insurance_emails = int((df["detected_intent"] != "NOT_INSURANCE_EMAIL").sum())
non_insurance = int((df["detected_intent"] == "NOT_INSURANCE_EMAIL").sum())
total_escalated = int(df["escalated"].sum())
ai_used = int((df["ai_status"] == "AI_USED").sum())
fallback_used = int((df["ai_status"] == "FALLBACK_USED").sum())

# ---------------- MODERN KPI CARDS ----------------


st.markdown(f"""
<div style="display:flex; gap:20px; flex-wrap:wrap;">
  <div style="flex:1; background:#ffffff; padding:20px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08);">
    <div style="color:#6b7280;">Total Emails</div>
    <div style="font-size:28px; font-weight:700;">{total_emails}</div>
  </div>

  <div style="flex:1; background:#ffffff; padding:20px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08);">
    <div style="color:#6b7280;">Insurance Emails</div>
    <div style="font-size:28px; font-weight:700; color:#2563eb;">{insurance_emails}</div>
  </div>

  <div style="flex:1; background:#ffffff; padding:20px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08);">
    <div style="color:#6b7280;">Non-Insurance</div>
    <div style="font-size:28px; font-weight:700; color:#dc2626;">{non_insurance}</div>
  </div>

  <div style="flex:1; background:#ffffff; padding:20px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08);">
    <div style="color:#6b7280;">AI Used</div>
    <div style="font-size:28px; font-weight:700; color:#16a34a;">{ai_used}</div>
  </div>

  <div style="flex:1; background:#ffffff; padding:20px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08);">
    <div style="color:#6b7280;">Fallback Used</div>
    <div style="font-size:28px; font-weight:700; color:#f59e0b;">{fallback_used}</div>
  </div>

  <div style="flex:1; background:#ffffff; padding:20px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08);">
    <div style="color:#6b7280;">Escalated</div>
    <div style="font-size:28px; font-weight:700; color:#7c2d12;">{total_escalated}</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

# ---------------- MODERN INTENT CHART ----------------

st.subheader("Intent Distribution")

intent_counts = df["detected_intent"].value_counts().reset_index()
intent_counts.columns = ["Intent", "Count"]

chart = alt.Chart(intent_counts).mark_bar(
    cornerRadiusTopLeft=6,
    cornerRadiusTopRight=6
).encode(
    x=alt.X('Intent:N', sort='-y', title=""),
    y=alt.Y('Count:Q', title="Email Volume"),
    tooltip=['Intent', 'Count'],
    color=alt.Color(
        'Intent:N',
        legend=None,
        scale=alt.Scale(scheme='blues')
    )
).properties(
    height=380
)

st.altair_chart(chart, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ---------------- UNIQUE CLEAN SENDERS ----------------
st.subheader("Unique Email Senders")

unique_senders = df[["Sender Name", "Sender Email"]].drop_duplicates().reset_index(drop=True)
unique_senders.insert(0, "S.No", range(1, len(unique_senders) + 1))

st.dataframe(unique_senders, use_container_width=True, hide_index=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------- FILTERS ----------------
st.subheader("Filters")

c1, c2, c3 = st.columns(3)

with c1:
    intent_filter = st.multiselect(
        "Intent Type",
        options=df["detected_intent"].unique(),
        default=df["detected_intent"].unique()
    )

with c2:
    ai_filter = st.multiselect(
        "AI Status",
        options=df["ai_status"].unique(),
        default=df["ai_status"].unique()
    )

with c3:
    sender_filter = st.multiselect(
        "Sender",
        options=df["Sender Email"].unique(),
        default=df["Sender Email"].unique()
    )

filtered_df = df[
    (df["detected_intent"].isin(intent_filter)) &
    (df["ai_status"].isin(ai_filter)) &
    (df["Sender Email"].isin(sender_filter))
]

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------- MAIN TABLE ----------------
st.subheader("Processed Email Records")

st.dataframe(
    filtered_df[
        [
            "Sender Name",
            "Sender Email",
            "subject",
            "detected_intent",
            "ai_status",
            "repeat_count",
            "escalated",
            "first_seen",
            "last_seen"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------- ESCALATION PANEL ----------------
st.subheader("Escalated Cases")

escalated_df = df[df["escalated"] == True]

if escalated_df.empty:
    st.info("No escalated cases at the moment.")
else:
    st.dataframe(escalated_df, use_container_width=True, hide_index=True)

# ---------------- FOOTER ----------------
st.markdown("""
<p style="text-align:center; color:gray; margin-top:30px;">
Internal Support Intelligence System – Insurance Email Automation
</p>
""", unsafe_allow_html=True)
