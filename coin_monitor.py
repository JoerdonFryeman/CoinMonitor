import asyncio
import aiohttp
from configuration import Configuration, error, use_default_colors, init_pair, color_pair


class Connection(Configuration):
    @staticmethod
    def verify_data(data, currency):
        if 'data' in data and 'rates' in data['data']:
            return data['data']['rates'].get(currency)
        return None

    async def get_connection(self, coin: str, currency: str) -> dict | None:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f'{self.api}{coin}') as response:
                    response.raise_for_status()
                    return self.verify_data(await response.json(), currency)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
        return None


class Base(Connection):
    def __init__(self):
        super().__init__()
        self.max_coins_length = 11
        self.max_coins_zero = 10
        self.max_percent_zero = 3
        self.max_percent_length = 8
        self.x_percentage = 4
        self.start_rates = []
        self.previous_rates = []
        self.initial_rates_set = False

    @staticmethod
    def get_x_negative_percent(x, percentage):
        if float(percentage[:len(percentage) - 1]) < 0:
            return x - 1
        return x

    def format_percentage(self, percentage):
        if len(percentage) > self.max_percent_length:
            return f'{percentage[:self.max_percent_length - 4]}..%'
        return percentage

    async def create_coins_list(self, coins: dict) -> list:
        pairs_list = await asyncio.gather(
            *(self.get_connection(coin, currency['currency']) for coin, currency in coins.items()))
        len_pairs_list = len(pairs_list)
        if len_pairs_list > 75:
            raise Exception(f'Превышение максимального количества монет: {len_pairs_list}!')
        return [
            (
                coin, currency['currency'], f'{float(rate):.{self.max_coins_zero}f}'
                if rate is not None else '0.000000000', currency['coin_color'], currency['currency_color']
            )
            for (coin, currency), rate in zip(coins.items(), pairs_list)
        ]

    def get_percentage_difference(self, start_value, final_value) -> str:
        difference = (final_value - start_value) / abs(start_value) * 100
        formatted_difference = f'{difference:.{self.max_percent_zero}f}%'
        return formatted_difference

    def verify_initial_rates(self, rates):
        if not self.initial_rates_set:
            self.start_rates = [float(rate) for _, _, rate, _, _ in rates]
            self.initial_rates_set = True

    def verify_previous_rates(self, rates):
        if len(self.previous_rates) != len(rates):
            self.previous_rates = [0.0] * len(rates)

    def verify_length(self, coin, currency, rate):
        len_currency = len(f'{coin}/{currency}:')
        len_rate = len(f'{rate}')

        def verify_rate_length():
            if len_rate > self.max_coins_length:
                return rate[:len_rate - (len_rate - self.max_coins_length)]
            elif len_rate == self.max_coins_length:
                return rate
            elif len_rate < self.max_coins_length:
                return " " * (self.max_coins_length - len_rate) + rate
            return rate

        if len_currency < self.max_coins_length:
            return " " * (self.max_coins_length - len_currency) + verify_rate_length()
        elif len_currency == self.max_coins_length:
            return verify_rate_length()
        elif len_currency > self.max_coins_length:
            return rate[:(len_rate - (len_rate - self.max_coins_length) - (len_currency - self.max_coins_length))]
        return rate[:self.max_coins_length]


class Visualization(Base):
    def paint(self, color: str) -> object:
        """
        Метод раскрашивает текст или текстовое изображение.

        :param color: Цвет изображения.
        :return: Объект color_pair.
        """
        colors_dict: dict[str, int] = {
            'MAGENTA': 1, 'BLUE': 2, 'CYAN': 3, 'GREEN': 4,
            'YELLOW': 5, 'RED': 6, 'WHITE': 7, 'BLACK': 8
        }
        for i in range(len(list(colors_dict.keys()))):
            use_default_colors(), init_pair(1 + i, self.verify_color(list(colors_dict.keys())[0 + i]), -1)
        return color_pair(colors_dict[color])

    def get_color(self, index, current: float, previous: float) -> str:
        start = self.start_rates[index]
        if current > previous:
            return 'GREEN'
        elif current < previous:
            return 'RED'
        else:
            if current > start:
                return 'GREEN'
            elif current < start:
                return 'RED'
            return 'YELLOW'

    def display_info(self, stdscr):
        try:
            stdscr.addstr(11, 31, 'CoinMonitor (version 1.0.0)', self.paint('GREEN'))
            stdscr.addstr(12, 31, 'https://github.com/JoerdonFryeman/CoinMonitor', self.paint('GREEN'))
            stdscr.addstr(13, 31, 'MIT License, copyright (c) 2025 JoerdonFryeman', self.paint('GREEN'))
        except error:
            pass

    def display_rates(self, stdscr, index, y, x, coin, currency, rate, coin_color, currency_color):
        try:
            stdscr.addstr(index + y, x, str(coin), self.paint(coin_color))
            stdscr.addstr(index + y, len(str(coin)) + x, '/', self.paint(self.marks_color))
            stdscr.addstr(index + y, len(str(coin)) + (x + 1), str(currency), self.paint(currency_color))
            stdscr.addstr(index + y, len(str(coin) + str(currency)) + (x + 1), ':', self.paint(self.marks_color))
            stdscr.addstr(
                index + y, len(coin + currency) + (x + 3), str(self.verify_length(coin, currency, rate)),
                self.paint(self.get_color(index, float(rate), self.previous_rates[index]))
            )
            percentage = self.get_percentage_difference(self.start_rates[index], float(rate))
            stdscr.addstr(
                index + y, x + self.max_coins_length * 2 + self.get_x_negative_percent(self.x_percentage, percentage),
                self.format_percentage(percentage),
                self.paint(self.get_color(index, float(rate), self.previous_rates[index]))
            )
        except ZeroDivisionError:
            self.initial_rates_set = False
        except error:
            pass
