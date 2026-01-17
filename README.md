# ЭЛЕКТРОНИКА 54 (CoinMonitor)

Консольное приложение для отслеживания курса криптовалют.

![CoinMonitor](https://github.com/user-attachments/assets/4afb65d8-45bd-4649-a898-5aa132f6d3a7)

## Запуск
Скачайте [последний релиз](https://github.com/JoerdonFryeman/CoinMonitor/releases/tag/CoinMonitor_v1.0.2).

В Linux запустите ```CoinMonitor_v1.0.2.app``` с помощью терминала или введите следующую команду:

```console
cd /home/your_directories.../CoinMonitor_v1.0.2/Linux/ && ./CoinMonitor_v1.0.2.app
```

В Windows запустите ```CoinMonitor_v1.0.2.exe```

## Docker

Образ [последний релиз](https://hub.docker.com/r/joerdonfryeman/coinmonitor).

Запустите прикреплённый к стандартным потокам ввода/вывода образ:

```console
docker run -it joerdonfryeman/coinmonitor:1.0.3
```

С автоудалением контейнера:

```console
docker run --rm -it joerdonfryeman/coinmonitor:1.0.3
```

## Структура проекта

- `main.py`: Главный модуль для запуска цикла.
- `coin_monitor.py`: Основной модуль программы.
- `base.py`: Базовый модуль программы.
- `configuration.py`: Вспомогательный модуль для загрузки конфигурационных данных.
- `coinmonitor_config.json`: Файл настройки и конфигурации программы.
- `coinmonitor_config_coinmarketcap.json`: Пример конфигурации с использованием списка монет от CoinMarketCap.

## Требования

- Python 3.13
- aiohttp 3.11.18
- windows-curses 2.4.1a1 (для Windows)

## Установка

Скачать проект

``` console
git clone https://github.com/JoerdonFryeman/CoinMonitor
cd CoinMonitor
```

## Для Linux

Создайте и активируйте виртуальное окружение:

``` console
python -m venv venv && source venv/bin/activate
```

Установите необходимые требования и запустите скрипт в консоли:

``` console
pip install --upgrade pip && pip install -r requirements_for_linux.txt
python main.py
```

## Для Windows

Создайте и активируйте виртуальное окружение:

``` console
python -m venv venv && venv\Scripts\activate
```

Установите необходимые требования и запустите скрипт в консоли:

``` console
python.exe -m pip install --upgrade pip && pip install -r requirements_for_windows.txt
python main.py
```

## Закрыть

Просто нажми Enter или попробуй любую другую клавишу.

## Настройки

Некоторые настройки программы можно изменить в файле coinmonitor_config.json.

- Добавьте нужную вам криптовалюту, токен, фиатную валюту или используйте готовый пример coinmonitor_config_coinmarketcap.json (необходимо переименовать в coinmonitor_config.json).
- Вы можете изменить цвет каждой монеты и знаков: BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW.
- Изменить API можно в соответствующей настройке.
- С помощью true или false включите или отключите информацию о программе.

Настройки по умолчанию можно восстановить, удалив файл coinmonitor_config.json и перезапустив программу.

## Лицензия

Этот проект разрабатывается под лицензией MIT.

## Поддержать с помощью Биткоина:

bc1qewfgtrrg2gqgtvzl5d2pr9pte685pp5n3g6scy
