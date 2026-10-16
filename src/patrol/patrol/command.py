"""Выбор команды скорости по последней сохранённой позе."""

MAX_LINEAR_X = 0.5
MAX_ANGULAR_Z = 1.0


def command_from_pose(pose, linear_x=0.5, angular_z=0.3):
    """
    Вернуть linear.x и angular.z либо нули, если позы ещё нет.

    Запрошенные скорости ограничиваются: linear.x входит в [0, 0.5],
    angular.z входит в [-1, 1].
    """
    if pose is None:
        return 0.0, 0.0
    limited_linear = min(max(float(linear_x), 0.0), MAX_LINEAR_X)
    limited_angular = min(max(float(angular_z), -MAX_ANGULAR_Z), MAX_ANGULAR_Z)
    return limited_linear, limited_angular
