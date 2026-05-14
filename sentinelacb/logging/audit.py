from __future__ import annotations
import json
from pathlib import Path
from typing import List
from ..core.models import AuditEntry

class AuditChain:
    def __init__(self, log_path: str = "logs/audit_chain.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.chain: List[AuditEntry] = []
        self._load_chain()

    def _load_chain(self):
        if self.log_path.exists():
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.chain.append(AuditEntry.model_validate(json.loads(line)))

    def append(self, action_id: str, decision: str, risk_score: float) -> AuditEntry:
        prev_hash = self.chain[-1].signature_hash if self.chain else "GENESIS"
        entry = AuditEntry.create(len(self.chain), action_id, decision, risk_score, prev_hash)
        self.chain.append(entry)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")
        return entry

    def verify(self) -> bool:
        if not self.chain: return True
        current_hash = "GENESIS"
        for entry in self.chain:
            if entry.prev_hash != current_hash:
                return False
            payload_str = f"{entry.sequence}|{entry.action_id}|{entry.decision}|{entry.risk_score}"
            expected_payload = __import__("hashlib").sha256(payload_str.encode("utf-8")).hexdigest()
            if entry.payload_hash != expected_payload:
                return False
            current_hash = entry.signature_hash
        return True