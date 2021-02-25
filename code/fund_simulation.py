#!/usr/bin/env python3

# import packages
import pandas as pd
import numpy as np
import datetime as dt
import warnings
import sys
from datetime import date, timedelta
import time


def stamp_to_date(timestamp):
    """ function that converts timestamp into datetime type. """
    dDate = dt.date(timestamp.year, timestamp.month, timestamp.day)
    return dDate


def fund_subset(df, acc_code):
    """ Subset dataset by fund code """
    return df[df["acc_code"] == acc_code]


def get_mean(df):
    """ Group dataset by year"""
    return df.apply(lambda x: np.mean(x) if x.dtype == "float64" else x.unique(), axis=0)


def find_sDate(df, sDate, dateCol="date2"):
    year = int(sDate[:4]) + 1
    sDate = df[:dt.date(year, 1, 1)][dateCol][-1]
    return sDate


def idxToDate(df, dateCol="date", copyName=None):
    """ Set date column as index 
    
    Arguments:
    =========
    df: Dataframe
    dateCol: Name of date column
    copyName: Name of copied date column after seting original one as index (Default None: don't copy new data column after setting index)
    
    """
    if copyName != None:
        df[copyName] = df[dateCol].copy()
        colnames = df.columns[0:-1].to_list()
        colnames.insert(0, copyName)
        df = df[colnames]
    df.set_index(dateCol, inplace=True)
    return df


def idx_to_column(df, dateName="date"):
    """ change datetime from index to column
    
    Arguments:
    =========
    df: Dataframe
    dateName: The column name
    
    """
    df[dateName] = df.index.to_list()
    colnames = df.columns[0:-1].to_list()
    colnames.insert(0, dateName)
    df = df[colnames]
    df.reset_index(drop=True, inplace=True)
    return df


def get_alpha(df, fromStart=False):
    """ Calulating alpha between fund and hs300 index 
    
    Argument:
    =========
    df_changed: Dataframe after time-frequency changed.
    fromStart: calculating alpha from start date
    
    """

    df["alpha"] = df.nv_return - df.hs300_return
    if fromStart == True:
        df["alpha_start"] = [np.nan] * df.shape[0]
        for row in range(1, df.shape[0] - 1):
            df.at[row, "alpha_start"] = (
                df.at[row, "net_values"]/df.at[0, "net_values"] - 1) - (df.at[row, "hs300"]/df.at[0, "hs300"] - 1)
    return df


def get_subset(df, startDate, rollingWin, dateCol="date2", iter=True):
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
    df = df[df[dateCol] >= sDate]
    # 筛选出三年数据
    dfs = df[(df[dateCol] >= sDate) & (df[dateCol] <= eDate)]
    dfs.reset_index(drop=True, inplace=True)
    last_idx = dfs.index[-1]
    first_idx = dfs.index[0]

    if dateCol != None and iter == True:
        #         while df[dateCol][-1] != dfs[dateCol][-1]:
        while last_idx < df.index[-1]:

            lastRow = dfs[dateCol][last_idx]
#             print("get_subset:", df[dateCol][0].month)
            if lastRow.month == df[dateCol][0].month:
                break

            dfs = dfs.append(df[(last_idx+1):(last_idx+2)])
            last_idx += 1

    return dfs


def randCol_generator(df, seed=None):
    if seed != None:
        np.random.seed(seed)
    df["rand_num"] = np.random.uniform(0, 1, df.shape[0])
    df["rand_num"] = df["rand_num"].apply(lambda x: 1 if x > 0.5 else -1)
    return df


def timeFreq_adjust(df, sDate, freq="Q", reset_idx=True):
    """ To get subset of whole dataset of differnt time frequency.

    Arguments:
    ===========
    df: whole dataset
    year: Start year of subset data
    freq: date frequency (BM for business month, M for calender month)
    reset_idx: True or False

    Returns:
    ===========
    quarterly_df: Dataframe after finishing time frequency modification
    
    """

    sDate = pd.to_datetime(
        sDate) if sDate != None else stamp_to_date(df["date2"][0])
    df = df[sDate:]

    def custom_resampler(arr_like):
        if arr_like.dtypes != "float64":
            return arr_like[-1]
        if arr_like.name == "net_values" or arr_like.name == "hs300":
            return arr_like[-1]
        if arr_like.name == "hs300_return" or arr_like.name == "nv_return":
            return np.prod(1 + arr_like) - 1

    df_changed = df.resample(freq, convention="end").apply(custom_resampler)
    df_changed.reset_index(drop=True, inplace=True)

    if reset_idx == False:
        df_changed.set_index(dateCol, inplace=True)

    return df_changed


def timeFreq_expand(df_origin, df_adjusted=None, time_expand=1, toStart=True, toEnd=False):
    """ Expand datasets with day time frequency
    
    Argument:
    =========
    df_origin: Dataframe before time-frequency adjusted.
    df_adjusted: Dataframe after time-frequency adjusted.
    time_expand: The number of time frequency interval to be expanded.
    toStart: True or False, if need to expand to the start of the dataset.
    toEnd: True or False, if need to expand the dataset backwards.
    
    Return:
    ==========
    df_expanded: Expanded Dataframe
    
    """

    if df_adjusted.index.dtype != "datetime64[ns]":
        df_adjusted.set_index("date2", inplace=True)

    if toStart == True:
        sDate = stamp_to_date(df_origin.index[0])
        eDate = stamp_to_date(df_adjusted.index[time_expand - 1])
    else:
        if time_expand == 1:
            sDate = stamp_to_date(df_origin.index[0])
            print(sDate)
            eDate = stamp_to_date(df_adjusted.index[time_expand - 1])
            print(eDate)
        else:
            sDate = stamp_to_date(
                df_adjusted.index[time_expand - 2]) + timedelta(days=1)
            print(sDate)
            eDate = stamp_to_date(df_adjusted.index[time_expand - 1])
            print(eDate)

    return df_origin[sDate:eDate] if toEnd == False else df_origin[eDate + timedelta(days=1):]


def simulation_start(df_origin, df_changed, random=True, alpha_start=False, Einit=1e9, rollingWin=1, year=2008, changeAmt=[0.1, 0.1], dateCol="date2"):
    """ Fund simulation function.

    Arguments:
    ===========
    df_origin: Datasets with modified time frequency (Quarterly or Monthly) [Dataframe]
    df_changed: Datasets with day time frequency [Dataframe]
    mode: Simulating mode [integer]
    Einit: Initilized Equity [float]
    rollingWin: Rolling window (year) [integer]
    year: Starting year [integer]
    
    Returns:
    ===========
    res: Simulated results with single year [Dataframe]

    """

    # Variable Initiation
    E = Einit
    E_end = Einit
    # print("inital E_end", E_end)
    net_cf = 0
    cf_sum = 0

    sDate = "%i-1-1" % (int(year))

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

    ### Inner functions ###
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
        benchmark_return = E * interval_return + \
            np.sum(cf_occupied)  # 计算期间基准投资收益
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

        margin = round(Emean_return * (Eacc_ratio -
                                       benchmk_return_3yr) * .1, 3)
        return min(margin, Emean_return * .03) if margin > 0 else max(margin, 0)

    # Simulation Start
    sDate = pd.to_datetime(sDate)
    y, m, d = sDate.year, sDate.month, sDate.day
    while num < rollingWin:

        dfs = get_subset(df_changed, "%i-%i-%i" %
                         (y, m, d), 1, dateCol, iter=False)
        end_date = stamp_to_date(dfs.iat[-1, 0])
        Nt = dfs.shape[0]

        for idx in range(0, dfs.shape[0]):

            monthSum += 1
            monthTotal += 1
            E_end = E_end * (1 + dfs["nv_return"][idx])
            start_date = stamp_to_date(dfs["date2"][idx])
            df_rest = df_origin[start_date:end_date]

            def E_adjustment(amount=[E_end * 0.1,  -E_end * 0.1], Elimit=[1e10, 2e8], idx=idx, E_end=E_end, cf_sum=cf_sum):
                """ Define rule of rule of equity increase/decrease """
                if dfs["alpha"][idx] > 0 and E_end < Elimit[0]:

                    net_cf = amount[0]
                    # print("net_cf increased to:", net_cf)
                    E_end += net_cf
                    # print("E_end increased to:", E_end)
                    cf_sum += net_cf  # 净现金流入

                elif dfs["alpha"][idx] < 0 and E_end > Elimit[1]:

                    net_cf = amount[1]
                    # print("net_cf decreased to:", net_cf)
                    E_end += net_cf
                    # print("E_end decreased to:", E_end)
                    cf_sum += net_cf  # 净现金流出

                else:
                    net_cf = 0
                    cf_sum += net_cf

                return E_end, net_cf, cf_sum

            def E_adjustment_random(amount=[E_end * 0.1,  -E_end * 0.1], Elimit=[1e10, 2e8], alpha_start=True,
                                    idx=idx, E_end=E_end, cf_sum=cf_sum):
                """ Define rule of rule of equity increase/decrease """
                net_cf = 0
                if alpha_start == True:

                    if dfs["rand_num"][idx] == 1 and ~np.isnan(dfs["alpha_start"][idx]) and dfs["alpha_start"][idx] >= 0 and E_end < Elimit[0]:

                        net_cf = amount[0]
                        # print("net_cf increased to:", net_cf)
                        E_end += net_cf
                        # print("E_end increased to:", E_end)
                        cf_sum += net_cf  # 净现金流入

                if alpha_start == False:

                    if dfs["rand_num"][idx] == 1 and E_end < Elimit[0]:
                        net_cf = amount[0]
                        # print("net_cf increased to:", net_cf)
                        E_end += net_cf
                        # print("E_end increased to:", E_end)
                        cf_sum += net_cf  # 净现金流入

                if dfs["rand_num"][idx] == -1 and E_end > Elimit[1]:

                    net_cf = amount[1]
                    # print("net_cf decreased to:", net_cf)
                    E_end += net_cf
                    # print("E_end decreased to:", E_end)
                    cf_sum += net_cf  # 净现金流出

                return E_end, net_cf, cf_sum

            # Mode set-up
            if random == False and monthTotal < rollingWin * Nt:

                E_end, net_cf, cf_sum = E_adjustment(amount=[E_end * changeAmt[0], -E_end * changeAmt[1]],
                                                     Elimit=[1e10, 2e8])

            if random == True:

                if alpha_start == False and monthTotal < rollingWin * Nt:
                    E_end, net_cf, cf_sum = E_adjustment_random(amount=[E_end * changeAmt[0], -E_end * changeAmt[1]],
                                                                Elimit=[
                                                                    1e10, 2e8],
                                                                alpha_start=False)

                if alpha_start == True and monthTotal < rollingWin * Nt:
                    E_end, net_cf, cf_sum = E_adjustment_random(amount=[E_end * changeAmt[0], -E_end * changeAmt[1]],
                                                                Elimit=[
                                                                    1e10, 2e8],
                                                                alpha_start=True)

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

        df_3yrs = df_origin[dt.datetime(y, m, d):end_date]
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

    if alpha_start == True:
        mode = "Random_with_alpha"
    elif alpha_start == False:
        mode = "Random_without_alpha"

    if random == False:
        mode = "non-Random"

    res = {
        "year": yr_intv,
        "account_code": df_changed["acc_code"].unique()[0],
        "mode":  mode,
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


def get_first_freq_summary(df, sDate, acc_code, rollingPeriods, freq, Einit, dateCol="date2"):

    df_selected = fund_subset(df, acc_code)  # Subset specified subset
    sDate = find_sDate(df_selected, sDate, dateCol)

    # Get time-frequecy adjusted dataset
    df_changed = timeFreq_adjust(
        df_selected, sDate=sDate, freq=freq, reset_idx=True)
    # calculating alpha and alpha (from start) columns for adjusted dateset
    df_changed = get_alpha(df_changed, fromStart=True)
    df_changed = get_subset(df_changed, str(df_changed.at[0, dateCol])[
                            :10], rollingWin=rollingPeriods, dateCol=dateCol)

    # get original subset based on adjusted subset
    df_origin = timeFreq_expand(
        df_selected, df_changed, time_expand=df_changed.shape[0], toStart=True)
    df_origin = df_origin[pd.to_datetime(sDate):]
    # delete date column
    df_origin = df_origin[df_origin.columns.to_list()[1:]]

    # Change datatime from index to column
    df_changed = idx_to_column(df_changed, "date2")
    df_changed = df_changed.dropna()
    df_changed.reset_index(drop=True, inplace=True)
    df_origin = df_origin[1:]

    return df_origin, df_changed


def simulation_output(df, changeAmt, year=(2007, 2010), acc_code="161005.OF", Einit=1e9, rollingPeriods=1, mode=1, freq="Q", dateCol="date2"):
    """ Multiple years of simulated results.
    Arguments:
    ===========
    df_all: original dataset (Dayly dataset) [Dataframe]
    acc_code: Fund code
    year: List or tuple [int(start year), int(end year)]
    mode: Simulation mode [int]
    rollingWin: Rolling Window (yearly) [integer]
    freq: Time frequency of simulation

    Returns:
    =========
    res: Results dataset [Dataframe]
    """

    res = pd.DataFrame(data=None)
#     print(type(year) == int)
    if type(year) == int:
        condition = range(year, year + 1)
    else:
        condition = range(year[0], year[1])

    len_sum = None
    for yr in condition:

        df_origin, df_changed = get_first_freq_summary(
            df, "%i-%i-%i" % (yr-1, 12, 23), acc_code, rollingPeriods, freq, Einit)
        if (df_changed.shape[0] != len_sum) and (len_sum != None):
            break
        len_sum = df_changed.shape[0]
        row = simulation_start(df_origin, df_changed, year=yr,
                               random=False, rollingWin=rollingPeriods,
                               Einit=Einit, changeAmt=changeAmt, dateCol="date2")  # fund simulation
        res = res.append(row)
    res.reset_index(drop=True, inplace=True)
    return res


def multi_simu_output(df, yr, acc_code, rollingPeriods, freq, alpha_start, Einit, rep_times, changeAmt, verbose=False, dateCol="date2"):

    def process_bar(percent, start_str='', end_str='', total_length=0):
        bar = ''.join(["\033[1;30m%s" % '=='] *
                      int(percent * total_length)) + ''
        bar = '\r' + start_str + \
            bar.ljust(total_length) + \
            ' {:0>4.1f}%|'.format(percent*100) + end_str
        print(bar, end='', flush=True)
#         print("/n")
        return None

    randNum = 0
    rand_res = pd.DataFrame(data=None)
    while randNum < rep_times:

        df_origin, df_changed = get_first_freq_summary(
            df, "%i-%i-%i" % (yr-1, 12, 23), acc_code, rollingPeriods, freq, Einit, dateCol)
        df_changed = randCol_generator(df_changed)

        if verbose == True:
            display(df_changed)

        row = simulation_start(df_origin, df_changed, year=yr, rollingWin=rollingPeriods, Einit=Einit,
                               alpha_start=alpha_start, random=True, changeAmt=changeAmt, dateCol=dateCol)

        rand_res = rand_res.append(row)
        randNum += 1

        time.sleep(0.1)
        end_str = '100%'
        process_bar(randNum/rep_times, start_str='',
                    end_str=end_str, total_length=12)

    print(" ", sep="/r")
    rand_res.reset_index(drop=True, inplace=True)
    return rand_res


def simulation_repeat(df, year, acc_code, changeAmt, rollingPeriods, freq, alpha_start, Einit, rep_times):

    if type(year) == int:
        condition = range(year, year + 1)
    else:
        condition = range(year[0], year[1])

    res = pd.DataFrame(data=None)
    for yr in condition:
        row = multi_simu_output(df=df, yr=yr, acc_code=acc_code, changeAmt=changeAmt,
                                rollingPeriods=rollingPeriods, freq=freq, alpha_start=alpha_start, Einit=Einit,
                                rep_times=rep_times)
        row = get_mean(row)
        res = res.append(row)
    # clear()
    res.reset_index(drop=True, inplace=True)
    return res

df_all = pd.read_csv("data/fund_data_all.csv")  # 读取基金数据
# 转换column types
df_all["date"] = pd.to_datetime(df_all["date"])
df_all["acc_code"] = df_all["acc_code"].astype("string")
df_all["acc_chName"] = df_all["acc_chName"].astype("string")
df_all["hs300_return"] = df_all["hs300_return"] / 100
df_all["date2"] = df_all["date"].copy()
df_all = df_all[["date", "acc_code", "acc_chName", "net_values", "hs300", "hs300_return", "nv_return"]];
df_all = idxToDate(df_all, dateCol = "date", copyName = "date2")

# print(get_first_freq_summary(df_all, "2017-12-25", "161005.OF", 1, "M", 1e9)[1])

# print(simulation_output(df = df_all, year = [2007, 2020], acc_code = "161005.OF", changeAmt = [0.1, 0.1],
#                         rollingPeriods = 3, freq = "Q", Einit = 1e9))

print(simulation_repeat(df_all, [2007, 2018], "161005.OF",[0.1, 0.1], 1, "M", False, 1e9, 20))
