# Nami Trading System README

## Overview

This trading system is a ranking system designed to handle strategy development, backtesting, ranking of market instruments, and live trading. It is structured with modularity in mind, allowing easy integration and maintenance of individual components. The system leverages advanced algorithms for evaluating market performance and optimizing trading strategies.

## Folder Structure

### 1. **/strategies**
   - **Purpose**: This folder contains all the strategies used by the system for trading. Each strategy is implemented as a separate Python class or module, allowing flexibility in switching or modifying trading tactics. 
   - **Contents**:  
     - Individual strategy files (e.g., `mean_reversion.py`, `trend_following.py`)
     - Strategy templates for different market conditions or assets.

### 2. **/backtesting**
   - **Purpose**: The backtesting folder includes all the logic related to simulating past market conditions to test how trading strategies would have performed historically. 
   - **Contents**:  
     - **Data handling**: Scripts for preprocessing market data, ensuring it’s in the correct format for backtesting.
     - **Performance metrics**: Metrics to evaluate the strategy’s performance (e.g., Sharpe ratio, win/loss rate).

### 3. **/ranking**
   - **Purpose**: This folder is responsible for evaluating and ranking strategies based on their performance from their. It helps in selecting the most promising strategies for deployment in live trading.
   - **Contents**:  
     - **Ranking algorithms**: Modules for ranking strategies, stocks, or other assets (e.g., `ranker.py`).
     - **Metrics**: Different performance and risk metrics used to rank the strategies (e.g., ROI, volatility, etc.).
     - **Ranking models**: Scripts that incorporate machine learning models or statistical approaches for ranking.

### 4. **/live_trading**
   - **Purpose**: This folder contains the components for live trading execution, interfacing with real-time market data and placing trades. The logic here ensures that the system can run autonomously in a live market environment.
   - **Contents**:  
     - **Real-time data processing**: Scripts for processing incoming live data feeds, such as price changes
     - **Trade management**: Modules for managing open positions, placing stop-losses, take-profits, and executing trades based on the selected strategy.
---

## Installation and Setup

1. Install dependencies:  
   `pip install -r requirements.txt`

---
