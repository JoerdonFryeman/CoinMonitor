import asyncio
from configuration import curs_set, wrapper
from coin_monitor import Visualization


class RunProgram(Visualization):
    """Основной класс, реализующий цикл программы для обновления и отображения курсов валют."""

    async def create_loop(self, stdscr) -> None:
        """
        Основной цикл программы, который обновляет и отображает курсы валют.
        :param stdscr: Объект stdscr для работы с экраном.
        """
        while True:
            stdscr.clear(), curs_set(False)
            height, width = stdscr.getmaxyx()
            rates = await self.create_coins_list(self.coins)
            self.verify_initial_rates(rates)
            self.verify_previous_rates(rates)
            counter_first, counter_second, counter_third = 0, 0, 0

            for i, (coin, currency, rate, coin_color, currency_color) in enumerate(rates):
                current_rate = float(rate)

                if self.info:
                    if width >= 78:
                        self.display_info(stdscr)
                else:
                    if width >= 34:
                        if counter_first <= height - 2:
                            args = (coin, currency, rate, coin_color, currency_color)
                            self.display_rates(stdscr, i, 1, 1, *args)
                            counter_first += 1
                        else:
                            if width >= 71:
                                if counter_second <= height - 2:
                                    args = (coin, currency, rate, coin_color, currency_color)
                                    self.display_rates(
                                        stdscr, i, - height + 2, 38, *args)
                                    counter_second += 1
                                else:
                                    if width >= 108:
                                        if counter_third <= height - 2:
                                            args = (coin, currency, rate, coin_color, currency_color)
                                            self.display_rates(stdscr, i, - counter_second - height + 2, 75, *args)
                                        counter_third += 1
                    self.previous_rates[i] = current_rate

            stdscr.refresh()
            await asyncio.sleep(0.5)


run_program = RunProgram()


def main() -> None:
    """Запускающая все процессы главная функция."""
    try:
        wrapper(lambda stdscr: asyncio.run(run_program.create_loop(stdscr)))
    except Exception as error:
        print(f'Проверка выдала ошибку: {error}')


if __name__ == '__main__':
    main()
