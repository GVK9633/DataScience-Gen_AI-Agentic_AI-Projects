# ML Assignment 2 — Classification Models with Streamlit Deployment

**Course:** M.Tech (AIML/DSE), Machine Learning — BITS Pilani WILP
**Student ID:** 2025AC05267

---

## a. Problem Statement

Breast cancer diagnosis from digitized fine needle aspirate (FNA) images is a
critical medical classification task. Given a set of numeric measurements
describing cell nuclei present in a breast mass (radius, texture, perimeter,
area, smoothness, compactness, concavity, symmetry, fractal dimension, etc.,
each summarized as mean / standard-error / "worst" value), the goal is to
classify the mass as **malignant** or **benign**.

This assignment implements and compares five classification algorithms on
this dataset, exposes them through an interactive Streamlit web application,
and deploys the app for live evaluation.

---

## b. Dataset Description

- **Name:** Breast Cancer Wisconsin (Diagnostic) Data Set
- **Source:** UCI Machine Learning Repository
  (https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic),
  accessed via `sklearn.datasets.load_breast_cancer`
- **Instances:** 569 (≥ 500 ✅)
- **Features:** 30 numeric features (≥ 12 ✅)
- **Target:** Binary — `0 = malignant`, `1 = benign`
- **Class balance:** 212 malignant / 357 benign
- **Train/Test split:** 80% / 20%, stratified on the target, `random_state=42`

The 20% held-out test split (features + true label) is saved as
[`test_data.csv`](./test_data.csv) and is the file used to demo the Streamlit
app / for evaluation.

---

## c. GitHub Repository Link

> **TODO:** Push this project to a GitHub repository and paste the link here,
> e.g. `https://github.com/<your-username>/ml-assignment-2-classification`

---

## d. Models Used

All 5 models were trained on the same dataset and same train/test split.

### Comparison Table

| ML Model Name | Accuracy | AUC | Precision | Recall | F1 | MCC |
|---|---|---|---|---|---|---|
| Logistic Regression | 0.9825 | 0.9954 | 0.9861 | 0.9861 | 0.9861 | 0.9623 |
| Decision Tree | 0.9123 | 0.9147 | 0.9559 | 0.9028 | 0.9286 | 0.8174 |
| kNN | 0.9737 | 0.9884 | 0.9600 | 1.0000 | 0.9796 | 0.9442 |
| Naive Bayes | 0.9386 | 0.9878 | 0.9452 | 0.9583 | 0.9517 | 0.8676 |
| Random Forest (Ensemble) | 0.9474 | 0.9937 | 0.9583 | 0.9583 | 0.9583 | 0.8869 |

*(Regenerated automatically from `model/model_results.csv` by
`model/train_models.py` — figures may shift slightly if you change the
random seed or re-tune hyperparameters.)*

### Observations

| ML Model Name | Observation about model performance |
|---|---|
| Logistic Regression | Best overall performer on this dataset. The classes are close to linearly separable once features are standardized, so a linear decision boundary generalizes very well — highest Accuracy, AUC, F1, and MCC of all five models. |
| Decision Tree | Weakest performer. A single tree (even depth-limited to 6) overfits the training split and is sensitive to small variations in the data, giving noticeably lower AUC and MCC than the other models. |
| kNN | Very strong performer, with perfect Recall (no malignant/benign case missed at this threshold) and the second-best F1. Distance-based similarity works well because the standardized features form fairly compact, well-separated clusters. |
| Naive Bayes | Reasonable but the weakest of the "probabilistic" models — the conditional-independence assumption across 30 correlated features (e.g., radius/perimeter/area are inherently correlated) costs some precision and MCC. |
| Random Forest (Ensemble) | Solid, well-balanced performance and the highest AUC after Logistic Regression — averaging many trees reduces the overfitting seen in the single Decision Tree, though it doesn't beat Logistic Regression or kNN on this particular dataset. |
| **Overall Winner for your dataset?** | **Logistic Regression** — it achieves the best or near-best score on every metric (Accuracy 0.9825, AUC 0.9954, F1 0.9861, MCC 0.9623), and is also the simplest, most interpretable, and cheapest model to deploy. kNN is a very close second, notably on Recall. |

---

## Repository Structure

```
project-folder/
│-- app.py                       # Streamlit application (imports each model
│                                   from model/*.py and trains live, in-app)
│-- requirements.txt
│-- README.md
│-- test_data.csv                # held-out test split (features + label)
│-- model/
│   │-- __init__.py
│   │-- data.py                  # shared dataset loading + train/test split
│   │-- logistic_regression.py   # Logistic Regression model
│   │-- decision_tree.py         # Decision Tree model
│   │-- knn.py                   # k-Nearest Neighbors model
│   │-- naive_bayes.py           # Gaussian Naive Bayes model
│   │-- random_forest.py         # Random Forest (ensemble) model
│   │-- registry.py              # collects all 5 models into one ordered mapping
│   │-- train_models.py          # reference/reproducibility script: reuses
│   │                              the same model files, regenerates
│   │                              test_data.csv and the metrics table below
│   │-- model_results.csv        # metrics table (source of truth for README table)
```

**No model pickling.** Each classifier lives in its own `.py` file under
`model/`, defining how to build and train that model (`build_model()`,
`train()`, `NEEDS_SCALING`). `app.py` imports these files directly and
trains all 5 live at startup (cached with `st.cache_resource` so it only
runs once per session, not on every click), using the exact same dataset,
train/test split, and `random_state` as `model/train_models.py`. There is
no `.pkl` file anywhere in the project, so there's no risk of a
scikit-learn version mismatch between the training and deployment
environments.

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Live Streamlit App Link

> **TODO:** Deploy on https://streamlit.io/cloud (New App → select this repo →
> branch `main` → main file `app.py` → Deploy) and paste the live link here.

## Streamlit App Features

0. **No pickled models** — each model is defined in its own `model/*.py`
   file and trained live when the app starts (cached per session), so the
   app has no dependency on a specific scikit-learn version matching a
   saved `.pkl` file.
1. **Dataset upload (CSV)** — upload `test_data.csv` (or any file with the
   same 30 feature columns, optionally with a `diagnosis` column).
2. **Model selection dropdown** — choose among Logistic Regression, Decision
   Tree, kNN, Naive Bayes, and Random Forest.
3. **Evaluation metrics display** — Accuracy, AUC, Precision, Recall, F1, MCC
   computed live on the uploaded data (if labels are present).
4. **Confusion matrix + classification report** — heatmap and per-class
   precision/recall/F1 table.
5. Optional: run all 5 models at once on the uploaded data for a live
   side-by-side comparison.

## BITS Virtual Lab Screenshot

> **TODO:** Add your screenshot of running this on the BITS Virtual Lab here,
> e.g. `![BITS Lab screenshot](./screenshot.png)`, and include the same
> image in the final submitted PDF as required by the assignment.
