# Market Analysis

A set of Jupyter Notebooks analyzing the crypto markets. Generally useful for identifying trends in data, and finding undervalued projects based on derived metrics.

## Bitcoin Market Analysis

Understanding market cycles using basic mathematics is a fun exercise. Here we use simple geometric progressions on the length of Bitcoin bull and bear 
cycles to estimate the length of future cycles. This simple model is able to accurately predict a 26 month bull cycle peaking in April 2021, followed 
by a 3 month bear cycle. It further predicts 10 month bull cycle ending in **July 2022**, after which the model starts predicting a bear cycle length tending to 0.

We speculate that the bear cycle length is likely due to the failure of the model. 
However, if this is not the case, then possibly a large event has led to hyperbitcoinization, leading to only bull cycles. 
Given the nature of the geometric progression however, this will not last forever, and the bull cycle length will also tend to 0 with time.

The full analysis is in the Jupyter Notebook [here](https://github.com/dineshpinto/market_analysis/blob/main/notebooks/BitcoinGeometricProgression.ipynb)

## Project Valuation
Finding undervalued projects based on metrics such as fully diluted valuation, current valuation and percent since ATH.

The full analysis is in the Jupyter Notebook [here](https://github.com/dineshpinto/market_analysis/blob/main/notebooks/ProjectValuation.ipynb)


## Installation
1. Create the conda environment from file
   + ```conda env create --file conda-env.yml```
2. Activate environment 
   + ```conda activate market_analytics```
3. Add environment to Jupyter kernel 
    + ```python -m ipykernel install --name=market_analytics```
4. Install jupyter lab extensions for plotly 
   + ```jupyter labextension install jupyterlab-plotly```
5. Explore the various Jupyterlab Notebooks under `notebooks/`


### Export conda environment
```conda env export --no-builds | grep -v "^prefix: " > conda-env.yml```

## Disclaimer
This project is only for educational purposes, always do your own research before making any investment decisions.
