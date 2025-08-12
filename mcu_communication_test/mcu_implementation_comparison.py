#!/usr/bin/env python3
"""
MCU 구현 비교 테스트

기존 LMAMCU vs Fast LMAMCU 성능 및 안정성 비교
동일한 조건에서 두 구현의 차이점을 정확히 측정
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# 프로젝트 루트를 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from fast_lma_mcu_test import FastLMAMCU

    from src.domain.enums.mcu_enums import TestMode
    from src.infrastructure.implementation.hardware.mcu.lma.lma_mcu import LMAMCU
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    print("필요한 모듈을 확인하세요.")
    sys.exit(1)


class MCUImplementationComparator:
    """MCU 구현 비교 분석기"""

    def __init__(self, port: str = "COM4", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.test_results: Dict[str, List[Dict]] = {"original": [], "fast": []}

    async def test_original_mcu(self, wait_time: float = 0.1) -> Dict[str, Any]:
        """기존 LMAMCU 테스트"""
        print(f"\n🔧 기존 LMAMCU 테스트 (대기시간: {wait_time}s)")
        print("=" * 50)

        mcu = LMAMCU()
        session_start = time.time()

        try:
            # 연결
            await mcu.connect(
                port=self.port,
                baudrate=self.baudrate,
                timeout=10.0,
                bytesize=8,
                stopbits=1,
                parity=None,
            )

            # 테스트 시퀀스
            commands = [
                ("set_test_mode", lambda: mcu.set_test_mode(TestMode.MODE_1)),
                ("set_upper_temperature", lambda: mcu.set_upper_temperature(52.0)),
                ("set_fan_speed", lambda: mcu.set_fan_speed(10)),
                ("start_standby_heating", lambda: mcu.start_standby_heating(52.0, 35.0, 10000)),
            ]

            for i, (cmd_name, cmd_func) in enumerate(commands, 1):
                print(f"\n[{i}/{len(commands)}] {cmd_name}")

                cmd_start = time.time()
                success = False
                error_msg = None

                try:
                    await cmd_func()
                    success = True
                    print(f"✅ 성공")
                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ 실패: {e}")

                execution_time = time.time() - cmd_start

                # 설정된 대기시간 적용
                if wait_time > 0:
                    print(f"⏳ {wait_time}s 대기...")
                    await asyncio.sleep(wait_time)

                total_time = time.time() - cmd_start

                result = {
                    "command": cmd_name,
                    "success": success,
                    "execution_time": execution_time,
                    "wait_time": wait_time,
                    "total_time": total_time,
                    "error": error_msg,
                }

                self.test_results["original"].append(result)
                print(
                    f"⏱️ 소요시간: 실행 {execution_time*1000:.1f}ms + 대기 {wait_time:.1f}s = 총 {total_time:.3f}s"
                )

        except Exception as e:
            print(f"❌ 연결 오류: {e}")
            return {"success": False, "error": str(e)}
        finally:
            try:
                await mcu.disconnect()
            except:
                pass

        session_time = time.time() - session_start
        success_count = len([r for r in self.test_results["original"] if r.get("success", False)])

        print(f"\n📊 기존 MCU 결과:")
        print(f"   전체 시간: {session_time:.3f}s")
        print(
            f"   성공률: {success_count}/{len(commands)} ({success_count/len(commands)*100:.1f}%)"
        )

        return {
            "success": success_count == len(commands),
            "session_time": session_time,
            "success_rate": success_count / len(commands),
        }

    async def test_fast_mcu(self) -> Dict[str, Any]:
        """Fast LMAMCU 테스트"""
        print(f"\n⚡ Fast LMAMCU 테스트")
        print("=" * 50)

        mcu = FastLMAMCU()
        session_start = time.time()

        try:
            # 연결
            await mcu.connect(port=self.port, baudrate=self.baudrate, timeout=5.0)

            # 테스트 시퀀스 (기존과 동일)
            commands = [
                ("set_test_mode", lambda: mcu.set_test_mode(TestMode.MODE_1)),
                ("set_upper_temperature", lambda: mcu.set_upper_temperature(52.0)),
                ("set_fan_speed", lambda: mcu.set_fan_speed(10)),
                ("start_standby_heating", lambda: mcu.start_standby_heating(52.0, 35.0, 10000)),
            ]

            for i, (cmd_name, cmd_func) in enumerate(commands, 1):
                print(f"\n[{i}/{len(commands)}] {cmd_name}")

                cmd_start = time.time()
                success = False
                error_msg = None

                try:
                    await cmd_func()
                    success = True
                    print(f"✅ 성공")
                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ 실패: {e}")

                total_time = time.time() - cmd_start

                result = {
                    "command": cmd_name,
                    "success": success,
                    "execution_time": total_time,  # Fast는 대기시간 없음
                    "wait_time": 0.0,
                    "total_time": total_time,
                    "error": error_msg,
                }

                self.test_results["fast"].append(result)
                print(f"⏱️ 소요시간: {total_time*1000:.1f}ms")

        except Exception as e:
            print(f"❌ 연결 오류: {e}")
            return {"success": False, "error": str(e)}
        finally:
            try:
                await mcu.disconnect()
            except:
                pass

        session_time = time.time() - session_start
        success_count = len([r for r in self.test_results["fast"] if r.get("success", False)])

        print(f"\n📊 Fast MCU 결과:")
        print(f"   전체 시간: {session_time:.3f}s")
        print(
            f"   성공률: {success_count}/{len(commands)} ({success_count/len(commands)*100:.1f}%)"
        )

        return {
            "success": success_count == len(commands),
            "session_time": session_time,
            "success_rate": success_count / len(commands),
        }

    def analyze_performance_differences(self) -> Dict[str, Any]:
        """성능 차이 분석"""
        print("\n📊 성능 차이 분석")
        print("=" * 60)

        analysis = {"command_comparison": {}, "overall_comparison": {}, "recommendations": []}

        # 명령별 비교
        original_by_cmd = {r["command"]: r for r in self.test_results["original"]}
        fast_by_cmd = {r["command"]: r for r in self.test_results["fast"]}

        print(f"\n🔍 명령별 성능 비교:")
        for cmd in original_by_cmd.keys():
            if cmd in fast_by_cmd:
                orig = original_by_cmd[cmd]
                fast = fast_by_cmd[cmd]

                if orig["success"] and fast["success"]:
                    orig_time = orig["total_time"] * 1000  # ms로 변환
                    fast_time = fast["total_time"] * 1000
                    improvement = orig_time - fast_time
                    improvement_pct = (improvement / orig_time) * 100 if orig_time > 0 else 0

                    print(f"   {cmd}:")
                    print(f"     기존: {orig_time:.1f}ms, Fast: {fast_time:.1f}ms")
                    print(f"     개선: {improvement:+.1f}ms ({improvement_pct:+.1f}%)")

                    analysis["command_comparison"][cmd] = {
                        "original_time_ms": orig_time,
                        "fast_time_ms": fast_time,
                        "improvement_ms": improvement,
                        "improvement_percentage": improvement_pct,
                    }
                else:
                    print(f"   {cmd}: 비교 불가 (실패)")

        # 전체 성능 비교
        orig_total = sum([r["total_time"] for r in self.test_results["original"] if r["success"]])
        fast_total = sum([r["total_time"] for r in self.test_results["fast"] if r["success"]])

        if orig_total > 0 and fast_total > 0:
            total_improvement = orig_total - fast_total
            total_improvement_pct = (total_improvement / orig_total) * 100

            print(f"\n🎯 전체 성능 비교:")
            print(f"   기존 총 시간: {orig_total:.3f}s")
            print(f"   Fast 총 시간: {fast_total:.3f}s")
            print(f"   시간 단축: {total_improvement:+.3f}s ({total_improvement_pct:+.1f}%)")

            analysis["overall_comparison"] = {
                "original_total_time": orig_total,
                "fast_total_time": fast_total,
                "time_savings": total_improvement,
                "improvement_percentage": total_improvement_pct,
            }

        # 안정성 비교
        orig_success_rate = len([r for r in self.test_results["original"] if r["success"]]) / max(
            1, len(self.test_results["original"])
        )
        fast_success_rate = len([r for r in self.test_results["fast"] if r["success"]]) / max(
            1, len(self.test_results["fast"])
        )

        print(f"\n🛡️ 안정성 비교:")
        print(f"   기존 성공률: {orig_success_rate*100:.1f}%")
        print(f"   Fast 성공률: {fast_success_rate*100:.1f}%")

        # 권장사항 생성
        if fast_success_rate >= orig_success_rate and fast_total < orig_total:
            analysis["recommendations"].append("✅ Fast 구현 사용 권장 - 성능 향상 + 안정성 유지")
        elif fast_success_rate < orig_success_rate:
            analysis["recommendations"].append("⚠️ Fast 구현 안정성 개선 필요")
        else:
            analysis["recommendations"].append("🔧 Fast 구현 추가 최적화 가능")

        return analysis

    def save_comparison_results(self):
        """비교 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results/mcu_implementation_comparison_{timestamp}.json"

        results_data = {
            "test_info": {
                "test_type": "MCU Implementation Comparison",
                "port": self.port,
                "baudrate": self.baudrate,
                "timestamp": datetime.now().isoformat(),
            },
            "test_results": self.test_results,
            "analysis": self.analyze_performance_differences(),
        }

        try:
            os.makedirs("test_results", exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            print(f"\n📋 비교 결과 저장: {filename}")
        except Exception as e:
            print(f"❌ 결과 저장 실패: {e}")


async def main():
    """메인 실행"""
    print("⚖️ MCU 구현 비교 테스트")
    print("=" * 40)

    comparator = MCUImplementationComparator(port="COM4", baudrate=115200)

    try:
        print("\n테스트 순서:")
        print("1. 기존 LMAMCU (mcu_command_stabilization = 0.1s)")
        print("2. Fast LMAMCU (대기시간 없음)")
        print("3. 성능 비교 분석")

        input("\nEnter를 눌러 시작하세요...")

        # 1. 기존 MCU 테스트 (0.1초 대기)
        orig_result = await comparator.test_original_mcu(wait_time=0.1)

        # 잠시 대기 (MCU 안정화)
        print("\n⏳ MCU 안정화 대기 (2초)...")
        await asyncio.sleep(2.0)

        # 2. Fast MCU 테스트
        fast_result = await comparator.test_fast_mcu()

        # 3. 성능 분석
        analysis = comparator.analyze_performance_differences()

        # 결과 저장
        comparator.save_comparison_results()

        # 최종 결론
        print(f"\n🎉 비교 테스트 완료!")

        if analysis.get("overall_comparison"):
            improvement = analysis["overall_comparison"].get("improvement_percentage", 0)
            if improvement > 0:
                print(f"🚀 Fast 구현이 {improvement:.1f}% 더 빠름!")
            else:
                print(f"⚠️ Fast 구현 성능 개선 필요")

        print("\n💡 다음 단계:")
        for rec in analysis.get("recommendations", []):
            print(f"   {rec}")

    except KeyboardInterrupt:
        print("\n⏹️ 사용자 중단")
    except Exception as e:
        print(f"\n❌ 테스트 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())
