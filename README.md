# hep-simulation-stack
Many HEP simulation tools in one image

## Usage

### Running as non-root user

Run the container with configuration options

```
docker run \
    --rm \
    -ti \
    --publish 8888:8888 \
    --user $(id -u $USER):$(id -g) \
    --volume $PWD:/work \
    matthewfeickert/hep-simulation-stack:latest
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
    --user $(id -u $USER):$(id -g) \
    --volume $PWD:/work \
    matthewfeickert/hep-simulation-stack:latest:latest --
```
