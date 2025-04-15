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

directories = ('config_files', 'icons')
for directory in directories:
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass


class Configuration:
    """Класс Configuration используется для чтения и управления настройками конфигурации из JSON-файла."""

    coinmonitor_config = {
        "API": "https://api.coinbase.com/v2/exchange-rates?currency=",
        "marks_color": "MAGENTA",
        "info": False,
        "coins": {
            "BTC": {
                "currency": "USDT",
                "coin_color": "BLUE",
                "currency_color": "CYAN"
            },
            "ETH": {
                "currency": "USDT",
                "coin_color": "BLUE",
                "currency_color": "CYAN"
            },
            "XRP": {
                "currency": "USDT",
                "coin_color": "BLUE",
                "currency_color": "CYAN"
            },
            "BNB": {
                "currency": "USDT",
                "coin_color": "BLUE",
                "currency_color": "CYAN"
            },
            "SOL": {
                "currency": "USDT",
                "coin_color": "BLUE",
                "currency_color": "CYAN"
            }
        }
    }

    @staticmethod
    def write_json_data(config_name: str, json_data: dict) -> None:
        """
        Метод создает новый файл конфигурации по умолчанию, если указанный JSON-файл не существует.

        :param config_name: Имя файла конфигурации (без расширения .json).
        :param json_data: Записываемые в виде словаря данные.
        """
        try:
            with open(f'config_files/{config_name}.json', 'x', encoding='UTF-8') as write_file:
                assert isinstance(write_file, TextIOWrapper)  # Явная проверка типа
                dump(json_data, write_file, ensure_ascii=False, indent=4)
        except FileExistsError:
            pass
        except OSError as e:
            print(f'\nFailed to create file "{config_name}.json" due to {e}')

    @staticmethod
    def get_json_data(config_name: str):
        """
        Метод считывает JSON-файл конфигурации.
        :param config_name: Имя файла конфигурации (без расширения .json).
        """
        with open(f'config_files/{config_name}.json', encoding='UTF-8') as read_file:
            data = load(read_file)
        return data

    def get_config_data(self, config_name: str) -> dict | None:
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
            print(f'\nJSONDecodeError! File "{config_name}.json" is corrupted or not a valid JSON!')
        except OSError as e:
            print(f'\nOSError! Failed to read file "{config_name}.json" due to {e}.')

    __slots__ = ('variables', 'api', 'coins', 'marks_color', 'info')

    def __init__(self):
        self.variables = self.get_config_data('coinmonitor_config')
        try:
            self.api = self.variables['API']
            self.coins = self.variables['coins']
            self.marks_color = self.variables['marks_color']
            self.info = self.variables['info']
        except TypeError:
            print('\nTypeError! Variables can\'t be initialized!')

    @staticmethod
    def verify_config_files(coins: dict, start_rates: list):
        if len(coins.keys()) != len(start_rates):
            raise Exception('Количество монет не совпадает с количеством начальных курсов!')

    @staticmethod
    def verify_color(color):
        """
        Метод проверяет настройку цвета из конфигурации.
        :return: COLOR_*: Цветовая константа, соответствующая цветовой конфигурации.
        """
        color_map = {
            'BLACK': COLOR_BLACK, 'BLUE': COLOR_BLUE, 'CYAN': COLOR_CYAN, 'GREEN': COLOR_GREEN,
            'MAGENTA': COLOR_MAGENTA, 'RED': COLOR_RED, 'WHITE': COLOR_WHITE, 'YELLOW': COLOR_YELLOW,
        }
        return color_map.get(color, COLOR_WHITE)
