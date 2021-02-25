#!/usr/bin/env python3

# import packages
import pandas as pd
import numpy as np
import datetime as dt
import warnings
import sys
from datetime import date, timedelta
# from mode_function import *

df_all = pd.read_csv("data/fund_data_all.csv")  # 读取基金数据

# 转换column types
df_all["date"] = pd.to_datetime(df_all["date"])
df_all["date2"] = df_all["date"].copy()
df_all.set_index('date', inplace=True)
df_all["acc_code"] = df_all["acc_code"].astype("string")
df_all["acc_chName"] = df_all["acc_chName"].astype("string")
df_all["hs300_return"] = df_all["hs300_return"] / 100
df_all = df_all[["date2", "acc_code", "acc_chName", "net_values", "hs300", "hs300_return", "nv_return"]]


def get_quarData(df, acc_code, sDate, year, freq="Q", rollingWin=1):
    """ To get subset of whole dataset of differnt time frequency.

    Arguments:
    ===========
    df: whole dataset
    acc_code: Code of the fund
    sDate: Start date of subset data
    freq: date frequency (BM for business month, M for calender month)
    rollingWin: Rolling window of time
    year: starting year

    Returns:
    ===========
    quarterly_df: Dataframe after finishing time frequency modification
    df: Dataframe with original time frequency (Days)
    
     """

    sDate = pd.to_datetime(sDate)
    df = df[df["acc_code"] == acc_code]
    df = df[sDate:]

    def custom_resampler(arr_like):
        if arr_like.dtypes != "float64":
            return arr_like[-1]
        if arr_like.name == "net_values" or arr_like.name == "hs300":
            return np.mean(arr_like)
        if arr_like.name == "hs300_return" or arr_like.name == "nv_return":
            return np.prod(1 + arr_like) - 1

    quarterly_df = df.resample(freq, convention="end").apply(custom_resampler)
    quarterly_df.reset_index(drop=True, inplace=True)
    quarterly_df["alpha"] = quarterly_df.nv_return - quarterly_df.hs300_return
    quarterly_df = get_subset(quarterly_df, "%i-1-1" % year, rollingWin)
    df = get_subset(df, "%i-1-1" % year, rollingWin)
    df.set_index("date2", inplace=True)
    return quarterly_df, df


def get_subset(df, startDate, rollingWin):
    """ function that gets the subset from the whole fund data within given rolling window. 
    
    Arguments:
    ==========
    df: a dataframe with date column
    startDate: start date (String)
    rollingWin: rolling windows (int)
    
    Returns:
    =========
    dfs: sliced subset (DataFrame)

    """
    sDate = pd.to_datetime(startDate)  # 确认开始日期
    eDate = dt.datetime(sDate.year + rollingWin * 3,
                        sDate.month, sDate.day)  # 确认结束日期
    df = df[df["date2"] >= sDate]
    # 筛选出三年数据
    dfs = df[(df["date2"] >= sDate) & (df["date2"] <= eDate)]
    dfs.reset_index(drop=True, inplace=True)
    return dfs


def stamp_to_datetime(timestamp):
    """ function that converts timestamp into datetime type. """
    dDate = dt.datetime(timestamp.year, timestamp.month, timestamp.day)
    return dDate


def method1(df, E_end, E, cf_sum, cf_occupied, Eacc_return, Emean_return):
    """ The first methods computing return margin.

    Arguments:
    ===========
    df: 3yrs dataset with day frequency
    E_end: Equity at the end of term
    E: Equity at the beginning of term
    cf_sum: Sum of Cash Flow
    cf_occupied: Occupied Cash Flow
    Eacc_return: Accumulated Return of Equity 
    Emean_return: Average Return of Equity 
    
    Returns:
    ===========
    return margin (float)

    """

    # 运作期间基准收益率(全阶段) == 业绩基准收益率
    interval_return = np.prod(1 + df["hs300_return"]) - 1
    benchmark_return = E * interval_return + np.sum(cf_occupied)  # 计算期间基准投资收益
    # 基金经理业绩收益
    excess_return = Eacc_return - benchmark_return
    upper_limit = Emean_return * .03
    margin = round((Eacc_return - benchmark_return) * .1, 3)
    return min(margin, Emean_return * .03) if margin > 0 else max(margin, 0), excess_return, upper_limit


def method2(df, Emean_return, benchmk_return_3yr):
    """ The second methods computing return margin.

    Arguments:
    ===========
    df: 3yrs dataset with day frequency
    Emean_return: Average Return of Equity 
    benchmk_return_3yrs: Return of hs300 within 3 years
    
    Returns:
    ===========
    return margin (float)

    """

    # 期间连乘收益率
    intv_prod_return = np.prod(1 + df["nv_return"]) - 1
    margin = round(Emean_return * (intv_prod_return -
                                   benchmk_return_3yr) * .1, 3)
    # return margin
    return min(margin, Emean_return * .03) if margin > 0 else max(margin, 0)


def method3(Emean_return, Eacc_ratio, benchmk_return_3yr):
    """ The third methods computing return margin.

    Arguments:
    ===========
    Emean_return: Average Return of Equity 
    Eacc_ratio: Eacc_return / Emean_return
    benchmk_return_3yrs: Return of hs300 within 3 years
    
    Returns:
    ===========
    return margin (float)

    """

    margin = round(Emean_return * (Eacc_ratio - benchmk_return_3yr) * .1, 3)
    return min(margin, Emean_return * .03) if margin > 0 else max(margin, 0)


def fund_simulation(dfQuar, dfDay, mode=1, Einit=1e9, rollingWin=1, year=2008):
    """ Fund simulation function.

    Arguments:
    ===========
    dfQuar: Datasets with modified time frequency (Quarterly or Monthly) [Dataframe]
    dfDay: Datasets with day time frequency [Dataframe]
    mode: Simulating mode [integer]
    Einit: Initilized Equity [float]
    rollingWin: Rolling window (year) [integer]
    year: Starting year [integer]
    
    Returns:
    ===========
    res: Simulated results with single year [Dataframe]

    """

    E = Einit
    E_end = Einit
    # print("inital E_end", E_end)
    net_cf = 0
    cf_sum = 0

    sDate = "%i-01-01" % year

    num, monthSum, monthTotal = 0, 0, 0
    occ_return, fund_return = 0, 0
    fdOper_return, Eacc_return, Emean_return, Eacc_ratio = 0, 0, 0, 0
    benchmk_return_3yr, alpha_3yrs = 0, 0

    cf_occupied = []
    cf_occFund = []
    cfDt_Nt = []

    return_margin, return_margin2, return_margin3 = [], [], []
    margin, margin2, margin3 = [], [], []
    acc_return, excess_return = [], []
    upper_limit = []

    sDate = pd.to_datetime(sDate)
    y, m, d = sDate.year, sDate.month, sDate.day
    while num < rollingWin:

        dfs = get_subset(dfQuar, "%i-%i-%i" % (y, m, d), 1)
        end_date = stamp_to_datetime(dfs.iat[-1, 0])
        Nt = dfs.shape[0]

        for idx in range(0, dfs.shape[0]):

            monthSum += 1
            monthTotal += 1
            E_end = E_end * (1 + dfs["nv_return"][idx])
            start_date = stamp_to_datetime(dfs["date2"][idx])
            df_rest = dfDay[start_date:end_date]

            # if mode == 1 and (num == 0) or (num > 0 and monthTotal < rollingWin * Nt):
            if mode == 1 and monthTotal < rollingWin * Nt:

                # print("E_end%i: %f" % (idx, E_end))

                if dfs["alpha"][idx] > 0 and E_end < 1e10:

                    net_cf = E_end * 0.1
                    # print("net_cf increased to:", net_cf)
                    E_end += net_cf  # 则加仓5亿
                    # print("E_end increased to:", E_end)
                    cf_sum += net_cf  # 净现金流入

                elif dfs["alpha"][idx] < 0 and E_end > 2e8:

                    net_cf = -(E_end * 0.1)
                    # print("net_cf decreased to:", net_cf)
                    E_end += net_cf  # 减仓5亿
                    # print("E_end decreased to:", E_end)
                    cf_sum += net_cf  # 净现金流出

                else:
                    net_cf = 0
                    cf_sum += net_cf

            elif mode == 2 and monthTotal < rollingWin * Nt:

                if dfs["alpha"][idx] > 0 and E_end < 1e10:

                    net_cf = E_end * 0.5
                    E_end += net_cf  # 则加仓5亿
                    cf_sum += net_cf  # 净现金流入

                elif dfs["alpha"][idx] < 0 and E_end > 2e8:

                    net_cf = -E_end * 0.3
                    E_end += net_cf  # 减仓5亿
                    cf_sum += net_cf  # 净现金流出

                else:
                    net_cf = 0
                    cf_sum += net_cf

            # 将现季度超额收益存入alpha变量
            Dt = Nt - monthSum  # 第t笔现金流发生日距离考核期末的实际季度数
            # 计算现金流占用期间收益率
            occ_return = df_rest.iat[-1, 3]/df_rest.iat[0, 3] - 1
            # print("occ_return%i:" % (monthSum), occ_return)
            fund_return = df_rest.iat[-1, 2]/df_rest.iat[0, 2] - 1
            # print("fund_return%i:" % (monthSum), fund_return)
            cf_occupied.append(net_cf * occ_return)  # 现金流×现金流占用期间收益率
            # print("cf_occupied%i:" % (monthSum), cf_occupied)
            cf_occFund.append(net_cf * fund_return)
            # print("cf_occFund%i:" % (monthSum), cf_occFund)
            cfDt_Nt.append(net_cf * Dt / Nt)

        df_3yrs = dfDay[dt.datetime(y, m, d):end_date]
        fdOper_return = np.prod(1 + df_3yrs["nv_return"]) - 1
        Eacc_return = E * fdOper_return + np.sum(cf_occFund)  # 计算期间委托资产累计投资收益
        Emean_return = E + np.sum(cfDt_Nt)  # 期间委托资产平均资金占用
        Eacc_ratio = Eacc_return / Emean_return  # 期间委托资产累计收益率
        benchmk_return_3yr = np.prod(1 + df_3yrs["hs300_return"]) - 1
        alpha_3yrs = fdOper_return - benchmk_return_3yr

        # 算法A
        result1 = method1(df_3yrs, E_end, E, cf_sum,
                          cf_occupied, Eacc_return, Emean_return)
        # print("result1:", result1)
        margin.append(result1[0])
        excess_return.append(result1[1])
        upper_limit.append(result1[2])

        # 算法B
        result2 = method2(df_3yrs, Emean_return, benchmk_return_3yr)
        # print("result2:", result2)
        margin2.append(result2)

        #算法C
        result3 = method3(Emean_return, Eacc_ratio, benchmk_return_3yr)
        # print("result3:", result3)
        margin3.append(result3)

        E = E_end
        cf_sum = 0
        cf_occupied = []
        cf_occFund = []
        cfDt_Nt = []
        monthSum = 0
        y += 3
        num += 1

    return_margin.append(margin)
    # print("return_margin", return_margin)
    return_margin2.append(margin2)
    # print("return_margin2", return_margin2)
    return_margin3.append(margin3)
    # print("return_margin3", return_margin3)
    yr_intv = str(sDate)[:4]

    res = {
        "year": yr_intv,
        "account_code": dfQuar["acc_code"].unique()[0],
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


def simulation_output(df_all, accCode, sYear, eYear, mode=1, rollingWin=1, freq="Q"):
    
    """ Multiple years of simulated results.
    Arguments:
    ===========
    df_all: original dataset (Dayly dataset) [Dataframe]
    accCode: Fund code
    sYear: Start year of simulation
    eYear: End year of simulation
    mode: Simulation mode [int]
    rollingWin: Rolling Window (yearly) [integer]
    freq: Time frequency of simulation

    Returns:
    =========
    res: Results dataset [Dataframe]
    """

    res = pd.DataFrame(data=None)
    for yr in range(sYear, eYear):
        quar_df, df = get_quarData(
            df_all, accCode, "%i-1-1" % sYear, year=yr, rollingWin=rollingWin, freq=freq)
        row = fund_simulation(quar_df, df, year=yr,
                              mode=mode, rollingWin=rollingWin)
        res = res.append(row)
    return res


simulation_output(df_all, "161005.OF", sYear = 2007, eYear = 2018, mode = 1, rollingWin = 1, freq = "M")
