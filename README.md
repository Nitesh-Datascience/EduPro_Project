# EduPro learner intelligence

A Streamlit dashboard with six views: Overview, Learner Explorer, Recommendations, Segment Comparison, Model Comparison, and Model & Data. The Overview includes an interactive 3D PCA learner map with a 2D switch. The supplied workbook lives at `data/edupro.xlsx`.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python pipeline.py
streamlit run app.py
```

Open the local URL printed by Streamlit. For Streamlit Community Cloud, place this folder at the repository root, set the main file to `app.py`, and keep `data/edupro.xlsx` in the repo. The workbook includes user names and email addresses: obtain consent or replace identifying fields before publishing the repo. The dashboard shows IDs, and its export excludes emails.

## Method

Transactions join to Courses by CourseID and to Users by UserID. User-level features cover enrollment volume and frequency, category diversity, spend, rating, paid share, course level, and depth. Continuous skewed fields are log transformed, median imputed, and standardized. K-Means tests 2–6 segments (where feasible) and selects the highest sampled silhouette score. Hierarchical clustering provides a separate agreement check on a fixed 500-learner sample. PCA is used only for the two-dimensional display. Segment labels are descriptive heuristics, not learned targets.

Recommendations exclude already taken courses and rank by 40% category match, 20% level match, 20% popularity among the learner's segment, and 20% rating with five global-mean pseudo-observations. Filtering applies before ranking. Because the dataset lacks exposures, clicks, completions, and outcomes, offline precision and engagement lift cannot be honestly computed. A production evaluation would use chronological holdouts and an A/B experiment, with privacy-aware logging.

`pipeline.py` writes `artifacts/learner_segments.csv` and `artifacts/model_metrics.json`. Outputs are reproducible with random seed 42. `Amount` and `CoursePrice` are displayed as rupees for the intended India-facing prototype; confirm workbook currency before operational use.

## Compare the requested 13 models

```bash
python compare_models.py
```

Open **Model Comparison** in the dashboard. The comparison includes seven classification models (Dummy, Logistic Regression, KNN, Decision Tree, Random Forest, Gradient Boosting, and an MLP with three hidden layers), three regression models (Linear, degree-2 Polynomial with Ridge, SVR), and three anomaly models (Isolation Forest, One-Class SVM, and a bottleneck MLP autoencoder). K-Means and hierarchical clustering still handle learner segmentation. The recommendation page still uses an interpretable content and segment-popularity ranking; the classifier does not automatically replace it because the observed held-out category results are weak. See `MODEL_COMPARISON.md` and `artifacts/model_comparison.csv`.
