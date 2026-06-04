FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV ANDROID_NDK_HOME=/opt/android-sdk/ndk/25.2.9519653
ENV PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/build-tools/33.0.2:${ANDROID_HOME}/tools/bin:/usr/local/bin:${PATH}"

# ── System packages ──────────────────────────────────────
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python3-pip \
    git zip unzip \
    openjdk-17-jdk \
    wget curl \
    autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev \
    libffi-dev libssl-dev \
    cmake build-essential ant \
    libltdl-dev \
    && rm -rf /var/lib/apt/lists/*

# Force python3 → python3.10
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 \
 && update-alternatives --set python3 /usr/bin/python3.10

# ── Android SDK cmdline-tools ─────────────────────────────
RUN mkdir -p /opt/android-sdk/cmdline-tools \
 && wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip \
         -O /tmp/cmdtools.zip \
 && unzip -q /tmp/cmdtools.zip -d /opt/android-sdk/cmdline-tools \
 && mv /opt/android-sdk/cmdline-tools/cmdline-tools \
       /opt/android-sdk/cmdline-tools/latest \
 && rm /tmp/cmdtools.zip

# ── Accept licenses & install SDK components ─────────────
RUN yes | sdkmanager --licenses 2>/dev/null || true
RUN sdkmanager \
    "platform-tools" \
    "platforms;android-33" \
    "build-tools;33.0.2" \
    "ndk;25.2.9519653"

# Compat symlinks for tools/bin (buildozer needs them)
RUN mkdir -p /opt/android-sdk/tools/bin \
 && ln -sf /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager \
           /opt/android-sdk/tools/bin/sdkmanager \
 && ln -sf /opt/android-sdk/cmdline-tools/latest/bin/avdmanager \
           /opt/android-sdk/tools/bin/avdmanager

# ── Python build tools ────────────────────────────────────
RUN pip3 install --upgrade pip \
 && pip3 install "cython>=3.0.0,<4" buildozer==1.5.0

# ── Non-root user ─────────────────────────────────────────
RUN useradd -m -u 1000 builder \
 && chown -R builder:builder /opt/android-sdk

USER builder
WORKDIR /app
