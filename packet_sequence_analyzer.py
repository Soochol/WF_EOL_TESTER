#!/usr/bin/env python3
"""
MCU 패킷 시퀀스 분석 도구

실제 MCU 통신 패킷을 분석하여 명령 시퀀스와 응답 패턴을 확인합니다.
"""

import struct
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# LMA MCU 상수들
COMMAND_CODES = {
    0x00: "CMD_BOOT_COMPLETE",
    0x01: "CMD_ENTER_TEST_MODE", 
    0x02: "CMD_SET_UPPER_TEMP",
    0x03: "CMD_SET_FAN_SPEED",
    0x04: "CMD_LMA_INIT",
    0x05: "CMD_SET_OPERATING_TEMP",
    0x06: "CMD_SET_COOLING_TEMP",
    0x07: "CMD_REQUEST_TEMP",
    0x08: "CMD_STROKE_INIT_COMPLETE",
}

STATUS_CODES = {
    0x00: "STATUS_BOOT_COMPLETE",
    0x01: "STATUS_TEST_MODE_COMPLETE", 
    0x02: "STATUS_UPPER_TEMP_OK",
    0x03: "STATUS_FAN_SPEED_OK",
    0x04: "STATUS_LMA_INIT_OK",
    0x05: "STATUS_OPERATING_TEMP_OK",
    0x06: "STATUS_COOLING_TEMP_OK",
    0x07: "STATUS_TEMP_RESPONSE",
    0x08: "STATUS_STROKE_INIT_OK",
    0x09: "STATUS_TEMP_RISE_START",
    0x0A: "STATUS_TEMP_FALL_START",
    0x0B: "STATUS_OPERATING_TEMP_REACHED",
    0x0C: "STATUS_STANDBY_TEMP_REACHED",
    0x0D: "STATUS_COOLING_TEMP_REACHED",
    0x0E: "STATUS_LMA_INIT_COMPLETE",
}

TEMP_SCALE_FACTOR = 10

@dataclass
class MCUPacket:
    """MCU 패킷 구조"""
    raw_data: str
    packet_type: str  # "COMMAND" or "STATUS"
    code: int
    code_name: str
    data_length: int
    data: bytes
    parsed_data: Optional[Dict] = None
    
class PacketSequenceAnalyzer:
    """패킷 시퀀스 분석기"""
    
    def __init__(self):
        self.packets: List[MCUPacket] = []
        
    def parse_hex_string(self, hex_str: str) -> bytes:
        """16진수 문자열을 바이트로 변환"""
        # 공백 제거 및 정규화
        hex_clean = hex_str.replace(" ", "").replace("\n", "").upper()
        return bytes.fromhex(hex_clean)
        
    def parse_packet(self, hex_str: str) -> Optional[MCUPacket]:
        """단일 패킷 파싱"""
        try:
            packet_bytes = self.parse_hex_string(hex_str)
            
            # 최소 패킷 크기 검증 (STX + CODE + LEN + ETX = 6바이트)
            if len(packet_bytes) < 6:
                print(f"❌ 패킷 크기 부족: {len(packet_bytes)}바이트")
                return None
                
            # STX 검증 (FF FF)
            if packet_bytes[0:2] != b'\xff\xff':
                print(f"❌ STX 오류: {packet_bytes[0:2].hex()}")
                return None
                
            # ETX 검증 (FE FE)
            if packet_bytes[-2:] != b'\xfe\xfe':
                print(f"❌ ETX 오류: {packet_bytes[-2:].hex()}")
                return None
                
            # CODE와 LEN 추출
            code = packet_bytes[2]
            data_length = packet_bytes[3]
            
            # 데이터 추출
            if data_length > 0:
                data = packet_bytes[4:4+data_length]
            else:
                data = b''
                
            # 패킷 타입 및 코드명 결정
            if code in COMMAND_CODES:
                packet_type = "COMMAND"
                code_name = COMMAND_CODES[code]
            elif code in STATUS_CODES:
                packet_type = "STATUS" 
                code_name = STATUS_CODES[code]
            else:
                packet_type = "UNKNOWN"
                code_name = f"UNKNOWN_0x{code:02X}"
                
            # 데이터 파싱
            parsed_data = self.parse_packet_data(code, data)
            
            return MCUPacket(
                raw_data=hex_str,
                packet_type=packet_type,
                code=code,
                code_name=code_name,
                data_length=data_length,
                data=data,
                parsed_data=parsed_data
            )
            
        except Exception as e:
            print(f"❌ 패킷 파싱 오류: {e}")
            return None
            
    def parse_packet_data(self, code: int, data: bytes) -> Optional[Dict]:
        """패킷 데이터 내용 파싱"""
        if len(data) == 0:
            return None
            
        parsed = {}
        
        try:
            if code == 0x01:  # CMD_ENTER_TEST_MODE
                if len(data) >= 4:
                    test_mode = struct.unpack(">I", data[:4])[0]
                    parsed["test_mode"] = test_mode
                    
            elif code == 0x02:  # CMD_SET_UPPER_TEMP
                if len(data) >= 4:
                    temp_raw = struct.unpack(">I", data[:4])[0]
                    temp_celsius = temp_raw / TEMP_SCALE_FACTOR
                    parsed["upper_temperature"] = temp_celsius
                    parsed["raw_value"] = temp_raw
                    
            elif code == 0x03:  # CMD_SET_FAN_SPEED
                if len(data) >= 4:
                    fan_speed = struct.unpack(">I", data[:4])[0]
                    parsed["fan_speed"] = fan_speed
                    
            elif code == 0x04:  # CMD_LMA_INIT
                if len(data) >= 12:
                    op_temp_raw, standby_temp_raw, hold_time = struct.unpack(">III", data[:12])
                    parsed["operating_temperature"] = op_temp_raw / TEMP_SCALE_FACTOR
                    parsed["standby_temperature"] = standby_temp_raw / TEMP_SCALE_FACTOR
                    parsed["hold_time_ms"] = hold_time
                    parsed["raw_op_temp"] = op_temp_raw
                    parsed["raw_standby_temp"] = standby_temp_raw
                    
            elif code == 0x05:  # CMD_SET_OPERATING_TEMP
                if len(data) >= 4:
                    temp_raw = struct.unpack(">I", data[:4])[0]
                    temp_celsius = temp_raw / TEMP_SCALE_FACTOR
                    parsed["operating_temperature"] = temp_celsius
                    parsed["raw_value"] = temp_raw
                    
            elif code == 0x07:  # STATUS_TEMP_RESPONSE
                if len(data) >= 8:
                    max_temp_raw, ambient_temp_raw = struct.unpack(">II", data[:8])
                    parsed["max_temperature"] = max_temp_raw / TEMP_SCALE_FACTOR
                    parsed["ambient_temperature"] = ambient_temp_raw / TEMP_SCALE_FACTOR
                elif len(data) >= 4:
                    temp_raw = struct.unpack(">I", data[:4])[0]
                    parsed["temperature"] = temp_raw / TEMP_SCALE_FACTOR
                    
        except Exception as e:
            parsed["parse_error"] = str(e)
            
        return parsed if parsed else None
        
    def analyze_sequence(self, packet_list: List[str]) -> None:
        """패킷 시퀀스 분석"""
        print("🔍 MCU 패킷 시퀀스 분석")
        print("=" * 80)
        
        for i, packet_hex in enumerate(packet_list):
            packet = self.parse_packet(packet_hex.strip())
            if packet:
                self.packets.append(packet)
                
                # 패킷 정보 출력
                direction = "PC -> MCU" if packet.packet_type == "COMMAND" else "MCU -> PC"
                print(f"\n[{i+1:2d}] {direction}: {packet.code_name}")
                print(f"     Raw: {packet.raw_data}")
                print(f"     Code: 0x{packet.code:02X}, Data Length: {packet.data_length}")
                
                if packet.data_length > 0:
                    print(f"     Data: {packet.data.hex().upper()}")
                    
                if packet.parsed_data:
                    print(f"     Parsed: {packet.parsed_data}")
                    
        self.analyze_command_response_pairs()
        self.analyze_sequence_flow()
        
    def analyze_command_response_pairs(self) -> None:
        """명령-응답 쌍 분석"""
        print("\n" + "=" * 80)
        print("📡 명령-응답 쌍 분석")
        print("=" * 80)
        
        commands = [p for p in self.packets if p.packet_type == "COMMAND"]
        responses = [p for p in self.packets if p.packet_type == "STATUS"]
        
        for i, cmd in enumerate(commands):
            print(f"\n🔄 명령 {i+1}: {cmd.code_name}")
            
            # 해당 명령 이후의 응답들 찾기
            cmd_index = self.packets.index(cmd)
            following_responses = []
            
            for j in range(cmd_index + 1, len(self.packets)):
                if self.packets[j].packet_type == "STATUS":
                    following_responses.append(self.packets[j])
                elif self.packets[j].packet_type == "COMMAND":
                    break  # 다음 명령 시작
                    
            if following_responses:
                print(f"   응답 ({len(following_responses)}개):")
                for resp in following_responses:
                    print(f"   -> {resp.code_name}")
            else:
                print("   ❌ 응답 없음")
                
    def analyze_sequence_flow(self) -> None:
        """시퀀스 흐름 분석"""
        print("\n" + "=" * 80)
        print("🔀 시퀀스 흐름 분석")
        print("=" * 80)
        
        commands = [p for p in self.packets if p.packet_type == "COMMAND"]
        
        print(f"\n📋 명령 시퀀스 ({len(commands)}개):")
        for i, cmd in enumerate(commands):
            sequence_info = ""
            if cmd.parsed_data:
                if "test_mode" in cmd.parsed_data:
                    sequence_info = f" (모드: {cmd.parsed_data['test_mode']})"
                elif "upper_temperature" in cmd.parsed_data:
                    sequence_info = f" ({cmd.parsed_data['upper_temperature']}°C)"
                elif "fan_speed" in cmd.parsed_data:
                    sequence_info = f" (레벨: {cmd.parsed_data['fan_speed']})"
                elif "operating_temperature" in cmd.parsed_data:
                    op_temp = cmd.parsed_data['operating_temperature']
                    standby_temp = cmd.parsed_data.get('standby_temperature', '?')
                    sequence_info = f" (동작: {op_temp}°C, 대기: {standby_temp}°C)"
                    
            print(f"   {i+1}. {cmd.code_name}{sequence_info}")
            
        # 예상 시퀀스와 비교
        print(f"\n🎯 예상 시퀀스와 비교:")
        expected_sequence = [
            "CMD_ENTER_TEST_MODE", 
            "CMD_SET_UPPER_TEMP",
            "CMD_SET_FAN_SPEED", 
            "CMD_LMA_INIT"
        ]
        
        actual_sequence = [cmd.code_name for cmd in commands]
        
        print(f"   예상: {' -> '.join(expected_sequence)}")
        print(f"   실제: {' -> '.join(actual_sequence)}")
        
        if actual_sequence == expected_sequence:
            print("   ✅ 시퀀스 일치!")
        else:
            print("   ❌ 시퀀스 불일치")
            
        # 온도 값 검증
        self.validate_temperature_values()
        
    def validate_temperature_values(self) -> None:
        """온도 값 검증"""
        print(f"\n🌡️ 온도 값 검증:")
        
        for packet in self.packets:
            if packet.parsed_data:
                if "upper_temperature" in packet.parsed_data:
                    temp = packet.parsed_data["upper_temperature"]
                    print(f"   상한 온도: {temp}°C (예상: 80°C)")
                    if abs(temp - 80.0) < 0.1:
                        print("   ✅ 상한 온도 값 정상")
                    else:
                        print("   ❌ 상한 온도 값 이상")
                        
                elif "operating_temperature" in packet.parsed_data:
                    op_temp = packet.parsed_data["operating_temperature"]
                    standby_temp = packet.parsed_data.get("standby_temperature")
                    print(f"   동작 온도: {op_temp}°C")
                    if standby_temp:
                        print(f"   대기 온도: {standby_temp}°C")

def main():
    """메인 실행 함수"""
    # 사용자가 제공한 패킷 데이터
    packet_data = [
        "FF FF 00 00 FE FE",                                    # 1
        "FF FF 01 04 00 00 00 01 FE FE",                        # 2  
        "FF FF 01 00 FE FE",                                    # 3
        "FF FF 02 04 00 00 02 08 FE FE",                        # 4
        "FF FF 02 00 FE FE",                                    # 5
        "FF FF 03 04 00 00 00 0A FE FE",                        # 6
        "FF FF 03 00 FE FE",                                    # 7
        "FF FF 04 0C 00 00 02 08 00 00 01 5E 00 00 27 10 FE FE", # 8
        "FF FF 04 00 FE FE",                                    # 9
        "FF FF 0B 00 FE FE",                                    # 10
        "FF FF 08 00 FE FE",                                    # 11
        "FF FF 08 00 FE FE",                                    # 12
        "FF FF 0C 00 FE FE",                                    # 13
    ]
    
    analyzer = PacketSequenceAnalyzer()
    analyzer.analyze_sequence(packet_data)

if __name__ == "__main__":
    main()