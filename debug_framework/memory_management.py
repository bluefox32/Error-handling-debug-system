"""
ProcessHookManager - メモリ管理のコア機構
"""

import threading
from enum import Enum
from dataclasses import dataclass


class ProcessState(Enum):
    """プロセス状態"""
    NORMAL = 0
    DEGRADED = 1
    CRITICAL = 2
    HALTED = 3


@dataclass
class ProcessHook:
    """プロセスフック情報"""
    max_processes: int = 100
    current_processes: int = 0
    memory_limit_kb: int = 512 * 1024
    current_memory_kb: int = 0
    state: ProcessState = ProcessState.NORMAL
    simulated_memory_percent: float = 0.0


class ProcessHookManager:
    """メモリ管理マネージャー"""
    def __init__(self, max_processes=100, memory_limit_kb=512*1024):
        self.hook = ProcessHook(
            max_processes=max_processes,
            memory_limit_kb=memory_limit_kb
        )
        self.process_queue = []
        self.lock = threading.RLock()

    def check_hook_state(self, simulated_memory_percent=None):
        """最新の状態を確認"""
        with self.lock:
            # シミュレーションか実測か確認
            if simulated_memory_percent is not None:
                memory_percent = simulated_memory_percent
            else:
                # 実測値を取得
                try:
                    import psutil
                    memory_percent = psutil.virtual_memory().percent
                except:
                    memory_percent = 50

            self.hook.simulated_memory_percent = memory_percent

            # 状態判定
            if memory_percent > 90:
                self.hook.state = ProcessState.CRITICAL
                self.hook.max_processes = 10
            elif memory_percent > 75:
                self.hook.state = ProcessState.DEGRADED
                self.hook.max_processes = 50
            elif memory_percent > 50:
                self.hook.state = ProcessState.DEGRADED
                self.hook.max_processes = 75
            else:
                self.hook.state = ProcessState.NORMAL
                self.hook.max_processes = 100

            return self.hook.state

    def can_process_accept(self):
        """プロセスを受け入れられるか確認"""
        with self.lock:
            return self.hook.current_processes < self.hook.max_processes

    def register_process(self, process_id):
        """プロセスを登録"""
        with self.lock:
            if not self.can_process_accept():
                return False
            
            self.hook.current_processes += 1
            self.process_queue.append(process_id)
            return True

    def unregister_process(self, process_id):
        """プロセスを削除"""
        with self.lock:
            if process_id in self.process_queue:
                self.process_queue.remove(process_id)
                self.hook.current_processes = max(0, self.hook.current_processes - 1)
                return True
            return False
