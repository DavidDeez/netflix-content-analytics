from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Netflix Content Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "netflix_titles.csv"
VISUALS_DIR = PROJECT_ROOT / "visuals"

@st.cache_data
def load_and_clean_data():
    df_raw = pd.read_csv(DATA_PATH)
    df = df_raw.copy()

    # Repair 3 records with duration values shifted into the rating column
    mask_shifted = df["rating"].astype(str).str.contains("min", na=False)
    df.loc[mask_shifted, "duration"] = df.loc[mask_shifted, "rating"]
    df.loc[mask_shifted, "rating"] = np.nan

    # Strip standard and non-breaking whitespace (\xa0) and deduplicate on (title, type)
    df["title"] = df["title"].str.replace("\xa0", " ", regex=False).str.strip()
    df["_title_key"] = df["title"].str.lower()
    df = (
        df.drop_duplicates(subset=["_title_key", "type"], keep="first")
        .drop(columns=["_title_key"])
        .reset_index(drop=True)
    )

    # Parse date_added and compute temporal features
    df["date_added_clean"] = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
    df["year_added"] = df["date_added_clean"].dt.year.astype("Int64")
    df["month_added"] = df["date_added_clean"].dt.month.astype("Int64")
    df["month_name_added"] = df["date_added_clean"].dt.month_name()
    df["acquisition_lag"] = df["year_added"] - df["release_year"]

    # Standardize rating categories and map to unified maturity tiers
    df["rating_clean"] = df["rating"].str.strip().replace({"UR": "NR"}).fillna("Unrated / Unknown")
    maturity_map = {
        "TV-Y": "Kids & Family", "TV-Y7": "Kids & Family", "TV-Y7-FV": "Kids & Family",
        "G": "Kids & Family", "TV-G": "Kids & Family", "PG": "Kids & Family", "TV-PG": "Kids & Family",
        "PG-13": "Teens (13+)", "TV-14": "Teens (13+)",
        "R": "Mature Adults (17+)", "TV-MA": "Mature Adults (17+)", "NC-17": "Mature Adults (17+)",
        "NR": "Unrated / Unknown", "Unrated / Unknown": "Unrated / Unknown"
    }
    df["maturity_tier"] = df["rating_clean"].map(maturity_map)

    # Explicit labels for missing categorical metadata
    df["director_clean"] = df["director"].fillna("Unknown / Not Applicable").str.strip()
    df["cast_clean"] = df["cast"].fillna("Unknown / Uncredited").str.strip()
    df["country_clean"] = df["country"].fillna("Unknown / Unspecified").str.strip()

    # Numeric duration extraction
    dur_num = df["duration"].str.extract(r"(\d+)")[0].astype(int)
    df["duration_min"] = np.where(df["type"] == "Movie", dur_num, np.nan)
    df["seasons"] = np.where(df["type"] == "TV Show", dur_num, np.nan)

    return df_raw, df

df_raw, df_clean = load_and_clean_data()

# Sidebar
st.sidebar.markdown("### Netflix Content Analytics")
st.sidebar.caption("Author: David Olukayode  \nAI & ML Engineer | Applied Research")
st.sidebar.markdown("---")
st.sidebar.subheader("Catalogue Filters")

selected_types = st.sidebar.multiselect(
    "Content Format (type)",
    options=["Movie", "TV Show"],
    default=["Movie", "TV Show"]
)

min_yr, max_yr = int(df_clean["release_year"].min()), int(df_clean["release_year"].max())
selected_years = st.sidebar.slider(
    "Original Release Year (release_year)",
    min_value=min_yr, max_value=max_yr, value=(1980, max_yr)
)

maturity_options = ["Mature Adults (17+)", "Teens (13+)", "Kids & Family", "Unrated / Unknown"]
selected_tiers = st.sidebar.multiselect(
    "Audience Maturity Tier",
    options=maturity_options,
    default=maturity_options
)

search_query = st.sidebar.text_input("Filter by Title, Director, or Cast", "")

filtered_df = df_clean[
    df_clean["type"].isin(selected_types) &
    df_clean["release_year"].between(selected_years[0], selected_years[1]) &
    df_clean["maturity_tier"].isin(selected_tiers)
].copy()

if search_query.strip():
    q = search_query.strip().lower()
    filtered_df = filtered_df[
        filtered_df["title"].str.lower().str.contains(q, na=False) |
        filtered_df["director_clean"].str.lower().str.contains(q, na=False) |
        filtered_df["cast_clean"].str.lower().str.contains(q, na=False)
    ]

# Header
st.title("Netflix Content Analytics")
st.markdown(
    "**An Exploratory Data Analysis of Global Streaming Content**  \n"
    "Author: David Olukayode | AI & ML Engineer | Applied Research | Trustworthy AI"
)

# Summary Metrics
col1, col2, col3, col4, col5 = st.columns(5)
total_n = len(filtered_df)
movies_n = (filtered_df["type"] == "Movie").sum()
tv_n = (filtered_df["type"] == "TV Show").sum()
med_dur = filtered_df["duration_min"].median()
mature_pct = (filtered_df["maturity_tier"] == "Mature Adults (17+)").mean() * 100 if total_n > 0 else 0

col1.metric("Unique Titles (Filtered)", f"{total_n:,}", f"of {len(df_clean):,} total")
col2.metric("Movies", f"{movies_n:,}", f"{(movies_n/total_n*100 if total_n else 0):.1f}% share")
col3.metric("TV Shows", f"{tv_n:,}", f"{(tv_n/total_n*100 if total_n else 0):.1f}% share")
col4.metric("Median Movie Runtime", f"{med_dur:.0f} min" if pd.notna(med_dur) else "N/A", "IQR: 87–114 min")
col5.metric("Mature (17+) Share", f"{mature_pct:.1f}%", "TV-MA / R / NC-17")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Statistical Figures",
    "2. Cross-Tabulations",
    "3. Data Quality Audit",
    "4. Key Findings & Limitations",
    "5. Catalogue Table"
])

with tab1:
    st.subheader("Statistical Figures (N = 8,803 Unique Titles)")
    st.caption("Figures generated from the cleaned dataset in netflix_content_analytics.ipynb.")

    chart_specs = [
        ("01_catalogue_composition.png", "Figure 1: Catalogue Composition (RQ01)",
         "Movies account for 6,128 titles (69.61%) vs. 2,675 TV Shows (30.39%), a 2.29:1 format ratio."),
        ("02_release_year_distribution.png", "Figure 2: Release Year Distribution (1980–2021)",
         "84.85% of titles were released from 2010 onward, and 62.08% from 2015–2021. Movie releases peaked in 2017–2018 (767/yr); TV Show releases peaked in 2020 (436)."),
        ("03_top_10_countries.png", "Figure 3: Top 10 Producing Countries by Format Split (RQ02)",
         "United States (3,689), India (1,046), and United Kingdom (806) lead overall. India is 92.0% Movies, whereas South Korea (73.6% TV) and Japan (62.6% TV) specialize in series."),
        ("04_top_10_genres.png", "Figure 4: Top 10 Overall Genre Categories (RQ03)",
         "International Movies (2,749, 31.2%), Dramas (2,425, 27.5%), Comedies (1,672, 19.0%), and International TV Shows (1,350, 15.3%) lead across 19,315 genre tags."),
        ("05_movie_duration_distribution.png", "Figure 5: Movie Runtime Distribution (RQ05 — Movies)",
         "Median runtime is 98.0 min (Mean = 99.56 min, SD = 28.30, IQR = 87–114 min). Tukey 1.5xIQR fences flag 249 short titles (<46.5 min) and 201 long titles (>154.5 min)."),
        ("06_tv_show_season_distribution.png", "Figure 6: TV Show Season Distribution (RQ05 — TV Shows)",
         "67.03% (1,793) of TV Shows have 1 Season, and 82.92% have 2 or fewer Seasons."),
        ("07_content_rating_distribution.png", "Figure 7: Content Rating Distribution (RQ06)",
         "TV-MA (36.40%) and TV-14 (24.54%) together represent 60.93% of the catalogue."),
        ("08_yearly_content_addition_trends.png", "Figure 8: Yearly & Monthly Content Additions (RQ04)",
         "Annual additions grew from 82 titles (2015) to 2,016 titles (2019). TV Show additions reached 595 titles in 2020."),
        ("09_content_ratings_by_type.png", "Figure 9: Maturity Ratings by Content Format (RQ06)",
         "Reconciling MPAA and TV Parental ratings shows TV Shows allocate 29.5% to Kids & Family vs. 20.7% for Movies."),
        ("10_genre_comparisons_by_type.png", "Figure 10: Genre Comparison by Format (RQ03)",
         "International tags appear on 44.9% of Movies and 50.5% of TV Shows; Crime TV (17.6%), Kids' TV (16.9%), and Docuseries (14.8%) anchor episodic television."),
        ("11_country_genre_heatmap.png", "Figure 11: Country x Genre Row-Normalized Matrix (RQ07)",
         "Row-normalized specialization matrix across the top 8 countries and top 8 genres."),
        ("12_acquisition_lag_distribution.png", "Figure 12: Content Acquisition Lag (year_added - release_year, RQ04)",
         "51.98% of TV Shows are added in their release year (median lag = 0 yrs), whereas 29.12% of Movies are library films added 6+ years post-release.")
    ]

    for i in range(0, len(chart_specs), 2):
        c1, c2 = st.columns(2)
        for col, spec in zip([c1, c2], chart_specs[i:i+2]):
            fname, title, desc = spec
            img_path = VISUALS_DIR / fname
            with col:
                st.markdown(f"#### {title}")
                if img_path.exists():
                    st.image(str(img_path), use_container_width=True)
                st.caption(desc)

with tab2:
    st.subheader("Cross-Tabulations on Filtered Selection")
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown("##### Format x Audience Maturity Tier")
        if len(filtered_df) > 0:
            ct_mat = pd.crosstab(filtered_df["type"], filtered_df["maturity_tier"], margins=True)
            st.dataframe(ct_mat, use_container_width=True)
            ct_mat_pct = (pd.crosstab(filtered_df["type"], filtered_df["maturity_tier"], normalize="index") * 100).round(2)
            st.caption("Row-Normalized Percentage (% within Format):")
            st.dataframe(ct_mat_pct, use_container_width=True)

    with c_right:
        st.markdown("##### Top 10 Producing Countries in Filtered Selection")
        if len(filtered_df) > 0:
            exp_c = (
                filtered_df.assign(_c=filtered_df["country_clean"].str.split(","))
                .explode("_c")
            )
            exp_c["Country"] = exp_c["_c"].str.strip()
            exp_c = exp_c[(exp_c["Country"] != "") & (~exp_c["Country"].str.startswith("Unknown"))]
            top_c_table = pd.crosstab(exp_c["Country"], exp_c["type"])
            top_c_table["Total"] = top_c_table.sum(axis=1)
            if "TV Show" in top_c_table.columns:
                top_c_table["TV_Share (%)"] = (top_c_table["TV Show"] / top_c_table["Total"] * 100).round(1)
            top_c_table = top_c_table.sort_values("Total", ascending=False).head(10)
            st.dataframe(top_c_table, use_container_width=True)

with tab3:
    st.subheader("Data Quality Audit (Raw N = 8,807 -> Cleaned N = 8,803)")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### 1. Missing-Value Profile Stratified by Format")
        miss_cnt = df_raw.isnull().sum()
        miss_df = pd.DataFrame({
            "Missing_Count": miss_cnt,
            "Overall_%": (miss_cnt / len(df_raw) * 100).round(2),
            "Movies_%": (df_raw[df_raw["type"] == "Movie"].isnull().mean() * 100).round(2),
            "TV_Shows_%": (df_raw[df_raw["type"] == "TV Show"].isnull().mean() * 100).round(2),
        })
        st.dataframe(miss_df[miss_df["Missing_Count"] > 0].sort_values("Missing_Count", ascending=False), use_container_width=True)
        st.caption(
            "Note: director is missing in 91.41% of TV Shows vs. 3.07% of Movies (MAR conditioned on format). "
            "Dropping null rows would remove 91.4% of all TV Shows."
        )
    with col_b:
        st.markdown("##### 2. Misplaced Duration Values in rating Column (3 Records)")
        shifted_rows = df_raw[df_raw["rating"].astype(str).str.contains("min", na=False)][
            ["show_id", "type", "title", "release_year", "rating", "duration"]
        ]
        st.dataframe(shifted_rows, use_container_width=True)
        st.caption("Reassigning '74 min', '84 min', and '66 min' from rating to duration resolves all 3 duration nulls.")

        st.markdown("##### 3. Duplicate (title, type) Pairs After Whitespace/Case Normalization")
        norm_t = df_raw["title"].str.replace("\xa0", " ", regex=False).str.strip().str.lower()
        dups_df = df_raw[df_raw.assign(_nt=norm_t).duplicated(subset=["_nt", "type"], keep=False)][
            ["show_id", "type", "title", "director", "release_year", "date_added", "duration"]
        ].sort_values("release_year")
        st.dataframe(dups_df, use_container_width=True)

with tab4:
    st.subheader("Summary of Findings & Methodological Limitations")
    st.markdown("""
1. **Catalogue Composition:** 6,128 Movies (69.61%) vs. 2,675 TV Shows (30.39%), a 2.29:1 ratio.
2. **Data Quality Corrections:** All 3 missing `duration` records were recovered from shifted `rating` values; 4 duplicate `(title, type)` pairs were removed (`8,807 -> 8,803`).
3. **Regional Format Split:** United States (3,689), India (1,046), and United Kingdom (806) lead total credits. India is 92.0% Movies, whereas South Korea (73.6% TV Shows) and Japan (62.6% TV Shows) focus on episodic series.
4. **Genre Distribution:** `International Movies` (31.2%), `Dramas` (27.5%), `Comedies` (19.0%), and `International TV Shows` (15.3%) lead overall.
5. **Addition Trends:** Annual additions rose from 82 (2015) to 2,016 (2019); TV Show additions peaked at 595 titles in 2020.
6. **Release Year Distribution:** 84.85% of the catalogue was released from 2010 onward (62.08% from 2015–2021).
7. **Acquisition Lag (`year_added - release_year`):** 51.98% of TV Shows are added in their release year (median lag = 0 yrs) vs. 30.40% of Movies (median lag = 2 yrs); 29.12% of Movies are library films added 6+ years post-release.
8. **Movie Runtimes:** Median 98.0 min (Mean = 99.56 min, IQR = 87–114 min). `Classic Movies` (112 min) and `International Movies` (107 min) run significantly longer than `Stand-Up Comedy` (62 min).
9. **TV Show Seasons:** 67.03% (1,793) of TV Shows have 1 Season, and 82.92% have 2 or fewer Seasons.
10. **Maturity Ratings:** 75.61% of the catalogue targets Mature Adults (45.51%) or Teens (30.10%), while TV Shows allocate a larger share to Kids & Family (29.50%) than Movies (20.71%).

**Scope Limitation:** This dataset captures static catalogue metadata as of September 25, 2021. It does not contain viewership hours, completion rates, or revenue metrics.
    """)

with tab5:
    st.subheader(f"Catalogue Records ({len(filtered_df):,} rows)")
    display_cols = [
        "show_id", "type", "title", "director_clean", "country_clean",
        "release_year", "year_added", "acquisition_lag", "rating_clean",
        "maturity_tier", "duration", "listed_in"
    ]
    st.dataframe(filtered_df[display_cols], use_container_width=True, height=520)
