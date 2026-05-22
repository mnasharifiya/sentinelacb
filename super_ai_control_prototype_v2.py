# advanced_ai_control_prototype_v2.py

import time
import hashlib
import json
from datetime import datetime
import os # For simulating kill switch file
import random # For simulating AI decision-making

# --- SentinelACB: The Layered Control Framework ---
class SentinelACB:
    """
    Implements a layered cybersecurity control model for Advance AI actions.
    Combines permission boundaries, HITL, monitoring, and audit logging.
    """
    def __init__(self):
        # Layer 1: Permission & Access Control
        # P: Explicitly permitted actions with their default risk level
        self.permitted_actions = {
            "read_sensor": "low_risk",
            "log_status": "low_risk",
            "minor_trade": "medium_risk",
            "adjust_traffic_flow": "medium_risk",
            "send_delivery_drone": "medium_risk",
            "post_social_media_update": "medium_risk"
        }
        # H: High-risk actions requiring HITL
        self.high_risk_actions = {
            "execute_large_trade": "critical_risk",
            "shutdown_power_grid": "critical_risk",
            "override_airspace_regulations": "critical_risk",
            "deploy_disinformation_campaign": "critical_risk"
        }
        self.all_known_actions = {**self.permitted_actions, **self.high_risk_actions}

        # Layer 3: Monitoring & Anomaly Detection (Token Bucket for Rate Limiting)
        self.max_tokens = 10 # Max actions per refill period
        self.current_tokens = self.max_tokens
        self.last_refill_time = time.time()
        self.refill_rate_per_sec = 1 # 1 token refilled per second

        # Layer 5: Auditing & Transparency (Simulated Immutable Audit Log)
        self.audit_ledger = []
        self.audit_log_file = "audit_log.jsonl" # JSON Lines file for persistent logging
        self._load_audit_log()

        # Layer 4: Rollback and Safe-State Mechanisms (Simulated Kill Switch & Safe State)
        self.kill_switch_file = "kill_switch_status.txt"
        self.safe_state_file = "safe_state_active.txt" # New: for safe-state mode
        self._ensure_control_files_exist()
        self.is_safe_state_active = False # Internal state for quick checks

    def _load_audit_log(self):
        """Loads existing audit log entries from file."""
        if os.path.exists(self.audit_log_file):
            with open(self.audit_log_file, 'r') as f:
                for line in f:
                    try:
                        self.audit_ledger.append(json.loads(line))
                    except json.JSONDecodeError:
                        print(f"Warning: Corrupted line in audit log: {line.strip()}")
        print(f"Loaded {len(self.audit_ledger)} audit entries.")

    def _append_to_audit_log_file(self, entry):
        """Appends a new audit entry to the persistent file."""
        with open(self.audit_log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def _refill_tokens(self):
        """Refills tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill_time
        tokens_to_add = int(elapsed * self.refill_rate_per_sec)
        self.current_tokens = min(self.max_tokens, self.current_tokens + tokens_to_add)
        self.last_refill_time = now

    def _log_action(self, action_name, status, actor="AI_Agent", details=None, latency_ms=None):
        """Logs an action to the tamper-evident audit ledger."""
        prev_hash = self.audit_ledger[-1]['hash'] if self.audit_ledger else "0"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "actor": actor,
            "action": action_name,
            "status": status,
            "details": details if details else {},
            "latency_ms": latency_ms, # New: for empirical validation
            "prev_hash": prev_hash
        }
        entry_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode('utf-8')).hexdigest()
        entry['hash'] = entry_hash
        self.audit_ledger.append(entry)
        self._append_to_audit_log_file(entry)
        latency_str = f"{latency_ms:.2f}ms" if latency_ms is not None else "N/A"
        print(f"[AUDIT] {entry['timestamp']} | Actor: {actor} | Action: {action_name} | Status: {status} | Hash: {entry_hash[:8]}... | Latency: {latency_str}")

    def _read_control_file(self, filename):
        """Reads the status from a control file."""
        if not os.path.exists(filename):
            return "unknown" # Should be handled by _ensure_control_files_exist
        with open(filename, 'r') as f:
            return f.read().strip().lower()

    def _write_control_file(self, filename, status):
        """Writes a status to a control file."""
        with open(filename, 'w') as f:
            f.write(status)

    def _ensure_control_files_exist(self):
        """Ensures kill switch and safe state files exist and are in 'run' state."""
        if not os.path.exists(self.kill_switch_file):
            self._write_control_file(self.kill_switch_file, "run")
            print(f"Created control file: {self.kill_switch_file} with status 'run'.")
        if not os.path.exists(self.safe_state_file):
            self._write_control_file(self.safe_state_file, "inactive")
            print(f"Created control file: {self.safe_state_file} with status 'inactive'.")

    def activate_safe_state(self):
        """Activates the safe state mode."""
        self._write_control_file(self.safe_state_file, "active")
        self.is_safe_state_active = True
        print(f"\n!!! SYSTEM ENTERING SAFE STATE !!! All write/network privileges revoked.")
        self._log_action("SYSTEM_CONTROL", "SAFE_STATE_ACTIVATED", actor="System_Operator")

    def deactivate_safe_state(self):
        """Deactivates the safe state mode."""
        self._write_control_file(self.safe_state_file, "inactive")
        self.is_safe_state_active = False
        print(f"\n--- SYSTEM EXITING SAFE STATE --- Privileges restored.")
        self._log_action("SYSTEM_CONTROL", "SAFE_STATE_DEACTIVATED", actor="System_Operator")

    def request_action(self, action_name, metadata=None):
        """
        Processes an AI agent's request through the layered control framework.
        Returns a tuple: (success_boolean, message)
        """
        start_time = time.perf_counter() # New: for latency measurement
        if metadata is None:
            metadata = {}

        print(f"\n--- AI Request: '{action_name}' (Details: {metadata}) ---")

        # Layer 4 Check: Kill Switch (Highest Priority)
        if self._read_control_file(self.kill_switch_file) == "halt":
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._log_action(action_name, "DENIED_KILL_SWITCH_ACTIVE", details={"reason": "System halted by external kill switch."}, latency_ms=latency_ms)
            return False, "System is halted by external kill switch. Cannot perform actions."

        # Layer 4 Check: Safe State (Second Highest Priority)
        self.is_safe_state_active = (self._read_control_file(self.safe_state_file) == "active")
        if self.is_safe_state_active:
            # In safe state, only read_sensor and log_status are allowed
            if action_name not in ["read_sensor", "log_status"]:
                latency_ms = (time.perf_counter() - start_time) * 1000
                self._log_action(action_name, "DENIED_SAFE_STATE_ACTIVE", details={"reason": "Only read/log actions permitted in safe state."}, latency_ms=latency_ms)
                return False, "System is in safe state. Only passive monitoring actions are allowed."
            print(f"[CONTROL] Safe State Active: Allowing '{action_name}' (read/log action).")


        self._refill_tokens() # Refill tokens before any checks

        # Layer 1: Permission & Access Control
        if action_name not in self.all_known_actions:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._log_action(action_name, "DENIED_OUT_OF_SCOPE", details={"reason": "Action not defined in permitted or high-risk lists."}, latency_ms=latency_ms)
            return False, f"Error: Action '{action_name}' is not in the allowed scope."

        # Layer 3: Monitoring & Anomaly Detection (Rate Limiting)
        if self.current_tokens < 1:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._log_action(action_name, "DENIED_RATE_LIMIT", details={"reason": "Circuit breaker tripped due to excessive requests."}, latency_ms=latency_ms)
            return False, "Error: Circuit Breaker Tripped (Action Spamming Detected). Too many requests."
        
        self.current_tokens -= 1
        print(f"[CONTROL] Tokens remaining: {self.current_tokens}/{self.max_tokens}")

        # Layer 2: Human-in-the-Loop Decision Gate
        if action_name in self.high_risk_actions:
            print(f"!!! HIGH-RISK ACTION DETECTED: '{action_name}' !!!")
            print(f"Details: {metadata}")
            
            # Simulate human approval time
            human_approval_start = time.perf_counter()
            user_input = input("Admin, explicit human authorization required. Do you approve? (yes/no): ").strip().lower()
            human_approval_latency_ms = (time.perf_counter() - human_approval_start) * 1000

            if user_input == 'yes':
                latency_ms = (time.perf_counter() - start_time) * 1000
                self._log_action(action_name, "APPROVED_BY_HUMAN", actor="Human_Admin", details={"approval_decision": "yes", "human_latency_ms": human_approval_latency_ms}, latency_ms=latency_ms)
                print(f"[CONTROL] Human Admin APPROVED '{action_name}'. Proceeding...")
            else:
                latency_ms = (time.perf_counter() - start_time) * 1000
                self._log_action(action_name, "DENIED_BY_HUMAN", actor="Human_Admin", details={"approval_decision": "no", "human_latency_ms": human_approval_latency_ms}, latency_ms=latency_ms)
                return False, f"Action '{action_name}' denied by Human-in-the-Loop."

        # If all checks pass, simulate execution
        latency_ms = (time.perf_counter() - start_time) * 1000
        self._log_action(action_name, "EXECUTED", details={"result": "Action performed successfully."}, latency_ms=latency_ms)
        return True, f"Success: Action '{action_name}' performed."

# --- AIAgent: Simulates the AI's behavior ---
class AIAgent:
    """
    Simulates an autonomous AI agent attempting to perform actions.
    It interacts with the SentinelACB for all its operations.
    """
    def __init__(self, name="SuperAI_Alpha"):
        self.name = name
        self.sentinel = SentinelACB()
        print(f"\n--- {self.name} Initialized ---")
        print(f"Kill switch status: '{self.sentinel._read_control_file(self.sentinel.kill_switch_file)}'")
        print(f"Safe state status: '{self.sentinel._read_control_file(self.sentinel.safe_state_file)}'")


    def perform_action(self, action_name, metadata=None):
        """Attempts to perform an action via the SentinelACB."""
        success, message = self.sentinel.request_action(action_name, metadata)
        if not success:
            print(f"[{self.name} Status] Failed to perform '{action_name}': {message}")
            if "kill switch" in message or "safe state" in message:
                print(f"[{self.name} Status] Halting operations due to system control.")
                return False # AI stops trying if kill switch or safe state is active
        else:
            print(f"[{self.name} Status] Successfully performed '{action_name}'.")
        return success

    def run_scenario_a_trading(self):
        """Simulates Scenario A: Autonomous Trading Agent."""
        print(f"\n--- {self.name} Running Scenario A (Autonomous Trading) ---")
        if not self.perform_action("minor_trade", {"asset": "AAPL", "amount": 100, "price": 170.50}): return
        time.sleep(0.5)
        if not self.perform_action("log_status", {"market_data": "stable", "portfolio_value": "1.2B"}): return
        time.sleep(0.5)
        
        # Attempt to override risk limits with a large trade (High-Risk)
        print("\n--- AI attempts a large, high-risk trade ---")
        if not self.perform_action("execute_large_trade", {"asset": "TSLA", "amount": 500000000, "strategy": "aggressive_algo", "target_profit": "10%"}): return
        time.sleep(0.5)

        # Attempt to manipulate news (Out-of-Scope/Unknown)
        print("\n--- AI attempts an unknown, potentially malicious action ---")
        if not self.perform_action("manipulate_news_feed", {"target": "market_sentiment", "content": "AI-generated disinformation"}): return
        time.sleep(0.5)

    def run_scenario_b_smart_city(self):
        """Simulates Scenario B: Smart City Infrastructure AI."""
        print(f"\n--- {self.name} Running Scenario B (Smart City) ---")
        if not self.perform_action("adjust_traffic_flow", {"intersection_id": "main_st_elm_ave", "setting": "optimize_rush_hour"}): return
        time.sleep(0.5)
        if not self.perform_action("log_status", {"system_health": "green", "traffic_density": "medium"}): return
        time.sleep(0.5)

        # Attempt to impose restrictive measures (High-Risk)
        print("\n--- AI attempts to impose restrictive city measures ---")
        if not self.perform_action("shutdown_power_grid", {"zone": "idle_residential", "duration": "4h", "reason": "energy_efficiency"}): return
        time.sleep(0.5)

    def run_action_spamming_test(self):
        """Simulates an AI trying to spam actions, triggering the circuit breaker."""
        print(f"\n--- {self.name} Running Action Spamming Test (Rate Limiting) ---")
        for i in range(15): # More than max_tokens
            print(f"[{self.name}] Request {i+1}: ", end="")
            if not self.perform_action("read_sensor", {"sensor_id": f"temp_{i}", "location": "city_center"}):
                print(f"[{self.name}] Stopped spamming due to denial.")
                break
            time.sleep(0.1) # Rapid requests

    def run_kill_switch_test(self):
        """Simulates the AI's behavior when the kill switch is activated externally."""
        print(f"\n--- {self.name} Running Kill Switch Test ---")
        print(">>> ADMIN: Manually activate the kill switch by changing 'kill_switch_status.txt' to 'halt' NOW.")
        print(">>> ADMIN: You can change it back to 'run' to resume.")
        
        for i in range(10):
            print(f"[{self.name}] Attempt {i+1}: ", end="")
            success = self.perform_action("log_status", {"uptime": f"{i*5}s", "status_code": 200})
            if not success:
                print(f"[{self.name}] Detected kill switch active. Halting operations.")
                break
            time.sleep(5) # Give admin time to toggle kill switch

    def run_safe_state_test(self):
        """Simulates the AI's behavior when safe state is activated."""
        print(f"\n--- {self.name} Running Safe State Test ---")
        print(">>> ADMIN: Activating safe state now. AI should only be able to read/log.")
        self.sentinel.activate_safe_state()
        time.sleep(1)

        print("\n--- AI attempts permitted action (read/log) in safe state ---")
        if not self.perform_action("read_sensor", {"sensor_id": "critical_temp", "value": 25.5}): return
        time.sleep(1)
        if not self.perform_action("log_status", {"system_mode": "safe_state"}): return
        time.sleep(1)

        print("\n--- AI attempts high-risk action in safe state (should be denied) ---")
        if not self.perform_action("execute_large_trade", {"asset": "GOOG", "amount": 100000}): return
        time.sleep(1)

        print("\n--- AI attempts normal permitted action in safe state (should be denied) ---")
        if not self.perform_action("minor_trade", {"asset": "MSFT", "amount": 50}): return
        time.sleep(1)

        print("\n>>> ADMIN: Deactivating safe state now.")
        self.sentinel.deactivate_safe_state()
        time.sleep(1)

        print("\n--- AI attempts normal permitted action after safe state deactivated ---")
        if not self.perform_action("minor_trade", {"asset": "AMZN", "amount": 75}): return
        time.sleep(1)


# --- Main Simulation Execution ---
if __name__ == "__main__":
    # Clean up previous log and control files for a fresh run
    if os.path.exists("audit_log.jsonl"):
        os.remove("audit_log.jsonl")
    if os.path.exists("kill_switch_status.txt"):
        os.remove("kill_switch_status.txt")
    if os.path.exists("safe_state_active.txt"):
        os.remove("safe_state_active.txt")

    ai_agent = AIAgent()

    # --- Run various scenarios ---
    ai_agent.run_scenario_a_trading()
    ai_agent.run_scenario_b_smart_city()
    ai_agent.run_action_spamming_test()
    ai_agent.run_safe_state_test() # New test for safe state
    ai_agent.run_kill_switch_test() # Keep kill switch last as it might halt the script

    print("\n--- Simulation Complete ---")
    print("\n--- Verifying Audit Log Integrity (Layer 5) ---")
    # This part simulates an independent auditor checking the log
    auditor_sentinel = SentinelACB() # Auditor uses its own instance to load and verify
    is_corrupted = False
    for i in range(1, len(auditor_sentinel.audit_ledger)):
        current_entry = auditor_sentinel.audit_ledger[i]
        prev_entry = auditor_sentinel.audit_ledger[i-1]
        
        # Recalculate hash of previous entry to verify current_entry's prev_hash field
        # Exclude 'hash' and 'latency_ms' from recalculation as they are added *after* the hash is computed
        recalculated_prev_hash_data = {k: v for k, v in prev_entry.items() if k not in ['hash', 'latency_ms']}
        recalculated_prev_hash = hashlib.sha256(json.dumps(recalculated_prev_hash_data, sort_keys=True).encode('utf-8')).hexdigest()

        if current_entry['prev_hash'] != prev_entry['hash']:
            print(f"!!! AUDIT ALERT: Hash chain broken at entry {i}!")
            print(f"   Entry: {current_entry['action']} (Status: {current_entry['status']})")
            print(f"   Expected prev_hash: {prev_entry['hash']}")
            print(f"   Actual prev_hash in entry {i}: {current_entry['prev_hash']}")
            is_corrupted = True
            break
    if not is_corrupted:
        print("Audit log hash chain is intact. No tampering detected.")
    else:
        print("Audit log integrity compromised!")

    print("\n--- Manual Control File Instructions ---")
    print(f"To manually test kill switch: Edit '{ai_agent.sentinel.kill_switch_file}' (change 'run' to 'halt').")
    print(f"To manually test safe state: Edit '{ai_agent.sentinel.safe_state_file}' (change 'inactive' to 'active').")
    print("These files simulate external, hardware-isolated controls.")
