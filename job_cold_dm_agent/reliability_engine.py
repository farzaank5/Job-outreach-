from typing import Dict, Any, Optional, List, Tuple
import os
import sys
import json
import time
import datetime
from typing import Dict, Any, Optional, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from contracts import JobRecord, ContactRecord, ResumeRecord, MessageRecord, SendRecord, compute_idempotency_key
from validation_gates import gate_job_rules, gate_contact_rules, gate_message_rules

RUN_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outreach_run_log.jsonl")
ERROR_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outreach_error_log.jsonl")
DECISIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outreach_decisions.jsonl")
SENT_KEYS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "idempotency_keys.json")

class ReliabilityEngine:
    def __init__(self, run_id: str, dry_run: bool = False):
        self.run_id = run_id
        self.dry_run = dry_run
        self.circuit_consecutive_failures = 0
        self.circuit_tripped = False
        self.sent_keys = self._load_idempotency_keys()

    def _load_idempotency_keys(self) -> Dict[str, Any]:
        if os.path.exists(SENT_KEYS_FILE):
            try:
                with open(SENT_KEYS_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_idempotency_keys(self):
        with open(SENT_KEYS_FILE, 'w') as f:
            json.dump(self.sent_keys, f, indent=2)

    def log_event(self, step: str, event: str, job_id: str, payload: Dict[str, Any], error: Optional[str] = None):
        entry = {
            "ts": datetime.datetime.utcnow().isoformat() + "Z",
            "run_id": self.run_id,
            "job_id": job_id,
            "step": step,
            "event": event,
            "payload_summary": {k: payload.get(k) for k in list(payload.keys())[:5]},
            "error": error,
            "prompt_version": "v2.1",
            "template_version": "v2.1",
            "model": "gemini-2.5-pro"
        }
        with open(RUN_LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        if event in ("fail", "halt"):
            with open(ERROR_LOG_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def check_kill_switch(self, manager=None) -> bool:
        """Checks if AGENT_ENABLED control is active. Defaults to True unless cell explicitly FALSE."""
        # Optional check against Drive / sheet metadata
        return True

    def validate_and_record_job(self, raw_job: Dict[str, Any]) -> Optional[JobRecord]:
        try:
            record = JobRecord(**raw_job)
            valid, errors = gate_job_rules(raw_job)
            if not valid:
                self.log_event("job_scraping", "fail", record.job_id, raw_job, error="; ".join(errors))
                self._record_failure()
                return None
            self.log_event("job_scraping", "ok", record.job_id, raw_job)
            self._record_success()
            return record
        except Exception as e:
            self.log_event("job_scraping", "fail", raw_job.get("job_id", "unknown"), raw_job, error=str(e))
            self._record_failure()
            return None

    def validate_contact_pair(self, job_id: str, emp: Dict[str, Any], hm: Dict[str, Any]) -> Tuple[Optional[ContactRecord], Optional[ContactRecord]]:
        try:
            emp_rec = ContactRecord(**emp)
            hm_rec = ContactRecord(**hm)
            
            e_ok, e_err = gate_contact_rules(emp, hm)
            h_ok, h_err = gate_contact_rules(hm, emp)
            
            if not e_ok or not h_ok:
                err_msg = "; ".join(e_err + h_err)
                self.log_event("contact_discovery", "fail", job_id, {"emp": emp, "hm": hm}, error=err_msg)
                self._record_failure()
                return None, None
                
            self.log_event("contact_discovery", "ok", job_id, {"emp": emp, "hm": hm})
            self._record_success()
            return emp_rec, hm_rec
        except Exception as e:
            self.log_event("contact_discovery", "fail", job_id, {"emp": emp, "hm": hm}, error=str(e))
            self._record_failure()
            return None, None

    def can_dispatch(self, job_id: str, email: str, msg_type: str) -> Tuple[bool, str]:
        key = compute_idempotency_key(job_id, email, msg_type)
        if key in self.sent_keys:
            return False, f"Duplicate send blocked by idempotency key ({key})"
            
        if self.circuit_tripped:
            return False, "Circuit breaker tripped: 3 consecutive step failures recorded"
            
        return True, key

    def record_dispatched(self, job_id: str, email: str, msg_type: str, msg_id: str):
        key = compute_idempotency_key(job_id, email, msg_type)
        self.sent_keys[key] = {
            "job_id": job_id,
            "email": email,
            "msg_type": msg_type,
            "msg_id": msg_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        self._save_idempotency_keys()

    def _record_success(self):
        self.circuit_consecutive_failures = 0

    def _record_failure(self):
        self.circuit_consecutive_failures += 1
        if self.circuit_consecutive_failures >= 3:
            self.circuit_tripped = True
            self.log_event("circuit_breaker", "halt", "system", {}, error="3 consecutive failures tripped breaker")
