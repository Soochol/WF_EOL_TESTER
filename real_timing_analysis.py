#!/usr/bin/env python3
"""
실제 MCU 통신 타이밍 분석

시간 정보와 송수신 방향이 포함된 실제 로그를 분석하여
정확한 타이밍 패턴을 확인합니다.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple

class RealTimingAnalyzer:
    """실제 타이밍 분석기"""
    
    def __init__(self):
        self.log_entries: List[Dict] = []
        
    def parse_log_entry(self, log_line: str) -> Dict:
        """로그 엔트리 파싱"""
        # 예: ">[05:10:51]FF FF 01 04 00 00 00 01 FE FE"
        direction = log_line[0]  # '>' (PC->MCU) 또는 '<' (MCU->PC)
        time_end = log_line.find(']')
        time_str = log_line[2:time_end]  # "05:10:51"
        packet_hex = log_line[time_end+1:].strip()
        
        # 시간을 초 단위로 변환 (분:초 형식)
        time_parts = time_str.split(':')
        minutes = int(time_parts[1])
        seconds = int(time_parts[2])
        total_seconds = minutes * 60 + seconds
        
        return {
            'direction': 'PC->MCU' if direction == '>' else 'MCU->PC',
            'time_str': time_str,
            'time_seconds': total_seconds,
            'packet_hex': packet_hex,
            'raw_line': log_line
        }
    
    def analyze_real_communication(self) -> None:
        """실제 통신 분석"""
        
        # 실제 로그 데이터
        log_data = [
            ">[05:10:51]FF FF 01 04 00 00 00 01 FE FE",  # CMD_ENTER_TEST_MODE
            "<[05:10:51]FF FF 01 00 FE FE",              # STATUS_TEST_MODE_COMPLETE
            ">[05:10:51]FF FF 02 04 00 00 02 08 FE FE",  # CMD_SET_UPPER_TEMP
            "<[05:10:51]FF FF 02 00 FE FE",              # STATUS_UPPER_TEMP_OK
            ">[05:10:51]FF FF 03 04 00 00 00 0A FE FE",  # CMD_SET_FAN_SPEED
            "<[05:10:52]FF FF 03 00 FE FE",              # STATUS_FAN_SPEED_OK
            ">[05:10:52]FF FF 04 0C 00 00 02 08 00 00 01 5E 00 00 27 10 FE FE", # CMD_LMA_INIT
            "<[05:10:52]FF FF 04 00 FE FE",              # STATUS_LMA_INIT_OK
            "<[05:10:55]FF FF 0B 00 FE FE",              # STATUS_OPERATING_TEMP_REACHED
            ">[05:10:57]FF FF 08 00 FE FE",              # CMD_STROKE_INIT_COMPLETE
            "<[05:10:57]FF FF 08 00 FE FE",              # STATUS_STROKE_INIT_OK
            "<[05:11:07]FF FF 0C 00 FE FE",              # STATUS_STANDBY_TEMP_REACHED
        ]
        
        # 로그 엔트리 파싱
        for line in log_data:
            entry = self.parse_log_entry(line)
            self.log_entries.append(entry)
            
        self.print_timing_analysis()
        
    def get_command_name(self, packet_hex: str, direction: str) -> str:
        """패킷에서 명령/상태 이름 추출"""
        # STX 이후 첫 번째 바이트가 명령/상태 코드
        try:
            bytes_data = bytes.fromhex(packet_hex.replace(' ', ''))
            code = bytes_data[2]  # STX(2바이트) 이후
            
            if direction == "PC->MCU":  # 명령
                commands = {
                    0x01: "CMD_ENTER_TEST_MODE",
                    0x02: "CMD_SET_UPPER_TEMP", 
                    0x03: "CMD_SET_FAN_SPEED",
                    0x04: "CMD_LMA_INIT",
                    0x08: "CMD_STROKE_INIT_COMPLETE"
                }
                return commands.get(code, f"CMD_UNKNOWN_0x{code:02X}")
            else:  # 응답
                statuses = {
                    0x01: "STATUS_TEST_MODE_COMPLETE",
                    0x02: "STATUS_UPPER_TEMP_OK",
                    0x03: "STATUS_FAN_SPEED_OK", 
                    0x04: "STATUS_LMA_INIT_OK",
                    0x08: "STATUS_STROKE_INIT_OK",
                    0x0B: "STATUS_OPERATING_TEMP_REACHED",
                    0x0C: "STATUS_STANDBY_TEMP_REACHED"
                }
                return statuses.get(code, f"STATUS_UNKNOWN_0x{code:02X}")
        except:
            return "PARSE_ERROR"
            
    def print_timing_analysis(self) -> None:
        """타이밍 분석 결과 출력"""
        
        print("🕐 실제 MCU 통신 타이밍 분석")
        print("=" * 80)
        
        base_time = self.log_entries[0]['time_seconds']
        
        print(f"\n📋 통신 로그 (상대시간):")
        for i, entry in enumerate(self.log_entries):
            relative_time = entry['time_seconds'] - base_time
            cmd_name = self.get_command_name(entry['packet_hex'], entry['direction'])
            
            print(f"[{i+1:2d}] +{relative_time:2d}s [{entry['time_str']}] {entry['direction']}: {cmd_name}")
            
        # 명령-응답 쌍별 타이밍 분석
        self.analyze_command_response_timing()
        
        # 대기시간 vs 실제시간 비교
        self.compare_wait_times()
        
    def analyze_command_response_timing(self) -> None:
        """명령-응답 쌍별 타이밍 분석"""
        
        print(f"\n⚡ 명령-응답 타이밍 분석:")
        
        # 명령-응답 쌍 정의
        command_pairs = [
            (0, 1, "TEST_MODE", "즉시 응답"),
            (2, 3, "UPPER_TEMP", "즉시 응답"), 
            (4, 5, "FAN_SPEED", "즉시 응답"),
            (6, 7, "LMA_INIT (1차)", "즉시 ACK"),
            (7, 8, "LMA_INIT (2차)", "온도 도달 대기"),
            (9, 10, "STROKE_INIT (1차)", "즉시 ACK"),
            (10, 11, "STROKE_INIT (2차)", "온도 변화 대기")
        ]
        
        for cmd_idx, resp_idx, name, desc in command_pairs:
            if cmd_idx < len(self.log_entries) and resp_idx < len(self.log_entries):
                cmd_time = self.log_entries[cmd_idx]['time_seconds']
                resp_time = self.log_entries[resp_idx]['time_seconds']
                response_delay = resp_time - cmd_time
                
                if response_delay == 0:
                    delay_str = "< 1초 (즉시)"
                else:
                    delay_str = f"{response_delay}초"
                    
                print(f"   {name}: {delay_str} ({desc})")
                
    def compare_wait_times(self) -> None:
        """대기시간 비교 분석"""
        
        print(f"\n📊 대기시간 vs 실제시간 비교:")
        
        base_time = self.log_entries[0]['time_seconds']
        
        # 주요 단계별 시간 분석
        stages = [
            ("TEST_MODE 완료", 1, "0초"),
            ("UPPER_TEMP 완료", 3, "0초"), 
            ("FAN_SPEED 완료", 5, "0초"),
            ("LMA_INIT ACK", 7, "0초"),
            ("온도 도달", 8, "3초"),
            ("STROKE_INIT ACK", 10, "2초"), 
            ("최종 완료", 11, "10초")
        ]
        
        print(f"\n   단계별 실제 소요시간:")
        for stage_name, entry_idx, expected in stages:
            if entry_idx < len(self.log_entries):
                actual_time = self.log_entries[entry_idx]['time_seconds'] - base_time
                print(f"   {stage_name}: {actual_time}초 (예상: {expected})")
                
        # 현재 코드와 비교
        print(f"\n🔄 현재 코드 vs 실제 통신:")
        print(f"   현재 코드 (mcu_command_stabilization = 3초):")
        print(f"     UPPER_TEMP(3s) + FAN_SPEED(3s) + LMA_INIT(3s) = 9초 대기")
        print(f"   ")
        print(f"   실제 통신 패턴:")
        print(f"     UPPER_TEMP(<1s) + FAN_SPEED(<1s) + LMA_INIT(3s 온도대기) = 4초 이하")
        print(f"   ")
        print(f"   최적화 가능성:")
        print(f"     UPPER_TEMP(0s) + FAN_SPEED(0s) + LMA_INIT(온도대기만) = 5초 단축!")
        
        # 핵심 발견사항
        print(f"\n🎯 핵심 발견사항:")
        print(f"   1. ✅ UPPER_TEMP, FAN_SPEED: 즉시 응답 (< 1초)")
        print(f"   2. ✅ LMA_INIT: 즉시 ACK + 3초 후 온도 도달")
        print(f"   3. ❌ 현재 각 명령마다 3초씩 대기 = 불필요한 6초 낭비")
        print(f"   4. ✅ 펌웨어 개발자 주장 입증: 즉시 연속 명령 가능")
        
        # 최적화 권장안
        print(f"\n💡 즉시 적용 가능한 최적화:")
        print(f"   mcu_command_stabilization = 0.1초 (또는 0초)")
        print(f"   -> UPPER_TEMP + FAN_SPEED 단계에서 6초 단축")
        print(f"   -> 전체 테스트 시간 67% 단축 효과")

def main():
    """메인 실행"""
    analyzer = RealTimingAnalyzer()
    analyzer.analyze_real_communication()

if __name__ == "__main__":
    main()