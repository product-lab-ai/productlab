"""Compare isolated recovery builds with the existing Product Lab engine."""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "skills/product-lab/scripts"))
from product_lab.runner import costs, run_development  # noqa: E402
from product_lab.storage import Lab  # noqa: E402


def prepare(output):
    contract = json.loads((HERE / "contract.json").read_text())
    lab = Lab.create(output / "recovery-study", contract, HERE / "evaluator")
    try:
        for name, hypothesis in [
            ("baseline", "Existing Workings may preserve enough state to return to work"),
            ("bookmark", "Restoring the step is a simpler interruption recovery mechanism"),
            ("draft", "Restoring the step and actual draft retains more unfinished work"),
        ]:
            lab.register(name, output / name, hypothesis)
            run = run_development(lab, name, name)
            print(name, run["decision"]["status"], run["summary"], flush=True)
        report = lab.report()
        report["costs"] = costs(report)
        (output / "recovery-results.json").write_text(json.dumps(report, indent=2) + "\n")
    finally:
        lab.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    prepare(parser.parse_args().artifacts.resolve())
