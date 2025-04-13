import os
from io import TextIOWrapper
from json import load, dump
from typing import Dict

try:
    from curses import (
        wrapper, error, curs_set, baudrate, start_color, init_pair, use_default_colors, color_pair, A_BOLD,
        COLOR_BLACK, COLOR_BLUE, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA, COLOR_RED, COLOR_WHITE, COLOR_YELLOW
    )
except ModuleNotFoundError:
    print('\nДля Windows необходимо установить файл requirements_for_windows.txt!\n')

try:
    directories: tuple[str, str] = ('config_files', 'icons')
    for i in range(len(directories)):
        os.mkdir(directories[i])
        i += 1
except FileExistsError:
    pass


class Configuration:
    """Класс Configuration используется для чтения и управления настройками конфигурации из JSON-файла."""

    json_data = {
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
            "LTC": {
                "currency": "USDT",
                "coin_color": "BLUE",
                "currency_color": "CYAN"
            },
            "BNB": {
                "currency": "USDT",
                "coin_color": "BLUE",
                "currency_color": "CYAN"
            }
        }
    }

    @classmethod
    def get_json_data(cls, config_name: str) -> Dict:
        """
        Метод считывает конфигурационный файл JSON.
        Если указанный JSON-файл не существует, он создает новый файл с конфигурациями по умолчанию.

        :param config_name: Имя файла конфигурации (без расширения .json).
        :return Dict: Данные конфигурации, загруженные из файла JSON.
        """
        try:
            with open(f'config_files/{config_name}.json', encoding='UTF-8') as read_file:
                data = load(read_file)
            return data
        except FileNotFoundError:
            print(f'\nFileNotFoundError! File "{config_name}.json" not found!')
            try:
                if config_name == 'coinmonitor_config':
                    with open(f'config_files/{config_name}.json', 'w', encoding='UTF-8') as write_file:
                        if isinstance(write_file, TextIOWrapper):
                            dump(cls.json_data, write_file, ensure_ascii=False, indent=4)
                        else:
                            raise TypeError("Expected TextIOWrapper for the file type")
                else:
                    raise TypeError(f'Файл "{config_name}.json" не найден!')
            except OSError as e:
                print(f'\nFailed to create file "{config_name}.json" due to {e}')
            return cls.json_data

    __slots__ = ('variables', 'api', 'coins', 'marks_color', 'info')

    def __init__(self):
        self.variables = self.get_json_data('coinmonitor_config')
        try:
            self.api = self.variables['API']
            self.coins = self.variables['coins']
            self.marks_color = self.variables['marks_color']
            self.info = self.variables['info']
        except TypeError:
            print('\nTypeError! Variables can\'t be initialized!')

    @staticmethod
    def verify_color(color):
        """
        Метод проверяет настройку цвета из конфигурации.
        :return: COLOR_*: Цветовая константа, соответствующая цветовой конфигурации.
        """
        dictionary = {
            'BLACK': lambda: COLOR_BLACK, 'BLUE': lambda: COLOR_BLUE,
            'CYAN': lambda: COLOR_CYAN, 'GREEN': lambda: COLOR_GREEN,
            'MAGENTA': lambda: COLOR_MAGENTA, 'RED': lambda: COLOR_RED,
            'WHITE': lambda: COLOR_WHITE, 'YELLOW': lambda: COLOR_YELLOW,
        }[color]
        return dictionary()
