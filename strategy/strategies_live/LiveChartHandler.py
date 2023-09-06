import plotly.graph_objects as go
from plotly.subplots import make_subplots
from strategies_live import Position_live
import pandas as pd


def get_index_by_date(data, date, start=0):
    for i in range(start, len(data)):
        if str(data.loc[i]['DateTime']) == str(date):
            return i
    return 0  # Ha nincs benne akkor a dátum a legrégebbi candle előtti


class LiveChart:
    def __init__(self, symbol, timeframe, data, create_subplot=False, subplot_title=''):
        self.chart = make_subplots(rows=1, cols=1)
        self.symbol = symbol
        self.timeframe = timeframe
        self.position = None
        self.has_subplot = create_subplot
        self.subplot_title = subplot_title
        if not create_subplot:
            self.chart.add_trace(
                go.Candlestick(x=data.index,
                               open=data['Open'],
                               high=data['High'],
                               low=data['Low'],
                               close=data['Close'],
                               hovertext=data['DateTime'],
                               name=f'{symbol}{timeframe}'),
                row=1, col=1
            )
        else:
            self.chart = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                       vertical_spacing=0.03, subplot_titles=subplot_title,
                                       row_heights=[0.85, 0.15])
            self.chart.add_trace(
                go.Candlestick(x=data.index,
                               open=data['Open'],
                               high=data['High'],
                               low=data['Low'],
                               close=data['Close'],
                               hovertext=data['DateTime'],
                               name=f'{symbol}{timeframe}'),
                row=1, col=1
            )

        self.chart.update_layout(xaxis_rangeslider_visible=False, width=1800, height=880)

    def add_subplot_data(self, data: [], graph_type: str, color='blue', show_legend=False):
        if not self.has_subplot: return

        if graph_type == 'line':
            self.chart.add_trace(go.Line(x=data.index, y=data, showlegend=show_legend, line=dict(color=color)),
                                 row=2, col=1)
        elif graph_type == 'bar':
            self.chart.add_trace(go.Bar(x=data.index, y=data, showlegend=show_legend, marker_color=color),
                                 row=2, col=1)

    def update_chart(self, data):
        self.chart = None
        if not self.has_subplot:
            self.chart = make_subplots(rows=1, cols=1)
            self.chart.add_trace(
                go.Candlestick(x=data.index,
                               open=data['Open'],
                               high=data['High'],
                               low=data['Low'],
                               close=data['Close'],
                               hovertext=data['DateTime'],
                               name=f'{self.symbol}{self.timeframe}'),
                row=1, col=1
            )
        else:
            self.chart = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                       vertical_spacing=0.03, subplot_titles=self.subplot_title,
                                       row_heights=[0.85, 0.15])
            self.chart.add_trace(
                go.Candlestick(x=data.index,
                               open=data['Open'],
                               high=data['High'],
                               low=data['Low'],
                               close=data['Close'],
                               hovertext=data['DateTime'],
                               name=f'{self.symbol}{self.timeframe}'),
                row=1, col=1
            )

        current_candle = data.tail(1)
        if self.position is not None:
            if self.position.stop_loss is None:
                self.__draw_position(self.position, data, draw_target=True)
        self.__draw_position(self.position, data)
        self.chart.update_layout(xaxis_rangeslider_visible=False, width=1800, height=880, showlegend=False)

    def __draw_position(self, position: Position_live.LivePosition, data, draw_target=True, draw_stop_loss=True):
        if self.position is None: return  # Ha nincs aktiv position akkor nincs mit rajzolni
        self.position = position
        start = get_index_by_date(data, self.position.entry_date)
        current_candle = data.iloc[len(data)-1]
        target_price = self.position.target_price
        stop_loss = self.position.stop_loss

        if target_price is None:
            if self.position.is_position_in_profit(current_candle):
                target_price = current_candle['Close']
            else:
                target_price = self.position.entry_price
        if stop_loss is None:
            if self.position.is_position_in_profit(current_candle):
                stop_loss = self.position.entry_price
            else:
                stop_loss = current_candle['Close']

        self.chart.add_shape(
            type='rect',
            x0=start, y0=position.entry_price, x1=data.loc[len(data) - 1].name, y1=target_price,
            line=dict(
                color='green',
                width=1,
            ),
            fillcolor='green',
            opacity=0.4
        )

        self.chart.add_shape(
            type='rect',
            x0=start, y0=position.entry_price, x1=data.loc[len(data) - 1].name, y1=stop_loss,
            line=dict(
                color='red',
                width=1,
            ),
            fillcolor='red',
            opacity=0.4
        )
        self.chart.update()

    def add_moving_line(self, data: [], color: str, width: int, name: str):
        """
        Ha van subplot akkor előbb azt kell meghívni
        """
        self.chart.add_trace(go.Scatter(x=data.index.values, y=data, line=dict(color=color, width=width), name=name)
                             )

    def draw_rectangle(self, start_x, start_y, end_x, end_y, color='blue', width=1, fillcolor='blue', opacity=0.4):
        self.chart.add_shape(
            type='rect',
            x0=start_x, y0=start_y, x1=end_x, y1=end_y,
            line=dict(
                color=color,
                width=width,
            ),
            fillcolor=fillcolor,
            opacity=opacity
        )
        self.chart.update()


