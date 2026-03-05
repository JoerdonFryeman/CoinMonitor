import os
import asyncio
import aiohttp

from .visualisation import error, Visualisation


class Connection(Visualisation):

    @staticmethod
    def _verify_data(data: dict, currency: str) -> float | None:
        """Проверяет наличие данных и возвращает курс валюты, если он доступен."""
        if 'data' in data and 'rates' in data['data']:
            return data['data']['rates'].get(currency)
        return None

    async def get_connection(self, coin: str, currency: str) -> dict | None:
        """Получает данные о курсе указанной криптовалюты в заданной валюте."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f'{self.api}{coin}') as response:
                    response.raise_for_status()
                    return self._verify_data(await response.json(), currency)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None
        except Exception as e:
            print(f'Возникла непредвиденная ошибка: {e}')
        return None


class FormatColumn(Connection):

    @staticmethod
    def verify_name_length(name: str, max_length: int) -> str:
        """Проверяет длину названия и обрезает его, если длина превышает максимальную."""
        if len(name) > max_length:
            return f'{name[:max_length - 1]}~'
        return name

    def _get_x_negative_percent(self, x: float, percentage: str) -> float:
        """Возвращает значение x, уменьшенное на 1, если процент отрицательный."""
        if float(percentage[:-1]) < 0:
            self.max_percent_length: int = 8
            return x - 1
        self.max_percent_length: int = 7
        return x

    def _format_percentage(self, percentage: str) -> str:
        """Форматирует процент, обрезая его, если длина превышает максимальную."""
        if len(percentage) > self.max_percent_length:
            return f'{percentage[:self.max_percent_length - 1]}%'
        return percentage

    def _verify_rate_length(self, coin: str, currency: str, rate: str) -> str:
        """Проверяет и форматирует строку с курсом валюты, чтобы она соответствовала максимальной длине."""
        len_currency: int = len(f'{self.verify_name_length(coin, 5)}/{self.verify_name_length(currency, 4)}:')
        len_rate: int = len(rate)

        def inner_function() -> str:
            if len_rate > self.max_coins_length:
                return rate[:self.max_coins_length]
            elif len_rate < self.max_coins_length:
                return " " * (self.max_coins_length - len_rate) + rate
            return rate

        if len_currency < self.max_coins_length:
            return " " * (self.max_coins_length - len_currency) + inner_function()
        elif len_currency == self.max_coins_length:
            return inner_function()
        else:
            return rate[:self.max_coins_length]

    def _get_color(self, index: int, current: float, previous: float) -> str:
        """Определяет цвет в зависимости от текущего и предыдущего значений."""
        start: float = self.start_rates[index]
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

    def _get_percentage_difference(self, start_value: float, final_value: float) -> str:
        """Вычисляет процентное изменение между начальным и конечным значениями."""
        difference: float = (final_value - start_value) / abs(start_value) * 100
        formatted_difference: str = f'{difference:.{self.max_percent_zero}f}%'
        return formatted_difference

    def display_rates(
            self, stdscr, index: int, y: int, x: int, coin: str,
            currency: str, rate: str, coin_color: str, currency_color: str
    ) -> None:
        """Отображает курсы валют на экране."""
        try:
            coin_name: str = self.verify_name_length(coin, 5)
            currency_name: str = self.verify_name_length(currency, 4)

            stdscr.addstr(index + y, x, coin_name, self.paint(coin_color, False))
            stdscr.addstr(index + y, len(coin_name) + x, '/', self.paint(self.marks_color, False))
            stdscr.addstr(index + y, len(coin_name) + (x + 1), currency_name, self.paint(currency_color, False))
            stdscr.addstr(index + y, len(coin_name + currency_name) + (x + 1), ':', self.paint(self.marks_color, False))
            stdscr.addstr(
                index + y, len(coin_name + currency_name) + (x + 3),
                str(self._verify_rate_length(coin, currency, rate)),
                self.paint(self._get_color(index, float(rate), self.previous_rates[index]), False)
            )
            if rate is not None and rate != self.zero_value:
                percentage: str = self._get_percentage_difference(self.start_rates[index], float(rate))
                stdscr.addstr(
                    index + y,
                    x + self.max_coins_length * 2 + self._get_x_negative_percent(self.x_percentage, percentage),
                    self._format_percentage(percentage),
                    self.paint(self._get_color(index, float(rate), self.previous_rates[index]), False)
                )
        except ZeroDivisionError:
            self.initial_rates = False
        except error:
            pass


class RatesManager(FormatColumn):

    @staticmethod
    def _verify_config(coins: dict[str, dict[str, str]], start_rates: str | bool | dict[str, dict[str, str]]) -> None:
        """Проверяет, совпадает ли количество монет с количеством начальных курсов."""
        if len(coins) != len(start_rates):
            raise ValueError('Количество монет не совпадает с количеством начальных курсов!')

    async def create_coins_list(self, coins: dict) -> list:
        """Создает список монет с их курсами и дополнительной информацией."""
        pairs_list = await asyncio.gather(
            *(self.get_connection(coin, currency['currency']) for coin, currency in coins.items())
        )
        len_pairs_list: int = len(pairs_list)
        if len_pairs_list > 75:
            raise Exception(f'Превышение максимального количества монет: {len_pairs_list}!')
        return [
            (
                coin, currency['currency'], f'{float(rate):.{self.max_coins_zero}f}'
            if rate is not None else self.zero_value, currency['coin_color'], currency['currency_color']
            )
            for (coin, currency), rate in zip(coins.items(), pairs_list)
        ]

    def get_percentage_difference(self, start_value: float, final_value: float) -> str:
        """Вычисляет процентное изменение между начальным и конечным значениями."""
        difference: float = (final_value - start_value) / abs(start_value) * 100
        formatted_difference: str = f'{difference:.{self.max_percent_zero}f}%'
        return formatted_difference

    def verify_initial_rates(self, rates: list[str]) -> None:
        """Проверяет и устанавливает начальные курсы валют."""
        if not self.initial_rates:
            if os.path.exists('config_files/start_rates.json'):
                start_rates: str | bool = self.get_config_data('start_rates')['start_rates']
                self._verify_config(self.coins, start_rates)
                self.start_rates = start_rates
            else:
                self.start_rates: list[float] = [float(rate) for _, _, rate, _, _ in rates]
                self.save_json_data('config_files', 'start_rates', {"start_rates": self.start_rates})
            self.initial_rates = True

    def verify_previous_rates(self, rates: list[str]) -> None:
        """Проверяет и обновляет предыдущие курсы, если их количество не совпадает с текущими курсами."""
        if len(self.previous_rates) != len(rates):
            self.previous_rates: list[float] = [0.0] * len(rates)
