import os
import asyncio
import aiohttp

from .base import Base


class Connection(Base):

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


class RatesManager(Connection):
    __slots__ = ('max_coins_zero', 'max_percent_zero', 'zero_value', 'start_rates', 'previous_rates', 'initial_rates')

    def __init__(self):
        super().__init__()
        self.max_coins_zero = 10
        self.max_percent_zero = 4
        self.zero_value = f'0.{"0" * (self.max_coins_zero - 1)}'
        self.start_rates = []
        self.previous_rates = []
        self.initial_rates = False

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
