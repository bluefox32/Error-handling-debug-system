"""
周波数適応型リトライマネージャーと各種フレームワーク
"""

import time
from enum import Enum


class CircuitBreakerState(Enum):
    """サーキットブレーカーの状態"""
    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2


class FrequencyAdaptiveRetryManager:
    """周波数適応型リトライマネージャー"""
    def __init__(self, safe_load_threshold=1000, critical_load_threshold=5000):
        self.safe_load_threshold = safe_load_threshold
        self.critical_load_threshold = critical_load_threshold
        self.measured_frequency = 2e9

    def compute_effective_retry_load(self, frequency_hz, latency_ns, retry_count):
        """実効リトライ負荷 = 周波数 × レイテンシ × リトライ回数"""
        return frequency_hz * (latency_ns * 1e-9) * retry_count

    def compute_safe_retry_count(self, estimated_latency_ns, error_rate_percent):
        """安全なリトライ回数を計算"""
        f = self.measured_frequency
        L = estimated_latency_ns * 1e-9
        
        safe_r = int(self.safe_load_threshold / (f * L + 1e-12))
        
        if error_rate_percent > 5.0:
            safe_r = max(1, safe_r // 2)
        elif error_rate_percent > 2.0:
            safe_r = max(2, int(safe_r * 0.75))
        
        return max(1, min(5, safe_r))

    def predict_hangup_risk(self, current_load, error_rate):
        """ハングアップリスクを予測"""
        if current_load > self.critical_load_threshold:
            return {
                'risk_level': 'CRITICAL',
                'estimated_seconds': 10,
                'action': 'REDUCE_FREQUENCY_IMMEDIATELY'
            }
        elif current_load > self.safe_load_threshold:
            return {
                'risk_level': 'HIGH',
                'estimated_seconds': 60,
                'action': 'REDUCE_FREQUENCY'
            }
        else:
            return {
                'risk_level': 'SAFE',
                'estimated_seconds': None,
                'action': 'NORMAL'
            }


class FrequencyControlledCircuitBreaker:
    """周波数制御されたサーキットブレーカー"""
    def __init__(self, error_threshold=0.05, window_size=1000, max_frequency_hz=4e9):
        self.state = CircuitBreakerState.CLOSED
        self.error_threshold = error_threshold
        self.error_count = 0
        self.total_count = 0
        self.window_size = window_size
        self.max_frequency_hz = max_frequency_hz
        self.current_frequency_hz = max_frequency_hz
        self.open_time = None
        self.half_open_attempts = 0

    def record_attempt(self, success):
        """試行を記録"""
        self.total_count += 1
        if not success:
            self.error_count += 1
        
        if self.total_count > self.window_size:
            self.error_count = max(0, self.error_count - 1)
            self.total_count = self.window_size
        
        error_rate = self.error_count / max(1, self.total_count)
        
        if self.state == CircuitBreakerState.CLOSED:
            if error_rate > self.error_threshold:
                self._open_circuit()
        
        elif self.state == CircuitBreakerState.OPEN:
            if time.time() - self.open_time > 2:
                self._half_open_circuit()
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.half_open_attempts += 1
            if success and self.half_open_attempts > 5:
                self._close_circuit()
            elif not success:
                self._open_circuit()

    def _open_circuit(self):
        self.state = CircuitBreakerState.OPEN
        self.open_time = time.time()
        self.current_frequency_hz = self.max_frequency_hz * 0.5

    def _half_open_circuit(self):
        self.state = CircuitBreakerState.HALF_OPEN
        self.current_frequency_hz = self.max_frequency_hz * 0.75
        self.half_open_attempts = 0

    def _close_circuit(self):
        self.state = CircuitBreakerState.CLOSED
        self.current_frequency_hz = self.max_frequency_hz
        self.error_count = 0
        self.total_count = 0

    def can_process(self):
        """処理できるか確認"""
        return self.state != CircuitBreakerState.OPEN
