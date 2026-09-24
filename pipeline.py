"""Reproducible learner segmentation and cluster-aware course recommendations."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent
LEVEL = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}

def load_data(path=ROOT / 'data/edupro.xlsx'):
    users = pd.read_excel(path, sheet_name='Users')
    courses = pd.read_excel(path, sheet_name='Courses')
    transactions = pd.read_excel(path, sheet_name='Transactions')
    for name, df, key in [('users', users, 'UserID'), ('courses', courses, 'CourseID'), ('transactions', transactions, 'TransactionID')]:
        if df[key].isna().any() or df[key].duplicated().any():
            raise ValueError(f'{name}: missing or duplicate {key}')
    transactions['TransactionDate'] = pd.to_datetime(transactions['TransactionDate'], errors='coerce')
    tx = transactions.merge(courses, on='CourseID', how='inner', validate='many_to_one')
    if len(tx) != len(transactions):
        raise ValueError('Transactions refer to unknown courses')
    if not tx.UserID.isin(users.UserID).all():
        raise ValueError('Transactions refer to unknown users')
    return users, courses, tx

def build_profiles(users, courses, tx):
    t = tx.copy()
    t['level_num'] = t.CourseLevel.map(LEVEL).fillna(0)
    grouped = t.groupby('UserID')
    features = grouped.agg(enrollments=('CourseID', 'size'), unique_courses=('CourseID', 'nunique'),
        diversity=('CourseCategory', 'nunique'), total_spend=('Amount', 'sum'),
        avg_spend=('Amount', 'mean'), avg_rating=('CourseRating', 'mean'),
        avg_level=('level_num', 'mean'), paid_share=('CourseType', lambda v: (v == 'Paid').mean()),
        active_months=('TransactionDate', lambda d: d.dt.to_period('M').nunique()),
        first_enrollment=('TransactionDate','min'),last_enrollment=('TransactionDate','max'))
    features['courses_per_category'] = features.enrollments / features.diversity.clip(lower=1)
    features['enrollments_per_active_month'] = features.enrollments / features.active_months.clip(lower=1)
    features['depth_index'] = grouped.level_num.apply(lambda v: (v.ge(2).sum() + 1)/(v.eq(0).sum() + 1))
    features['preferred_category'] = grouped.CourseCategory.apply(lambda v: v.value_counts().index[0])
    features['preferred_level'] = grouped.CourseLevel.apply(lambda v: v.value_counts().index[0])
    profiles = users.merge(features.reset_index(), on='UserID', how='left')
    profiles['enrollments'] = profiles.enrollments.fillna(0).astype(int)
    profiles['status'] = np.where(profiles.enrollments > 0, 'Enrolled', 'No enrollment')
    return profiles

NUMERIC = ['enrollments','diversity','courses_per_category','enrollments_per_active_month',
           'avg_spend','avg_rating','avg_level','paid_share','depth_index']

def fit_segments(profiles):
    active = profiles[profiles.enrollments > 0].copy()
    x = active[NUMERIC].copy()
    for col in ['enrollments','courses_per_category','enrollments_per_active_month','avg_spend','depth_index']:
        x[col] = np.log1p(x[col].clip(lower=0))
    arr = StandardScaler().fit_transform(SimpleImputer(strategy='median').fit_transform(x))
    ks = range(2, min(7, len(active)-1))
    scores = {k: float(silhouette_score(arr, KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(arr), sample_size=min(1500,len(arr)), random_state=42)) for k in ks}
    best_k = max(scores, key=scores.get)
    labels = KMeans(n_clusters=best_k, n_init=20, random_state=42).fit_predict(arr)
    active['cluster'] = labels
    coords = PCA(n_components=3, random_state=42).fit_transform(arr)
    active['x'], active['y'], active['z'] = coords[:,0], coords[:,1], coords[:,2]
    sample = np.random.default_rng(42).choice(len(arr), min(500,len(arr)), replace=False)
    hierarchical = AgglomerativeClustering(n_clusters=best_k).fit_predict(arr[sample])
    agreement = float(adjusted_rand_score(labels[sample], hierarchical))
    centers = active.groupby('cluster')[NUMERIC].mean()
    names = {}
    for cluster, row in centers.iterrows():
        if row.enrollments >= centers.enrollments.median() and row.diversity >= centers.diversity.median():
            name = 'Cross-domain Explorer'
        elif row.enrollments < centers.enrollments.median():
            name = 'Early-stage Learner'
        else:
            name = 'Focused Learner'
        names[int(cluster)] = f'{name} · {int(cluster)+1:02d}'
    active['segment'] = active.cluster.map(names)
    return active, {'silhouette_by_k':scores,'selected_k':best_k,'silhouette':scores[best_k], 'hierarchical_ari_sample':agreement}

def recommend(user_id, profiles, courses, tx, limit=8, category=None, level=None):
    person = profiles.loc[profiles.UserID == user_id]
    if person.empty: raise ValueError('Unknown learner')
    person = person.iloc[0]
    seen = set(tx.loc[tx.UserID == user_id, 'CourseID'])
    candidates = courses.loc[~courses.CourseID.isin(seen)].copy()
    if category: candidates = candidates[candidates.CourseCategory == category]
    if level: candidates = candidates[candidates.CourseLevel == level]
    if candidates.empty: return candidates.assign(score=pd.Series(dtype=float), why=pd.Series(dtype=str))
    # Bayesian rating prevents tiny, weakly rated courses from dominating.
    counts = tx.groupby('CourseID').size()
    cluster_users = set(profiles.loc[profiles.segment == person.segment, 'UserID']) if pd.notna(person.get('segment')) else set()
    cluster_counts = tx.loc[tx.UserID.isin(cluster_users)].groupby('CourseID').UserID.nunique()
    cat = person.preferred_category if pd.notna(person.get('preferred_category')) else None
    lev = person.preferred_level if pd.notna(person.get('preferred_level')) else None
    candidates['category_match'] = (candidates.CourseCategory == cat).astype(float)
    candidates['level_match'] = (candidates.CourseLevel == lev).astype(float)
    candidates['cluster_popularity'] = candidates.CourseID.map(cluster_counts).fillna(0).astype(float)
    denom = max(candidates.cluster_popularity.max(),1)
    candidates['cluster_popularity'] = np.log1p(candidates.cluster_popularity)/np.log1p(denom)
    global_mean = courses.CourseRating.mean()
    n = candidates.CourseID.map(counts).fillna(0)
    candidates['rating_score'] = ((n*candidates.CourseRating + 5*global_mean)/(n+5)/5).clip(0,1)
    candidates['score'] = 100*(.4*candidates.category_match + .2*candidates.level_match + .2*candidates.cluster_popularity + .2*candidates.rating_score)
    candidates['why'] = np.select([candidates.category_match.eq(1)&candidates.level_match.eq(1), candidates.category_match.eq(1), candidates.level_match.eq(1)], ['Matches your category and level','Matches your preferred category','Matches your preferred level'], default='Popular with similar learners')
    return candidates.sort_values(['score','CourseID'],ascending=[False,True]).head(limit)

def main():
    users,courses,tx = load_data()
    profiles = build_profiles(users,courses,tx)
    active,metrics = fit_segments(profiles)
    out = ROOT/'artifacts'; out.mkdir(exist_ok=True)
    active.drop(columns=['Email']).to_csv(out/'learner_segments.csv',index=False)
    (out/'model_metrics.json').write_text(json.dumps(metrics,indent=2))
    print(json.dumps({'users':len(users),'courses':len(courses),'transactions':len(tx),'active_learners':len(active),**metrics},indent=2))
if __name__ == '__main__': main()
