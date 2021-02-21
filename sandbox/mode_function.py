#!/usr/bin/env python3

""" Mode functions for fund stimulation"""

import pandas as pd
import numpy as np
import datetime as dt
import time
import math
from datetime import date, timedelta


def stamp_to_datetime(timestamp):
    """ function that converts timestamp into datetime type """
    dDate = dt.datetime(timestamp.year, timestamp.month, timestamp.day)
    return dDate


def get_subset(df, startDate, rollingYear):
    """ function that gets the subset of all fund data within three years"""
    sDate = pd.to_datetime(startDate)  # 确认开始日期
    eDate = dt.datetime(sDate.year + rollingYear * 3,
                        sDate.month, sDate.day)  # 确认结束日期
    df = df[df["date"] >= sDate]
    # 筛选出三年数据
    dfs = df[(df["date"] >= sDate) & (df["date"] <= eDate)]
    dfs.reset_index(drop=True, inplace=True)
    last_idx = dfs.index[-1]
    first_idx = dfs.index[0]

    while True:
        firstRow = dfs.iat[1, 0]
        if firstRow.month == 1:
            break
        else:
            dfs = dfs[(first_idx + 1):]

    while df.iat[-1, 0] != dfs.iat[-1, 0]:
        
        lastRow = dfs.iat[-1, 0]
        if lastRow.month == 1:
            break

        dfs = dfs.append(df[(last_idx+1):(last_idx+2)])
        last_idx += 1
    # dfs.reset_index(drop = True, inplace = True)
    # dfs = dfs.loc[0:dfs.shape[0] - 2]
    return dfs


def method1(df, E_end, E, cf_sum, cf_occupied, Eacc_return, Emean_return):
    # 运作期间基准收益率(全阶段) == 业绩基准收益率
    interval_return = (df.iat[-2, 4] / df.iat[0, 4] - 1)
    benchmark_return = E * interval_return + np.sum(cf_occupied)  # 计算期间基准投资收益
    # 基金经理业绩收益
    excess_return = Eacc_return - benchmark_return
    upper_limit = Emean_return * .03
    margin = round((Eacc_return - benchmark_return) * .1, 3)
    return min(margin, Emean_return * .03) if margin > 0 else max(margin, 0), excess_return, upper_limit


def method2(df, Emean_return, benchmk_return_3yr):
    # 期间连乘收益率
    # intv_prod_return = np.prod(1 + df["nv_return"]) - 1
    intv_prod_return = df.iat[-2, 3] / df.iat[0, 3] - 1
    margin = round(Emean_return * (intv_prod_return - benchmk_return_3yr) * .1, 3)
    # return margin
    return min(margin, Emean_return * .03) if margin > 0 else max(margin, 0)


def method3(Emean_return, Eacc_ratio, benchmk_return_3yr):
    margin = round(Emean_return * (Eacc_ratio - benchmk_return_3yr) * .1, 3)
    return min(margin, Emean_return * .03) if margin > 0 else max(margin, 0)
    
def var_init(sDate, E_init):
    dTime = sDate
    quater_sum = 0
    quater_sumin = 0
    year_sum = 0
    quater_date = []

    alpha = 0
    E = E_init
    E_end = E
    E_acc_end = E
    cf_sum = 0
    # Nt = 12

    cf_occupied = []
    cf_occFund = []
    cfDt_Nt = []
    # Emean_return = []

    return_margin = []
    margin = []
    return_margin2 = []
    margin2 = []
    return_margin3 = []
    margin3 = []
    acc_return = []
    excess_return = []
    upper_limit = []
    return dTime, quater_sum, quater_sumin, year_sum, quater_date, alpha, \
        E, E_end, cf_sum, cf_occupied, cf_occFund, cfDt_Nt, return_margin, margin, return_margin2, margin2, \
        return_margin3, margin3, acc_return, excess_return, upper_limit, E_acc_end


def singIntv_retMargin(df, mode=1, E_init=1e9, rollingYear=1):
    sDate = stamp_to_datetime(df.iloc[0].date)  # 确认开始日期
    eDate = stamp_to_datetime(df.iloc[-1].date)  # 确认结束日期
    subset_yr = get_subset(df, sDate, 1)
    if (sDate.year >= eDate.year - 3 * rollingYear):
        return pd.DataFrame(data=None)

    # Variable Initiation
    Nt = 12
    
    dTime, quater_sum, quater_sumin, year_sum, quater_date, alpha, \
    E, E_end, cf_sum, cf_occupied, cf_occFund, cfDt_Nt, return_margin, \
    margin, return_margin2, margin2, return_margin3, margin3, acc_return, \
    excess_return, upper_limit, E_acc_end = var_init(sDate, E_init)

    i = 0
    while quater_sum < rollingYear * 12 + 1:
        i += 1
        # 遍历日期时间
        dTime = stamp_to_datetime(df.iloc[i].date)
        # 找到日期时间年和月
        y, m, d = dTime.year, dTime.month, dTime.day

        try:
            mNext = stamp_to_datetime(df.iloc[i + 1].date).month
            yNext = stamp_to_datetime(df.iloc[i + 1].date).year
        except IndexError:
            break

        # 季度汇总
        # 每季度汇总
        if m % 3 == 0 and (i > 2) and (mNext == m + 1 or mNext == 1):

            quater_sum += 1
            quater_sumin += 1
            quater_date.append(str(dTime))  # 记录三年内每年每个季度的具体日期
            
            net_cf = 0
            if quater_sum == 1:

                dfq = df[(df["date"] >= sDate) & (df["date"] <= dTime)]
                dfq.reset_index(drop=True, inplace=True)
                startDate = stamp_to_datetime(dfq.iat[-1, 0])
                quater_return = dfq.iat[-1, 3]/dfq.iat[0, 3] - 1
                # E_net = E_end
                E_end = E_end * (1 + quater_return)
                # alpha = ((np.prod(1 + dfq["nv_return"]) - 1) - (np.prod(1 + dfq["hs300_return"]/100) - 1))
                alpha = (dfq.iat[-1, 3]/dfq.iat[0, 3] - 1) - (dfq.iat[-1, 4]/dfq.iat[0, 4] - 1)

            elif quater_sum > 1 and quater_sum < (rollingYear * 12 + 1):

                dfq = df[(df["date"] >= startDate) & (df["date"] <= dTime)]
                startDate = stamp_to_datetime(dfq.iat[-1, 0])
                quater_return = dfq.iat[-1, 3]/dfq.iat[0, 3] - 1
                # E_net = E_end
                E_end = E_end * (1 + quater_return)
                alpha = (quater_return - (dfq.iat[-1, 4]/dfq.iat[0, 4] - 1))
                
            if quater_sum != rollingYear * 12:

                if mode == 1:

                    if alpha > 0 and E_end < 1e10:

                        net_cf = E_end * 0.1
                        E_end += net_cf  # 则加仓5亿
                        cf_sum += net_cf  # 净现金流入

                    # elif keep_value < alpha and E_end > 1e9:  # 否则
                    elif alpha < 0 and E_end > 2e8:

                        net_cf = -E_end * 0.1
                        E_end += net_cf  # 减仓5亿
                        cf_sum += net_cf  # 净现金流出

                elif mode == 2:

                    if alpha > 0 and E_end < 1e10:

                        net_cf = E_end * 0.5
                        E_end += net_cf  # 则加仓5亿
                        # E_net += net_cf
                        cf_sum += net_cf  # 净现金流入

                    # elif keep_value < alpha and E_end > 1e9:  # 否则
                    elif alpha < 0 and E_end > 2e8:

                        net_cf = -E_end * 0.3
                        E_end += net_cf  # 减仓5亿
                        # E_net += net_cf
                        cf_sum += net_cf  # 净现金流出

            # if quater_sum != rollingYear * 12:
            dfq_rest = subset_yr[(subset_yr["date"] >= dTime)]
            dfq_rest.reset_index(drop=True, inplace=True)

            startDate = stamp_to_datetime(dfq.iat[-1, 0])
            # 将现季度超额收益存入alpha变量
            Dt = Nt - quater_sumin  # 第t笔现金流发生日距离考核期末的实际季度数
            # 计算现金流占用期间收益率
            # occ_return = np.prod(1 + dfq_rest["hs300_return"]) - 1
            occ_return = dfq_rest.iat[-2, 4]/dfq_rest.iat[0, 4] - 1
            fund_return = dfq_rest.iat[-2, 3]/dfq_rest.iat[0, 3] - 1
            cf_occupied.append(net_cf * occ_return)  # 现金流×现金流占用期间收益率
            cf_occFund.append(net_cf * fund_return)
            cfDt_Nt.append(net_cf * Dt / Nt)
            

        if (quater_sumin % 12 == 0) and (quater_sumin != 0):

            year_sum += 1

            # df_3yrs = df[(df["date"] >= startDate_3yrs) & (df["date"] <= dTime)]
            fdOper_return = subset_yr.iat[-2, 3] / subset_yr.iat[0, 3] - 1
            Eacc_return = E * fdOper_return + np.sum(cf_occFund)  # 计算期间委托资产累计投资收益
            Emean_return = E + np.sum(cfDt_Nt)  # 期间委托资产平均资金占用
            Eacc_ratio = Eacc_return / Emean_return  # 期间委托资产累计收益率
            benchmk_return_3yr = subset_yr.iat[-2, 4] / subset_yr.iat[0, 4] - 1    # 业绩基准收益率
            alpha_3yrs = fdOper_return - benchmk_return_3yr

            # 算法A
            result1 = method1(subset_yr, E_end, E, cf_sum, cf_occupied, Eacc_return, Emean_return)
            margin.append(result1[0])
            excess_return.append(result1[1])
            upper_limit.append(result1[2])

            # 算法B
            result2 = method2(subset_yr, Emean_return, benchmk_return_3yr)
            margin2.append(result2)

            #算法C
            result3 = method3(Emean_return, Eacc_ratio, benchmk_return_3yr)
            margin3.append(result3)

            E = E_end
            cf_sum = 0
            cf_occupied = []
            cf_occFund = []
            cfDt_Nt = []
            quater_sumin = 0
            startDate_3yrs = dTime
            subset_yr = get_subset(df, dTime, 1)

    return_margin.append(margin)
    return_margin2.append(margin2)
    return_margin3.append(margin3)
    yr_intv = "%s--%s" % (str(sDate)[:10], str(eDate)[:10])

    res = {
        "year": yr_intv,
        "account_code": df["acc_code"].unique()[0],
        "mode": "mode%i" % mode,
        "return_margin": [np.sum(return_margin)],
        "return_margin2": [np.sum(return_margin2)],
        "return_margin3": [np.sum(return_margin3)],
        "E_end": E_end,
        "excess_return": [np.sum(excess_return)],
        "upper_limit": [np.sum(upper_limit)],
        "acc_return": [Eacc_return],
        "Emean_return": [Emean_return]
    }

    return pd.DataFrame(res)
