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

In effect, the contract acts as market maker, which can adjust it's risk by 
adjusting the spread between the lowest bid and highest ask. As prices rise and
fall on the exterior market the contract profits. During periods of high 
volatility, revenue from this bid/ask spread is deposited into contract's 
reserve, elevating its value and allowing the token contract to expand 
further at a constant reserve ratio. 

# Reserve Ratio

In the beginning, while the Stable Unit economy is small, the price band 
(spread) surrounding the stable price tight and the contract is fully backed
at target reserve ratio of 1:1. This effectively shields the contract 
from risk but limits the possible quantity of Stable Units in incirculation.
As the market grows however, the reserve ratio decreases and the the bid-ask 
spread is allowed to increases in width. In effect the contract can maintain a 
larger market value while still affording strong protection to the underlying 
reserve. 

# Bond Mechanism

The Bitcoin reserve is itself subject to it's own risk, and the overarching 
goal of the Stable Unit token is to remove all dependences on secondary 
markets. Because of this, as the system grows, we reduce the dependence of 
Stable Units on reserve backing, and instead, open up a secondary market 
for bonds.

# Simulation Parameters

We simulate the behavior of the Stable Unit contract through two Monte Carlo 
series: 
    1) The price of Bitcoin held in reserve and 
    2) The Demand for Stable Units from the Token contract. 

Updates to the contract state follows a few simple rules. 
    1) Buying SU from the contract increases the supply in exchange for Bitcoin.
    2) Selling SU at the contract decreases the supply at the expense of the
        Bitcoin held in reserve. 
    
When the ratio between SU and BTC held in reserve drops below a threshold value
we consider this a failure contract, allowing us to probabilistically measure 
and understand the inherent risks in the system.

This mechanism itself has risks which is why we employ additional stabalization 
mechanisms which come into play once the first stop gap has been broken. 
Although these methods are not tested here, the real contract will employ 
selling of bonds, fund parking, and share dilution to maintain the contract 
health. 

# A Note on the theory.

Geometric Brownian motion Monte Carlo methods are common place in statistical 
finance since they allow us to make empirical estimations of risk bounds in the 
system under certain assumptions about the movement of the underlying assets. 
This is achieved repeated simulation of the contract under the movement from a
statistical 
We can use these empirical results to make statements such as 'There is a 90%
chance that the contract reserve ratio will remain above above 0.5 within the
year under these reasonable assumptions'

It should be noted that there is no perfect method for assessing the risk here 
because financial data it notorious random, subject to black swan events, 
and long trail distributions. However, for the purposes of testing the behaviour
of this system, Monte Carlo methods serve as usefull way of understanding the 
different dynamics that may appear.

# Method

We use a two non-correlated Geometric Brownian Motion timeseries over the 
bitcoin price and Stable Unit demand. The demand for Stable Units during 
downturns in the Bitcoin price suggest that these two series should be
anti-correlated but this caveat has been left out. We parametrize both GBM
series with a drift and volatility term. We vary these parameters to simulate
the behaviour during a number of market conditions two show how the system
reacts.

The contract is parameterized using, 'highest_bid', 'lowest_ask', and 
'initial_reserve_ratio': The higest bid is the rate the contract offers to redeem
Stable Units for bitcoin. The lowest ask is the rate the contract offers to sell
Stable Units for bitcoin. The initial reserve ratio being the ratio between 
Bitcoin and Stable Units at contract genesis.

# Experiments





