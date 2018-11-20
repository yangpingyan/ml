# coding: utf-8

import csv
import json
import pandas as pd
import numpy as np
import os
# Suppress warnings
import warnings
from mltools import *
from mldata import *
import operator
import time

warnings.filterwarnings('ignore')
# to make output display better
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 10)
pd.set_option('display.width', 2000)

# read large csv file
csv.field_size_limit(100000000)

starttime = time.clock()
all_data_df = get_order_data()
print(time.clock() - starttime)
all_data_df_tmp = all_data_df.copy()
all_data_df.shape
# 丢弃不需要的数据
# 去掉白名单用户
df = read_mlfile('risk_white_list', ['user_id'])
user_ids = df['user_id'].values
all_data_df = all_data_df[all_data_df['user_id'].isin(user_ids) != True]

# 去掉joke非0的order
all_data_df = all_data_df[all_data_df['joke'] == 0]

# 根据state生成target，代表最终审核是否通过
state_values = ['pending_receive_goods', 'running', 'user_canceled', 'pending_pay',
                'artificial_credit_check_unpass_canceled', 'pending_artificial_credit_check', 'lease_finished',
                'return_overdue', 'order_payment_overtime_canceled', 'pending_send_goods',
                'merchant_not_yet_send_canceled', 'running_overdue', 'buyout_finished', 'pending_user_compensate',
                'repairing', 'express_rejection_canceled', 'pending_return', 'returning', 'return_goods',
                'pending_relet_check', 'returned_received', 'relet_finished', 'merchant_relet_check_unpass_canceled',
                'system_credit_check_unpass_canceled', 'pending_jimi_credit_check', 'pending_relet_start',
                'pending_refund_deposit', 'merchant_credit_check_unpass_canceled', 'pending_order_receiving']
failure_state_values = ['artificial_credit_check_unpass_canceled', 'return_overdue', 'running_overdue',
                        'merchant_relet_check_unpass_canceled', 'system_credit_check_unpass_canceled',
                        'merchant_credit_check_unpass_canceled', 'user_canceled_system_credit_unpass']
pending_state_values = ['user_canceled', 'pending_artificial_credit_check', 'pending_relet_check',
                        'pending_jimi_credit_check',
                        'pending_relet_start', 'pending_order_receiving']
state_values_newest = all_data_df['state'].unique().tolist()
# 若state字段有新的状态产生， 抛出异常
assert (len(list(set(state_values_newest).difference(set(state_values)))) == 0)

# user_canceled 中部分是机审拒绝， 更改其state为'user_canceled_system_credit_unpass'
# all_data_df[all_data_df['state'] == 'user_canceled'][all_data_df['mibao_remark'] == '机审审核不通过']
# all_data_df[all_data_df['state'] == 'user_canceled']
# all_data_df[all_data_df['state'] == 'artificial_credit_check_unpass_canceled']
all_data_df.loc[(all_data_df['state'] == 'user_canceled') & (all_data_df['mibao_remark'] == '机审审核不通过') ,
    'state'] = 'user_canceled_system_credit_unpass'

all_data_df = all_data_df[all_data_df['state'].isin(pending_state_values) != True]



all_data_df.insert(0, 'target', np.where(all_data_df['state'].isin(failure_state_values), 0, 1))

# 去除测试数据和内部员工数据
all_data_df = all_data_df[all_data_df['cancel_reason'].str.contains('测试') != True]
all_data_df = all_data_df[all_data_df['check_remark'].str.contains('测试') != True]
# 去除命中商户白名单的订单
all_data_df = all_data_df[all_data_df['hit_merchant_white_list'].str.contains('01') != True]

# 丢弃不需要的特征
all_data_df.drop(
    ['tongdun_detail_json', 'mibao_result', 'order_number', 'cancel_reason', 'hit_merchant_white_list', 'check_remark',
     'joke', 'mibao_remark', 'tongdun_remark', 'bai_qi_shi_remark', 'guanzhu_remark'],
    axis=1,
    inplace=True, errors='ignore')

# print(set(all_data_df.columns.tolist()) - set(all_data_df_sql.columns.tolist()))
# 保存数据
all_data_df.to_csv("mibaodata_merged.csv", index=False)
print("mibao.csv saved with shape {}".format(all_data_df.shape))
# missing_values_table(all_data_df)


# In[]
exit('mergedata')
