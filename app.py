import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_adult.csv")
    return df

df = load_data()

st.title("Income Inequality Dashboard")

st.subheader("Overall Income Distribution")

income_counts = filtered_df["income"].value_counts()

fig, ax = plt.subplots()
ax.pie(income_counts, labels=income_counts.index, autopct="%1.1f%%", startangle=90)
ax.set_title("Overall Income Distribution")

st.pyplot(fig)

st.subheader("Key Metrics")

total = len(df)
high_income = len(df[df["income"] == ">50K"])
percentage = (high_income / total) * 100

gender_total = df.groupby("sex")["income"].count()
gender_high_income = df[df["income"] == ">50K"].groupby("sex")["income"].count()
gender_percent = (gender_high_income / gender_total) * 100
gap = abs(gender_percent.get("Male",0) - gender_percent.get("Female",0))

col1, col2, col3 = st.columns(3)
col1.metric("Total Records", total)
col2.metric("% Earning >50K", f"{percentage:.2f}%")
col3.metric("Gender Wage Gap", f"{gap:.2f}%")

st.sidebar.header("Filters")
gender_filter = st.sidebar.multiselect(
    "Select Gender",
    options=df["sex"].unique(),
    default=df["sex"].unique()
)
race_filter = st.sidebar.multiselect(
    "Select Race",
    options=df["race"].unique(),
    default=df["race"].unique()
)

filtered_df = df[
    (df["sex"].isin(gender_filter)) &
    (df["race"].isin(race_filter))
]

st.subheader("Income Distribution by Race")
race_income = pd.crosstab(filtered_df["race"], filtered_df["income"])
race_income_pct = race_income.div(race_income.sum(axis=1), axis=0)

for race in race_income_pct.index:
    fig, ax = plt.subplots()
    ax.pie(race_income_pct.loc[race], labels=race_income_pct.columns, autopct="%1.1f%%", startangle=90)
    ax.set_title(f"{race}")
    st.pyplot(fig)

st.subheader("Gender vs Income")
gender_income = pd.crosstab(filtered_df["sex"], filtered_df["income"])
st.bar_chart(gender_income)

st.subheader("Income Trend by Age Group")
filtered_df = filtered_df.copy()
filtered_df["age_group"] = pd.cut(
    filtered_df["age"],
    bins=[20,30,40,50,60,70,90],
    labels=["20-30","30-40","40-50","50-60","60-70","70+"]
)
age_trend = filtered_df.groupby("age_group")["income"].apply(lambda x: (x==">50K").mean())
st.line_chart(age_trend)

st.subheader("Summary Table (Gender & Race)")
summary_table = filtered_df.groupby(["sex","race"]).agg(
    total_count=("income","count"),
    high_income=("income", lambda x: (x==">50K").sum())
)
summary_table["% >50K"] = (summary_table["high_income"]/summary_table["total_count"])*100
st.dataframe(summary_table.reset_index())

st.subheader("Raw Data Preview")
st.dataframe(filtered_df.head(20))