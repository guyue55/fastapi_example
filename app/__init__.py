import os
import traceback
from subprocess import check_output

try:
    VERSION = __import__("pkg_resources").get_distribution("inference").version
except Exception:
    VERSION = "unknown"

# fix is in the works see: https://github.com/mpdavis/python-jose/pull/207
import warnings

warnings.filterwarnings("ignore", message="int_from_bytes is deprecated")

# sometimes we pull version info before inference is totally installed
try:
    from inference.project.models import Project  # noqa lgtm[py/unused-import]


except Exception:
    traceback.print_exc()


def _get_git_revision(path):
    if not os.path.exists(os.path.join(path, ".git")):
        return None
    try:
        revision = check_output(["git", "rev-parse", "HEAD"], cwd=path, env=os.environ)
    except Exception:
        # binary didn't exist, wasn't on path, etc
        return None
    return revision.decode("utf-8").strip()


def get_revision():
    """
    :returns: Revision number of this branch/checkout, if available. None if
        no revision number can be determined.
    """
    if "INFERENCE_BUILD" in os.environ:
        return os.environ["INFERENCE_BUILD"]
    package_dir = os.path.dirname(__file__)
    checkout_dir = os.path.normpath(os.path.join(package_dir, os.pardir, os.pardir))
    path = os.path.join(checkout_dir)
    if os.path.exists(path):
        return _get_git_revision(path)
    return None


def get_version():
    if __build__:
        return f"{__version__}.{__build__}"
    return __version__


__version__ = VERSION
__build__ = get_revision()
