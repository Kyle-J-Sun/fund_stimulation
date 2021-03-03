#!/bin/bash

# Author: Jingkai Sun
# Script: run_main.sh
# Desc: Integration of python and R scripts
# Arguments: none
# Date: Jan 2021

echo "Starting to run stimulations..."
python3 code/main.py
echo "Stimulation Finished! Starting to analyse stimulated result..."
Rscript code/fund_analysis.R
echo "Fund Analysis Finished!"