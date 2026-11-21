# Visuals Directory — Exported Analytical Figures

This directory stores high-resolution (`300 DPI`) publication-grade figures automatically exported by `netflix_content_analytics.ipynb` during execution. These figures are referenced in the root `README.md` and can be used directly in technical reports, slide decks, or portfolio write-ups.

## Generated Figure Inventory

| Figure File | Analytical Stage | Description |
| :--- | :--- | :--- |
| `01_catalogue_composition.png` | Section 8.1 | Catalogue split (Movies vs. TV Shows) with exact counts and percentage shares |
| `02_release_year_distribution.png` | Section 8.2 | Historical production release year curve (1925–2021) by content type |
| `03_top_10_countries.png` | Section 8.3 | Top 10 contributing countries (exploded multi-country attribution) with Movie vs. TV Show stacked breakdown |
| `04_top_10_genres.png` | Section 8.4 | Top 10 overall catalogue genres across all exploded genre tags |
| `05_movie_duration_distribution.png` | Section 8.5 | Movie runtime distribution (histogram, KDE, boxplot, mean/median/IQR markers) |
| `06_tv_show_season_distribution.png` | Section 8.6 | TV show season count frequency distribution highlighting single-season dominance |
| `07_content_rating_distribution.png` | Section 8.7 | Overall maturity rating distribution across standardized rating tiers |
| `08_yearly_content_addition_trends.png` | Section 8.8 | Yearly content addition velocity (`year_added`, 2008–2021) and seasonality heatmap |
| `09_content_ratings_by_type.png` | Section 8.9 | Cross-tabulated proportional comparison of maturity ratings between Movies and TV Shows |
| `10_genre_comparisons_by_type.png` | Section 8.10 | Dual-panel comparative breakdown of Top 10 Movie genres vs. Top 10 TV Show genres |
| `11_country_genre_heatmap.png` | Section 8.11 | Multivariate row-normalized specialization heatmap of Top 8 countries × Top 8 genres |
| `12_acquisition_lag_distribution.png` | Section 8.12 | Licensing vs. original release lag distribution (`year_added - release_year`) by content type |

## Reproducibility Note

All figures in this directory are deterministically generated when executing `netflix_content_analytics.ipynb` from top to bottom.
