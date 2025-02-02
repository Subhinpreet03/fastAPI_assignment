from pydantic import BaseModel


class Coin(BaseModel):
    symbol: str
    last_price: float
    price_change_percent: float

    def get_trend(self):
        return "Up" if self.price_change_percent > 0 else "Down"
