# Model comparison and honest interpretation

## What each model predicts

| Task | Models | Outcome and evaluation |
| --- | --- | --- |
| Next course category | Dummy, Logistic Regression, KNN, Decision Tree, Random Forest, Gradient Boosting, three-hidden-layer MLP | Final observed enrollment category per learner; macro F1, accuracy and balanced accuracy on held-out learners |
| Next transaction amount | Linear Regression, degree-2 Polynomial Regression with Ridge, SVR | Final observed transaction amount; MAE, RMSE and R² on held-out learners |
| Unusual learner profile | Isolation Forest, One-Class SVM, bottleneck MLP autoencoder | No ground truth; report only the fraction flagged on held-out learners |

Only users with at least two enrollments qualify for a next-enrollment target. For each, historical features come strictly from transactions before that learner's final observed enrollment. The 75/25 train/test split separates learners and stratifies by target category. Preprocessing fits only on training learners. The autoencoder is a three-hidden-layer MLP regressor trained to reconstruct its input; high reconstruction error is flagged above the 95th percentile of training errors. Its architecture is `(32, 8, 32)`. Classification MLP has `(32, 16, 8)` hidden layers. These are compact neural networks, not sequence models.

## Measured result

1,380 learners qualify: 1,035 training and 345 held out. There are 12 next-category classes. Dummy macro F1 is 0.0141. See `artifacts/model_comparison.csv` for every model's measured score. Low category performance indicates limited predictive signal in these enrollment records; choosing a classifier by its apparent rank would overstate usefulness. Regression is about recorded amounts, not demand forecasts or learner value. Anomaly detectors have no validated positive class; their flag rates are not precision, recall, or evidence of fraud.

The live recommendation ranking remains based on the learner's prior category and level, segment course popularity, and smoothed ratings. The classification models are an evaluated experiment and are not presented as proven recommendation precision. Model selection for deployment needs chronological backtesting, actual recommendation exposures, and a controlled engagement or completion trial. The data includes no outcomes for engagement lift, course completion or educational benefit.

## Reproduce

Run `python compare_models.py` in the project folder. It writes `artifacts/model_comparison.csv` and `artifacts/comparison_metadata.json` and uses random seed 42. Then run `streamlit run app.py` and open Model Comparison. No API keys or external data downloads are required.
