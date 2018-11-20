# coding:utf8
import os
import time
from argparse import ArgumentParser
from flask import Flask, jsonify
from flask import make_response
import pandas as pd
import json
import lightgbm as lgb
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import warnings
from gevent.pywsgi import WSGIServer
from mltools import *
from mldata import *
import logging
from log import log
import random

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', 60)

# 获取训练数据
all_data_df = pd.read_csv(os.path.join(workdir, "mibaodata_ml.csv"), encoding='utf-8', engine='python')
df = all_data_df.copy()
print("数据量: {}".format(df.shape))
x = df.drop(['target', 'order_id'], axis=1)
y = df['target']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)

# 机器学习模型训练
with open(os.path.join(workdir, "lgb_params.json"), 'r') as f:
    lgb_params_auc = json.load(f)

lgb_clf = lgb.LGBMClassifier(**lgb_params_auc)
lgb_clf.fit(x_train, y_train)
y_pred = lgb_clf.predict(x_test)
accuracy_score = accuracy_score(y_test, y_pred)
print("auc score:", accuracy_score)
assert accuracy_score > 0.96

app = Flask(__name__)


@app.route('/ml_result/<int:order_id>', methods=['GET'])
def get_predict_result(order_id):
    log.debug("order_id: {}".format(order_id))
    ret_data = 2
    df = get_order_data(order_id, is_sql=True)
    if len(df) != 0:
        log.debug(df)
        df = process_data_mibao(df)
        df.drop(['order_id', 'state'], axis=1, inplace=True, errors='ignore')
        # print(list(set(all_data_df.columns.tolist()).difference(set(df.columns.tolist()))))
        if len(df.columns) == 54:
            y_pred = lgb_clf.predict(df)
            ret_data = y_pred[0]
    log.debug("y_pred: {}".format(ret_data))
    # print("reference:", all_data_df[all_data_df['order_id'] == order_id])
    return jsonify({"code": 200, "data": {"result": int(ret_data)}, "message": "SUCCESS"}), 200


@app.route('/debug/<int:debug>', methods=['GET'])
def set_debug_mode(debug):
    if debug == 1:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    log.debug("log mode ", log.level)
    return jsonify({'log_mode': int(log.level)}), 201


@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'bug'}), 404)


if __name__ == '__main__':
    opt = ArgumentParser()
    opt.add_argument('--model', default='gevent')
    args = opt.parse_args()

    if args.model == 'gevent':
        http_server = WSGIServer(('0.0.0.0', 5000), app)
        print('listen on 0.0.0.0:5000')
        http_server.serve_forever()
    elif args.model == 'raw':
        app.run(host='0.0.0.0')

# In[]
