#!/usr/bin/env python3
"""
현재 프로젝트 코드 테스트

기존 LMAMCU 클래스를 사용하여 동일한 시퀀스를 테스트하고
3초 대기의 필요성을 확인합니다.
"""

import asyncio
import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, List

# 프로젝트 루트를 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from src.infrastructure.implementation.hardware.mcu.lma.lma_mcu import LMAMCU
    from src.domain.enums.mcu_enums import TestMode
except ImportError as e:
    print(f"❌ 프로젝트 모듈 임포트 실패: {e}")
    print("프로젝트 루트 디렉토리에서 실행하세요.")
    sys.exit(1)

class CurrentCodeTester:
    """현재 코드 테스터"""
    
    def __init__(self, port: str = "COM4", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.mcu: Optional[LMAMCU] = None
        self.test_results: List[Dict] = []
        
    async def setup_mcu(self) -> bool:
        """MCU 설정 및 연결"""
        try:
            self.mcu = LMAMCU()
            
            await self.mcu.connect(
                port=self.port,
                baudrate=self.baudrate,
                timeout=10.0,
                bytesize=8,
                stopbits=1,
                parity=None
            )
            
            print(f"✅ MCU 연결 성공: {self.port} @ {self.baudrate}")
            return True
            
        except Exception as e:
            print(f"❌ MCU 연결 실패: {e}")
            return False
            
    async def cleanup_mcu(self):
        """MCU 정리"""
        if self.mcu:
            try:
                await self.mcu.disconnect()
                print("📴 MCU 연결 해제")
            except Exception as e:
                print(f"⚠️ MCU 해제 오류: {e}")
                
    async def test_command_with_timing(self, command_name: str, command_func, wait_time: float = 0.0) -> Dict:
        """명령 실행 및 타이밍 측정"""
        print(f"\n🔄 {command_name} 실행 (대기시간: {wait_time}초)")
        
        start_time = time.time()
        success = False
        error_message = None
        
        try:
            await command_func()
            success = True
            print(f"✅ {command_name} 성공")
        except Exception as e:
            error_message = str(e)
            print(f"❌ {command_name} 실패: {e}")
            
        execution_time = time.time() - start_time
        
        # 대기시간 적용
        if wait_time > 0:
            print(f"⏳ {wait_time}초 대기 중...")
            await asyncio.sleep(wait_time)
            
        total_time = time.time() - start_time
        
        result = {
            "command": command_name,
            "success": success,
            "execution_time": execution_time,
            "wait_time": wait_time,
            "total_time": total_time,
            "error": error_message
        }
        
        self.test_results.append(result)
        print(f"⏱️ 소요시간: 실행 {execution_time:.3f}s + 대기 {wait_time:.3f}s = 총 {total_time:.3f}s")
        
        return result
        
    async def run_sequence_test_with_delays(self) -> bool:
        """3초 대기를 포함한 시퀀스 테스트"""
        print("\n🚀 현재 코드 테스트 시작 (3초 대기 포함)")
        print("=" * 60)
        
        session_start = time.time()
        all_success = True
        
        try:
            # 1. 테스트 모드 설정 (실제 로그에 있었던 단계)
            result = await self.test_command_with_timing(
                "set_test_mode",
                lambda: self.mcu.set_test_mode(TestMode.MODE_1),
                wait_time=3.0
            )
            if not result["success"]:
                all_success = False
                
            # 2. 상한 온도 설정
            result = await self.test_command_with_timing(
                "set_upper_temperature",
                lambda: self.mcu.set_upper_temperature(52.0),  # 실제 로그 값
                wait_time=3.0
            )
            if not result["success"]:
                all_success = False
                
            # 3. 팬 속도 설정  
            result = await self.test_command_with_timing(
                "set_fan_speed",
                lambda: self.mcu.set_fan_speed(10),
                wait_time=3.0
            )
            if not result["success"]:
                all_success = False
                
            # 4. LMA 초기화 (standby heating)
            result = await self.test_command_with_timing(
                "start_standby_heating",
                lambda: self.mcu.start_standby_heating(
                    operating_temp=52.0,  # 실제 로그 값
                    standby_temp=35.0,    # 실제 로그 값
                    hold_time_ms=10000
                ),
                wait_time=3.0
            )
            if not result["success"]:
                all_success = False
                
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            all_success = False
            
        session_time = time.time() - session_start
        print(f"\n⏱️ 전체 테스트 시간: {session_time:.3f}초")
        
        return all_success
        
    async def run_sequence_test_no_delays(self) -> bool:
        """대기시간 없는 시퀀스 테스트"""
        print("\n🚀 현재 코드 테스트 시작 (대기시간 없음)")
        print("=" * 60)
        
        session_start = time.time()
        all_success = True
        
        try:
            # 대기시간 0초로 동일한 시퀀스 실행
            commands = [
                ("set_test_mode", lambda: self.mcu.set_test_mode(TestMode.MODE_1)),
                ("set_upper_temperature", lambda: self.mcu.set_upper_temperature(52.0)),
                ("set_fan_speed", lambda: self.mcu.set_fan_speed(10)),
                ("start_standby_heating", lambda: self.mcu.start_standby_heating(52.0, 35.0, 10000))
            ]
            
            for cmd_name, cmd_func in commands:
                result = await self.test_command_with_timing(cmd_name, cmd_func, wait_time=0.0)
                if not result["success"]:
                    all_success = False
                    
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            all_success = False
            
        session_time = time.time() - session_start
        print(f"\n⏱️ 전체 테스트 시간: {session_time:.3f}초")
        
        return all_success
        
    def save_results(self, test_type: str):
        """테스트 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results/current_code_{test_type}_{timestamp}.json"
        
        results_data = {
            "test_info": {
                "test_type": f"Current Code Test ({test_type})",
                "port": self.port,
                "baudrate": self.baudrate,
                "timestamp": datetime.now().isoformat()
            },
            "results": self.test_results,
            "summary": {
                "total_commands": len(self.test_results),
                "successful_commands": len([r for r in self.test_results if r.get("success", False)]),
                "total_execution_time": sum([r.get("execution_time", 0) for r in self.test_results]),
                "total_wait_time": sum([r.get("wait_time", 0) for r in self.test_results]),
                "total_time": sum([r.get("total_time", 0) for r in self.test_results])
            }
        }
        
        try:
            os.makedirs("test_results", exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            print(f"📊 결과 저장: {filename}")
        except Exception as e:
            print(f"❌ 결과 저장 실패: {e}")

async def main():
    """메인 실행"""
    print("🔧 현재 프로젝트 코드 테스트")
    print("=" * 40)
    
    tester = CurrentCodeTester(port="COM4", baudrate=115200)
    
    try:
        # MCU 연결
        if not await tester.setup_mcu():
            return
            
        # 사용자 선택
        print("\n테스트 모드 선택:")
        print("1. 3초 대기 포함 테스트")
        print("2. 대기시간 없는 테스트")
        print("3. 두 방식 모두 테스트")
        
        try:
            choice = input("선택 (1-3): ").strip()
        except KeyboardInterrupt:
            print("\n⏹️ 사용자 중단")
            return
            
        if choice in ["1", "3"]:
            print("\n" + "="*60)
            print("📋 3초 대기 포함 테스트")
            print("="*60)
            success1 = await tester.run_sequence_test_with_delays()
            tester.save_results("with_delays")
            print(f"🎯 결과: {'성공' if success1 else '실패'}")
            
            # 결과 초기화
            tester.test_results = []
            
        if choice in ["2", "3"]:
            print("\n" + "="*60)
            print("📋 대기시간 없는 테스트")  
            print("="*60)
            success2 = await tester.run_sequence_test_no_delays()
            tester.save_results("no_delays")
            print(f"🎯 결과: {'성공' if success2 else '실패'}")
            
    except KeyboardInterrupt:
        print("\n⏹️ 사용자 중단")
    except Exception as e:
        print(f"\n❌ 테스트 오류: {e}")
    finally:
        await tester.cleanup_mcu()

if __name__ == "__main__":
    asyncio.run(main())