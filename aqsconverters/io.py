import os
import json
from pathlib import Path

AQS_DIR = "aq"
ENV_RENKU_HOME = "RENKU_HOME"
COMMON_DIR = "latest"


def log_renku_aqs(aqs, hash, force=False, run=None):
    print(f"\033[32mlog_renku_aqs\033[0m {aqs, hash}")

    if ENV_RENKU_HOME in os.environ:
        renku_project_root = os.environ[ENV_RENKU_HOME]
    elif force:
        # hope for the best...
        renku_project_root = ".renku"
    else:
        # we are not running as part of renku run
        # hence NOP
        return

    path = Path(os.path.join(renku_project_root, AQS_DIR, COMMON_DIR))
    if not path.exists():
        path.mkdir(parents=True)

    # this is the way
    jsonld_path = path / (hash + ".jsonld")
    with jsonld_path.open(mode="w") as f:
        print("writing", jsonld_path)
        f.write(aqs)

    # this is not the way
    if False:
        json_path = path / (hash + ".json")
        with json_path.open(mode="w") as f:
            json.dump(
                {
                    "query_type": run.aq_query_type,
                    "aq_module": run.aq_module_name,
                    "args": [str(a) for a in run.aq_args],
                    "kwargs": {k:str(v) for k,v in run.aq_kwargs.items()}
                },
                f,
                sort_keys=True,
                indent=4,
            )
