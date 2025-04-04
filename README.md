# CoinMonitor

 Консольное приложение для отслеживания курса криптовалют.
 
## Структура проекта

- `main.py`: Главный модуль для запуска цикла.
- `coin_monitor.py`: Основной модуль программы.
- `configuration.py`: Вспомогательный модуль для загрузки конфигурационных данных.
- `coinmonitor_config.json`: Файл настройки и конфигурации программы.

## Требования

- Python 3
- aiohttp 3.11.16
- windows-curses 2.4.1a1 (для Windows)

## Установка

Скачать проект

``` console
git clone https://github.com/JoerdonFryeman/CoinMonitor
cd CoinMonitor
```

Создайте виртуальное окружение и установите необходимые требования

## Для Linux
``` console
python -m venv venv && source venv/bin/activate
pip install --upgrade pip && pip install -r requirements_for_linux.txt
```

## Для Windows
``` console
python -m venv venv && venv\Scripts\activate
python.exe -m pip install --upgrade pip && pip install -r requirements_for_windows.txt
```

## Запуск
Вы можете запустить проект в консоли

``` console
python main.py
```

## Настройки

Некоторые настройки программы можно задать в файле coinmonitor_config.json.

- Добавьте нужную вам криптовалюту.
- Вы можете изменить цвет каждой монеты и знаков: BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW.
- Изменить API можно в соответствующей настройке.
- С помощью true или false включите или отключите информацию о программе.

Настройки по умолчанию можно восстановить, удалив файл coinmonitor_config.json и перезапустив программу.

## Лицензия

Этот проект разрабатывается под лицензией MIT.

## Поддержать с помощью Биткоина:

bc1qewfgtrrg2gqgtvzl5d2pr9pte685pp5n3g6scy
