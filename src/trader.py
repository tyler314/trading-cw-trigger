from strategies.strategy import Strategy


class Trader:
    def __init__(self):
        self.strategies: list[Strategy] = []

    def set_strategies(self, *strategies: Strategy) -> None:
        self.strategies = [strategy for strategy in strategies]

    def trade(self) -> list:
        logs = []
        for strategy in self.strategies:
            try:
                log = strategy.execute()
            except Exception as e:
                log = e
            logs.append(log)
        return logs
