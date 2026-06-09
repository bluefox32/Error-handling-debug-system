# Architecture

## システムアーキテクチャ

### 全体図

```
RobustProcessingSystem
├── SafeExceptionHandler (予約メモリで例外処理を保護)
├── ProcessHookManager (メモリ連動の処理数管理)
├── AdaptiveRetryManager (実測データから動的調整)
├── FrequencyAdaptiveRetryManager (周波数適応型リトライ)
├── FrequencyControlledCircuitBreaker (周波数制御)
└── RingBufferErrorHook (エラーログ循環バッファ)
```

## 3層防御アーキテクチャ

### Layer 1: 前処理（Pre-processing）

```
入力
  ↓
[SafeExceptionHandler.pre_handler_check()]
  - 予約メモリへの読み書き検証
  - 例外処理可能性を事前確認
  ↓
[ProcessHookManager.check_hook_state()]
  - メモリ状態を更新
  - 処理削減レベルを判定
  ↓
前処理完了 → メイン処理へ
```

### Layer 2: メイン処理（Main processing）

```
前処理済み処理
  ↓
[ProcessHookManager.can_process_accept()]
  → 処理受け入れ可否を判定
  ↓
[FrequencyControlledCircuitBreaker.can_process()]
  → サーキット状態を確認
  ↓
[FrequencyAdaptiveRetryManager.compute_safe_retry_count()]
  → リトライ上限を計算
  ↓
[リトライループ]
  → 処理実行
  → エラー処理
  → リトライ判定
  ↓
成功/失敗結果
```

### Layer 3: 後処理（Post-processing）

```
処理完了
  ↓
[ProcessHookManager.unregister_process()]
  - 処理カウンターをデクリメント
  ↓
[エラーハンドリング]
  - エラーログをバッファに記録
  ↓
[リカバリ処理]
  - 段階的にシステムを復帰
  ↓
クリーンアップ完了
```

## 各コンポーネントの責務

### 1. SafeExceptionHandler

**目的**: 例外処理自体のハングアップを防止

**実装方式**:
- 初期化時に固定サイズのバッファを確保（512KB）
- 例外処理前に必ずpre_handler_checkを実行
- 失敗時は緊急シャットダウンで安全性を確保

**キーメソッド**:
```python
pre_handler_check()      # 安全性確認
safe_handle(exception)   # 例外処理
_log_to_reserved_memory() # 予約メモリにログ
```

### 2. ProcessHookManager

**目的**: メモリ圧力に応じた処理数の動的削減

**状態遷移**:
```
NORMAL (< 50%)
  ↓ (メモリ使用率上昇)
DEGRADED (50-90%)
  ↓ (メモリ使用率上昇)
CRITICAL (> 90%)
```

**処理数削減ルール**:
- NORMAL: max_processes = 100
- DEGRADED: max_processes = 50-75
- CRITICAL: max_processes = 10

### 3. AdaptiveRetryManager

**目的**: 実測データから動的にリトライパラメータを調整

**追跡メトリクス**:
- 95パーセンタイルレイテンシ
- 99パーセンタイルレイテンシ
- エラー率（失敗回数/総試行回数）

**計算式**:
```
バックオフ = p95_latency × 1.3 × (エラー率係数)
リトライ数 = min(5, floor(recover_time / latency))
```

### 4. FrequencyAdaptiveRetryManager

**目的**: 周波数とレイテンシから安全なリトライ数を計算

**臨界関係式**:
```
有効リトライロード = 周波数 (Hz) × レイテンシ (秒) × リトライ数

安全: < 1000
警告: 1000-5000
危険: > 5000
```

**リトライ削減ロジック**:
```python
# エラー率に応じて削減
if error_rate > 5%:
    safe_r = safe_r // 2
elif error_rate > 2%:
    safe_r = int(safe_r * 0.75)
```

### 5. FrequencyControlledCircuitBreaker

**目的**: エラー率に応じた周波数制御とシステム保護

**状態遷移**:
```
CLOSED (正常)
  ↓ (エラー率 > 閾値)
OPEN (周波数50%削減)
  ↓ (2秒待機)
HALF_OPEN (周波数75%で試験)
  ↓ (成功x5)
CLOSED (復帰)
```

**周波数制御**:
- CLOSED → OPEN: 4GHz → 2GHz (50%削減)
- OPEN → HALF_OPEN: 2GHz → 3GHz (75%復帰)
- HALF_OPEN → CLOSED: 3GHz → 4GHz (100%復帰)

### 6. RingBufferErrorHook

**目的**: メモリリークなしでエラーログを保持

**実装方式**:
- 固定サイズのバッファ（デフォルト10000エントリ）
- 循環上書き方式で古いログを削除
- 統計情報の動的計算

**メモリ効率**:
- エントリ1個: 約100bytes
- 10000エントリ: 約1MB

## 処理フロー詳細

### 成功ケース

```
execute_with_protection()
  ├─ pre_handler_check() ✓
  ├─ check_hook_state() ✓
  ├─ can_process_accept() ✓
  ├─ circuit_breaker.can_process() ✓
  ├─ compute_safe_retry_count() → 3回
  ├─ register_process() ✓
  ├─ [リトライループ]
  │   ├─ [attempt 1] process_func() → 成功
  │   └─ record_success()
  ├─ unregister_process() ✓
  └─ return {'status': 'SUCCESS', ...}
```

### エラー回復ケース

```
execute_with_protection()
  ├─ [初期チェック] ✓
  ├─ [リトライループ]
  │   ├─ [attempt 1] process_func() → 失敗
  │   │   ├─ record_attempt(False)
  │   │   ├─ log_error()
  │   │   └─ backoff待機
  │   │
  │   ├─ [attempt 2] process_func() → 失敗
  │   │   ├─ record_attempt(False)
  │   │   ├─ log_error()
  │   │   └─ backoff待機
  │   │
  │   └─ [attempt 3] process_func() → 成功 ✓
  │       └─ record_success()
  └─ return {'status': 'SUCCESS', 'attempts': 3}
```

### メモリ圧力下でのケース

```
execute_with_protection()
  ├─ check_hook_state(memory=85%) → DEGRADED
  ├─ can_process_accept() 
  │   └─ 現在の処理数が50を超えている
  │   └─ return False
  └─ return {'status': 'CAPACITY_EXCEEDED'}
```

## 周波数-レイテンシ-リトライの臨界関係

### グラフ表現

```
周波数 [GHz]
│
│  4.0 ┌──────────┐
│      │ CRITICAL │  有効ロード > 5000
│      │  Zone    │
│ 2.0 ├──────────┤
│      │  CAUTION │  有効ロード 1000-5000
│      │  Zone    │
│ 1.0 └──────────┘
│      │  SAFE    │  有効ロード < 1000
└──────┼──────────────→ レイテンシ [ns]
     100   200   500
     
リトライ数の安全圏：
    1GHz, 100ns → 最大5回
    2GHz, 100ns → 最大3回
    4GHz, 500ns → 最大1回
```

## パフォーマンス特性

### 時間計算量

- `pre_handler_check()`: O(1)
- `check_hook_state()`: O(1)
- `can_process_accept()`: O(1)
- `compute_safe_retry_count()`: O(1)
- `log_error()`: O(1)
- `get_error_statistics()`: O(n) (n = バッファサイズ)

### 空間計算量

- 基本フレームワーク: O(1)
- 予約メモリ: O(reserved_memory_kb)
- エラーバッファ: O(max_entries)
- **合計**: O(reserved_memory_kb + max_entries)

### ベンチマーク結果

| 操作 | 平均レイテンシ |
|------|---------------|
| 処理実行（成功）| 15ms |
| リトライ1回 | 20ms |
| メモリチェック | <1ms |
| エラーログ記録 | <1ms |

## 拡張ポイント

### 1. カスタム優先度ロジック

```python
class CustomProcessHookManager(ProcessHookManager):
    def can_process_accept(self, priority=5):
        if priority >= 8:
            # 高優先度はCRITICAL時も通す
            return True
        return super().can_process_accept()
```

### 2. 外部メトリクス連携

```python
def get_metrics(system):
    health = system.get_system_health()
    return {
        'circuit_state': health['circuit_breaker_state'],
        'error_rate': health['adaptive_failure_rate'],
        'frequency': health['circuit_breaker_frequency_hz'],
        'processes': health['processes_active'],
    }
```

### 3. カスタムアラート

```python
health = system.get_system_health()
if health['circuit_breaker_state'] == 'OPEN':
    send_alert("Circuit breaker opened")
if float(health['adaptive_failure_rate'].rstrip('%')) > 10:
    send_alert("Error rate exceeds 10%")
```

## 推奨される監視設定

### Prometheus互換メトリクス

```prometheus
# HELP debug_framework_circuit_breaker_state Circuit breaker state (0=CLOSED, 1=OPEN, 2=HALF_OPEN)
# TYPE debug_framework_circuit_breaker_state gauge

# HELP debug_framework_error_rate Current error rate (%)
# TYPE debug_framework_error_rate gauge

# HELP debug_framework_active_processes Active process count
# TYPE debug_framework_active_processes gauge

# HELP debug_framework_frequency Current frequency (Hz)
# TYPE debug_framework_frequency gauge
```

---

詳細については [README.md](../README.md) を参照してください。
