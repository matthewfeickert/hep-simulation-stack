# hep-simulation-stack
Many HEP simulation tools in one image for both x86_64 and aarch64 machines.

[![Docker Hub](https://img.shields.io/badge/DockerHub-blue?logo=Docker)](https://hub.docker.com/r/matthewfeickert/hep-simulation-stack/tags)

## Distributed Software

* ROOT 6.28.04
* BOOST
* HepMC v2.06.11
* LHAPDF v6.5.3
* FastJet v3.4.0
* YODA v1.9.7
* Rivet
* GSL v2.7.1
* ThePEG v2.2.3
* GoSam
* PYTHIA v8.306
* MadGraph5_aMC@NLO v3.4.2
* OpenLoops v2.1.2 ([x86_64 only](https://gitlab.com/openloops/OpenLoops/-/issues/8))
* HERWIG v7.2.2 (x86_64 only)
* Awkward v2
* matplotlib v3.7
* JupyterLab v4
* jupytext v1.14

## Usage

As the image is mult-manifest, both x86_64 and aarch64 versions of the image are available under the same tag

```
docker pull matthewfeickert/hep-simulation-stack:les-houches-2023
```

### Running as default 'moby' non-root user

Run the container with configuration options

```
docker run \
    --rm \
    -ti \
    --publish 8888:8888 \
    --volume $PWD:/home/moby/work \
    matthewfeickert/hep-simulation-stack:les-houches-2023
```

which will then launch Jupyter Lab with corresponding option defaults

```
jupyter lab --no-browser --ip 0.0.0.0 --port 8888
```

#### Running without the defaults

If you just want an interactive shell or need to run with different options then pass in `--` as the `CMD`:

```
docker run \
    --rm \
    -ti \
    --publish 8888:8888 \
    --volume $PWD:/home/moby/work \
    matthewfeickert/hep-simulation-stack:les-houches-2023 --
```
