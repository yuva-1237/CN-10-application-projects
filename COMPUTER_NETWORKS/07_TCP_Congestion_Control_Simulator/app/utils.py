"""Plotting and formatting utilities for TCP Congestion Simulator."""
import logging
from pathlib import Path
from typing import List

def render_ascii_graph(rounds: List[int], cwnd_values: List[float], max_height: int = 15) -> str:
    """Generate high-clarity ASCII line plot of cwnd vs Transmission Round for terminal and viva."""
    if not rounds or not cwnd_values:
        return ""

    max_cwnd = max(max(cwnd_values), 1.0)
    width = len(rounds)
    grid = [[" " for _ in range(width)] for _ in range(max_height + 1)]

    # Plot points
    for idx, cwnd in enumerate(cwnd_values):
        # Scale to row index (0 is bottom)
        row = int(round((cwnd / max_cwnd) * max_height))
        row = min(max(row, 0), max_height)
        grid[row][idx] = "*"

    lines = []
    lines.append(f"  ^ cwnd (MSS) [Peak: {max_cwnd:.1f}]")
    lines.append("  |")
    for r in range(max_height, -1, -1):
        y_val = (r / max_height) * max_cwnd
        row_str = "".join(grid[r])
        lines.append(f"{y_val:>4.0f} | {row_str}")

    lines.append("   0 +-" + "-" * width + "-> Transmission Round (RTT)")

    # Render round numbers below axis
    round_labels = ""
    for r in rounds:
        if r % 5 == 0 or r == 1 or r == rounds[-1]:
            round_labels += str(r % 10)
        else:
            round_labels += " "
    lines.append("       " + round_labels)

    return "\n".join(lines)

def setup_logger(name: str, log_file: Path | None = None) -> logging.Logger:
    """Configure standard logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
