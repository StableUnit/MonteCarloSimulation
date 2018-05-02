from google.apputils import app
import matplotlib.pyplot as plt
import numpy as np

import gflags
import math

FLAGS = gflags.FLAGS

'''
    This file application runs a Geometric Brownian Motion simulation over
two indices: 1) The bitcoin price, parameterized by a drift and volatility
and 2) Stable Unit demand change, parameterized by a drift and volatility.
Both of these series interact with the state of the underlying contract on
evenly spaced time steps 'delta t'. The contract is initialized with a reserve
of Bitcoin and circulation of outstanding Stable Units (presumably distributed
during a token sale). The reserve holds the Stable Unit pegged to a dollar by
maintaining a highest bid and lowest ask around a 1 USD. As the BTC price
and Stable Unit demand during each simulation, the contract intervenes, selling
Stable Units at the ask price and buying them at the bid price there by hoilding
it's value within these bounds.
'''

# Simulation Paramters.
gflags.DEFINE_integer('total_trials', 1000,
        'The total number of trials per experiment')
gflags.DEFINE_integer('total_steps', 1000,
        'The total number of steps per trial')
gflags.DEFINE_boolean('print_step', False,
        'Logging On or Off.')

# Brownian Motion Parameters.
gflags.DEFINE_float('delta_t', 1.0,
        'GBM time delta')
gflags.DEFINE_float('btc_price_drift', 0.0,
        'BTC Monte Carlo GBM price drift.')
gflags.DEFINE_float('btc_price_volatility', 0.001,
        'BTC Monte Carlo GBM price volatility')
gflags.DEFINE_float('su_demand_drift', 0.0,
        'SU Monte Carlo GBM demand drift.')
gflags.DEFINE_float('su_demand_volatility', 0.001,
        'SU Monte Carlo GBM demand volatility.')

# Contract Parameters.
gflags.DEFINE_float('initial_reserve_ratio', 1.0,
        'the initial ratio between Bitcoin and Stable Units.')
gflags.DEFINE_float('target_reserve_ratio', 1.0,
        'The reserve ratio targeted by the contract')
gflags.DEFINE_float('initial_btc_reserve', 100,
        'Initial amount of BTC held in reserve.')
gflags.DEFINE_float('initial_btc_price', 8000,
        'BTC Initial price.')
gflags.DEFINE_float('lowest_ask', 1.01,
        'The contract spread above the dollar.')
gflags.DEFINE_float('highest_bid', 0.99,
        'The contract spread below the dollar.')
gflags.DEFINE_boolean('do_rebase', False,
        'The contract rebases supply after each step')

class Params:
    """Params hold a set of hyper parameters relevant to a simulation experiment

    Attributes:
        total_steps (int): The total number of steps per trial.
        btc_price_drift (float): BTC Monte Carlo GBM price drift.
        btc_price_volatility (float): BTC Monte Carlo GBM price volatility.
        su_demand_drift (float): SU Monte Carlo GBM demand drift.
        su_demand_volatility (float): SU Monte Carlo std demand volatility.
        initial_reserve_ratio (float): The ratio initial between Bitcoin and
            Stable units.
        target_reserve_ratio (float): The reserve ratio targeted by the contract
        initial_btc_reserve (float): Initial Bitcoin reserve size.
        initial_btc_price (float): Initial Bitcoin price per unit.
        lowest_ask (float): The contract spread above 1 dollar.
        highest_bid (float): The contract spread bellow 1 dollar.
    """
    def __init__(self):
        self.total_steps = FLAGS.total_steps
        self.total_trials = FLAGS.total_trials
        self.delta_t = FLAGS.delta_t
        self.btc_price_drift = FLAGS.btc_price_drift
        self.btc_price_volatility = FLAGS.btc_price_volatility
        self.su_demand_drift = FLAGS.su_demand_drift
        self.su_demand_volatility = FLAGS.su_demand_volatility
        self.initial_reserve_ratio = FLAGS.initial_reserve_ratio
        self.target_reserve_ratio = FLAGS.target_reserve_ratio
        self.initial_btc_reserve  = FLAGS.initial_btc_reserve
        self.initial_btc_price  = FLAGS.initial_btc_price
        self.lowest_ask = FLAGS.lowest_ask
        self.highest_bid = FLAGS.highest_bid
        self.do_rebase = FLAGS.do_rebase
        self.print_step = FLAGS.print_step

    def __str__(self):
        return (' total steps: ' + "%0.2f" % self.total_steps + '\n' + \
                ' total trials: ' + "%0.2f" % self.total_trials + '\n' + \
    ' delta t: ' + "%0.4f" % self.delta_t + '\n' + \
    ' btc price drift: ' + "%0.4f" % self.btc_price_drift + '\n' + \
    ' btc price volatility: ' + "%0.4f" % self.btc_price_volatility + '\n' + \
    ' su demand drift: ' + "%0.4f" % self.su_demand_drift + '\n' + \
    ' su demand volatility: ' + "%0.4f" % self.su_demand_volatility + '\n' + \
    ' initial reserve ratio: '+"%0.4f" % self.initial_reserve_ratio + '\n' + \
    ' initial btc reserve: ' + "%0.4f" % self.initial_btc_reserve + '\n' + \
    ' initial btc price: ' + "%0.4f" % self.initial_btc_price + '\n' + \
    ' lowest ask: ' + "%0.3f" % self.lowest_ask + '\n' + \
    ' highest bid: ' + "%0.3f" % self.highest_bid + '\n' + \
    ' do rebase: ' + str(self.do_rebase) + '\n' + \
    ' print step: ' + str(self.print_step))


class State:
    """State holds the current and historical values associated with a trial.

    Attributes:
        steps (list[int]): Step number index.
        btc_reserve (list[float]): Total BTC in reserve at each step.
        btc_prices (list[float]): USD per unit BTC per step.
        btc_reserve_value (list[float]): US dollar value of BTC reserve.
        reserve_ratio (list[float]): BTC reserve value over SU.
        su_cumulative_demand (list[float]): Cumulative density of Stable unit
            demand at each step.
        su_circulation (list[float]): Total SU in circulation per step.
    """
    def __init__(self, params):
        """ Args:
                params (Class): object carrying hyperparams for experiment.
        """
        self.steps = [0]
        self.btc_reserve = [params.initial_btc_reserve]
        self.btc_prices =  [params.initial_btc_price]
        self.btc_reserve_value = \
            [params.initial_btc_reserve * params.initial_btc_price]
        self.reserve_ratio = [params.initial_reserve_ratio]
        self.su_cumulative_demand = [0.0]
        self.su_circulation = [params.initial_btc_reserve * \
                params.initial_btc_price * 1 / params.initial_reserve_ratio]

    def __str__(self):
        return 'step ' + "%0.0f" % self.steps[-1] +\
               ' su_total ' + "%0.2f" % self.su_circulation[-1] + \
               ' btc_total ' + "%0.4f" % self.btc_reserve[-1] + \
               ' btc_price ' + "%0.4f" % self.btc_prices[-1] + \
               ' btc_value ' + "%0.4f" % self.btc_reserve_value[-1] + \
               ' reserve_ratio ' + "%0.4f" % self.reserve_ratio[-1]

def do_analysis(end_states, params):
    """ Plots the a histogram over the simulation end states.
        Args:
            end_states (list(Class)): List of Object containing the
                contract states after a trial.
            params (Class): Object carrying byperparams for the experiment.
    """
    # Build results.
    reserve_ratio = []
    su_circulation = []
    btc_price = []
    for state in end_states:
        reserve_ratio.append(state.reserve_ratio[-1])
        su_circulation.append((state.su_circulation[-1] - \
                state.su_circulation[0]) / state.su_circulation[0] )
        btc_price.append((state.btc_prices[-1] - \
                state.btc_prices[0]) / state.btc_prices[0])

    # Produce Result Plot
    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 10))
    experiment_string = params.__str__()

    # Plot Params.
    props = dict(boxstyle='round', facecolor='white', alpha=0.0)
    ax1.text(0.05, 0.95, experiment_string, transform=ax1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
    ax1.get_xaxis().set_visible(False)
    ax1.get_yaxis().set_visible(False)
    ax1.axis('off')
    ax1.set_title('Experiment Params')

    # Final Reserve Ratio Histogram.
    ax2.hist(reserve_ratio, bins=int(math.sqrt(params.total_trials)))
    ax2.set_title("Final Reserve Ratio.")

    # Final Stable Circulation.
    ax3.hist(su_circulation, bins=int(math.sqrt(params.total_trials)))
    ax3.set_title("Final Stable Unit Circulation Drift")

    # Final Stable Circulation.
    ax4.hist(btc_price, bins=int(math.sqrt(params.total_trials)))
    ax4.set_title("Final BTC Price Drift")

    plt.show()


def plot(state):
    """ Produces a plot of the MCS.
        Args:
            state (Class): Object containing the contract's state through time.
    """
    # TODO(const) Legend and line types.
    plt.subplot(4, 1, 1)
    plt.plot(state.steps, state.btc_prices, color="b")
    plt.ylabel('USD / BTC')
    plt.grid(True)

    plt.subplot(4, 1, 2)
    plt.plot(state.steps, state.su_cumulative_demand, color="b")
    plt.ylabel('SU Demand')
    plt.grid(True)

    plt.subplot(4, 1, 3)
    plt.plot(state.steps, state.btc_reserve_value, color="b")
    plt.plot(state.steps, state.su_circulation, color="g")
    plt.ylabel('USD')
    plt.grid(True)

    plt.subplot(4, 1, 4)
    plt.plot(state.steps, state.reserve_ratio, color="b")
    plt.ylabel('Reserve Ratio')
    plt.grid(True)

    plt.show()


def do_step(params, state):
    """ Performs a single Monte Carlo Step simulating the state of the contract.
        Args:
            params (Class): Object containing the contract hyperparameters.
            state (Class): Object containing the contract's current state.
    """
    # Produce a Bitcoin price delta using Geometric Brownian motion (GBM).
    btc_price_delta = state.btc_prices[-1] * \
        (params.btc_price_drift * params.delta_t + \
         params.btc_price_volatility * math.sqrt(params.delta_t) * \
         np.random.standard_normal())

    # Next Bitcoin price.
    btc_price = state.btc_prices[-1] + btc_price_delta

    # Produce a Stable Unit demand delta using GBM.
    su_demand_delta = state.su_circulation[-1] * \
            (params.su_demand_drift * params.delta_t + \
             params.su_demand_volatility * math.sqrt(params.delta_t) * \
             np.random.standard_normal())

    # Update the Stable Unit CDF
    su_cumulative_demand = state.su_cumulative_demand[-1] + su_demand_delta

    # At each step we model the change in SU circulation with respect to the
    # change in demand.
    circulation_delta = su_demand_delta

    # Below: Simulate the contract buy-sell behavior outside the spread.
    # SUs are being minted from the smart contract in exchange for Bitcoin.
    if circulation_delta >= 0:
        # SU circulation is expanded with demand.
        su_circulation_delta = circulation_delta

        # The bitcoin reserve is credited with the new sale of stable units.
        btc_reserve_delta = (1 /state.btc_prices[-1]) * circulation_delta * \
                (params.lowest_ask)

    # SUs are being sold to the contract in exchange for Bitcoin.
    else:
        # SU circulation is decreased in response to a loss of demand.
        su_circulation_delta = circulation_delta

        # The contracts reserve is depleted as it buys back stable units.
        btc_reserve_delta =  su_circulation_delta * \
                (1 / state.btc_prices[-1]) * params.highest_bid

    # Updated State Params.
    su_circulation = state.su_circulation[-1] + su_circulation_delta
    btc_reserve = state.btc_reserve[-1] + btc_reserve_delta
    btc_reserve_value = btc_reserve * btc_price
    reserve_ratio = btc_reserve_value / su_circulation

    # If the target reserve ratio pushes above the target. The contract rebases
    # the ratio of Stable Units by splitting units and increasing supply.
    su_rebase_delta = 0
    if params.do_rebase:
        off_factor = (reserve_ratio-params.target_reserve_ratio) / reserve_ratio
        if off_factor > 0:
            su_rebase_delta = su_circulation * (1 + off_factor) - su_circulation
            su_circulation = su_circulation + su_rebase_delta

    # Update the  State.
    state.su_circulation.append(su_circulation)
    state.su_cumulative_demand.append(su_cumulative_demand)
    state.btc_prices.append(btc_price)
    state.btc_reserve.append(btc_reserve)
    state.btc_reserve_value.append(btc_reserve_value)
    state.reserve_ratio.append(reserve_ratio)
    state.steps.append(state.steps[-1] + 1)

    if params.print_step:
        print(  'step', "%0.0f" % state.steps[-1], \
                'su_total', "%0.2f" % su_circulation, \
                'su_demand_delta',"%0.4f" % su_demand_delta, \
                'su_circulation_delta' , "%0.2f" % circulation_delta, \
                'su_delta', "%0.2f" % su_circulation_delta, \
                'su_rebase_delta', "%0.2f" % su_rebase_delta, \
                'btc_total', "%0.4f" % btc_reserve, \
                'btc_price', "%0.4f" % btc_price, \
                'btc_price_delta', "%0.4f" % btc_price_delta, \
                'btc_delta', "%0.4f" % btc_reserve_delta, \
                'btc_value', "%0.4f" % btc_reserve_value, \
                'reserve_ratio', "%0.4f" % reserve_ratio)


    return state

def should_end_trial(params, state):
    if (state.btc_reserve[-1] < 0):
        return True
    elif (state.su_circulation[-1] < 0):
        return True
    elif (state.steps[-1] >= params.total_steps):
        return True
    else:
        return False

def run_trial(params):
    state = State(params)
    while not should_end_trial(params, state):
        state = do_step(params, state)
    return state

def run_experiment(params):
    results = []
    for trial in xrange(0, params.total_trials):
        results.append(run_trial(params))
    do_analysis(results, params)

def main(argv):
    params = Params()
    print ("Experiment Params: " + params.__str__())
    run_experiment(params)

if __name__ == '__main__':
  app.run()
