# Robotics

Личный репозиторий практикума ROS 2. Среда этой работы: ROS 2 Lyrical, `ROS_DOMAIN_ID=16`.

## ПР02. Пакет и запуск turtlesim

Из корня репозитория, в терминале с базовой установкой ROS:

```bash
source /opt/ros/lyrical/setup.bash
colcon build --symlink-install --packages-select turtle_bringup
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py
```

Launch-файл ставится в `share/turtle_bringup/launch/sim.launch.py`. Проверка:

```bash
ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
```

Одна команда скорости:

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

`Ctrl+C` в терминале launch завершает turtlesim, который он запустил. Наблюдения лежат в `evidence/pr02/`.

## ПР03. Нода patrol: поза и команда

Пакет `turtle_bringup` остаётся. Рядом — `src/patrol`, команда `patrol`.

```bash
source /opt/ros/lyrical/setup.bash
colcon build --symlink-install --packages-select patrol
source install/setup.bash
export ROS_DOMAIN_ID=16
python3 -m pytest src/patrol/test
```

В одном терминале симулятор, в другом нода. Без remap издатель пишет в относительный `cmd_vel` (`/cmd_vel`) и не соединён с `/turtle1/cmd_vel`. Связь исправляет запуск:

```bash
ros2 launch turtle_bringup sim.launch.py
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Наблюдения лежат в `evidence/pr03/`.

## ПР04. Параметры движения

Та же нода `patrol`. Скорость, поворот и частота — параметры `linear_speed`, `turn_rate` и `publish_hz`.

```bash
source /opt/ros/lyrical/setup.bash
colcon build --symlink-install --packages-select patrol
source install/setup.bash
export ROS_DOMAIN_ID=16
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
python3 -m pytest src/patrol/test
ros2 launch turtle_bringup sim.launch.py
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
ros2 param set /patrol publish_hz 5.0
ros2 param set /patrol publish_hz 0.0
```

Ноль и другие значения вне 1–30 Гц отклоняются до пересоздания таймера. Наблюдения лежат в `evidence/pr04/`.

## ПР05. Launch, QoS и повтор записи

Пакет `course_bringup` поднимает turtlesim, `patrol` и relay позы одной командой. Имена внутри нод относительные: `turtle1/pose`, `cmd_vel`, `sensor_pose`. Launch помещает patrol и relay в `namespace` и переназначает команду и позу на глобальную черепаху. `sensor_pose` издаётся с best effort. Подписчик берёт `subscriber_reliability`. Запись MCAP стартует только при `record:=true`.

```bash
source /opt/ros/lyrical/setup.bash
colcon build --symlink-install --packages-select patrol course_bringup
source install/setup.bash
export ROS_DOMAIN_ID=16
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
python3 -m pytest src/course_bringup/test/test_qos.py src/course_bringup/test/test_launch_description.py
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=best_effort record:=false
```

Повтор записи:

```bash
ros2 bag play evidence/pr05/bag \
  --qos-profile-overrides-path config/qos-overrides.yaml
```

Наблюдения лежат в `evidence/pr05/`.
