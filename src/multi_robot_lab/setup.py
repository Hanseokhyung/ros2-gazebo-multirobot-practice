from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'multi_robot_lab'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        (
            'share/' + package_name,
            ['package.xml'],
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py'),
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*'),
        ),
        (
            os.path.join('share', package_name, 'worlds'),
            glob('worlds/*'),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='han',
    maintainer_email='han@todo.todo',
    description='Gazebo multi-robot practice package',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
	    'tf_relay = multi_robot_lab.tf_relay:main',
            'odom_tf_relay = multi_robot_lab.odom_tf_relay:main',
        ],
    },
)
