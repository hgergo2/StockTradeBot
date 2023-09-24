
class LivePosition:
    def __init__(self, symbol: str, order_type: str, is_active: bool,
                 entry_price: float, entry_date: str, target_price: float,
                 stop_loss: float, mongo_id: int, strategy_name: str):
        #if order_type != 'long' or order_type != 'short': return
        self.symbol = symbol.upper()
        self.order_type = order_type
        self.is_active = is_active
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.target_price = target_price
        self.stop_loss = stop_loss
        self.mongo_id = mongo_id
        self.strategy_name = strategy_name

    def is_position_in_profit(self, current_candle):
        if self.order_type == 'long':
            if current_candle['Close'] > self.entry_price:
                return True
            else:
                return False
        elif self.order_type == 'short':
            if current_candle['Close'] < self.entry_price:
                return True
            else:
                return False
