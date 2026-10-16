# ПР04. Параметры движения

Среда: ROS 2 Lyrical, `ROS_DOMAIN_ID=16`, `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`. Тип позы: `turtlesim_msgs/msg/Pose`. Симулятор поднят `ros2 launch turtle_bringup sim.launch.py`. Нода: `ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel`.

Стартовые значения:

```text
$ ros2 param get /patrol linear_speed --no-daemon --spin-time 2
Double value is: 0.5

$ ros2 param get /patrol turn_rate --no-daemon --spin-time 2
Double value is: 0.3

$ ros2 param get /patrol publish_hz --no-daemon --spin-time 2
Double value is: 10.0
```

`ros2 param list /patrol` показывает `linear_speed`, `turn_rate`, `publish_hz`.

## 10 Гц → 5 Гц

До смены, 10 секунд `ros2 topic hz /turtle1/cmd_vel --qos-reliability reliable --spin-time 1`:

```text
average rate: 10.000
	min: 0.099s max: 0.101s std dev: 0.00042s window: 79
```

```text
$ ros2 param set /patrol publish_hz 5.0 --no-daemon --spin-time 2
Set parameter successful

$ ros2 param get /patrol publish_hz --no-daemon --spin-time 2
Double value is: 5.0
```

Те же 10 секунд `ros2 topic hz`:

```text
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00041s window: 39
```

Период стал около 0,2 с. Обратная установка `publish_hz 10.0` снова дала `average rate: 10.000`, окно 79, `min: 0.099s max: 0.101s`.

`linear_speed 0.8` и `turn_rate 0.6` приняты. Следующая поза:

```text
x: 7.4605841636657715
y: 8.755001068115234
theta: 3.096029281616211
linear_velocity: 0.800000011920929
angular_velocity: 0.6000000238418579
```

`linear_speed 2.0` отклонён: `Setting parameter failed: linear_speed вне диапазона [0.0, 1.0]`. `ros2 param get` остался `Double value is: 0.8`.

## Ноль без проверки частоты

В рабочей копии на время этого запуска проверка диапазона не смотрела на `publish_hz`: условие стало `name != 'publish_hz'`. Нода запущена заново, `ros2 param get /patrol publish_hz` перед запросом — `Double value is: 10.0`.

```text
$ ros2 param set /patrol publish_hz 0.0 --no-daemon --spin-time 2 --service-timeout 5
Timed out waiting for set_parameters response from node /patrol (timeout: 5.0s)
```

Код завершения клиента — 1. В stderr ноды:

```text
File ".../patrol/patrol.py", line 92, in _restart_timer
    period = 1.0 / self.publish_hz
ZeroDivisionError: division by zero
[ros2run]: Process exited with failure 1
```

`ros2 node list --no-daemon --spin-time 2` после этого напечатал только `/turtlesim`. Поток `Twist` прекратился вместе с процессом: период `1/0` вычислялся в callback службы параметров, исключение вышло из `rclpy.spin`, ответ клиенту не был отправлен.

Проверка диапазона возвращена в файл до коммита реализации. Полный traceback — `unchecked.txt`.

## Тот же запрос после проверки

Новая нода со включённой проверкой. Перед отказом поток был `average rate: 10.000`, окно 79.

```text
$ ros2 param set /patrol publish_hz 0.0 --no-daemon --spin-time 2 --service-timeout 5
Setting parameter failed: publish_hz вне диапазона [1.0, 30.0]

$ ros2 param get /patrol publish_hz --no-daemon --spin-time 2
Double value is: 10.0
```

Следующие 10 секунд `ros2 topic hz /turtle1/cmd_vel --qos-reliability reliable --spin-time 1`:

```text
average rate: 10.000
	min: 0.099s max: 0.101s std dev: 0.00040s window: 79
```

Значение параметра и поток команд остались прежними. Отрицательное значение:

```text
$ ros2 param set /patrol publish_hz -1.0 --no-daemon --spin-time 2 --service-timeout 5
Setting parameter failed: publish_hz вне диапазона [1.0, 30.0]

$ ros2 param get /patrol publish_hz --no-daemon --spin-time 2
Double value is: 10.0
```

Слово `nan` в CLI пришло строкой, и rclpy отклонил тип до нашей функции: `Setting parameter failed: Wrong parameter type, expected '3' got '4'`. `param get` остался `10.0`. Конечные `nan` и `inf`, ноль и отрицательная частота отклоняются тестом `validate_values` в `tests.txt`.

## /clear и /turtle1/rotate_absolute

Patrol остановлен, turtlesim ещё в графе. Поза до очистки:

```text
x: 8.661500930786133
y: 5.928821563720703
theta: 0.6001322865486145
linear_velocity: 0.0
angular_velocity: 0.0
```

```text
$ ros2 service type /clear
std_srvs/srv/Empty

$ ros2 service call /clear std_srvs/srv/Empty "{}" --timeout 5
response:
std_srvs.srv.Empty_Response()
```

Поза после вызова совпала побайтно с позой до него. После `ros2 daemon stop`:

```text
$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim_msgs/action/RotateAbsolute]

$ ros2 action info /turtle1/rotate_absolute
Action servers: 1
    /turtlesim
```

`ros2 interface show turtlesim_msgs/action/RotateAbsolute` показывает цель `theta`, результат `delta` и обратную связь `remaining`.

Запрос `/clear` — один вызов и один ответ: клиент посылает пустой `std_srvs/srv/Empty`, сервер сразу возвращает пустой ответ, поза черепахи не меняется. Цель `/turtle1/rotate_absolute` длится во времени: клиент задаёт абсолютный угол `theta`, сервер по ходу может сообщать `remaining` и в конце отдаёт `delta`.
