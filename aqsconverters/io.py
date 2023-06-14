import os
from pathlib import Path

ODA_ANNOTATION_DIR = "oda"
ENV_RENKU_HOME = "RENKU_HOME"
COMMON_DIR = "latest"


def log_oda_annotation(oda_annotation, hash, force=False):
    print(f"\033[32mlog_renku_aqs\033[0m {oda_annotation, hash}")

    if ENV_RENKU_HOME in os.environ:
        renku_project_root = os.environ[ENV_RENKU_HOME]
    elif force:
        # hope for the best...
        renku_project_root = ".renku"
    else:
        # we are not running as part of renku run
        # hence NOP
        return

    path = Path(os.path.join(renku_project_root, ODA_ANNOTATION_DIR, COMMON_DIR))
    if not path.exists():
        path.mkdir(parents=True)

    # this is the way
    jsonld_path = path / (hash + ".jsonld")
    with jsonld_path.open(mode="w") as f:
        print("writing", jsonld_path)
        f.write(oda_annotation)
