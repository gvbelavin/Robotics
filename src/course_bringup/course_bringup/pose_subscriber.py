"""Подписчик sensor_pose с надёжностью из параметра."""

from course_bringup.qos import pose_message_type, subscriber_profile
import rclpy
from rclpy.node import Node


class PoseSubscriber(Node):
    """Слушать относительный sensor_pose выбранным профилем QoS."""

    def __init__(self):
        super().__init__('pose_subscriber')
        self.declare_parameter('reliability', 'best_effort')
        reliability = self.get_parameter('reliability').value
        try:
            profile = subscriber_profile(reliability)
        except ValueError:
            self.destroy_node()
            raise
        pose_type = pose_message_type()
        self.pose_sub = self.create_subscription(
            pose_type, 'sensor_pose', self.on_pose, profile)
        self.count = 0
        self.get_logger().info(
            'reliability=%s topic=%s' % (
                reliability, self.resolve_topic_name('sensor_pose')))

    def on_pose(self, message):
        """Посчитать доставленную позу и записать её в лог."""
        self.count += 1
        self.get_logger().info(
            'pose x=%.3f y=%.3f count=%d' % (
                message.x, message.y, self.count))


def main(args=None):
    """Создать подписчика и крутить его до Ctrl+C."""
    rclpy.init(args=args)
    node = None
    try:
        node = PoseSubscriber()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
