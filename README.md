## Python simulation of Stable Unit

# About this simulation
We run two monte carlo simulations. One of the Ethereum price which is held in
the SU contract reserve. The other is SU demand, measured in quantity being 
bought and sold from the SU contract at each step. Steps length is arbitrary
for this simulation.

Updates to the contract state follows a few simple rules. 1) Buying SU from the
contract increases the supply in exchange for Ethereum. 2) Selling SU at the
contract decreases the supply and is exchanged for Ethereum. When the ratio 
between SU and ETH held in reserve drop bellow a threshold, then the contract
moves to creating bonds instead of returning ETH. Bonds will be sold at a
premium i.e. 1.5 Bonds per SU using a dutch auction IRL, but for the sake of
this simulation it is 1:1. Bonds yield in the future when the price of SU 
is expanded. 

# A Note on the graph.
1) The top graph shows the Ethereum price.
2) The second graph shows cumulative SU demand over time.
3) The third, ETH reserve (Blue) Bonds circulation (Red) SU market cap (Green).
4) The fourth, ETH value / SU value reserve ratio.

# Running the simulation
pip install -r requirments.txt
python main.py
