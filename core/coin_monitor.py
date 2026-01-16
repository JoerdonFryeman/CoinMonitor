from .configuration import error
from .base import Base


class FormatColumn(Base):
    """Форматирует ширину строки столбца"""

    def get_x_negative_percent(self, x: float, percentage: str) -> float:
        """
        Возвращает значение x, уменьшенное на 1, если процент отрицательный.

        :param x Исходное значение.
        :param percentage: Процент в виде строки (например, "-5%").

        :return: Обновленное значение x.
        """
        if float(percentage[:-1]) < 0:
            self.max_percent_length: int = 8
            return x - 1
        self.max_percent_length: int = 7
        return x

    @staticmethod
    def verify_name_length(name: str, max_length: int) -> str:
        """
        Проверяет длину названия и обрезает его, если длина превышает максимальную.

        :param name: Название в виде строки.
        :param max_length: Максимально допустимая длина названия.

        :return: Отформатированное название.
        Если длина превышает максимальную, возвращает обрезанную строку с добавлением "~".
        """
        if len(name) > max_length:
            return f'{name[:max_length - 1]}~'
        return name

    def format_percentage(self, percentage: str) -> str:
        """
        Форматирует процент, обрезая его, если длина превышает максимальную.

        :param percentage: Процент в виде строки (например, "123.45%").

        :return: Отформатированный процент.
        Если длина превышает максимальную, возвращает обрезанную строку с добавлением "%".
        """
        if len(percentage) > self.max_percent_length:
            return f'{percentage[:self.max_percent_length - 1]}%'
        return percentage

    def verify_rate_length(self, coin: str, currency: str, rate: str) -> str:
        """
        Проверяет и форматирует строку с курсом валюты, чтобы она соответствовала максимальной длине.

        :param coin: Название криптовалюты.
        :param currency: Код валюты.
        :param rate: Курс валюты в виде строки.

        :return: Отформатированная строка с курсом валюты.
        """
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


class Visualization(FormatColumn):
    """Отвечает за отображение информации о криптовалютах и их курсах на экране."""

    def get_color(self, index: int, current: float, previous: float) -> str:
        """
        Определяет цвет в зависимости от текущего и предыдущего значений.

        :param index: Индекс монеты в списке.
        :param current: Текущее значение курса.
        :param previous: Предыдущее значение курса.

        :return: Цвет, соответствующий изменению курса.
        """
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

    def display_info(self, stdscr) -> None:
        """
        Отображает информацию о приложении на экране.
        :param stdscr: Объект stdscr для работы с экраном.
        """
        try:
            stdscr.addstr(11, 31, 'CoinMonitor (version 1.0.2) | ЭЛЕКТРОНИКА 54', self.paint(self.info_color, False))
            stdscr.addstr(12, 31, 'MIT License, (c) 2025 JoerdonFryeman', self.paint(self.info_color, False))
            stdscr.addstr(13, 31, 'https://github.com/JoerdonFryeman/CoinMonitor', self.paint(self.info_color, False))
        except error:
            pass

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
            coin_name: str = self.verify_name_length(coin, 5)
            currency_name: str = self.verify_name_length(currency, 4)

            stdscr.addstr(index + y, x, coin_name, self.paint(coin_color, False))
            stdscr.addstr(index + y, len(coin_name) + x, '/', self.paint(self.marks_color, False))
            stdscr.addstr(index + y, len(coin_name) + (x + 1), currency_name, self.paint(currency_color, False))
            stdscr.addstr(index + y, len(coin_name + currency_name) + (x + 1), ':', self.paint(self.marks_color, False))
            stdscr.addstr(
                index + y, len(coin_name + currency_name) + (x + 3), str(self.verify_rate_length(coin, currency, rate)),
                self.paint(self.get_color(index, float(rate), self.previous_rates[index]), False)
            )
            if rate is not None and rate != self.zero_value:
                percentage: str = self.get_percentage_difference(self.start_rates[index], float(rate))
                stdscr.addstr(
                    index + y,
                    x + self.max_coins_length * 2 + self.get_x_negative_percent(self.x_percentage, percentage),
                    self.format_percentage(percentage),
                    self.paint(self.get_color(index, float(rate), self.previous_rates[index]), False)
                )
        except ZeroDivisionError:
            self.initial_rates_set = False
        except error:
            pass
