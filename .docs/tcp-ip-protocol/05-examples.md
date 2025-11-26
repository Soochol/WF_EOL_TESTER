# 예제 코드

> **Version**: 1.1.0
> **Last Updated**: 2025-01-26

## 개요

이 문서는 다양한 프로그래밍 언어로 NeuroHub Client와 연동하는 예제 코드를 제공합니다.

> **핵심 원칙**: 검사 장비 SW는 **WIP ID(serial_number)와 검사 결과만 전송**합니다.
> 작업자 ID, 공정 ID, 설비 ID는 NeuroHub Client에서 설정된 값을 사용합니다.

---

## 1. Python 예제

### 1.1 TCP 클라이언트 (기본)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroHub TCP 클라이언트 - 기본 예제
"""

import socket
import json


def send_to_neurohub(data: dict, host: str = "127.0.0.1", port: int = 9000) -> dict:
    """
    검사 결과를 NeuroHub Client로 전송

    Args:
        data: 검사 결과 데이터 (dict)
        host: NeuroHub Client 호스트
        port: TCP 포트 번호

    Returns:
        ACK 응답 (dict)
    """
    # JSON 직렬화
    json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(10)
        sock.connect((host, port))

        # 길이 헤더 전송 (4바이트, Big Endian)
        length_header = len(json_bytes).to_bytes(4, byteorder='big')
        sock.sendall(length_header)

        # JSON 데이터 전송
        sock.sendall(json_bytes)

        # ACK 수신
        response = sock.recv(4096)
        return json.loads(response.decode('utf-8'))


# 사용 예시
if __name__ == "__main__":
    # 착공 (START) 메시지 - WIP ID만 전송
    start_data = {
        "message_type": "START",
        "serial_number": "WIP-KR01PSA2511-001"  # WIP ID (필수)
    }

    # 완공 (COMPLETE) 메시지 - WIP ID + 검사 결과
    result_data = {
        "message_type": "COMPLETE",
        "serial_number": "WIP-KR01PSA2511-001",  # WIP ID (필수)
        "result": "PASS",
        "measurements": [
            {
                "code": "VOLTAGE",
                "name": "전압 측정",
                "value": 12.1,
                "unit": "V",
                "spec": {
                    "min": 11.8,
                    "max": 12.4,
                    "target": 12.0
                },
                "result": "PASS"
            },
            {
                "code": "CURRENT",
                "name": "전류 측정",
                "value": 2.5,
                "unit": "A",
                "spec": {
                    "min": 2.0,
                    "max": 3.0
                },
                "result": "PASS"
            }
        ]
    }

    # 전송
    try:
        ack = send_to_neurohub(result_data)
        print(f"응답: {ack}")

        if ack.get('status') == 'OK':
            print("✅ 전송 성공!")
        else:
            print(f"❌ 전송 실패: {ack.get('message')}")
    except Exception as e:
        print(f"❌ 에러: {e}")
```

### 1.2 TCP 클라이언트 (재시도 포함)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroHub TCP 클라이언트 - 재시도 로직 포함
"""

import socket
import json
import time
import logging
from typing import Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class NeuroHubClient:
    """NeuroHub 통신 클라이언트"""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9000,
        timeout: int = 10,
        max_retries: int = 3
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries

    def send(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        검사 결과 전송 (자동 재시도)

        Args:
            data: 검사 결과 데이터

        Returns:
            ACK 응답

        Raises:
            RuntimeError: 모든 재시도 실패 시
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return self._send_once(data)
            except (socket.error, ConnectionError) as e:
                last_error = e
                logger.warning(f"전송 실패 (시도 {attempt + 1}/{self.max_retries}): {e}")

                if attempt < self.max_retries - 1:
                    delay = 2 ** attempt  # 1, 2, 4초
                    logger.info(f"{delay}초 후 재시도...")
                    time.sleep(delay)

        raise RuntimeError(f"전송 실패 (최대 재시도 초과): {last_error}")

    def _send_once(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """단일 전송 시도"""
        json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))

            # 길이 헤더 + 데이터 전송
            length_header = len(json_bytes).to_bytes(4, byteorder='big')
            sock.sendall(length_header + json_bytes)

            # ACK 수신
            response = sock.recv(4096)
            if not response:
                raise ConnectionError("서버 응답 없음")

            return json.loads(response.decode('utf-8'))


# 사용 예시
if __name__ == "__main__":
    client = NeuroHubClient()

    # 착공 (START) 메시지
    start_data = {
        "message_type": "START",
        "serial_number": "WIP-KR01PSA2511-001"  # WIP ID (필수)
    }

    # 완공 (COMPLETE) 메시지
    complete_data = {
        "message_type": "COMPLETE",
        "serial_number": "WIP-KR01PSA2511-001",  # WIP ID (필수)
        "result": "PASS",
        "measurements": [
            {"code": "VOLTAGE", "value": 12.1, "result": "PASS"}
        ]
    }

    try:
        # 착공 전송
        ack = client.send(start_data)
        logger.info(f"착공 완료: {ack}")

        # ... 검사 수행 ...

        # 완공 전송
        ack = client.send(complete_data)
        logger.info(f"완공 완료: {ack}")
    except RuntimeError as e:
        logger.error(f"전송 실패: {e}")
```

### 1.3 파일 기반 연동

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroHub 파일 기반 연동 예제
"""

import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Any


class NeuroHubFileWriter:
    """파일 기반 NeuroHub 연동"""

    def __init__(self, base_folder: str = "C:/neurohub_work"):
        self.base_folder = base_folder
        self.pending_folder = os.path.join(base_folder, "pending")

        # 폴더 생성
        os.makedirs(self.pending_folder, exist_ok=True)

    def save_result(self, data: Dict[str, Any]) -> str:
        """
        검사 결과를 JSON 파일로 저장

        Args:
            data: 검사 결과 데이터

        Returns:
            저장된 파일 경로
        """
        # 고유 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"result_{timestamp}.json"

        # 임시 파일에 먼저 저장 (atomic write)
        fd, temp_path = tempfile.mkstemp(
            suffix='.tmp',
            dir=self.pending_folder
        )

        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 최종 파일명으로 rename
            final_path = os.path.join(self.pending_folder, filename)
            os.rename(temp_path, final_path)

            return final_path

        except Exception:
            # 에러 시 임시 파일 삭제
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise


# 사용 예시
if __name__ == "__main__":
    writer = NeuroHubFileWriter()

    # WIP ID + 검사 결과만 전송 (worker_id, process_id, equipment_id는 Client에서 보충)
    data = {
        "serial_number": "WIP-KR01PSA2511-001",  # WIP ID (필수)
        "result": "PASS",
        "measurements": [
            {
                "code": "TEMP_SENSOR",
                "name": "온도 센서",
                "value": 60.2,
                "unit": "°C",
                "spec": {"min": 55, "max": 65},
                "result": "PASS"
            }
        ]
    }

    filepath = writer.save_result(data)
    print(f"파일 저장 완료: {filepath}")
```

---

## 2. C# 예제

### 2.1 TCP 클라이언트

```csharp
// NeuroHubClient.cs
using System;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace NeuroHub
{
    public class NeuroHubClient : IDisposable
    {
        private readonly string _host;
        private readonly int _port;
        private readonly int _timeout;

        public NeuroHubClient(string host = "127.0.0.1", int port = 9000, int timeout = 10000)
        {
            _host = host;
            _port = port;
            _timeout = timeout;
        }

        public async Task<AckResponse> SendAsync(EquipmentData data)
        {
            using var client = new TcpClient();
            client.ReceiveTimeout = _timeout;
            client.SendTimeout = _timeout;

            await client.ConnectAsync(_host, _port);

            using var stream = client.GetStream();

            // JSON 직렬화
            var jsonString = JsonSerializer.Serialize(data, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                WriteIndented = false
            });
            var jsonBytes = Encoding.UTF8.GetBytes(jsonString);

            // 길이 헤더 (4바이트, Big Endian)
            var lengthBytes = BitConverter.GetBytes(jsonBytes.Length);
            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(lengthBytes);
            }

            // 전송
            await stream.WriteAsync(lengthBytes, 0, 4);
            await stream.WriteAsync(jsonBytes, 0, jsonBytes.Length);

            // ACK 수신
            var buffer = new byte[4096];
            var bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
            var responseJson = Encoding.UTF8.GetString(buffer, 0, bytesRead);

            return JsonSerializer.Deserialize<AckResponse>(responseJson, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            });
        }

        public void Dispose()
        {
            // 리소스 정리
        }
    }

    // 데이터 모델
    public class EquipmentData
    {
        public string MessageType { get; set; }  // "START" 또는 "COMPLETE"
        public string SerialNumber { get; set; }  // WIP ID (필수)
        public string Result { get; set; }
        public MeasurementItem[] Measurements { get; set; }
        public DefectItem[] Defects { get; set; }
    }

    public class MeasurementItem
    {
        public string Code { get; set; }
        public string Name { get; set; }
        public double Value { get; set; }
        public string Unit { get; set; }
        public SpecLimit Spec { get; set; }
        public string Result { get; set; }
    }

    public class SpecLimit
    {
        public double? Min { get; set; }
        public double? Max { get; set; }
        public double? Target { get; set; }
    }

    public class DefectItem
    {
        public string Code { get; set; }
        public string Reason { get; set; }
    }

    public class AckResponse
    {
        public string Status { get; set; }
        public string Message { get; set; }
    }
}
```

### 2.2 사용 예제

```csharp
// Program.cs
using System;
using System.Threading.Tasks;
using NeuroHub;

class Program
{
    static async Task Main(string[] args)
    {
        var client = new NeuroHubClient();

        // 착공 (START) 메시지 - WIP ID만 전송
        var startData = new EquipmentData
        {
            MessageType = "START",
            SerialNumber = "WIP-KR01PSA2511-001"  // WIP ID (필수)
        };

        // 완공 (COMPLETE) 메시지 - WIP ID + 검사 결과
        var completeData = new EquipmentData
        {
            MessageType = "COMPLETE",
            SerialNumber = "WIP-KR01PSA2511-001",  // WIP ID (필수)
            Result = "PASS",
            Measurements = new[]
            {
                new MeasurementItem
                {
                    Code = "VOLTAGE",
                    Name = "전압 측정",
                    Value = 12.1,
                    Unit = "V",
                    Spec = new SpecLimit { Min = 11.8, Max = 12.4, Target = 12.0 },
                    Result = "PASS"
                }
            }
        };

        try
        {
            // 착공 전송
            var ack = await client.SendAsync(startData);
            Console.WriteLine($"착공 응답: {ack.Status}");

            // ... 검사 수행 ...

            // 완공 전송
            ack = await client.SendAsync(completeData);
            if (ack.Status == "OK")
            {
                Console.WriteLine($"✅ 전송 성공: {ack.Message}");
            }
            else
            {
                Console.WriteLine($"❌ 전송 실패: {ack.Message}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ 에러: {ex.Message}");
        }
    }
}
```

---

## 3. C++ 예제

### 3.1 TCP 클라이언트 (Windows)

```cpp
// neurohub_client.h
#pragma once

#include <string>
#include <vector>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "Ws2_32.lib")

namespace NeuroHub {

struct MeasurementItem {
    std::string code;
    std::string name;
    double value;
    std::string unit;
    double spec_min;
    double spec_max;
    double spec_target;
    std::string result;
};

struct EquipmentData {
    std::string result;
    std::vector<MeasurementItem> measurements;
};

struct AckResponse {
    std::string status;
    std::string message;
};

class NeuroHubClient {
public:
    NeuroHubClient(const std::string& host = "127.0.0.1", int port = 9000);
    ~NeuroHubClient();

    AckResponse Send(const EquipmentData& data);

private:
    std::string host_;
    int port_;
    bool initialized_;

    std::string ToJson(const EquipmentData& data);
    AckResponse ParseAck(const std::string& json);
};

} // namespace NeuroHub
```

```cpp
// neurohub_client.cpp
#include "neurohub_client.h"
#include <sstream>
#include <stdexcept>

namespace NeuroHub {

NeuroHubClient::NeuroHubClient(const std::string& host, int port)
    : host_(host), port_(port), initialized_(false) {

    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        throw std::runtime_error("WSAStartup failed");
    }
    initialized_ = true;
}

NeuroHubClient::~NeuroHubClient() {
    if (initialized_) {
        WSACleanup();
    }
}

AckResponse NeuroHubClient::Send(const EquipmentData& data) {
    // 소켓 생성
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        throw std::runtime_error("Socket creation failed");
    }

    // 연결
    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port_);
    inet_pton(AF_INET, host_.c_str(), &serverAddr.sin_addr);

    if (connect(sock, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        closesocket(sock);
        throw std::runtime_error("Connection failed");
    }

    try {
        // JSON 변환
        std::string json = ToJson(data);

        // 길이 헤더 (Big Endian)
        uint32_t length = static_cast<uint32_t>(json.length());
        uint32_t lengthBE = htonl(length);

        // 전송
        send(sock, (char*)&lengthBE, 4, 0);
        send(sock, json.c_str(), static_cast<int>(json.length()), 0);

        // ACK 수신
        char buffer[4096];
        int bytesReceived = recv(sock, buffer, sizeof(buffer) - 1, 0);
        buffer[bytesReceived] = '\0';

        closesocket(sock);
        return ParseAck(std::string(buffer));
    }
    catch (...) {
        closesocket(sock);
        throw;
    }
}

std::string NeuroHubClient::ToJson(const EquipmentData& data) {
    std::ostringstream ss;
    ss << "{\"result\":\"" << data.result << "\",\"measurements\":[";

    for (size_t i = 0; i < data.measurements.size(); ++i) {
        const auto& m = data.measurements[i];
        if (i > 0) ss << ",";
        ss << "{\"code\":\"" << m.code << "\","
           << "\"name\":\"" << m.name << "\","
           << "\"value\":" << m.value << ","
           << "\"unit\":\"" << m.unit << "\","
           << "\"spec\":{\"min\":" << m.spec_min
           << ",\"max\":" << m.spec_max
           << ",\"target\":" << m.spec_target << "},"
           << "\"result\":\"" << m.result << "\"}";
    }

    ss << "]}";
    return ss.str();
}

AckResponse NeuroHubClient::ParseAck(const std::string& json) {
    AckResponse ack;
    // 간단한 JSON 파싱 (실제로는 라이브러리 사용 권장)
    auto statusPos = json.find("\"status\":\"");
    if (statusPos != std::string::npos) {
        auto start = statusPos + 10;
        auto end = json.find("\"", start);
        ack.status = json.substr(start, end - start);
    }

    auto msgPos = json.find("\"message\":\"");
    if (msgPos != std::string::npos) {
        auto start = msgPos + 11;
        auto end = json.find("\"", start);
        ack.message = json.substr(start, end - start);
    }

    return ack;
}

} // namespace NeuroHub
```

### 3.2 사용 예제

```cpp
// main.cpp
#include "neurohub_client.h"
#include <iostream>

int main() {
    try {
        NeuroHub::NeuroHubClient client;

        NeuroHub::EquipmentData data;
        data.result = "PASS";

        NeuroHub::MeasurementItem m;
        m.code = "VOLTAGE";
        m.name = "전압 측정";
        m.value = 12.1;
        m.unit = "V";
        m.spec_min = 11.8;
        m.spec_max = 12.4;
        m.spec_target = 12.0;
        m.result = "PASS";
        data.measurements.push_back(m);

        auto ack = client.Send(data);

        if (ack.status == "OK") {
            std::cout << "전송 성공: " << ack.message << std::endl;
        } else {
            std::cout << "전송 실패: " << ack.message << std::endl;
        }
    }
    catch (const std::exception& e) {
        std::cerr << "에러: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
```

---

## 4. LabVIEW 예제

### 4.1 TCP 통신 블록 다이어그램

LabVIEW에서 TCP 통신을 구현하기 위한 단계:

```
1. TCP Open Connection
   - Address: 127.0.0.1
   - Port: 9000
   - Timeout: 10000 ms

2. Build JSON String (Flatten To JSON)
   - Cluster를 JSON 문자열로 변환

3. String to Byte Array (UTF-8)

4. Calculate Length (Array Size)

5. Build Length Header
   - U32 to Byte Array
   - Swap Bytes (Little → Big Endian)

6. TCP Write
   - Length Header (4 bytes)
   - JSON Data

7. TCP Read
   - Buffer: 4096 bytes
   - Timeout: 10000 ms

8. Parse ACK Response (Unflatten From JSON)

9. TCP Close Connection
```

### 4.2 데이터 타입 정의

```
// Measurement Cluster
typedef struct {
    String code;
    String name;
    Double value;
    String unit;
    Cluster spec {
        Double min;
        Double max;
        Double target;
    };
    String result;
} MeasurementItem;

// Equipment Data Cluster
typedef struct {
    String result;
    Array<MeasurementItem> measurements;
} EquipmentData;

// ACK Response Cluster
typedef struct {
    String status;
    String message;
} AckResponse;
```

---

## 5. 테스트 도구

### 5.1 Python 테스트 서버 (개발용)

```python
#!/usr/bin/env python3
"""
개발용 NeuroHub 테스트 서버
실제 NeuroHub Client 없이 검사 장비 SW를 테스트할 때 사용
"""

import socket
import json
import threading


def handle_client(client_socket, address):
    """클라이언트 요청 처리"""
    print(f"연결: {address}")

    try:
        # 길이 헤더 수신
        header = client_socket.recv(4)
        if len(header) < 4:
            # 직접 전송 모드
            data = header + client_socket.recv(65536)
        else:
            length = int.from_bytes(header, 'big')
            data = b''
            while len(data) < length:
                chunk = client_socket.recv(min(4096, length - len(data)))
                if not chunk:
                    break
                data += chunk

        # JSON 파싱
        try:
            json_data = json.loads(data.decode('utf-8'))
            print(f"수신 데이터: {json.dumps(json_data, ensure_ascii=False, indent=2)}")

            # 성공 ACK
            ack = {"status": "OK", "message": "Data received successfully"}
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 에러: {e}")
            ack = {"status": "ERROR", "message": f"JSON 파싱 오류: {e}"}

        # ACK 전송
        response = json.dumps(ack).encode('utf-8')
        client_socket.sendall(response)

    except Exception as e:
        print(f"에러: {e}")
    finally:
        client_socket.close()
        print(f"연결 종료: {address}")


def main():
    host = "0.0.0.0"
    port = 9000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)

    print(f"테스트 서버 시작: {host}:{port}")

    try:
        while True:
            client, address = server.accept()
            thread = threading.Thread(target=handle_client, args=(client, address))
            thread.start()
    except KeyboardInterrupt:
        print("\n서버 종료")
    finally:
        server.close()


if __name__ == "__main__":
    main()
```

### 5.2 연결 테스트 스크립트

```python
#!/usr/bin/env python3
"""
NeuroHub 연결 테스트 스크립트
"""

import socket
import sys


def test_connection(host="127.0.0.1", port=9000):
    """연결 테스트"""
    print(f"테스트 대상: {host}:{port}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        sock.close()
        print("✅ 연결 성공!")
        return True
    except ConnectionRefusedError:
        print("❌ 연결 거부 - NeuroHub Client가 실행 중인지 확인하세요")
        return False
    except socket.timeout:
        print("❌ 연결 타임아웃 - 네트워크 상태를 확인하세요")
        return False
    except Exception as e:
        print(f"❌ 에러: {e}")
        return False


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9000
    test_connection(host, port)
```

---

## 6. 문제 해결 가이드

### 6.1 일반적인 문제

| 문제 | 원인 | 해결 |
|------|------|------|
| 연결 거부 | NeuroHub Client 미실행 | 프로그램 실행 확인 |
| 타임아웃 | 포트 불일치 | 포트 설정 확인 |
| JSON 에러 | 형식 오류 | JSON 검증 도구 사용 |
| 한글 깨짐 | 인코딩 문제 | UTF-8 사용 확인 |

### 6.2 디버깅 팁

1. **연결 테스트**: 테스트 스크립트로 기본 연결 확인
2. **JSON 검증**: jsonlint.com 등에서 JSON 유효성 검사
3. **Wireshark**: 네트워크 패킷 분석
4. **로그 활성화**: 상세 로깅으로 문제 추적

---

## 7. 참조 자료

- [TCP/IP 프로토콜 사양](./01-tcp-protocol.md)
- [JSON 메시지 스키마](./02-json-schema.md)
- [파일 기반 연동](./03-file-integration.md)
- [에러 처리](./04-error-handling.md)

---

*이 문서는 NeuroHub 프로젝트의 일부입니다.*
