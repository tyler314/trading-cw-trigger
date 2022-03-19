import datetime

from dto.options import VerticalSpread, OptionLeg
from dto.stock import Stock
from tda_api.broker import Broker
from utils.common_utils import (
    transform_ticker,
    TradingPlatforms,
    OrderType,
    Instruction,
    OptionType,
)
import logging
import watchtower

logging.basicConfig(level=logging.ERROR, handlers=[watchtower.CloudWatchLogHandler()])
logger = logging.getLogger(__name__)


class OptionFactory:
    _ROUNDING_PRECISION = 0.05

    def __init__(
        self,
        ticker: str,
        quantity: int,
        order_type: OrderType,
        expiration_date: datetime,
    ):
        self._broker = Broker()
        self.order_type = order_type
        self.stock = Stock(ticker)
        self.quantity = quantity
        self.expiration_date = expiration_date.strftime("%Y-%m-%d")
        (
            self.put_map,
            self.call_map,
        ) = self._get_put_and_call_maps()  # maps strike-price -> metadata

    def get_vertical_spread(
        self, short_leg_strike: float, buying_power: int, option_type: OptionType
    ):
        (short_leg, long_leg,) = self._get_legs_for_vertical_spread(
            short_leg_strike, buying_power, option_type
        )
        price = self._calculate_price_for_vertical_spread(
            option_type, short_leg, long_leg
        )
        return VerticalSpread(
            order_type=self.order_type,
            quantity=self.quantity,
            expiration_date=self.expiration_date,
            short_leg=short_leg,
            long_leg=long_leg,
            price=price,
        )

    def _get_put_and_call_maps(self) -> (dict, dict):
        options = self._broker.option_chain(
            transform_ticker(self.stock.ticker, TradingPlatforms.TDA)
        )
        if options.get("status") == "FAILED":
            msg = "Call to TDA's option chain api failed, with ticker: {}".format(
                self.stock.ticker
            )
            logging.error(msg)
            raise RuntimeError(msg)
        put_exp_map = options["putExpDateMap"]
        call_exp_map = options["callExpDateMap"]
        put_option = None
        call_option = None
        for key in put_exp_map.keys():
            if self.expiration_date == key[: len(self.expiration_date)]:
                put_option = put_exp_map[key]
                break
        for key in call_exp_map.keys():
            if self.expiration_date == key[: len(self.expiration_date)]:
                call_option = call_exp_map[key]
                break
        if not put_option or not call_option:
            msg = "No options available with an expiration date of {}".format(
                self.expiration_date
            )
            logging.error(msg)
            raise RuntimeError(msg)
        return put_option, call_option

    def _get_legs_for_vertical_spread(
        self, rough_strike: float, width: int, option_type: OptionType
    ) -> (OptionLeg, OptionLeg):
        def get_leg(strike: float, instruction: Instruction) -> OptionLeg:
            metadata = {"metadata": ""}
            if option_type == OptionType.CALL:
                metadata = self.call_map[str(strike)][0]
            elif option_type == OptionType.PUT:
                metadata = self.put_map[str(strike)][0]
            return OptionLeg(
                symbol=metadata["symbol"],
                instruction=instruction,
                quantity=self.quantity,
                metadata=metadata,
            )

        def get_long_leg_strike(
            strikes: list, strike_index: int, short_strike: float
        ) -> float:
            if option_type == OptionType.CALL:
                strikes = strikes[strike_index:]
            elif option_type == OptionType.PUT:
                strikes = strikes[: strike_index + 1]
                strikes.reverse()
            else:
                return -1
            prev_strike = strikes[0]
            for strike in strikes:
                if abs(float(strike) - short_strike) >= width / 100:
                    if abs(float(strike) - short_strike) > width / 100:
                        return float(prev_strike)
                    return float(strike)
                prev_strike = strike

        short_leg_strike = -1
        strike_prices = list()
        short_strike_index = -1
        if option_type == OptionType.CALL:
            strike_prices = sorted(self.call_map.keys())
        elif option_type == OptionType.PUT:
            strike_prices = sorted(self.put_map.keys())
        elif option_type == OptionType.NO_OP:
            return -1, -1

        min_diff = float("Inf")
        for i, strike_price in enumerate(strike_prices):
            diff = abs(float(strike_price) - rough_strike)
            if diff < min_diff:
                short_strike_index = i
                min_diff = diff
                short_leg_strike = float(strike_price)
        long_leg_strike = get_long_leg_strike(
            strikes=strike_prices,
            strike_index=short_strike_index,
            short_strike=short_leg_strike,
        )
        if short_leg_strike == long_leg_strike:
            msg = "Vertical spread {} strike prices are the same for both long & short legs: {}".format(
                option_type.name, short_leg_strike
            )
            logging.error(msg)
            print(msg)
        return (
            get_leg(short_leg_strike, Instruction.SELL_TO_OPEN),
            get_leg(long_leg_strike, Instruction.BUY_TO_OPEN),
        )

    def _calculate_price_for_vertical_spread(
        self, option_type: OptionType, short_leg: OptionLeg, long_leg: OptionLeg
    ) -> float:
        if option_type == OptionType.NO_OP:
            return -1
        long_leg_price = (long_leg.metadata["bid"] + long_leg.metadata["ask"]) / 2.0
        short_leg_price = (short_leg.metadata["bid"] + short_leg.metadata["ask"]) / 2.0
        price = (
            int((short_leg_price - long_leg_price) / self._ROUNDING_PRECISION)
            * self._ROUNDING_PRECISION
            + self._ROUNDING_PRECISION
        )
        return round(price, 2)
