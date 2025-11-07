# Yokogawa WT1800E SCPI 명령어 완전 가이드
## 프로그래머를 위한 커맨드 레퍼런스

---

## 📌 개요

이 문서는 Yokogawa WT1800E 정밀 전력 분석기의 모든 SCPI(Simplified Commands for Programmable Instruments) 명령어를 정리한 것입니다.

**통신 프로토콜:** TCP/IP (VXI-11)  
**포트:** 111 (RPC) / 5555 (데이터)  
**문서:** IM WT1801-17EN_programming.pdf (4th Edition)

---

## 🔤 명령어 표기법

| 기호 | 의미 | 예시 |
|------|------|------|
| `< >` | 정의된 값 | `<x> = 1 to 6` |
| `{ }` | 선택 사항 중 하나 | `{ON\|OFF}` |
| `\|` | 또는 (OR) | `{ON\|OFF}` |
| `[ ]` | 생략 가능 | `[:NORMal]` |
| `?` | 쿼리 (읽기) | `:NUMERIC:VALUE?` |

---

## 📋 명령어 그룹 목록

1. [AOutput Group](#1-aoutput-group) - D/A 출력
2. [AUX Group](#2-aux-group) - 보조 입력
3. [COMMunicate Group](#3-communicate-group) - 통신 제어
4. [CURSor Group](#4-cursor-group) - 커서 측정
5. [DISPlay Group](#5-display-group) - 디스플레이 설정
6. [FILE Group](#6-file-group) - 파일 작업
7. [HARMonics Group](#7-harmonics-group) - 고조파 분석
8. [HCOPy Group](#8-hcopy-group) - 인쇄 설정
9. [HOLD Group](#9-hold-group) - 데이터 홀드
10. [HSPeed Group](#10-hspeed-group) - 고속 데이터 캡처
11. [IMAGe Group](#11-image-group) - 화면 이미지
12. [INPut Group](#12-input-group) - 입력 설정
13. [INTEGrate Group](#13-integrate-group) - 적분
14. [MEASure Group](#14-measure-group) - 측정 계산
15. [MOTor Group](#15-motor-group) - 모터 평가
16. [NUMeric Group](#16-numeric-group) - 수치 데이터
17. [RATE Group](#17-rate-group) - 데이터 레이트
18. [STATus Group](#18-status-group) - 상태 보고
19. [STORe Group](#19-store-group) - 데이터 저장
20. [SYSTem Group](#20-system-group) - 시스템 설정
21. [WAVeform Group](#21-waveform-group) - 파형 데이터
22. [Common Commands](#22-common-commands) - IEEE 488.2 공통 명령

---

## 1. AOutput Group

D/A 출력 설정 (옵션: /DA)

### :AOUTput?
**설명:** 모든 D/A 출력 설정을 조회합니다.

```
명령: :AOUTput?
응답: 10000,0,0
```

### :AOUTput:NORMal?
**설명:** 모든 D/A 출력 설정을 조회합니다.

```
명령: :AOUTput:NORMal?
응답: 10000,0,0
```

### :AOUTput[:NORMal]:CHANnel<x>
**설명:** D/A 출력 항목(함수, 요소, 고조파)을 설정하거나 조회합니다.

```
문법: :AOUTput[:NORMal]:CHANnel<x> {NONE|<Function>[,<Element>][,<Order>]}
      :AOUTput[:NORMal]:CHANnel<x>?

파라미터:
  <x> = 1 to 20 (출력 채널)
  NONE = 출력 항목 없음
  <Function> = {URMS|IRMS|P|S|Q|...}
  <Element> = {1-6|SIGMa|SIGMB|SIGMC}
  <Order> = {TOTal|DC|1-500}

예제:
  :AOUTPUT:NORMAL:CHANNEL1 URMS,1
  :AOUTPUT:NORMAL:CHANNEL1?  → :AOUTPUT:NORMAL:CHANNEL1 URMS,1
```

### :AOUTput[:NORMal]:IRTime
**설명:** D/A 출력의 적분값에 사용되는 적분 시간을 설정하거나 조회합니다.

```
문법: :AOUTput[:NORMal]:IRTime {<h>,<m>,<s>}
      :AOUTput[:NORMal]:IRTime?

파라미터:
  시간 = 0 to 10000 (시)
  분 = 0 to 59
  초 = 0 to 59

예제:
  :AOUTPUT:NORMAL:IRTIME 1,0,0
  :AOUTPUT:NORMAL:IRTIME?  → :AOUTPUT:NORMAL:IRTIME 1,0,0
```

### :AOUTput[:NORMal]:MODE<x>
**설명:** D/A 출력 항목의 정격값 설정 모드를 설정하거나 조회합니다.

```
문법: :AOUTput[:NORMal]:MODE<x> {FIXed|MANual}
      :AOUTput[:NORMal]:MODE<x>?

파라미터:
  <x> = 1 to 20 (출력 채널)
  FIXed = 고정 모드
  MANual = 수동 모드

예제:
  :AOUTPUT:NORMAL:MODE1 FIXED
  :AOUTPUT:NORMAL:MODE1?  → :AOUTPUT:NORMAL:MODE1 FIXED
```

### :AOUTput[:NORMal]:RATE<x>
**설명:** D/A 출력 항목의 최대/최소 정격값을 설정하거나 조회합니다.

```
문법: :AOUTput[:NORMal]:RATE<x> {<Upper>,<Lower>}
      :AOUTput[:NORMal]:RATE<x>?

파라미터:
  <x> = 1 to 20 (출력 채널)
  <Upper> = -9.999E+12 to 9.999E+12 (상한)
  <Lower> = -9.999E+12 to 9.999E+12 (하한)

예제:
  :AOUTPUT:NORMAL:RATE1 100,-100
  :AOUTPUT:NORMAL:RATE1?  → :AOUTPUT:NORMAL:RATE1 100.0E+00,-100.0E+00

주의: 상한을 먼저 설정한 후 하한을 설정합니다.
      MODE<x>가 MANual일 때 유효합니다.
```

---

## 2. AUX Group

보조 입력 설정 (옵션: /AUX)

### :AUX<x>?
**설명:** 모든 보조 입력 설정을 조회합니다.

```
문법: :AUX<x>?
파라미터: <x> = 1 or 2 (보조 입력 채널)
```

### :AUX<x>:AUTO
**설명:** 지정된 보조 입력의 자동 범위 설정을 설정하거나 조회합니다.

```
문법: :AUX<x>:AUTO {ON|OFF}
      :AUX<x>:AUTO?

예제:
  :AUX1:AUTO ON
  :AUX1:AUTO?  → :AUX1:AUTO 1
```

### :AUX<x>:FILTer?
**설명:** 보조 입력 필터 설정을 조회합니다.

```
문법: :AUX<x>:FILTer?
응답: 필터 설정 값
```

### :AUX<x>:FILTer[:LINE]
**설명:** 보조 입력의 라인 필터를 설정하거나 조회합니다.

```
문법: :AUX<x>:FILTer[:LINE] {OFF|<Frequency>}
      :AUX<x>:FILTer:LINE?

파라미터:
  OFF = 라인 필터 끄기
  <Frequency> = 100 Hz, 1 kHz (차단 주파수)

예제:
  :AUX:FILTER:LINE OFF
  :AUX:FILTER:LINE?  → :AUX1:FILTER:LINE OFF
```

### :AUX<x>:LSCale?
**설명:** 보조 입력 선형 스케일링 설정을 조회합니다.

```
문법: :AUX<x>:LSCale?
파라미터: <x> = 1 or 2
```

### :AUX<x>:LSCale:AVALue
**설명:** 보조 입력의 선형 스케일의 기울기(A)를 설정하거나 조회합니다.

```
문법: :AUX<x>:LSCale:AVALue {<Value>}
      :AUX<x>:LSCale:AVALue?

파라미터:
  <Value> = 1.000E-03 to 1.000E+06

예제:
  :AUX1:LSCALE:AVALUE 1.000
  :AUX1:LSCALE:AVALUE?  → :AUX1:LSCALE:AVALUE 1.000E+00
```

### :AUX<x>:LSCale:BVALue
**설명:** 보조 입력의 선형 스케일의 오프셋(B)을 설정하거나 조회합니다.

```
문법: :AUX<x>:LSCale:BVALue {<Value>}
      :AUX<x>:LSCale:BVALue?

파라미터:
  <Value> = -1.000E+06 to 1.000E+06

예제:
  :AUX1:LSCALE:BVALUE 0
  :AUX1:LSCALE:BVALUE?  → :AUX1:LSCALE:BVALUE 0.000E+00
```

### :AUX<x>:LSCale:CALCulate?
**설명:** 보조 입력 선형 스케일의 파라미터 계산 설정을 조회합니다.

```
문법: :AUX<x>:LSCale:CALCulate?
```

### :AUX<x>:LSCale:CALCulate:{P1X|P1Y|P2X|P2Y}
**설명:** 보조 입력 선형 스케일의 파라미터 계산 데이터를 설정하거나 조회합니다.

```
문법: :AUX<x>:LSCale:CALCulate:{P1X|P1Y|P2X|P2Y} {<Value>}
      :AUX<x>:LSCale:CALCulate:{P1X|P1Y|P2X|P2Y}?

파라미터:
  P1X, P1Y = 포인트 1 좌표
  P2X, P2Y = 포인트 2 좌표
  <Value> = -1.000E+12 to 1.000E+12

예제:
  :AUX1:LSCALE:CALCULATE:P1X 0
  :AUX1:LSCALE:CALCULATE:P1X?  → :AUX1:LSCALE:CALCULATE:P1X 0.000E+00
```

### :AUX<x>:LSCale:CALCulate:EXECute
**설명:** 보조 입력 선형 스케일의 파라미터를 계산합니다.

```
문법: :AUX<x>:LSCale:CALCulate:EXECute

예제:
  :AUX1:LSCALE:CALCULATE:EXECUTE

주의: 이전에 설정한 P1X, P1Y, P2X, P2Y 데이터를 사용하여
      기울기(A)와 오프셋(B)을 계산하고 자동으로 설정합니다.
```

### :AUX<x>:NAME
**설명:** 보조 입력의 이름을 설정하거나 조회합니다.

```
문법: :AUX<x>:NAME {<String>}
      :AUX<x>:NAME?

파라미터:
  <String> = 최대 8자

예제:
  :AUX1:NAME "AUX1"
  :AUX1:NAME?  → :AUX1:NAME "AUX1"
```

### :AUX<x>:RANGe
**설명:** 보조 입력의 전압 범위를 설정하거나 조회합니다.

```
문법: :AUX<x>:RANGe {<Voltage>}
      :AUX<x>:RANGe?

파라미터:
  <Voltage> = 50mV, 100mV, 200mV, 500mV, 1V, 2V, 5V, 10V, 20V

예제:
  :AUX1:RANGE 20V
  :AUX1:RANGE?  → :AUX1:RANGE 20.00E+00
```

### :AUX<x>:SCALing
**설명:** 보조 입력의 스케일링 계수를 설정하거나 조회합니다.

```
문법: :AUX<x>:SCALing {<Value>}
      :AUX<x>:SCALing?

파라미터:
  <Value> = 0.0001 to 99999.9999

예제:
  :AUX1:SCALING 1
  :AUX1:SCALING?  → :AUX1:SCALING 1.0000
```

### :AUX<x>:UNIT
**설명:** 보조 입력에 할당할 단위를 설정하거나 조회합니다.

```
문법: :AUX<x>:UNIT {<String>}
      :AUX<x>:UNIT?

파라미터:
  <String> = 최대 8자

예제:
  :AUX1:UNIT "kW/m2"
  :AUX1:UNIT?  → :AUX1:UNIT "kW/m2"

주의: 이 명령은 계산 결과에 영향을 주지 않습니다 (표시 목적만).
```

---

## 3. COMMunicate Group

통신 제어 명령

### :COMMunicate?
**설명:** 모든 통신 설정을 조회합니다.

```
문법: :COMMunicate?
```

### :COMMunicate:HEADer
**설명:** 쿼리에 대한 응답에 헤더를 추가할지 여부를 설정하거나 조회합니다.

```
문법: :COMMunicate:HEADer {ON|OFF}
      :COMMunicate:HEADer?

예제 (헤더 포함):
  :COMMUNICATE:HEADER ON
  명령: :DISPLAY:MODE?
  응답: :DISPLAY:MODE NUMERIC

예제 (헤더 미포함):
  :COMMUNICATE:HEADER OFF
  명령: :DISPLAY:MODE?
  응답: NUMERIC
```

### :COMMunicate:LOCKout
**설명:** 로컬 잠금을 설정하거나 해제합니다.

```
문법: :COMMunicate:LOCKout {ON|OFF}
      :COMMunicate:LOCKout?

예제:
  :COMMUNICATE:LOCKOUT ON
  :COMMUNICATE:LOCKOUT?  → :COMMUNICATE:LOCKOUT 1

주의: ON일 때 LOCAL 키를 사용해도 로컬 모드로 전환되지 않습니다.
```

### :COMMunicate:OPSE
**설명:** *OPC, *OPC?, *WAI 명령에 사용할 오버랩 명령을 설정하거나 조회합니다.

```
문법: :COMMunicate:OPSE <Register>
      :COMMunicate:OPSE?

파라미터:
  <Register> = 0 to 65535 (비트 패턴)

예제:
  :COMMUNICATE:OPSE 65535
  :COMMUNICATE:OPSE?  → :COMMUNICATE:OPSE 96

비트 정의:
  Bit 5 (PRN) = 내장 프린터 작업
  Bit 6 (ACS) = 저장 매체 접근
```

### :COMMunicate:OPSR?
**설명:** 작업 대기 상태 레지스터를 조회합니다.

```
문법: :COMMunicate:OPSR?

응답:
  0 = 모든 작업 완료
  Bit 5 설정 = 프린터 작업 진행 중
  Bit 6 설정 = 저장 매체 접근 중

예제:
  :COMMUNICATE:OPSR?  → 0
```

### :COMMunicate:OVERlap
**설명:** 오버랩 명령으로 작동할 명령들을 설정하거나 조회합니다.

```
문법: :COMMunicate:OVERlap <Register>
      :COMMunicate:OVERlap?

파라미터:
  <Register> = 0 to 65535

예제:
  :COMMUNICATE:OVERLAP 65535
  :COMMUNICATE:OVERLAP?  → :COMMUNICATE:OVERLAP 96
```

### :COMMunicate:REMote
**설명:** WT1800을 원격 모드(ON) 또는 로컬 모드(OFF)로 설정합니다.

```
문법: :COMMunicate:REMote {ON|OFF}
      :COMMunicate:REMote?

예제:
  :COMMUNICATE:REMOTE ON
  :COMMUNICATE:REMOTE?  → :COMMUNICATE:REMOTE 1

상태:
  ON (1) = 원격 모드 - 모든 키 사용 불가 (LOCAL 키 제외)
  OFF (0) = 로컬 모드 - 모든 키 사용 가능
```

### :COMMunicate:VERBose
**설명:** 쿼리 응답을 완전하게(VERBOSE) 또는 약자로(COMPACT) 반환할지 설정합니다.

```
문법: :COMMunicate:VERBose {ON|OFF}
      :COMMunicate:VERBose?

예제 (VERBOSE ON):
  :COMMUNICATE:VERBOSE ON
  명령: :NUMERIC:VALUE?
  응답: :NUMERIC:NORMAL:VALUE 123.45

예제 (VERBOSE OFF):
  :COMMUNICATE:VERBOSE OFF
  명령: :NUMERIC:VALUE?
  응답: 123.45
```

### :COMMunicate:WAIT
**설명:** 지정된 확장 이벤트가 발생할 때까지 대기합니다.

```
문법: :COMMunicate:WAIT <Register>

파라미터:
  <Register> = 0 to 65535 (확장 이벤트 레지스터)

예제:
  :COMMUNICATE:WAIT 1  (비트 0이 설정될 때까지 대기)

사용 사례: 데이터 동기화
  :COMMUNICATE:WAIT 1
  :NUMERIC:NORMAL:VALUE?  (측정 완료 후에만 실행)
```

### :COMMunicate:WAIT?
**설명:** 지정된 확장 이벤트가 발생했을 때 응답을 생성합니다.

```
문법: :COMMunicate:WAIT? <Register>

파라미터:
  <Register> = 0 to 65535

예제:
  :COMMUNICATE:WAIT? 65535  → 1
```

---

## 4. CURSor Group

커서 측정 명령

### :CURSor?
**설명:** 모든 커서 측정 설정을 조회합니다.

```
문법: :CURSor?
```

### :CURSor:BAR?
**설명:** 모든 막대 그래프 커서 측정 설정을 조회합니다.

```
문법: :CURSor:BAR?

주의: 고조파 측정 옵션 (/G5 또는 /G6)이 필요합니다.
```

### :CURSor:BAR:LINKage
**설명:** 막대 그래프의 커서 위치 연결을 설정하거나 조회합니다.

```
문법: :CURSor:BAR:LINKage {ON|OFF}
      :CURSor:BAR:LINKage?

예제:
  :CURSOR:BAR:LINKAGE OFF
  :CURSOR:BAR:LINKAGE?  → :CURSOR:BAR:LINKAGE 0
```

### :CURSor:BAR:POSition<x>
**설명:** 막대 그래프의 지정된 커서 위치를 설정하거나 조회합니다.

```
문법: :CURSor:BAR:POSition<x> {<Value>}
      :CURSor:BAR:POSition<x>?

파라미터:
  <x> = 1 or 2 (커서 번호)
  <Value> = 0 to 500

예제:
  :CURSOR:BAR:POSITION1 1
  :CURSOR:BAR:POSITION1?  → :CURSOR:BAR:POSITION1 1
```

### :CURSor:BAR[:STATe]
**설명:** 막대 그래프 커서 표시를 켜거나 끕니다.

```
문법: :CURSor:BAR[:STATe] {ON|OFF}
      :CURSor:BAR:STATe?

예제:
  :CURSOR:BAR:STATE ON
  :CURSOR:BAR:STATE?  → :CURSOR:BAR:STATE 1
```

### :CURSor:BAR:{Y<x>|DY}?
**설명:** 막대 그래프 커서의 측정값을 조회합니다.

```
문법: :CURSor:BAR:{Y1|Y2|Y3|DY1|DY2|DY3}?

파라미터:
  Y1, Y2, Y3 = 커서 위치의 Y축 값
  DY1, DY2, DY3 = 커서 간의 Y축 차이

예제:
  :CURSOR:BAR:Y1?  → 78.628E+00

주의: 커서 표시가 꺼져있으면 NAN이 반환됩니다.
```

### :CURSor:TRENd?
**설명:** 모든 추세 그래프 커서 측정 설정을 조회합니다.

```
문법: :CURSor:TRENd?
```

### :CURSor:TRENd:LINKage
**설명:** 추세 그래프의 커서 위치 연결을 설정하거나 조회합니다.

```
문법: :CURSor:TRENd:LINKage {ON|OFF}
      :CURSor:TRENd:LINKage?

예제:
  :CURSOR:TREND:LINKAGE OFF
  :CURSOR:TREND:LINKAGE?  → :CURSOR:TREND:LINKAGE 0
```

### :CURSor:TRENd:POSition<x>
**설명:** 추세 그래프의 지정된 커서 위치를 설정하거나 조회합니다.

```
문법: :CURSor:TRENd:POSition<x> {<Value>}
      :CURSor:TRENd:POSition<x>?

파라미터:
  <x> = 1 or 2
  <Value> = 0 to 1601

예제:
  :CURSOR:TREND:POSITION1 160
  :CURSOR:TREND:POSITION1?  → :CURSOR:TREND:POSITION1 160
```

### :CURSor:TRENd[:STATe]
**설명:** 추세 그래프 커서 표시를 설정합니다.

```
문법: :CURSor:TRENd[:STATe] {ON|OFF}
      :CURSor:TRENd:STATe?

예제:
  :CURSOR:TREND:STATE ON
  :CURSOR:TREND:STATE?  → :CURSOR:TREND:STATE 1
```

### :CURSor:TRENd:TRACe<x>
**설명:** 추세 그래프 커서의 대상을 설정하거나 조회합니다.

```
문법: :CURSor:TRENd:TRACe<x> {<Value>}
      :CURSor:TRENd:TRACe<x>?

파라미터:
  <x> = 1 or 2 (커서)
  <Value> = 1 to 16 (T1 to T16)

예제:
  :CURSOR:TREND:TRACE1 1
  :CURSOR:TREND:TRACE1?  → :CURSOR:TREND:TRACE1 1
```

### :CURSor:TRENd:{X<x>|Y<x>|DY}?
**설명:** 추세 그래프 커서의 측정값을 조회합니다.

```
문법: :CURSor:TRENd:{X1|X2|Y1|Y2|DY}?

파라미터:
  X1, X2 = 커서 위치의 시간 (문자열)
  Y1, Y2 = Y축 값
  DY = Y축 차이

예제:
  :CURSOR:TREND:X1?  → "2010/01/01 12:34:56"
  :CURSOR:TREND:Y1?  → 78.628E+00

주의: 커서가 꺼져있으면:
  X<x>: "****/**/** **:**:**"
  Y<x>, DY: NAN
```

### :CURSor:WAVE?
**설명:** 모든 파형 그래프 커서 측정 설정을 조회합니다.

```
문법: :CURSor:WAVE?
```

### :CURSor:WAVE:LINKage
**설명:** 파형 그래프의 커서 위치 연결을 설정합니다.

```
문법: :CURSor:WAVE:LINKage {ON|OFF}
      :CURSor:WAVE:LINKage?

예제:
  :CURSOR:WAVE:LINKAGE OFF
  :CURSOR:WAVE:LINKAGE?  → :CURSOR:WAVE:LINKAGE 0
```

### :CURSor:WAVE:PATH
**설명:** 파형 그래프의 커서 경로를 설정합니다.

```
문법: :CURSor:WAVE:PATH {MAX|MIN|MID}
      :CURSor:WAVE:PATH?

파라미터:
  MAX = 최대 경로
  MIN = 최소 경로
  MID = 중간 경로

예제:
  :CURSOR:WAVE:PATH MAX
  :CURSOR:WAVE:PATH?  → :CURSOR:WAVE:PATH MAX
```

### :CURSor:WAVE:POSition<x>
**설명:** 파형 그래프의 지정된 커서 위치를 설정합니다.

```
문법: :CURSor:WAVE:POSition<x> {<Value>}
      :CURSor:WAVE:POSition<x>?

파라미터:
  <x> = 1 or 2
  <Value> = 0 to 800

예제:
  :CURSOR:WAVE:POSITION1 160
  :CURSOR:WAVE:POSITION1?  → :CURSOR:WAVE:POSITION1 160
```

### :CURSor:WAVE[:STATe]
**설명:** 파형 그래프 커서 표시를 설정합니다.

```
문법: :CURSor:WAVE[:STATe] {ON|OFF}
      :CURSor:WAVE:STATe?

예제:
  :CURSOR:WAVE:STATE ON
  :CURSOR:WAVE:STATE?  → :CURSOR:WAVE:STATE 1
```

### :CURSor:WAVE:TRACe<x>
**설명:** 파형 그래프 커서의 대상을 설정합니다.

```
문법: :CURSor:WAVE:TRACe<x> {U<x>|I<x>|SPEed|TORQue|AUX<x>}
      :CURSor:WAVE:TRACe<x>?

파라미터:
  <x> (TRACe) = 1 or 2 (커서)
  <x> (U/I) = 1 to 6 (요소)
  <x> (AUX) = 1 or 2 (보조 입력)

예제:
  :CURSOR:WAVE:TRACE1 U1
  :CURSOR:WAVE:TRACE1?  → :CURSOR:WAVE:TRACE1 U1
```

### :CURSor:WAVE:{X<x>|DX|PERDt|Y<x>|DY}?
**설명:** 파형 그래프 커서의 측정값을 조회합니다.

```
문법: :CURSor:WAVE:{X1|X2|DX|PERDt|Y1|Y2|DY}?

파라미터:
  X1, X2 = 커서 X축 위치
  DX = X축 차이
  PERDt = 1/DX 값 (주파수)
  Y1, Y2 = Y축 값
  DY = Y축 차이

예제:
  :CURSOR:WAVE:Y1?  → 78.628E+00

주의: 커서가 꺼져있으면 NAN이 반환됩니다.
```

---

## 5. DISPlay Group

디스플레이 설정 명령

### :DISPlay?
**설명:** 모든 디스플레이 설정을 조회합니다.

```
문법: :DISPlay?
응답: 현재 디스플레이 모드의 모든 설정
```

### :DISPlay:MODE
**설명:** 디스플레이 모드를 설정하거나 조회합니다.

```
문법: :DISPlay:MODE {<Mode>}
      :DISPlay:MODE?

가능한 모드:
  NUMERIC = 수치 표시
  WAVE = 파형 표시
  TRENd = 추세 표시
  BAR = 막대 그래프 표시 (옵션: /G5, /G6)
  VECTor = 벡터 표시 (옵션: /G5, /G6)
  HSPeed = 고속 데이터 캡처 표시 (옵션: /HS)
  NWAVe = 수치+파형 표시
  NTRend = 수치+추세 표시
  NBAR = 수치+막대 표시
  WTRend = 파형+추세 표시

예제:
  :DISPLAY:MODE NUMERIC
  :DISPLAY:MODE?  → :DISPLAY:MODE NUMERIC
```

### :DISPlay:NUMeric?
**설명:** 모든 수치 표시 설정을 조회합니다.

```
문법: :DISPlay:NUMeric?
```

### :DISPlay:NUMeric:FRAMe
**설명:** 수치 표시의 데이터 섹션 프레임을 설정합니다.

```
문법: :DISPlay:NUMeric:FRAMe {ON|OFF}
      :DISPlay:NUMeric:FRAMe?

예제:
  :DISPLAY:NUMERIC:FRAME ON
  :DISPLAY:NUMERIC:FRAME?  → :DISPLAY:NUMERIC:FRAME 1
```

### :DISPlay:TRENd?
**설명:** 모든 추세 표시 설정을 조회합니다.

```
문법: :DISPlay:TRENd?
```

### :DISPlay:TRENd:ITEM<x>
**설명:** 추세 항목을 설정하거나 조회합니다.

```
문법: :DISPlay:TRENd:ITEM<x> {<Function>,<Element>}
      :DISPlay:TRENd:ITEM<x>?

파라미터:
  <x> = 1 to 16 (추세 번호)
  <Function> = {U|I|P|S|Q|...}
  <Element> = 1 to 6

예제:
  :DISPLAY:TREND:ITEM1 U,1
  :DISPLAY:TREND:ITEM1?  → :DISPLAY:TREND:ITEM1 U,1
```

### :DISPlay:WAVE?
**설명:** 모든 파형 표시 설정을 조회합니다.

```
문법: :DISPlay:WAVE?
```

### :DISPlay:WAVE:TRIGger?
**설명:** 모든 트리거 설정을 조회합니다.

```
문법: :DISPlay:WAVE:TRIGger?
```

### :DISPlay:WAVE:TRIGger:MODE
**설명:** 파형 트리거 모드를 설정합니다.

```
문법: :DISPlay:WAVE:TRIGger:MODE {<Mode>}
      :DISPlay:WAVE:TRIGger:MODE?

파라미터:
  <Mode> = 트리거 모드

예제:
  :DISPLAY:WAVE:TRIGGER:MODE AUTO
```

---

## 6. FILE Group

파일 작업 명령

### :FILE?
**설명:** 모든 파일 작업 설정을 조회합니다.

```
문법: :FILE?
```

### :FILE:CDIRectory
**설명:** 현재 디렉토리를 변경합니다.

```
문법: :FILE:CDIRectory {<Path>}

파라미터:
  <Path> = 디렉토리 경로
  ".." = 상위 디렉토리로 이동

예제:
  :FILE:CDIRECTORY "DATA"
  :FILE:CDIRECTORY ".."  (상위 디렉토리)
```

### :FILE:DRIVe
**설명:** 현재 드라이브를 설정합니다.

```
문법: :FILE:DRIVe {<Drive>}

파라미터:
  <Drive> = 드라이브 문자 또는 이름

예제:
  :FILE:DRIVE "C:"
```

### :FILE:FREE?
**설명:** 현재 드라이브의 남은 공간을 조회합니다.

```
문법: :FILE:FREE?

응답: 바이트 단위의 남은 공간

예제:
  :FILE:FREE?  → 1073741824  (1GB)
```

### :FILE:LOAD:SETup
**설명:** 설정 파일을 로드합니다.

```
문법: :FILE:LOAD:SETup {<Filename>}

파라미터:
  <Filename> = 파일 이름 (확장자 포함)

예제:
  :FILE:LOAD:SETUP "CONFIG1.SET"

주의: 오버랩 명령입니다 - *WAI 또는 *OPC 사용 권장
```

### :FILE:PATH?
**설명:** 현재 디렉토리의 절대 경로를 조회합니다.

```
문법: :FILE:PATH?

응답: 절대 경로 (문자열)

예제:
  :FILE:PATH?  → "D:\\DATA"
```

### :FILE:SAVE:SETup
**설명:** 설정을 파일에 저장합니다.

```
문법: :FILE:SAVE:SETup

예제:
  :FILE:SAVE:SETUP

주의: 오버랩 명령입니다 - *WAI 또는 *OPC 사용 권장
```

### :FILE:SAVE:NUMeric
**설명:** 수치 데이터를 파일에 저장합니다.

```
문법: :FILE:SAVE:NUMeric[:EXECute]

예제:
  :FILE:SAVE:NUMERIC

주의: 오버랩 명령입니다 - *WAI 또는 *OPC 사용 권장
```

### :FILE:SAVE:WAVE
**설명:** 파형 데이터를 파일에 저장합니다.

```
문법: :FILE:SAVE:WAVE[:EXECute]

예제:
  :FILE:SAVE:WAVE

주의: 오버랩 명령입니다 - *WAI 또는 *OPC 사용 권장
```

---

## 7. HARMonics Group

고조파 분석 명령 (옵션: /G5, /G6)

### :HARMonics<x>?
**설명:** 모든 고조파 측정 설정을 조회합니다.

```
문법: :HARMonics<x>?
파라미터: <x> = 요소 번호
```

### :HARMonics<x>:CONFigure?
**설명:** 고조파 측정 그룹을 조회합니다.

```
문법: :HARMonics<x>:CONFigure?
```

### :HARMonics<x>:ORDer
**설명:** 분석할 최대/최소 고조파 차수를 설정합니다.

```
문법: :HARMonics<x>:ORDer {<Min>,<Max>}
      :HARMonics<x>:ORDer?

파라미터:
  <Min> = 0 to 490
  <Max> = 10 to 500 (최소보다 10 이상 커야 함)

예제:
  :HARMONICS1:ORDER 1,100
  :HARMONICS1:ORDER?  → 1,100
```

### :HARMonics<x>:PLLSource
**설명:** PLL 소스를 설정합니다.

```
문법: :HARMonics<x>:PLLSource {<Source>}
      :HARMonics<x>:PLLSource?
```

### :HARMonics<x>:THD
**설명:** THD(Total Harmonic Distortion) 계산 방정식을 설정합니다.

```
문법: :HARMonics<x>:THD {<Formula>}
      :HARMonics<x>:THD?

파라미터:
  <Formula> = THD 계산 방식
```

---

## 8. HCOPy Group

인쇄 설정 명령

### :HCOPy?
**설명:** 모든 인쇄 설정을 조회합니다.

```
문법: :HCOPy?
```

### :HCOPy:EXECute
**설명:** 인쇄 작업을 실행합니다.

```
문법: :HCOPy:EXECute

예제:
  :HCOPY:EXECUTE

주의: 오버랩 명령입니다
```

### :HCOPy:AUTO:STARt
**설명:** 자동 인쇄 시작을 설정합니다.

```
문법: :HCOPy:AUTO:STARt {ON|OFF}
      :HCOPy:AUTO:STARt?
```

---

## 9. HOLD Group

데이터 홀드 명령

### :HOLD
**설명:** 디스플레이 및 통신의 출력 홀드 기능을 설정합니다.

```
문법: :HOLD {ON|OFF}
      :HOLD?

예제:
  :HOLD ON
  :HOLD?  → 1
```

---

## 10. HSPeed Group

고속 데이터 캡처 명령 (옵션: /HS)

### :HSPeed?
**설명:** 모든 고속 데이터 캡처 설정을 조회합니다.

```
문법: :HSPeed?
```

### :HSPeed:STARt
**설명:** 데이터 캡처를 시작합니다.

```
문법: :HSPeed:STARt

예제:
  :HSPEED:START
```

### :HSPeed:STOP
**설명:** 데이터 캡처를 중지합니다.

```
문법: :HSPeed:STOP

예제:
  :HSPEED:STOP
```

### :HSPeed:STATe?
**설명:** 고속 데이터 캡처 상태를 조회합니다.

```
문법: :HSPeed:STATe?

응답:
  0 = 정지됨
  1 = 캡처 중
  2 = 준비 완료

예제:
  :HSPEED:STATE?  → 1
```

### :HSPeed:COUNt
**설명:** 데이터 캡처 횟수를 설정합니다.

```
문법: :HSPeed:COUNt {<Value>}
      :HSPeed:COUNt?

파라미터:
  <Value> = 캡처 횟수

예제:
  :HSPEED:COUNT 100
  :HSPEED:COUNT?  → 100
```

### :HSPeed:CAPTured?
**설명:** 수행된 캡처 횟수를 조회합니다.

```
문법: :HSPeed:CAPTured?

응답: 현재 캡처 횟수

예제:
  :HSPEED:CAPTURED?  → 50
```

---

## 11. IMAGe Group

화면 이미지 저장 명령

### :IMAGe?
**설명:** 모든 화면 이미지 설정을 조회합니다.

```
문법: :IMAGe?
```

### :IMAGe:EXECute
**설명:** 화면 이미지 저장을 실행합니다.

```
문법: :IMAGe:EXECute

예제:
  :IMAGE:EXECUTE

주의: 오버랩 명령입니다 - *WAI 또는 *OPC 사용 권장
```

### :IMAGe:FORMat
**설명:** 이미지 저장 형식을 설정합니다.

```
문법: :IMAGe:FORMat {BMP|PNG|JPEG}
      :IMAGe:FORMat?

예제:
  :IMAGE:FORMAT PNG
  :IMAGE:FORMAT?  → :IMAGE:FORMAT PNG
```

### :IMAGe:SAVE:NAME
**설명:** 저장할 파일 이름을 설정합니다.

```
문법: :IMAGe:SAVE:NAME {<Filename>}
      :IMAGe:SAVE:NAME?

파라미터:
  <Filename> = 확장자 제외

예제:
  :IMAGE:SAVE:NAME "SCREEN01"
  :IMAGE:SAVE:NAME?  → :IMAGE:SAVE:NAME "SCREEN01"
```

---

## 12. INPut Group

입력 설정 명령

### [:INPut]?
**설명:** 모든 입력 설정을 조회합니다.

```
문법: [:INPut]?
```

### [:INPut]:VOLTage?
**설명:** 모든 전압 측정 설정을 조회합니다.

```
문법: [:INPut]:VOLTage?
```

### [:INPut]:VOLTage:RANGe?
**설명:** 모든 요소의 전압 범위를 조회합니다.

```
문법: [:INPut]:VOLTage:RANGe?

응답: 각 요소의 범위
```

### [:INPut]:VOLTage:RANGe[:ALL]
**설명:** 모든 요소의 전압 범위를 설정합니다.

```
문법: [:INPut]:VOLTage:RANGe[:ALL] {<Range>}

파라미터:
  <Range> = 5V, 10V, 15V, 20V, 25V, 50V, 100V, 150V, 200V, 250V, 500V, 750V, 1000V

예제:
  :INPUT:VOLTAGE:RANGE 100V
  :INPUT:VOLTAGE:RANGE?  → :INPUT:VOLTAGE:RANGE 100V
```

### [:INPut]:VOLTage:RANGe:ELEMent<x>
**설명:** 지정된 요소의 전압 범위를 설정합니다.

```
문법: [:INPut]:VOLTage:RANGe:ELEMent<x> {<Range>}
      [:INPut]:VOLTage:RANGe:ELEMent<x>?

파라미터:
  <x> = 1 to 6 (요소)
  <Range> = 5V, 10V, 15V, 20V, 25V, 50V, 100V, 150V, 200V, 250V, 500V, 750V, 1000V

예제:
  :INPUT:VOLTAGE:RANGE:ELEMENT1 100V
  :INPUT:VOLTAGE:RANGE:ELEMENT1?  → :INPUT:VOLTAGE:RANGE:ELEMENT1 100V
```

### [:INPut]:VOLTage:AUTO?
**설명:** 모든 요소의 자동 범위 설정을 조회합니다.

```
문법: [:INPut]:VOLTage:AUTO?
```

### [:INPut]:VOLTage:AUTO[:ALL]
**설명:** 모든 요소의 자동 범위를 설정합니다.

```
문법: [:INPut]:VOLTage:AUTO[:ALL] {ON|OFF}
      [:INPut]:VOLTage:AUTO[:ALL]?

예제:
  :INPUT:VOLTAGE:AUTO ON
  :INPUT:VOLTAGE:AUTO?  → :INPUT:VOLTAGE:AUTO 1
```

### [:INPut]:VOLTage:AUTO:ELEMent<x>
**설명:** 지정된 요소의 자동 범위를 설정합니다.

```
문법: [:INPut]:VOLTage:AUTO:ELEMent<x> {ON|OFF}
      [:INPut]:VOLTage:AUTO:ELEMent<x>?

파라미터:
  <x> = 1 to 6

예제:
  :INPUT:VOLTAGE:AUTO:ELEMENT1 ON
  :INPUT:VOLTAGE:AUTO:ELEMENT1?  → :INPUT:VOLTAGE:AUTO:ELEMENT1 1
```

### [:INPut]:CURRent?
**설명:** 모든 전류 측정 설정을 조회합니다.

```
문법: [:INPut]:CURRent?
```

### [:INPut]:CURRent:RANGe?
**설명:** 모든 요소의 전류 범위를 조회합니다.

```
문법: [:INPut]:CURRent:RANGe?
```

### [:INPut]:CURRent:RANGe[:ALL]
**설명:** 모든 요소의 전류 범위를 설정합니다.

```
문법: [:INPut]:CURRent:RANGe[:ALL] {<Range>}

파라미터:
  <Range> = 5A, 10A, 15A, 20A, 25A, 50A, 100A

예제:
  :INPUT:CURRENT:RANGE 10A
  :INPUT:CURRENT:RANGE?  → :INPUT:CURRENT:RANGE 10A
```

### [:INPut]:CURRent:RANGe:ELEMent<x>
**설명:** 지정된 요소의 전류 범위를 설정합니다.

```
문법: [:INPut]:CURRent:RANGe:ELEMent<x> {<Range>}
      [:INPut]:CURRent:RANGe:ELEMent<x>?

파라미터:
  <x> = 1 to 6
  <Range> = 5A, 10A, 15A, 20A, 25A, 50A, 100A

예제:
  :INPUT:CURRENT:RANGE:ELEMENT1 10A
```

### [:INPut]:CURRent:AUTO?
**설명:** 모든 요소의 전류 자동 범위 설정을 조회합니다.

```
문법: [:INPut]:CURRent:AUTO?
```

### [:INPut]:CURRent:AUTO[:ALL]
**설명:** 모든 요소의 전류 자동 범위를 설정합니다.

```
문법: [:INPut]:CURRent:AUTO[:ALL] {ON|OFF}
      [:INPut]:CURRent:AUTO[:ALL]?

예제:
  :INPUT:CURRENT:AUTO ON
  :INPUT:CURRENT:AUTO?  → :INPUT:CURRENT:AUTO 1
```

### [:INPut]:WIRing
**설명:** 배선 시스템을 설정합니다.

```
문법: [:INPut]:WIRing {1PH2W|1PH3W|3PH3W|3PH4W}
      [:INPut]:WIRing?

파라미터:
  1PH2W = 1상 2선
  1PH3W = 1상 3선
  3PH3W = 3상 3선
  3PH4W = 3상 4선

예제:
  :INPUT:WIRING 3PH3W
  :INPUT:WIRING?  → :INPUT:WIRING 3PH3W
```

---

## 13. INTEGrate Group

적분 명령

### :INTEGrate?
**설명:** 모든 적분 설정을 조회합니다.

```
문법: :INTEGrate?
```

### :INTEGrate:STARt
**설명:** 적분을 시작합니다.

```
문법: :INTEGrate:STARt

예제:
  :INTEGRATE:START
```

### :INTEGrate:STOP
**설명:** 적분을 중지합니다.

```
문법: :INTEGrate:STOP

예제:
  :INTEGRATE:STOP
```

### :INTEGrate:STATe?
**설명:** 적분 상태를 조회합니다.

```
문법: :INTEGrate:STATe?

응답:
  0 = 중지됨
  1 = 적분 중
  2 = 준비 완료

예제:
  :INTEGRATE:STATE?  → 1
```

### :INTEGrate:RESet
**설명:** 적분값을 초기화합니다.

```
문법: :INTEGrate:RESet

예제:
  :INTEGRATE:RESET
```

### :INTEGrate:TIMer<x>
**설명:** 적분 타이머 값을 설정합니다.

```
문법: :INTEGrate:TIMer<x> {<Hours>,<Minutes>,<Seconds>}
      :INTEGrate:TIMer<x>?

파라미터:
  <x> = 타이머 번호
  시간, 분, 초

예제:
  :INTEGRATE:TIMER1 1,0,0
  :INTEGRATE:TIMER1?  → 1,0,0
```

### :INTEGrate:MODE
**설명:** 적분 모드를 설정합니다.

```
문법: :INTEGrate:MODE {TIMER|RealTime}
      :INTEGrate:MODE?

파라미터:
  TIMER = 타이머 적분
  RealTime = 실시간 적분

예제:
  :INTEGRATE:MODE TIMER
```

---

## 14. MEASure Group

측정 계산 명령

### :MEASure?
**설명:** 모든 측정 설정을 조회합니다.

```
문법: :MEASure?
```

### :MEASure:AVERaging?
**설명:** 모든 평균화 설정을 조회합니다.

```
문법: :MEASure:AVERaging?
```

### :MEASure:AVERaging:STATe
**설명:** 평균화 기능을 설정합니다.

```
문법: :MEASure:AVERaging:STATe {ON|OFF}
      :MEASure:AVERaging:STATe?

예제:
  :MEASURE:AVERAGING:STATE ON
  :MEASURE:AVERAGING:STATE?  → 1
```

### :MEASure:AVERaging:COUNt
**설명:** 평균화 계수를 설정합니다.

```
문법: :MEASure:AVERaging:COUNt {<Value>}
      :MEASure:AVERaging:COUNt?

파라미터:
  <Value> = 평균 처리 횟수

예제:
  :MEASURE:AVERAGING:COUNT 10
```

### :MEASure:SAMPling
**설명:** 샘플링 주파수를 설정합니다.

```
문법: :MEASure:SAMPling {<Frequency>}
      :MEASure:SAMPling?

파라미터:
  <Frequency> = 샘플링 주파수 (Hz)

예제:
  :MEASURE:SAMPLING 50000
```

### :MEASure:SYNChronize
**설명:** 동기 측정 모드를 설정합니다.

```
문법: :MEASure:SYNChronize {ON|OFF}
      :MEASure:SYNChronize?

예제:
  :MEASURE:SYNCHRONIZE ON
```

---

## 15. MOTor Group

모터 평가 명령 (옵션: /MTR)

### :MOTor?
**설명:** 모든 모터 평가 설정을 조회합니다.

```
문법: :MOTor?
```

### :MOTor:POLE
**설명:** 모터의 극 수를 설정합니다.

```
문법: :MOTor:POLE {<Value>}
      :MOTor:POLE?

파라미터:
  <Value> = 극의 수 (2, 4, 6, ...)

예제:
  :MOTOR:POLE 4
  :MOTOR:POLE?  → :MOTOR:POLE 4
```

### :MOTor:SPEed?
**설명:** 모든 회전 속도 설정을 조회합니다.

```
문법: :MOTor:SPEed?
```

### :MOTor:SPEed:TYPE
**설명:** 회전 속도 신호 입력 유형을 설정합니다.

```
문법: :MOTor:SPEed:TYPE {PULSE|ANALOG}
      :MOTor:SPEed:TYPE?

파라미터:
  PULSE = 펄스 입력
  ANALOG = 아날로그 입력

예제:
  :MOTOR:SPEED:TYPE PULSE
```

### :MOTor:SPEed:PULSe
**설명:** 회전 속도 신호(펄스)의 펄스 수를 설정합니다.

```
문법: :MOTor:SPEed:PULSe {<Value>}
      :MOTor:SPEed:PULSe?

파라미터:
  <Value> = 회전당 펄스 수

예제:
  :MOTOR:SPEED:PULSE 100
  :MOTOR:SPEED:PULSE?  → :MOTOR:SPEED:PULSE 100
```

### :MOTor:SPEed:UNIT
**설명:** 회전 속도에 추가할 단위를 설정합니다.

```
문법: :MOTor:SPEed:UNIT {<String>}
      :MOTor:SPEed:UNIT?

파라미터:
  <String> = 단위 (예: rpm, r/min)

예제:
  :MOTOR:SPEED:UNIT "rpm"
```

### :MOTor:TORQue?
**설명:** 모든 토크 설정을 조회합니다.

```
문법: :MOTor:TORQue?
```

### :MOTor:TORQue:TYPE
**설명:** 토크 신호 입력 유형을 설정합니다.

```
문법: :MOTor:TORQue:TYPE {PULSE|ANALOG}
      :MOTor:TORQue:TYPE?

예제:
  :MOTOR:TORQUE:TYPE ANALOG
```

### :MOTor:TORQue:UNIT
**설명:** 토크에 추가할 단위를 설정합니다.

```
문법: :MOTor:TORQue:UNIT {<String>}
      :MOTor:TORQue:UNIT?

파라미터:
  <String> = 단위 (예: Nm, kgf·m)

예제:
  :MOTOR:TORQUE:UNIT "Nm"
```

---

## 16. NUMeric Group

수치 데이터 명령

### :NUMeric?
**설명:** 모든 수치 데이터 출력 설정을 조회합니다.

```
문법: :NUMeric?
```

### :NUMeric:NORMal?
**설명:** 모든 수치 데이터 설정을 조회합니다.

```
문법: :NUMeric[:NORMal]?
```

### :NUMeric[:NORMal]:ITEM<x>
**설명:** 지정된 수치 데이터 출력 항목을 설정합니다.

```
문법: :NUMeric[:NORMal]:ITEM<x> {<Function>[,<Element>][,<Order>]}
      :NUMeric[:NORMal]:ITEM<x>?

파라미터:
  <x> = 1 to 200 (항목 번호)
  <Function> = {URMS|IRMS|P|S|Q|...}
  <Element> = {1-6|SIGMa|SIGMB|SIGMC}
  <Order> = {TOTal|DC|1-500}

예제:
  :NUMERIC:ITEM1 URMS,1
  :NUMERIC:ITEM1?  → :NUMERIC:ITEM1 URMS,1
```

### :NUMeric[:NORMal]:NUMber
**설명:** 전송할 수치 데이터 항목 수를 설정합니다.

```
문법: :NUMeric[:NORMal]:NUMber {<Value>}
      :NUMeric[:NORMal]:NUMber?

파라미터:
  <Value> = 1 to 200

예제:
  :NUMERIC:NUMBER 10
  :NUMERIC:NUMBER?  → :NUMERIC:NUMBER 10
```

### :NUMeric[:NORMal]:VALue?
**설명:** 수치 데이터를 조회합니다.

```
문법: :NUMeric[:NORMal]:VALue?

응답: 설정된 항목의 측정값들 (쉼표로 구분)

예제:
  :NUMERIC:VALUE?  → 100.0,200.0,50.0,100.0
```

### :NUMeric:FORMat
**설명:** 수치 데이터 형식을 설정합니다.

```
문법: :NUMeric:FORMat {ASCII|REAL}
      :NUMeric:FORMat?

파라미터:
  ASCII = 텍스트 형식
  REAL = 실수 형식 (REAL32 또는 REAL64)

예제:
  :NUMERIC:FORMAT ASCII
```

### :NUMeric:HOLD
**설명:** 수치 데이터 홀드를 설정합니다.

```
문법: :NUMeric:HOLD {ON|OFF}
      :NUMeric:HOLD?

예제:
  :NUMERIC:HOLD ON
  :NUMERIC:HOLD?  → 1
```

---

## 17. RATE Group

데이터 레이트 명령

### :RATE
**설명:** 데이터 업데이트 레이트를 설정합니다.

```
문법: :RATE {<Frequency>}
      :RATE?

파라미터:
  <Frequency> = 데이터 업데이트 주파수 (Hz)

예제:
  :RATE 50
  :RATE?  → 50
```

---

## 18. STATus Group

상태 보고 명령

### :STATus?
**설명:** 모든 통신 상태 설정을 조회합니다.

```
문법: :STATus?
```

### :STATus:CONDition?
**설명:** 조건 레지스터의 내용을 조회합니다.

```
문법: :STATus:CONDition?

응답: 상태 값 (정수)

예제:
  :STATUS:CONDITION?  → 0
```

### :STATus:ERRor?
**설명:** 마지막 오류의 코드와 메시지를 조회합니다.

```
문법: :STATus:ERRor?

응답: 오류 코드와 메시지

예제:
  :STATUS:ERROR?  → 0,"No error"
```

### :STATus:EESE
**설명:** 확장 이벤트 활성화 레지스터를 설정합니다.

```
문법: :STATus:EESE {<Register>}
      :STATus:EESE?

파라미터:
  <Register> = 0 to 65535

예제:
  :STATUS:EESE 1
```

### :STATus:EESR?
**설명:** 확장 이벤트 레지스터를 조회하고 클리어합니다.

```
문법: :STATus:EESR?

응답: 확장 이벤트 레지스터 값

예제:
  :STATUS:EESR?  → 1
```

### :STATus:FILTer<x>
**설명:** 전이 필터를 설정합니다.

```
문법: :STATus:FILTer<x> {RISE|FALL}
      :STATus:FILTer<x>?

파라미터:
  <x> = 필터 번호
  RISE = 상승 엣지 감지
  FALL = 하강 엣지 감지

예제:
  :STATUS:FILTER1 FALL
```

---

## 19. STORe Group

데이터 저장 명령

### :STORe?
**설명:** 모든 데이터 저장 설정을 조회합니다.

```
문법: :STORe?
```

### :STORe:STARt
**설명:** 데이터 저장을 시작합니다.

```
문법: :STORe:STARt

예제:
  :STORE:START
```

### :STORe:STOP
**설명:** 데이터 저장을 중지합니다.

```
문법: :STORe:STOP

예제:
  :STORE:STOP
```

### :STORe:STATe?
**설명:** 데이터 저장 상태를 조회합니다.

```
문법: :STORe:STATe?

응답:
  0 = 중지됨
  1 = 저장 중
  2 = 준비 완료

예제:
  :STORE:STATE?  → 1
```

### :STORe:RESet
**설명:** 저장 기능을 초기화합니다.

```
문법: :STORe:RESet

예제:
  :STORE:RESET
```

### :STORe:INTerval
**설명:** 저장 간격을 설정합니다.

```
문법: :STORe:INTerval {<Seconds>}
      :STORe:INTerval?

파라미터:
  <Seconds> = 저장 간격 (초)

예제:
  :STORE:INTERVAL 1
  :STORE:INTERVAL?  → 1
```

---

## 20. SYSTem Group

시스템 설정 명령

### :SYSTem?
**설명:** 모든 시스템 설정을 조회합니다.

```
문법: :SYSTem?
```

### :SYSTem:DATE
**설명:** 날짜를 설정하거나 조회합니다.

```
문법: :SYSTem:DATE {YYYY,MM,DD}
      :SYSTem:DATE?

파라미터:
  YYYY = 연도 (2000-2099)
  MM = 월 (1-12)
  DD = 일 (1-31)

예제:
  :SYSTEM:DATE 2024,11,15
  :SYSTEM:DATE?  → 2024,11,15
```

### :SYSTem:TIME
**설명:** 시간을 설정하거나 조회합니다.

```
문법: :SYSTem:TIME {HH,MM,SS}
      :SYSTem:TIME?

파라미터:
  HH = 시간 (0-23)
  MM = 분 (0-59)
  SS = 초 (0-59)

예제:
  :SYSTEM:TIME 12,30,45
  :SYSTEM:TIME?  → 12,30,45
```

### :SYSTem:MODel?
**설명:** 모델 코드를 조회합니다.

```
문법: :SYSTem:MODel?

응답: 모델 코드

예제:
  :SYSTEM:MODEL?  → WT1800
```

### :SYSTem:SERial?
**설명:** 시리얼 번호를 조회합니다.

```
문법: :SYSTem:SERial?

응답: 시리얼 번호

예제:
  :SYSTEM:SERIAL?  → SN123456
```

### :SYSTem:LANGuage:MENU
**설명:** 메뉴 언어를 설정합니다.

```
문법: :SYSTem:LANGuage:MENU {English|Japanese|Chinese|...}
      :SYSTem:LANGuage:MENU?

예제:
  :SYSTEM:LANGUAGE:MENU English
```

---

## 21. WAVeform Group

파형 데이터 명령

### :WAVeform?
**설명:** 모든 파형 설정을 조회합니다.

```
문법: :WAVeform?
```

### :WAVeform:TRACe
**설명:** 파형 데이터 대상을 설정합니다.

```
문법: :WAVeform:TRACe {U<x>|I<x>}
      :WAVeform:TRACe?

파라미터:
  <x> = 1 to 6 (요소)

예제:
  :WAVEFORM:TRACE U1
  :WAVEFORM:TRACE?  → U1
```

### :WAVeform:SEND?
**설명:** 파형 데이터를 조회합니다.

```
문법: :WAVeform:SEND?

응답: 파형 데이터 (바이너리 또는 텍스트 형식)
```

### :WAVeform:STARt
**설명:** 파형 데이터의 시작점을 설정합니다.

```
문법: :WAVeform:STARt {<Point>}
      :WAVeform:STARt?

파라미터:
  <Point> = 시작점 인덱스

예제:
  :WAVEFORM:START 0
```

### :WAVeform:END
**설명:** 파형 데이터의 끝점을 설정합니다.

```
문법: :WAVeform:END {<Point>}
      :WAVeform:END?

파라미터:
  <Point> = 끝점 인덱스

예제:
  :WAVEFORM:END 10000
```

### :WAVeform:LENGth?
**설명:** 파형의 총 포인트 수를 조회합니다.

```
문법: :WAVeform:LENGth?

응답: 포인트 수

예제:
  :WAVEFORM:LENGTH?  → 10000
```

### :WAVeform:FORMat
**설명:** 파형 데이터 형식을 설정합니다.

```
문법: :WAVeform:FORMat {ASCII|REAL}
      :WAVeform:FORMat?

파라미터:
  ASCII = 텍스트 형식
  REAL = 실수 형식

예제:
  :WAVEFORM:FORMAT ASCII
```

---

## 22. Common Commands

IEEE 488.2 표준 공통 명령

### *IDN?
**설명:** 기기 정보를 조회합니다.

```
문법: *IDN?

응답: 제조사,모델,시리얼번호,펌웨어

예제:
  *IDN?  → YOKOGAWA,WT1800,SN123456,V1.0
```

### *RST
**설명:** 기기를 초기화합니다.

```
문법: *RST

예제:
  *RST
```

### *CLS
**설명:** 표준/확장 이벤트 레지스터 및 오류 큐를 클리어합니다.

```
문법: *CLS

예제:
  *CLS
```

### *OPC
**설명:** 지정된 오버랩 명령 완료 시 OPC 비트를 1로 설정합니다.

```
문법: *OPC

예제:
  :FILE:LOAD:SETUP "CONFIG1"
  *OPC
```

### *OPC?
**설명:** 지정된 오버랩 명령이 완료되었으면 1을 반환합니다.

```
문법: *OPC?

응답: 0 또는 1

예제:
  :FILE:LOAD:SETUP "CONFIG1"
  *OPC?  → 1 (완료됨)
```

### *WAI
**설명:** 지정된 오버랩 명령 완료까지 다음 명령 실행을 대기합니다.

```
문법: *WAI

예제:
  :FILE:LOAD:SETUP "CONFIG1"
  *WAI
  :NUMERIC:VALUE?  (파일 로드 완료 후 실행)
```

### *ESE
**설명:** 표준 이벤트 활성화 레지스터를 설정합니다.

```
문법: *ESE {<Register>}
      *ESE?

파라미터:
  <Register> = 0 to 255

예제:
  *ESE 1
  *ESE?  → 1
```

### *ESR?
**설명:** 표준 이벤트 레지스터를 조회하고 클리어합니다.

```
문법: *ESR?

응답: 레지스터 값 (0-255)

예제:
  *ESR?  → 0
```

### *SRE
**설명:** 서비스 요청 활성화 레지스터를 설정합니다.

```
문법: *SRE {<Register>}
      *SRE?

파라미터:
  <Register> = 0 to 255

예제:
  *SRE 32
  *SRE?  → 32
```

### *STB?
**설명:** 상태 바이트 레지스터를 조회합니다.

```
문법: *STB?

응답: 상태 바이트 (0-255)

예제:
  *STB?  → 0
```

### *TRG
**설명:** 단일 측정을 실행합니다.

```
문법: *TRG

예제:
  *TRG
```

### *TST?
**설명:** 자체 검사를 수행하고 결과를 반환합니다.

```
문법: *TST?

응답: 0 (정상) 또는 1 (오류)

예제:
  *TST?  → 0
```

### *CAL?
**설명:** 제로 캘리브레이션을 실행합니다.

```
문법: *CAL?

응답: 0 (성공) 또는 1 (실패)

예제:
  *CAL?  → 0

주의: 이는 SHIFT+CAL 키 누름과 동일합니다.
```

### *OPT?
**설명:** 설치된 옵션을 조회합니다.

```
문법: *OPT?

응답: 옵션 코드 (쉼표로 구분)

예제:
  *OPT?  → /G5,/MTR,/HS

옵션:
  /G5 = 고조파 분석 (5차까지)
  /G6 = 고조파 분석 (6차까지)
  /MTR = 모터 평가
  /HS = 고속 데이터 캡처
  /AUX = 보조 입력
  /DA = D/A 출력
```

---

## 🔧 사용 예제

### 1. 기본 연결 및 식별

```python
# 기기 연결
import socket

wt1800 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
wt1800.connect(("192.168.1.100", 5555))

# 기기 정보 조회
wt1800.sendall(b"*IDN?\n")
response = wt1800.recv(1024)
print(response.decode())  # YOKOGAWA,WT1800,SN123456,V1.0
```

### 2. 원격 모드 활성화

```python
# 원격 모드 설정
wt1800.sendall(b":COMMUNICATE:REMOTE ON\n")
wt1800.recv(1024)

# 헤더 제거
wt1800.sendall(b":COMMUNICATE:HEADER OFF\n")
wt1800.recv(1024)

# 장황한 모드 활성화
wt1800.sendall(b":COMMUNICATE:VERBOSE OFF\n")
wt1800.recv(1024)
```

### 3. 입력 설정

```python
# 배선 설정 (3상 3선)
wt1800.sendall(b":INPUT:WIRING 3PH3W\n")
wt1800.recv(1024)

# 전압 범위 설정 (100V)
wt1800.sendall(b":INPUT:VOLTAGE:RANGE 100V\n")
wt1800.recv(1024)

# 전류 범위 설정 (10A)
wt1800.sendall(b":INPUT:CURRENT:RANGE 10A\n")
wt1800.recv(1024)

# 자동 범위 활성화
wt1800.sendall(b":INPUT:VOLTAGE:AUTO ON\n")
wt1800.recv(1024)
```

### 4. 측정 항목 설정

```python
# 측정 항목 1: 전압 RMS (요소 1)
wt1800.sendall(b":NUMERIC:ITEM1 URMS,1\n")
wt1800.recv(1024)

# 측정 항목 2: 전류 RMS (요소 1)
wt1800.sendall(b":NUMERIC:ITEM2 IRMS,1\n")
wt1800.recv(1024)

# 측정 항목 3: 실전력 (요소 1)
wt1800.sendall(b":NUMERIC:ITEM3 P,1\n")
wt1800.recv(1024)

# 측정 항목 수 설정
wt1800.sendall(b":NUMERIC:NUMBER 3\n")
wt1800.recv(1024)
```

### 5. 측정값 읽기

```python
# 측정값 조회
wt1800.sendall(b":NUMERIC:VALUE?\n")
response = wt1800.recv(1024).decode()
values = response.split(',')
print(f"전압: {values[0]} V")
print(f"전류: {values[1]} A")
print(f"전력: {values[2]} W")
```

### 6. 설정 저장/로드

```python
# 설정 저장
wt1800.sendall(b":FILE:SAVE:SETUP\n")
wt1800.recv(1024)

# 설정 로드
wt1800.sendall(b":FILE:LOAD:SETUP \"CONFIG1\"\n")
wt1800.recv(1024)

# 대기
wt1800.sendall(b"*WAI\n")
wt1800.recv(1024)
```

### 7. 고속 데이터 캡처

```python
# 고속 캡처 설정 (옵션: /HS 필요)
wt1800.sendall(b":HSPEED:COUNT 100\n")
wt1800.recv(1024)

# 캡처 시작
wt1800.sendall(b":HSPEED:START\n")
wt1800.recv(1024)

# 완료 대기
while True:
    wt1800.sendall(b":HSPEED:STATE?\n")
    state = int(wt1800.recv(1024).decode().strip())
    if state == 0:  # 정지됨
        break
    time.sleep(0.1)
```

### 8. 오류 확인

```python
# 오류 확인
wt1800.sendall(b":STATUS:ERROR?\n")
response = wt1800.recv(1024).decode()
print(f"오류: {response}")

# 오류 큐 클리어
wt1800.sendall(b"*CLS\n")
wt1800.recv(1024)
```

---

## ⚡ 팁 & 주의사항

1. **오버랩 명령 대기**
   - FILE:LOAD:SETUP, FILE:SAVE:* 등은 오버랩 명령입니다.
   - 항상 *WAI 또는 *OPC?를 사용하여 완료를 확인하세요.

2. **헤더 제거**
   - 응답 처리를 간단히 하려면 `:COMMUNICATE:HEADER OFF` 설정
   - 기본값: ON (응답에 명령어 포함)

3. **장황한 모드**
   - `:COMMUNICATE:VERBOSE OFF`로 축약된 응답 받기
   - 네트워크 트래픽 감소

4. **타임아웃 설정**
   - 소켓 타임아웃: 10~30초 권장
   - 장시간 작업 시 더 길게 설정

5. **배치 명령**
   - 여러 명령을 한 번에 보낼 수 있음 (세미콜론 구분자 사용)
   - `:COMMUNICATE:HEADER OFF;:NUMERIC:VALUE?`

6. **동기화**
   - 측정 완료 후 데이터 읽기는 `:COMMUNICATE:WAIT` 또는 `:STATUS:CONDITION?` 사용

---

**최종 업데이트:** 2024년 11월  
**문서 버전:** 1.0  
**기기:** Yokogawa WT1800E Precision Power Analyzer  
**프로토콜:** SCPI (TCP/IP VXI-11)
