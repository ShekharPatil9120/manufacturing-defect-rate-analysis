# Manufacturing Defect Rate Statistical Analysis

## Overview
This project analyzes defect rates from a manufacturing line to identify process improvement areas using statistical methods.

## Objectives
- Calculate defect rate, mean, standard deviation, and confidence intervals
- Compare Day and Night production shifts using a t-test
- Visualize process stability using a control chart

## Tools & Technologies
- MS Excel
- Python
- pandas, numpy, scipy, matplotlib

## Project Structure
- `data/` – Raw defect data (Excel)
- `excel/` – Excel analysis with control chart
- `python/` – Python analysis script
- `outputs/` – Generated PDF statistical report
- `screenshots/` – Submission screenshots

## Methodology
1. Defect rate calculated as Defect_Count / Units_Produced
2. Descriptive statistics computed in Excel and Python
3. 95% confidence interval calculated using t-distribution
4. Independent t-test performed to compare Day vs Night shifts
5. Control chart created using ±3σ limits

## Key Findings
- Night shift has a significantly higher defect rate
- p-value < 0.05 indicates statistically significant difference
- Process is generally stable but Night shift needs improvement focus

## How to Run
```bash
pip install -r requirements.txt
python python/analysis.py
