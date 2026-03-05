try:
    from curses import (
        wrapper, error, curs_set, baudrate, start_color, init_pair, use_default_colors, has_colors, color_pair,
        A_BOLD, COLOR_BLACK, COLOR_BLUE, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA, COLOR_RED, COLOR_WHITE, COLOR_YELLOW
    )
except ModuleNotFoundError:
    print('\nДля работы программы необходимо установить модуль curses!\n')

from .rates_manager import RatesManager


class Visualisation(RatesManager):
    __slots__ = ('max_coins_length', 'max_percent_length', 'x_percentage')

    def __init__(self):
        super().__init__()
        self.max_coins_length = 11
        self.max_percent_length = 7
        self.x_percentage = 4

    @staticmethod
    def safe_wrapper(function, *args) -> None:
        """Оборачивает вызов wrapper в try/except и подавляет исключения curses.error."""
        try:
            if any(args):
                wrapper(function, *args)
            else:
                wrapper(function)
        except error:
            pass

    @staticmethod
    def verify_color(color: str) -> int:
        """Метод проверяет настройку цвета из конфигурации."""
        color_map: dict[str, int] = {
            'BLACK': COLOR_BLACK, 'BLUE': COLOR_BLUE, 'CYAN': COLOR_CYAN, 'GREEN': COLOR_GREEN,
            'MAGENTA': COLOR_MAGENTA, 'RED': COLOR_RED, 'WHITE': COLOR_WHITE, 'YELLOW': COLOR_YELLOW,
        }
        return color_map.get(color.upper(), COLOR_WHITE)

    @staticmethod
    def init_curses(stdscr) -> None:
        """Инициализирует экран curses"""
        stdscr.clear()
        stdscr.refresh()
        curs_set(0)
        if has_colors():
            use_default_colors()
            start_color()

    @staticmethod
    def verify_name_length(name: str, max_length: int) -> str:
        """Проверяет длину названия и обрезает его, если длина превышает максимальную."""
        if len(name) > max_length:
            return f'{name[:max_length - 1]}~'
        return name

    def paint(self, color: str, a_bold: bool) -> int:
        """Раскрашивает текст или текстовое изображение."""
        colors = ('MAGENTA', 'BLUE', 'CYAN', 'GREEN', 'YELLOW', 'RED', 'WHITE', 'BLACK')
        for i in range(1, len(colors) + 1):
            init_pair(i, self.verify_color(colors[i - 1]), -1)
        try:
            pair_index = colors.index((color or '').upper()) + 1
        except (ValueError, AttributeError):
            error_message = f'Цвет "{color}" не найден в доступных цветах.'
            self.logger.error('%s (доступные: %s)', error_message, ', '.join(colors))
            raise KeyError(error_message)
        attribute = color_pair(pair_index)
        if a_bold:
            attribute |= A_BOLD
        return attribute

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
                percentage: str = self.get_percentage_difference(self.start_rates[index], float(rate))
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
