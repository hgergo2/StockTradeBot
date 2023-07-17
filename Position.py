class Position:
    def __init__(self, is_long: bool, target_price: float, stop_loss: float, index: int, buy_price: float, symbol: str):
        """
        Profit: %
        """
        self.is_long = is_long
        self.target_price = target_price
        self.stop_loss = stop_loss
        self.index = index
        self.buy_price = buy_price
        self.symbol = symbol
        self.trade_length = 0
        self.is_win = False
        self.profit = 0

