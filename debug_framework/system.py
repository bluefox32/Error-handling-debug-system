"""
Comprehensive Debug Framework
Null参照ハング・メモリ枯渇・リトライ無限ループ対策フレームワーク
"""

import time
from .exception_handler import SafeExceptionHandler
from .memory_management import ProcessHookManager, ProcessState, ProcessHook
from .retry_manager import AdaptiveRetryManager
from .frequency_control import FrequencyAdaptiveRetryManager, FrequencyControlledCircuitBreaker, CircuitBreakerState
from .error_logging import RingBufferErrorHook


class RobustProcessingSystem:
    """包括的なエラーハンドリング・メモリ管理・リトライ無限ループ対策システム"""
    def __init__(self, max_processes=100, memory_limit_kb=512*1024):
        self.exception_handler = SafeExceptionHandler(reserved_memory_kb=512)
        self.hook_manager = ProcessHookManager(max_processes=max_processes)
        self.adaptive = AdaptiveRetryManager()
        self.frequency_mgr = FrequencyAdaptiveRetryManager()
        self.circuit_breaker = FrequencyControlledCircuitBreaker()
        self.error_hook = RingBufferErrorHook()
        
        self.startup_phase = True
        self.warmup_samples = 50
        self.calibration_count = 0

    def execute_with_protection(self, process_func, priority=5, simulated_memory_percent=None):
        """エラーハンドラ付きで実行"""
        process_id = f"proc_{id(process_func)}_{time.time()}"
        
        # 1. 最終チェック（エラーハンドラの状態確認）
        if not self.exception_handler.pre_handler_check():
            return {'status': 'UNSAFE', 'process_id': process_id}
        
        # 2. メモリ状態を確認
        self.hook_manager.check_hook_state(simulated_memory_percent)
        
        # 3. プロセスを受け入れ可能か確認
        if not self.hook_manager.can_process_accept():
            return {'status': 'CAPACITY_EXCEEDED', 'process_id': process_id}
        
        # 4. サーキットブレーカーを確認
        if not self.circuit_breaker.can_process():
            return {'status': 'CIRCUIT_OPEN', 'process_id': process_id}
        
        # 5. 適応型リトライ回数の決定
        error_rate = self.adaptive.current_failure_rate * 100
        retry_limit = self.frequency_mgr.compute_safe_retry_count(
            estimated_latency_ns=100,
            error_rate_percent=error_rate
        )
        
        # 6. プロセスを登録
        if not self.hook_manager.register_process(process_id):
            return {'status': 'REGISTRATION_FAILED', 'process_id': process_id}
        
        attempt = 0
        start_time = time.perf_counter()
        
        try:
            # 7. リトライループを実行
            for attempt in range(1, retry_limit + 1):
                try:
                    result = process_func()
                    
                    self.circuit_breaker.record_attempt(True)
                    self.adaptive.record_success()
                    
                    if self.startup_phase:
                        self.calibration_count += 1
                        if self.calibration_count >= self.warmup_samples:
                            self.startup_phase = False
                    
                    elapsed = (time.perf_counter() - start_time) * 1000
                    return {
                        'status': 'SUCCESS',
                        'process_id': process_id,
                        'attempts': attempt,
                        'elapsed_ms': elapsed,
                        'result': result
                    }
                
                except Exception as e:
                    self.circuit_breaker.record_attempt(False)
                    
                    latency_ns = int((time.perf_counter() - start_time) * 1e9)
                    self.error_hook.log_error(
                        timestamp=time.time(),
                        error_type=type(e).__name__,
                        retry_count=attempt,
                        frequency_hz=self.circuit_breaker.current_frequency_hz
                    )
                    
                    # エラー処理
                    self.exception_handler.safe_handle(e, {
                        'process_id': process_id,
                        'attempt': attempt,
                        'priority': priority
                    })
                    
                    if attempt < retry_limit:
                        backoff = self.adaptive.get_optimal_backoff_ms()
                        time.sleep(backoff / 1000)
                    else:
                        self.adaptive.record_failure(latency_ns, recovered=False)
        
        finally:
            # 8. プロセスを削除
            self.hook_manager.unregister_process(process_id)
        
        elapsed = (time.perf_counter() - start_time) * 1000
        return {
            'status': 'FAILED',
            'process_id': process_id,
            'attempts': attempt,
            'elapsed_ms': elapsed
        }

    def get_system_health(self):
        """システムの健全性を確認"""
        error_stats = self.error_hook.get_error_statistics()
        
        return {
            'circuit_breaker_state': self.circuit_breaker.state.name,
            'circuit_breaker_frequency_hz': self.circuit_breaker.current_frequency_hz,
            'hook_state': self.hook_manager.hook.state.name,
            'processes_active': self.hook_manager.hook.current_processes,
            'max_processes': self.hook_manager.hook.max_processes,
            'memory_percent': self.hook_manager.hook.simulated_memory_percent,
            'adaptive_failure_rate': f"{self.adaptive.current_failure_rate*100:.2f}%",
            'adaptive_p95_latency_ns': self.adaptive.percentile_95_latency,
            'error_total': self.error_hook.total_errors,
            'error_stats': error_stats
        }
