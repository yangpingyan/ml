# Author: Tim Head <betatim@gmail.com>
#
# License: BSD 3 clause

import numpy as np

np.random.seed(10)

import matplotlib.pyplot as plt

from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (RandomTreesEmbedding, RandomForestClassifier,
                              GradientBoostingClassifier)
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve
from sklearn.pipeline import make_pipeline

n_estimator = 10
X, y = make_classification(n_samples=80000)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)
# It is important to train the ensemble of trees on a different subset
# of the training data than the linear regression model to avoid
# overfitting, in particular if the total number of leaves is
# similar to the number of training samples
X_train, X_train_lr, y_train, y_train_lr = train_test_split(X_train,
                                                            y_train,
                                                            test_size=0.5)

# Unsupervised transformation based on totally random trees
rt = RandomTreesEmbedding(max_depth=3, n_estimators=n_estimator,
                          random_state=0)

rt_lm = LogisticRegression()
pipeline = make_pipeline(rt, rt_lm)
pipeline.fit(X_train, y_train)
y_pred_rt = pipeline.predict_proba(X_test)[:, 1]
fpr_rt_lm, tpr_rt_lm, _ = roc_curve(y_test, y_pred_rt)

# Supervised transformation based on random forests
rf = RandomForestClassifier(max_depth=3, n_estimators=n_estimator)
rf_enc = OneHotEncoder()
rf_lm = LogisticRegression()
rf.fit(X_train, y_train)
rf_enc.fit(rf.apply(X_train))
rf_lm.fit(rf_enc.transform(rf.apply(X_train_lr)), y_train_lr)

y_pred_rf_lm = rf_lm.predict_proba(rf_enc.transform(rf.apply(X_test)))[:, 1]
fpr_rf_lm, tpr_rf_lm, _ = roc_curve(y_test, y_pred_rf_lm)

grd = GradientBoostingClassifier(n_estimators=n_estimator)
grd_enc = OneHotEncoder()
grd_lm = LogisticRegression()
grd.fit(X_train, y_train)
grd_enc.fit(grd.apply(X_train)[:, :, 0])
grd_lm.fit(grd_enc.transform(grd.apply(X_train_lr)[:, :, 0]), y_train_lr)

y_pred_grd_lm = grd_lm.predict_proba(
    grd_enc.transform(grd.apply(X_test)[:, :, 0]))[:, 1]
fpr_grd_lm, tpr_grd_lm, _ = roc_curve(y_test, y_pred_grd_lm)

# The gradient boosted model by itself
y_pred_grd = grd.predict_proba(X_test)[:, 1]
fpr_grd, tpr_grd, _ = roc_curve(y_test, y_pred_grd)

# The random forest model by itself
y_pred_rf = rf.predict_proba(X_test)[:, 1]
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_pred_rf)

plt.figure(1)
plt.plot([0, 1], [0, 1], 'k--')
plt.plot(fpr_rt_lm, tpr_rt_lm, label='RT + LR')
plt.plot(fpr_rf, tpr_rf, label='RF')
plt.plot(fpr_rf_lm, tpr_rf_lm, label='RF + LR')
plt.plot(fpr_grd, tpr_grd, label='GBT')
plt.plot(fpr_grd_lm, tpr_grd_lm, label='GBT + LR')
plt.xlabel('False positive rate')
plt.ylabel('True positive rate')
plt.title('ROC curve')
plt.legend(loc='best')
plt.show()

plt.figure(2)
plt.xlim(0, 0.2)
plt.ylim(0.8, 1)
plt.plot([0, 1], [0, 1], 'k--')
plt.plot(fpr_rt_lm, tpr_rt_lm, label='RT + LR')
plt.plot(fpr_rf, tpr_rf, label='RF')
plt.plot(fpr_rf_lm, tpr_rf_lm, label='RF + LR')
plt.plot(fpr_grd, tpr_grd, label='GBT')
plt.plot(fpr_grd_lm, tpr_grd_lm, label='GBT + LR')
plt.xlabel('False positive rate')
plt.ylabel('True positive rate')
plt.title('ROC curve (zoomed in at top left)')
plt.legend(loc='best')
plt.show()

import json

mibao_dic = [{'relevanceRule': 'tdTotalScore',
              'score': 123,
              'dataSourceStr': '同盾类',
              'threshold': 10,
              'tactfullyDescription': '商品同盾风险分阈值',
              'status': '命中'},
             {'relevanceRule': 'zu_lin_ren_shen_fen_zheng_yan_zheng',
              'score': 5,
              'dataSourceStr': '同盾类',
              'threshold': 80,
              'tactfullyDescription': '租赁人身份证验证',
              'status': '未命中'},
             {'relevanceRule': 'zu_lin_ren_xing_wei',
              'score': 113,
              'dataSourceStr': '同盾类',
              'threshold': 60,
              'tactfullyDescription': '租赁人行为',
              'status': '命中'},
             {'relevanceRule': 'shou_ji_hao_yan_zheng',
              'score': 5,
              'dataSourceStr': '同盾类',
              'threshold': 60,
              'tactfullyDescription': '手机号码验证',
              'status': '未命中'},
             {'relevanceRule': 'fan_qi_za',
              'score': 0,
              'dataSourceStr': '同盾类',
              'threshold': 60,
              'tactfullyDescription': '反欺诈',
              'status': '未命中'}]
tongdun_dict = {'success': True,
                'result_desc': {'INFOANALYSIS': {'address_detect': {'true_ip_address': '中国广东省惠州市',
                                                                    'mobile_address': '广东省惠州市',
                                                                    'id_card_address': '四川省泸州市叙永县'},
                                                 'geoip_info': {'proxy_info': [],
                                                                'isp': '电信',
                                                                'latitude': 23.079405,
                                                                'position': '中国广东省惠州市',
                                                                'longitude': 114.4126},
                                                 'device_info': {'error': '参数缺失'},
                                                 'geotrueip_info': {}},
                                'RENT': {'final_score': 71,
                                         'risk_items': [{'rule_id': 23612664,
                                                         'score': 5,
                                                         'decision': 'Accept',
                                                         'risk_name': '租赁人身份证命中中风险关注名单',
                                                         'risk_detail': [{'hit_type_display_name': '租赁人身份证',
                                                                          'fraud_type_display_name': '异常绑卡、信用异常、异常借款、申请行为异常',
                                                                          'grey_list_details': [
                                                                              {'evidence_time': 1521434039000,
                                                                               'risk_level': '中',
                                                                               'fraud_type': 'suspiciousBinding',
                                                                               'fraud_type_display_name': '异常绑卡',
                                                                               'value': '510524197809055357'},
                                                                              {'evidence_time': 1536443899000,
                                                                               'risk_level': '中',
                                                                               'fraud_type': 'creditSuspicious',
                                                                               'fraud_type_display_name': '信用异常',
                                                                               'value': '510524197809055357'},
                                                                              {'evidence_time': 1527888447000,
                                                                               'risk_level': '中',
                                                                               'fraud_type': 'suspiciousLoan',
                                                                               'fraud_type_display_name': '异常借款',
                                                                               'value': '510524197809055357'},
                                                                              {'evidence_time': 1527888447000,
                                                                               'risk_level': '中',
                                                                               'fraud_type': 'applySuspicious',
                                                                               'fraud_type_display_name': '申请行为异常',
                                                                               'value': '510524197809055357'}],
                                                                          'description': '验证匹配字段是否在关注名单中',
                                                                          'type': 'grey_list'}]},
                                                        {'rule_id': 23612714,
                                                         'score': 2,
                                                         'decision': 'Accept',
                                                         'risk_name': '租赁人身份证命中低风险关注名单',
                                                         'risk_detail': [{'hit_type_display_name': '租赁人身份证',
                                                                          'fraud_type_display_name': '异常租赁',
                                                                          'grey_list_details': [
                                                                              {'evidence_time': 1537169918000,
                                                                               'risk_level': '低',
                                                                               'fraud_type': 'suspiciousRent',
                                                                               'fraud_type_display_name': '异常租赁',
                                                                               'value': '510524197809055357'}],
                                                                          'description': '租赁人身份证命中低风险关注名单',
                                                                          'type': 'grey_list'}]},
                                                        {'rule_id': 23612674,
                                                         'score': 25,
                                                         'decision': 'Accept',
                                                         'risk_name': '7天内租赁人在多个平台申请借款',
                                                         'risk_detail': [{'platform_detail_dimension': [{'count': 4,
                                                                                                         'detail': [{
                                                                                                             'count': 2,
                                                                                                             'industry_display_name': '一般消费分期平台'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '银行个人业务'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': 'P2P网贷'}],
                                                                                                         'dimension': '租赁人手机'},
                                                                                                        {'count': 5,
                                                                                                         'detail': [{
                                                                                                             'count': 2,
                                                                                                             'industry_display_name': '一般消费分期平台'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '银行个人业务'},
                                                                                                             {
                                                                                                                 'count': 2,
                                                                                                                 'industry_display_name': 'P2P网贷'}],
                                                                                                         'dimension': '租赁人身份证'}],
                                                                          'platform_detail': [{'count': 2,
                                                                                               'industry_display_name': '一般消费分期平台'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '银行个人业务'},
                                                                                              {'count': 2,
                                                                                               'industry_display_name': 'P2P网贷'}],
                                                                          'description': '7天内租赁人在多个平台申请借款',
                                                                          'type': 'platform_detail',
                                                                          'platform_count': 5}]},
                                                        {'rule_id': 23612694,
                                                         'score': 24,
                                                         'decision': 'Accept',
                                                         'risk_name': '1个月内租赁人在多个平台申请借款',
                                                         'risk_detail': [{'platform_detail_dimension': [{'count': 13,
                                                                                                         'detail': [{
                                                                                                             'count': 2,
                                                                                                             'industry_display_name': '一般消费分期平台'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '大数据金融'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '银行个人业务'},
                                                                                                             {
                                                                                                                 'count': 4,
                                                                                                                 'industry_display_name': '银行消费金融公司'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '信用卡中心'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '网上银行'},
                                                                                                             {
                                                                                                                 'count': 2,
                                                                                                                 'industry_display_name': 'P2P网贷'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '综合类电商平台'}],
                                                                                                         'dimension': '租赁人身份证'},
                                                                                                        {'count': 10,
                                                                                                         'detail': [{
                                                                                                             'count': 2,
                                                                                                             'industry_display_name': '一般消费分期平台'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '大数据金融'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '银行个人业务'},
                                                                                                             {
                                                                                                                 'count': 4,
                                                                                                                 'industry_display_name': '银行消费金融公司'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': 'P2P网贷'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '综合类电商平台'}],
                                                                                                         'dimension': '租赁人手机'}],
                                                                          'platform_detail': [{'count': 2,
                                                                                               'industry_display_name': '一般消费分期平台'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '大数据金融'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '银行个人业务'},
                                                                                              {'count': 4,
                                                                                               'industry_display_name': '银行消费金融公司'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '信用卡中心'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '网上银行'},
                                                                                              {'count': 2,
                                                                                               'industry_display_name': 'P2P网贷'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '综合类电商平台'}],
                                                                          'description': '在指定时间内，主属性关联的合作方或行业类型的个数',
                                                                          'type': 'platform_detail',
                                                                          'platform_count': 13}]},
                                                        {'rule_id': 23612704,
                                                         'score': 10,
                                                         'decision': 'Accept',
                                                         'risk_name': '3个月内租赁人在多个平台申请借款',
                                                         'risk_detail': [{'platform_detail_dimension': [{'count': 15,
                                                                                                         'detail': [{
                                                                                                             'count': 3,
                                                                                                             'industry_display_name': '一般消费分期平台'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '互联网金融门户'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '大数据金融'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '银行个人业务'},
                                                                                                             {
                                                                                                                 'count': 4,
                                                                                                                 'industry_display_name': '银行消费金融公司'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '信用卡中心'},
                                                                                                             {
                                                                                                                 'count': 3,
                                                                                                                 'industry_display_name': 'P2P网贷'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '综合类电商平台'}],
                                                                                                         'dimension': '租赁人手机'},
                                                                                                        {'count': 17,
                                                                                                         'detail': [{
                                                                                                             'count': 3,
                                                                                                             'industry_display_name': '一般消费分期平台'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '互联网金融门户'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '大数据金融'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '银行个人业务'},
                                                                                                             {
                                                                                                                 'count': 4,
                                                                                                                 'industry_display_name': '银行消费金融公司'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '信用卡中心'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '网上银行'},
                                                                                                             {
                                                                                                                 'count': 4,
                                                                                                                 'industry_display_name': 'P2P网贷'},
                                                                                                             {
                                                                                                                 'count': 1,
                                                                                                                 'industry_display_name': '综合类电商平台'}],
                                                                                                         'dimension': '租赁人身份证'}],
                                                                          'platform_detail': [{'count': 3,
                                                                                               'industry_display_name': '一般消费分期平台'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '互联网金融门户'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '大数据金融'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '银行个人业务'},
                                                                                              {'count': 4,
                                                                                               'industry_display_name': '银行消费金融公司'},
                                                                                              {'count': 2,
                                                                                               'industry_display_name': '信用卡中心'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '网上银行'},
                                                                                              {'count': 4,
                                                                                               'industry_display_name': 'P2P网贷'},
                                                                                              {'count': 1,
                                                                                               'industry_display_name': '综合类电商平台'}],
                                                                          'description': '在指定时间内，主属性关联的合作方或行业类型的个数',
                                                                          'type': 'platform_detail',
                                                                          'platform_count': 18}]},
                                                        {'rule_id': 23612464,
                                                         'score': 5,
                                                         'decision': 'Accept',
                                                         'risk_name': '手机号命中中风险关注名单',
                                                         'risk_detail': [{'hit_type_display_name': '租赁人手机',
                                                                          'fraud_type_display_name': '信用异常、异常借款',
                                                                          'grey_list_details': [
                                                                              {'evidence_time': 1536443899000,
                                                                               'risk_level': '中',
                                                                               'fraud_type': 'creditSuspicious',
                                                                               'fraud_type_display_name': '信用异常',
                                                                               'value': '18026454319'},
                                                                              {'evidence_time': 1527888447000,
                                                                               'risk_level': '中',
                                                                               'fraud_type': 'suspiciousLoan',
                                                                               'fraud_type_display_name': '异常借款',
                                                                               'value': '18026454319'}],
                                                                          'description': '验证匹配字段是否在关注名单中',
                                                                          'type': 'grey_list'}]}],
                                         'final_decision': 'REVIEW'}},
                'id': 'WF2018092510074313331596'}

baiqishi_dict = {'finalDecision': 'Review',
                 'finalScore': '0',
                 'flowNo': '1809251115CF43E47710384CA8AD61C5419FB180925',
                 'resultCode': 'BQS000',
                 'strategySet': [{'hitRules': [{'decision': 'Review',
                                                'memo': '百度信用分：575',
                                                'ruleId': '520102',
                                                'ruleName': '用户百度信用分评估一般',
                                                'score': 0,
                                                'template': 'bdScore'}],
                                  'riskType': 'suspiciousAction',
                                  'strategyDecision': 'Review',
                                  'strategyId': '3a90ba87c2104ea5a5906906fd7eb9e2',
                                  'strategyMode': 'WorstMode',
                                  'strategyName': '百度风险名单策略',
                                  'strategyScore': 0},
                                 {'hitRules': [{'decision': 'Review',
                                                'detail': [{'name': '总数', 'type': 'all', 'value': '20'},
                                                           {'name': '持牌消费金融', 'type': 'single', 'value': '1'},
                                                           {'name': 'P2P理财', 'type': 'single', 'value': '1'},
                                                           {'name': '互联网小贷', 'type': 'single', 'value': '2'},
                                                           {'name': '消费分期', 'type': 'single', 'value': '2'},
                                                           {'name': '现金借贷', 'type': 'single', 'value': '12'},
                                                           {'name': '其它', 'type': 'single', 'value': '2'}],
                                                'memo': '总数:20,持牌消费金融:1,P2P理财:1,互联网小贷:2,消费分期:2,现金借贷:12,其它:2',
                                                'ruleId': '520068',
                                                'ruleName': '手机号一个月内多头申请过多',
                                                'score': 0,
                                                'template': 'multiLoan'},
                                               {'decision': 'Review',
                                                'detail': [{'name': '总数', 'type': 'all', 'value': '3'},
                                                           {'name': '现金借贷', 'type': 'single', 'value': '1'},
                                                           {'name': '垂直金融', 'type': 'single', 'value': '1'},
                                                           {'name': '生活租赁', 'type': 'single', 'value': '1'}],
                                                'memo': '总数:3,现金借贷:1,垂直金融:1,生活租赁:1',
                                                'ruleId': '520078',
                                                'ruleName': '身份证号一天内多头申请过多',
                                                'score': 0,
                                                'template': 'realTimeMultiLoan'},
                                               {'decision': 'Review',
                                                'detail': [{'name': '总数', 'type': 'all', 'value': '27'},
                                                           {'name': '持牌消费金融', 'type': 'single', 'value': '1'},
                                                           {'name': '垂直金融', 'type': 'single', 'value': '1'},
                                                           {'name': 'P2P理财', 'type': 'single', 'value': '2'},
                                                           {'name': '互联网小贷', 'type': 'single', 'value': '5'},
                                                           {'name': '消费分期', 'type': 'single', 'value': '2'},
                                                           {'name': '现金借贷', 'type': 'single', 'value': '14'},
                                                           {'name': '其它', 'type': 'single', 'value': '2'}],
                                                'memo': '总数:27,持牌消费金融:1,垂直金融:1,P2P理财:2,互联网小贷:5,消费分期:2,现金借贷:14,其它:2',
                                                'ruleId': '520064',
                                                'ruleName': '身份证三个月内多头申请过多',
                                                'score': 0,
                                                'template': 'multiLoan'},
                                               {'decision': 'Review',
                                                'detail': [{'name': '总数', 'type': 'all', 'value': '27'},
                                                           {'name': '持牌消费金融', 'type': 'single', 'value': '1'},
                                                           {'name': '垂直金融', 'type': 'single', 'value': '1'},
                                                           {'name': 'P2P理财', 'type': 'single', 'value': '2'},
                                                           {'name': '互联网小贷', 'type': 'single', 'value': '4'},
                                                           {'name': '消费分期', 'type': 'single', 'value': '2'},
                                                           {'name': '现金借贷', 'type': 'single', 'value': '15'},
                                                           {'name': '其它', 'type': 'single', 'value': '2'}],
                                                'memo': '总数:27,持牌消费金融:1,垂直金融:1,P2P理财:2,互联网小贷:4,消费分期:2,现金借贷:15,其它:2',
                                                'ruleId': '520069',
                                                'ruleName': '手机号三个月内多头申请过多',
                                                'score': 0,
                                                'template': 'multiLoan'},
                                               {'decision': 'Review',
                                                'detail': [{'name': '总数', 'type': 'all', 'value': '14'},
                                                           {'name': 'P2P理财', 'type': 'single', 'value': '1'},
                                                           {'name': '互联网小贷', 'type': 'single', 'value': '2'},
                                                           {'name': '消费分期', 'type': 'single', 'value': '2'},
                                                           {'name': '现金借贷', 'type': 'single', 'value': '9'}],
                                                'memo': '总数:14,P2P理财:1,互联网小贷:2,消费分期:2,现金借贷:9',
                                                'ruleId': '520063',
                                                'ruleName': '身份证七天内多头申请过多',
                                                'score': 0,
                                                'template': 'multiLoan'},
                                               {'decision': 'Review',
                                                'detail': [{'name': '总数', 'type': 'all', 'value': '14'},
                                                           {'name': 'P2P理财', 'type': 'single', 'value': '1'},
                                                           {'name': '互联网小贷', 'type': 'single', 'value': '2'},
                                                           {'name': '消费分期', 'type': 'single', 'value': '2'},
                                                           {'name': '现金借贷', 'type': 'single', 'value': '9'}],
                                                'memo': '总数:14,P2P理财:1,互联网小贷:2,消费分期:2,现金借贷:9',
                                                'ruleId': '520067',
                                                'ruleName': '手机号七天内多头申请过多',
                                                'score': 0,
                                                'template': 'multiLoan'},
                                               {'decision': 'Review',
                                                'detail': [{'name': '总数', 'type': 'all', 'value': '20'},
                                                           {'name': '持牌消费金融', 'type': 'single', 'value': '1'},
                                                           {'name': 'P2P理财', 'type': 'single', 'value': '1'},
                                                           {'name': '互联网小贷', 'type': 'single', 'value': '2'},
                                                           {'name': '消费分期', 'type': 'single', 'value': '2'},
                                                           {'name': '现金借贷', 'type': 'single', 'value': '12'},
                                                           {'name': '其它', 'type': 'single', 'value': '2'}],
                                                'memo': '总数:20,持牌消费金融:1,P2P理财:1,互联网小贷:2,消费分期:2,现金借贷:12,其它:2',
                                                'ruleId': '520065',
                                                'ruleName': '身份证一个月内多头申请过多',
                                                'score': 0,
                                                'template': 'multiLoan'},
                                               {'decision': 'Review',
                                                'detail': [{'name': '总数', 'type': 'all', 'value': '3'},
                                                           {'name': '现金借贷', 'type': 'single', 'value': '1'},
                                                           {'name': '垂直金融', 'type': 'single', 'value': '1'},
                                                           {'name': '生活租赁', 'type': 'single', 'value': '1'}],
                                                'memo': '总数:3,现金借贷:1,垂直金融:1,生活租赁:1',
                                                'ruleId': '520079',
                                                'ruleName': '手机号一天内多头申请过多',
                                                'score': 0,
                                                'template': 'realTimeMultiLoan'}],
                                  'riskType': 'multipleLoan',
                                  'strategyDecision': 'Review',
                                  'strategyId': '7a49514a69544831a6656fc698d88b81',
                                  'strategyMode': 'WorstMode',
                                  'strategyName': '多头风险策略',
                                  'strategyScore': 0},
                                 {'hitRules': [{'decision': 'Review',
                                                'memo': '中风险-历史调用多头风险-90天内调用多头过多-2018年04月28日到2018年07月27日关联个数为20',
                                                'ruleId': '520122',
                                                'ruleName': '90天手机号多头大于等于20中风险',
                                                'score': 0,
                                                'template': 'historyMulti'},
                                               {'decision': 'Review',
                                                'memo': '中风险-历史调用多头风险-30天内调用多头过多-2018年04月16日到2018年05月16日关联个数为15',
                                                'ruleId': '520127',
                                                'ruleName': '30天身份证多头大于等于15中风险',
                                                'score': 0,
                                                'template': 'historyMulti'},
                                               {'decision': 'Review',
                                                'memo': '中风险-历史调用多头风险-90天内调用多头过多-2018年06月24日到2018年09月22日关联个数为20',
                                                'ruleId': '520126',
                                                'ruleName': '90天身份证多头大于等于20中风险',
                                                'score': 0,
                                                'template': 'historyMulti'},
                                               {'decision': 'Review',
                                                'memo': '中风险-历史调用多头风险-30天内调用多头过多-2018年04月16日到2018年05月16日关联个数为15',
                                                'ruleId': '520123',
                                                'ruleName': '30天手机号多头大于等于15中风险',
                                                'score': 0,
                                                'template': 'historyMulti'},
                                               {'decision': 'Review',
                                                'memo': '中风险-历史调用多头风险-7天内调用多头过多-2018年08月12日到2018年08月19日关联个数为10',
                                                'ruleId': '520128',
                                                'ruleName': '7天身份证多头大于等于10中风险',
                                                'score': 0,
                                                'template': 'historyMulti'}],
                                  'riskType': 'suspiciousAction',
                                  'strategyDecision': 'Review',
                                  'strategyId': 'abdc9e8979854d5eb8224ad399f0cc27',
                                  'strategyMode': 'WorstMode',
                                  'strategyName': '历史多头',
                                  'strategyScore': 0}]}

'''
df['tdjs'] = df['guanzhu_detail_json'].map(lambda x : json.loads(x) if isinstance(x, str) else 0)
df.at[63677,'tdjs']
test = df[df['guanzhu_result'].notnull() & df['guanzhu_result'].str.match('命中')]
'''

guanzhu_dict1 = {'bizNo': 'ZM201809253000000394600104398959',
                 'body': '{"success":true,"biz_no":"ZM201809253000000394600104398959","details":[{"biz_code":"AA","code":"AA001007","extend_info":[{"description":"逾期金额（元）","key":"event_max_amt_code","value":"M03"},{"description":"编号","key":"id","value":"ec52de5594297be50310d3ce2a8475d5"},{"description":"违约时间","key":"event_end_time_desc","value":"2016-07"}],"level":3,"refresh_time":"2018-09-23 00:00:00","settlement":true,"type":"AA001"}],"is_matched":true}',
                 'details': [{'bizCode': 'AA 金融信贷类',
                              'code': 'AA001007  逾期180天以上',
                              'extendInfo': [{'description': '逾期金额（元）',
                                              'key': 'event_max_amt_code',
                                              'value': 'M03'},
                                             {'description': '编号',
                                              'key': 'id',
                                              'value': 'ec52de5594297be50310d3ce2a8475d5'},
                                             {'description': '违约时间', 'key': 'event_end_time_desc', 'value': '2016-07'}],
                              'level': 3,
                              'refreshTime': 1537632000000,
                              'settlement': True,
                              'type': 'AA001 逾期未还款'}],
                 'isMatched': True,
                 'params': {
                     'params': 'aLPM3nVMVrQICcltA/eoaPbDKkj2YR6yONxTHHg6B6VOF+w9lK7IlDQwFaHqWVEohTGUdnU3tLEeTcnW8X6hLGNVbn8YB28ANYtdwUOvSSjkozGYg3KeKjMPAi6tQfSkfrRM7UzZgqdJnv79AAlgVZWmxwcCnm2v7gm9x8asbsc='},
                 'success': True}
