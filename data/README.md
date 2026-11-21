# Data Directory — Acquisition & Configuration Guide

This directory stores local dataset files used by `netflix_content_analytics.ipynb`. To adhere to repository hygiene best practices, raw CSV files (`*.csv`) and archive bundles (`*.zip`) are excluded from version control via `.gitignore`.

## Dataset Specification

* **Dataset Title:** Netflix Movies and TV Shows (`shivamb/netflix-shows`)
* **Primary File:** `netflix_titles.csv`
* **Source URL:** [https://www.kaggle.com/datasets/shivamb/netflix-shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)
* **License:** CC0: Public Domain (`CC0-1.0`)
* **Dimensions:** 8,807 rows × 12 columns

## How to Obtain the Dataset

### Option 1: Using the Kaggle CLI (Recommended)

If you have the Kaggle API configured (`~/.kaggle/kaggle.json`), run from the project root (`netflix-content-analytics/`):

```bash
kaggle datasets download -d shivamb/netflix-shows -p ./data --unzip
```

### Option 2: Manual Download from Kaggle

1. Navigate to [Kaggle: Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows).
2. Click **Download** to obtain `archive.zip`.
3. Extract `netflix_titles.csv` into this `data/` folder:
   ```text
   netflix-content-analytics/
   └── data/
       ├── README.md
       └── netflix_titles.csv
   ```

## Configurable Data Loading Architecture

The notebook (`netflix_content_analytics.ipynb`) implements an environment-aware path resolution helper (`resolve_dataset_path()`) that checks paths in the following priority order:

1. **Explicit Environment Variable Override:** `NETFLIX_DATA_PATH` (if set in your shell or OS environment).
2. **Local Project Data Directory:** `./data/netflix_titles.csv` (standard local execution from `netflix-content-analytics/`).
3. **Workspace Relative Data Directory:** `./netflix-content-analytics/data/netflix_titles.csv` (if launched from the parent directory).
4. **Current Working Directory:** `./netflix_titles.csv`.
5. **Kaggle Kernel Environment:** `/kaggle/input/netflix-shows/netflix_titles.csv` (automatic fallback when running inside a hosted Kaggle Notebook).
