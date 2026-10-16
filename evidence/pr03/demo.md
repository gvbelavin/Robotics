# ПР03. Как устроена нода patrol

Среда: ROS 2 Lyrical, `ROS_DOMAIN_ID=16`, тип позы `turtlesim_msgs/msg/Pose`. Симулятор поднят `ros2 launch turtle_bringup sim.launch.py`. На этом домене уже работал чужой `/teleop_turtle` (издатель `/turtle1/cmd_vel` без потока сообщений). Его не останавливали: до remap поза оставалась стартовой, после remap скорости совпали с командой patrol, а не с клавишами teleop.

## init, spin, callback, Ctrl+C

`rclpy.init` создаёт контекст процесса: подключение к middleware и разбор аргументов, в том числе `-r`. Пока init не вызван, ноды нет.

`Patrol()` только регистрирует концы графа. Подписка на `/turtle1/pose` сохранена в поле `pose_sub`. Её callback `on_pose` записывает последнее сообщение в `latest_pose` и больше ничего не делает. Издатель создан с относительным именем `cmd_vel`. Таймер 0,1 с вызывает `on_timer`.

`rclpy.spin` — это ожидание событий в том же потоке. Исполнитель сам вызывает `on_pose`, когда приходит поза, и `on_timer`, когда истекает период. Callback не вызывает другой callback и не крутит цикл.

До первой позы `command_from_pose` возвращает нули. После неё — `linear.x=0.5`, `angular.z=0.3`, уже ограниченные диапазонами `[0, 0.5]` и `[-1, 1]`.

`Ctrl+C` прерывает `spin` исключением `KeyboardInterrupt`. В `finally` нода уничтожается и вызывается `rclpy.try_shutdown`. Нулевой `Twist` при этом не публикуется. Исчезновение процесса — не команда торможения.

Это видно по времени в `pose-stop-timeline.txt`. В 05:22:16.477Z поза ещё была с `linear_velocity=0.5` и `angular_velocity=0.3` (`x=7.194882869720459`, `y=7.412644386291504`). SIGINT ноды — 05:22:18.429Z. Следующая поза уже с нулевыми скоростями (`x=7.0103583335876465`, `y=7.996688365936279`), и секунду спустя числа те же. `/turtlesim` при этом оставался в списке нод (`nodes-after-patrol-stop.txt`). Сам симулятор завершился только от SIGINT launch в 05:22:26.605Z: в `launch.txt` есть `signal_handler(signum=2)` и чистый выход процесса. После этого в графе остался прежний `/teleop_turtle`.

## Разрыв имени и remap

Без `-r` `ros2 node info /patrol` показывает издателя `/cmd_vel`. `ros2 topic info /cmd_vel --verbose`: publisher count 1 (`patrol`), subscription count 0. У `/turtle1/cmd_vel` подписчик — `turtlesim`, издатель patrol туда не входит. Поза не сдвинулась: `x=5.544444561004639`, `y=5.544444561004639`, обе скорости 0 (`pose-during-broken.txt`). Тип сообщения тот же, `geometry_msgs/msg/Twist`; не совпало полное имя.

Относительное `cmd_vel` в корневом пространстве имён становится `/cmd_vel`. Имя `/turtle1/cmd_vel` задано от корня графа и само к пространству имён ноды не добавляется.

Запуск `ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel` меняет только имя при старте. Код тот же. `node-info-fixed.txt` показывает издателя `/turtle1/cmd_vel`. Топика `/cmd_vel` больше нет (`info-cmd-vel-fixed.txt`: `Unknown topic '/cmd_vel'`). Поза пошла с `linear_velocity=0.5` и `angular_velocity=0.30000001192092896` (`pose-during-fixed.txt`).

На `/turtle1/cmd_vel` вместе с patrol остаётся издатель teleop, поэтому publisher count равен 2. Поток ненулевых `Twist` в этом прогоне даёт patrol: до него скорости были нулевыми, после него — ровно 0,5 и 0,3.

## Частота за 10 секунд

Таймер просит период 0,1 с. Это намерение, не гарантия. Измерение — `timeout --signal=INT 10s ros2 topic hz /turtle1/cmd_vel --qos-reliability reliable`. Стена часов: 05:22:05.322Z … 05:22:16.469Z. Последняя строка в `cmd-hz.txt`:

```text
average rate: 9.998
	min: 0.099s max: 0.101s std dev: 0.00040s window: 79
```

Реальная частота команды около 9,998 Гц, окно 79 сообщений.
