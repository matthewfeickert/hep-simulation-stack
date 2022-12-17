ARG BASE_IMAGE=atlasamglab/stats-base:root6.26.10
FROM ${BASE_IMAGE} as base

ARG TARGETARCH

SHELL [ "/bin/bash", "-c" ]

FROM base as builder

# https://herwig.hepforge.org/tutorials/installation/prerequisite.html

RUN apt-get -qq -y update && \
    apt-get -qq -y install \
        python3-dev \
        libboost-all-dev && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

# Install BOOST
# c.f. https://www.boost.org/doc/libs/1_81_0/more/getting_started/unix-variants.html
ARG BOOST_VERSION=1.81.0
RUN export CPLUS_INCLUDE_PATH="${CPLUS_INCLUDE_PATH}:/usr/local/include/python3.10/" && \
    mkdir -p /code && \
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

# Install HepMC
ARG HEPMC_VERSION=2.06.11
RUN mkdir /code && \
    cd /code && \
    curl --silent --location --remote-name http://hepmc.web.cern.ch/hepmc/releases/hepmc${HEPMC_VERSION}.tgz && \
    tar xvfz hepmc${HEPMC_VERSION}.tgz && \
    mv HepMC-${HEPMC_VERSION} src && \
    cmake \
      -DCMAKE_CXX_COMPILER=$(which g++) \
      -DCMAKE_BUILD_TYPE=Release \
      -Dbuild_docs:BOOL=OFF \
      -Dmomentum:STRING=MEV \
      -Dlength:STRING=MM \
      -DCMAKE_INSTALL_PREFIX=/usr/local/venv \
      -S src \
      -B build && \
    cmake build -L && \
    cmake --build build --parallel $(nproc --ignore=12) && \
    cmake --build build --target install && \
    rm -rf /code

# Install LHAPDF
ARG LHAPDF_VERSION=6.5.3
RUN mkdir /code && \
    cd /code && \
    curl --silent --location https://lhapdf.hepforge.org/downloads/?f=LHAPDF-${LHAPDF_VERSION}.tar.gz --output LHAPDF-${LHAPDF_VERSION}.tar.gz && \
    tar xvfz LHAPDF-${LHAPDF_VERSION}.tar.gz && \
    cd LHAPDF-${LHAPDF_VERSION} && \
    ./configure --help && \
    export CXX=$(which g++) && \
    export PYTHON=$(which python) && \
    ./configure \
      --prefix=/usr/local/venv && \
    make -j$(nproc --ignore=12) && \
    make install && \
    rm -rf /code

# Install FastJet
# c.f. https://github.com/scikit-hep/fastjet/tree/d87d56bec13c76ef2911705140cd6d8cd9e1fc7a#build-dependencies
ARG FASTJET_VERSION=3.4.0
RUN mkdir /code && \
    cd /code && \
    curl --silent --location --remote-name http://fastjet.fr/repo/fastjet-${FASTJET_VERSION}.tar.gz && \
    tar xvfz fastjet-${FASTJET_VERSION}.tar.gz && \
    cd fastjet-${FASTJET_VERSION} && \
    ./configure --help && \
    export CXX=$(which g++) && \
    ./configure \
      --prefix=/usr/local/venv && \
    make -j$(nproc --ignore=12) && \
    make check && \
    make install && \
    if [[ "${TARGETARCH}" == "arm64" ]]; then \
        apt-get -qq -y update && \
        apt-get -qq -y install \
          libboost-dev \
          libmpfr-dev \
          libgmp-dev \
          swig \
          autoconf \
          libtool && \
        apt-get -y autoclean && \
        apt-get -y autoremove && \
        rm -rf /var/lib/apt/lists/* ; \
    fi && \
    python -m pip --no-cache-dir install "fastjet~=${FASTJET_VERSION}.0" && \
    rm -rf /code
