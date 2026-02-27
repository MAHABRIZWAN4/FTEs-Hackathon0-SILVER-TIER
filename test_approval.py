"""
Test the Human Approval Agent
"""
from scripts.request_approval import request_approval, ApprovalTimeout
import sys

print("Testing Human Approval Agent...")
print("=" * 60)

# Test 1: Create approval request (will timeout quickly for demo)
try:
    print("\nTest 1: Creating approval request with 5-second timeout")
    print("(This will timeout to demonstrate the timeout mechanism)")

    approved = request_approval(
        title="Test Approval Request",
        description="This is a test of the approval system",
        details={
            "test_type": "automated",
            "expected_result": "timeout"
        },
        timeout_seconds=5,
        priority="low",
        requester="test_script"
    )

    print(f"Result: {'APPROVED' if approved else 'REJECTED'}")

except ApprovalTimeout as e:
    print(f"\n[EXPECTED] Timeout occurred: {e}")
    print("This demonstrates the timeout mechanism working correctly.")
    sys.exit(0)

except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
    sys.exit(1)
