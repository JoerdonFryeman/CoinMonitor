import asyncio
from threading import Thread

from configuration import curs_set, wrapper, error
from coin_monitor import Visualization


class RunProgram(Visualization):
    """Основной класс, реализующий цикл программы для обновления и отображения курсов валют."""

    running = True

    @staticmethod
    def safe_wrapper(function) -> None:
        """Запускает метод в обёртке и игнорирует ошибки curses."""
        try:
            wrapper(function)
        except error:
            pass
        except Exception as e:
            print(f'Проверка выдала ошибку: {e}\nНажми Enter для завершения.')

    @classmethod
    def wait_for_enter(cls, stdscr) -> None:
        """Ожидает нажатия клавиши."""
        stdscr.nodelay(False)
        stdscr.getch()
        cls.running: bool = False
        stdscr.clear()

    async def create_loop(self, stdscr) -> None:
        """
        Основной цикл программы, который обновляет и отображает курсы валют.
        :param stdscr: Объект stdscr для работы с экраном.
        """
        while self.running:
            stdscr.clear(), curs_set(False)
            height, width = stdscr.getmaxyx()
            rates: list[str] = await self.create_coins_list(self.coins)

            self.verify_initial_rates(rates)
            self.verify_previous_rates(rates)

            counter_first: int = 0
            counter_second: int = 0
            counter_third: int = 0

            for i, (coin, currency, rate, coin_color, currency_color) in enumerate(rates):
                current_rate = float(rate)

                if self.info:
                    if width >= 78:
                        self.display_info(stdscr)
                else:
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


run_program = RunProgram()


def main() -> None:
    """Запускающая все процессы главная функция."""
    try:
        Thread(target=run_program.safe_wrapper, args=(run_program.wait_for_enter,)).start()
        run_program.safe_wrapper(lambda stdscr: asyncio.run(run_program.create_loop(stdscr)))
    except Exception as e:
        print(f'Проверка выдала ошибку: {e}')


if __name__ == '__main__':
    main()
