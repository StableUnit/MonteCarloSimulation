import matplotlib.pyplot as plt
import numpy as np

class Params:
    """Params hold a set of hyper parameters relevant to a simulation trial.

    Attributes:
        total_steps (int): The total number of steps per trial.
        initial_reserve_ratio (float): The ratio initial between Ethereum and
            Stable units.
        minimum_reserve_ratio (float): A limit ratio between ETH and SU.
        eth_drift (float): ETH Monte Carlo distribution mean.
        eth_volatility (float): ETH Monte Carlo standard deviation.
        initial_eth_reserve (float): Initial Ethereum reserve size.
        initial_eth_price (float): Initial Ethereum price per unit.
        demand_drift (float): SU Monte Carlo drift in demand.
        demand_volatility (float): SU Monte Carlo std in demand.
    """
    def __init__(self):
        self.total_steps = 100
        self.initial_reserve_ratio = 1.0
        self.minimum_reserve_ratio = 0.05
        self.eth_drift = 0.0
        self.eth_volatility = 0.0
        self.initial_eth_reserve  = 100
        self.initial_eth_price  = 500
        self.demand_drift = -0.001
        self.demand_volatility = 0.001
        self.print_step = True

class State:
    """State holds the current and historical values associated with a trial.

    Attributes:
        steps (list[int]): Step number index.
        eth_reserve (list[float]): Total ETH in reserve at each step.
        eth_prices (list[float]): USD per unit ETH per step.
        eth_reserve_value (list[float]): US dollar value of ETH reserve.
        reserve_ratio (list[float]): ETH reserve value over SU.
        su_cumulative_demand (list[float]): Cumulative density of Stable unit
            demand at each step.
        su_circulation (list[float]): Total SU in circulation per step.
        bond_circulation (list[float]): Total bond pool size per step.
    """
    def __init__(self, params):
        """ Args:
                params (Class): object carrying hyperparams for trial.
        """
        self.steps = [0]
        self.eth_reserve = [params.initial_eth_reserve]
        self.eth_prices =  [params.initial_eth_price]
        self.eth_reserve_value = \
            [params.initial_eth_reserve * params.initial_eth_price]
        self.reserve_ratio = [params.initial_reserve_ratio]
        self.su_cumulative_demand = [0.0]
        self.su_circulation = [params.initial_eth_reserve * \
                params.initial_eth_price * 1 / params.initial_reserve_ratio]
        self.bond_circulation = [0]

    def check_state(self):
        if (self.eth_reserve[-1] < 0 or
            self.su_circulation[-1] < 0 or
            self.bond_circulation[-1] < 0 or
            self.eth_prices[-1] < 0):
            return False
        return True

def plot(state):
    """ Produces a plot of the MCS.
        Args:
            state (Class): Object containing the contract's state through time.
    """
    plt.subplot(4, 1, 1)
    plt.plot(state.steps, state.eth_prices, color="b")
    plt.ylabel('USD / ETH')
    plt.grid(True)

    plt.subplot(4, 1, 2)
    plt.plot(state.steps, state.su_cumulative_demand, color="b")
    plt.ylabel('SU Demand')
    plt.grid(True)

    plt.subplot(4, 1, 3)
    plt.plot(state.steps, state.eth_reserve_value, color="b")
    plt.plot(state.steps, state.su_circulation, color="g")
    plt.plot(state.steps, state.bond_circulation, color="r")
    plt.ylabel('USD')
    plt.grid(True)

    plt.subplot(4, 1, 4)
    plt.plot(state.steps, state.reserve_ratio, color="b")
    plt.ylabel('USD')
    plt.grid(True)

    print ('SU: ', state.su_circulation[-1])
    print ('ETH: ', state.eth_reserve[-1])
    print ('ETHv: ', state.eth_reserve_value[-1])
    print ('R: ', state.reserve_ratio[-1])
    print ('CD: ', state.su_cumulative_demand[-1])

    plt.show()


def do_step(params, state):
    """ Performs a single Monte Carlo Step simulating the state of the contract.
        Args:
            params (Class): Object containing the contract hyperparameters.
            state (Class): Object containing the contract's current state.
    """

    # Ethereum price movement modeled using a log normal distribution.
    eth_demand_delta = np.random.lognormal(params.eth_drift, \
            params.eth_volatility, 1)[0] - 1
    state.eth_prices.append(state.eth_prices[-1] + state.eth_prices[-1] * \
            eth_demand_delta)

    # Change in stable unit demand is modeled using a lognormal distribution.
    # This scews demand in the positive direction towards infinity while
    # bounding the potential demand shock below by zero. This reflects the
    # potential for inifinite buying demand and finite sell pressure.
    su_demand_delta = np.random.lognormal(params.demand_drift, \
            params.demand_volatility, 1)[0] - 1
    state.su_cumulative_demand.append(state.su_cumulative_demand[-1] + \
            su_demand_delta)

    # At each step we model the change in SU circulation with respect to the
    # change in demand.
    circulation_delta = su_demand_delta * state.su_circulation[-1]

    # In the event of an expansion, SU supply is expanded through two processes
    # 1) SU Bonds purchased earlier are redeemed
    # 2) New stable units are minted.
    if circulation_delta >= 0:
        # SU circulation is expanded with demand.
        su_circulation_delta = circulation_delta

        # Bonds purchased earlier are exchanged for ethereum.
        bond_circulation_delta = -min(state.bond_circulation[-1], \
                circulation_delta)

        # The eth reserve is credited with the new sale of stable units.
        eth_reserve_delta = (1 /state.eth_prices[-1]) * (circulation_delta + \
                bond_circulation_delta)

    # If we are contracting and the reserve ratio has dropped bellow it's
    # lower bound the contract issues bonds using a reverse dutch auction.
    # These can be redeemed at a later date for ethereum during expansion.
    elif state.reserve_ratio[-1] < params.minimum_reserve_ratio:
        # Stable units are sold off in exchange for bonds.
        su_circulation_delta = circulation_delta

        # Instead the contract issues bonds which redeem ethereum at a later
        # date.
        bond_circulation_delta = -circulation_delta

        # The ethereum reserve is protected by bond sales.
        eth_reserve_delta = 0

    # In the event of a depression within the reserve ratio bound, the contract
    # buys su in circulation in exchange for ethereum held in reserve.
    else:
        # The stable unit circulation is decreased
        su_circulation_delta = circulation_delta

        bond_circulation_delta = 0

        # The contract buys back stable units at market the rate.
        eth_reserve_delta = (-1) * su_circulation_delta * (1 / state.eth_prices[-1]) *\
                (1 / 0.99)

    # Update primary contract state params.
    state.su_circulation.append(state.su_circulation[-1] + su_circulation_delta)
    state.bond_circulation.append(state.bond_circulation[-1] + \
            bond_circulation_delta)
    state.eth_reserve.append(state.eth_reserve[-1] + eth_reserve_delta)

    # Update secondary and misc params.
    state.eth_reserve_value.append(state.eth_reserve[-1] * state.eth_prices[-1])
    state.reserve_ratio.append(state.eth_reserve_value[-1] / \
            state.su_circulation[-1])
    state.steps.append(state.steps[-1] + 1)

    if params.print_step:
        print(  'step', "%0.0f" % state.steps[-1], \
                'demand_delta',"%0.2f" % circulation_delta, \
                'su_delta', "%0.2f" % su_circulation_delta, \
                'su_total', "%0.2f" % state.su_circulation[-1], \
                'bond_delta', "%0.2f" % bond_circulation_delta, \
                'bond_total', "%0.2f" % state.bond_circulation[-1], \
                'eth_delta', "%0.4f" % eth_reserve_delta, \
                'eth_total', "%0.4f" % state.eth_reserve[-1], \
                'eth_value', "%0.4f" % state.eth_reserve_value[-1], \
                'reserve_ratio', "%0.4f" % state.reserve_ratio[-1])

    if state.check_state() == False:
        parms.print_step = True
        print ('Error in State')
        assert(False)

    return state

def run_trial(params):
    state = State(params)
    for _ in xrange(0, params.total_steps):
        state = do_step(params, state)
    plot(state)

def main():
    run_trial(Params())

if __name__ == "__main__":
    main()
