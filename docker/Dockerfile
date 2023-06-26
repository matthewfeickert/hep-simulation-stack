ARG BASE_IMAGE=atlasamglab/stats-base:root6.28.04
FROM ${BASE_IMAGE} as base

FROM base as builder

ARG TARGETARCH

USER root
WORKDIR /

SHELL [ "/bin/bash", "-c" ]

RUN echo -e "#\n# TARGETARCH: ${TARGETARCH}" && \
    mkdir -p /docker/logs

# https://herwig.hepforge.org/tutorials/installation/prerequisite.html

RUN apt-get -qq -y update && \
    apt-get -qq -y install \
        libboost-all-dev \
        wget \
        bzip2 \
        time \
        gfortran \
        rsync \
        ghostscript && \
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
    ./b2 --help && \
    if [[ "${TARGETARCH}" == "amd64" ]]; then \
        export B2_ARCH="x86"; \
    elif [[ "${TARGETARCH}" == "arm64" ]]; then \
        export B2_ARCH="arm"; \
    else \
      echo "TARGETARCH ${TARGETARCH} not supported. Exiting now."; \
      exit -1; \
    fi && \
    ./b2 \
        architecture="${B2_ARCH}" \
        --layout=tagged \
        -j$(nproc --ignore=1) \
        install && \
    unset B2_ARCH && \
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
      -Dmomentum:STRING=GEV \
      -Dlength:STRING=MM \
      -DCMAKE_INSTALL_PREFIX=/usr/local/venv \
      -S src \
      -B build && \
    cmake build -L && \
    cmake --build build --parallel $(nproc --ignore=1) && \
    cmake --build build --target install && \
    rm -rf /code

# FIXME: Causing compile issues with MG5aMC_PY8_interface
# # Install HepMC3
# ARG HEPMC3_VERSION=3.2.6
# RUN mkdir /code && \
#     cd /code && \
#     wget https://hepmc.web.cern.ch/hepmc/releases/HepMC3-${HEPMC3_VERSION}.tar.gz && \
#     tar xvfz HepMC3-${HEPMC3_VERSION}.tar.gz && \
#     mv HepMC3-${HEPMC3_VERSION} src && \
#     cmake \
#       -DCMAKE_CXX_COMPILER=$(command -v g++) \
#       -DCMAKE_BUILD_TYPE=Release \
#       -DHEPMC3_ENABLE_ROOTIO=OFF \
#       -DHEPMC3_ENABLE_PYTHON=ON \
#       -DHEPMC3_PYTHON_VERSIONS=3.X \
#       -DHEPMC3_ENABLE_TEST=ON \
#       -DCMAKE_INSTALL_PREFIX=/usr/local/venv \
#       -S src \
#       -B build && \
#     cmake build -L && \
#     cmake --build build --parallel "$(nproc --ignore=1)" && \
#     cmake --build build --target install && \
#     cd && \
#     rm -rf /code

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
    make -j$(nproc --ignore=1) && \
    make check && \
    make install && \
    rm -rf /code

COPY /docker/requirements.lock /docker/requirements.lock

# Use Brett Cannon's recommendations for pip-secure-install to ensure environment
# is reproducible and installed as securely as possible.
# c.f. https://www.python.org/dev/peps/pep-0665/#secure-by-design
# c.f. https://github.com/brettcannon/pip-secure-install
# c.f. https://twitter.com/brettsky/status/1486137764315688961
# exceptions need to be made for some libraries which only ship sdists, these
# libraries are explicitly named in --no-binary to allow for installation from
# sdist.
RUN python -m pip --no-cache-dir install \
        --upgrade \
        --no-deps \
        --require-hashes \
        --requirement /docker/requirements.lock

# Install FastJet
# c.f. https://github.com/scikit-hep/fastjet/tree/d87d56bec13c76ef2911705140cd6d8cd9e1fc7a#build-dependencies
# Use of fragile-shared-install is required by RIVET
# TODO: See if --enable-allplugins is actually needed
# Set CXXFLAGS to avoid use of -ffast-math
# c.f. https://moyix.blogspot.com/2022/09/someones-been-messing-with-my-subnormals.html
# c.f. https://gitlab.com/fastjet/siscone/-/blob/c2d0bdb645ee836874dc474985d1be50be0d548f/configure.ac#L26
ARG FASTJET_VERSION=3.4.0
ARG FASTJET_CONTRIB_VERSION=1.050
RUN mkdir /code && \
    cd /code && \
    curl --silent --location --remote-name http://fastjet.fr/repo/fastjet-${FASTJET_VERSION}.tar.gz && \
    tar xvfz fastjet-${FASTJET_VERSION}.tar.gz && \
    cd fastjet-${FASTJET_VERSION} && \
    ./configure --help && \
    export CXX=$(which g++) && \
    export CXXFLAGS=" -Wall -O3 " && \
    ./configure \
        --prefix=/usr/local/venv \
        --enable-allcxxplugins && \
    make -j$(nproc --ignore=1) && \
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
    unset CXXFLAGS && \
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
        -j$(nproc --ignore=1) \
        fragile-shared-install &> /docker/logs/fastjet.log.txt && \
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
    make -j$(nproc --ignore=1) && \
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
    MAKE="make -j $(nproc --ignore=1)"\
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
    make -j$(nproc --ignore=1) &> /docker/logs/gsl.log.txt && \
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
    make -j$(nproc --ignore=1) &> /docker/logs/thepeg.log.txt && \
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
        -j $(nproc --ignore=1) \
        --batch \
        --verbose &> /docker/logs/gosam.log.txt && \
    cd / && \
    rm -rf /code

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
    if [[ "${TARGETARCH}" == "amd64" ]]; then \
        export CXX_COMMON="-O2 -m64 -pedantic -W -Wall -Wshadow -fPIC -std=c++17"; \
    elif [[ "${TARGETARCH}" == "arm64" ]]; then \
        export CXX_COMMON="-O2 -pedantic -W -Wall -Wshadow -fPIC -std=c++17"; \
    else \
      echo "TARGETARCH ${TARGETARCH} not supported. Exiting now."; \
      exit -1; \
    fi && \
    ./configure \
      --prefix=/usr/local/venv \
      --arch=Linux \
      --cxx=g++ \
      --enable-64bit \
      --enable-shared \
      --with-fastjet3=/usr/local/venv \
      --with-hepmc2=/usr/local/venv \
      --with-lhapdf6=/usr/local/venv \
      --with-rivet=/usr/local/venv \
      --with-root=/usr/local/venv \
      --with-gzip \
      --with-python-bin=/usr/local/venv/bin/ \
      --with-python-lib=/usr/local/venv/lib/python${PYTHON_MINOR_VERSION} \
      --with-python-include=/usr/local/include/python${PYTHON_MINOR_VERSION} \
      --cxx-common="${CXX_COMMON}" \
      --cxx-shared="-shared -std=c++17" && \
    make --jobs "$(nproc --ignore=1)" &> /docker/logs/pythia8.log.txt && \
    make install && \
    unset CXX_COMMON && \
    rm -rf /code

# Install MadGraph5_aMC@NLO for Python 3 and PYTHIA 8 interface
ARG MG_VERSION=3.4.2
# Versions viewable on Illinois mirror
# http://madgraph.physics.illinois.edu/Downloads/MG5aMC_PY8_interface/
ARG MG5aMC_PY8_INTERFACE_VERSION=1.3
RUN cd /usr/local/venv && \
    wget --quiet https://launchpad.net/mg5amcnlo/3.0/3.4.x/+download/MG5_aMC_v${MG_VERSION}.tar.gz && \
    mkdir -p /usr/local/venv/MG5_aMC && \
    tar -xzvf MG5_aMC_v${MG_VERSION}.tar.gz --strip=1 --directory=MG5_aMC &> /docker/logs/mg5.log.txt && \
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
    sed -i 's|# eps_viewer.*|eps_viewer = '$(command -v ghostscript)'|g' /usr/local/venv/MG5_aMC/input/mg5_configuration.txt && \
    sed -i 's|# fortran_compiler.*|fortran_compiler = '$(command -v gfortran)'|g' /usr/local/venv/MG5_aMC/input/mg5_configuration.txt && \
    sed -i 's|# f2py_compiler_py3.*|f2py_compiler_py3 = '$(command -v f2py)'|g' /usr/local/venv/MG5_aMC/input/mg5_configuration.txt

# TODO: Install NLO dependencies independently for greater control
# Running the NLO process forces install of cuttools and iregi
RUN . /root/.bashrc && \
    echo "exit" | mg5_aMC && \
    echo "install ninja" | mg5_aMC && \
    echo "install collier" | mg5_aMC && \
    echo "generate p p > e+ e- aEW=2 aS=0 [QCD]; output test_nlo" | mg5_aMC && \
    rm -rf test_nlo && \
    rm -rf $(find /usr/local/ -type d -name HEPToolsInstallers) && \
    rm py.py

# DEBUG: Install currently broken
# # Install NJet
# # c.f. https://bitbucket.org/njet/njet/wiki/Installation for why qcdloops-1 and qd
# ARG NJET_VERSION=3.1.1
# RUN mkdir /code && \
#     cd /code && \
#     wget --quiet "https://bitbucket.org/njet/njet/downloads/njet-${NJET_VERSION}.tar.gz" && \
#     tar xvfz "njet-${NJET_VERSION}.tar.gz" && \
#     cd "njet-${NJET_VERSION}" && \
#     ./configure --help && \
#     export CXX=$(which g++) && \
#     ./configure \
#         --prefix=/usr/local/venv \
#         --disable-autoflags && \
#     cd lib-qcdloop1 && \
#     make --jobs $(nproc --ignore=1) && \
#     make check && \
#     make install && \
#     cd ../lib-qd && \
#     make --jobs $(nproc --ignore=1) && \
#     make check && \
#     make install && \
#     cd .. && \
#     ./configure \
#         --prefix=/usr/local/venv \
#         --with-qcdloop1=/usr/local/venv \
#         --with-qd=/usr/local/venv && \
#     make --jobs $(nproc --ignore=1) && \
#     make check && \
#     make install && \
#     cd / && \
#     rm -rf /code

# Install OpenLoops
# not useable for noraml work given https://gitlab.com/openloops/OpenLoops/-/issues/2
# Also can't use for aarch64 https://gitlab.com/openloops/OpenLoops/-/issues/8
ARG OPENLOOPS_VERSION=2.1.2
RUN if [[ "${TARGETARCH}" == "amd64" ]]; then \
        cd /usr/local/venv/ && \
        git clone https://gitlab.com/openloops/OpenLoops.git && \
        cd OpenLoops && \
        git checkout "OpenLoops-${OPENLOOPS_VERSION}" && \
        ./scons; \
    fi

# https://herwig.hepforge.org/tutorials/installation/prerequisite.html#decays

#TODO: PHOTOS, EvtGen

# Install TAUOLA
# ARG TAUOLA_VERSION=1.1.8
# RUN mkdir /code && \
#     cd /code && \
#     wget --quiet "http://tauolapp.web.cern.ch/tauolapp/resources/TAUOLA.${TAUOLA_VERSION}/TAUOLA.${TAUOLA_VERSION}.tar.gz" && \
#     tar -xzvf "TAUOLA.${TAUOLA_VERSION}.tar.gz" && \
#     cd TAUOLA && \
#     ./configure --help && \
#     export CXX=$(command -v g++) && \
#     ./configure \
#       --prefix=/usr/local/venv \
#       --with-hepmc=/usr/local/venv \
#       --without-hepmc3 \
#       --with-pythia8=/usr/local/venv \
#       --with-lhapdf=/usr/local/venv && \
#     make --jobs $(nproc --ignore=1) && \
#     make install && \
#     cd / && \
#     rm -rf /code

# Install HERWIG7
# Need to set am_cv_python_version manually as there is a bug in configure that can't handle Python 3.10
# FIXME: HERWIG_VERSION=7.2.3 fails to build
# CT14 required for HERWIG
ARG HERWIG_VERSION=7.2.2
RUN lhapdf install CT14nlo && \
    lhapdf install CT14lo && \
    mkdir /code && \
    cd /code && \
    wget --quiet "https://herwig.hepforge.org/downloads/Herwig-${HERWIG_VERSION}.tar.bz2" && \
    tar xjf Herwig-${HERWIG_VERSION}.tar.bz2 && \
    cd Herwig-${HERWIG_VERSION} && \
    ./configure --help && \
    export CXX=$(command -v g++) && \
    export PYTHON=$(command -v python) && \
    export am_cv_python_version=${PYTHON_VERSION%.*} && \
    if [[ "${TARGETARCH}" == "amd64" ]]; then \
        ./configure \
        --prefix=/usr/local/venv \
        --with-gsl=/usr/local/venv \
        --with-thepeg=/usr/local/venv \
        --with-boost=/usr/local/venv \
        --with-gosam=/usr/local/venv \
        --with-openloops=/usr/local/venv/OpenLoops \
        --with-madgraph=/usr/local/venv/MG5_aMC \
        --with-pythia=/usr/local/venv \
        --with-fastjet=/usr/local/venv && \
        make --jobs $(nproc --ignore=1) && \
        make check && \
        make install; \
    elif [[ "${TARGETARCH}" == "arm64" ]]; then \
        echo "Skipping TARGETARCH ${TARGETARCH} given HERWIG7 build failures."; \
    #     ./configure \
    #     --prefix=/usr/local/venv \
    #     --with-gsl=/usr/local/venv \
    #     --with-thepeg=/usr/local/venv \
    #     --with-boost=/usr/local/venv \
    #     --with-gosam=/usr/local/venv \
    #     --with-madgraph=/usr/local/venv/MG5_aMC \
    #     --with-pythia=/usr/local/venv \
    #     --with-fastjet=/usr/local/venv; \
    else \
      echo "TARGETARCH ${TARGETARCH} not supported. Exiting now."; \
      exit -1; \
    fi && \
    cd / && \
    rm -rf /code

# # TODO: Clean up and move around
# COPY jupyter_notebook_config.py /etc/jupyter/
# COPY jupyter_lab_config.py /etc/jupyter/

# # Make sure environment gets loaded regarldess of user
# # FIXME: Remove need for --allow-root
# RUN cp /root/.bashrc /etc/.bashrc && \
#     echo 'if [ -f /etc/.bashrc ]; then . /etc/.bashrc; fi' >> /etc/profile && \
#     printf '#!/bin/bash\n\njupyter lab --no-browser --ip 0.0.0.0 --port 8888 --allow-root\n' > /docker/entrypoint.sh && \
#     chmod 777 /docker/entrypoint.sh && \
#     mkdir -p \
#         /.local \
#         /.jupyter \
#         /.config \
#         /.cache \
#         /work && \
#     chmod -R 777 \
#         /.local \
#         /.jupyter \
#         /.config \
#         /.cache \
#         /work && \
#     chmod -R 777 /usr/local/venv && \
#     echo "SHELL=/bin/bash" >> /etc/environment

FROM base

USER root

SHELL [ "/bin/bash", "-c" ]
ENV PATH=/usr/local/venv/bin:"${PATH}"
ENV PYTHONPATH=/usr/local/venv/lib:${PYTHONPATH}
ENV LD_LIBRARY_PATH=/usr/local/venv/lib:${LD_LIBRARY_PATH}

# Install any packages needed by default user
RUN apt-get -qq update && \
    apt-get -qq -y install --no-install-recommends \
      gcc \
      g++ \
      gfortran \
      make \
      cmake \
      vim \
      zlib1g \
      zlib1g-dev \
      libbz2-dev \
      rsync \
      bash-completion \
      wget \
      curl \
      ghostscript \
      bc \
      git && \
    apt-get -y clean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user "moby" with uid 1000
RUN adduser \
      --shell /bin/bash \
      --gecos "default user" \
      --uid 1000 \
      --disabled-password \
      moby && \
    chown -R moby /home/moby && \
    mkdir -p /home/moby/work && \
    chown -R moby /home/moby/work && \
    mkdir /work && \
    chown -R moby /work && \
    mkdir /docker && \
    chown -R moby /docker && \
    printf '\nexport PATH=/usr/local/venv/bin:"${PATH}"\n' >> /root/.bashrc && \
    printf '\nexport PATH=/usr/local/venv/MG5_aMC/bin:"${PATH}"\n' >> /root/.bashrc && \
    cp /root/.bashrc /etc/.bashrc && \
    echo 'if [ -f /etc/.bashrc ]; then . /etc/.bashrc; fi' >> /etc/profile && \
    echo "SHELL=/bin/bash" >> /etc/environment

USER moby

ENV USER ${USER}
ENV HOME /home/moby
WORKDIR ${HOME}/work

COPY --chown=moby docker/jupyter_notebook_config.py /etc/jupyter/
COPY --chown=moby docker/jupyter_lab_config.py /etc/jupyter/
COPY --chown=moby docker/entrypoint.sh /docker/entrypoint.sh
COPY --chown=moby docker/00-wurlitzer.py /docker/00-wurlitzer.py
COPY --chown=moby docker/requirements.txt /docker/requirements.txt
COPY --chown=moby docker/requirements.lock /docker/requirements.lock
COPY --chown=moby pyproject.toml "${HOME}"

COPY --from=builder --chown=moby /usr/local/venv /usr/local/venv/
# As the virtual environment already exists from the base image any libraries
# that already exist in the base image at a different version then the builder
# (e.g. PyYAML) will have both versions in the virtual environment as the
# result of the previous COPY.
# To avoid any potential problems with this, reinstall from the lock file again
# which will upgrade the libraries and remove the older version properly.
USER root
RUN python -m pip --no-cache-dir install \
        --upgrade \
        --no-deps \
        --require-hashes \
        --requirement /docker/requirements.lock && \
    python -m pip --no-cache-dir install \
        --upgrade \
        pip \
        setuptools \
        wheel && \
    chown -R moby /usr/local/venv/
USER moby

# Avoid https://gitlab.com/Pythia8/releases/-/issues/238
RUN cp /docker/00-wurlitzer.py "$(ipython locate)/profile_default/startup/"

# Use C.UTF-8 locale to avoid issues with ASCII encoding
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENV PATH=${HOME}/.local/bin:${PATH}

# Run with login shell to trigger /etc/profile
# c.f. https://youngstone89.medium.com/unix-introduction-bash-startup-files-loading-order-562543ac12e9
ENTRYPOINT ["/bin/bash", "-l"]

CMD ["/docker/entrypoint.sh"]
