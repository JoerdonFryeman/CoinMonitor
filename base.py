import os, asyncio, aiohttp

from configuration import (
    Configuration, use_default_colors, init_pair, color_pair, A_BOLD, COLOR_BLACK,
    COLOR_BLUE, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA, COLOR_RED, COLOR_WHITE, COLOR_YELLOW
)


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

    __slots__ = (
        'max_coins_length', 'max_coins_zero', 'max_percent_zero', 'max_percent_length',
        'x_percentage', 'zero_value', 'start_rates', 'previous_rates', 'initial_rates_set'
    )

    def __init__(self):
        super().__init__()
        self.max_coins_length: int = 11
        self.max_coins_zero: int = 10
        self.max_percent_zero: int = 4
        self.max_percent_length: int = 7
        self.x_percentage: int = 4
        self.zero_value: str = f'0.{"0" * (self.max_coins_zero - 1)}'
        self.start_rates: list[float] = []
        self.previous_rates: list[float] = []
        self.initial_rates_set: bool = False

    @staticmethod
    def verify_color(color) -> object | int:
        """
        Метод проверяет настройку цвета из конфигурации.
        :return: COLOR_*: Цветовая константа, соответствующая цветовой конфигурации.
        """
        color_map: dict[str, int] = {
            'BLACK': COLOR_BLACK, 'BLUE': COLOR_BLUE, 'CYAN': COLOR_CYAN, 'GREEN': COLOR_GREEN,
            'MAGENTA': COLOR_MAGENTA, 'RED': COLOR_RED, 'WHITE': COLOR_WHITE, 'YELLOW': COLOR_YELLOW,
        }
        return color_map.get(color, COLOR_WHITE)

    def paint(self, color: str, a_bold: bool) -> object:
        """
        Метод раскрашивает текст или текстовое изображение.

        :param color: Цвет изображения.
        :param a_bold: A bold symbol true or false

        :return: Объект color_pair.
        :raises KeyError: Если указанный цвет не найден в словаре цветов.
        """
        colors_dict: dict[str, int] = {
            'MAGENTA': 1, 'BLUE': 2, 'CYAN': 3, 'GREEN': 4,
            'YELLOW': 5, 'RED': 6, 'WHITE': 7, 'BLACK': 8
        }
        if color not in colors_dict:
            raise KeyError(f'Цвет "{color}" не найден в доступных цветах.')
        for i, color_name in enumerate(colors_dict.keys()):
            use_default_colors()
            init_pair(1 + i, self.verify_color(color_name), -1)
        if a_bold:
            return color_pair(colors_dict[color]) | A_BOLD
        return color_pair(colors_dict[color])

    async def create_coins_list(self, coins: dict) -> list:
        """
        Создает список монет с их курсами и дополнительной информацией.

        :param coins: Словарь, где ключи - названия монет, а значения - словари с информацией о валюте.

        :return: Список кортежей, содержащих информацию о монетах и их курсах.
        :raises Exception: Если количество монет превышает 75.
        """
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
        """
        Вычисляет процентное изменение между начальным и конечным значениями.

        :param start_value: Начальное значение.
        :param final_value: Конечное значение.

        :return: Процентное изменение, отформатированное с заданным количеством знаков после запятой.
        """
        difference: float = (final_value - start_value) / abs(start_value) * 100
        formatted_difference: str = f'{difference:.{self.max_percent_zero}f}%'
        return formatted_difference

    def verify_initial_rates(self, rates: list[str]) -> None:
        """
        Проверяет и устанавливает начальные курсы валют.

        Этот метод проверяет, были ли уже установлены начальные курсы.
        Если они не были установлены, метод пытается загрузить их из конфигурационного файла.
        Если файл не существует, он извлекает курсы из переданного списка и сохраняет их в файл.

        :param rates: Список курсов, полученных от API.
        Каждый элемент списка должен быть строкой, представляющей курс валюты.

        :raises ValueError: Если переданный список курсов пуст или содержит недопустимые значения.
        :raises FileNotFoundError: Если файл конфигурации не найден и не удается извлечь курсы из списка.
        """
        if not self.initial_rates_set:
            if os.path.exists('config_files/start_rates.json'):
                start_rates: str | bool = self.get_config_data('start_rates')['start_rates']
                self.verify_config_files(self.coins, start_rates)
                self.start_rates = start_rates
            else:
                self.start_rates: list[float] = [float(rate) for _, _, rate, _, _ in rates]
                self.write_json_data('start_rates', {"start_rates": self.start_rates})
            self.initial_rates_set = True

    def verify_previous_rates(self, rates: list[str]) -> None:
        """
        Проверяет и обновляет предыдущие курсы, если их количество не совпадает с текущими курсами.
        :param rates: Список курсов, где каждый элемент - это кортеж с информацией о монете.
        """
        if len(self.previous_rates) != len(rates):
            self.previous_rates: list[float] = [0.0] * len(rates)
