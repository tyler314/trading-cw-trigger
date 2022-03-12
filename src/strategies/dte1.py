import datetime

from pytz import timezone

from dto.options import VerticalSpread
from strategies.strategy import Strategy
from tda_api.broker import Broker
from utils.common_utils import OrderType, OptionType, AssetType, OptionLeg, Instruction


class Dte1(Strategy):
    CALL_ATR_MULTIPLIER = 1
    PUT_ATR_MULTIPLIER = 1
    _ROUNDING_PRECISION = 0.05
    _DTE = 1

    def __init__(
        self,
        ticker: str = "SPX",
        order_type: OrderType = OrderType.CREDIT,
        buying_power: int = 500,
        monday_quantity: int = 1,
        wednesday_quantity: int = 1,
        friday_quantity: int = 1,
    ):
        self._broker = Broker()
        self._buying_power = buying_power
        self._vs = VerticalSpread(
            ticker, self._get_quantity(), order_type, self._get_expiration_date()
        )
        self._option_type = self._get_option_type()
        (
            self._short_leg_strike,
            self._long_leg_strike,
        ) = self._calc_short_and_long_leg_strikes()
        self._long_leg = self._get_long_leg()
        self._short_leg = self._get_short_leg()
        self._price = self._calculate_price()
        self._monday_quantity = monday_quantity
        self._wednesday_quantity = wednesday_quantity
        self._friday_quantity = friday_quantity

    def execute(self) -> dict:
        response = {"code": "bad", "order_body": "Null"}
        if self._option_type != OptionType.NO_OP:
            response = self._broker.place_option_spread_order(
                order_type=self._vs.order_type,
                price=self._price,
                asset_type=self.asset_type,
                long_leg=self._long_leg,
                short_leg=self._short_leg,
            )
        return response

    @property
    def asset_type(self) -> AssetType:
        return AssetType.OPTION

    def _get_quantity(self) -> int:
        if self._is_friday():
            return self._monday_quantity
        elif self._is_tuesday():
            return self._wednesday_quantity
        elif self._is_thursday():
            return self._friday_quantity
        return 1

    @property
    def _adjusted_atr_multiplier(self) -> float:
        multiplier = 0
        if self._option_type == OptionType.CALL:
            green_cnt = self._get_consecutive_green_days()
            multiplier = self.CALL_ATR_MULTIPLIER
            if green_cnt == 0:
                multiplier += 0.8
            elif green_cnt == 1:
                multiplier += 0.6
            elif green_cnt == 2:
                multiplier += 0.2
            elif green_cnt == 3:
                multiplier += 0.1
            elif green_cnt == 4:
                multiplier += 0.1
        elif self._option_type == OptionType.PUT:
            red_cnt = self._get_consecutive_red_days()
            multiplier = self.PUT_ATR_MULTIPLIER
            if red_cnt == 0:
                multiplier += 1.
            elif red_cnt == 1:
                multiplier += 0.8
            elif red_cnt == 2:
                multiplier += 0.4
            elif red_cnt == 3:
                multiplier += 0.3
            elif red_cnt == 4:
                multiplier += 0.0
        return multiplier

    @property
    def _dte(self) -> int:
        if self._is_friday():
            return self._DTE + 2
        return self._DTE

    def _get_short_leg(self) -> OptionLeg:
        metadata = {"metadata": ""}
        if self._option_type == OptionType.CALL:
            metadata = self._vs.call_map[str(self._short_leg_strike)][0]
        elif self._option_type == OptionType.PUT:
            metadata = self._vs.put_map[str(self._short_leg_strike)][0]
        return OptionLeg(
            symbol=metadata["symbol"],
            instruction=Instruction.SELL_TO_OPEN,
            quantity=self._vs.quantity,
            metadata=metadata,
        )

    def _get_long_leg(self) -> OptionLeg:
        metadata = {"metadata": ""}
        if self._option_type == OptionType.CALL:
            metadata = self._vs.call_map[str(self._long_leg_strike)][0]
        if self._option_type == OptionType.PUT:
            metadata = self._vs.put_map[str(self._long_leg_strike)][0]
        self._long_leg = OptionLeg(
            symbol=metadata["symbol"],
            instruction=Instruction.BUY_TO_OPEN,
            quantity=self._vs.quantity,
            metadata=metadata,
        )
        return self._long_leg

    def _get_expiration_date(self) -> datetime:
        day = datetime.datetime.now(timezone("US/Eastern")) + datetime.timedelta(
            hours=24 * self._dte
        )
        return day  # "2022-02-28"

    def _calculate_price(self) -> float:
        if self._option_type == OptionType.NO_OP:
            return -1
        long_leg_price = (
            self._long_leg.metadata["bid"] + self._long_leg.metadata["ask"]
        ) / 2.0
        short_leg_price = (
            self._short_leg.metadata["bid"] + self._short_leg.metadata["ask"]
        ) / 2.0
        price = (
            int((short_leg_price - long_leg_price) / self._ROUNDING_PRECISION)
            * self._ROUNDING_PRECISION
            + self._ROUNDING_PRECISION
        )
        return round(price, 2)

    def _get_consecutive_red_days(self):
        cnt = 0
        while self._vs.stock.candles[cnt].close < self._vs.stock.candles[cnt].open:
            cnt += 1
        return cnt

    def _get_consecutive_green_days(self):
        cnt = 0
        while self._vs.stock.candles[cnt].open < self._vs.stock.candles[cnt].close:
            cnt += 1
        return cnt

    def _get_option_type(self):
        if self._get_consecutive_green_days() > 0:
            return OptionType.CALL
        elif self._get_consecutive_red_days() > 0:
            return OptionType.PUT
        return OptionType.NO_OP

    def _calc_short_and_long_leg_strikes(self) -> (float, float):
        def get_long_leg_strike(
            strikes: list, strike_index: int, short_strike: float
        ) -> float:
            if self._option_type == OptionType.CALL:
                for j in range(strike_index + 1, len(strikes)):
                    if (
                        abs(float(strikes[j]) - short_strike)
                        >= self._buying_power / 100
                    ):
                        if (
                            abs(float(strikes[j]) - short_strike)
                            > self._buying_power / 100
                        ):
                            return float(strike_prices[j - 1])
                        return float(strike_prices[j])
            elif self._option_type == OptionType.PUT:
                for j in range(strike_index - 1, -1, -1):
                    if (
                        abs(float(strikes[j]) - short_strike)
                        >= self._buying_power / 100
                    ):
                        if (
                            abs(float(strikes[j]) - short_strike)
                            > self._buying_power / 100
                        ):
                            return float(strike_prices[j + 1])
                        return float(strike_prices[j])
            return -1

        short_leg_strike = -1
        rough_strike = -1
        strike_prices = list()
        short_strike_index = -1
        if self._option_type == OptionType.CALL:
            rough_strike = (
                self._vs.stock.candles[0].close
                + self._vs.stock.atr * self._adjusted_atr_multiplier
            )
            strike_prices = sorted(self._vs.call_map.keys())
        elif self._option_type == OptionType.PUT:
            rough_strike = (
                self._vs.stock.candles[0].close
                - self._vs.stock.atr * self._adjusted_atr_multiplier
            )
            strike_prices = sorted(self._vs.put_map.keys())
        elif self._option_type == OptionType.NO_OP:
            return -1, -1

        min_diff = float("Inf")
        for i, strike in enumerate(strike_prices):
            diff = abs(float(strike) - rough_strike)
            if diff < min_diff:
                short_strike_index = i
                min_diff = diff
                short_leg_strike = float(strike)

        return (
            short_leg_strike,
            get_long_leg_strike(
                strikes=strike_prices,
                strike_index=short_strike_index,
                short_strike=short_leg_strike,
            ),
        )
