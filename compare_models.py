"""Benchmark model families on honest enrollment-derived tasks."""
from pathlib import Path
import json
import warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.impute import SimpleImputer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.svm import SVR, OneClassSVM
from sklearn.metrics import accuracy_score, f1_score, balanced_accuracy_score, mean_absolute_error, mean_squared_error, r2_score
from pipeline import load_data, ROOT, LEVEL

SEED = 42

def make_examples(tx):
    """One example per eligible learner; the final transaction is the target."""
    t = tx.sort_values(['UserID','TransactionDate','TransactionID']).copy()
    rows=[]
    for user, g in t.groupby('UserID',sort=False):
        if len(g)<2: continue
        past, future=g.iloc[:-1],g.iloc[-1]
        categories=past.CourseCategory.value_counts()
        levels=past.CourseLevel.value_counts()
        dates=past.TransactionDate.dropna()
        rows.append({'UserID':user,'past_enrollments':len(past),
            'past_categories':past.CourseCategory.nunique(),
            'past_avg_amount':past.Amount.mean(), 'past_paid_share':past.CourseType.eq('Paid').mean(),
            'past_avg_rating':past.CourseRating.mean(),
            'past_avg_level':past.CourseLevel.map(LEVEL).mean(),
            'past_months':dates.dt.to_period('M').nunique(),
            'past_span_days':(dates.max()-dates.min()).days if len(dates) else 0,
            'last_amount':past.iloc[-1].Amount,
            'last_level':past.iloc[-1].CourseLevel,
            'last_category':past.iloc[-1].CourseCategory,
            'preferred_category':categories.index[0],
            'preferred_level':levels.index[0],
            'next_category':future.CourseCategory,'next_amount':future.Amount})
    return pd.DataFrame(rows)

def prepare(examples):
    train,test=train_test_split(examples,test_size=.25,random_state=SEED,stratify=examples.next_category)
    excluded=['UserID','next_category','next_amount']
    xtr=pd.get_dummies(train.drop(columns=excluded),dtype=float)
    xte=pd.get_dummies(test.drop(columns=excluded),dtype=float).reindex(columns=xtr.columns,fill_value=0)
    imp=SimpleImputer(strategy='median',add_indicator=True)
    xtr=imp.fit_transform(xtr);xte=imp.transform(xte)
    scaler=StandardScaler();return train,test,scaler.fit_transform(xtr),scaler.transform(xte)

def run():
    _,_,tx=load_data(); examples=make_examples(tx)
    train,test,xtr,xte=prepare(examples)
    ytr,yte=train.next_category,test.next_category
    ctr=test.next_category.value_counts()
    classifiers={
      'Dummy Classifier':DummyClassifier(strategy='most_frequent'),
      'Logistic Regression':LogisticRegression(max_iter=500),
      'K-Nearest Neighbours (KNN)':KNeighborsClassifier(n_neighbors=11),
      'Decision Tree':DecisionTreeClassifier(min_samples_leaf=8,random_state=SEED),
      'Random Forest':RandomForestClassifier(n_estimators=120,min_samples_leaf=4,n_jobs=-1,random_state=SEED),
      'Gradient Boosting':GradientBoostingClassifier(n_estimators=80,max_depth=2,random_state=SEED),
      'Deep Neural Network (MLP)':MLPClassifier(hidden_layer_sizes=(32,16,8),early_stopping=False,max_iter=160,random_state=SEED),
    }
    rows=[]
    for name, model in classifiers.items():
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            model.fit(xtr,ytr)
        pred=model.predict(xte)
        rows.append({'model':name,'task':'Next course category','metric':'Macro F1','score':round(float(f1_score(yte,pred,average='macro',zero_division=0)),4),
                     'accuracy':round(float(accuracy_score(yte,pred)),4),'balanced_accuracy':round(float(balanced_accuracy_score(yte,pred)),4),'sample_size':len(test)})
    regression={
       'Linear Regression':LinearRegression(),
       'Polynomial Regression with Ridge':None,
       'Support Vector Regression (SVR)':SVR(C=5,epsilon=.1),
    }
    amount_tr=train.next_amount.to_numpy();amount_te=test.next_amount.to_numpy()
    for name, model in regression.items():
        a,b=xtr,xte
        if model is None:
            poly=PolynomialFeatures(degree=2,include_bias=False)
            a=poly.fit_transform(xtr);b=poly.transform(xte)
            model=Ridge(alpha=100.0)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore');model.fit(a,amount_tr)
        pred=model.predict(b)
        rows.append({'model':name,'task':'Next transaction amount','metric':'MAE (amount units)','score':round(float(mean_absolute_error(amount_te,pred)),4),
                     'rmse':round(float(np.sqrt(mean_squared_error(amount_te,pred))),4),
                     'r2':round(float(r2_score(amount_te,pred)),4),'sample_size':len(test)})
    anomaly={
       'Isolation Forest':IsolationForest(contamination=.05,n_estimators=150,random_state=SEED),
       'One-Class SVM':OneClassSVM(nu=.05,gamma='scale'),
    }
    for name, model in anomaly.items():
        model.fit(xtr)
        flags=(model.predict(xte)==-1)
        rows.append({'model':name,'task':'Unusual behavior detection','metric':'Flag rate (unlabeled)','score':round(float(flags.mean()),4),'sample_size':len(test)})
    # MLPRegressor with bottleneck is an autoencoder: input and target are the same.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        encoder=MLPRegressor(hidden_layer_sizes=(32,8,32),activation='relu',alpha=.01,early_stopping=True,max_iter=180,random_state=SEED)
        encoder.fit(xtr,xtr)
    reconstruction=((encoder.predict(xte)-xte)**2).mean(axis=1)
    threshold=np.quantile(((encoder.predict(xtr)-xtr)**2).mean(axis=1),.95)
    rows.append({'model':'Autoencoder (MLP bottleneck)','task':'Unusual behavior detection','metric':'Flag rate (unlabeled)',
                 'score':round(float((reconstruction>threshold).mean()),4),'sample_size':len(test)})
    out=ROOT/'artifacts';out.mkdir(exist_ok=True)
    result=pd.DataFrame(rows)
    result.to_csv(out/'model_comparison.csv',index=False)
    metadata={'split':'One final enrollment per learner held out as target; disjoint learner train/test 75/25',
              'eligible_learners':len(examples),'train_learners':len(train),'test_learners':len(test),
              'target_classes':int(ytr.nunique()),'target_definition':'Next category or next amount; these are observed enrollments, not completion labels',
              'anomaly_limit':'No anomaly labels exist; flag rates are descriptive, not precision/recall',
              'classification_baseline_macro_f1':rows[0]['score']}
    (out/'comparison_metadata.json').write_text(json.dumps(metadata,indent=2))
    print(result.to_string(index=False));print(json.dumps(metadata,indent=2))
    return result
if __name__=='__main__':run()
