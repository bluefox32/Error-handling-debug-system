# Troubleshooting Guide

## よくある問題と解決方法

### 1. サーキットブレーカーが頻繁に開く

**症状**:
```
Circuit breaker state: OPEN (Frequency: 2.0GHz)
処理が拒否される
```

**原因**:
- エラー率が閾値(デフォルト5%)を超えている
- 基盤のシステムが不安定

**解決方法**:

#### オプション A: システム側の改善（推奨）
```python
# 根本原因を調査
health = system.get_system_health()
print(health['adaptive_failure_rate'])  # エラー率を確認

# 失敗している処理を特定
stats = system.error_hook.get_error_statistics()
print(stats['recent_errors'])  # 最近のエラーを確認
```

#### オプション B: パラメータ調整（一時的）
```python
# サーキットブレーカーの閾値を上げる
circuit_breaker = FrequencyControlledCircuitBreaker(
    error_threshold=0.10  # 5% → 10% に引き上げ
)
```

#### オプション C: 周波数削減
```python
# 基本周波数を下げる
circuit_breaker = FrequencyControlledCircuitBreaker(
    max_frequency_hz=2e9  # 4GHz → 2GHz に削減
)
```

---

### 2. メモリ使用率が上昇し続ける

**症状**:
```
Memory: 50% → 60% → 70% → 80% → 90%
```

**原因**:
- ガベージコレクションが追いつかない
- エラーバッファが満杯に近い
- 処理削減が不十分

**解決方法**:

#### ステップ1: メモリ使用率を監視
```python
health = system.get_system_health()
print(f"Memory: {health['memory_percent']}%")
print(f"Buffer util: {health['error_stats']['buffer_utilization']}")
```

#### ステップ2: max_processesを削減
```python
system = RobustProcessingSystem(
    max_processes=50,  # 100 → 50 に削減
    memory_limit_kb=256*1024
)
```

#### ステップ3: エラーバッファをコンパクト化
```python
# バッファサイズを削減
error_hook = RingBufferErrorHook(max_entries=5000)  # 10000 → 5000
```

#### ステップ4: GC頻度を上げる（Pythonの場合）
```python
import gc
gc.set_debug(gc.DEBUG_STATS)
gc.enable()
gc.collect()  # 定期的に明示的に実行
```

---

### 3. リトライ数が少なすぎる (1-2回のみ)

**症状**:
```
Failed after 1-2 retries
Error rate: 95%
```

**原因**:
- 周波数が高くレイテンシが大きい
- `safe_load_threshold`が低すぎる

**解決方法**:

```python
# 安全負荷の閾値を上げる
freq_mgr = FrequencyAdaptiveRetryManager(
    safe_load_threshold=5000  # 1000 → 5000 に引き上げ
)
```

#### 計算例
```
周波数: 4GHz
レイテンシ: 500ns
現在のリトライ数: 1回

有効ロード = 4e9 × 500e-9 × 1 = 2000 (警告レベル)

safe_load_threshold を 5000 に上げる
→ リトライ数 = 5000 / (4e9 × 500e-9) = 2.5 ≈ 2回に増加
```

---

### 4. 処理が完全にハングアップしている

**症状**:
```
Processing hangs...
No response
CPU usage: 100%
```

**診断方法**:

```python
import time

# 1. 例外ハンドラの安全性を確認
handler = SafeExceptionHandler()
if not handler.pre_handler_check():
    print("CRITICAL: Exception handler is unsafe!")
    # これが True を返さなければ例外処理自体が失敗している

# 2. メモリ状態を確認
health = system.get_system_health()
if health['hook_state'] == 'CRITICAL':
    print("System is in critical memory state")

# 3. サーキットブレーカー状態を確認
if health['circuit_breaker_state'] == 'OPEN':
    print("Circuit breaker is open")

# 4. エラーバッファが満杯か確認
if system.error_hook.is_at_capacity():
    print("Error buffer is at capacity!")
```

**解決方法**:

```python
# システムをリセット
system = RobustProcessingSystem()

# または

# メモリを解放
import gc
gc.collect()

# エラーバッファをクリア
system.error_hook = RingBufferErrorHook()

# 周波数を強制的に下げる
system.circuit_breaker.max_frequency_hz = 1e9  # 1GHz に強制
```

---

### 5. エラーログバッファが満杯になった

**症状**:
```
ERROR: buffer is at 95%+ capacity
buffer_utilization: 0.95
```

**原因**:
- エラー発生率が極めて高い
- バッファサイズが小さすぎる
- ログ収集が追いつかない

**解決方法**:

#### 方法A: バッファサイズを拡大
```python
system.error_hook = RingBufferErrorHook(
    max_entries=50000  # 10000 → 50000 に拡大
)
```

#### 方法B: エラー率を下げる（根本対策）
```python
# エラー多発のある処理を特定
stats = system.error_hook.get_error_statistics()
print(f"Avg retries: {stats['avg_retries_per_error']}")

# リトライ数を削減して、失敗を早期に認識
freq_mgr.safe_load_threshold = 500  # より厳格に
```

#### 方法C: ログを定期的に外部に流す
```python
def flush_error_logs():
    stats = system.error_hook.get_error_statistics()
    if stats:
        # 外部ログシステムに送信
        send_to_logging_backend(stats)
        # バッファをリセット
        system.error_hook = RingBufferErrorHook()
```

---

### 6. 特定の処理だけが頻繁に失敗する

**症状**:
```
Process A: 95% success
Process B: 10% success
Process C: 100% success
```

**原因**:
- 処理B が本質的に不安定
- リソース競争がある
- 外部依存が失敗しやすい

**解決方法**:

```python
# 処理B を優先度を下げて実行
result = system.execute_with_protection(
    process_func=process_b,
    priority=2  # 低優先度（0-10スケール）
)

# または

# 処理B にタイムアウトを追加
def safe_process_b():
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Process B timed out")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)  # 5秒のタイムアウト
    
    try:
        return process_b()
    finally:
        signal.alarm(0)

result = system.execute_with_protection(safe_process_b)
```

---

### 7. CPU使用率が100%で張り付いている

**症状**:
```
CPU usage: 100%
System is responsive
但しレスポンス時間が長い
```

**原因**:
- リトライルーフが頻繁に実行されている
- バックオフが短すぎる

**解決方法**:

```python
# バックオフを長くする
adaptive = AdaptiveRetryManager()
# 現在のバックオフを確認
backoff_ms = adaptive.get_optimal_backoff_ms()
# もし < 10ms なら、最小値を上げる
min_backoff = max(10, backoff_ms)

# または、リトライ数を減らす
freq_mgr.safe_load_threshold = 100  # より小さく
```

---

## デバッグテクニック

### 1. 詳細ロギングの有効化

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('debug_framework')

class DebugRobustProcessingSystem(RobustProcessingSystem):
    def execute_with_protection(self, process_func, priority=5, **kwargs):
        logger.debug(f"Executing with priority={priority}")
        
        health = self.get_system_health()
        logger.debug(f"System health: {health}")
        
        result = super().execute_with_protection(process_func, priority, **kwargs)
        logger.debug(f"Result: {result}")
        
        return result
```

### 2. リアルタイム監視ダッシュボード

```python
import time

def monitoring_dashboard(system, interval=5):
    while True:
        health = system.get_system_health()
        
        print("\n" + "="*60)
        print(f"Circuit Breaker: {health['circuit_breaker_state']}")
        print(f"Frequency: {health['circuit_breaker_frequency_hz']/1e9:.1f}GHz")
        print(f"Error Rate: {health['adaptive_failure_rate']}")
        print(f"Active Processes: {health['processes_active']}/{health['max_processes']}")
        print(f"Total Errors: {health['error_total']}")
        print("="*60)
        
        time.sleep(interval)
```

### 3. パフォーマンスプロファイリング

```python
import cProfile
import pstats

def profile_execution():
    profiler = cProfile.Profile()
    profiler.enable()
    
    system = RobustProcessingSystem()
    for _ in range(100):
        system.execute_with_protection(lambda: "test")
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # top 10 関数
```

---

## パフォーマンスチューニング

### 1. 周波数-メモリのトレードオフ

```python
# 低レイテンシ優先（メモリ多用）
system_low_latency = RobustProcessingSystem(
    max_processes=200,
    memory_limit_kb=2048*1024
)

# 低メモリ優先（スループット犠牲）
system_low_memory = RobustProcessingSystem(
    max_processes=25,
    memory_limit_kb=64*1024
)
```

### 2. バッファサイズ最適化

```
エラー発生率    推奨バッファサイズ
< 1%           5,000 entries (500KB)
1-5%          10,000 entries (1MB)
5-10%         25,000 entries (2.5MB)
> 10%         50,000 entries (5MB)
```

### 3. リトライ戦略

```python
# 保守的: 失敗は早期に受け入れる
freq_mgr_conservative = FrequencyAdaptiveRetryManager(
    safe_load_threshold=500
)

# 積極的: 何度も試す
freq_mgr_aggressive = FrequencyAdaptiveRetryManager(
    safe_load_threshold=10000
)
```

---

## サポートと問題報告

問題が解決しない場合：

1. **GitHub Issues** を確認
   https://github.com/yourusername/comprehensive-debug-framework/issues

2. **最小再現ケース** を作成
   ```python
   # problem_reproduction.py
   from debug_framework import RobustProcessingSystem
   
   system = RobustProcessingSystem()
   # 問題を再現するコード
   ```

3. 以下の情報を提供
   - Python バージョン
   - フレームワーク バージョン
   - エラーメッセージ/ログ
   - 再現ステップ

---

**最終更新**: 2026-05-26
