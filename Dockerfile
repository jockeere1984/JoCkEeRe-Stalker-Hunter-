
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk

RUN apt-get update && apt-get install -y \
    python3 python3-pip git zip unzip \
    openjdk-17-jdk wget curl \
    autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev \
    libffi-dev libssl-dev \
    cmake build-essential ant && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/android-sdk/tools/bin && \
    ln -sf /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager /opt/android-sdk/tools/bin/sdkmanager && \
    ln -sf /opt/android-sdk/cmdline-tools/latest/bin/avdmanager /opt/android-sdk/tools/bin/avdmanager

RUN useradd -m -u 1000 builder && \
    chown -R builder:builder /opt/android-sdk

USER builder
WORKDIR /app
