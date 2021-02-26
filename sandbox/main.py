#!/usr/bin/env python3

""" Running fund stimulations """

__appname__ = "fund_stimulation.py"
__author__ = 'Jingkai Sun (jingkai.sun20@imperial.ac.uk)'
__version__ = '0.0.1'


import pandas as pd
import numpy as np
import datetime as dt
import warnings
import sys
from datetime import date, timedelta
from mode_function import *

def rolling_start(df_all, fund_code=["161005.OF"], period=2, E = 1e9):


    res = pd.DataFrame(data=None)

    for code in fund_code:
        for yr in range(2006, 2017):
            df = df_all[df_all["acc_code"] == code]
            dfs = get_subset(df, "%i-12-24" % yr, period)
            dfs.reset_index(drop=True, inplace=True)
            row1 = singIntv_retMargin(dfs, mode=1, E_init=E, rollingYear=period)
            row2 = singIntv_retMargin(dfs, mode=2, E_init=E, rollingYear=period)
            res = res.append(row1)
            res = res.append(row2)

    res["ret_exc"] = res["return_margin"]/res["excess_return"]
    res["ret_exc2"] = res["return_margin2"]/res["excess_return"]
    res["ret_exc3"] = res["return_margin3"]/res["excess_return"]
    res["ret_emean"] = res["return_margin"]/res["Emean_return"]
    res["ret_emean2"] = res["return_margin2"]/res["Emean_return"]
    res["ret_emean3"] = res["return_margin3"]/res["Emean_return"]
    res["year2"] = res["year"].apply(lambda x: int(x[:4]) + 1)

    res.to_csv("result/rolling%iyrs.csv" % period, index=False)
    
    print("rolling %i years finished !" % (period * 3))
    
    return res


def main(argv):
    """ main function """
    
    df_all = pd.read_csv("../data/fund_data_all.csv")  # 读取基金数据

    # 转换column types
    df_all["date"] = pd.to_datetime(df_all["date"])
    df_all["acc_code"] = df_all["acc_code"].astype("string")
    df_all["acc_chName"] = df_all["acc_chName"].astype("string")
    df_all["hs300_return"] = df_all["hs300_return"] / 100
    df_all = df_all[["date", "acc_code", "acc_chName", "net_values", "hs300", "hs300_return", "nv_return"]]
    # df_all = df_all[df_all["date"] <= dt.datetime(2020, 1, 6)]
    
    for i in range(1, 4):
        # print(rolling_start(df_all, fund_code=["340006.OF", "163402.OF", "519005.OF", "161005.OF"], period=i, E=1e9))
        print(rolling_start(df_all, fund_code=["161005.OF"], period=2, E=1e9))
    return 0

if __name__ == "__main__":
    status = main(sys.argv)
    sys.exit(status)
    
    



