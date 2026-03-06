# ЭЛЕКТРОНИКА 54 (CoinMonitor)

Консольное приложение для отслеживания курса криптовалют.

![CoinMonitor](https://github.com/user-attachments/assets/4afb65d8-45bd-4649-a898-5aa132f6d3a7)

## Запуск
Скачайте [последний релиз](https://github.com/JoerdonFryeman/CoinMonitor/releases/tag/CoinMonitor_v1.0.3).

В Linux запустите ```CoinMonitor_v1.0.3``` в терминале с помощью команды:
```console
cd /home/your_directories.../CoinMonitor_v1.0.3/Linux/ && ./CoinMonitor_v1.0.3
```
В Windows запустите ```CoinMonitor_v1.0.3.exe```

## Docker

Образ [последний релиз](https://hub.docker.com/r/joerdonfryeman/coinmonitor).

Запуск с подключёнными стандартными потоками (интерактивный терминал):

```console
docker run -it joerdonfryeman/coinmonitor:1.0.3
```

То же с автоматическим удалением контейнера после выхода:

```console
docker run --rm -it joerdonfryeman/coinmonitor:1.0.3
```

## Требования

- Python: >= 3.11
- windows-curses: >= 2.4.1a1 (for Windows)
- aiohttp >= 3.11
- Приложение было разработано для Arch Linux с рабочей средой KDE Plasma, но должно работать и в других дистрибутивах, а также в Windows.

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
pip install --upgrade pip && pip install -r requirements.txt
python main.py
```

## Для Windows

Создайте и активируйте виртуальное окружение:

``` console
python -m venv venv
venv\Scripts\activate
```

Установите необходимые требования и запустите скрипт в консоли:

``` console
python.exe -m pip install --upgrade pip
pip install -r requirements_for_windows.txt
python main.py
```

## Закрыть

Просто нажми Enter или попробуй любую другую клавишу.

## Настройки

Некоторые настройки программы можно изменить в файле config.json.

- Добавьте нужную вам криптовалюту, токен, фиатную валюту или используйте готовый пример config_coinmarketcap.json (необходимо переименовать в config.json).
- Вы можете изменить цвет каждой монеты и знаков: BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW.
- Изменить API можно в соответствующей настройке.

Настройки по умолчанию можно восстановить, удалив файл config.json и перезапустив программу.

## Лицензия

Этот проект разрабатывается под лицензией MIT.

## Поддержать с помощью Биткоина:

bc1qewfgtrrg2gqgtvzl5d2pr9pte685pp5n3g6scy
