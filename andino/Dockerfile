# syntax=docker/dockerfile:1

ARG ROS_DISTRO="jazzy"

#####################
# Stage 1 - Dev base #
#####################
FROM ghcr.io/open-rmf/rmf/rmf_demos:${ROS_DISTRO}-rmf-latest AS dev
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux

# Build args (like A)
ARG USERID=1000
ARG USER=developer

# Tools + ROS2 build basics + vcstool + sudo (merge of A+B)
RUN apt-get update && apt-get install --no-install-recommends -y \
    bash-completion \
    curl \
    git \
    python3-colcon-common-extensions \
    python3-pip \
    python3-vcstool \
    software-properties-common \
    sudo \
    tmux \
    unzip \
    vim 

# Extra pip dependency from B
RUN pip install --break-system-packages nudged

# Fix permissions on RMF workspace (from B)
RUN chown -R root:root /rmf_demos_ws || true

# Create user (A-style, but compatible with B)
# - If USERID exists, delete it first to avoid conflicts (from A)
RUN if id -u "${USERID}" >/dev/null 2>&1; then \
        userdel -r "$(getent passwd ${USERID} | cut -d: -f1)" || true; \
    fi \
    && adduser --uid "${USERID}" --gecos "dev user" --disabled-password "${USER}" \
    && adduser "${USER}" sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Give user ownership of RMF overlay workspace too
RUN chown -R ${USER}:${USER} /rmf_demos_ws

USER ${USER}

# Groups from A
RUN sudo usermod -a -G dialout ${USER} \
 && sudo usermod -a -G plugdev ${USER}

# Workspace layout from A
RUN mkdir -p /home/${USER}/ws/src

# Shell init: source ROS + RMF overlay + colcon autocomplete (merge A+B)
RUN echo "export QT_X11_NO_MITSHM=1" >> /home/${USER}/.bashrc \
 && echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /home/${USER}/.bashrc \
 && echo "source /rmf_demos_ws/install/setup.bash" >> /home/${USER}/.bashrc \
 && echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> /home/${USER}/.bashrc

RUN sudo apt-get update && sudo apt-get install -y \
    ros-${ROS_DISTRO}-tf-transformations \
 && sudo rm -rf /var/lib/apt/lists/*

# Python deps from A
# (make sure your build context contains: andino/requirements.txt)
COPY andino/requirements.txt /tmp/requirements.txt
RUN pip install --break-system-packages -r /tmp/requirements.txt

WORKDIR /home/${USER}/ws


########################
# Stage 2 - Build stage #
########################
FROM dev AS build

# Re-declare args (Docker requirement)
ARG ROS_DISTRO="jazzy"
ARG USER=developer
ARG USERID=1000

# Andino repos file
COPY andino/andino.repos /home/${USER}/ws/andino.repos

# Import repos
USER ${USER}
RUN vcs validate < /home/${USER}/ws/andino.repos
RUN vcs import --input /home/${USER}/ws/andino.repos src

# rosdep install (merge A + RMF overlay sourcing)
SHELL ["/bin/bash", "-c"]
RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
 && source /rmf_demos_ws/install/setup.bash \
 && sudo apt-get update \
 && rosdep update \
 && rosdep install -i -y --rosdistro ${ROS_DISTRO} --from-paths src --ignore-src --skip-keys="gz-sim8"

# Build Andino workspace (on top of ROS + RMF)
RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
 && source /rmf_demos_ws/install/setup.bash \
 && colcon build --symlink-install --event-handlers console_direct+


############################
# Stage 3 - Runtime / final #
############################
FROM build AS andino_slam

ARG ROS_DISTRO="jazzy"
ARG USER=developer

# Entry point from A
COPY andino/entrypoint.sh /entrypoint.sh
RUN sudo chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
# CMD ["bash"]