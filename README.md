# ROS2 Gazebo Multi-Robot Practice

ROS 2 Jazzy와 Gazebo를 이용한 개인 Multi-Robot 실습 프로젝트.

Gazebo 실습은 2026-10-04 센서 렌더링 crash로 종료했다. 멀티로봇 namespace·TF·SLAM·Nav2 구조를 바탕으로, **[hp_dt](https://github.com/Hanseokhyung/hp_dt)의 Isaac Sim 환경에서 AMR 두 대의 자동 SLAM·맵 병합 검증을 이어간다.** 이 저장소는 당시 구현과 시행착오를 보존한다.

이관 대상, 구조 변경, 실제 확인 범위는 **[Isaac Sim 이관 기록](docs/02_isaac_transfer.md)**에 정리했다. 아래 Goal은 초기 목표이며, 완료 상태는 Progress를 기준으로 읽는다.

## Goal

TurtleBot4 2대를 Gazebo에서 운용하여 다음 과정을 직접 구현한다.

- Two Robot Spawn
- One RViz / Two Robots
- Multi-Robot TF / Namespace
- Automatic SLAM
- Map Merge
- Merged Map Save
- AMCL + Nav2
- Multi-Robot Patrol
- Gazebo Object Detection
- YOLO Integration

## Environment

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- RViz2
- TurtleBot4
- slam_toolbox
- multirobot_map_merge
- Nav2
- YOLO

## Progress

| Gazebo에서 확인한 범위 | 완료하지 못한 범위 |
|---|---|
| 두 로봇 spawn·namespace 분리, RViz의 TF·RobotModel·Scan 구성 | 안정적인 장시간 자동 SLAM |
| 로봇별 slam_toolbox 실행, odom → base_link TF relay, global TF relay | 최종 merged map 생성·저장 |
| 두 로봇 Nav2 lifecycle active, explore_lite → Nav2 목표 전달 | 자동 탐색 주행 완료, 병합 지도 기반 AMCL·순찰·YOLO 통합 |

당시 수동 구동도 일부 이동 후 중단되는 문제가 남았다. 원인 추적 중 DDS·bridge·TF 문제를 정리했지만, 이후 반복된 Gazebo 센서 렌더링 crash 때문에 환경을 Isaac Sim으로 전환했다. 상세 경과와 미완료 항목은 [진행 기록](docs/gazebo_multirobot_progress_2026-09-26.md)을 참고한다.

저장된 `two_robots.rviz`에는 Map 표시 항목이 없다. 당시 진행 기록의 Map 구성 주장은 저장 설정으로 확인되지 않아 현재 완료 목록에서는 제외했다.

2026-10-10 현재 hp_dt에서는 12 m 센서를 사용하는 두 AMR 자동 탐색·Nav2·RViz 맵 병합의 실제 시험 결과가 있으며, 안전·정리 경로의 독립 리뷰는 진행 중이다. 2 m 센서 자동 탐색과 병원 전체 탐색은 완료되지 않았다. 시험 run·코드 해시·STALE 상태는 [이관 기록](docs/02_isaac_transfer.md)에 구분했다.
