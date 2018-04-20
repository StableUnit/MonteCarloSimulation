from google.apputils import app
import matplotlib.pyplot as plt
import numpy as np

import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_integer('total_steps', 100,
        'The total number of steps per trial')
gflags.DEFINE_float('initial_reserve_ratio', 1.0,
        'the initial ratio between Bitcoin and Stable Units.')
gflags.DEFINE_float('target_reserve_ratio', 1.0,
        'The reserve ratio targeted by the contract')
gflags.DEFINE_float('btc_drift', 0.0,
        'BTC Monte Carlo mean')
gflags.DEFINE_float('btc_volatility', 0.001,
        'BTC Monte Carlo mean.')
gflags.DEFINE_float('initial_btc_reserve', 100,
        'Initial amount of BTC held in reserve.')
gflags.DEFINE_float('initial_btc_price', 8000,
        'BTC Initial price.')
gflags.DEFINE_float('demand_drift', 0.001,
        'SU Monte Carlo drift in demand.')
gflags.DEFINE_float('demand_volatility', 0.0001,
        'SU Monte Calro standard deviation.')
gflags.DEFINE_float('lowest_ask', 1.01,
        'The contract spread above the dollar.')
gflags.DEFINE_float('highest_bid', 0.99,
        'The contract spread below the dollar.')
gflags.DEFINE_boolean('print_step', True,
        'Logging On or Off.')

class Params:
    """Params hold a set of hyper parameters relevant to a simulation trial.

    Attributes:
        total_steps (int): The total number of steps per trial.
        initial_reserve_ratio (float): The ratio initial between Bitcoin and
            Stable units.
        target_reserve_ratio (float): The reserve ratio targeted by the contract
        btc_drift (float): BTC Monte Carlo distribution mean.
        btc_volatility (float): BTC Monte Carlo standard deviation.
        initial_btc_reserve (float): Initial Bitcoin reserve size.
        initial_btc_price (float): Initial Bitcoin price per unit.
        demand_drift (float): SU Monte Carlo drift in demand.
        demand_volatility (float): SU Monte Carlo std in demand.
        lowest_ask (float): The contract spread above 1 dollar.
        highest_bid (float): The contract spread bellow 1 dollar.
    """
    def __init__(self):
        self.total_steps = FLAGS.total_steps
        self.initial_reserve_ratio = FLAGS.initial_reserve_ratio
        self.target_reserve_ratio = FLAGS.target_reserve_ratio
        self.btc_drift = FLAGS.btc_drift
        self.btc_volatility = FLAGS.btc_volatility
        self.initial_btc_reserve  = FLAGS.initial_btc_reserve
        self.initial_btc_price  = FLAGS.initial_btc_price
        self.demand_drift = FLAGS.demand_drift
        self.demand_volatility = FLAGS.demand_volatility
        self.lowest_ask = FLAGS.lowest_ask
        self.highest_bid = FLAGS.highest_bid
        self.print_step = FLAGS.print_step



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
                params (Class): object carrying hyperparams for trial.
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

    def check_state(self):
        if (self.btc_reserve[-1] < 0 or
            self.su_circulation[-1] < 0 or
            self.btc_prices[-1] < 0):
            return False
        return True

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

    print ('SU: ', state.su_circulation[-1])
    print ('BTC: ', state.btc_reserve[-1])
    print ('BTCv: ', state.btc_reserve_value[-1])
    print ('R: ', state.reserve_ratio[-1])
    print ('CD: ', state.su_cumulative_demand[-1])

    plt.show()


def do_step(params, state):
    """ Performs a single Monte Carlo Step simulating the state of the contract.
        Args:
            params (Class): Object containing the contract hyperparameters.
            state (Class): Object containing the contract's current state.
    """
    # Determine the Bitcoin demand delta.
    btc_demand_delta = np.random.lognormal(params.btc_drift, \
            params.btc_volatility, 1)[0] - 1

    # Update the Bitcoin Price.
    btc_price = state.btc_prices[-1] + state.btc_prices[-1] * btc_demand_delta

    # Determine the Stable unit demand delta.
    su_demand_delta = np.random.lognormal(params.demand_drift, \
            params.demand_volatility, 1)[0] - 1

    # Update the Stable Unit CDF
    su_cumulative_demand = state.su_cumulative_demand[-1] + su_demand_delta

    # At each step we model the change in SU circulation with respect to the
    # change in demand: dSU = dD * SU.
    # TODO(const) Model demand brake from arbitragers in secondary markets.
    circulation_delta = su_demand_delta * state.su_circulation[-1]

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
        btc_reserve_delta = (-1) * su_circulation_delta * \
                (1 / state.btc_prices[-1]) * (1 / params.highest_bid)


    # Updated State Params.
    su_circulation = state.su_circulation[-1] + su_circulation_delta
    btc_reserve = state.btc_reserve[-1] + btc_reserve_delta
    btc_reserve_value = btc_reserve * btc_price
    reserve_ratio = btc_reserve_value / su_circulation

    # Here we will rebase the Stable Unit supply in response to reserve ratio
    # increase above some threshold. This is payed directly to token holders
    # through direct increases in account values.
    off_factor = (reserve_ratio - params.target_reserve_ratio) / reserve_ratio
    if off_factor > 0:
        su_circulation = su_circulation * (1 + off_factor)
        su_circulation_delta = su_circulation - state.su_circulation[-1]

    # Update State.
    state.su_circulation.append(su_circulation)
    state.su_cumulative_demand.append(su_cumulative_demand)
    state.btc_prices.append(btc_price)
    state.btc_reserve.append(btc_reserve)
    state.btc_reserve_value.append(state.btc_reserve_value)
    state.reserve_ratio.append(reserve_ratio)
    state.steps.append(state.steps[-1] + 1)

    if params.print_step or state.steps[-1] == params.total_steps:
        print(  'step', "%0.0f" % state.steps[-1], \
                'su_total', "%0.2f" % su_circulation, \
                'demand_delta',"%0.2f" % circulation_delta, \
                'su_delta', "%0.2f" % su_circulation_delta, \
                'btc_total', "%0.4f" % btc_reserve, \
                'btc_delta', "%0.4f" % btc_reserve_delta, \
                'btc_value', "%0.4f" % btc_reserve_value, \
                'reserve_ratio', "%0.4f" % reserve_ratio)

    if state.check_state() == False:
        print ('Error in State')
        assert(False)

    return state

def run_trial(params):
    state = State(params)
    for _ in xrange(0, params.total_steps):
        state = do_step(params, state)
    plot(state)

def main(argv):
    run_trial(Params())

if __name__ == '__main__':
  app.run()
