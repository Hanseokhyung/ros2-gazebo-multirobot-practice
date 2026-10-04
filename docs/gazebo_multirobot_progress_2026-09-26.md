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


# 2026-09-28 진행 기록

## 1. robot5 / robot11 TF 복구 완료

기존 Gazebo TF 경로에서 odom -> base_link TF가 안정적으로 나오지 않는 문제가 있었다.

Odometry 토픽 자체는 정상:
- /robot5/odom
  - frame_id: robot5/odom
  - child_frame_id: robot5/base_link
- /robot11/odom
  - frame_id: robot11/odom
  - child_frame_id: robot11/base_link

커스텀 odom_tf_relay를 사용해 Odometry 데이터를 TF로 변환하도록 구성했다.

확인 완료:

robot5:
robot5/map
└── robot5/odom
    └── robot5/base_link

robot11:
robot11/map
└── robot11/odom
    └── robot11/base_link

tf2_echo에서 다음 체인을 모두 확인했다.

robot5:
- robot5/odom -> robot5/base_link
- robot5/map -> robot5/odom
- robot5/map -> robot5/base_link

robot11:
- robot11/odom -> robot11/base_link
- robot11/map -> robot11/odom
- robot11/map -> robot11/base_link

## 2. support.launch.py 개선

기존 support.launch.py에 다음 두 노드를 추가했다.

- /robot5/odom_tf_relay
- /robot11/odom_tf_relay

현재 support.launch.py 역할:

- robot5 odom -> base_link TF relay
- robot11 odom -> base_link TF relay
- robot5/11 namespaced TF -> global /tf relay
- world -> robot5/map static TF
- world -> robot11/map static TF
- RViz 실행

따라서 별도 터미널에서 odom_tf_relay를 수동 실행할 필요가 없도록 정리했다.

## 3. LiDAR / SLAM 상태

수동 ros_gz_bridge를 통해 두 로봇 scan 데이터 정상 확인.

- /robot5/scan 정상
- /robot11/scan 정상

robot5에서는 약 19Hz 수준까지 확인했다.

slam_toolbox:
- /robot5/slam_toolbox active
- /robot11/slam_toolbox active

robot5 /robot5/tf에서 반복적으로 다음 두 transform 확인:

- robot5/map -> robot5/odom
- robot5/odom -> robot5/base_link

## 4. Nav2 lifecycle 활성화

robot5 초기 bringup 과정에서 lifecycle manager가 다음과 같은 일시적인 서비스 오류를 냈다.

route_server/get_state service client:
async_send_request failed

또한 controller_server/get_state 서비스를 오랫동안 기다리는 현상이 있었다.

하지만 이후 상태 확인 결과 robot5와 robot11 모두 주요 Nav2 lifecycle 노드가 active [3] 상태가 되었다.

확인 노드:

- controller_server
- smoother_server
- planner_server
- behavior_server
- route_server
- bt_navigator
- velocity_smoother
- collision_monitor

robot11도 동일하게 모두 active [3].

route_server 노드와 get_state/change_state 서비스 자체는 robot5/11 모두 존재했으므로
route_server 설정 자체의 문제로 판단하지 않았다.

## 5. explore_lite 진행

robot5 explore_lite 실행 시:

Waiting for costmap to become available, topic: map

이후:

Waiting to connect to move_base nav2 server

단계까지 진행했다.

Nav2 controller 로그에서는 실제 goal 및 path가 전달됨을 확인:

- Received a goal, begin computing control effort.
- Passing new path to controller.
- Failed to make progress

따라서 explore -> Nav2 goal 전달은 동작하고 있으나 실제 robot5 이동이 지속되지 않는 문제가 남아 있다.

## 6. robot5 속도 명령 경로 확인

토픽:

- /robot5/cmd_vel_nav
- /robot5/cmd_vel_smoothed
- /robot5/cmd_vel
- /robot5/cmd_vel_unstamped
- /robot5/diffdrive_controller/cmd_vel

구조 확인:

controller_server
-> /robot5/cmd_vel_nav
-> velocity_smoother
-> /robot5/cmd_vel_smoothed
-> collision_monitor
-> /robot5/cmd_vel
-> motion_control
-> /robot5/diffdrive_controller/cmd_vel
-> diff_drive_controller / Gazebo

motion_control:
- /robot5/cmd_vel 구독
- /robot5/cmd_vel_unstamped 구독
- /robot5/diffdrive_controller/cmd_vel 발행

controller_manager 상태:

- diffdrive_controller active
- joint_state_broadcaster active

## 7. 직접 구동 테스트

robot5 undock:
- 성공
- motion_control 로그에서 "Undock Goal Succeeded" 확인

RotateAngle 테스트:

요청:
- angle: 1.57 rad
- max_rotation_speed: 0.35 rad/s

실제 /robot5/diffdrive_controller/cmd_vel에서:

angular.z ~= 0.35

확인.

로봇은 조금 회전했으나 90도 전체 회전 전에 중단됨.

마지막 feedback 예:

remaining_angle_travel: 1.403721...

결과:
Goal finished with status: ABORTED

DriveDistance 테스트:

요청:
- distance: -0.25 m
- max_translation_speed: 0.20 m/s

처음에 로봇이 조금 이동했으나 이후 정지.

feedback가 반복적으로 거의 동일하게 유지:

remaining_travel_distance ~= -0.3477

따라서 액션 서버 및 motion_control 명령 생성 자체는 동작하지만
실제 로봇 이동이 중간에 멈추는 원인은 추가 확인이 필요하다.

## 8. hazard 확인

/robot5/hazard_detection:

detections: []

/robot5/ir_intensity:

value: 15

현재 확인된 시점에는 bumper/cliff 계열 hazard가 직접 검출되지는 않았다.

## 9. 현재 가장 큰 환경 문제: FastDDS SHM

오늘 전체 테스트 동안 반복적으로 다음 오류 발생:

RTPS_TRANSPORT_SHM Error
Failed init_port fastrtps_port7085:
open_and_lock_file failed

증상:

- ros2 lifecycle get 응답이 매우 늦음
- service discovery가 수십 초 지연됨
- ros2 topic echo가 메시지를 못 받는 경우 발생
- ros2 topic pub 실행 중 context invalid 오류 발생
- failed to create timer
- failed to initialize wait set

FASTDDS_BUILTIN_TRANSPORTS=UDPv4를 테스트 터미널에 적용하여 일부 CLI 테스트를 계속 진행했으나
전체 실행환경 자체는 이미 SHM 오류가 누적된 상태였다.

따라서 다음 세션에서는 로봇 구동 문제를 더 추적하기 전에
모든 ROS/Gazebo 프로세스를 완전히 종료한 상태에서 FastDDS SHM을 먼저 정리한다.

## 10. 다음 시작 지점

다음 세션 순서:

1. 모든 ROS/Gazebo 프로세스 종료 상태 확인
2. FastDDS SHM 상태 확인 및 안전하게 cleanup
3. ros2 node list 등 CLI 응답 정상 여부 확인
4. Gazebo + robot5 하나만 최소 구성으로 실행
5. robot5 undock
6. RotateAngle / DriveDistance 단독 구동 테스트
7. 정상 구동 확인 후 SLAM + Nav2 추가
8. robot5 explore_lite 재실행
9. robot11 추가
10. map_merge 진행

현재까지 해결 완료:

- 두 로봇 LiDAR
- 두 로봇 SLAM
- robot5/11 odom -> base_link TF
- map -> odom -> base_link 전체 TF 체인
- global TF relay
- support.launch.py 통합
- Nav2 lifecycle 활성화
- explore -> Nav2 goal 전달 확인

현재 핵심 미해결:

- FastDDS SHM 오류
- robot5가 RotateAngle / DriveDistance 중 조금 움직인 뒤 멈추는 문제
- 안정적인 AutoSLAM 실제 주행

---

# 2026-10-04 Gazebo 멀티로봇 실습 종료

## 최종 상태

Gazebo 기반 TurtleBot4 멀티로봇 실습은 아래 항목까지 검증하였다.

- TurtleBot4 2대 namespace 분리
  - `/robot5`
  - `/robot11`
- 각 로봇 odom / TF 구조 분리
- `odom -> base_link` TF relay 구현
- namespaced TF를 global `/tf`, `/tf_static`으로 relay
- `world -> robot5/map`
- `world -> robot11/map`
- RViz2에서 멀티로봇 TF / RobotModel / Scan / Map 구성
- robot5 / robot11 각각 `slam_toolbox` 실행
- robot5 / robot11 각각 Nav2 lifecycle active 확인
- `explore_lite`에서 Nav2 goal 전달까지 확인
- Gazebo LiDAR raw topic을 ROS2 `/robot5/scan`, `/robot11/scan`으로 수동 bridge하여 사용
- multi-robot map merge 패키지 설치 및 후속 구조 검토

## 미완료 항목

아래 항목은 Gazebo 환경에서 최종 완료하지 않았다.

- 두 로봇의 안정적인 장시간 AutoSLAM
- 최종 merged `/map` 생성
- merged map 저장

## 종료 사유

robot spawn 시 Gazebo `gz-sim-sensors-system`의 rendering thread에서 반복적으로 crash가 발생하였다.

대표 증상:

- `Scene already exists with name: scene`
- `SensorsPrivate::RenderThread()`
- `OgreScene::InitImpl()`
- `Segmentation fault` / `Aborted`

DDS / ROS2 namespace / TF 문제와는 별개의 Gazebo rendering / sensor 초기화 문제로 판단하였다.

world의 sensor render engine도 확인 및 테스트하였으나 동일한 crash가 반복되어,
Gazebo 자체 디버깅에 시간을 더 사용하지 않고 프로젝트를 종료하기로 결정하였다.

## 다음 단계

멀티로봇 SLAM 구조는 Isaac Sim 기반 IDC / 병원 자동화 프로젝트로 이관한다.

예정 구조:

Isaac Sim
- AMR1 / AMR2
- 2D LiDAR
- odometry
- TF
- ROS2 Bridge

ROS2
- slam_toolbox x2
- Nav2
- autonomous exploration
- multirobot_map_merge
- RViz2
- map_saver

Gazebo 프로젝트의 목적이었던 멀티로봇 namespace / TF / SLAM / Nav2 구조 학습은 완료하였으며,
최종 멀티로봇 AutoSLAM 및 map merge 검증은 Isaac Sim 환경에서 계속한다.
