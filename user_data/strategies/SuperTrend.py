import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import pandas_ta as pta
import freqtrade.vendor.qtpylib.indicators as qtpylib

import pandas_ta as pd_ta

class SuperTrend(IStrategy):

    INTERFACE_VERSION = 2

    # Optimal timeframe for the strategy.
    timeframe = '5m'

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "0": 100
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.10

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = True
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optional order type mapping.
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }
    plot_config = {
        'main_plot': {
            'ST_long': {'color': 'green'},
            'ST_short': {'color': 'red' }
        }
    }
    
    @property
    def plot_config(self):
        return {
            # Main plot indicators (Moving averages, ...)
            'main_plot': {
                'bb_upperband': {'color': 'grey'},
                 'bb_middleband': {'color': 'red'},
                  'bb_lowerband': {'color': 'grey'},
            },
            'subplots': {
                # Subplots - each dict defines one additional plot
                "RSI": {
                    'rsi': {'color': 'blue'},
                    'overbought': {'color': 'red'},
                }
            }
        }

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        periodo = 7
        atr_multiplicador = 3.0
        dataframe['ST_long'] = pd_ta.supertrend(dataframe['high'], dataframe['low'], dataframe['close'],length=periodo,
         multiplier=atr_multiplicador)[f'SUPERTl_{periodo}_{atr_multiplicador}']

        dataframe['ST_short'] = pd_ta.supertrend(dataframe['high'], dataframe['low'], dataframe['close'],length=periodo,
         multiplier=atr_multiplicador)[f'SUPERTs_{periodo}_{atr_multiplicador}']

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
              (dataframe['ST_long'] < dataframe['close']) &
              (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
             (dataframe['ST_long'] > dataframe['close']) &
             (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'sell'] = 1
        return dataframe
    