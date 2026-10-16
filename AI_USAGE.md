# Использование ИИ

## PR01

- Использован ИИ: да, Cursor.
- Затронутые файлы: evidence/pr01/graph.md, evidence/pr01/environment.json, evidence/pr01/report.json и этот файл.
- Помощь: пошаговые объяснения, формулировка команд и черновик текста отчёта по уже снятым измерениям.
- Проверка: команды ROS выполнялись вручную в трёх терминалах одного контейнера. Координаты, частота и коды завершения взяты из вывода этих команд и лежат в evidence/pr01. Результаты не подставлены вместо запуска симулятора.
- Переписка и секреты не включены.

## PR02

- Использован ИИ: да
- Модель: Grok 4.7
- Инструмент: Cursor
- Затронутые компоненты: пакет `src/turtle_bringup`, `.github/workflows/pr02.yml`, `README.md`, `evidence/pr02/`, этот файл
- Характер помощи: создание пакета и launch-файла, настройка CI, запуск команд сборки и turtlesim, черновик `commands.md`, `types.md` и `report.json` по выводу этих команд
- Проверка: `colcon build` и `ros2 launch` выполнены локально в ROS 2 Lyrical, домен 16. Позы, `ros2 topic info` и код завершения launch взяты из этого запуска и лежат в `evidence/pr02`. Числа в отчёте не подставлены вместо симулятора. `python3 -m py_compile` для launch-файла завершился успешно.

## PR03

- Использован ИИ: да
- Модель: Grok 4.7
- Инструмент: Cursor
- Затронутые компоненты: пакет `src/patrol`, `.github/workflows/pr03.yml`, `README.md`, `evidence/pr03/`, этот файл
- Характер помощи: нода с подпиской, таймером и чистой функцией команды, тесты, workflow и черновик `demo.md` с `report.json` по выводу локального запуска
- Проверка: `colcon build` и `python3 -m pytest src/patrol/test` выполнены локально в ROS 2 Lyrical. Позы, `ros2 topic info`, частота `ros2 topic hz` и остановка по SIGINT сняты с запущенных turtlesim и patrol в домене 16 и лежат в `evidence/pr03`. Числа в отчёте не подставлены вместо симулятора.

## PR04

- Использован ИИ: да
- Модель: Grok 4.7
- Инструмент: Cursor
- Затронутые компоненты: параметры ноды `src/patrol`, `src/patrol/test/test_parameters.py`, `.github/workflows/pr04.yml`, `README.md`, `evidence/pr04/`, этот файл
- Характер помощи: чистая проверка трёх параметров, смена одного таймера, тесты отказа, workflow и черновик `parameters.md` с `report.json` по выводу локального запуска
- Проверка: `colcon build` и `python3 -m pytest src/patrol/test` выполнены локально в ROS 2 Lyrical, 16 passed, 1 skipped. Частоты `ros2 topic hz`, отказ `publish_hz 0.0`, traceback `ZeroDivisionError`, поза, `/clear` и `ros2 action list -t` сняты с turtlesim и patrol в домене 16 и лежат в `evidence/pr04`. Числа в отчёте не подставлены вместо симулятора.

## PR05

- Использован ИИ: да
- Модель: Grok 4.7
- Инструмент: Cursor
- Затронутые компоненты: пакет `src/course_bringup`, относительное имя позы в `src/patrol`, `config/qos-overrides.yaml`, `.github/workflows/pr05.yml`, `README.md`, `evidence/pr05/`, этот файл
- Характер помощи: launch с аргументами, namespace и условной записью MCAP, ноды pose_relay и pose_subscriber, тесты QoS и завершения launch, workflow и черновик `report.json` по выводу локального запуска
- Проверка: `colcon build` и `colcon test --packages-select patrol course_bringup` выполнены локально в ROS 2 Lyrical: 30 tests, 0 errors, 0 failures, 2 skipped. Несовместимость reliable против best effort, поза после смены профиля, `ros2 bag info` на 1642 сообщения и оба echo при повторе той же записи сняты с turtlesim в домене 16 и лежат в `evidence/pr05`. Числа в отчёте не подставлены вместо симулятора.
