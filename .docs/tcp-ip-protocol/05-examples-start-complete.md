# 착공/완공 예제 코드

> **Version**: 1.0.0
> **Last Updated**: 2025-01-26

## 개요

이 문서는 착공(START)과 완공(COMPLETE) 메시지를 전송하는 예제 코드를 제공합니다.

---

## Python 예제

### 착공/완공 클라이언트

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroHub 착공/완공 클라이언트
"""

import socket
import json
from datetime import datetime


class NeuroHubClient:
    """NeuroHub 통신 클라이언트"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9000):
        self.host = host
        self.port = port
    
    def _send(self, data: dict) -> dict:
        """TCP로 데이터 전송"""
        json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((self.host, self.port))
            
            # 길이 헤더 + JSON 전송
            length_header = len(json_bytes).to_bytes(4, byteorder='big')
            sock.sendall(length_header + json_bytes)
            
            # ACK 수신
            response = sock.recv(4096)
            return json.loads(response.decode('utf-8'))
    
    def start_work(self, serial_number: str, **kwargs) -> dict:
        """
        착공 (작업 시작) 전송
        
        Args:
            serial_number: WIP 시리얼 번호
            **kwargs: 추가 필드 (equipment_id, worker_id 등)
        """
        data = {
            "message_type": "START",
            "serial_number": serial_number,
            **kwargs
        }
        return self._send(data)
    
    def complete_work(self, serial_number: str, result: str,
                      measurements: list = None, defects: list = None,
                      **kwargs) -> dict:
        """
        완공 (작업 완료) 전송
        
        Args:
            serial_number: WIP 시리얼 번호
            result: 검사 결과 ("PASS" 또는 "FAIL")
            measurements: 측정 데이터 목록
            defects: 불량 목록 (FAIL 시)
            **kwargs: 추가 필드
        """
        data = {
            "message_type": "COMPLETE",
            "serial_number": serial_number,
            "result": result,
            **kwargs
        }
        if measurements:
            data["measurements"] = measurements
        if defects:
            data["defects"] = defects
        return self._send(data)


# 사용 예시
if __name__ == "__main__":
    client = NeuroHubClient()
    serial = "WIP-KR01PSA2511-001"
    
    # 1. 착공
    print("=== 착공 ===")
    ack = client.start_work(serial)
    print(f"응답: {ack}")
    
    # 2. 검사 수행...
    print("\n검사 수행 중...")
    
    # 3. 완공 (PASS)
    print("\n=== 완공 (PASS) ===")
    measurements = [
        {
            "code": "VOLTAGE",
            "name": "전압",
            "value": 12.1,
            "unit": "V",
            "spec": {"min": 11.8, "max": 12.4},
            "result": "PASS"
        }
    ]
    ack = client.complete_work(serial, "PASS", measurements=measurements)
    print(f"응답: {ack}")
```

### 착공만 전송

```python
# 착공만 전송 (간단)
data = {
    "message_type": "START",
    "serial_number": "WIP-KR01PSA2511-001"
}
ack = send_to_neurohub(data)
```

### 완공만 전송 (착공 생략)

```python
# 완공만 전송 (착공 없이도 가능)
data = {
    "message_type": "COMPLETE",
    "result": "PASS",
    "serial_number": "WIP-KR01PSA2511-001",
    "measurements": [...]
}
ack = send_to_neurohub(data)
```

### FAIL 결과 전송

```python
# 불량 결과 전송
data = {
    "message_type": "COMPLETE",
    "result": "FAIL",
    "serial_number": "WIP-KR01PSA2511-001",
    "measurements": [
        {
            "code": "VOLTAGE",
            "value": 12.8,
            "result": "FAIL"
        }
    ],
    "defects": [
        {
            "code": "VOLTAGE",
            "reason": "상한 초과 (12.8V > 12.4V)"
        }
    ]
}
ack = send_to_neurohub(data)
```

---

## C# 예제

### 착공/완공 클라이언트

```csharp
using System;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;

public class NeuroHubClient
{
    private readonly string _host;
    private readonly int _port;
    
    public NeuroHubClient(string host = "127.0.0.1", int port = 9000)
    {
        _host = host;
        _port = port;
    }
    
    private string Send(object data)
    {
        var json = JsonSerializer.Serialize(data);
        var jsonBytes = Encoding.UTF8.GetBytes(json);
        
        using var client = new TcpClient(_host, _port);
        using var stream = client.GetStream();
        
        // 길이 헤더 (Big Endian)
        var lengthBytes = BitConverter.GetBytes(jsonBytes.Length);
        if (BitConverter.IsLittleEndian)
            Array.Reverse(lengthBytes);
        
        stream.Write(lengthBytes, 0, 4);
        stream.Write(jsonBytes, 0, jsonBytes.Length);
        
        // ACK 수신
        var buffer = new byte[4096];
        var bytesRead = stream.Read(buffer, 0, buffer.Length);
        return Encoding.UTF8.GetString(buffer, 0, bytesRead);
    }
    
    public string StartWork(string serialNumber)
    {
        var data = new {
            message_type = "START",
            serial_number = serialNumber
        };
        return Send(data);
    }
    
    public string CompleteWork(string serialNumber, string result, object[] measurements = null)
    {
        var data = new {
            message_type = "COMPLETE",
            serial_number = serialNumber,
            result = result,
            measurements = measurements
        };
        return Send(data);
    }
}

// 사용 예시
var client = new NeuroHubClient();
var serial = "WIP-KR01PSA2511-001";

// 착공
var ack1 = client.StartWork(serial);
Console.WriteLine($"착공 응답: {ack1}");

// 완공
var measurements = new[] {
    new { code = "VOLTAGE", value = 12.1, result = "PASS" }
};
var ack2 = client.CompleteWork(serial, "PASS", measurements);
Console.WriteLine($"완공 응답: {ack2}");
```

---

## 시퀀스 다이어그램

```
[검사 장비]                    [NeuroHub Client]              [Backend]
     │                               │                           │
     │  START (착공)                 │                           │
     │──────────────────────────────>│                           │
     │                               │  POST /start-process      │
     │                               │──────────────────────────>│
     │                               │         OK                │
     │                               │<──────────────────────────│
     │  ACK {status: "OK"}           │                           │
     │<──────────────────────────────│                           │
     │                               │                           │
     │       ~~~ 검사 수행 ~~~        │                           │
     │                               │                           │
     │  COMPLETE (완공)              │                           │
     │──────────────────────────────>│                           │
     │                               │  POST /complete-process   │
     │                               │──────────────────────────>│
     │                               │         OK                │
     │                               │<──────────────────────────│
     │  ACK {status: "OK"}           │                           │
     │<──────────────────────────────│                           │
     │                               │                           │
```

---

*참조: [JSON 메시지 스키마](./02-json-schema.md)*
