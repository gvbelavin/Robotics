"""Переложить позу черепахи в относительный sensor_pose с best effort."""

from course_bringup.qos import pose_message_type, sensor_profile
import rclpy
from rclpy.node import Node


class PoseRelay(Node):
    """Читать относительную позу и публиковать её как сенсорный поток."""

    def __init__(self):
        super().__init__('pose_relay')
        pose_type = pose_message_type()
        self.pose_sub = self.create_subscription(
            pose_type, 'turtle1/pose', self.on_pose, 10)
        self.sensor_pub = self.create_publisher(
            pose_type, 'sensor_pose', sensor_profile())
        self.get_logger().info(
            'subscribe %s, publish %s best_effort' % (
                self.resolve_topic_name('turtle1/pose'),
                self.resolve_topic_name('sensor_pose'),
            ))

    def on_pose(self, message):
        """Переслать позу без изменения полей."""
        self.sensor_pub.publish(message)


def main(args=None):
    """Создать relay и крутить его до Ctrl+C."""
    rclpy.init(args=args)
    node = None
    try:
        node = PoseRelay()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
