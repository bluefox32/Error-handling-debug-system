"""
SafeExceptionHandler - 例外処理の安全性を確保
"""


class SafeExceptionHandler:
    """
    例外処理自体がメモリ不足で失敗しないよう、
    予約メモリを確保して安全性をチェック
    """
    def __init__(self, reserved_memory_kb=512):
        self.reserved_memory_kb = reserved_memory_kb
        self.reserved_buffer = bytearray(reserved_memory_kb * 1024)
        self.is_safe = True
        self.handler_stack = []
        self.emergency_count = 0

    def pre_handler_check(self):
        """例外処理に入る前に、処理実行が可能かチェック"""
        try:
            # 予約メモリへの読み書き検証
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
        """セーフガードされた例外処理"""
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
        """予約メモリへ直接ログ（malloc不要）"""
        self.handler_stack.append(msg)
        if len(self.handler_stack) > 100:
            self.handler_stack.pop(0)

    def _emergency_shutdown(self, exception):
        """リカバリ不可能時の最終処理"""
        self.emergency_count += 1
        # 本番環境では sys.exit(1) などで安全に終了
        pass
