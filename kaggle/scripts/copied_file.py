import datetime
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
import xgboost as xgb
import random
import time
from sklearn.metrics import log_loss
import os
data_dir = '/home/satyendra/sessions/kaggle/data/talking_data'

random.seed(12345)

def run_xgb(train, test, features, target, random_state=0):
    eta = 0.015
    max_depth = 6
    subsample = 0.45
    colsample_bytree = 0.5
    start_time = time.time()

    print('XGBoost params. ETA: {}, MAX_DEPTH: {}, SUBSAMPLE: {}, COLSAMPLE_BY_TREE: {}'.format(eta, max_depth, subsample, colsample_bytree))
    params = {
        "objective": "multi:softprob",
        "num_class": 12,
        "booster" : "gbtree",
        "eval_metric": "mlogloss",
        "eta": eta,
        "max_depth": max_depth,
        "subsample": subsample,
        "colsample_bytree": colsample_bytree,
        "silent": 1,
        "seed": random_state,
    }
    num_boost_round = 1000
    early_stopping_rounds = 25
    test_size = 0.15

    X_train, X_valid = train_test_split(train, test_size=test_size, random_state=random_state)
    print('Length train:', len(X_train.index))
    print('Length valid:', len(X_valid.index))
    y_train = X_train[target]
    y_valid = X_valid[target]
    dtrain = xgb.DMatrix(X_train[features], y_train)
    dvalid = xgb.DMatrix(X_valid[features], y_valid)

    watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
    gbm = xgb.train(params, dtrain, num_boost_round, evals=watchlist, early_stopping_rounds=early_stopping_rounds, verbose_eval=True)

    print("Validating...")
    check = gbm.predict(xgb.DMatrix(X_valid[features]), ntree_limit=gbm.best_iteration)
    score = log_loss(y_valid.tolist(), check)

    print("Predict test set...")
    test_prediction = gbm.predict(xgb.DMatrix(test[features]), ntree_limit=gbm.best_iteration)

    print('Training time: {} minutes'.format(round((time.time() - start_time)/60, 2)))
    return test_prediction.tolist(), score


def create_submission(score, test, prediction):
    # Make Submission
    now = datetime.datetime.now()
    sub_file = 'submission_' + str(score) + '_' + str(now.strftime("%Y-%m-%d-%H-%M")) + '.csv'
    print('Writing submission: ', sub_file)
    f = open(sub_file, 'w')
    f.write('device_id,F23-,F24-26,F27-28,F29-32,F33-42,F43+,M22-,M23-26,M27-28,M29-31,M32-38,M39+\n')
    total = 0
    test_val = test['device_id'].values
    for i in range(len(test_val)):
        str1 = str(test_val[i])
        for j in range(12):
            str1 += ',' + str(prediction[i][j])
        str1 += '\n'
        total += 1
        f.write(str1)
    f.close()


def map_column(table, f):
    labels = sorted(table[f].unique())
    mappings = dict()
    for i in range(len(labels)):
        mappings[labels[i]] = i
    table = table.replace({f: mappings})
    return table


def read_train_test():
    # App
    print('Read apps...')
    app = pd.read_csv(os.path.join(data_dir,"app_events.csv"), dtype={'device_id': np.str})
    app['appcounts'] = app.groupby(['event_id'])['app_id'].transform('count')
    app_small = app[['event_id', 'appcounts']].drop_duplicates('event_id', keep='first')

    # Events
    print('Read events...')
    events = pd.read_csv(os.path.join(data_dir,"events.csv"), dtype={'device_id': np.str})
    events['counts'] = events.groupby(['device_id'])['event_id'].transform('count')
    events_small = events[['device_id', 'counts']].drop_duplicates('device_id', keep='first')
    e1=pd.merge(events, app_small, how='left', on='event_id', left_index=True)
    e1.loc[e1.isnull()['appcounts'] ==True, 'appcounts']=0
    e1['appcounts1'] = e1.groupby(['device_id'])['appcounts'].transform('sum')
    e1_small = e1[['device_id', 'appcounts1']].drop_duplicates('device_id', keep='first')


    # Phone brand
    print('Read brands...')
    device_df = pd.read_csv(os.path.join(data_dir,"phone_brand_device_model.csv"), dtype={'device_id': np.str})
    #pbd.drop_duplicates('device_id', keep='first', inplace=True)
    #pbd = map_column(pbd, 'phone_brand')
    #pbd = map_column(pbd, 'device_model')
    device_df['phone'] = device_df['phone_brand'] + device_df['device_model']
    del device_df['phone_brand']
    del device_df['device_model']
    device_df['phone'] = device_df['phone'].map(lambda x: x.replace(' ',''))
    device__df.drop_duplicates('device_id',keep='first',inplace='True')
    device_df = map_column(device_df, 'phone')
    from sklearn.feature_extraction.text import CountVectorizer
    vectorizer = CountVectorizer(min_df=1)
    X = vectorizer.fit_transform(device_df['phone'])
    df1 = pd.DataFrame(X.toarray(),columns=vectorizer.get_feature_names())
    del device_df['phone']
    pbd = pd.concat([device_df,df1],axis=1)
    device_df = None
    df1 = None
    X = None

    # Train
    print('Read train...')
    train = pd.read_csv(os.path.join(data_dir,"gender_age_train.csv"), dtype={'device_id': np.str})
    train = map_column(train, 'group')
    train = train.drop(['age'], axis=1)
    train = train.drop(['gender'], axis=1)
    train = pd.merge(train, pbd, how='left', on='device_id', left_index=True)
    train = pd.merge(train, events_small, how='left', on='device_id', left_index=True)
    train = pd.merge(train, e1_small, how='left', on='device_id', left_index=True)
    train.fillna(-1, inplace=True)

    # Test
    print('Read test...')
    test = pd.read_csv(os.path.join(data_dir,"gender_age_test.csv"), dtype={'device_id': np.str})
    test = pd.merge(test, pbd, how='left', on='device_id', left_index=True)
    test = pd.merge(test, events_small, how='left', on='device_id', left_index=True)
    test = pd.merge(test, e1_small, how='left', on='device_id', left_index=True)
    test.fillna(-1, inplace=True)

    # Features
    features = list(test.columns.values)
    features.remove('device_id')

    return train, test, features


train, test, features = read_train_test()
print('Length of train: ', len(train))
print('Length of test: ', len(test))
print('Features [{}]: {}'.format(len(features), sorted(features)))
test_prediction, score = run_xgb(train, test, features, 'group')
print("LS: {}".format(round(score, 5)))
create_submission(score, test, test_prediction)
