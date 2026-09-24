# EduPro: learner segmentation and personalized recommendations

## Abstract
This project analyzes the supplied EduPro workbook to describe learner behavior and rank unseen courses for each enrolled learner. The analysis covers 3,000 registered learners, 60 courses, and 10,000 transactions. K-Means selected two clusters by silhouette score; recommendations combine course metadata, segment popularity, and smoothed rating.

## Research question and data
Can enrollment and course attributes yield useful learner groups and transparent course rankings? Users supplies demographics; Courses supplies category, level, type, and rating; Transactions supplies dated enrollments and amount. Teachers is present but outside the stated scope. All 3,000 users have at least one enrollment. Transaction frequency is a count of observed enrollments per active calendar month, not session activity. No completion or engagement event data is present.

## Preparation and EDA
The pipeline checks unique IDs and join coverage, then aggregates transactions at UserID level. Features include enrollments, unique courses, category diversity, courses per category, enrollments per active month, mean spending, mean enrolled rating, mean course level, paid share, and an advanced-to-beginner ratio. It also retains the most frequently enrolled category and level for recommendations. Skewed nonnegative measures receive log1p; numeric inputs receive median imputation and standard scaling. Names, emails, age, and gender are excluded from clustering.

Enrollment activity separates the dominant group of early-stage learners from a smaller group exploring many categories. Segments describe historical records and should not be treated as aptitude or protected characteristics.

## Clustering and validation
K-Means with random seed 42 and 20 initializations chooses the highest silhouette among k=2 through k=6. Sampled silhouette by k: 2 = 0.428, 3 = 0.361, 4 = 0.366, 5 = 0.382, 6 = 0.376. The selected k=2 model yields 2,533 Early-stage Learners (1.53 average enrollments, 1.48 categories) and 467 Cross-domain Explorers (13.12 average enrollments, 8.54 categories). Hierarchical clustering on a fixed 500-learner sample agrees with the K-Means assignments at adjusted Rand index 0.968. PCA coordinates serve visualization only. Segment membership is descriptive, not causal.

## Recommendation method
For each learner, exclude courses already enrolled in. Rank eligible courses with 40% category preference, 20% level preference, 20% log-scaled popularity among learners in the same cluster, and 20% Bayesian-smoothed course rating. The dashboard supports level and category filtering and explains the strongest content match. Segment popularity shares historical data with the learner being recommended to; use a chronological holdout when measuring predictive quality.

## Operational recommendations
Offer early-stage learners a short path of beginner courses in their preferred category and allow explorers to branch into adjacent categories. Explain recommendation reasons and allow users to change their interests. Avoid making high-stakes decisions from segments. Before deployment, validate currency, remove personal identifiers from shared repositories, refresh segments on a schedule, monitor group-level coverage, and log impressions and outcomes with appropriate consent.

## Evaluation limits
The silhouette score measures clustering separation, not learner benefit. The workbook lacks impressions, clicks, completion, satisfaction, or retention, so recommendation precision and engagement lift cannot be measured from it. To validate impact, collect timestamped recommendation exposures and subsequent enrollment/completion, assess held-out ranking by time, then test against the existing recommendation policy through a randomized A/B experiment. Do not report a proxy as proven lift.

## Reproducibility
Run `python pipeline.py`, then `streamlit run app.py`. Source code and dependency ranges are included. The app computes the model from the supplied workbook with fixed random seeds.

## Additional supervised and anomaly model study
The companion `MODEL_COMPARISON.md` defines thirteen requested models across three distinct tasks. Learners' final transactions form held-out next-category and next-amount labels, using only previous transactions as predictors. The 1,380 eligible learners split into 1,035 training and 345 test learners. Dummy macro F1 is 0.0141 across 12 classes. A weak baseline and low model scores argue for caution: these records do not establish accurate personalized prediction. Isolation Forest, One-Class SVM and an MLP autoencoder flag unusual profiles, but cannot be validated without anomaly labels. These additional studies do not replace the unsupervised segmentation or prove engagement lift.
