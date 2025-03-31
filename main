import asyncio
from configuration import wrapper
from coin_monitor import Visualization


class RunProgram(Visualization):
    async def create_loop(self, stdscr):
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            rates = await self.create_coins_list(self.coins)
            self.verify_previous_rates(rates), self.verify_initial_rates(rates)

            first, second, third = 0, 0, 0
            for i, (coin, currency, rate, coin_color, currency_color) in enumerate(rates):
                current_rate = float(rate)

                if width >= 36:
                    if first <= height - 2:
                        self.display_rates(
                            stdscr, i, 1, 1,
                            coin, currency, rate, coin_color, currency_color
                        )
                        first += 1
                    else:
                        if width >= 73:
                            if second <= height - 2:
                                self.display_rates(
                                    stdscr, i, - height + 2, 38,
                                    coin, currency, rate, coin_color, currency_color
                                )
                                second += 1
                            else:
                                if width >= 107:
                                    if third <= height - 2:
                                        self.display_rates(
                                            stdscr, i, - second - height + 2, 75,
                                            coin, currency, rate, coin_color, currency_color
                                        )
                                        third += 1

                self.previous_rates[i] = current_rate
            stdscr.refresh()
            await asyncio.sleep(0.5)


run_program = RunProgram()


def main():
    try:
        wrapper(lambda stdscr: asyncio.run(run_program.create_loop(stdscr)))
    except Exception as error:
        print(f'Проверка выдала ошибку: {error}')


if __name__ == '__main__':
    main()
