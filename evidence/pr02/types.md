# Типы сообщений ПР02

Дистрибутив: Lyrical. Имена и типы сняты командами `ros2 interface show`, `ros2 topic type` и `ros2 topic info` при запущенном turtlesim.

## Топики

| Топик | Тип | Назначение |
| --- | --- | --- |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | Команда скорости для черепахи `turtle1` |
| `/turtle1/pose` | `turtlesim_msgs/msg/Pose` | Поза и фактические скорости той же черепахи |

На Jazzy тип позы был бы `turtlesim/msg/Pose`. Здесь `ros2 topic type /turtle1/pose` напечатал `turtlesim_msgs/msg/Pose`.

`/cmd_vel` в этом опыте — ошибочное имя. У него тот же тип Twist, но подписчика turtlesim нет.

## `geometry_msgs/msg/Twist`

```text
Vector3 linear
    float64 x
    float64 y
    float64 z
Vector3 angular
    float64 x
    float64 y
    float64 z
```

`linear` — линейная скорость, м/с. Для turtlesim рабочее поле — `linear.x`: движение вперёд вдоль текущего курса. `linear.y` и `linear.z` симулятор не использует.

`angular` — угловая скорость, рад/с. Рабочее поле — `angular.z`: вращение вокруг вертикальной оси. Положительное значение поворачивает против часовой стрелки. `angular.x` и `angular.y` не используются.

В опыте отправлялось `linear.x = 1.0` и `angular.z = 0.5`.

## `turtlesim_msgs/msg/Pose`

```text
float32 x
float32 y
float32 theta
float32 linear_velocity
float32 angular_velocity
```

`x` и `y` — положение в окне turtlesim, `theta` — курс в радианах. `linear_velocity` и `angular_velocity` — скорости, с которыми черепаха движется сейчас. После одиночной публикации они возвращаются к нулю: одно сообщение Twist не задаёт бесконечное движение.
