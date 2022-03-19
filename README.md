# Market Analysis

A set of Jupyter Notebooks analyzing the crypto markets. Generally useful for identifying trends in data, and finding undervalued projects based on derived metrics.

## Orderbook Delta
Counter trade the volume delta (bid - ask) on the BTC-PERP pair. Based on the principle of mean reversion, long/short entries are determined by a large standard deviation in the volume delta at orderbook depth 0. 

The full analysis is in the Jupyter Notebook [here](notebooks/OrderbookDeltaAnalyzer.ipynb)

Interactive image [here](images/orderbook_delta_analyzer.html) (may need to be downloaded as GitHub limits hosted file size)

![orderbook_delta_analyzer.png](images/orderbook_delta_analyzer.png)


## Bitcoin Market Analysis

Understanding market cycles using basic mathematics is a fun exercise. Here we use simple geometric progressions on the length of Bitcoin bull and bear 
cycles to estimate the length of future cycles. This simple model is able to accurately predict a 26 month bull cycle peaking in April 2021, followed 
by a 3 month bear cycle. It further predicts 10 month bull cycle ending in **July 2022**, after which the model starts predicting a bear cycle length tending to 0.

We speculate that the bear cycle length is likely due to the failure of the model. 
However, if this is not the case, then possibly a large event has led to hyperbitcoinization, leading to only bull cycles. 
Given the nature of the geometric progression however, this will not last forever, and the bull cycle length will also tend to 0 with time.

The full analysis is in the Jupyter Notebook [here](notebooks/BitcoinGeometricProgression.ipynb)


![BLX_2021-12-29_14-32-48_ba615.png](images/BLX_2021-12-29_14-32-48_ba615.png)

## Project Valuation
Finding undervalued projects based on metrics such as fully diluted valuation, current valuation and percent since ATH.

The full analysis is in the Jupyter Notebook [here](notebooks/ProjectValuation.ipynb)


## Installation
1. Create the conda environment from file
```
conda env create --file conda-env.yml
```
3. Activate environment 
```shell
conda activate market_analytics
```
4. Add environment to Jupyter kernel 
```shell
python -m ipykernel install --name=market_analytics
```
5. Install jupyter lab extensions for plotly 
```shell
jupyter labextension install jupyterlab-plotly
```
6. Explore the various Jupyterlab Notebooks under `notebooks/`


### Export conda environment
```shell
conda env export --no-builds | grep -v "^prefix: " > conda-env.yml
```

## Disclaimer
This project is only for educational purposes, always do your own research before making any investment decisions.
