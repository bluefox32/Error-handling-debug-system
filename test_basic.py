"""
基本的なテスト - 各コンポーネントの単体テスト
"""

import pytest
import time
import sys
sys.path.insert(0, '/mnt/user-data/outputs/comprehensive-debug-framework')

from debug_framework import (
    SafeExceptionHandler,
    ProcessHookManager,
    AdaptiveRetryManager,
    FrequencyAdaptiveRetryManager,
    FrequencyControlledCircuitBreaker,
    RingBufferErrorHook,
    ProcessState,
    CircuitBreakerState,
)


class TestSafeExceptionHandler:
    """SafeExceptionHandler のテスト"""
    
    def test_pre_handler_check_success(self):
        """安全性チェックが成功する"""
        handler = SafeExceptionHandler(reserved_memory_kb=512)
        assert handler.pre_handler_check() is True
        assert handler.is_safe is True
    
    def test_safe_handle(self):
        """例外を安全に処理"""
        handler = SafeExceptionHandler()
        try:
            raise ValueError("test")
        except ValueError as e:
            result = handler.safe_handle(e, {})
            assert result is True


class TestProcessHookManager:
    """ProcessHookManager のテスト"""
    
    def test_normal_state(self):
        """正常状態でプロセス受け入れ"""
        hook = ProcessHookManager(max_processes=100)
        hook.check_hook_state(simulated_memory_percent=10)
        assert hook.hook.state == ProcessState.NORMAL
        assert hook.can_process_accept() is True
    
    def test_degraded_state(self):
        """低下状態での処理削減"""
        hook = ProcessHookManager(max_processes=100)
        hook.check_hook_state(simulated_memory_percent=75)
        assert hook.hook.state == ProcessState.DEGRADED
        assert hook.hook.max_processes == 50
    
    def test_critical_state(self):
        """クリティカル状態での厳格な制限"""
        hook = ProcessHookManager(max_processes=100)
        hook.check_hook_state(simulated_memory_percent=95)
        assert hook.hook.state == ProcessState.CRITICAL
        assert hook.hook.max_processes == 10


class TestAdaptiveRetryManager:
    """AdaptiveRetryManager のテスト"""
    
    def test_record_success(self):
        """成功を記録"""
        mgr = AdaptiveRetryManager()
        mgr.record_success()
        mgr.record_success()
        assert mgr.total_attempts == 2


class TestFrequencyAdaptiveRetryManager:
    """周波数適応型リトライマネージャのテスト"""
    
    def test_compute_safe_retry_count(self):
        """安全なリトライ数を計算"""
        mgr = FrequencyAdaptiveRetryManager()
        retry_count = mgr.compute_safe_retry_count(100, 1.0)
        assert 1 <= retry_count <= 5


class TestFrequencyControlledCircuitBreaker:
    """サーキットブレーカーのテスト"""
    
    def test_initial_state(self):
        """初期状態は CLOSED"""
        cb = FrequencyControlledCircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.can_process() is True


class TestRingBufferErrorHook:
    """循環バッファエラーログのテスト"""
    
    def test_log_errors(self):
        """エラーをログ"""
        buffer = RingBufferErrorHook(max_entries=100)
        for i in range(50):
            buffer.log_error(time.time(), "Error", 1, 2e9)
        assert buffer.total_errors == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
