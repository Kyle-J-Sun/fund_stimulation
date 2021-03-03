# import packages
import pandas as pd
import numpy as np
import datetime as dt
import warnings
import sys
import os
from datetime import date, timedelta
import time
# from IPython.display import clear_output as clear
from simulation_functions import *

def main(argvs):
    
    df_all = pd.read_csv("fund_data_all.csv")  # 读取基金数据

    # 转换column types
    df_all["date"] = pd.to_datetime(df_all["date"])
    df_all["acc_code"] = df_all["acc_code"].astype("string")
    df_all["acc_chName"] = df_all["acc_chName"].astype("string")
    df_all["hs300_return"] = df_all["hs300_return"] / 100
    df_all["date2"] = df_all["date"].copy()
    df_all = df_all[["date", "acc_code", "acc_chName",
                    "net_values", "hs300", "hs300_return", "nv_return"]]
    df_all = idxToDate(df_all, dateCol="date", copyName="date2")
    
    
    rollingPeriod_vec = [1, 2, 3]
    amt_vec = [[0.1,0.1], [0.5,0.3]]
    mode_vec = [True, False]
    acc_code = list(df_all["acc_code"].unique())
    print(acc_code)
    start = time.time()
    
    # Parallel Computing
    # ite = int(os.environ['PBS_ARRAY_INDEX'])
    ite = 48
    # for ite in range(1,13):
    if ite == 1:
        period = rollingPeriod_vec[0]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[0]; print(fund)
    if ite == 2:
        period = rollingPeriod_vec[1]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[0]
    if ite == 3:
        period = rollingPeriod_vec[2]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[0]
    if ite == 4:
        period = rollingPeriod_vec[0]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[0]
    if ite == 5:
        period = rollingPeriod_vec[1]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[0]
    if ite == 6:
        period = rollingPeriod_vec[2]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[0]
    if ite == 7:
        period = rollingPeriod_vec[0]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[0]
    if ite == 8:
        period = rollingPeriod_vec[1]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[0]
    if ite == 9:
        period = rollingPeriod_vec[2]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[0]
    if ite == 10:
        period = rollingPeriod_vec[0]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[0]
    if ite == 11:
        period = rollingPeriod_vec[1]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[0]
    if ite == 12:
        period = rollingPeriod_vec[2]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[0]
    
    if ite == 13:
        period = rollingPeriod_vec[0]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[1]
    if ite == 14:
        period = rollingPeriod_vec[1]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[1]
    if ite == 15:
        period = rollingPeriod_vec[2]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[1]
    if ite == 16:
        period = rollingPeriod_vec[0]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[1]
    if ite == 17:
        period = rollingPeriod_vec[1]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[1]
    if ite == 18:
        period = rollingPeriod_vec[2]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[1]
    if ite == 19:
        period = rollingPeriod_vec[0]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[1]
    if ite == 20:
        period = rollingPeriod_vec[1]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[1]
    if ite == 21:
        period = rollingPeriod_vec[2]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[1]
    if ite == 22:
        period = rollingPeriod_vec[0]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[1]
    if ite == 23:
        period = rollingPeriod_vec[1]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[1]
    if ite == 24:
        period = rollingPeriod_vec[2]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[1]
        
    if ite == 25:
        period = rollingPeriod_vec[0]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[2]
    if ite == 26:
        period = rollingPeriod_vec[1]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[2]
    if ite == 27:
        period = rollingPeriod_vec[2]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[2]
    if ite == 28:
        period = rollingPeriod_vec[0]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[2]
    if ite == 29:
        period = rollingPeriod_vec[1]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[2]
    if ite == 30:
        period = rollingPeriod_vec[2]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[2]
    if ite == 31:
        period = rollingPeriod_vec[0]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[2]
    if ite == 32:
        period = rollingPeriod_vec[1]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[2]
    if ite == 33:
        period = rollingPeriod_vec[2]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[2]
    if ite == 34:
        period = rollingPeriod_vec[0]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[2]
    if ite == 35:
        period = rollingPeriod_vec[1]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[2]
    if ite == 36:
        period = rollingPeriod_vec[2]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[2]
        
    if ite == 37:
        period = rollingPeriod_vec[0]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[3]
    if ite == 38:
        period = rollingPeriod_vec[1]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[3]
    if ite == 39:
        period = rollingPeriod_vec[2]
        amt = amt_vec[0]
        mode = mode_vec[0]
        fund = acc_code[3]
    if ite == 40:
        period = rollingPeriod_vec[0]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[3]
    if ite == 41:
        period = rollingPeriod_vec[1]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[3]
    if ite == 42:
        period = rollingPeriod_vec[2]
        amt = amt_vec[0]
        mode = mode_vec[1]
        fund = acc_code[3]
    if ite == 43:
        period = rollingPeriod_vec[0]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[3]
    if ite == 44:
        period = rollingPeriod_vec[1]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[3]
    if ite == 45:
        period = rollingPeriod_vec[2]
        amt = amt_vec[1]
        mode = mode_vec[0]
        fund = acc_code[3]
    if ite == 46:
        period = rollingPeriod_vec[0]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[3]
    if ite == 47:
        period = rollingPeriod_vec[1]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[3]
    if ite == 48:
        period = rollingPeriod_vec[2]
        amt = amt_vec[1]
        mode = mode_vec[1]
        fund = acc_code[3]

    # np.seed(ite)
    simulation_repeat(df_all, [2007, 2020], [fund,], amt, period, "M", mode, Einit=1e9,
                    rep_times=10000, verbose=False, seed=None, outputPath="random_%s_alpha%s_rolling%iyears_%i_%i.csv" % (fund, mode,period,amt[0]*100,amt[1]*100))

    print("This program takes %s minutes to run." % ((time.time() - start)/60))
    
    return 0

if __name__ == "__main__":
    status = main(sys.argv)
    sys.exit(status)
