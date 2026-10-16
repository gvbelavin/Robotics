from geometry_msgs.msg import Twist
from patrol.command import command_from_pose
from patrol.parameters import validate_values, values_with_update
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node


def pose_message_type():
    """Вернуть тип позы turtlesim для текущей дистрибуции ROS."""
    try:
        from turtlesim_msgs.msg import Pose
    except ImportError:
        from turtlesim.msg import Pose
    return Pose


class Patrol(Node):
    """Хранить последнюю позу и публиковать Twist по таймеру."""

    def __init__(self, **kwargs):
        super().__init__('patrol', **kwargs)
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('turn_rate', 0.3)
        self.declare_parameter('publish_hz', 10.0)
        self.latest_pose = None
        self.timer = None
        self.linear_speed = None
        self.turn_rate = None
        self.publish_hz = None
        linear_speed = self.get_parameter('linear_speed').value
        turn_rate = self.get_parameter('turn_rate').value
        publish_hz = self.get_parameter('publish_hz').value
        ok, reason = validate_values(linear_speed, turn_rate, publish_hz)
        if not ok:
            self.destroy_node()
            raise ValueError(reason)
        self._apply(linear_speed, turn_rate, publish_hz)
        pose_type = pose_message_type()
        self.pose_sub = self.create_subscription(
            pose_type, 'turtle1/pose', self.on_pose, 10)
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.add_on_set_parameters_callback(self.on_set_parameters)

    def on_pose(self, message):
        """Сохранить последнее сообщение позы и ничего больше не делать."""
        self.latest_pose = message

    def on_timer(self):
        """Опубликовать команду, выбранную по последней сохранённой позе."""
        self.cmd_pub.publish(self.command_twist())

    def command_twist(self):
        """Собрать Twist из текущих linear_speed и turn_rate."""
        linear_x, angular_z = command_from_pose(
            self.latest_pose, self.linear_speed, self.turn_rate)
        command = Twist()
        command.linear.x = linear_x
        command.angular.z = angular_z
        return command

    def on_set_parameters(self, params):
        """Принять тройку настроек целиком или оставить прежнее состояние."""
        updates = {}
        for param in params:
            if param.name in ('linear_speed', 'turn_rate', 'publish_hz'):
                updates[param.name] = param.value
        if not updates:
            return SetParametersResult(successful=True)
        linear_speed, turn_rate, publish_hz = values_with_update(
            self.linear_speed, self.turn_rate, self.publish_hz, updates)
        ok, reason = validate_values(linear_speed, turn_rate, publish_hz)
        if not ok:
            return SetParametersResult(successful=False, reason=reason)
        self._apply(linear_speed, turn_rate, publish_hz)
        return SetParametersResult(successful=True)

    def _apply(self, linear_speed, turn_rate, publish_hz):
        """Записать уже проверенные числа и сменить таймер только с частотой."""
        linear_speed = float(linear_speed)
        turn_rate = float(turn_rate)
        publish_hz = float(publish_hz)
        hz_changed = self.publish_hz is None or publish_hz != self.publish_hz
        self.linear_speed = linear_speed
        self.turn_rate = turn_rate
        if hz_changed:
            self.publish_hz = publish_hz
            self._restart_timer()

    def _restart_timer(self):
        """Остановить прежний таймер и оставить один с периодом 1/publish_hz."""
        period = 1.0 / self.publish_hz
        previous = self.timer
        if previous is not None:
            self.destroy_timer(previous)
            self.timer = None
        self.timer = self.create_timer(period, self.on_timer)


def main(args=None):
    """Инициализировать контекст, крутить ноду и освободить её по Ctrl+C."""
    rclpy.init(args=args)
    node = None
    try:
        node = Patrol()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
