import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

import Position


class ChartHandlerBacktest:

    def __init__(self, data: [], symbol: str, rangeslider_visible=False, subplot_title=''):
        self.subplot_title = subplot_title
        self.symbol = symbol
        self.data = pd.DataFrame(data)
        if self.subplot_title is '':
            self.chart = make_subplots(rows=1, cols=1)
        else:
            self.chart = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                            vertical_spacing=0.01, subplot_titles=('Chart', subplot_title), row_heights=[0.7, 0.15])
        self.chart.add_trace(
            go.Candlestick(x=self.data.index,
                                 open=self.data['Open'],
                                 high=self.data['High'],
                                 low=self.data['Low'],
                                 close=self.data['Close'],
                                 hovertext=self.data["DateTime"],
                                 name=symbol),
            row=1, col=1
        )
        self.chart.update_layout(xaxis_rangeslider_visible=rangeslider_visible)

    def __remake_chart_with_subplots(self, subplot_title: str, rangeslider_visible=False):
        self.chart = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                   vertical_spacing=0.03, subplot_titles=(' ', subplot_title),
                                   row_heights=[0.85, 0.15])
        self.chart.add_trace(
            go.Candlestick(x=self.data.index,
                           open=self.data['Open'],
                           high=self.data['High'],
                           low=self.data['Low'],
                           close=self.data['Close'],
                           hovertext=self.data["DateTime"],
                           name=self.symbol),
            row=1, col=1
        )
        self.chart.update_layout(xaxis_rangeslider_visible=rangeslider_visible)

    def draw_position(self, position: Position.Position, sell_index: int):
        self.chart.add_shape(
            type='rect',
            x0=position.index, y0=position.buy_price, x1=sell_index, y1=position.target_price,
            line=dict(
                color='green',
                width=1,
            ),
            fillcolor='green',
            opacity=0.4
        )
        self.chart.add_shape(
            type='rect',
            x0=position.index, y0=position.buy_price, x1=sell_index, y1=position.stop_loss,
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
        self.chart.add_trace(go.Scatter(x=self.data.index, y=data, line=dict(color=color, width=width), name=name)
        )

    def add_subplot(self, data: [], type: str, title='', show_legend=False):
        """
        Mindig ezt kell először meghivni moving line előtt
        """
        if self.subplot_title is '':
            if type is 'line':
                if title is '':
                    self.__remake_chart_with_subplots(data.name)
                else:
                    self.__remake_chart_with_subplots(title)
                self.chart.add_trace(go.Line(x=data.index, y=data, showlegend=show_legend), row=2, col=1)
            elif type is 'bar':
                if title is '':
                    self.__remake_chart_with_subplots(data.name)
                else:
                    self.__remake_chart_with_subplots(title)
                self.chart.add_trace(go.Bar(x=data.index, y=data, showlegend=show_legend), row=2, col=1)
        else:
            if type is 'line':
                self.chart.add_trace(go.Line(x=data.index, y=data, showlegend=show_legend), row=2, col=1)
            elif type is 'bar':
                self.chart.add_trace(go.Bar(x=data.index, y=data, showlegend=show_legend), row=2, col=1)



    def add_title(self, text: str):
        self.chart.update_layout(
            title_text=text
        )
