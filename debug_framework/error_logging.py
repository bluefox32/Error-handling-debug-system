"""
RingBufferErrorHook - リングバッファ型エラーロギング
"""


class RingBufferErrorHook:
    """リングバッファ型エラーロギング機構"""
    def __init__(self, max_entries=10000):
        self.max_entries = max_entries
        self.buffer = [None] * max_entries
        self.write_index = 0
        self.entry_count = 0
        self.total_errors = 0

    def log_error(self, timestamp, error_type, retry_count, frequency_hz):
        """エラーをログに記録"""
        self.buffer[self.write_index] = {
            'timestamp': timestamp,
            'error_type': error_type,
            'retry_count': retry_count,
            'frequency_hz': frequency_hz
        }
        
        self.write_index = (self.write_index + 1) % self.max_entries
        self.entry_count = min(self.entry_count + 1, self.max_entries)
        self.total_errors += 1

    def get_error_statistics(self):
        """統計情報を取得"""
        if self.entry_count == 0:
            return None
        
        recent_errors = [e for e in self.buffer[:self.entry_count] if e]
        
        if len(recent_errors) == 0:
            return None
        
        total_retries = sum(e['retry_count'] for e in recent_errors)
        avg_retries = total_retries / len(recent_errors)
        
        high_freq_errors = sum(1 for e in recent_errors if e['frequency_hz'] > 3e9)
        
        return {
            'total_errors_ever': self.total_errors,
            'recent_errors': len(recent_errors),
            'avg_retries_per_error': avg_retries,
            'high_frequency_errors': high_freq_errors,
            'buffer_utilization': self.entry_count / self.max_entries
        }

    def is_at_capacity(self):
        """容量に達しているか確認"""
        return self.entry_count > self.max_entries * 0.95
