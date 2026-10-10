# Команды ПР02

Среда: ROS 2 Lyrical, `ROS_DOMAIN_ID=16`, корень workspace — корень репозитория. Установленный `turtlesim` лежит в `/opt/ros/lyrical`; это не текущий каталог.

## Три команды Linux

### `pwd`

```bash
cd "$(git rev-parse --show-toplevel)"
pwd
```

Назначение: убедиться, что оболочка стоит в корне репозитория. Этот каталог и есть корень workspace.

Результат: `/home/gleb/robot`.

### `mkdir -p src evidence/pr02`

Назначение: создать каталог исходников и вложенный каталог свидетельств. `-p` создаёт недостающих родителей и не завершается ошибкой, если каталог уже есть.

Результат: появились `src/` и `evidence/pr02/`.

### `printenv ROS_DISTRO ROS_DOMAIN_ID`

Назначение: прочитать настройки уже текущего терминала, не меняя их.

Результат:

```text
lyrical
16
```

Рядом `ls -a` показал скрытые файлы корня: `.course-kit`, `.git`, `.github`, `.gitignore`, `AI_USAGE.md`, `course-kit.tar.gz`, `evidence`. `ros2 pkg prefix turtlesim` напечатал `/opt/ros/lyrical`. Путь установленного пакета и `pwd` — разные места.

## `>` и `|`, `source` и новая программа

`>` перенаправляет stdout в файл и заменяет прежнее содержимое. Следующая команда этот поток не читает.

`|` передаёт stdout следующей команде. Сам по себе файл не создаёт. В сборке использовано оба приёма сразу:

```bash
set -o pipefail
colcon build --symlink-install --packages-select turtle_bringup \
  2>&1 | tee evidence/pr02/build.txt
```

`2>&1` присоединяет stderr к stdout. `tee` и показывает этот поток, и пишет его в файл. `pipefail` сохраняет ненулевой статус, если `colcon` завершился с ошибкой, даже когда `tee` сам отработал успешно.

`source /opt/ros/lyrical/setup.bash` выполняет файл в текущей оболочке, поэтому `AMENT_PREFIX_PATH` и остальные переменные остаются в этом терминале. Запуск того же файла новой программой (`bash /opt/ros/lyrical/setup.bash`) создал бы отдельный процесс: его `export` исчез бы вместе с ним, и текущий терминал ROS не увидел бы.

## Сборка и launch

Пустой пакет, ещё без `launch/`, собрался из корня. Лог `build-empty.txt`:

```text
Starting >>> turtle_bringup
Finished <<< turtle_bringup [1.93s]
Summary: 1 package finished [2.12s]
```

После `source install/setup.bash` префикс был `/home/gleb/robot/install/turtle_bringup`. В `share/turtle_bringup` лежали только метаданные, каталога `launch` не было. Сборка и `source` нашли пакет, но процесс не запустили.

После добавления `sim.launch.py` и записи в `data_files` повторная сборка (`build.txt`) тоже завершилась одной успешной пакетой за 1.83 с. Установленный файл:

```text
/home/gleb/robot/install/turtle_bringup/share/turtle_bringup/launch/sim.launch.py
```

Файл в `src/` сам по себе ещё не установленный ресурс. Нода появляется только когда launch его запускает.

Запуск и остановка:

```bash
source /opt/ros/lyrical/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py
ros2 node list --no-daemon --spin-time 2
```

Launch написал `process started` и `Starting turtlesim with node name /turtlesim`. `ros2 node list` показал `/turtlesim`. SIGINT (`signum=2`, как Ctrl+C) дал в логе `signal_handler` и `process has finished cleanly`. Следующий `ros2 node list` ноды `/turtlesim` уже не содержал. Запущенный этим launch процесс завершился вместе с ним.

Тот же запуск повторён для опыта с командой. В графе при этом уже был чужой `/teleop_turtle`: процесс `turtle_teleop_key` от 9 октября принадлежит root, остановить его без прав нельзя. Он издатель `/turtle1/cmd_vel` и не подписчик этого топика. Клавиши ему не отправлялись; ниже видно, что поза менялась только от наших публикаций в полное имя.

## Команда, сбой имени, исправление

Тип и поза до команды:

```bash
ros2 interface show geometry_msgs/msg/Twist
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose --once
```

Тип позы: `turtlesim_msgs/msg/Pose`. Начальная поза:

```text
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

Ожидание для `{linear: {x: 1.0}, angular: {z: 0.5}}`: положительный `linear.x` двигает черепаху вперёд по текущему курсу, положительный `angular.z` поворачивает против часовой стрелки. При `theta` около нуля это рост `x` и небольшой поворот влево. Одна публикация не держит скорость.

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Поза после неё:

```text
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
linear_velocity: 0.0
angular_velocity: 0.0
```

`x` и `theta` выросли, скорости снова нулевые: без новых сообщений turtlesim остановился.

### Сбой: то же сообщение в `/cmd_vel`

Скорость, домен и тип не менялись. Изменено только имя топика.

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Пока издатель работал:

| Топик | Издатели | Подписчики |
| --- | --- | --- |
| `/cmd_vel` | 1, нода `_ros2cli_97168` | 0 |
| `/turtle1/cmd_vel` | 1, нода `teleop_turtle` | 1, нода `turtlesim` |

Поза осталась `x: 6.509308815002441`, `y: 5.796990871429443`, `theta: 0.5040000081062317`, скорости 0. Издатель в графе был виден, turtlesim его сообщения не получал.

Правильного типа недостаточно. Оба топика несли `geometry_msgs/msg/Twist`, но доставка идёт по полному имени. Подписка turtlesim висит на `/turtle1/cmd_vel`. Сообщение в `/cmd_vel` обнаружено как публикация и никому не доставлено.

### После: исправлено только имя

Издатель остановлен через SIGINT. Повтор той же команды с тем же Twist, той же частотой и тем же доменом, имя заменено на `/turtle1/cmd_vel`.

`/cmd_vel` после остановки ошибочного издателя: `Unknown topic '/cmd_vel'`.

`/turtle1/cmd_vel`: издателей 2 (`_ros2cli_97323` и прежний `teleop_turtle`), подписчик 1 — `turtlesim`.

Поза во время этой публикации:

```text
x: 6.49107027053833
y: 9.30190658569336
theta: 2.640000104904175
linear_velocity: 1.0
angular_velocity: 0.5
```

Скорости совпали с отправленным Twist, `theta` и `y` заметно выросли: команда дошла до подписчика. После остановки издателя скорости вернулись к нулю (`linear_velocity: 0.0`, `angular_velocity: 0.0`), поза остановилась на `x: 5.794905662536621`, `y: 9.527667999267578`, `theta: 3.007999897003174`.

Полный вывод `ros2 topic info --verbose` сохранён в `info-cmd-vel-broken.txt`, `info-turtle-cmd-broken.txt` и `info-turtle-cmd-fixed.txt`.
