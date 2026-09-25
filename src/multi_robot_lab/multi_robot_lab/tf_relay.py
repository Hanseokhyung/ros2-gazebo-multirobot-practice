import copy

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    DurabilityPolicy,
    HistoryPolicy,
)
from tf2_msgs.msg import TFMessage


class TfRelay(Node):

    def __init__(self):
        super().__init__('tf_relay')

        tf_input_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=100,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )

        tf_output_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=100,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )

        static_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=100,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        self.tf_pub = self.create_publisher(
            TFMessage,
            '/tf',
            tf_output_qos
        )

        self.tf_static_pub = self.create_publisher(
            TFMessage,
            '/tf_static',
            static_qos
        )

        for namespace in ['robot5', 'robot11']:
            self.create_subscription(
                TFMessage,
                f'/{namespace}/tf',
                lambda msg, ns=namespace: self.relay(msg, ns, False),
                tf_input_qos
            )

            self.create_subscription(
                TFMessage,
                f'/{namespace}/tf_static',
                lambda msg, ns=namespace: self.relay(msg, ns, True),
                static_qos
            )

        self.get_logger().info(
            'TF relay running: robot5 + robot11 -> global TF'
        )

    def prefix_frame(self, frame, namespace):
        frame = frame.lstrip('/')

        if frame.startswith(namespace + '/'):
            return frame

        return namespace + '/' + frame

    def relay(self, msg, namespace, is_static):
        output = TFMessage()

        for transform in msg.transforms:
            parent = self.prefix_frame(
                transform.header.frame_id,
                namespace
            )

            child = self.prefix_frame(
                transform.child_frame_id,
                namespace
            )

            if parent == child:
                continue

            new_transform = copy.deepcopy(transform)

            new_transform.header.frame_id = parent
            new_transform.child_frame_id = child

            output.transforms.append(new_transform)

        if not output.transforms:
            return

        if is_static:
            self.tf_static_pub.publish(output)
        else:
            self.tf_pub.publish(output)


def main(args=None):
    rclpy.init(args=args)

    node = TfRelay()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
