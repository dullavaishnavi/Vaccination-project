import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px

st.set_page_config(page_title="Vaccination Analytics", page_icon="💉", layout="wide")

BASE = Path(__file__).parent
DATA = BASE / "data"
EXPORT = BASE / "exports"

@st.cache_data
def load_table(name):
    p = DATA / name
    if not p.exists():
        p = EXPORT / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

def pick_file(prefixes):
    for p in list(DATA.glob("*.csv")) + list(EXPORT.glob("*.csv")):
        if any(p.stem.lower().startswith(x) for x in prefixes):
            return p
    return None

coverage = load_table("coverage_clean.csv")
if coverage.empty: 
    p=pick_file(["coverage"])
    coverage=pd.read_csv(p) if p else pd.DataFrame()
incidence = load_table("incidence_rate_clean.csv")
cases = load_table("reported_cases_clean.csv")
introduction = load_table("vaccine_introduction_clean.csv")
schedule = load_table("vaccine_schedule_clean.csv")

st.title("💉 Global Vaccination Data Analysis")
st.caption("Public Health & Epidemiology • Python + SQL + Streamlit • Power BI-ready exports")

if coverage.empty and cases.empty:
    st.error("No cleaned data found. Run the Google Colab notebook and copy the generated CSV files into the repository's data/ folder.")
    st.stop()

# normalize common fields
for df in [coverage, incidence, cases]:
    if not df.empty:
        if "year" in df: df["year"] = pd.to_numeric(df["year"], errors="coerce")
        if "coverage" in df: df["coverage"] = pd.to_numeric(df["coverage"], errors="coerce")

with st.sidebar:
    st.header("Filters")
    if "year" in coverage.columns and coverage["year"].notna().any():
        yrs=sorted(coverage["year"].dropna().astype(int).unique())
        yr=st.slider("Year", min(yrs), max(yrs), (min(yrs),max(yrs)))
        coverage_f=coverage[coverage["year"].between(*yr)]
    else:
        coverage_f=coverage.copy()
    if "name" in coverage_f.columns:
        countries=sorted(coverage_f["name"].dropna().astype(str).unique())
        selected=st.multiselect("Country", countries)
        if selected: coverage_f=coverage_f[coverage_f["name"].isin(selected)]
    if "antigen" in coverage_f.columns:
        ants=sorted(coverage_f["antigen"].dropna().astype(str).unique())
        ant=st.multiselect("Antigen", ants)
        if ant: coverage_f=coverage_f[coverage_f["antigen"].isin(ant)]

c1,c2,c3,c4=st.columns(4)
c1.metric("Avg Coverage", f"{coverage_f['coverage'].mean():.1f}%" if "coverage" in coverage_f else "N/A")
c2.metric("Countries", coverage_f["name"].nunique() if "name" in coverage_f else "N/A")
c3.metric("Reported Cases", f"{int(cases['cases'].sum()):,}" if "cases" in cases else "N/A")
c4.metric("Coverage Records", f"{len(coverage_f):,}")

tab1,tab2,tab3,tab4=st.tabs(["Coverage","Disease","Introduction","Data Quality"])

with tab1:
    st.subheader("Vaccination coverage trend")
    if {"year","coverage"}.issubset(coverage_f.columns):
        trend=coverage_f.groupby("year",as_index=False)["coverage"].mean()
        st.plotly_chart(px.line(trend,x="year",y="coverage",markers=True,title="Average Vaccination Coverage"),use_container_width=True)
    if {"name","coverage"}.issubset(coverage_f.columns):
        top=coverage_f.groupby("name",as_index=False)["coverage"].mean().sort_values("coverage")
        st.plotly_chart(px.bar(top,x="coverage",y="name",orientation="h",title="Average Coverage by Country"),use_container_width=True)

with tab2:
    st.subheader("Disease incidence and reported cases")
    if {"year","cases"}.issubset(cases.columns):
        cy=cases.groupby("year",as_index=False)["cases"].sum()
        st.plotly_chart(px.line(cy,x="year",y="cases",markers=True,title="Reported Cases Over Time"),use_container_width=True)
    if {"code","year","coverage"}.issubset(coverage.columns) and {"code","year","incidence_rate"}.issubset(incidence.columns):
        cc=coverage.groupby(["code","year"],as_index=False)["coverage"].mean()
        ii=incidence.groupby(["code","year"],as_index=False)["incidence_rate"].mean()
        m=cc.merge(ii,on=["code","year"]).dropna()
        if len(m)>1:
            corr=m["coverage"].corr(m["incidence_rate"])
            st.metric("Coverage vs incidence correlation", f"{corr:.3f}")
            st.plotly_chart(px.scatter(m,x="coverage",y="incidence_rate",trendline="ols",
                                       title="Vaccination Coverage vs Disease Incidence"),use_container_width=True)
            st.caption("Correlation indicates association, not proof that vaccination alone caused the change.")

with tab3:
    st.subheader("Vaccine introduction")
    if not introduction.empty:
        st.dataframe(introduction.head(1000),use_container_width=True)
        if {"year","intro"}.issubset(introduction.columns):
            iy=introduction.groupby("year",as_index=False)["intro"].mean()
            st.plotly_chart(px.line(iy,x="year",y="intro",markers=True,title="Introduction Indicator Over Time"),use_container_width=True)
    else:
        st.info("Vaccine introduction table not found.")

with tab4:
    st.subheader("Data quality")
    rows=[]
    for name,df in [("coverage",coverage),("incidence",incidence),("cases",cases),("introduction",introduction),("schedule",schedule)]:
        if not df.empty:
            rows.append({"table":name,"rows":len(df),"columns":len(df.columns),
                         "duplicate_rows":int(df.duplicated().sum()),
                         "missing_cells":int(df.isna().sum().sum())})
    st.dataframe(pd.DataFrame(rows),use_container_width=True)
    st.info("Gender, education, urban/rural, density, seasonality and strategy comparisons are only shown when those fields exist in the source data.")

st.divider()
st.subheader("Power BI-ready files")
st.write("The repository contains cleaned CSV exports generated by the Colab notebook. Connect Power BI to these files or to the SQLite database generated by the notebook.")
