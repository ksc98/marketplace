#!/usr/bin/env python3
"""Snake-draft pick numbers: picks.py <teams> <slot> [rounds]."""
import sys

teams, slot = int(sys.argv[1]), int(sys.argv[2])
rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 13
print([r * teams + (slot if r % 2 == 0 else teams - slot + 1) for r in range(rounds)])
