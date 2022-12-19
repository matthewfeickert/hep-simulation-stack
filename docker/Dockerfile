ARG BASE_IMAGE=atlasamglab/stats-base:root6.26.10
FROM ${BASE_IMAGE} as base

ARG TARGETARCH

SHELL [ "/bin/bash", "-c" ]

FROM base as builder

# https://herwig.hepforge.org/tutorials/installation/prerequisite.html

RUN apt-get -qq -y update && \
    apt-get -qq -y install \
        python3-dev \
        libboost-all-dev \
        wget \
        bzip2 \
        time && \
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
      --prefix=/usr/local/venv \
      --with-boost=/usr/local/venv && \
    make -j$(nproc --ignore=12) && \
    make install && \
    rm -rf /code

COPY requirements.txt /docker/requirements.txt

RUN python -m pip --no-cache-dir install --upgrade pip setuptools wheel && \
    python -m pip --no-cache-dir install -r /docker/requirements.txt

# Install FastJet
# c.f. https://github.com/scikit-hep/fastjet/tree/d87d56bec13c76ef2911705140cd6d8cd9e1fc7a#build-dependencies
# Use of fragile-shared-install is required by RIVET
ARG FASTJET_VERSION=3.4.0
ARG FASTJET_CONTRIB_VERSION=1.050
RUN mkdir /code && \
    cd /code && \
    curl --silent --location --remote-name http://fastjet.fr/repo/fastjet-${FASTJET_VERSION}.tar.gz && \
    tar xvfz fastjet-${FASTJET_VERSION}.tar.gz && \
    cd fastjet-${FASTJET_VERSION} && \
    ./configure --help && \
    export CXX=$(which g++) && \
    ./configure \
        --prefix=/usr/local/venv \
        --enable-allcxxplugins && \
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
    cd / && \
    rm -rf /code && \
    mkdir -p /code && \
    cd /code && \
    curl --silent --location --remote-name http://fastjet.hepforge.org/contrib/downloads/fjcontrib-${FASTJET_CONTRIB_VERSION}.tar.gz && \
    tar xvfz fjcontrib-${FASTJET_CONTRIB_VERSION}.tar.gz && \
    cd fjcontrib-${FASTJET_CONTRIB_VERSION} && \
    ./configure --help && \
    export CXX=$(which g++) && \
    ./configure --help && \
    ./configure \
        --fastjet-config=$(command -v fastjet-config) \
        --prefix=/usr/local/venv && \
    make \
        -j$(nproc --ignore=12) \
        fragile-shared-install && \
    make check && \
    make install && \
    cd / && \
    rm -rf /code

# Install YODA
ARG YODA_VERSION=1.9.7
RUN mkdir /code && \
    cd /code && \
    curl --silent --location --remote-name https://yoda.hepforge.org/downloads/YODA-${YODA_VERSION}.tar.gz && \
    tar xvfz YODA-${YODA_VERSION}.tar.gz && \
    cd YODA-${YODA_VERSION} && \
    autoreconf --install && \
    export CXX=$(command -v g++) && \
    export PYTHON=$(command -v python) && \
    ./configure --help && \
    ./configure \
        --prefix=/usr/local/venv && \
    make -j$(nproc --ignore=12) && \
    make check && \
    make install && \
    cd / && \
    rm -rf /code

# https://gitlab.com/hepcedar/rivet/-/blob/release-3-1-x/doc/tutorials/installation.md
# TODO: Don't use bootstrap for reproducibility
RUN mkdir /code && \
    cd /code && \
    wget https://gitlab.com/hepcedar/rivetbootstrap/raw/3.1.6/rivet-bootstrap && \
    chmod +x rivet-bootstrap && \
    export CXX=$(command -v g++) && \
    export PYTHON=$(command -v python) && \
    INSTALL_PREFIX=/usr/local/venv \
    INSTALL_BOOST=0 \
    INSTALL_HEPMC=0 \
    INSTALL_FASTJET=0 \
    INSTALL_FJCONTRIB=0 \
    INSTALL_CYTHON=0\
    INSTALL_YODA=0 \
    BOOSTPATH=/usr/local/venv \
    HEPMCPATH=/usr/local/venv \
    FASTJETPATH=/usr/local/venv \
    FJCONTRIBPATH=/usr/local/venv \
    YODAPATH=/usr/local/venv \
    MAKE="make -j $(nproc --ignore=12)"\
    ./rivet-bootstrap && \
    cd / && \
    rm -rf /code

# GSL
ARG GSL_VERSION=2.7.1
RUN mkdir /code && \
    cd /code && \
    wget https://mirror.ibcp.fr/pub/gnu/gsl/gsl-${GSL_VERSION}.tar.gz && \
    tar xvfz gsl-${GSL_VERSION}.tar.gz && \
    cd gsl-${GSL_VERSION} && \
    ./configure --help && \
    ./configure \
        --prefix=/usr/local/venv && \
    make -j$(nproc --ignore=12) && \
    make check && \
    make install && \
    cd / && \
    rm -rf /code

# ThePEG
ARG ThePEG_VERSION=2.2.3
RUN mkdir /code && \
    cd /code && \
    wget https://thepeg.hepforge.org/downloads/ThePEG-${ThePEG_VERSION}.tar.bz2 && \
    tar -xvf ThePEG-${ThePEG_VERSION}.tar.bz2 && \
    cd ThePEG-${ThePEG_VERSION} && \
    ./configure --help && \
    export CXX=$(which g++) && \
    ./configure \
        --prefix=/usr/local/venv \
        --with-gsl=/usr/local/venv \
        --with-lhapdf=/usr/local/venv \
        --with-hepmc=/usr/local/venv \
        --with-rivet=/usr/local/venv \
        --with-fastjet=/usr/local/venv \
        --with-boost=/usr/local/venv && \
    make -j$(nproc --ignore=12) && \
    make check && \
    make install && \
    cd / && \
    rm -rf /code

# https://herwig.hepforge.org/tutorials/installation/prerequisite.html#external-amplitude-providers

# GoSam
# TODO: Check if following needed
# > You need to run the following line to set environment variables before you can use GoSam:
# >  source /usr/local/venv/bin/gosam_setup_env.sh
# > Add it to your ~/profile to automate this after the re-login.
RUN mkdir /code && \
    cd /code && \
    curl --silent --location --remote-name http://gosam.hepforge.org/gosam_installer.py && \
    python gosam_installer.py \
        --prefix=/usr/local/venv/ \
        -j $(nproc --ignore=12) \
        --batch \
        --verbose && \
    cd / && \
    rm -rf /code

RUN apt-get -qq -y update && \
    apt-get -qq -y install \
        gfortran && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

# Install PYTHIA
# Install before MadGraph to get hooks
ARG PYTHIA_VERSION=8306
# PYTHON_VERSION already exists in the base image
RUN mkdir /code && \
    cd /code && \
    wget --quiet "https://pythia.org/download/pythia${PYTHIA_VERSION:0:2}/pythia${PYTHIA_VERSION}.tgz" && \
    tar xvfz pythia${PYTHIA_VERSION}.tgz && \
    cd pythia${PYTHIA_VERSION} && \
    ./configure --help && \
    export PYTHON_MINOR_VERSION=${PYTHON_VERSION%.*} && \
    ./configure \
      --prefix=/usr/local/venv \
      --arch=Linux \
      --cxx=g++ \
      --enable-64bit \
      --with-fastjet3=/usr/local/venv \
      --with-hepmc2=/usr/local/venv \
      --with-lhapdf6=/usr/local/venv \
      --with-rivet=/usr/local/venv \
      --with-root=/usr/local/venv \
      --with-gzip \
      --with-python-bin=/usr/local/venv/bin/ \
      --with-python-lib=/usr/local/venv/lib/python${PYTHON_MINOR_VERSION} \
      --with-python-include=/usr/local/include/python${PYTHON_MINOR_VERSION} \
      --cxx-common="-O2 -m64 -pedantic -W -Wall -Wshadow -fPIC -std=c++17" \
      --cxx-shared="-shared -std=c++17" && \
    make --jobs $(nproc --ignore=12) && \
    make install && \
    rm -rf /code

# Install MadGraph5_aMC@NLO for Python 3 and PYTHIA 8 interface
ARG MG_VERSION=3.4.1
# Versions viewable on Illinois mirror
# http://madgraph.physics.illinois.edu/Downloads/MG5aMC_PY8_interface/
ARG MG5aMC_PY8_INTERFACE_VERSION=1.3
RUN cd /usr/local/venv && \
    wget --quiet https://launchpad.net/mg5amcnlo/3.0/3.4.x/+download/MG5_aMC_v${MG_VERSION}.tar.gz && \
    mkdir -p /usr/local/venv/MG5_aMC && \
    tar -xzvf MG5_aMC_v${MG_VERSION}.tar.gz --strip=1 --directory=MG5_aMC && \
    rm MG5_aMC_v${MG_VERSION}.tar.gz && \
    echo "Installing MG5aMC_PY8_interface" && \
    mkdir /code && \
    cd /code && \
    wget --quiet http://madgraph.phys.ucl.ac.be/Downloads/MG5aMC_PY8_interface/MG5aMC_PY8_interface_V${MG5aMC_PY8_INTERFACE_VERSION}.tar.gz && \
    mkdir -p /code/MG5aMC_PY8_interface && \
    tar -xzvf MG5aMC_PY8_interface_V${MG5aMC_PY8_INTERFACE_VERSION}.tar.gz --directory=MG5aMC_PY8_interface && \
    cd MG5aMC_PY8_interface && \
    python compile.py /usr/local/venv/ --pythia8_makefile $(find /usr/local/ -type d -name MG5_aMC) && \
    mkdir -p /usr/local/venv/MG5_aMC/HEPTools/MG5aMC_PY8_interface && \
    cp *.h /usr/local/venv/MG5_aMC/HEPTools/MG5aMC_PY8_interface/ && \
    cp *_VERSION_ON_INSTALL /usr/local/venv/MG5_aMC/HEPTools/MG5aMC_PY8_interface/ && \
    cp MG5aMC_PY8_interface /usr/local/venv/MG5_aMC/HEPTools/MG5aMC_PY8_interface/ && \
    rm -rf /code && \
    printf '\nexport PATH=/usr/local/venv/MG5_aMC/bin:"${PATH}"\n' >> /root/.bashrc

# Change the MadGraph5_aMC@NLO configuration settings
RUN sed -i '/fastjet =/s/^# //g' /usr/local/venv/MG5_aMC/input/mg5_configuration.txt && \
    sed -i '/lhapdf_py3 =/s/^# //g' /usr/local/venv/MG5_aMC/input/mg5_configuration.txt && \
    sed -i 's|# pythia8_path.*|pythia8_path = /usr/local/venv|g' /usr/local/venv/MG5_aMC/input/mg5_configuration.txt && \
    sed -i '/mg5amc_py8_interface_path =/s/^# //g' /usr/local/venv/MG5_aMC/input/mg5_configuration.txt && \
    sed -i 's|# fortran_compiler.*|fortran_compiler = '$(command -v gfortran)'|g' /usr/local/venv/MG5_aMC/input/mg5_configuration.txt && \
    sed -i 's|# f2py_compiler_py3.*|f2py_compiler_py3 = '$(command -v f2py)'|g' /usr/local/venv/MG5_aMC/input/mg5_configuration.txt

# TODO: Install NLO dependencies independently for greater control
# Running the NLO process forces install of cuttools and iregi
RUN echo "exit" | mg5_aMC && \
    echo "install ninja" | mg5_aMC && \
    echo "install collier" | mg5_aMC && \
    echo "generate p p > e+ e- aEW=2 aS=0 [QCD]; output test_nlo" | mg5_aMC && \
    rm -rf test_nlo && \
    rm -rf $(find /usr/local/ -type d -name HEPToolsInstallers) && \
    rm py.py

RUN lhapdf install CT14nlo && \
    lhapdf install CT14lo
