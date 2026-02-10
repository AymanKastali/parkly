FROM python:3.14-trixie

COPY --from=ghcr.io/astral-sh/uv:0.10.0 /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        curl \
        bash-completion \
        build-essential \
        sudo \
        openssh-client \
        default-jre-headless \
        graphviz \
        plantuml \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

ENV UV_LINK_MODE=copy
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
