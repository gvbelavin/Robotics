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
