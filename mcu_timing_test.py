#!/usr/bin/env python3
"""
MCU 타이밍 최적화 테스트

다양한 대기시간 설정으로 MCU 명령 시퀀스를 테스트하여
최적의 타이밍을 찾습니다.
"""

import asyncio
import time
import json
from pathlib import Path
import sys
from typing import Dict, List, Optional, Any
from loguru import logger

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 필요한 모듈들 임포트 (실제 프로젝트 구조에 맞게 조정)
try:
    from src.domain.value_objects.test_configuration import TestConfiguration
    from src.infrastructure.factory import ServiceFactory
    from mcu_timing_monitor import timing_monitor, create_monitored_mcu_wrapper
except ImportError as e:
    logger.warning(f"Import warning: {e}")
    logger.info("Mock 모드로 실행됩니다.")

class MCUTimingTest:
    """MCU 타이밍 테스트 클래스"""
    
    def __init__(self):
        self.test_results: List[Dict] = []
        self.mcu = None
        self.mock_mode = False
        
    async def setup_mcu(self, config: Dict[str, Any] = None):
        """MCU 설정 및 연결"""
        try:
            if config is None:
                config = {
                    "model": "lma",
                    "port": "COM4", 
                    "baudrate": 115200,
                    "timeout": 10.0,
                    "bytesize": 8,
                    "stopbits": 1,
                    "parity": None
                }
            
            # MCU 서비스 생성
            self.mcu = ServiceFactory.create_mcu_service(config)
            
            # 모니터링 래퍼로 감싸기
            self.mcu = create_monitored_mcu_wrapper(self.mcu)
            
            # 연결
            await self.mcu.connect(
                port=config["port"],
                baudrate=config["baudrate"], 
                timeout=config["timeout"],
                bytesize=config["bytesize"],
                stopbits=config["stopbits"],
                parity=config["parity"]
            )
            
            logger.info("✅ MCU 연결 성공")
            return True
            
        except Exception as e:
            logger.warning(f"MCU 연결 실패: {e}")
            logger.info("Mock 모드로 전환")
            self.mock_mode = True
            return False
    
    async def test_command_sequence_with_timing(
        self, 
        upper_temp_wait: float = 3.0,
        fan_speed_wait: float = 3.0, 
        standby_heating_wait: float = 3.0,
        upper_temp: float = 80.0,
        fan_speed: int = 10,
        operating_temp: float = 70.0,
        standby_temp: float = 50.0
    ) -> Dict[str, Any]:
        """지정된 타이밍으로 MCU 명령 시퀀스 테스트"""
        
        test_start_time = time.time()
        test_result = {
            "test_config": {
                "upper_temp_wait": upper_temp_wait,
                "fan_speed_wait": fan_speed_wait,
                "standby_heating_wait": standby_heating_wait,
                "upper_temp": upper_temp,
                "fan_speed": fan_speed,
                "operating_temp": operating_temp,
                "standby_temp": standby_temp
            },
            "results": {},
            "success": True,
            "error_message": None,
            "total_time": 0.0
        }
        
        logger.info(f"🧪 타이밍 테스트 시작: upper({upper_temp_wait}s), fan({fan_speed_wait}s), heating({standby_heating_wait}s)")
        
        try:
            # 1. Upper Temperature 설정
            step_start = time.time()
            if self.mock_mode:
                await self._mock_set_upper_temperature(upper_temp)
            else:
                await self.mcu.set_upper_temperature(upper_temp)
            
            if upper_temp_wait > 0:
                logger.info(f"⏳ upper_temperature 대기: {upper_temp_wait}s")
                await asyncio.sleep(upper_temp_wait)
            
            test_result["results"]["upper_temperature"] = {
                "duration": time.time() - step_start,
                "success": True
            }
            
            # 2. Fan Speed 설정
            step_start = time.time()
            if self.mock_mode:
                await self._mock_set_fan_speed(fan_speed)
            else:
                await self.mcu.set_fan_speed(fan_speed)
                
            if fan_speed_wait > 0:
                logger.info(f"⏳ fan_speed 대기: {fan_speed_wait}s")
                await asyncio.sleep(fan_speed_wait)
            
            test_result["results"]["fan_speed"] = {
                "duration": time.time() - step_start,
                "success": True
            }
            
            # 3. Standby Heating 시작
            step_start = time.time()
            if self.mock_mode:
                await self._mock_start_standby_heating(operating_temp, standby_temp)
            else:
                await self.mcu.start_standby_heating(operating_temp, standby_temp)
                
            if standby_heating_wait > 0:
                logger.info(f"⏳ standby_heating 대기: {standby_heating_wait}s")
                await asyncio.sleep(standby_heating_wait)
            
            test_result["results"]["standby_heating"] = {
                "duration": time.time() - step_start,
                "success": True
            }
            
            # 4. 온도 확인 (실제 동작 검증)
            if not self.mock_mode:
                current_temp = await self.mcu.get_temperature()
                test_result["results"]["temperature_check"] = {
                    "current_temperature": current_temp,
                    "target_reached": current_temp > standby_temp
                }
                
                if current_temp <= standby_temp:
                    test_result["success"] = False
                    test_result["error_message"] = f"온도 상승 실패: {current_temp}°C <= {standby_temp}°C"
            
        except Exception as e:
            test_result["success"] = False
            test_result["error_message"] = str(e)
            logger.error(f"❌ 테스트 실패: {e}")
        
        test_result["total_time"] = time.time() - test_start_time
        
        if test_result["success"]:
            logger.info(f"✅ 테스트 성공: {test_result['total_time']:.3f}s")
        else:
            logger.error(f"❌ 테스트 실패: {test_result['error_message']}")
        
        return test_result
    
    async def _mock_set_upper_temperature(self, upper_temp: float):
        """Mock upper temperature 설정"""
        timing = timing_monitor.log_command_start("set_upper_temperature", {"upper_temp": upper_temp})
        timing_monitor.log_packet_sent(timing, f"FFFF 05 04 {int(upper_temp*10):08X} FEFE")
        await asyncio.sleep(0.02)  # 응답 시간 시뮬레이션
        timing_monitor.log_packet_received(timing, "FFFF 0A 00 FEFE", "STATUS_UPPER_TEMP_OK")
        timing_monitor.log_command_completion(timing, True)
    
    async def _mock_set_fan_speed(self, fan_speed: int):
        """Mock fan speed 설정"""
        timing = timing_monitor.log_command_start("set_fan_speed", {"fan_level": fan_speed})
        timing_monitor.log_packet_sent(timing, f"FFFF 06 04 {fan_speed:08X} FEFE")
        await asyncio.sleep(0.02)
        timing_monitor.log_packet_received(timing, "FFFF 0B 00 FEFE", "STATUS_FAN_SPEED_OK")
        timing_monitor.log_command_completion(timing, True)
    
    async def _mock_start_standby_heating(self, operating_temp: float, standby_temp: float):
        """Mock standby heating 시작"""
        timing = timing_monitor.log_command_start("start_standby_heating", {
            "operating_temp": operating_temp,
            "standby_temp": standby_temp
        })
        
        # 패킷 전송
        op_temp_int = int(operating_temp * 10)
        standby_temp_int = int(standby_temp * 10)
        packet_data = f"{op_temp_int:08X}{standby_temp_int:08X}00002710"  # 10초 홀드
        timing_monitor.log_packet_sent(timing, f"FFFF 02 0C {packet_data} FEFE")
        
        await asyncio.sleep(0.03)
        timing_monitor.log_packet_received(timing, "FFFF 08 00 FEFE", "STATUS_LMA_INIT_OK")
        
        # 온도 도달 시뮬레이션
        await asyncio.sleep(0.5)  # 온도 도달 시간
        timing_monitor.log_packet_received(timing, "FFFF 0C 00 FEFE", "STATUS_OPERATING_TEMP_REACHED")
        
        timing_monitor.log_command_completion(timing, True)
    
    async def run_timing_tests(self) -> List[Dict[str, Any]]:
        """다양한 타이밍으로 테스트 실행"""
        
        test_scenarios = [
            {
                "name": "현재 설정 (3초 대기)",
                "upper_temp_wait": 3.0,
                "fan_speed_wait": 3.0,
                "standby_heating_wait": 3.0
            },
            {
                "name": "중간 설정 (1초 대기)",
                "upper_temp_wait": 1.0,
                "fan_speed_wait": 1.0,
                "standby_heating_wait": 1.0
            },
            {
                "name": "짧은 설정 (0.5초 대기)",
                "upper_temp_wait": 0.5,
                "fan_speed_wait": 0.5,
                "standby_heating_wait": 0.5
            },
            {
                "name": "최소 설정 (0.1초 대기)",
                "upper_temp_wait": 0.1,
                "fan_speed_wait": 0.1,
                "standby_heating_wait": 0.1
            },
            {
                "name": "응답만 대기 (0초)",
                "upper_temp_wait": 0.0,
                "fan_speed_wait": 0.0,
                "standby_heating_wait": 0.0
            },
            {
                "name": "선택적 대기 (heating만 대기)",
                "upper_temp_wait": 0.0,
                "fan_speed_wait": 0.0,
                "standby_heating_wait": 3.0
            }
        ]
        
        timing_monitor.start_monitoring()
        
        for scenario in test_scenarios:
            logger.info(f"\n{'='*60}")
            logger.info(f"테스트 시나리오: {scenario['name']}")
            logger.info(f"{'='*60}")
            
            result = await self.test_command_sequence_with_timing(
                upper_temp_wait=scenario["upper_temp_wait"],
                fan_speed_wait=scenario["fan_speed_wait"],
                standby_heating_wait=scenario["standby_heating_wait"]
            )
            
            result["scenario_name"] = scenario["name"]
            self.test_results.append(result)
            
            # 테스트 간 간격
            await asyncio.sleep(1.0)
        
        timing_monitor.stop_monitoring()
        return self.test_results
    
    def analyze_test_results(self) -> Dict[str, Any]:
        """테스트 결과 분석"""
        if not self.test_results:
            return {"error": "No test results available"}
        
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        analysis = {
            "summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": len(successful_tests) / len(self.test_results) if self.test_results else 0
            },
            "timing_comparison": {},
            "recommendations": []
        }
        
        if successful_tests:
            # 타이밍 비교
            baseline = None
            fastest = None
            
            for result in successful_tests:
                scenario_name = result["scenario_name"]
                total_time = result["total_time"]
                
                config = result["test_config"]
                total_wait_time = config["upper_temp_wait"] + config["fan_speed_wait"] + config["standby_heating_wait"]
                
                analysis["timing_comparison"][scenario_name] = {
                    "total_time": total_time,
                    "total_wait_time": total_wait_time,
                    "actual_execution_time": total_time - total_wait_time,
                    "wait_time_percentage": (total_wait_time / total_time) * 100 if total_time > 0 else 0
                }
                
                if "현재 설정" in scenario_name:
                    baseline = analysis["timing_comparison"][scenario_name]
                
                if fastest is None or total_time < fastest["total_time"]:
                    fastest = analysis["timing_comparison"][scenario_name]
                    fastest["scenario"] = scenario_name
            
            # 권장사항 생성
            if baseline and fastest:
                time_savings = baseline["total_time"] - fastest["total_time"]
                if time_savings > 0:
                    analysis["recommendations"].append(
                        f"최적 시나리오 '{fastest['scenario']}'로 {time_savings:.3f}초 단축 가능"
                    )
                
                # 실패한 테스트가 있으면 안전한 범위 제안
                if failed_tests:
                    safe_scenarios = [r for r in successful_tests if r["total_time"] < baseline["total_time"]]
                    if safe_scenarios:
                        safest = min(safe_scenarios, key=lambda x: x["test_config"]["upper_temp_wait"])
                        analysis["recommendations"].append(
                            f"안전한 최적화: '{safest['scenario_name']}' 권장"
                        )
        
        # 실패 분석
        if failed_tests:
            common_failures = {}
            for failed in failed_tests:
                error = failed.get("error_message", "Unknown error")
                if error not in common_failures:
                    common_failures[error] = []
                common_failures[error].append(failed["scenario_name"])
            
            analysis["failure_analysis"] = common_failures
            
            for error, scenarios in common_failures.items():
                analysis["recommendations"].append(
                    f"주의: '{', '.join(scenarios)}'에서 '{error}' 발생"
                )
        
        return analysis
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        analysis = self.analyze_test_results()
        
        print("\n" + "="*80)
        print("MCU 타이밍 최적화 테스트 결과")
        print("="*80)
        
        print(f"\n📊 테스트 요약")
        summary = analysis.get("summary", {})
        print(f"   총 테스트: {summary.get('total_tests', 0)}")
        print(f"   성공: {summary.get('successful_tests', 0)}")
        print(f"   실패: {summary.get('failed_tests', 0)}")
        print(f"   성공률: {summary.get('success_rate', 0)*100:.1f}%")
        
        if "timing_comparison" in analysis:
            print(f"\n⏱️ 타이밍 비교")
            for scenario, data in analysis["timing_comparison"].items():
                print(f"   {scenario}:")
                print(f"     총 시간: {data['total_time']:.3f}s")
                print(f"     대기 시간: {data['total_wait_time']:.3f}s ({data['wait_time_percentage']:.1f}%)")
                print(f"     실제 실행: {data['actual_execution_time']:.3f}s")
        
        if "failure_analysis" in analysis:
            print(f"\n❌ 실패 분석")
            for error, scenarios in analysis["failure_analysis"].items():
                print(f"   {error}: {', '.join(scenarios)}")
        
        if "recommendations" in analysis and analysis["recommendations"]:
            print(f"\n💡 권장사항")
            for i, recommendation in enumerate(analysis["recommendations"], 1):
                print(f"   {i}. {recommendation}")
        
        print("="*80)
    
    def export_results(self, filename: str = None):
        """결과 내보내기"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"mcu_timing_test_results_{timestamp}.json"
        
        data = {
            "test_results": self.test_results,
            "analysis": self.analyze_test_results(),
            "timing_monitor_data": timing_monitor.analyze_timing_patterns()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 테스트 결과 저장: {filename}")
        return filename

async def main():
    """메인 테스트 실행"""
    tester = MCUTimingTest()
    
    # MCU 연결 시도
    await tester.setup_mcu()
    
    # 타이밍 테스트 실행
    await tester.run_timing_tests()
    
    # 결과 분석 및 출력
    tester.print_test_summary()
    timing_monitor.print_timing_summary()
    
    # 결과 저장
    tester.export_results()
    timing_monitor.export_timing_data()

if __name__ == "__main__":
    asyncio.run(main())