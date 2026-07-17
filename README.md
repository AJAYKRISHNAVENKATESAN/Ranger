# Ranger — Autonomous Mobile Robot (ROS2)

A differential drive AMR with two side wheels and a front castor, designed for indoor SLAM navigation and autonomous exploration, simulated in Ignition Gazebo.

## Demo

> Gazebo simulation with LiDAR-based SLAM mapping — demo GIF coming soon

## Stack

| Component | Technology |
|-----------|-----------|
| ROS2 distro | Humble |
| Simulator | Ignition Gazebo (Fortress) |
| SLAM | slam_toolbox (online async) |
| Localisation | robot_localization (EKF) |
| Navigation | Nav2 (in progress) |
| Control | ros2_control + diff_drive_controller |
| Sensor | 2D LiDAR + IMU |

## Package structure

```
ranger/
├── description/        # URDF/xacro — robot model, sensors, gazebo plugins
├── launch/
│   ├── gz_sim.launch.py    # Full simulation launch
│   ├── display.launch.py   # RViz visualisation only
│   └── test.launch.py      # Hardware test launch
├── config/
│   ├── controller.yaml     # ros2_control diff drive config
│   ├── ekf.yaml            # robot_localization EKF config
│   ├── gz_bridge.yaml      # Gazebo ↔ ROS2 topic bridge
│   └── mapper_params_online_async.yaml  # slam_toolbox config
├── meshes/             # STL files for robot body and wheels
├── worlds/             # Gazebo SDF world files
└── rviz/               # RViz config files
```

## Quick start

```bash
# 1. Clone into your ROS2 workspace
cd ~/ros2_ws/src
git clone git@github.com:AJAYKRISHNAVENKATESAN/Ranger.git ranger

# 2. Install dependencies
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y

# 3. Build
colcon build --symlink-install --packages-select ranger
source install/setup.bash

# 4. Launch in Gazebo
ros2 launch ranger gz_sim.launch.py

# 5. Visualise in RViz (separate terminal)
ros2 launch ranger display.launch.py
```
<img width="727" height="551" alt="Image" src="https://github.com/user-attachments/assets/01a86b9c-adf9-44dc-8951-655dbe317810" />

## Docker development environment

A standalone dev container is provided under `docker/` — ROS 2 Humble + Gazebo
Fortress (Ignition), plus `ros2_control`, `robot_localization`, and `slam_toolbox`.

```bash
cd docker
xhost +local:root          # allow the container to use your display
docker compose up -d --build
docker exec -it ranger-dev bash

# inside the container
cb   # colcon build --symlink-install
cs   # source install/setup.bash
ros2 launch ranger gz_sim.launch.py
```

Requires an NVIDIA GPU + `nvidia-container-toolkit` on the host for hardware-accelerated
RViz/Gazebo rendering. Build artifacts persist across restarts in the
`ranger_build`/`ranger_install`/`ranger_log` named volumes.

## Part of Project Drishti

Ranger is a component of [project-drishti](https://github.com/PavanSandaka/project-drishti), a multi-robot ROS2 monorepo. It is included there as a git submodule under `bots/ranger/`.
