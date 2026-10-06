"""TCP Congestion Control State Machine (Tahoe and Reno models)."""
from dataclasses import dataclass
from typing import Dict, List, Optional

STATE_SLOW_START = "SLOW_START"
STATE_CONGESTION_AVOIDANCE = "CONGESTION_AVOIDANCE"
STATE_FAST_RECOVERY = "FAST_RECOVERY"

EVENT_NORMAL_ACK = "ACK_RECEIVED"
EVENT_TIMEOUT = "TIMEOUT"
EVENT_TRIPLE_DUP_ACK = "TRIPLE_DUP_ACK"

@dataclass
class RoundLog:
    round_num: int
    cwnd: float
    ssthresh: float
    state: str
    event: str
    description: str

class TCPCongestionEngine:
    def __init__(
        self,
        initial_cwnd: float = 1.0,
        initial_ssthresh: float = 16.0,
        variant: str = "RENO"
    ):
        self.initial_cwnd = float(initial_cwnd)
        self.initial_ssthresh = float(initial_ssthresh)
        self.variant = variant.upper()

        self.cwnd = self.initial_cwnd
        self.ssthresh = self.initial_ssthresh
        self.state = STATE_SLOW_START
        self.current_round = 0
        self.history: List[RoundLog] = []

    def reset(self) -> None:
        """Reset state machine to initial configuration."""
        self.cwnd = self.initial_cwnd
        self.ssthresh = self.initial_ssthresh
        self.state = STATE_SLOW_START
        self.current_round = 0
        self.history.clear()

    def step(self, event: str = EVENT_NORMAL_ACK) -> RoundLog:
        """Advance simulation by one transmission round (RTT) given an event."""
        self.current_round += 1
        desc = ""

        if event == EVENT_TIMEOUT:
            # Drastic loss event (Timer expiry)
            old_cwnd = self.cwnd
            self.ssthresh = max(2.0, self.cwnd / 2.0)
            self.cwnd = 1.0
            self.state = STATE_SLOW_START
            desc = f"Timeout! ssthresh halved to {self.ssthresh:.0f}, cwnd reset from {old_cwnd:.0f} to 1. Entered Slow Start."

        elif event == EVENT_TRIPLE_DUP_ACK:
            # 3 Duplicate ACKs received (Fast Retransmit)
            old_cwnd = self.cwnd
            self.ssthresh = max(2.0, self.cwnd / 2.0)

            if self.variant == "TAHOE":
                # Tahoe treats triple dup ACK identically to timeout
                self.cwnd = 1.0
                self.state = STATE_SLOW_START
                desc = f"Triple Dup ACK (Tahoe): ssthresh={self.ssthresh:.0f}, cwnd reset to 1. Slow Start."
            else:
                # Reno enters Fast Recovery and resumes at ssthresh
                self.cwnd = self.ssthresh
                self.state = STATE_CONGESTION_AVOIDANCE
                desc = f"Triple Dup ACK (Reno Fast Recovery): ssthresh={self.ssthresh:.0f}, cwnd set to {self.cwnd:.0f}. Congestion Avoidance."

        else:
            # Normal in-order ACK round
            if self.state == STATE_SLOW_START:
                desc = f"Slow Start exponential growth: cwnd doubled ({self.cwnd:.0f} -> {self.cwnd * 2:.0f})."
                self.cwnd *= 2.0
                if self.cwnd >= self.ssthresh:
                    self.state = STATE_CONGESTION_AVOIDANCE
                    desc += f" cwnd reached ssthresh ({self.ssthresh:.0f}). Switched to Congestion Avoidance."
            elif self.state == STATE_CONGESTION_AVOIDANCE:
                self.cwnd += 1.0
                desc = f"Congestion Avoidance linear growth (AIMD): cwnd increased by +1 ({self.cwnd:.0f})."

        log_entry = RoundLog(
            round_num=self.current_round,
            cwnd=self.cwnd,
            ssthresh=self.ssthresh,
            state=self.state,
            event=event,
            description=desc
        )
        self.history.append(log_entry)
        return log_entry

    def run_simulation(self, total_rounds: int, loss_schedule: Dict[int, str]) -> List[RoundLog]:
        """Execute continuous simulation with scheduled loss events."""
        self.reset()
        for r in range(1, total_rounds + 1):
            event = loss_schedule.get(r, EVENT_NORMAL_ACK)
            self.step(event)
        return self.history
