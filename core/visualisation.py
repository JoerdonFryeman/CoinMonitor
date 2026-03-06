try:
    from curses import (
        wrapper, error, curs_set, baudrate, start_color, init_pair, use_default_colors, has_colors, color_pair,
        A_BOLD, COLOR_BLACK, COLOR_BLUE, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA, COLOR_RED, COLOR_WHITE, COLOR_YELLOW
    )
except ModuleNotFoundError:
    print('\nДля работы программы необходимо установить модуль curses!\n')

from .base import Base


class Visualisation(Base):

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
