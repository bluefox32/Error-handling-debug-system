"""
AdaptiveRetryManager - 適応型リトライ管理
"""

import time
from collections import deque


class AdaptiveRetryManager:
    """適応型リトライ戦略の実装"""
    def __init__(self, window_size=100):
        self.failure_times = deque(maxlen=window_size)
        self.recovery_times = deque(maxlen=window_size)
        self.observed_latencies = deque(maxlen=window_size)
        
        self.percentile_95_latency = 0
        self.percentile_99_latency = 0
        self.current_failure_rate = 0.0
        self.total_attempts = 0
        self.failed_attempts = 0

    def record_failure(self, latency_ns, recovered=True, recovery_latency_ns=None):
        """失敗を記録"""
        self.failure_times.append(time.time())
        self.observed_latencies.append(latency_ns)
        
        if recovered and recovery_latency_ns:
            self.recovery_times.append(recovery_latency_ns)
        
        self.failed_attempts += 1
        self.total_attempts += 1
        self._update_statistics()

    def record_success(self):
        """成功を記録"""
        self.total_attempts += 1
        self._update_statistics()

    def _update_statistics(self):
        """統計情報を更新"""
        if len(self.observed_latencies) < 5:
            return
        
        sorted_latencies = sorted(self.observed_latencies)
        idx_95 = int(len(sorted_latencies) * 0.95)
        idx_99 = int(len(sorted_latencies) * 0.99)
        
        self.percentile_95_latency = sorted_latencies[max(0, idx_95)]
        self.percentile_99_latency = sorted_latencies[max(0, idx_99)]
        
        self.current_failure_rate = (self.failed_attempts / max(1, self.total_attempts))

    def get_optimal_backoff_ms(self):
        """最適なバックオフ時間を計算"""
        if self.percentile_95_latency == 0:
            base_backoff = 10.0
        else:
            base_backoff = (self.percentile_95_latency / 1000) * 1.3
        
        if self.current_failure_rate > 0.5:
            base_backoff *= 2.0
        elif self.current_failure_rate > 0.2:
            base_backoff *= 1.5
        
        return max(1.0, min(100.0, base_backoff))

    def get_optimal_max_retries(self):
        """最適な最大リトライ回数を計算"""
        if self.current_failure_rate < 0.01:
            return 5
        elif self.current_failure_rate < 0.05:
            return 4
        elif self.current_failure_rate < 0.1:
            return 3
        else:
            return 2
