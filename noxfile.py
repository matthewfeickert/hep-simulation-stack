import shutil
from pathlib import Path

import nox

# Default sessions to run if no session handles are passed
nox.options.sessions = ["lock"]


DIR = Path(__file__).parent.resolve()


@nox.session(python=False)
def lock(session):
    """
    Build a lockfile for the image with pip-tools
    """
    base_image = "atlasamglab/stats-base:root6.28.04"
    session.run("docker", "pull", base_image, external=True)
    session.run(
        "docker",
        "run",
        "--rm",
        "-v",
        f"{DIR}:/build",
        "-w",
        "/build",
        base_image,
        "bash docker/compile_lock.sh",
        external=True,
    )

    # Make lockfile local user owned
    root_controlled_file = DIR / "requirements.lock.tmp"
    shutil.move(DIR / "docker" / "requirements.lock", root_controlled_file)
    shutil.copy(root_controlled_file, DIR / "docker" / "requirements.lock")

    if root_controlled_file.exists():
        root_controlled_file.unlink()
