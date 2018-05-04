## Stable Unit Python Simulation

# Installation
pip install -r requirements.txt

# Running.
python main.py
python main.py --flagfile=tests/su_black_swan.txt 

## Stable Unit

Stable Unit (SU) is a digital token designed to maintain a 1:1 peg to the US 
dollar. The system will be fully decentralized --running via smart contract on a
Bitcoin side chain-- and have its stability maintained using a non-fiat reserve.
The contract begins with a market cap which is fully collateralized by its 
Bitcoin reserve but eventually transitions into a highly liquid system dependent
on bonds as its market grows.

# Price Maintainance Model

Demand for Stable Units is likely to vary widely when the network is small.
At this stage we keep the system risk low by guaranteeing the redemption of 
Stable Units for bitcoin held in reserve at a 1:1 ratio.

The contract maintains liquidity around the dollar peg by offering SU to 
sellers and buyers through its main contract. We parametrize this mechanism with
a delta offset from the peg -- buyers can attain SU through the contract at a 
price greater than a dollar and redeem them through the contract at a price 
lower than a dollar. 

In effect, the contract acts as a market maker, which can adjust it's risk by 
adjusting the spread between the lowest bid and highest ask. As prices rise and
fall on the exterior market the contract profits. During periods of high 
volatility, revenue from this bid/ask spread is deposited into contract's 
reserve, elevating its value and allowing the token contract to expand 
further at a constant reserve ratio. 

# Reserve Ratio

In the beginning, while the Stable Unit economy is small, the price band 
(spread) surrounding the stable price is tight and the contract is fully backed
at target reserve ratio of 1:1. This effectively shields the contract 
from risk but limits the possible quantity of Stable Units in incirculation.
As the market grows however, the reserve ratio decreases and the the bid-ask 
spread is allowed to increases in width. In effect the contract can maintain a 
larger market value while still affording strong protection to the underlying 
reserve. 

# Bond Mechanism

This mechanism itself has risks which is why we employ additional stabalization 
mechanisms which come into play once the first stop gap has been broken. 
Although these methods are not tested here, the real contract will employ 
selling of bonds, fund parking, and share dilution to maintain the contract 
health. 

The Bitcoin reserve is itself subject to it's own risk, and the overarching 
goal of the Stable Unit token is to remove all dependences on secondary 
markets. Because of this, as the system grows, we reduce the dependence of 
Stable Units on reserve backing, and instead, open up a secondary market 
for bonds.

# Simulation Parameters

We simulate the behaviour of this contract useing two non-correlated Geometric 
Brownian Motion timeseries: 
1) The Bitcoin price and,
2) The demand for Stable Units on exterior markets.

# Bitcoin Price

The first of these series, the bitcoin price, is required in this simulation 
because it is being held by the contract reserve --used as the method of 
exchange. It's price with respect to the pegged, i.e the BTC/USD, must be 
derived using oracles to determine the bid and ask prices offered by the 
contract.

We use the standard GBM model with gaussian Wiener process. At each step we 
derive the next price using the following GBM step rule:

    dS_{t}=\mu S_{t}\,dt+\sigma S_{t}\,dW_{t}

Additional random walk distributions such as fractional Brownian motion (fBm)
could be used intead of this simple gaussian Wiener process. For simplicity we
use this model parameterized by it's dt, sigma and mu. Choices for these 
parameters are made by fitting this motion to the historical bitcoin price 
movement. We can additionally select mu (its drift term) to match either an 
upward or downward trend in the Bitcoin price. 

# Stable Unit Demand

Unlike the Bitcoin price, we model the Stable Unit demand, which  reflects the 
quantity of Stable Units being demanded on exterior markets. This is more 
relevant to the contract behaviour because it must engage with exterior markets 
by buying and selling Stable Units are the contract bid and ask prices. 

Again we use the standard GBM model and a gaussian Wiener process to model 
demand changes.

# The Contract.
The two motions interact with the contract according to the following rules:

1) When the Stable Unit demand increases on exterior markets, this reflects
a price drop which increases above the lowest ask price offered by the contract.
Traders sell Stable Units on exchanges and buy more from the contract to 
equalize the price.
    
2) When the demand for Stable Units drop on exterior markets the price drops 
bellow the highest bid offered by the contract. Traders buy Stable Units on 
exchanges and sell them to the contract to bring the price up.  
    
When the ratio between SU and BTC held in reserve drops below a threshold value
we consider this a failure. By running multiple trials and evalutating the 
outcomes statististically, we can probabilistically measure the risks to 
the system.

# Method.

Monte Carlo methods are common place tools in statistical finance which allow 
researchers to make empirical estimations of systemic risk, under specific 
assumptions about the movement and relationships between key system components.

In our case, Risk to Stable Unit system contract can be understood as the 
likelyhood of undesirable results occuring. We derive estimates of this risk
through repeatedly simulating the behaviour of the contract and recording 
results. Aggregations of these samples give us an outcome distribution from
which we can derive statistics over possible outcomes. For instance, 
'Given our assumptions about the behaviour of the Bitcoin price, and Stable 
Unit demand, there is a 90% chance that the contract reserve ratio will remain 
above above 0.5 within a years time.

It should be noted that there is no perfect method for assessing the risk to 
financial instruments. Financial data it notorious random and subject to black 
swan events as a consquence of price distributions which are long tailed and 
unknown. For the purposes of testing the behaviour of this system, however, 
Monte Carlo methods serve as usefull way of understanding the different 
dynamics that may appear and making rough estimations of risk.

# Results.




