"""Профили QoS сенсорного потока и подписчика."""

from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy


def pose_message_type():
    """Вернуть тип позы turtlesim для текущей дистрибуции ROS."""
    try:
        from turtlesim_msgs.msg import Pose
    except ImportError:
        from turtlesim.msg import Pose
    return Pose


def _profile(reliability):
    """Собрать keep_last 10, volatile и заданную надёжность."""
    return QoSProfile(
        reliability=reliability,
        durability=DurabilityPolicy.VOLATILE,
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
    )


def sensor_profile():
    """Профиль издателя sensor_pose: best effort не обслуживает reliable."""
    return _profile(ReliabilityPolicy.BEST_EFFORT)


def subscriber_profile(name):
    """Вернуть профиль подписчика для reliable или best_effort."""
    reliability = {
        'reliable': ReliabilityPolicy.RELIABLE,
        'best_effort': ReliabilityPolicy.BEST_EFFORT,
    }.get(name)
    if reliability is None:
        raise ValueError(
            'reliability должен быть reliable или best_effort, получено: %s'
            % name)
    return _profile(reliability)
