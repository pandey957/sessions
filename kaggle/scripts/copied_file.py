import datetime
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
import xgboost as xgb
import random
import time
import os
from sklearn.metrics import log_loss
random.seed(12345)
import sys
#sys.stdout = open('test.log','wb')
def run_xgb(train, test, features, target, depth=9, random_state=0):
    eta = 0.005
    max_depth = depth
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
    data_dir = '/datadrive/satyendra.pandey/sessions/kaggle/data'
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
    pbd = pd.read_csv(os.path.join(data_dir,"phone_brand_device_model.csv"), dtype={'device_id': np.str})
    pbd.drop_duplicates('device_id', keep='first', inplace=True)
    pbd = map_column(pbd, 'phone_brand')
    pbd = map_column(pbd, 'device_model')

    # Event_HourWise
    #dateparse = lambda dates: pd.datetime.strptime(dates, '%Y-%m-%d %H:%M:%S')
    event_df= pd.read_csv(os.path.join(data_dir,'events.csv'), dtype = {'device_id': np.str} )
    del event_df['longitude']
    del event_df['latitude']
    event_df['hour'] = event_df['timestamp'].map(lambda x: 'hour_' + x.split(' ')[-1][:2])
    del event_df['timestamp']
    event_df['event_id'] = 1
    event_df1= pd.pivot_table(event_df, values='event_id', columns = ['hour'], index='device_id', aggfunc=np.sum)
    final_df = event_df1.reset_index()

    # Lookign into locations used per day and unknown locations
    dateparse = lambda dates: pd.datetime.strftime(pd.datetime.strptime(dates, '%Y-%m-%d %H:%M:%S'),"%a")
    event_df= pd.read_csv(os.path.join(data_dir,'events.csv'), dtype = {'device_id': np.str},
                      date_parser=dateparse,parse_dates=['timestamp'] )
    del event_df['event_id']
    df1 = event_df.ix[(event_df.longitude!=0.00) | (event_df.latitude!=0.00),
                  ['device_id','timestamp','longitude','latitude']]
    df1['loc'] = df1.longitude.astype('str') + '-' + df1.latitude.astype('str')
    del df1['longitude']
    del df1['latitude']
    df1.drop_duplicates(['device_id','loc','timestamp'],inplace=True)
    df1.groupby(['device_id','timestamp']).count().reset_index(inplace=True)
    df1.ix[:,'loc'] = 1
    event_day_loc_cnt = pd.pivot_table(df1,values='loc', columns='timestamp',
                                   index='device_id', aggfunc=np.sum).reset_index()
    df2 = event_df.ix[(event_df.longitude==0.00) & (event_df.latitude==0.00)]
    df2 = df2.groupby(['device_id']).count().reset_index()
    del df2['latitude']
    del df2['longitude']
    df2.rename(columns={'timestamp':'unknow_loc_cnt'}, inplace=True)
    event_day_loc = pd.merge(event_day_loc_cnt,df2, how='outer', on='device_id').fillna(0)

    # Grouping data based on label category
    app_label_df = pd.read_csv(os.path.join(data_dir,'app_labels.csv'))
    label_df = pd.read_csv(os.path.join(data_dir,'label_categories.csv'))
    df2 = pd.merge(app_label_df, label_df, how='left', on = 'label_id')
    del df2['label_id']
    app_events_df = pd.read_csv(os.path.join(data_dir,'app_events.csv'), dtype={'device_id':np.str})
    events_df = pd.read_csv(os.path.join(data_dir,'events.csv'))
    del events_df['longitude']
    del events_df['latitude']
    del events_df['timestamp']
    device_evnt_app = pd.merge(events_df, app_events_df, how='inner', on='event_id')
    device_evnt_app = device_evnt_app.ix[device_evnt_app.is_active==1]
    df3 = pd.merge(device_evnt_app,df2, how='left', on = 'app_id')
    category_id = df3.ix[:,['device_id','category','is_active']].groupby(['device_id','category']).count().reset_index()
    category_device_df = pd.pivot_table(category_id, values='is_active',columns='category',
                                    index='device_id', aggfunc=np.sum).reset_index()
    del category_device_df['unknown']
    category_device_df.fillna(0,inplace=True)



    # Train
    print('Read train...')
    train = pd.read_csv(os.path.join(data_dir,"gender_age_train.csv"), dtype={'device_id': np.str})
    train = map_column(train, 'group')
    train = train.drop(['age'], axis=1)
    train = train.drop(['gender'], axis=1)
    train = pd.merge(train, pbd, how='left', on='device_id', left_index=True)
    train = pd.merge(train, events_small, how='left', on='device_id', left_index=True)
    train = pd.merge(train, e1_small, how='left', on='device_id', left_index=True)
    train = pd.merge(train,final_df, how = 'left', on='device_id', left_index=True)
    train = pd.merge(train,event_day_loc, how = 'left', on='device_id', left_index=True)
    train.fillna(-1, inplace=True)

    # Test
    print('Read test...')
    test = pd.read_csv(os.path.join(data_dir,"gender_age_test.csv"), dtype={'device_id': np.str})
    test = pd.merge(test, pbd, how='left', on='device_id', left_index=True)
    test = pd.merge(test, events_small, how='left', on='device_id', left_index=True)
    test = pd.merge(test, e1_small, how='left', on='device_id', left_index=True)
    test = pd.merge(test,final_df, how = 'left', on='device_id', left_index=True)
    test = pd.merge(test,event_day_loc, how = 'left', on='device_id', left_index=True)
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
