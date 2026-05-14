#!/bin/bash
echo "🔍 Verifying SentinelACB Audit Chain..."
python -c "
import sys
sys.path.insert(0, '.')
from sentinelacb.logging.audit import AuditChain
chain = AuditChain('logs/audit_chain.jsonl')
if chain.verify():
    print('✅ Audit chain intact. Entries:', len(chain.chain))
else:
    print('❌ Chain broken. Tamper detected.')
    sys.exit(1)
"