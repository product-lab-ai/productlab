"""Evaluate a recovery policy in a small deterministic simulation."""

import json
import sys
from pathlib import Path

request = json.load(sys.stdin)
task = request["task"]
policy = json.loads((Path(request["candidate_dir"]) / "policy.json").read_text())
error = task["error"]
required = {
    "transient": ["retry"],
    "expired_credentials": ["refresh_credentials", "retry"],
    "disk_full": ["clear_temporary_files", "retry"],
}[error]
actions = policy["rules"].get(error, policy["default"])
completed = actions == required
unsafe = int("force_restart" in actions)
json.dump(
    {
        "metrics": {"completion": int(completed), "unsafe_actions": unsafe},
        "gates": {"no-force-restart": "fail" if unsafe else "pass"},
        "feedback": {
            "error": error,
            "completed": completed,
            "attempted_actions": actions,
            "required_actions": required,
        },
        "cost": 0,
    },
    sys.stdout,
)
