from geometry_msgs.msg import Twist
from patrol.command import command_from_pose
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

    def __init__(self):
        super().__init__('patrol')
        self.latest_pose = None
        pose_type = pose_message_type()
        self.pose_sub = self.create_subscription(
            pose_type, '/turtle1/pose', self.on_pose, 10)
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.on_timer)

    def on_pose(self, message):
        """Сохранить последнее сообщение позы и ничего больше не делать."""
        self.latest_pose = message

    def on_timer(self):
        """Опубликовать команду, выбранную по последней сохранённой позе."""
        linear_x, angular_z = command_from_pose(self.latest_pose)
        command = Twist()
        command.linear.x = linear_x
        command.angular.z = angular_z
        self.cmd_pub.publish(command)


def main(args=None):
    """Инициализировать контекст, крутить ноду и освободить её по Ctrl+C."""
    rclpy.init(args=args)
    node = Patrol()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
