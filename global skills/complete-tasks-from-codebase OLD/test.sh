#!/bin/bash
# Quick test script for the complete-tasks-from-codebase skill

echo "================================"
echo "Testing complete-tasks-from-codebase skill"
echo "================================"
echo ""

# Get the directory of this script
SKILL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Test file path
TEST_FILE="/Users/admin/dev/Reports/hamm-therapy/requirements.json"

if [ ! -f "$TEST_FILE" ]; then
    echo "❌ Test file not found: $TEST_FILE"
    exit 1
fi

echo "📄 Running skill on: $TEST_FILE"
echo ""

# Run the skill
python3 "$SKILL_DIR/complete-tasks.py" "$TEST_FILE"

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Skill completed successfully!"
    echo ""
    echo "📊 Verification:"
    
    # Count enriched items
    python3 << 'EOF'
import json

with open('/Users/admin/dev/Reports/hamm-therapy/requirements.json', 'r') as f:
    data = json.load(f)

req_count = len(data.get('requirements', []))
test_count = 0
impl_count = 0

for req in data.get('requirements', []):
    if 'test' in req and req['test'] and 'Feature' in req['test']:
        test_count += 1
    
    for subtask in req.get('subtasks', []):
        if 'implementation' in subtask and subtask['implementation'] and 'Overview' in subtask['implementation']:
            impl_count += 1
        if 'test' in subtask and subtask['test'] and 'Feature' in subtask['test']:
            test_count += 1

print(f"  ✓ Requirements with tests: {test_count}")
print(f"  ✓ Subtasks with implementation: {impl_count}")
EOF
else
    echo ""
    echo "❌ Skill failed!"
    exit 1
fi
