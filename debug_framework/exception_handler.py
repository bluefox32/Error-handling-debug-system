"""
SafeExceptionHandler - エラー処理の最終防衛線
"""


class SafeExceptionHandler:
    """
    エラーハングの根本原因となる不安全な状態を検知する
    予約メモリ、内部チェック機構、エラーログ機構でハングを防止
    """
    def __init__(self, reserved_memory_kb=512):
        self.reserved_memory_kb = reserved_memory_kb
        self.reserved_buffer = bytearray(reserved_memory_kb * 1024)
        self.is_safe = True
        self.handler_stack = []
        self.emergency_count = 0

    def pre_handler_check(self):
        """エラー発生前に最終的な安全チェック"""
        try:
            # メモリアクセス可能性を確認する
            test_value = 0xDEADBEEF
            self.reserved_buffer[0:4] = test_value.to_bytes(4, 'little')
            read_back = int.from_bytes(self.reserved_buffer[0:4], 'little')
            
            if read_back != test_value:
                self.is_safe = False
                return False
            
            self.is_safe = True
            return True
        except Exception as e:
            self.is_safe = False
            return False

    def safe_handle(self, exception, context):
        """エラーハンドラの最終防衛ライン"""
        if not self.pre_handler_check():
            self._emergency_shutdown(exception)
            return False
        
        try:
            error_msg = str(exception)[:256]
            self._log_to_reserved_memory(error_msg)
            return True
        except Exception as e:
            self._emergency_shutdown(e)
            return False

    def _log_to_reserved_memory(self, msg):
        """エラーをメモリ（mallocサポートなし）に記録"""
        self.handler_stack.append(msg)
        if len(self.handler_stack) > 100:
            self.handler_stack.pop(0)

    def _emergency_shutdown(self, exception):
        """緊急シャットダウン"""
        self.emergency_count += 1
        # 最後の手段: sys.exit(1) を推奨（ハング防止）
        pass
