import shutil
from datetime import datetime
from pathlib import Path

import nox

# Default sessions to run if no session handles are passed
nox.options.sessions = ["lock"]


DIR = Path(__file__).parent.resolve()

@nox.session()
def build(session):
    """
    Build image
    """
    session.run("docker", "pull", "atlasamglab/stats-base:root6.26.10", external=True)
    session.run(
        "docker",
        "build",
        "--file",
        "docker/Dockerfile",
        "--build-arg",
        "BASE_IMAGE=atlasamglab/stats-base:root6.26.10",
        "--tag",
        "matthewfeickert/hep-simulation-stack:latest",
        "docker",
        external=True,
    )


@nox.session()
def tag(session):
    """
    Tag images
    """
    for tag in session.posargs:
        session.run(
            "docker",
            "tag",
            "hub.opensciencegrid.org/iris-hep/analysis-systems-base:latest",
            f"hub.opensciencegrid.org/iris-hep/analysis-systems-base:{tag}",
            external=True,
        )


@nox.session()
def publish(session):
    """
    Push images to container registries
    """
    for tag in ["latest", datetime.now().strftime("%Y-%m-%d")]:
        session.run(
            "docker",
            "push",
            f"hub.opensciencegrid.org/iris-hep/analysis-systems-base:{tag}",
            external=True,
        )


@nox.session()
def deploy(session):
    """
    Build, tag, and push to registry
    """
    session.notify("build")
    session.notify("publish")
