"""ReorderIQ: observable purchase propensity, with temporal evidence."""

import os

# Avoid optional Windows physical-core probes (WMIC is absent on recent Windows).
# Respect explicit caller settings; the experiment also bounds native pools.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

__version__ = "0.2.0"
