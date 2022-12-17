ARG BASE_IMAGE=atlasamglab/stats-base:root6.26.10
FROM ${BASE_IMAGE} as base

ARG TARGETARCH

SHELL [ "/bin/bash", "-c" ]

FROM base as builder

# https://herwig.hepforge.org/tutorials/installation/prerequisite.html

# Install BOOST
# c.f. https://www.boost.org/doc/libs/1_76_0/more/getting_started/unix-variants.html
# c.f. https://www.boost.org/doc/libs/1_81_0/more/getting_started/unix-variants.html
ARG BOOST_VERSION=1.81.0
RUN mkdir -p /code && \
    cd /code && \
    BOOST_VERSION_UNDERSCORE="${BOOST_VERSION//\./_}" && \
    curl --silent --location --remote-name "https://boostorg.jfrog.io/artifactory/main/release/${BOOST_VERSION}/source/boost_${BOOST_VERSION_UNDERSCORE}.tar.gz" && \
    tar -xzf "boost_${BOOST_VERSION_UNDERSCORE}.tar.gz" && \
    cd "boost_${BOOST_VERSION_UNDERSCORE}" && \
    ./bootstrap.sh --help && \
    ./bootstrap.sh \
      --prefix=/usr/local/venv \
      --with-python=$(command -v python3) && \
    ./b2 install \
        --layout=tagged \
        -j$(nproc --ignore=1) && \
    cd / && \
    rm -rf /code
