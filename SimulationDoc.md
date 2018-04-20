# Stable Unit

Stable Unit (SU) is a digital token designed to maintain a 1:1 peg to the US 
dollar. The system will be fully decentralized, run via smart contract on a 
Bitcoin side chain. Stability is maintained using non-fiat reserves as 
collateral, eventually transitioning from a parity reserve with very low risk 
into a highly liquid system based on bonds as its market grows.

# Price Maintainance Model

Demand for Stable Units is likely to vary widely when the network remains small.
At this stage we keep system risk low by guaranteeing the redemption of Stable 
Units for bitcoin held in reserve at a 1:1 ratio to Stable Units in circulation.

The contract maintains a liquidity around the dollar peg by offering SU to 
sellers and buyers through its main contract. We parametrize this mechanism with
a delta offset from the peg -- buyers can attain SU through the contract at a 
price greater than a dollar, and redeem them through the contract at a price 
lower than a dollar. 

In effect, the contract acts as market maker, which can adjust it's risk by 
adjusting this parameter, also known as a spread. Prices rise and fall 
on the exterior market, but are always bounded by the lowest Bid and highest Ask
that the contract offers. During periods of high volatility, Revenue from this 
bid/ask spread is deposited into Contract's reserve, elevating its value and 
allowing the token contract to expand further at a the same reserve ratio. 

# Reserve Ratio

In the beginning, while the Stable Unit economy is small, the price band 
(spread) surrounding the stable price tight, and the contract fully backed with
a target reserve ratio of 1:1. This effectively shields the contract 
from risk during its early stages. As the market grows however, the bid-ask 
spread is allowed to increases in width, allowing the contract to maintain a 
larger market value but still affording strong protection to the underlying 
reserve. 

# Bond Mechanism

The Bitcoin reserve is it self subject to it's own risk, and the overarching 
goal of the Stable Unit Blockchain is to remove all dependences on secondary 
markets. Because of this, as the system grows, we reduce the dependence of 
Stable Units on reserve backing, and instead, open up a secondary market 
for bonds.

# Simulation Parameters

We simulate the behavior of the Stable Unit contract through two Monte Carlo 
series 1) The price of Bitcoin held in reserve and 2) The Demand for Stable 
Units from the Token contract. 

Updates to the contract state follows a few simple rules. 1) Buying SU from the
contract increases the supply in exchange for Bitcoin. 2) Selling SU at the
contract decreases the supply and is exchanged for Bitcoin. When the ratio 
between SU and BTC held in reserve drop bellow a threshold, then the contract
moves to creating bonds instead of returning BTC. Bonds will be sold at a
premium i.e. 1.5 Bonds per SU using a dutch auction IRL, but for the sake of
this simulation it is 1:1. Bonds yield in the future when the price of SU 
is expanded. 

Note: Monte Carlo Methods are commonly used in 
statistical finance as a means of testing the behaviour of a system under 
differing conditions and open up a means of statistically evaluating the
performance of an asset.  We use a LogNormal distribution to simulate the prices movements for both
the Bitcoin Price and Stable Unit Demand. The long tail towards positive 
infinity and a bound at zeros in this distribution better reflects the demand 
curve for an asset.

The contract is simulated using a static spread of 0.99 - 1.01 and an initial 
1:1 reserve. The reserve target remains as a hyperparameter between trials.

# A Note on the graph.
1) The top graph shows the Bitcoin price.
2) The second graph shows cumulative SU demand over time.
3) The third, BTC reserve (Blue) Bonds circulation (Red) SU market cap (Green).
4) The fourth, BTC value / SU value reserve ratio.


