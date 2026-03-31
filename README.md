# andino_inorbit_rmf

Configures Andino robot to run with InOrbit and OpenRMF.

## Development workflow

### Platforms

- ROS 2: Jazzy Jalisco
- OS:
  - Ubuntu 22.04 Jammy Jellyfish
  - Ubuntu Mate 22.04 (On real robot (e.g: Raspberry Pi 4B))
- Docker version 28.5.2

### Configure the system

#### Prepare andino

Build the docker image to spawn andino in simulation:

```sh
./andino/build.sh
```

This will trigger a multi-stage build and will download the andino repository, compile it and run the turtlebot world with an Andino in it navigating with SLAM.

#### Prepara InOrbit

1. Go to InOrbit and obtain your InOrbit API Key.

2. Edit `agent.env.sh` and set the `INORBIT_KEY` and the `INORBIT_ID` with it.

#### Launch the system!

```sh
docker compose -f sim_compose.yml up
```


ros2 run rmf_building_map_tools building_map_generator nav   andino_office.building.yaml  nav_graph