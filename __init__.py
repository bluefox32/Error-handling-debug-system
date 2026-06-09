"""
Comprehensive Debug Framework
Null参照ハング・メモリ枯渇・リトライ無限ループ対策フレームワーク
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

from .exception_handler import SafeExceptionHandler
from .memory_management import ProcessHookManager, ProcessState, ProcessHook
from .retry_manager import AdaptiveRetryManager
from .frequency_control import FrequencyAdaptiveRetryManager, FrequencyControlledCircuitBreaker, CircuitBreakerState
from .error_logging import RingBufferErrorHook
from .system import RobustProcessingSystem

__all__ = [
    "SafeExceptionHandler",
    "ProcessHookManager",
    "ProcessState",
    "ProcessHook",
    "AdaptiveRetryManager",
    "FrequencyAdaptiveRetryManager",
    "FrequencyControlledCircuitBreaker",
    "CircuitBreakerState",
    "RingBufferErrorHook",
    "RobustProcessingSystem",
]
