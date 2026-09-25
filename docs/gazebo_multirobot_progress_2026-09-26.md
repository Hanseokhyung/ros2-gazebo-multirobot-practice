# Gazebo Multi-Robot Practice Progress

## 현재 구성

- ROS 2 Jazzy
- Gazebo / TurtleBot4
- ROS_DOMAIN_ID=60
- robot5 / robot11 멀티로봇 구성
- world: idc_world_final

## 완료된 항목

- Gazebo world 실행
- robot5 spawn
- robot11 spawn
- 두 로봇 namespace 분리
- RViz에서 두 로봇 표시
- robot5 / robot11 LaserScan 표시
- robot5 / robot11 SLAM 설정 파일 분리
- robot5 / robot11 Nav2 설정 파일 분리
- robot5 / robot11 explore_lite 설정 파일 분리
- global RViz용 tf_relay 구현
- world -> robot5/map static TF
- world -> robot11/map static TF
- support.launch.py 구성
- /robot5/map 생성 확인
- /robot11/map 생성 확인
- explore_lite -> Nav2 action server 연결 확인

## 외부 워크스페이스 수정 사항

아래 파일은 이 Git 저장소 외부의 ~/turtlebot4_ws 에 존재한다.

### TurtleBot4 RPLIDAR range

파일:

~/turtlebot4_ws/src/turtlebot4/turtlebot4_description/urdf/sensors/rplidar.urdf.xacro

현재 테스트 설정:

- r_min: 0.10 m
- r_max: 0.80 m
- r_res: 0.01 m

AutoSLAM 테스트 시 회전만으로 넓은 영역 전체를 인식하지 않도록
LiDAR 범위를 의도적으로 제한하였다.

### explore_lite OccupancyGrid QoS 수정

파일:

~/turtlebot4_ws/src/m-explore-ros2/explore/src/costmap_client.cpp

full map subscriber를 다음 QoS로 수정:

- Reliability: RELIABLE
- Durability: TRANSIENT_LOCAL
- History: KeepLast(1)

이유:

slam_toolbox의 /map publisher가 TRANSIENT_LOCAL인데
explore_lite 기본 subscriber가 VOLATILE이라 늦게 실행된 explore_lite가
기존 OccupancyGrid를 받지 못하고

Waiting for costmap to become available

상태에서 대기하는 문제가 발생했다.

## 현재 디버깅 상태

Gazebo 내부 RPLIDAR 원본 토픽은 정상적으로 메시지를 생성한다.

기본 turtlebot4 spawn에서 생성된 lidar_bridge는 endpoint는 존재하지만
실제 /robot5/scan, /robot11/scan 전달이 불안정했다.

별도 ros_gz_bridge parameter_bridge를 실행하면 두 로봇 scan 수신이 확인된다.

현재 임시 구성:

- /robot5/scan: 수동 bridge 사용
- /robot11/scan: 수동 bridge 사용

robot5 /odom 메시지는 정상적으로 생성된다.

예:

- frame_id: robot5/odom
- child_frame_id: robot5/base_link

하지만 Gazebo의 /model/robot5/turtlebot4/tf 토픽은 이름만 존재하고
실제 메시지가 생성되지 않는 현상을 확인하였다.

따라서 odometry 메시지를 TF로 변환하기 위한
odom_tf_relay.py를 구현했으며 현재 검증 중이다.

## 남은 문제

1. odom_tf_relay의 /robot5/tf publish 검증
2. robot11 odom -> base_link TF 처리
3. slam_toolbox map -> odom TF 안정화
4. Nav2 lifecycle 자동 bringup 안정화
5. FastDDS SHM 오류 정리
6. robot5 explore_lite AutoSLAM 실제 주행
7. robot11 explore_lite AutoSLAM 실제 주행
8. multirobot_map_merge
9. merged map 저장
10. merged map 기반 localization / patrol

## 현재 주요 TF 목표 구조

world
├── robot5/map
│   └── robot5/odom
│       └── robot5/base_link
└── robot11/map
    └── robot11/odom
        └── robot11/base_link

