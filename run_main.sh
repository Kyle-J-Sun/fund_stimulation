#!/bin/bash

echo "Starting to run stimulations..."
python3 code/main.py
echo "Stimulation Finished! Starting to analyse stimulated result..."
Rscript code/fund_analysis.R
echo "Fund Analysis Finished!"