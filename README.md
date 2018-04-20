## Stable Unit Python Simulation

# Installation
pip install -r requirements.txt

# Running.
python main.py
python main.py --flagfile=tests/su_black_swan.txt 

## Stable Unit

Stable Unit (SU) is a digital token designed to maintain a 1:1 peg to the US 
dollar. The system will be fully decentralized --running via smart contract on a
Bitcoin side chain-- and have its stability maintained using non-fiat reserve. 
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
further at constant reserve ratio. 

# Reserve Ratio

In the beginning, while the Stable Unit economy is small, the price band 
(spread) surrounding the stable price tight and the contract is fully backed
at target reserve ratio of 1:1. This effectively shields the contract 
from risk but limits the possible quantity of Stable Units incirculation.
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
    2) Selling SU at the contract decreases the supply and at the expense of the
        Bitcoin held in reserve. 
    
When the ratio between SU and BTC held in reserve drops below a threshold value
we consider this a failure contract, allowing us to measure and understand the 
inherent risks in the system. However, this is only one stabalization mechanism
being used by the contract, selling bonds, fund parking, and share 
dilution remain as mechanisms for retaining the contract health. 

# A Note on the theory.

Monte Carlo methods are common place in statistical finance. There is no perfect
method for assessing the risk in a system since this will nessecarily 
depend on the behaviour of actions out side the limits of a limited simulation. 

For the purposes of testing the behaviour of a system however, Monte Carlo 
methods serve as usefull way of understanding the system's behaviour under 
differing market conditions.

We use a LogNormal distribution to simulate the prices movements for both
the Bitcoin Price and Stable Unit Demand. The LogNormal distribution has a 
long tail which reaches towards positive infinity while being bounded at zero 
on the other end, this better reflects the demand curve for an asset which can
have infinite demand and only finite sell pressure.

# Method

The contract is simulated using a static spread of 0.99 - 1.01 and an initial 
1:1 reserve. We wish to understand how the system behaves under differing 
conditions for instance, 
    1) A Downward / Upward trending Bitcoin reserve price.
    2) A Downward / Upward trending Stable Unit demand.
    3) High / Low demand volatility for Stable Units.

# A Note on the graph.
1) The top graph shows the Bitcoin price.
2) The second graph shows cumulative SU demand over time.
3) The third, BTC reserve (Blue) Bonds circulation (Red) SU market cap (Green).
4) The fourth, BTC value / SU value reserve ratio.


