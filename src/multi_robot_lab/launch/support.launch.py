from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node

import os


def generate_launch_description():

    rviz_config = os.path.join(
        get_package_share_directory('multi_robot_lab'),
        'config',
        'two_robots.rviz'
    )

    return LaunchDescription([

        Node(
            package='multi_robot_lab',
            executable='tf_relay',
            name='tf_relay',
            output='screen',
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='world_to_robot5_map',
            arguments=[
                '--x', '1.582450',
                '--y', '2.547270',
                '--z', '0.0',
                '--yaw', '0.137750',
                '--pitch', '0.0',
                '--roll', '0.0',
                '--frame-id', 'world',
                '--child-frame-id', 'robot5/map',
            ],
            output='screen',
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='world_to_robot11_map',
            arguments=[
                '--x', '1.508200',
                '--y', '-2.588230',
                '--z', '0.0',
                '--yaw', '0.049462',
                '--pitch', '0.0',
                '--roll', '0.0',
                '--frame-id', 'world',
                '--child-frame-id', 'robot11/map',
            ],
            output='screen',
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': True}],
            output='screen',
        ),
    ])
