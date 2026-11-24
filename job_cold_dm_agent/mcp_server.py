import os
import sys
import json
import datetime
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from reliability_engine import ReliabilityEngine
from google_services import GoogleWorkspaceManager

def run_production_pipeline(mode: str = "dry-run", max_jobs: int = 10) -> Dict[str, Any]:
    run_id = f"run_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    engine = ReliabilityEngine(run_id=run_id, dry_run=(mode == "dry-run"))
    
    report = {
        "run_id": run_id,
        "mode": mode,
        "jobs_processed": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "messages_sent": 0,
        "blocked": [],
        "healed_failures": 0,
        "open_issues": [],
        "cost": "$0.00",
        "sheet_link": "https://docs.google.com/spreadsheets/d/1_SkccwnnUf7ktv3w7VNRBUoJTW8HArD9gFppAOmrdHE/edit"
    }
    
    # 1. Kill switch evaluation
    if not engine.check_kill_switch():
        report["blocked"].append("AGENT_ENABLED is not TRUE in control configuration")
        engine.log_event("kill_switch", "halt", "system", {}, error="Kill switch triggered")
        return report

    print(f"[{run_id}] Reliability Pipeline initialized in {mode.upper()} mode.")
    return report

if __name__ == "__main__":
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "dry-run"
    res = run_production_pipeline(mode=mode_arg)
    print(json.dumps(res, indent=2))
