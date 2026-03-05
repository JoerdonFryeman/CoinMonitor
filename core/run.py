import asyncio
from threading import Thread

from .visualisation import Visualisation


class RunProgram(Visualisation):
    __slots__ = ('running',)

    def __init__(self):
        super().__init__()
        self.running = True

    def wait_for_enter(self, stdscr) -> None:
        """Ждёт нажатия клавиши и устанавливает флаг остановки."""
        stdscr.getch()
        self.running: bool = False

    async def create_main_loop(self, stdscr) -> None:
        """Запускает все модули программы в цикле."""
        while self.running:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            rates: list[str] = await self.create_coins_list(self.coins)

            self.verify_initial_rates(rates)
            self.verify_previous_rates(rates)

            counter_first, counter_second, counter_third = 0, 0, 0

            for i, (coin, currency, rate, coin_color, currency_color) in enumerate(rates):
                current_rate = float(rate)

                if width >= 34:
                    if counter_first <= height - 2:
                        args: tuple = (coin, currency, rate, coin_color, currency_color)
                        self.display_rates(stdscr, i, 1, 1, *args)
                        counter_first += 1
                    else:
                        if width >= 71:
                            if counter_second <= height - 2:
                                args: tuple = (coin, currency, rate, coin_color, currency_color)
                                self.display_rates(
                                    stdscr, i, - height + 2, 38, *args)
                                counter_second += 1
                            else:
                                if width >= 108:
                                    if counter_third <= height - 2:
                                        args: tuple = (coin, currency, rate, coin_color, currency_color)
                                        self.display_rates(stdscr, i, - counter_second - height + 2, 75, *args)
                                    counter_third += 1

                self.previous_rates[i]: list[float] = current_rate

            if self.running:
                stdscr.refresh()
            await asyncio.sleep(0.5)

    def create_wrapped_threads(self) -> None:
        """Запускает главный цикл и поток ожидания нажатия клавиши."""
        self.safe_wrapper(self.init_curses, None)
        Thread(target=self.safe_wrapper, args=(self.wait_for_enter, None)).start()
        self.safe_wrapper(lambda stdscr: asyncio.run(self.create_main_loop(stdscr)))
