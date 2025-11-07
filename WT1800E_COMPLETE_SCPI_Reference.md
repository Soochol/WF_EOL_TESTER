# Yokogawa WT1800E 정밀 전력 분석기
## 완전한 SCPI 명령어 레퍼런스 (275개 명령어)

**최종 업데이트:** 2024년 11월  
**문서 버전:** 2.0 (완전판)  
**기기:** Yokogawa WT1800E Precision Power Analyzer  
**프로토콜:** SCPI (Simplified Commands for Programmable Instruments)  
**통신:** TCP/IP VXI-11 (포트 5555)  
**원본 문서:** IM WT1801-17EN_programming.pdf (4th Edition)

---

## 📚 목차

| 그룹 | 명령어 수 | 페이지 |
|------|---------|--------|
| AOutput | 6 | 5-16 |
| AUX | 11 | 5-17~18 |
| COMMunicate | 9 | 5-19~20 |
| CURSor | 23 | 5-21~22 |
| DISPlay | 100+ | 5-23~41 |
| FILE | 20 | 5-42~43 |
| HARMonics | 7 | 5-45 |
| HCOPy | 15 | 5-46~47 |
| HOLD | 1 | 5-48 |
| HSPeed | 30+ | 5-49~54 |
| IMAGe | 14 | 5-55~56 |
| INPut | 40+ | 5-57~66 |
| INTEGrate | 18 | 5-67~69 |
| MEASure | 25+ | 5-70~74 |
| MOTor | 33 | 5-75~79 |
| NUMeric | 35 | 5-80~86 |
| RATE | 1 | 5-92 |
| STATus | 8 | 5-93 |
| STORe | 25 | 5-94~96 |
| SYSTem | 25+ | 5-97~99 |
| WAVeform | 11 | 5-100~101 |
| Common Commands | 14 | 5-102~104 |

**총 명령어 수: 275개 이상**

---

## 1️⃣ AOutput Group (6개 명령어)
### D/A 출력 설정 (옵션: /DA)

```
:AOUTput?
:AOUTput:NORMal?
:AOUTput[:NORMal]:CHANnel<x> {NONE|<Function>[,<Element>][,<Order>]}
:AOUTput[:NORMal]:IRTime {<h>,<m>,<s>}
:AOUTput[:NORMal]:MODE<x> {FIXed|MANual}
:AOUTput[:NORMal]:RATE<x> {<Upper>,<Lower>}
```

| 명령어 | 기능 | 파라미터 |
|--------|------|---------|
| :AOUTput? | 모든 D/A 출력 설정 조회 | - |
| :AOUTput:NORMal? | 모든 D/A 출력 설정 조회 | - |
| :AOUTput[:NORMal]:CHANnel<x> | D/A 출력 항목 설정 | x=1~20, Function={URMS,IRMS,P,S,Q,...}, Element=1~6 또는 SIGMA |
| :AOUTput[:NORMal]:IRTime | D/A 출력 적분 시간 | h=0~10000, m=0~59, s=0~59 |
| :AOUTput[:NORMal]:MODE<x> | D/A 정격값 모드 | x=1~20, {FIXed\|MANual} |
| :AOUTput[:NORMal]:RATE<x> | D/A 정격값 설정 | x=1~20, 범위=-9.999E+12~9.999E+12 |

---

## 2️⃣ AUX Group (11개 명령어)
### 보조 입력 설정 (옵션: /AUX)

```
:AUX<x>?
:AUX<x>:AUTO {ON|OFF}
:AUX<x>:FILTer?
:AUX<x>:FILTer[:LINE] {OFF|<Frequency>}
:AUX<x>:LSCale?
:AUX<x>:LSCale:AVALue {<Value>}
:AUX<x>:LSCale:BVALue {<Value>}
:AUX<x>:LSCale:CALCulate?
:AUX<x>:LSCale:CALCulate:{P1X|P1Y|P2X|P2Y} {<Value>}
:AUX<x>:LSCale:CALCulate:EXECute
:AUX<x>:NAME {<String>}
:AUX<x>:RANGe {<Voltage>}
:AUX<x>:SCALing {<Value>}
:AUX<x>:UNIT {<String>}
```

| 명령어 | 기능 |
|--------|------|
| :AUX<x>:AUTO | 보조 입력 자동 범위 ON/OFF (x=1,2) |
| :AUX<x>:FILTer[:LINE] | 라인 필터 설정 (OFF, 100Hz, 1kHz) |
| :AUX<x>:LSCale:AVALue | 선형 스케일 기울기(A) 설정 (1.000E-03~1.000E+06) |
| :AUX<x>:LSCale:BVALue | 선형 스케일 오프셋(B) 설정 (-1.000E+06~1.000E+06) |
| :AUX<x>:LSCale:CALCulate:EXECute | P1X,P1Y,P2X,P2Y 데이터로 A,B 자동 계산 |
| :AUX<x>:NAME | 보조 입력 이름 설정 (최대 8자) |
| :AUX<x>:RANGe | 전압 범위 설정 (50mV~20V) |
| :AUX<x>:SCALing | 스케일링 계수 설정 (0.0001~99999.9999) |
| :AUX<x>:UNIT | 단위 설정 (최대 8자) |

---

## 3️⃣ COMMunicate Group (9개 명령어)
### 통신 제어

```
:COMMunicate?
:COMMunicate:HEADer {ON|OFF}
:COMMunicate:LOCKout {ON|OFF}
:COMMunicate:OPSE <Register>
:COMMunicate:OPSR?
:COMMunicate:OVERlap <Register>
:COMMunicate:REMote {ON|OFF}
:COMMunicate:VERBose {ON|OFF}
:COMMunicate:WAIT <Register>
:COMMunicate:WAIT? <Register>
```

| 명령어 | 기능 | 설명 |
|--------|------|------|
| :COMMunicate:HEADer | 응답에 헤더 추가 여부 | ON: :DISPLAY:MODE NUMERIC, OFF: NUMERIC |
| :COMMunicate:LOCKout | 로컬 잠금 | ON시 LOCAL 키 무시 |
| :COMMunicate:OPSE | *OPC/*OPC?/*WAI 사용 오버랩 명령 설정 | 0~65535 |
| :COMMunicate:OPSR? | 작업 대기 상태 레지스터 조회 | Bit5=PRN(프린터), Bit6=ACS(저장매체) |
| :COMMunicate:OVERlap | 오버랩 명령 설정 | 0~65535 |
| :COMMunicate:REMote | 원격/로컬 모드 | ON=원격, OFF=로컬 |
| :COMMunicate:VERBose | 장황한 응답 | ON=완전형, OFF=축약형 |
| :COMMunicate:WAIT | 이벤트 발생까지 대기 | 확장 이벤트 레지스터 |

---

## 4️⃣ CURSor Group (23개 명령어)
### 커서 측정

### BAR 커서 (고조파 옵션: /G5, /G6)
```
:CURSor:BAR?
:CURSor:BAR:LINKage {ON|OFF}
:CURSor:BAR:POSition<x> {<Value>}
:CURSor:BAR[:STATe] {ON|OFF}
:CURSor:BAR:{Y<x>|DY}?
```

### TREND 커서
```
:CURSor:TRENd?
:CURSor:TRENd:LINKage {ON|OFF}
:CURSor:TRENd:POSition<x> {<Value>}
:CURSor:TRENd[:STATe] {ON|OFF}
:CURSor:TRENd:TRACe<x> {<Value>}
:CURSor:TRENd:{X<x>|Y<x>|DY}?
```

### WAVE 커서
```
:CURSor:WAVE?
:CURSor:WAVE:LINKage {ON|OFF}
:CURSor:WAVE:PATH {MAX|MIN|MID}
:CURSor:WAVE:POSition<x> {<Value>}
:CURSor:WAVE[:STATe] {ON|OFF}
:CURSor:WAVE:TRACe<x> {U<x>|I<x>|SPEed|TORQue|AUX<x>}
:CURSor:WAVE:{X<x>|DX|PERDt|Y<x>|DY}?
```

---

## 5️⃣ DISPlay Group (100+ 명령어)
### 디스플레이 설정 (가장 복잡한 그룹)

### 기본 디스플레이
```
:DISPlay?
:DISPlay:MODE {NUMeric|WAVE|TRENd|BAR|VECTor|...}
:DISPlay:INFOrmation?
:DISPlay:INFOrmation:PAGE {POWer|RANGe|<NRf>}
:DISPlay:INFOrmation[:STATe] {ON|OFF}
```

### BAR 그래프 (고조파 옵션)
```
:DISPlay:BAR?
:DISPlay:BAR:FORMat {SINGle|DUAL|TRIad}
:DISPlay:BAR:ITEM<x>?
:DISPlay:BAR:ITEM<x>[:FUNCtion] {<Function>,<Element>}
:DISPlay:BAR:ITEM<x>:SCALing?
:DISPlay:BAR:ITEM<x>:SCALing:MODE {FIXed|MANual}
:DISPlay:BAR:ITEM<x>:SCALing:VALue {<Value>}
:DISPlay:BAR:ITEM<x>:SCALing:VERTical {LINear|LOG}
:DISPlay:BAR:ITEM<x>:SCALing:XAXis {BOTTom|CENTer}
:DISPlay:BAR:ORDer {<Start>,<End>}
```

### HSPeed 고속 데이터 캡처 (옵션: /HS)
```
:DISPlay:HSPeed?
:DISPlay:HSPeed:COLumn?
:DISPlay:HSPeed:COLumn:ITEM<x>
:DISPlay:HSPeed:COLumn:NUMber
:DISPlay:HSPeed:COLumn:RESet
:DISPlay:HSPeed:FRAMe {ON|OFF}
:DISPlay:HSPeed:PAGE {<NRf>}
:DISPlay:HSPeed:POVer {ON|OFF}
```

### NUMERIC 수치 표시 (일반)
```
:DISPlay:NUMeric?
:DISPlay:NUMeric:FRAMe {ON|OFF}
:DISPlay:NUMeric:NORMal?
```

### NUMERIC 커스텀 모드 (고급)
```
:DISPlay:NUMeric:CUSTom?
:DISPlay:NUMeric:CUSTom:FILE:CDIRectory {<Path>}
:DISPlay:NUMeric:CUSTom:FILE:DRIVe {RAM|USB|NETWork}
:DISPlay:NUMeric:CUSTom:FILE:FREE?
:DISPlay:NUMeric:CUSTom:FILE:LOAD:ABORt
:DISPlay:NUMeric:CUSTom:FILE:LOAD:BMP {<Filename>}
:DISPlay:NUMeric:CUSTom:FILE:LOAD:BOTH {<Filename>}
:DISPlay:NUMeric:CUSTom:FILE:LOAD:ITEM {<Filename>}
:DISPlay:NUMeric:CUSTom:FILE:PATH?
:DISPlay:NUMeric:CUSTom:FILE:SAVE:ANAMing {OFF|NUMBering|DATE}
:DISPlay:NUMeric:CUSTom:FILE:SAVE:ITEM {<Filename>}
:DISPlay:NUMeric:CUSTom:ITEM<x>?
:DISPlay:NUMeric:CUSTom:ITEM<x>:COLor {YELLow|GREen|RED|...(20색)}
:DISPlay:NUMeric:CUSTom:ITEM<x>[:FUNCtion]
:DISPlay:NUMeric:CUSTom:ITEM<x>:POSition {<X>,<Y>}
:DISPlay:NUMeric:CUSTom:ITEM<x>:SIZE {14|16|20|24|32|48|64|96|128}
:DISPlay:NUMeric:CUSTom:PAGE {<NRf>}
:DISPlay:NUMeric:CUSTom:PERPage {<NRf>}
:DISPlay:NUMeric:CUSTom:TOTal {<NRf>}
```

### NUMERIC ALL 항목 표시 모드
```
:DISPlay:NUMeric[:NORMal]:ALL?
:DISPlay:NUMeric[:NORMal]:ALL:COLumn?
:DISPlay:NUMeric[:NORMal]:ALL:COLumn:DAELem {ON|OFF}
:DISPlay:NUMeric[:NORMal]:ALL:COLumn:SCRoll {ON|OFF}
:DISPlay:NUMeric[:NORMal]:ALL:CURSor {<Value>}
:DISPlay:NUMeric[:NORMal]:ALL:ORDer {<Value>}
:DISPlay:NUMeric[:NORMal]:ALL:PAGE {<NRf>}
```

### NUMERIC LIST 리스트 표시 모드
```
:DISPlay:NUMeric[:NORMal]:LIST?
:DISPlay:NUMeric[:NORMal]:LIST:CURSor {<Value>}
:DISPlay:NUMeric[:NORMal]:LIST:HEADer {<Value>}
:DISPlay:NUMeric[:NORMal]:LIST:ITEM<x>
:DISPlay:NUMeric[:NORMal]:LIST:ORDer {<Value>}
```

### NUMERIC MATRIX 매트릭스 표시 모드
```
:DISPlay:NUMeric[:NORMal]:MATRix?
:DISPlay:NUMeric[:NORMal]:MATRix:COLumn?
:DISPlay:NUMeric[:NORMal]:MATRix:COLumn:ITEM<x>
:DISPlay:NUMeric[:NORMal]:MATRix:COLumn:NUMber
:DISPlay:NUMeric[:NORMal]:MATRix:COLumn:RESet
:DISPlay:NUMeric[:NORMal]:MATRix:CURSor
:DISPlay:NUMeric[:NORMal]:MATRix:ITEM<x>
:DISPlay:NUMeric[:NORMal]:MATRix:PAGE
:DISPlay:NUMeric[:NORMal]:MATRix:PRESet
```

### NUMERIC VAL4/VAL8/VAL16 다중 항목 표시
```
:DISPlay:NUMeric[:NORMal]:{VAL4|VAL8|VAL16}?
:DISPlay:NUMeric[:NORMal]:{VAL4|VAL8|VAL16}:CURSor
:DISPlay:NUMeric[:NORMal]:{VAL4|VAL8|VAL16}:ITEM<x>
:DISPlay:NUMeric[:NORMal]:{VAL4|VAL8|VAL16}:PAGE
:DISPlay:NUMeric[:NORMal]:{VAL4|VAL8|VAL16}:PRESet
```

### NUMERIC FORMAT
```
:DISPlay:NUMeric[:NORMal]:FORMat {<Format>}
```

### TREND 추세 표시
```
:DISPlay:TRENd?
:DISPlay:TRENd:ALL {ON|OFF}
:DISPlay:TRENd:CLEar
:DISPlay:TRENd:FORMat
:DISPlay:TRENd:ITEM<x>?
:DISPlay:TRENd:ITEM<x>[:FUNCtion]
:DISPlay:TRENd:ITEM<x>:SCALing?
:DISPlay:TRENd:ITEM<x>:SCALing:MODE
:DISPlay:TRENd:ITEM<x>:SCALing:VALue
:DISPlay:TRENd:T<x>
:DISPlay:TRENd:TDIV
```

### VECTOR 벡터 표시 (고조파 옵션)
```
:DISPlay:VECTor?
:DISPlay:VECTor:FORMat
:DISPlay:VECTor:ITEM<x>?
:DISPlay:VECTor:ITEM<x>:OBJect
:DISPlay:VECTor:ITEM<x>:{UMAG|IMAG}
:DISPlay:VECTor:NUMeric
```

### WAVE 파형 표시
```
:DISPlay:WAVE?
:DISPlay:WAVE:ALL {ON|OFF}
:DISPlay:WAVE:FORMat
:DISPlay:WAVE:GRATicule
:DISPlay:WAVE:INTerpolate
:DISPlay:WAVE:MAPPing?
:DISPlay:WAVE:MAPPing[:MODE]
:DISPlay:WAVE:MAPPing:{U<x>|I<x>|SPEed|TORQue|AUX<x>}
:DISPlay:WAVE:POSition?
:DISPlay:WAVE:POSition:{U<x>|I<x>}
:DISPlay:WAVE:POSition:{UALL|IALL}
:DISPlay:WAVE:SVALue {ON|OFF}
:DISPlay:WAVE:TDIV
:DISPlay:WAVE:TLABel {ON|OFF}
:DISPlay:WAVE:TRIGger?
:DISPlay:WAVE:TRIGger:LEVel
:DISPlay:WAVE:TRIGger:MODE
:DISPlay:WAVE:TRIGger:SLOPe
:DISPlay:WAVE:TRIGger:SOURce
:DISPlay:WAVE:{U<x>|I<x>|SPEed|TORQue|AUX<x>} {ON|OFF}
:DISPlay:WAVE:VZoom?
:DISPlay:WAVE:VZoom:{U<x>|I<x>}
:DISPlay:WAVE:VZoom:{UALL|IALL}
```

---

## 6️⃣ FILE Group (20개 명령어)
### 파일 작업

```
:FILE?
:FILE:CDIRectory {<Path>}
:FILE:DRIVe {<Drive>}
:FILE:FILTer
:FILE:FREE?
:FILE:LOAD:ABORt
:FILE:LOAD:SETup {<Filename>}
:FILE:PATH?
:FILE:DELete:IMAGe:{BMP|PNG|JPEG}
:FILE:DELete:NUMeric:ASCii {<Filename>}
:FILE:DELete:SETup {<Filename>}
:FILE:DELete:STORe:{DATA|HEADer}
:FILE:DELete:WAVE:ASCii {<Filename>}
:FILE:SAVE?
:FILE:SAVE:ABORt
:FILE:SAVE:ANAMing {OFF|NUMBering|DATE}
:FILE:SAVE:COMMent {<String>}
:FILE:SAVE:NUMeric[:EXECute]
:FILE:SAVE:NUMeric:ITEM {AUTO|MANual}
:FILE:SAVE:NUMeric:NORMal?
:FILE:SAVE:NUMeric:NORMal:ALL {ON|OFF}
:FILE:SAVE:NUMeric:NORMal:{ELEMent<x>|SIGMA}
:FILE:SAVE:NUMeric:NORMal:<Function> {ON|OFF}
:FILE:SAVE:NUMeric:NORMal:PRESet<x>
:FILE:SAVE:SETup[:EXECute]
:FILE:SAVE:WAVE[:EXECute]
```

---

## 7️⃣ HARMonics Group (7개 명령어)
### 고조파 분석 (옵션: /G5, /G6)

```
:HARMonics<x>?
:HARMonics<x>:CONFigure?
:HARMonics<x>:CONFigure[:ALL]
:HARMonics<x>:CONFigure:ELEMent<x>
:HARMonics<x>:CONFigure:{SIGMA|SIGMB|SIGMC}
:HARMonics<x>:ORDer {<Min>,<Max>}
:HARMonics<x>:PLLSource
:HARMonics<x>:THD {<Formula>}
```

| 명령어 | 파라미터 |
|--------|---------|
| :HARMonics<x>:ORDer | Min=0~490, Max=10~500 (Min+10 이상) |
| :HARMonics<x>:THD | THD 계산 방식 |

---

## 8️⃣ HCOPy Group (15개 명령어)
### 인쇄 설정

```
:HCOPy?
:HCOPy:ABORt
:HCOPy:AUTO?
:HCOPy:AUTO:COUNt {<Count>}
:HCOPy:AUTO:INTerval {<Interval>}
:HCOPy:AUTO:MODE {<Mode>}
:HCOPy:AUTO:PASTart {ON|OFF}
:HCOPy:AUTO:{STARt|END}
:HCOPy:AUTO[:STATe] {ON|OFF}
:HCOPy:AUTO:TEVent {<Event>}
:HCOPy:COMMent {<String>}
:HCOPy:EXECute
:HCOPy:PRINter?
:HCOPy:PRINter:FEED
:HCOPy:PRINter:FORMat
```

---

## 9️⃣ HOLD Group (1개 명령어)
### 데이터 홀드

```
:HOLD {ON|OFF}
:HOLD?
```

---

## 🔟 HSPeed Group (30+ 명령어)
### 고속 데이터 캡처 (옵션: /HS)

```
:HSPeed?
:HSPeed:STARt
:HSPeed:STOP
:HSPeed:STATe?
:HSPeed:CAPTured?
:HSPeed:COUNt {<Count>}
:HSPeed:MAXCount?
:HSPeed:MEASuring?
:HSPeed:MEASuring[:ALL]
:HSPeed:MEASuring:{U<x>|I<x>}
:HSPeed:MEASuring:{UALL|IALL}
:HSPeed:POVer?
:HSPeed:EXTSync {ON|OFF}

:HSPeed:DISPlay?
:HSPeed:DISPlay:COLumn?
:HSPeed:DISPlay:COLumn:ITEM<x>
:HSPeed:DISPlay:COLumn:NUMber
:HSPeed:DISPlay:COLumn:RESet
:HSPeed:DISPlay:FRAMe {ON|OFF}
:HSPeed:DISPlay:PAGE {<Page>}
:HSPeed:DISPlay:POVer {ON|OFF}

:HSPeed:FILTer?
:HSPeed:FILTer[:HS] {ON|OFF}
:HSPeed:FILTer:LINE?
:HSPeed:FILTer:LINE[:ALL]
:HSPeed:FILTer:LINE:ELEMent<x>

:HSPeed:RECord?
:HSPeed:RECord:FILE?
:HSPeed:RECord:FILE:ANAMing
:HSPeed:RECord:FILE:CDIRectory
:HSPeed:RECord:FILE:CONVert?
:HSPeed:RECord:FILE:CONVert:ABORt
:HSPeed:RECord:FILE:CONVert:AUTO
:HSPeed:RECord:FILE:CONVert:EXECute
:HSPeed:RECord:FILE:DRIVe
:HSPeed:RECord:FILE:FREE?
:HSPeed:RECord:FILE:NAME
:HSPeed:RECord:FILE:PATH?
:HSPeed:RECord:FILE:STATe?
:HSPeed:RECord:ITEM?
:HSPeed:RECord:ITEM:AUX<x>
:HSPeed:RECord:ITEM:{I<x>|IA|IB|IC}
:HSPeed:RECord:ITEM:{P<x>|PA|PB|PC}
:HSPeed:RECord:ITEM:{SPEed|TORQue|PM}
:HSPeed:RECord:ITEM:{U<x>|UA|UB|UC}
:HSPeed:RECord:ITEM:PRESet:ALL
:HSPeed:RECord:ITEM:PRESet:{ELEMent<x>|SIGMA}
:HSPeed:RECord:ITEM:PRESet:{U|I|P|MOTor|AUX}
:HSPeed:RECord[:STATe] {ON|OFF}

:HSPeed:TRIGger?
:HSPeed:TRIGger:LEVel {<Value>}
:HSPeed:TRIGger:MODE {<Mode>}
:HSPeed:TRIGger:SLOPe {RISE|FALL}
:HSPeed:TRIGger:SOURce {<Source>}
```

---

## 1️⃣1️⃣ IMAGe Group (14개 명령어)
### 화면 이미지 저장

```
:IMAGe?
:IMAGe:ABORt
:IMAGe:COLor {COLOR|MONO}
:IMAGe:COMMent {<String>}
:IMAGe:EXECute
:IMAGe:FORMat {BMP|PNG|JPEG}
:IMAGe:SAVE?
:IMAGe:SAVE:ANAMing {OFF|NUMBering|DATE}
:IMAGe:SAVE:CDIRectory {<Path>}
:IMAGe:SAVE:DRIVe {<Drive>}
:IMAGe:SAVE:FREE?
:IMAGe:SAVE:NAME {<Filename>}
:IMAGe:SAVE:PATH?
:IMAGe:SEND?
```

---

## 1️⃣2️⃣ INPut Group (40+ 명령어)
### 입력 설정

### 기본 입력 설정
```
[:INPut]?
[:INPut]:CFACtor {<Value>}
[:INPut]:ESELect {<Element>}
[:INPut]:INDependent {ON|OFF}
[:INPut]:MODUle?
[:INPut]:POVer?
[:INPut]:WIRing {1PH2W|1PH3W|3PH3W|3PH4W}
```

### NULL 영점 조정
```
[:INPut]:NULL:CONDition:{SPEed|TORQue|AUX<x>}?
[:INPut]:NULL:CONDition:{U<x>|I<x>}?
[:INPut]:NULL[:STATe] {ON|OFF}
[:INPut]:NULL:TARGet?
[:INPut]:NULL:TARGet[:MODE] {<Mode>}
[:INPut]:NULL:TARGet:{SPEed|TORQue|AUX<x>}
[:INPut]:NULL:TARGet:{U<x>|I<x>}
[:INPut]:NULL:TARGet:{UALL|IALL}
```

### 전압 설정
```
[:INPut]:VOLTage?
[:INPut]:VOLTage:AUTO?
[:INPut]:VOLTage:AUTO[:ALL] {ON|OFF}
[:INPut]:VOLTage:AUTO:ELEMent<x> {ON|OFF}
[:INPut]:VOLTage:AUTO:{SIGMA|SIGMB|SIGMC} {ON|OFF}
[:INPut]:VOLTage:CONFig?
[:INPut]:VOLTage:CONFig[:ALL] {<Config>}
[:INPut]:VOLTage:CONFig:ELEMent<x> {<Config>}
[:INPut]:VOLTage:POJump?
[:INPut]:VOLTage:POJump[:ALL] {<Range>}
[:INPut]:VOLTage:POJump:ELEMent<x> {<Range>}
[:INPut]:VOLTage:RANGe?
[:INPut]:VOLTage:RANGe[:ALL] {<Range>}
[:INPut]:VOLTage:RANGe:ELEMent<x> {<Range>}
[:INPut]:VOLTage:RANGe:{SIGMA|SIGMB|SIGMC} {<Range>}
```

### 전류 설정
```
[:INPut]:CURRent?
[:INPut]:CURRent:AUTO?
[:INPut]:CURRent:AUTO[:ALL]
[:INPut]:CURRent:AUTO:ELEMent<x>
[:INPut]:CURRent:AUTO:{SIGMA|SIGMB|SIGMC}
[:INPut]:CURRent:CONFig?
[:INPut]:CURRent:CONFig[:ALL]
[:INPut]:CURRent:CONFig:ELEMent<x>
[:INPut]:CURRent:EXTSensor?
[:INPut]:CURRent:EXTSensor:CONFig?
[:INPut]:CURRent:EXTSensor:CONFig[:ALL]
[:INPut]:CURRent:EXTSensor:CONFig:ELEMent<x>
[:INPut]:CURRent:EXTSensor:DISPlay {ON|OFF}
[:INPut]:CURRent:EXTSensor:POJump?
[:INPut]:CURRent:EXTSensor:POJump[:ALL]
[:INPut]:CURRent:EXTSensor:POJump:ELEMent<x>
[:INPut]:CURRent:POJump?
[:INPut]:CURRent:POJump[:ALL]
[:INPut]:CURRent:POJump:ELEMent<x>
[:INPut]:CURRent:RANGe?
[:INPut]:CURRent:RANGe[:ALL] {<Range>}
[:INPut]:CURRent:RANGe:ELEMent<x> {<Range>}
[:INPut]:CURRent:RANGe:{SIGMA|SIGMB|SIGMC} {<Range>}
[:INPut]:CURRent:SRATio?
[:INPut]:CURRent:SRATio[:ALL]
[:INPut]:CURRent:SRATio:ELEMent<x>
[:INPut]:CURRent:SRATio:{SIGMA|SIGMB|SIGMC}
```

### 필터 설정
```
[:INPut]:FILTer?
[:INPut]:FILTer:FREQuency?
[:INPut]:FILTer:FREQuency[:ALL]
[:INPut]:FILTer:FREQuency:ELEMent<x>
[:INPut]:FILTer:LINE?
[:INPut]:FILTer[:LINE][:ALL]
[:INPut]:FILTer[:LINE]:ELEMent<x>
[:INPut]:FILTer[:LINE]:{SIGMA|SIGMB|SIGMC}
```

### 스케일링
```
[:INPut]:SCALing?
[:INPut]:SCALing:STATe?
[:INPut]:SCALing[:STATe][:ALL]
[:INPut]:SCALing[:STATe]:ELEMent<x>
[:INPut]:SCALing:{VT|CT|SFACtor}?
[:INPut]:SCALing:{VT|CT|SFACtor}[:ALL]
[:INPut]:SCALing:{VT|CT|SFACtor}:ELEMent<x>
[:INPut]:SCALing:{VT|CT|SFACtor}:{SIGMA|SIGMB|SIGMC}
```

### 동기화
```
[:INPut]:SYNChronize?
[:INPut]:SYNChronize[:ALL]
[:INPut]:SYNChronize:ELEMent<x>
[:INPut]:SYNChronize:{SIGMA|SIGMB|SIGMC}
```

---

## 1️⃣3️⃣ INTEGrate Group (18개 명령어)
### 적분 설정 - ⚠️ 중요: 적산값 읽기 방법

```
:INTEGrate?
:INTEGrate:ACAL {ON|OFF}
:INTEGrate:INDependent {ON|OFF}
:INTEGrate:MODE {TIMER|RealTime}
:INTEGrate:QMODe?
:INTEGrate:QMODe[:ALL] {<Mode>}
:INTEGrate:QMODe:ELEMent<x> {<Mode>}
:INTEGrate:RESet
:INTEGrate:RTALl:{STARt|END} {<Time>}
:INTEGrate:RTIMe<x>?
:INTEGrate:RTIMe<x>:{STARt|END} {<Time>}
:INTEGrate:STARt
:INTEGrate:STATe?
:INTEGrate:STOP
:INTEGrate:TIMer<x> {<h>,<m>,<s>}
:INTEGrate:TMALl {<h>,<m>,<s>}
:INTEGrate:WPTYpe?
:INTEGrate:WPTYpe[:ALL] {<Type>}
:INTEGrate:WPTYpe:ELEMent<x> {<Type>}
```

### ⚠️ **중요 발견: 적산값을 직접 읽는 명령어 없음!**

`:INTEGrate:VALue?` ❌ **존재하지 않음**

**올바른 적산값 읽기 방법:** MEASure 함수 그룹 사용
```scpi
# 적산값은 특수 함수로만 접근 가능

:NUMERIC:ITEM1 WH,1          # ← 유효 전력량 (Wh)
:NUMERIC:ITEM2 AH,1          # ← 전하량 (Ah)
:NUMERIC:ITEM3 TIME,1        # ← 적산 시간 (초)
:NUMERIC:VALUE?              # ← 모든 적산값 반환

응답 예: 6.300E+01,3.200E+00,1.134E+02
        (63.0 Wh, 3.2 Ah, 113.4 s)
```

---

## 1️⃣4️⃣ MEASure Group (25+ 명령어)
### 측정 계산

### 기본 측정
```
:MEASure?
:MEASure:AVERaging?
:MEASure:AVERaging:COUNt {<Count>}
:MEASure:AVERaging[:STATe] {ON|OFF}
:MEASure:AVERaging:TYPE {<Type>}
:MEASure:SAMPling {<Frequency>}
:MEASure:SYNChronize {ON|OFF}
```

### 델타 측정
```
:MEASure:DMeasure?
:MEASure:DMeasure:MODE {<Mode>}
:MEASure:DMeasure:{SIGMA|SIGMB|SIGMC} {<Mode>}
```

### 효율
```
:MEASure:EFFiciency?
:MEASure:EFFiciency:ETA<x> {<Formula>}
:MEASure:EFFiciency:UDEF<x> {<Value>}
```

### 사용자 정의 이벤트
```
:MEASure:EVENt<x>?
:MEASure:EVENt<x>:EXPRession?
:MEASure:EVENt<x>:EXPRession:CONDition {<Condition>}
:MEASure:EVENt<x>:EXPRession:INVerse {ON|OFF}
:MEASure:EVENt<x>:EXPRession:ITEM {<Item>}
:MEASure:EVENt<x>:EXPRession:LIMit<x> {<Value>}
:MEASure:EVENt<x>:EXPRession:STRing?
:MEASure:EVENt<x>:EXPRession:TYPE {RANGE|COMPOUND}
:MEASure:EVENt<x>:FLABel {<String>}
:MEASure:EVENt<x>:NAME {<String>}
:MEASure:EVENt<x>[:STATe] {ON|OFF}
:MEASure:EVENt<x>:TLABel {<String>}
```

### 주파수
```
:MEASure:FREQuency?
:MEASure:FREQuency:ITEM<x> {<Element>}
```

### 사용자 정의 함수
```
:MEASure:FUNCtion<x>?
:MEASure:FUNCtion<x>:EXPRession {<Expression>}
:MEASure:FUNCtion<x>:NAME {<Name>}
:MEASure:FUNCtion<x>[:STATe] {ON|OFF}
:MEASure:FUNCtion<x>:UNIT {<Unit>}
:MEASure:MHOLd {ON|OFF}
```

### 수정된 전력 (Pc)
```
:MEASure:PC?
:MEASure:PC:IEC {<Formula>}
:MEASure:PC:P<x> {<Value>}
```

### 위상각
```
:MEASure:PHASe {<Format>}
```

### 여태 전력
```
:MEASure:SFORmula {<Formula>}
:MEASure:SQFormula {<Formula>}
```

---

## 1️⃣5️⃣ MOTor Group (33개 명령어)
### 모터 평가 (옵션: /MTR)

### 기본
```
:MOTor?
:MOTor:POLE {<Poles>}
```

### 전기각
```
:MOTor:EANGle?
:MOTor:EANGle:CORRection?
:MOTor:EANGle:CORRection:AENTer?
:MOTor:EANGle:CORRection:AENTer[:EXECute]
:MOTor:EANGle:CORRection:AENTer:TARGet {<Source>}
:MOTor:EANGle:CORRection:CLEar
:MOTor:EANGle:CORRection[:VALue] {<Value>}
:MOTor:EANGle[:STATe] {ON|OFF}
```

### 필터
```
:MOTor:FILTer?
:MOTor:FILTer[:LINE] {<Filter>}
```

### 모터 출력 (Pm)
```
:MOTor:PM?
:MOTor:PM:SCALing {<Scale>}
:MOTor:PM:UNIT {<Unit>}
```

### 회전 속도
```
:MOTor:SPEed?
:MOTor:SPEed:AUTO {ON|OFF}
:MOTor:SPEed:LSCale?
:MOTor:SPEed:LSCale:AVALue {<Value>}
:MOTor:SPEed:LSCale:BVALue {<Value>}
:MOTor:SPEed:LSCale:CALCulate?
:MOTor:SPEed:LSCale:CALCulate:{P1X|P1Y|P2X|P2Y} {<Value>}
:MOTor:SPEed:LSCale:CALCulate:EXECute
:MOTor:SPEed:PRANge {<Range>}
:MOTor:SPEed:PULSe {<Pulses>}
:MOTor:SPEed:RANGe {<Range>}
:MOTor:SPEed:SCALing {<Scale>}
:MOTor:SPEed:TYPE {PULSE|ANALOG}
:MOTor:SPEed:UNIT {<Unit>}
:MOTor:SSPeed {<Source>}
:MOTor:SYNChronize {<Source>}
```

### 토크
```
:MOTor:TORQue?
:MOTor:TORQue:AUTO {ON|OFF}
:MOTor:TORQue:LSCale?
:MOTor:TORQue:LSCale:AVALue {<Value>}
:MOTor:TORQue:LSCale:BVALue {<Value>}
:MOTor:TORQue:LSCale:CALCulate?
:MOTor:TORQue:LSCale:CALCulate:{P1X|P1Y|P2X|P2Y} {<Value>}
:MOTor:TORQue:LSCale:CALCulate:EXECute
:MOTor:TORQue:PRANge {<Range>}
:MOTor:TORQue:RANGe {<Range>}
:MOTor:TORQue:RATE?
:MOTor:TORQue:RATE:{UPPer|LOWer} {<Value>}
:MOTor:TORQue:SCALing {<Scale>}
:MOTor:TORQue:TYPE {PULSE|ANALOG}
:MOTor:TORQue:UNIT {<Unit>}
```

---

## 1️⃣6️⃣ NUMeric Group (35개 명령어)
### 수치 데이터

### 기본
```
:NUMeric?
:NUMeric:FORMat {ASCII|REAL}
:NUMeric:HOLD {ON|OFF}
```

### 정상 모드
```
:NUMeric:NORMal?
:NUMeric[:NORMal]:CLEar
:NUMeric[:NORMal]:DELete {<Index>}
:NUMeric[:NORMal]:ITEM<x> {<Function>[,<Element>][,<Order>]}
:NUMeric[:NORMal]:NUMber {<Count>}
:NUMeric[:NORMal]:PRESet {<Pattern>}
:NUMeric[:NORMal]:VALue?
```

### 고속 캡처 모드
```
:NUMeric:HSPeed?
:NUMeric:HSPeed:CLEar
:NUMeric:HSPeed:DELete {<Index>}
:NUMeric:HSPeed:HEADer?
:NUMeric:HSPeed:ITEM<x>
:NUMeric:HSPeed:{MAXimum|MINimum}?
:NUMeric:HSPeed:NUMber {<Count>}
:NUMeric:HSPeed:PRESet {<Pattern>}
:NUMeric:HSPeed:VALue?
```

### LIST 모드
```
:NUMeric:LIST?
:NUMeric:LIST:CLEar
:NUMeric:LIST:DELete {<Index>}
:NUMeric:LIST:ITEM<x>
:NUMeric:LIST:NUMber {<Count>}
:NUMeric:LIST:ORDer {<Order>}
:NUMeric:LIST:PRESet {<Pattern>}
:NUMeric:LIST:SELect {<Selection>}
:NUMeric:LIST:VALue?
```

---

## 1️⃣7️⃣ RATE Group (1개 명령어)
### 데이터 업데이트 레이트

```
:RATE {<Frequency>}
:RATE?
```

---

## 1️⃣8️⃣ STATus Group (8개 명령어)
### 상태 보고

```
:STATus?
:STATus:CONDition?
:STATus:EESE {<Register>}
:STATus:EESR?
:STATus:ERRor?
:STATus:FILTer<x> {RISE|FALL}
:STATus:QENable {ON|OFF}
:STATus:QMESsage {ON|OFF}
:STATus:SPOLl?
```

---

## 1️⃣9️⃣ STORe Group (25개 명령어)
### 데이터 저장

### 기본
```
:STORe?
:STORe:COUNt {<Count>}
:STORe:STARt
:STORe:STOP
:STORe:STATe?
:STORe:RESet
:STORe:INTerval {<Interval>}
```

### 저장 설정
```
:STORe:SMODe {NORMAL|RealTime|Event}
:STORe:SMODe?
:STORe:SASTart {ON|OFF}
:STORe:TEVent {<Event>}
```

### 실시간 저장
```
:STORe:RTIMe?
:STORe:RTIMe:{STARt|END} {<Time>}
```

### 파일 설정
```
:STORe:FILE?
:STORe:FILE:ANAMing {OFF|NUMBering|DATE}
:STORe:FILE:CDIRectory {<Path>}
:STORe:FILE:CONVert?
:STORe:FILE:CONVert:ABORt
:STORe:FILE:CONVert:AUTO {ON|OFF}
:STORe:FILE:CONVert:EXECute
:STORe:FILE:DRIVe {<Drive>}
:STORe:FILE:FREE?
:STORe:FILE:NAME {<Name>}
:STORe:FILE:PATH?
```

### 저장 항목
```
:STORe:NUMeric?
:STORe:NUMeric:ITEM {AUTO|MANual}
:STORe:NUMeric:NORMal?
:STORe:NUMeric[:NORMal]:ALL {ON|OFF}
:STORe:NUMeric[:NORMal]:{ELEMent<x>|SIGMA|SIGMB|SIGMC} {ON|OFF}
:STORe:NUMeric[:NORMal]:<Function> {ON|OFF}
:STORe:NUMeric[:NORMal]:PRESet<x>
```

---

## 2️⃣0️⃣ SYSTem Group (25+ 명령어)
### 시스템 설정

### 기본
```
:SYSTem?
:SYSTem:MODel?
:SYSTem:SERial?
:SYSTem:SUFFix?
```

### 날짜/시간
```
:SYSTem:CLOCk?
:SYSTem:CLOCk:DISPlay {ON|OFF}
:SYSTem:CLOCk:SNTP?
:SYSTem:CLOCk:SNTP[:EXECute]
:SYSTem:CLOCk:SNTP:GMTTime {<TimeOffset>}
:SYSTem:CLOCk:TYPE {MANual|SNTP}
:SYSTem:DATE {YYYY,MM,DD}
:SYSTem:TIME {HH,MM,SS}
```

### 디스플레이 설정
```
:SYSTem:DFLow:FREQuency {<Format>}
:SYSTem:DFLow:MOTor {<Format>}
:SYSTem:DPOint {PERIOD|COMMA}
:SYSTem:ECLear
:SYSTem:FONT {SMALL|NORMAL|LARGE}
:SYSTem:KLOCk {ON|OFF}
```

### 언어 설정
```
:SYSTem:LANGuage?
:SYSTem:LANGuage:MENU {English|Japanese|Chinese|...}
:SYSTem:LANGuage:MESSage {English|Japanese|Chinese|...}
```

### LCD 설정
```
:SYSTem:LCD?
:SYSTem:LCD:AOFF?
:SYSTem:LCD:AOFF[:STATe] {ON|OFF}
:SYSTem:LCD:AOFF:TIME {<Seconds>}
:SYSTem:LCD:BRIGhtness {<Level>}
:SYSTem:LCD:COLor?
:SYSTem:LCD:COLor:BASecolor {<Color>}
:SYSTem:LCD:COLor:GRAPh?
:SYSTem:LCD:COLor:GRAPh:CHANnel<x> {<Color>}
:SYSTem:LCD:COLor:GRAPh:PRESet
:SYSTem:LCD:COLor:INTENsity:GRID {<Intensity>}
:SYSTem:LCD[:STATe] {ON|OFF}
```

### 기타
```
:SYSTem:RESolution {<Resolution>}
:SYSTem:USBKeyboard {US|JP}
```

---

## 2️⃣1️⃣ WAVeform Group (11개 명령어)
### 파형 데이터

```
:WAVeform?
:WAVeform:BYTeorder {NORMAL|SWAP}
:WAVeform:END {<Point>}
:WAVeform:FORMat {ASCII|REAL}
:WAVeform:HOLD {ON|OFF}
:WAVeform:LENGth?
:WAVeform:SEND?
:WAVeform:SRATe?
:WAVeform:STARt {<Point>}
:WAVeform:TRACe {U<x>|I<x>}
:WAVeform:TRIGger?
```

---

## 2️⃣2️⃣ Common Commands (14개 명령어)
### IEEE 488.2 표준 공통 명령

| 명령어 | 기능 | 설명 |
|--------|------|------|
| *IDN? | 기기 정보 조회 | 응답: YOKOGAWA,WT1800,SN,FW |
| *RST | 기기 초기화 | 모든 설정 리셋 |
| *CLS | 레지스터 클리어 | 표준/확장 이벤트, 오류 큐 |
| *OPC | OPC 비트 설정 | 오버랩 명령 완료 대기 |
| *OPC? | OPC 쿼리 | 1=완료, 0=진행 중 |
| *WAI | 대기 | 다음 명령 실행 대기 |
| *ESE | 표준 이벤트 레지스터 | 0~255 |
| *ESR? | 표준 이벤트 조회 | 레지스터 값 반환 및 클리어 |
| *SRE | 서비스 요청 활성화 | 0~255 |
| *STB? | 상태 바이트 조회 | 0~255 |
| *TRG | 단일 측정 | SINGLE 키 누름 동일 |
| *TST? | 자체 검사 | 0=성공, 1=실패 |
| *CAL? | 제로 캘리브레이션 | SHIFT+CAL 동일 |
| *OPT? | 설치 옵션 조회 | /G5,/G6,/MTR,/HS,/AUX,/DA |

---

## 📋 빠른 참조 테이블

### 주요 측정 함수 (FUNCTION)
```
=== 기본 전력 함수 ===
URMS    - 전압 RMS
IRMS    - 전류 RMS
P       - 실전력
S       - 여태전력
Q       - 무효전력
LAMBda  - 역률
PHI     - 위상각
Z       - 임피던스
RS,XS   - 직렬 저항/리액턴스
RP,XP   - 병렬 저항/리액턴스

=== 고조파 함수 ===
UK      - 고조파 전압
IK      - 고조파 전류
PK      - 고조파 전력
CF      - 크레스트 인수
UHD     - 고조파 왜곡률 (전압)
IHD     - 고조파 왜곡률 (전류)

=== ✅ 적산값 함수 (매뉴얼 페이지 5-38) ===
TIME    - 적산 경과 시간 (초)
WH      - 유효 전력량 (Watt-Hour)
WHP     - 양극 유효 전력량 (Wh Positive)
WHM     - 음극 유효 전력량 (Wh Negative)
AH      - 전하량 (Ampere-Hour)
AHP     - 양극 전하량 (Ah Positive)
AHM     - 음극 전하량 (Ah Negative)
WS      - 피상 전력량 (VA-Hour)
WQ      - 무효 전력량 (Var-Hour)

=== 사용자 정의 함수 ===
F1~F20  - 사용자 정의 계산식
        예: "WH(E1)/TIME(E1)*3600" = 평균 전력 (W)
        예: "AH(E1)/TIME(E1)*3600" = 평균 전류 (A)
```

**사용 예시:**
```scpi
# 적산값 측정
:NUMERIC:ITEM1 URMS,1
:NUMERIC:ITEM2 IRMS,1
:NUMERIC:ITEM3 P,1
:NUMERIC:ITEM4 WH,1           # ← 누적 전력량
:NUMERIC:ITEM5 TIME,1         # ← 적산 시간
:NUMERIC:ITEM6 AH,1           # ← 누적 전하량
:NUMERIC:ITEM7 WHP,1          # ← 양극 전력량
:NUMERIC:ITEM8 WQ,1           # ← 무효 전력량
:NUMERIC:NUMBER 8

:INTEGRATE:START
[측정 수행 113.4초]
:INTEGRATE:STOP
:NUMERIC:VALUE?
→ 응답: V,A,W,Wh,s,Ah,Wh,Varh (예: ...,63.0,113.4,3.2,63.0,15.2)
```

### 주요 파라미터
```
<x>              = 채널/요소 번호 (1~6)
<Boolean>        = ON, OFF 또는 1, 0
<NRf>            = 부동소수점 (NR1, NR2, NR3)
<String>         = 문자열 (따옴표 포함)
<Multiplier>     = EX, PE, T, G, MA, K, M, U, N, P, F
<Unit>           = V, A, S, HZ, MHZ
<Element>        = 1~6 또는 SIGMa, SIGMB, SIGMC
<Order>          = TOTal, DC 또는 1~500
<Range>          = 자동 범위 (5V~1000V, 5A~100A 등)
```

### 응답 형식
```
수치: 1.000E+00 형식
문자: 따옴표 없이
boolean: 0 또는 1
오류: 오류코드,"오류메시지"
```

---

## 🔧 사용 예제

### Python 연결 예제
```python
import socket
import time

# WT1800E 연결
WT1800 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
WT1800.connect(("192.168.1.100", 5555))
WT1800.settimeout(30)

# 기본 명령어
def send_command(cmd):
    WT1800.sendall((cmd + "\n").encode())
    return WT1800.recv(4096).decode().strip()

# 기기 식별
print(send_command("*IDN?"))  
# YOKOGAWA,WT1800,SN123456,V1.0

# 원격 모드 활성화
send_command(":COMMUNICATE:REMOTE ON")

# 입력 설정
send_command(":INPUT:WIRING 3PH3W")
send_command(":INPUT:VOLTAGE:RANGE 100V")
send_command(":INPUT:CURRENT:RANGE 10A")

# 측정 항목 설정
send_command(":NUMERIC:ITEM1 URMS,1")
send_command(":NUMERIC:ITEM2 IRMS,1")
send_command(":NUMERIC:ITEM3 P,1")
send_command(":NUMERIC:NUMBER 3")

# 측정값 읽기
values = send_command(":NUMERIC:VALUE?")
print(f"측정값: {values}")

# 연결 종료
WT1800.close()
```

### 🔬 SMA Motor 에너지 측정 예제 (✅ 적산값 포함)
```python
import socket
import time

def sma_integration_test():
    """SMA 스프링 1사이클(113.4s) 적산 에너지 측정"""
    
    # WT1800E 연결
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("192.168.1.100", 5555))
    sock.settimeout(60)
    
    def cmd(command):
        sock.sendall((command + "\n").encode())
        return sock.recv(4096).decode().strip()
    
    # 1. 기본 설정
    cmd("*RST")
    cmd(":COMMUNICATE:REMOTE ON")
    cmd(":INPUT:WIRING 1PH2W")           # DC 입력
    cmd(":INPUT:VOLTAGE:RANGE 50V")
    cmd(":INPUT:CURRENT:RANGE 20A")
    
    # 2. 적산 설정 ✅
    cmd(":INTEGRATE:MODE TIMER")
    cmd(":INTEGRATE:TIMER1 0,0,113")    # 113초 (1사이클)
    cmd(":INTEGRATE:ACAL ON")            # 자동 캘리브레이션
    cmd(":INTEGRATE:QMODE RMS")          # RMS 모드
    
    # 3. 측정 항목 설정 ✅ (적산값 포함)
    cmd(":NUMERIC:ITEM1 URMS,1")         # 전압
    cmd(":NUMERIC:ITEM2 IRMS,1")         # 전류
    cmd(":NUMERIC:ITEM3 P,1")            # 순간 전력
    cmd(":NUMERIC:ITEM4 WH,1")           # 유효 전력량 ✅
    cmd(":NUMERIC:ITEM5 TIME,1")         # 적산 시간 ✅
    cmd(":NUMERIC:ITEM6 AH,1")           # 전하량 ✅
    cmd(":NUMERIC:ITEM7 WHP,1")          # 양극 전력량 ✅
    cmd(":NUMERIC:ITEM8 WQ,1")           # 무효 전력량 ✅
    cmd(":NUMERIC:NUMBER 8")
    cmd(":NUMERIC:FORMAT ASCII")
    
    # 4. 반복 측정 (10사이클)
    results = []
    for cycle in range(1, 11):
        print(f"\n=== Cycle {cycle} ===")
        
        # 적산 리셋 및 시작
        cmd(":INTEGRATE:RESET")
        cmd(":INTEGRATE:START")
        print(f"적산 시작: {time.strftime('%H:%M:%S')}")
        
        # 113.4초 대기
        time.sleep(114)
        
        # 적산 중지
        cmd(":INTEGRATE:STOP")
        print(f"적산 종료: {time.strftime('%H:%M:%S')}")
        
        # 적산값 읽기 ✅
        response = cmd(":NUMERIC:VALUE?")
        values = response.split(',')
        
        # 데이터 파싱
        data = {
            'cycle': cycle,
            'urms': float(values[0]),      # 전압 (V)
            'irms': float(values[1]),      # 전류 (A)
            'power': float(values[2]),     # 순간 전력 (W)
            'wh': float(values[3]),        # 적산 전력량 (Wh) ✅
            'time': float(values[4]),      # 적산 시간 (s) ✅
            'ah': float(values[5]),        # 적산 전하량 (Ah) ✅
            'whp': float(values[6]),       # 양극 전력량 (Wh)
            'wq': float(values[7]),        # 무효 전력량 (Varh)
        }
        
        # 평균값 계산
        data['avg_power'] = (data['wh'] / (data['time'] / 3600))  # W
        data['avg_current'] = (data['ah'] / (data['time'] / 3600))  # A
        
        results.append(data)
        
        # 출력
        print(f"WH(전력량): {data['wh']:.3f} Wh")
        print(f"AH(전하량): {data['ah']:.3f} Ah")
        print(f"TIME: {data['time']:.1f} s")
        print(f"평균 전력: {data['avg_power']:.1f} W")
        print(f"평균 전류: {data['avg_current']:.3f} A")
    
    # 5. 통계 분석
    print(f"\n\n=== 10 Cycles Statistics ===")
    wh_values = [r['wh'] for r in results]
    ah_values = [r['ah'] for r in results]
    avg_pwr = [r['avg_power'] for r in results]
    
    import statistics
    print(f"WH (Wh): {statistics.mean(wh_values):.2f} ± {statistics.stdev(wh_values):.2f}")
    print(f"AH (Ah): {statistics.mean(ah_values):.3f} ± {statistics.stdev(ah_values):.3f}")
    print(f"Avg Power (W): {statistics.mean(avg_pwr):.1f} ± {statistics.stdev(avg_pwr):.1f}")
    print(f"총 에너지: {sum(wh_values):.1f} Wh")
    print(f"총 전하: {sum(ah_values):.2f} Ah")
    
    # 연결 종료
    sock.close()

# 실행
if __name__ == "__main__":
    sma_integration_test()
```

---

## ⚠️ 중요 주의사항

### 1. ✅ 적산값(Integration Values) 읽기 (매뉴얼의 숨겨진 정보)

**문제:** INTEGrate 그룹에는 `:INTEGrate:VALue?` 명령어가 없음!

**해결책:** MEASure 함수를 통해 간접 접근
```scpi
# 올바른 방법:
:NUMERIC:ITEM1 WH,1           # 유효 전력량 (Wh)
:NUMERIC:ITEM2 AH,1           # 전하량 (Ah)
:NUMERIC:ITEM3 WS,1           # 피상 전력량 (VAh)
:NUMERIC:ITEM4 WQ,1           # 무효 전력량 (Varh)
:NUMERIC:ITEM5 TIME,1         # 적산 시간 (초)
:NUMERIC:VALUE?               # 모든 값 한번에 읽기

# 평균값 계산 (사용자 정의 함수):
:MEASURE:FUNCTION1:EXPRESSION "WH(1)/TIME(1)*3600"
:MEASURE:FUNCTION1:NAME "Avg_Power"
:MEASURE:FUNCTION1:UNIT "W"
```

**단위 주의:**
- WH = Watt-Hour (에너지, 전력 아님!)
- 평균 전력 = WH / (TIME/3600) [W]

### 2. 적산 시퀀스 순서 (중요!)
```scpi
❌ 틀린 순서:
:INTEGRATE:RESET
:NUMERIC:VALUE?      ← 0값만 나옴

✅ 올바른 순서:
:INTEGRATE:RESET     ← 값 초기화
:INTEGRATE:START     ← 적산 시작
[측정 수행]
:INTEGRATE:STOP      ← 적산 중지
:NUMERIC:VALUE?      ← 적산된 값 읽기
:INTEGRATE:RESET     ← 다음 주기 준비
```

### 3. 오버랩 명령 (Overlap Commands)
- FILE:LOAD:*, FILE:SAVE:*, HCOPy:*, IMAGe:*, HSPeed:STARt/STOP
- 항상 *WAI 또는 *OPC? 사용하여 완료 확인

### 4. 데이터 동기화
- 측정 완료 후 :NUMeric:VALUE? 사용
- :STATUS:CONDITION?로 업데이트 확인

### 5. 배치 명령
```
:COMMUNICATE:HEADER OFF;:NUMERIC:VALUE?
```

### 6. 오류 처리
```
:STATUS:ERROR?  → 오류 코드와 메시지 확인
*CLS            → 오류 큐 클리어
```

### 7. 타임아웃 설정
- 소켓 타임아웃: 10~30초 권장
- 파일 로드/저장 시 더 길게 설정
- 적산 측정 시 타임아웃 > 적산시간 필수

### 8. DC 측정 시 주의사항 (SMA Motor)
```scpi
:INPUT:WIRING 1PH2W              # DC 입력 지정
:INTEGRATE:ACAL ON               # 자동 캘리브레이션 권장
[:INPUT]:NULL:STATe ON           # 영점 오류 제거
[:INPUT]:VOLTAGE:AUTO ON
[:INPUT]:CURRENT:AUTO ON
```

---

**마지막 업데이트:** 2024년 11월 7일  
**총 명령어:** 275개 이상  
**적용 모델:** Yokogawa WT1800E  
**참고:** IM WT1801-17EN_programming.pdf 기반
