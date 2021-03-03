#!/bin/bash

# Author: Jingkai Sun
# Script: job_submit.sh
# Desc: Submission Commends for High Performance Computing at Imperial College London
# Arguments: none
# Date: Jan 2021

#PBS -l walltime=30:00:00
#PBS -l select=1:ncpus=1:mem=1gb
#PBS -J 1-48

module load anaconda3/personal
source activate python_prj

echo "Python is about to run"
python main.py

echo "Python has finished running"