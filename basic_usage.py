"""
基本的な使用例 - Comprehensive Debug Framework
"""

from debug_framework import RobustProcessingSystem
import time
import random


def example_1_basic_usage():
    """例1: 基本的な使い方"""
    print("=" * 70)
    print("例1: 基本的な使い方")
    print("=" * 70)
    
    # システムを初期化
    system = RobustProcessingSystem(
        max_processes=100,
        memory_limit_kb=512*1024
    )
    
    # 処理を定義
    def my_process():
        time.sleep(0.01)
        return "完了"
    
    # 処理を実行
    result = system.execute_with_protection(
        process_func=my_process,
        priority=5
    )
    
    print(f"結果: {result['status']}")
    print(f"実行時間: {result.get('elapsed_ms', 'N/A'):.2f}ms")


def example_2_error_handling():
    """例2: エラー処理"""
    print("\n" + "=" * 70)
    print("例2: エラー処理とリトライ")
    print("=" * 70)
    
    system = RobustProcessingSystem()
    
    attempt_count = [0]
    
    def failing_process():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise RuntimeError(f"エラー #{attempt_count[0]}")
        return "リトライで復帰"
    
    result = system.execute_with_protection(failing_process)
    
    print(f"結果: {result['status']}")
    print(f"試行回数: {result.get('attempts', 'N/A')}")
    print(f"記録されたエラー: {system.error_hook.total_errors}")


def example_3_memory_monitoring():
    """例3: メモリ圧力の監視"""
    print("\n" + "=" * 70)
    print("例3: メモリ圧力の監視")
    print("=" * 70)
    
    system = RobustProcessingSystem(max_processes=100)
    
    def sample_process():
        return "OK"
    
    # メモリ圧力を段階的にシミュレート
    memory_levels = [10, 50, 70, 85, 95]
    
    for mem in memory_levels:
        result = system.execute_with_protection(
            sample_process,
            simulated_memory_percent=mem
        )
        
        health = system.get_system_health()
        print(f"メモリ: {mem}% → 状態: {health['hook_state']}, " +
              f"最大処理: {health['max_processes']}")


def example_4_circuit_breaker():
    """例4: サーキットブレーカー"""
    print("\n" + "=" * 70)
    print("例4: サーキットブレーカーの動作")
    print("=" * 70)
    
    system = RobustProcessingSystem()
    
    def unreliable_process():
        # 70% の確率でエラー
        if random.random() < 0.7:
            raise RuntimeError("処理失敗")
        return "成功"
    
    success = 0
    failed = 0
    blocked = 0
    
    for i in range(30):
        result = system.execute_with_protection(unreliable_process)
        
        if result['status'] == 'SUCCESS':
            success += 1
        elif result['status'] == 'CIRCUIT_OPEN':
            blocked += 1
        else:
            failed += 1
        
        if (i + 1) % 10 == 0:
            health = system.get_system_health()
            print(f"[{i+1:2d}] Circuit: {health['circuit_breaker_state']}, " +
                  f"Freq: {health['circuit_breaker_frequency_hz']/1e9:.1f}GHz")
    
    print(f"\n結果: 成功={success}, 失敗={failed}, ブロック={blocked}")


def example_5_frequency_calculation():
    """例5: 周波数-レイテンシ-リトライの計算"""
    print("\n" + "=" * 70)
    print("例5: 周波数適応型リトライ計算")
    print("=" * 70)
    
    from debug_framework import FrequencyAdaptiveRetryManager
    
    mgr = FrequencyAdaptiveRetryManager()
    
    print("\n周波数が一定(2GHz)で、レイテンシとエラー率を変動:")
    print(f"{'Latency(ns)':>12} {'Error 1%':>12} {'Error 5%':>12} {'Error 10%':>12}")
    print("-" * 50)
    
    for latency in [50, 100, 200, 500]:
        r1 = mgr.compute_safe_retry_count(latency, 1.0)
        r5 = mgr.compute_safe_retry_count(latency, 5.0)
        r10 = mgr.compute_safe_retry_count(latency, 10.0)
        print(f"{latency:>12d} {r1:>12d} {r5:>12d} {r10:>12d}")


def example_6_system_health():
    """例6: システムヘルスレポート"""
    print("\n" + "=" * 70)
    print("例6: システムヘルスレポート")
    print("=" * 70)
    
    system = RobustProcessingSystem()
    
    # 処理を何度か実行
    for i in range(20):
        def test_process():
            if random.random() < 0.1:  # 10% のエラー率
                raise RuntimeError("テストエラー")
            time.sleep(0.001)
            return "OK"
        
        system.execute_with_protection(test_process)
    
    # ヘルスレポートを表示
    health = system.get_system_health()
    
    print(f"サーキットブレーカー状態: {health['circuit_breaker_state']}")
    print(f"周波数: {health['circuit_breaker_frequency_hz']/1e9:.1f}GHz")
    print(f"フック状態: {health['hook_state']}")
    print(f"アクティブプロセス: {health['processes_active']}/{health['max_processes']}")
    print(f"エラー率: {health['adaptive_failure_rate']}")
    print(f"総エラー数: {health['error_total']}")
    
    if health['error_stats']:
        print(f"平均リトライ数: {health['error_stats']['avg_retries_per_error']:.1f}")


def example_7_advanced_configuration():
    """例7: 高度な設定"""
    print("\n" + "=" * 70)
    print("例7: 高度な設定とカスタマイズ")
    print("=" * 70)
    
    from debug_framework import (
        RobustProcessingSystem,
        FrequencyAdaptiveRetryManager,
        FrequencyControlledCircuitBreaker
    )
    
    # カスタム周波数マネージャーの作成
    freq_mgr = FrequencyAdaptiveRetryManager(
        safe_load_threshold=2000,  # より許容的
        critical_load_threshold=8000
    )
    
    # カスタムサーキットブレーカーの作成
    cb = FrequencyControlledCircuitBreaker(
        error_threshold=0.08,  # 8% のエラー率で開く
        max_frequency_hz=2e9   # 最大2GHz
    )
    
    print(f"周波数マネージャー: safe_threshold={freq_mgr.safe_load_threshold}")
    print(f"サーキットブレーカー: error_threshold={cb.error_threshold*100:.1f}%")
    print(f"最大周波数: {cb.max_frequency_hz/1e9:.1f}GHz")
    
    # 有効リトライロードを計算
    load = freq_mgr.compute_effective_retry_load(2e9, 100, 3)
    risk = freq_mgr.predict_hangup_risk(load, 5.0)
    
    print(f"\n有効リトライロード: {load:.0f}")
    print(f"ハングアップリスク: {risk['risk_level']}")


def example_8_exception_safety():
    """例8: 例外処理の安全性"""
    print("\n" + "=" * 70)
    print("例8: 例外処理の安全性")
    print("=" * 70)
    
    from debug_framework import SafeExceptionHandler
    
    handler = SafeExceptionHandler(reserved_memory_kb=512)
    
    # 安全性チェック
    is_safe = handler.pre_handler_check()
    print(f"例外ハンドラは安全: {is_safe}")
    
    # 例外を処理
    try:
        raise ValueError("テスト例外")
    except ValueError as e:
        success = handler.safe_handle(e, {'context': 'example'})
        print(f"例外処理成功: {success}")
        print(f"ログスタックサイズ: {len(handler.handler_stack)}")


# ============================================================================
# メイン実行
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "包括的デバッグフレームワーク - 基本的な使用例".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    examples = [
        ("基本的な使い方", example_1_basic_usage),
        ("エラー処理", example_2_error_handling),
        ("メモリ監視", example_3_memory_monitoring),
        ("サーキットブレーカー", example_4_circuit_breaker),
        ("周波数計算", example_5_frequency_calculation),
        ("ヘルスレポート", example_6_system_health),
        ("高度な設定", example_7_advanced_configuration),
        ("例外処理安全性", example_8_exception_safety),
    ]
    
    for name, example_func in examples:
        try:
            example_func()
            time.sleep(0.5)
        except Exception as e:
            print(f"\n[エラー] {name}: {e}")
    
    print("\n" + "="*70)
    print("すべての例が完了しました")
    print("="*70)
    print("\n詳細は README.md と docs/ を参照してください。")
