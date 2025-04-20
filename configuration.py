import os
from io import TextIOWrapper
from json import load, dump, JSONDecodeError

try:
    from curses import (
        wrapper, error, curs_set, baudrate, start_color, init_pair, use_default_colors, color_pair, A_BOLD,
        COLOR_BLACK, COLOR_BLUE, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA, COLOR_RED, COLOR_WHITE, COLOR_YELLOW
    )
except ModuleNotFoundError:
    print('\nДля работы программы необходимо установить модуль curses!\n')

directories: tuple[str, str] = ('config_files', 'icons')
for directory in directories:
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass


class Configuration:
    """Класс Configuration используется для чтения и управления настройками конфигурации из JSON-файла."""

    coinmonitor_config: dict[str, str | bool | dict[str, dict[str, str]]] = {
        "API": "https://api.coinbase.com/v2/exchange-rates?currency=",
        "marks_color": "MAGENTA",
        "info": False,
        "info_color": "MAGENTA",
        "coins": {
            "BTC": {"currency": "USDT", "coin_color": "BLUE", "currency_color": "CYAN"},
            "ETH": {"currency": "USDT", "coin_color": "BLUE", "currency_color": "CYAN"},
            "XRP": {"currency": "USDT", "coin_color": "BLUE", "currency_color": "CYAN"},
            "LTC": {"currency": "USDT", "coin_color": "BLUE", "currency_color": "CYAN"},
            "BNB": {"currency": "USDT", "coin_color": "BLUE", "currency_color": "CYAN"},
            "SOL": {"currency": "USDT", "coin_color": "BLUE", "currency_color": "CYAN"}
        }
    }

    @staticmethod
    def verify_config_files(
            coins: dict[str, dict[str, str]], start_rates: str | bool | dict[str, dict[str, str]]
    ) -> None:
        """
        Проверяет, совпадает ли количество монет с количеством начальных курсов.

        :param coins: Словарь, где ключи - идентификаторы монет, а значения - их названия или другие данные.
        :param start_rates: Список начальных курсов, соответствующих монетам.
        :raises ValueError: Если количество монет не совпадает с количеством начальных курсов.
        """
        if len(coins) != len(start_rates):
            raise ValueError('Количество монет не совпадает с количеством начальных курсов!')

    @staticmethod
    def write_json_data(config_name: str, json_data: dict) -> None:
        """
        Метод создает новый файл конфигурации по умолчанию, если указанный JSON-файл не существует.

        :param config_name: Имя файла конфигурации (без расширения .json).
        :param json_data: Записываемые в виде словаря данные.
        """
        try:
            with open(f'config_files/{config_name}.json', 'x', encoding='UTF-8') as write_file:
                assert isinstance(write_file, TextIOWrapper)
                dump(json_data, write_file, ensure_ascii=False, indent=4)
        except FileExistsError:
            pass
        except OSError as e:
            print(f'\nНе удалось создать файл «{config_name}.json» из-за {e}')

    @staticmethod
    def get_json_data(config_name: str) -> dict[str, str | bool | dict[str, dict[str, str]]]:
        """
        Метод считывает JSON-файл конфигурации.
        :param config_name: Имя файла конфигурации (без расширения .json).
        """
        with open(f'config_files/{config_name}.json', encoding='UTF-8') as read_file:
            data: dict[str, str | bool | dict[str, dict[str, str]]] = load(read_file)
        return data

    def get_config_data(self, config_name: str) -> dict[str, str | bool] | None:
        """
        Метод пробует прочитать файл конфигурации и, если это не удаётся, перезаписывает его.

        :param config_name: Имя файла конфигурации (без расширения .json).
        :return dict: Данные конфигурации, загруженные из файла JSON.
        """
        try:
            return self.get_json_data(config_name)
        except FileNotFoundError:
            self.write_json_data(config_name, self.coinmonitor_config)
            return self.coinmonitor_config
        except JSONDecodeError:
            print(f'\nJSONDecodeError! Файл «{config_name}.json» поврежден или не является корректным JSON!')
            return None
        except OSError as e:
            print(f'\nOSError! Не удалось прочитать файл «{config_name}.json» из-за {e}')
            return None

    __slots__ = ('variables', 'api', 'coins', 'marks_color', 'info', 'info_color')

    def __init__(self):
        self.variables: dict[str, str | bool | dict[str, dict[str, str]]] = self.get_config_data('coinmonitor_config')
        try:
            self.api: str = self.variables['API']
            self.coins: dict[str, dict[str, str]] = self.variables['coins']
            self.marks_color: str = self.variables['marks_color']
            self.info: bool = self.variables['info']
            self.info_color: str = self.variables['info_color']
        except TypeError:
            print('\nTypeError! Переменные не могут быть инициализированы!')
