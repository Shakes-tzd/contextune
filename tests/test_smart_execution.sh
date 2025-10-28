#!/bin/bash
# Tests for smart script execution with AI error recovery

echo "🧪 Testing smart script execution system"
echo "=========================================="
echo ""

# Test 1: Success path (no errors)
echo "Test 1: Success path (script succeeds)"
echo "--------------------------------------"

cat > /tmp/test_success.sh << 'EOF'
#!/bin/bash
echo "Script executed successfully"
exit 0
EOF
chmod +x /tmp/test_success.sh

RESULT=$(./scripts/smart_execute.sh /tmp/test_success.sh 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ] && [[ "$RESULT" == *"successfully"* ]]; then
    echo "✅ PASS: Success path works"
else
    echo "❌ FAIL: Success path broken"
    echo "Result: $RESULT"
fi

echo ""

# Test 2: Simple error (should work without AI if handler not available)
echo "Test 2: Error detection"
echo "----------------------"

cat > /tmp/test_error.sh << 'EOF'
#!/bin/bash
echo "Simulated error" >&2
exit 1
EOF
chmod +x /tmp/test_error.sh

RESULT=$(./scripts/smart_execute.sh /tmp/test_error.sh 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "✅ PASS: Error detected correctly"
    if [[ "$RESULT" == *"Script failed with exit code 1"* ]]; then
        echo "✅ PASS: Error message formatted correctly"
    fi
else
    echo "❌ FAIL: Error not detected"
fi

echo ""

# Test 3: Error log creation
echo "Test 3: Error logging"
echo "--------------------"

ERROR_LOGS=$(ls logs/script_errors/*.json 2>/dev/null | wc -l)

if [ $ERROR_LOGS -gt 0 ]; then
    echo "✅ PASS: Error logs created ($ERROR_LOGS found)"

    # Check latest log format
    LATEST_LOG=$(ls -t logs/script_errors/*.json | head -1)
    if jq -e '.script and .exit_code and .error_output' "$LATEST_LOG" > /dev/null 2>&1; then
        echo "✅ PASS: Error log has correct JSON structure"
    else
        echo "❌ FAIL: Error log missing required fields"
    fi
else
    echo "⚠️  SKIP: No error logs found (might be first run)"
fi

echo ""

# Test 4: Script wrapper overhead
echo "Test 4: Performance (wrapper overhead)"
echo "-------------------------------------"

cat > /tmp/test_instant.sh << 'EOF'
#!/bin/bash
exit 0
EOF
chmod +x /tmp/test_instant.sh

START=$(date +%s%N)
./scripts/smart_execute.sh /tmp/test_instant.sh > /dev/null 2>&1
END=$(date +%s%N)

DURATION_MS=$(( ($END - $START) / 1000000 ))

if [ $DURATION_MS -lt 100 ]; then
    echo "✅ PASS: Wrapper overhead minimal (<100ms: ${DURATION_MS}ms)"
else
    echo "⚠️  WARNING: Wrapper overhead high (${DURATION_MS}ms)"
fi

echo ""

# Test 5: Deterministic git scripts exist
echo "Test 5: Git workflow scripts"
echo "----------------------------"

if [ -f "./scripts/commit_and_push.sh" ]; then
    echo "✅ PASS: commit_and_push.sh exists"
else
    echo "❌ FAIL: commit_and_push.sh missing"
fi

if [ -f "./scripts/create_pr.sh" ]; then
    echo "✅ PASS: create_pr.sh exists"
else
    echo "❌ FAIL: create_pr.sh missing"
fi

if [ -f "./scripts/merge_and_cleanup.sh" ]; then
    echo "✅ PASS: merge_and_cleanup.sh exists"
else
    echo "❌ FAIL: merge_and_cleanup.sh missing"
fi

echo ""

# Cleanup
rm -f /tmp/test_*.sh

echo "=========================================="
echo "✅ Smart execution tests complete"
echo "=========================================="
