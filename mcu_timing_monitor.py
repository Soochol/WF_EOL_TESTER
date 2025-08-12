#!/usr/bin/env python3
"""
MCU 타이밍 모니터링 도구

실시간으로 MCU 명령 실행 시간과 상태 변화를 모니터링하여
3초 대기시간의 필요성을 검증합니다.
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from loguru import logger

@dataclass
class MCUCommandTiming:
    """MCU 명령 타이밍 정보"""
    command_name: str
    start_time: float
    send_time: Optional[float] = None
    response_time: Optional[float] = None
    completion_time: Optional[float] = None
    wait_time: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    packet_sent: Optional[str] = None
    packet_received: Optional[str] = None
    mcu_status_before: Optional[str] = None
    mcu_status_after: Optional[str] = None

class MCUTimingMonitor:
    """MCU 타이밍 모니터링 클래스"""
    
    def __init__(self):
        self.command_timings: List[MCUCommandTiming] = []
        self.session_start_time = time.time()
        self.monitoring_active = False
        
    def start_monitoring(self):
        """모니터링 시작"""
        self.monitoring_active = True
        self.session_start_time = time.time()
        logger.info("🔍 MCU 타이밍 모니터링 시작")
        
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        logger.info("⏹️ MCU 타이밍 모니터링 중지")
        
    def create_command_timing(self, command_name: str) -> MCUCommandTiming:
        """새로운 명령 타이밍 생성"""
        timing = MCUCommandTiming(
            command_name=command_name,
            start_time=time.time()
        )
        self.command_timings.append(timing)
        return timing
        
    def update_timing(self, timing: MCUCommandTiming, **kwargs):
        """타이밍 정보 업데이트"""
        for key, value in kwargs.items():
            if hasattr(timing, key):
                setattr(timing, key, value)
                
    def log_command_start(self, command_name: str, parameters: Dict[str, Any] = None) -> MCUCommandTiming:
        """명령 시작 로그"""
        if not self.monitoring_active:
            return None
            
        timing = self.create_command_timing(command_name)
        
        params_str = ""
        if parameters:
            params_str = f" with {parameters}"
            
        logger.info(f"🚀 MCU COMMAND START: {command_name}{params_str}")
        logger.info(f"   Session time: {timing.start_time - self.session_start_time:.3f}s")
        
        return timing
        
    def log_packet_sent(self, timing: MCUCommandTiming, packet_hex: str):
        """패킷 전송 로그"""
        if not timing:
            return
            
        timing.send_time = time.time()
        timing.packet_sent = packet_hex
        
        send_duration = timing.send_time - timing.start_time
        logger.info(f"📤 PACKET SENT: {packet_hex}")
        logger.info(f"   Send delay: {send_duration*1000:.1f}ms")
        
    def log_packet_received(self, timing: MCUCommandTiming, packet_hex: str, status_message: str):
        """패킷 수신 로그"""
        if not timing:
            return
            
        timing.response_time = time.time()
        timing.packet_received = packet_hex
        
        if timing.send_time:
            response_duration = timing.response_time - timing.send_time
            logger.info(f"📥 PACKET RECEIVED: {packet_hex} ({status_message})")
            logger.info(f"   Response time: {response_duration*1000:.1f}ms")
        
    def log_mcu_status_change(self, timing: MCUCommandTiming, before_status: str, after_status: str):
        """MCU 상태 변화 로그"""
        if not timing:
            return
            
        timing.mcu_status_before = before_status
        timing.mcu_status_after = after_status
        
        logger.info(f"🔄 MCU STATUS CHANGE: {before_status} → {after_status}")
        
    def log_wait_start(self, timing: MCUCommandTiming, wait_time: float, reason: str):
        """대기 시작 로그"""
        if not timing:
            return
            
        timing.wait_time = wait_time
        
        logger.info(f"⏳ WAIT START: {wait_time}s ({reason})")
        
    def log_command_completion(self, timing: MCUCommandTiming, success: bool, error_message: str = None):
        """명령 완료 로그"""
        if not timing:
            return
            
        timing.completion_time = time.time()
        timing.success = success
        timing.error_message = error_message
        
        total_duration = timing.completion_time - timing.start_time
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{status}: {timing.command_name}")
        logger.info(f"   Total duration: {total_duration:.3f}s")
        
        if timing.send_time:
            send_delay = timing.send_time - timing.start_time
            logger.info(f"   Send delay: {send_delay*1000:.1f}ms")
            
        if timing.response_time and timing.send_time:
            response_time = timing.response_time - timing.send_time
            logger.info(f"   Response time: {response_time*1000:.1f}ms")
            
        if timing.wait_time > 0:
            logger.info(f"   Wait time: {timing.wait_time:.3f}s")
            
        if error_message:
            logger.info(f"   Error: {error_message}")
            
    def analyze_timing_patterns(self) -> Dict[str, Any]:
        """타이밍 패턴 분석"""
        if not self.command_timings:
            return {"error": "No timing data available"}
            
        analysis = {
            "total_commands": len(self.command_timings),
            "successful_commands": sum(1 for t in self.command_timings if t.success),
            "failed_commands": sum(1 for t in self.command_timings if not t.success),
            "command_analysis": {},
            "timing_summary": {}
        }
        
        # 명령별 분석
        command_groups = {}
        for timing in self.command_timings:
            if timing.command_name not in command_groups:
                command_groups[timing.command_name] = []
            command_groups[timing.command_name].append(timing)
            
        for command_name, timings in command_groups.items():
            successful_timings = [t for t in timings if t.success and t.completion_time]
            
            if successful_timings:
                durations = [t.completion_time - t.start_time for t in successful_timings]
                response_times = [
                    t.response_time - t.send_time 
                    for t in successful_timings 
                    if t.response_time and t.send_time
                ]
                
                analysis["command_analysis"][command_name] = {
                    "count": len(timings),
                    "success_rate": len(successful_timings) / len(timings),
                    "avg_duration": sum(durations) / len(durations) if durations else 0,
                    "min_duration": min(durations) if durations else 0,
                    "max_duration": max(durations) if durations else 0,
                    "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                    "total_wait_time": sum(t.wait_time for t in timings),
                    "unnecessary_wait_potential": 0  # 계산 필요
                }
                
                # 불필요한 대기시간 추정
                if response_times:
                    avg_response = sum(response_times) / len(response_times)
                    total_wait = sum(t.wait_time for t in timings)
                    # 응답 시간이 대기 시간보다 훨씬 짧으면 불필요한 대기로 추정
                    if total_wait > avg_response * 10:  # 10배 이상 차이
                        analysis["command_analysis"][command_name]["unnecessary_wait_potential"] = total_wait - avg_response
        
        # 전체 타이밍 요약
        all_successful = [t for t in self.command_timings if t.success and t.completion_time]
        if all_successful:
            total_session_time = max(t.completion_time for t in all_successful) - self.session_start_time
            total_wait_time = sum(t.wait_time for t in self.command_timings)
            
            analysis["timing_summary"] = {
                "total_session_time": total_session_time,
                "total_wait_time": total_wait_time,
                "wait_percentage": (total_wait_time / total_session_time) * 100 if total_session_time > 0 else 0,
                "potential_time_savings": total_wait_time * 0.8  # 80% 대기시간 단축 가능 추정
            }
            
        return analysis
        
    def export_timing_data(self, filename: str = None):
        """타이밍 데이터 내보내기"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mcu_timing_data_{timestamp}.json"
            
        data = {
            "session_info": {
                "start_time": self.session_start_time,
                "total_commands": len(self.command_timings),
                "monitoring_duration": time.time() - self.session_start_time
            },
            "command_timings": [asdict(timing) for timing in self.command_timings],
            "analysis": self.analyze_timing_patterns()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"📊 타이밍 데이터 저장됨: {filename}")
        return filename
        
    def print_timing_summary(self):
        """타이밍 요약 출력"""
        analysis = self.analyze_timing_patterns()
        
        print("\n" + "="*80)
        print("MCU 타이밍 모니터링 결과")
        print("="*80)
        
        print(f"\n📊 전체 통계")
        print(f"   총 명령 수: {analysis.get('total_commands', 0)}")
        print(f"   성공: {analysis.get('successful_commands', 0)}")
        print(f"   실패: {analysis.get('failed_commands', 0)}")
        
        if "timing_summary" in analysis:
            summary = analysis["timing_summary"]
            print(f"\n⏱️ 시간 분석")
            print(f"   전체 세션 시간: {summary.get('total_session_time', 0):.3f}s")
            print(f"   총 대기 시간: {summary.get('total_wait_time', 0):.3f}s")
            print(f"   대기 시간 비율: {summary.get('wait_percentage', 0):.1f}%")
            print(f"   예상 단축 가능: {summary.get('potential_time_savings', 0):.3f}s")
        
        if "command_analysis" in analysis:
            print(f"\n🔍 명령별 분석")
            for command, data in analysis["command_analysis"].items():
                print(f"   {command}:")
                print(f"     성공률: {data.get('success_rate', 0)*100:.1f}%")
                print(f"     평균 소요시간: {data.get('avg_duration', 0)*1000:.1f}ms")
                print(f"     평균 응답시간: {data.get('avg_response_time', 0)*1000:.1f}ms")
                print(f"     총 대기시간: {data.get('total_wait_time', 0):.3f}s")
                if data.get('unnecessary_wait_potential', 0) > 0:
                    print(f"     불필요 대기 추정: {data['unnecessary_wait_potential']:.3f}s")
        
        print("="*80)

# 전역 모니터 인스턴스
timing_monitor = MCUTimingMonitor()

def create_monitored_mcu_wrapper(original_mcu):
    """MCU 객체를 모니터링 기능으로 래핑"""
    
    class MonitoredMCU:
        def __init__(self, mcu):
            self._mcu = mcu
            
        async def set_upper_temperature(self, upper_temp: float):
            timing = timing_monitor.log_command_start("set_upper_temperature", {"upper_temp": upper_temp})
            try:
                result = await self._mcu.set_upper_temperature(upper_temp)
                timing_monitor.log_command_completion(timing, True)
                return result
            except Exception as e:
                timing_monitor.log_command_completion(timing, False, str(e))
                raise
                
        async def set_fan_speed(self, fan_level: int):
            timing = timing_monitor.log_command_start("set_fan_speed", {"fan_level": fan_level})
            try:
                result = await self._mcu.set_fan_speed(fan_level)
                timing_monitor.log_command_completion(timing, True)
                return result
            except Exception as e:
                timing_monitor.log_command_completion(timing, False, str(e))
                raise
                
        async def start_standby_heating(self, operating_temp: float, standby_temp: float, hold_time_ms: int = 10000):
            timing = timing_monitor.log_command_start("start_standby_heating", {
                "operating_temp": operating_temp,
                "standby_temp": standby_temp, 
                "hold_time_ms": hold_time_ms
            })
            try:
                result = await self._mcu.start_standby_heating(operating_temp, standby_temp, hold_time_ms)
                timing_monitor.log_command_completion(timing, True)
                return result
            except Exception as e:
                timing_monitor.log_command_completion(timing, False, str(e))
                raise
        
        # 다른 메서드들도 원본으로 전달
        def __getattr__(self, name):
            return getattr(self._mcu, name)
    
    return MonitoredMCU(original_mcu)

def main():
    """타이밍 모니터 테스트"""
    timing_monitor.start_monitoring()
    
    # 시뮬레이션 데이터로 테스트
    import random
    
    for i in range(3):
        # set_upper_temperature 시뮬레이션
        timing = timing_monitor.log_command_start("set_upper_temperature", {"upper_temp": 80.0})
        timing_monitor.log_packet_sent(timing, "FFFF 05 04 00000320 FEFE")
        time.sleep(random.uniform(0.01, 0.05))  # 응답 시간 시뮬레이션
        timing_monitor.log_packet_received(timing, "FFFF 0A 00 FEFE", "STATUS_UPPER_TEMP_OK")
        timing_monitor.log_wait_start(timing, 3.0, "mcu_command_stabilization")
        time.sleep(0.1)  # 실제로는 3초지만 테스트용으로 단축
        timing_monitor.log_command_completion(timing, True)
        
        # set_fan_speed 시뮬레이션  
        timing = timing_monitor.log_command_start("set_fan_speed", {"fan_level": 10})
        timing_monitor.log_packet_sent(timing, "FFFF 06 04 0000000A FEFE")
        time.sleep(random.uniform(0.01, 0.05))
        timing_monitor.log_packet_received(timing, "FFFF 0B 00 FEFE", "STATUS_FAN_SPEED_OK")
        timing_monitor.log_wait_start(timing, 3.0, "mcu_command_stabilization")
        time.sleep(0.1)
        timing_monitor.log_command_completion(timing, True)
        
        # start_standby_heating 시뮬레이션
        timing = timing_monitor.log_command_start("start_standby_heating", {
            "operating_temp": 70.0, "standby_temp": 50.0, "hold_time_ms": 10000
        })
        timing_monitor.log_packet_sent(timing, "FFFF 02 0C 000002BC000001F400002710 FEFE")
        time.sleep(random.uniform(0.02, 0.08))
        timing_monitor.log_packet_received(timing, "FFFF 08 00 FEFE", "STATUS_LMA_INIT_OK")
        time.sleep(random.uniform(0.5, 2.0))  # 온도 도달 시간
        timing_monitor.log_packet_received(timing, "FFFF 0C 00 FEFE", "STATUS_OPERATING_TEMP_REACHED")
        timing_monitor.log_wait_start(timing, 3.0, "mcu_command_stabilization")
        time.sleep(0.1)
        timing_monitor.log_command_completion(timing, True)
    
    timing_monitor.stop_monitoring()
    timing_monitor.print_timing_summary()
    timing_monitor.export_timing_data()

if __name__ == "__main__":
    main()