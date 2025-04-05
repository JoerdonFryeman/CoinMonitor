import asyncio
import aiohttp
from configuration import Configuration, error, use_default_colors, init_pair, color_pair


class Connection(Configuration):
    """Управляет подключением к API для получения курсов криптовалют и их валидации."""

    @staticmethod
    def verify_data(data: dict, currency: str) -> float | None:
        """
        Проверяет наличие данных и возвращает курс валюты, если он доступен.

        :param data: Данные, полученные от API.
        :param currency: Код валюты, для которой нужно получить курс.

        :return: Курс валюты, если он найден, иначе None.
        """
        if 'data' in data and 'rates' in data['data']:
            return data['data']['rates'].get(currency)
        return None

    async def get_connection(self, coin: str, currency: str) -> dict | None:
        """
        Получает данные о курсе указанной криптовалюты в заданной валюте.

        :param coin: Название криптовалюты.
        :param currency: Код валюты, в которой нужно получить курс.

        :return: Данные о курсе валюты, если запрос успешен, иначе None.
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f'{self.api}{coin}') as response:
                    response.raise_for_status()
                    return self.verify_data(await response.json(), currency)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None
        except Exception as e:
            print(f'Возникла непредвиденная ошибка: {e}')
        return None


class Base(Connection):
    """Содержит основные параметры и методы для работы с курсами криптовалют."""

    def __init__(self):
        super().__init__()
        self.max_coins_length = 11
        self.max_coins_zero = 10
        self.max_percent_zero = 3
        self.max_percent_length = 8
        self.x_percentage = 4
        self.zero_value = f'0.{"0" * (self.max_coins_zero - 1)}'
        self.start_rates = []
        self.previous_rates = []
        self.initial_rates_set = False

    async def create_coins_list(self, coins: dict) -> list:
        """
        Создает список монет с их курсами и дополнительной информацией.

        :param coins: Словарь, где ключи - названия монет, а значения - словари с информацией о валюте.

        :return: Список кортежей, содержащих информацию о монетах и их курсах.
        :raises Exception: Если количество монет превышает 75.
        """
        pairs_list = await asyncio.gather(
            *(self.get_connection(coin, currency['currency']) for coin, currency in coins.items()))
        len_pairs_list = len(pairs_list)
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
        """
        Вычисляет процентное изменение между начальным и конечным значениями.

        :param start_value: Начальное значение.
        :param final_value: Конечное значение.

        :return: Процентное изменение, отформатированное с заданным количеством знаков после запятой.
        """
        difference = (final_value - start_value) / abs(start_value) * 100
        formatted_difference = f'{difference:.{self.max_percent_zero}f}%'
        return formatted_difference

    def verify_initial_rates(self, rates: list) -> None:
        """
        Устанавливает начальные курсы, если они еще не были установлены.
        :param rates: Список курсов, полученных от API.
        """
        if not self.initial_rates_set:
            self.start_rates = [float(rate) for _, _, rate, _, _ in rates]
            self.initial_rates_set = True

    def verify_previous_rates(self, rates: list) -> None:
        """
        Проверяет и обновляет предыдущие курсы, если их количество не совпадает с текущими курсами.
        :param rates: Список курсов, где каждый элемент - это кортеж с информацией о монете.
        """
        if len(self.previous_rates) != len(rates):
            self.previous_rates = [0.0] * len(rates)


class Visualization(Base):
    """Отвечает за отображение информации о криптовалютах и их курсах на экране."""

    @staticmethod
    def get_x_negative_percent(x: float, percentage: str) -> float:
        """
        Возвращает значение x, уменьшенное на 1, если процент отрицательный.

        :param x Исходное значение.
        :param percentage: Процент в виде строки (например, "-5%").

        :return: Обновленное значение x.
        """
        if float(percentage[:-1]) < 0:
            return x - 1
        return x

    def format_percentage(self, percentage: str) -> str:
        """
        Форматирует процент, обрезая его, если длина превышает максимальную.

        :param percentage: Процент в виде строки (например, "123.45%").

        :return: Отформатированный процент.
        Если длина превышает максимальную, возвращает обрезанную строку с добавлением "..%".
        """
        if len(percentage) > self.max_percent_length:
            return f'{percentage[:self.max_percent_length - 4]}..%'
        return percentage

    def verify_length(self, coin: str, currency: str, rate: str) -> str:
        """
        Проверяет и форматирует строку с курсом валюты, чтобы она соответствовала максимальной длине.

        :param coin: Название криптовалюты.
        :param currency: Код валюты.
        :param rate: Курс валюты в виде строки.

        :return: Отформатированная строка с курсом валюты.
        """
        len_currency = len(f'{coin}/{currency}:')
        len_rate = len(rate)

        def verify_rate_length() -> str:
            if len_rate > self.max_coins_length:
                return rate[:self.max_coins_length]
            elif len_rate < self.max_coins_length:
                return " " * (self.max_coins_length - len_rate) + rate
            return rate

        if len_currency < self.max_coins_length:
            return " " * (self.max_coins_length - len_currency) + verify_rate_length()
        elif len_currency == self.max_coins_length:
            return verify_rate_length()
        else:
            return rate[:self.max_coins_length]

    def paint(self, color: str) -> object:
        """
        Метод раскрашивает текст или текстовое изображение.

        :param color: Цвет изображения.
        :return: Объект color_pair.

        :raises KeyError: Если указанный цвет не найден в словаре цветов.
        """
        colors_dict: dict[str, int] = {
            'MAGENTA': 1, 'BLUE': 2, 'CYAN': 3, 'GREEN': 4,
            'YELLOW': 5, 'RED': 6, 'WHITE': 7, 'BLACK': 8
        }
        for i, color_name in enumerate(colors_dict.keys()):
            use_default_colors()
            init_pair(1 + i, self.verify_color(color_name), -1)
        if color not in colors_dict:
            raise KeyError(f'Цвет "{color}" не найден в доступных цветах.')
        return color_pair(colors_dict[color])

    def get_color(self, index: int, current: float, previous: float) -> str:
        """
        Определяет цвет в зависимости от текущего и предыдущего значений.

        :param index: Индекс монеты в списке.
        :param current: Текущее значение курса.
        :param previous: Предыдущее значение курса.

        :return: Цвет, соответствующий изменению курса.
        """
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

    def display_info(self, stdscr) -> None:
        """
        Отображает информацию о приложении на экране.
        :param stdscr: Объект stdscr для работы с экраном.
        """
        try:
            stdscr.addstr(11, 31, 'CoinMonitor (version 1.0.0)', self.paint('GREEN'))
            stdscr.addstr(12, 31, 'https://github.com/JoerdonFryeman/CoinMonitor', self.paint('GREEN'))
            stdscr.addstr(13, 31, 'MIT License, copyright (c) 2025 JoerdonFryeman', self.paint('GREEN'))
        except error:
            pass  # Игнорируем ошибки, связанные с отображением

    def display_rates(
            self, stdscr, index: int, y: int, x: int, coin: str,
            currency: str, rate: str, coin_color: str, currency_color: str
    ) -> None:
        """
        Отображает курсы валют на экране.

        :param stdscr: Объект stdscr для работы с экраном.
        :param index: Индекс монеты в списке.
        :param y: Координата Y для отображения.
        :param x: Координата X для отображения.
        :param coin: Название криптовалюты.
        :param currency: Код валюты.
        :param rate: Курс валюты.
        :param coin_color: Цвет для отображения названия монеты.
        :param currency_color: Цвет для отображения кода валюты.
        """
        try:
            stdscr.addstr(index + y, x, str(coin), self.paint(coin_color))
            stdscr.addstr(index + y, len(str(coin)) + x, '/', self.paint(self.marks_color))
            stdscr.addstr(index + y, len(str(coin)) + (x + 1), str(currency), self.paint(currency_color))
            stdscr.addstr(index + y, len(str(coin) + str(currency)) + (x + 1), ':', self.paint(self.marks_color))
            stdscr.addstr(
                index + y, len(coin + currency) + (x + 3), str(self.verify_length(coin, currency, rate)),
                self.paint(self.get_color(index, float(rate), self.previous_rates[index]))
            )
            if rate is not None and rate != self.zero_value:
                percentage = self.get_percentage_difference(self.start_rates[index], float(rate))
                stdscr.addstr(
                    index + y,
                    x + self.max_coins_length * 2 + self.get_x_negative_percent(self.x_percentage, percentage),
                    self.format_percentage(percentage),
                    self.paint(self.get_color(index, float(rate), self.previous_rates[index]))
                )
        except ZeroDivisionError:
            self.initial_rates_set = False  # Устанавливаем флаг, если произошло деление на ноль
        except error:
            pass  # Игнорируем ошибки, связанные с отображением
