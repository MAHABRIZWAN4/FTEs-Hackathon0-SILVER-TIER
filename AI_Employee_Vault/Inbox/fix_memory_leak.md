# Fix Memory Leak in Background Worker

Priority: URGENT - Production issue!

## Issue
Background worker process memory usage grows continuously until crash.

## Symptoms
- Memory increases by ~100MB/hour
- Process crashes after 8-10 hours
- Requires manual restart

## Investigation Needed
- Profile memory usage
- Check for unclosed connections
- Review event listeners
- Analyze object retention
