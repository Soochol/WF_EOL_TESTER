//****************************************************************************
///****************************************************************************
//*****************************************************************************
//**
//** File Name
//** ----------
//**
//** AXC.PAS
//**
//** COPYRIGHT (c) AJINEXTEK Co., LTD
//**
//*****************************************************************************
//*****************************************************************************
//**
//** Description
//** -----------
//** Ajinextek Counter Library Header File
//** 
//**
//*****************************************************************************
//*****************************************************************************
//**
//** Source Change Indices
//** ---------------------
//** 
//** (None)
//**
//**
//*****************************************************************************
//*****************************************************************************
//**
//** Website
//** ---------------------
//**
//** http://www.ajinextek.com
//**
//*****************************************************************************
//*****************************************************************************
//*/
//

unit AXC;

interface

uses Windows, Messages, AXHS;


    //========== 보드 및 모듈 정보
    // CNT 모듈이 있는지 확인
    function AxcInfoIsCNTModule (upStatus : PDWord) : DWord; stdcall;

    // CNT 모듈 No 확인
    function AxcInfoGetModuleNo (lBoardNo : LongInt; lModulePos : LongInt; lpModuleNo : PLongInt) : DWord; stdcall;

    // CNT 입출력 모듈의 개수 확인
    function AxcInfoGetModuleCount (lpModuleCount : PLongInt) : DWord; stdcall;

    // 지정한 모듈의 카운터 입력 채널 개수 확인
    function AxcInfoGetChannelCount (lModuleNo : LongInt; lpCount : PLongInt) : DWord; stdcall;

    // 시스템에 장착된 카운터의 전 채널 수를 확인
    function AxcInfoGetTotalChannelCount (lpChannelCount : PLongInt) : DWord; stdcall;

    // 지정한 모듈 번호로 베이스 보드 번호, 모듈 위치, 모듈 ID 확인
    function AxcInfoGetModule (lModuleNo : LongInt; lpBoardNo : PLongInt; lpModulePos : PLongInt; upModuleID : PDWord) : DWord; stdcall;

    // 해당 모듈이 제어가 가능한 상태인지 반환한다.
    function AxcInfoGetModuleStatus (lModuleNo : LongInt) : DWord; stdcall;

    function AxcInfoGetFirstChannelNoOfModuleNo (lModuleNo : LongInt; lpChannelNo : PLongInt) : DWord; stdcall;
    function AxcInfoGetModuleNoOfChannelNo (lChannelNo : LongInt; lpModuleNo : PLongInt) : DWord; stdcall;

    // 카운터 모듈의 Encoder 입력 방식을 설정 합니다.
    // dwMethod --> 0x00 : Sign and pulse, x1 multiplication
    // dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    // dwMethod --> 0x08 : Sign and pulse, x2 multiplication
    // dwMethod --> 0x09 : Increment and decrement pulses, x1 multiplication
    // dwMethod --> 0x0A : Increment and decrement pulses, x2 multiplication
    // SIO-CN2CH/HPC4의 경우
    // dwMethod --> 0x00 : Up/Down 방식, A phase : 펄스, B phase : 방향
    // dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    // SIO-LCM4의 경우
    // dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    function AxcSignalSetEncInputMethod (lChannelNo : LongInt; dwMethod : DWord) : DWord; stdcall;

    // 카운터 모듈의 Encoder 입력 방식을 설정 합니다.
    // *dwpUpMethod --> 0x00 : Sign and pulse, x1 multiplication
    // *dwpUpMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // *dwpUpMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // *dwpUpMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    // *dwpUpMethod --> 0x08 : Sign and pulse, x2 multiplication
    // *dwpUpMethod --> 0x09 : Increment and decrement pulses, x1 multiplication
    // *dwpUpMethod --> 0x0A : Increment and decrement pulses, x2 multiplication
    // SIO-CN2CH/HPC4의 경우
    // dwMethod --> 0x00 : Up/Down 방식, A phase : 펄스, B phase : 방향
    // dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    // SIO-LCM4의 경우
    // dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    function AxcSignalGetEncInputMethod (lChannelNo : LongInt; dwpUpMethod : PDWord) : DWord; stdcall;

    // 카운터 모듈의 트리거를 설정 합니다.
    // dwMode -->  0x00 : Latch
    // dwMode -->  0x01 : State
    // dwMode -->  0x02 : Special State    --> SIO-CN2CH 전용
    // SIO-CN2CH의 경우
    // dwMode -->  0x00 : 절대 위치 트리거 또는 주기 위치 트리거.
    // 주의 : 제품마다 기능이 서로 다르기 때문에 구별하여 사용 필요.
    // dwMode -->  0x01 : 시간 주기 트리거(AxcTriggerSetFreq로 설정)
    // SIO-HPC4의 경우
    // dwMode -->  0x00 : timer mode with counter & frequncy.
    // dwMode -->  0x01 : timer mode.
    // dwMode -->  0x02 : absolute mode[with fifo].
    // dwMode -->  0x03 : periodic mode.[Default]
    function AxcTriggerSetFunction (lChannelNo : LongInt; dwMode : DWord) : DWord; stdcall;

    // 카운터 모듈의 트리거 설정을 확인 합니다.
    // *dwMode -->  0x00 : Latch
    // *dwMode -->  0x01 : State
    // *dwMode -->  0x02 : Special State
    // SIO-CN2CH의 경우
    // *dwMode -->  0x00 : 절대 위치 트리거 또는 주기 위치 트리거.
    // 주의 : 제품마다 기능이 서로 다르기 때문에 구별하여 사용 필요.
    // *dwMode -->  0x01 : 시간 주기 트리거(AxcTriggerSetFreq로 설정)
    // SIO-HPC4의 경우
    // *dwMode -->  0x00 : timer mode with counter & frequncy.
    // *dwMode -->  0x01 : timer mode.
    // *dwMode -->  0x02 : absolute mode[with fifo].
    // *dwMode -->  0x03 : periodic mode.[Default]
    function AxcTriggerGetFunction (lChannelNo : LongInt; dwpMode : PDWord) : DWord; stdcall;

    // dwUsage --> 0x00 : Trigger Not use
    // dwUsage --> 0x01 : Trigger use
    function AxcTriggerSetNotchEnable (lChannelNo : LongInt; dwUsage : DWord) : DWord; stdcall;

    // *dwUsage --> 0x00 : Trigger Not use
    // *dwUsage --> 0x01 : Trigger use
    function AxcTriggerGetNotchEnable (lChannelNo : LongInt; dwpUsage : PDWord) : DWord; stdcall;


    // 카운터 모듈의 Capture 극성을 설정 합니다.(External latch input polarity)
    // dwCapturePol --> 0x00 : Signal OFF -> ON
    // dwCapturePol --> 0x01 : Signal ON -> OFF
    function AxcSignalSetCaptureFunction (lChannelNo : LongInt; dwCapturePol : DWord) : DWord; stdcall;

    // 카운터 모듈의 Capture 극성 설정을 확인 합니다.(External latch input polarity)
    // *dwCapturePol --> 0x00 : Signal OFF -> ON
    // *dwCapturePol --> 0x01 : Signal ON -> OFF
    function AxcSignalGetCaptureFunction (lChannelNo : LongInt; dwpCapturePol : PDWord) : DWord; stdcall;

    // 카운터 모듈의 Capture 위치를 확인 합니다.(External latch)
    // *dbpCapturePos --> Capture position 위치
    function AxcSignalGetCapturePos (lChannelNo : LongInt; dbpCapturePos : PDouble) : DWord; stdcall;

    // 카운터 모듈의 카운터 값을 확인 합니다.
    // *dbpActPos --> 카운터 값
    function AxcStatusGetActPos (lChannelNo : LongInt; dbpActPos : PDouble) : DWord; stdcall;

    // 카운터 모듈의 카운터 값을 dbActPos 값으로 설정 합니다.
    function AxcStatusSetActPos (lChannelNo : LongInt; dbActPos : Double) : DWord; stdcall;

    // 카운터 모듈의 트리거 위치를 설정합니다.
    // 카운터 모듈의 트리거 위치는 2개까지만 설정 할 수 있습니다.
    function AxcTriggerSetNotchPos (lChannelNo : LongInt; dbLowerPos : Double; dbUpperPos : Double) : DWord; stdcall;

    // 카운터 모듈의 설정한 트리거 위치를 확인 합니다.
    function AxcTriggerGetNotchPos (lChannelNo : LongInt; dbpLowerPos : PDouble; dbpUpperPos : PDouble) : DWord; stdcall;

    // 카운터 모듈의 트리거 출력을 강제로 합니다.
    // dwOutVal --> 0x00 : 트리거 출력 '0'
    // dwOutVal --> 0x01 : 트리거 출력 '1'
    function AxcTriggerSetOutput (lChannelNo : LongInt; dwOutVal : DWord) : DWord; stdcall;

    // 카운터 모듈의 상태를 확인합니다.
    // Bit '0' : Carry (카운터 현재치가 덧셈 펄스에 의해 카운터 상한치를 넘어 0로 바뀌었을 때 1스캔만 ON으로 합니다.)
    // Bit '1' : Borrow (카운터 현재치가 뺄셈 펄스에 의해 0을 넘어 카운터 상한치로 바뀌었을 때 1스캔만 ON으로 합니다.)
    // Bit '2' : Trigger output status
    // Bit '3' : Latch input status
    function AxcStatusGetChannel (lChannelNo : LongInt; dwpChannelStatus : PDWord) : DWord; stdcall;


    // SIO-CN2CH 전용 함수군
    //
    // 카운터 모듈의 위치 단위를 설정한다.
    // 실제 위치 이동량에 대한 펄스 갯수를 설정하는데,
    // ex) 1mm 이동에 1000가 필요하다면dMoveUnitPerPulse = 0.001로 입력하고,
    //     이후 모든 함수의 위치와 관련된 값을 mm 단위로 설정하면 된다.
    function AxcMotSetMoveUnitPerPulse (lChannelNo : LongInt; dMoveUnitPerPulse : Double) : DWord; stdcall;

    // 카운터 모듈의 위치 단위를 확인한다.
    function AxcMotGetMoveUnitPerPulse (lChannelNo : LongInt; dpMoveUnitPerPuls : PDouble) : DWord; stdcall;

    // 카운터 모듈의 엔코더 입력 카운터를 반전 기능을 설정한다.
    // dwReverse --> 0x00 : 반전하지 않음.
    // dwReverse --> 0x01 : 반전.
    function AxcSignalSetEncReverse (lChannelNo : LongInt; dwReverse : DWord) : DWord; stdcall;

    // 카운터 모듈의 엔코더 입력 카운터를 반전 기능을 설정을 확인한다.
    function AxcSignalGetEncReverse (lChannelNo : LongInt; dwpReverse : PDWord) : DWord; stdcall;

    // 카운터 모듈의 Encoder 입력 신호를 선택한다.
    // dwSource -->  0x00 : 2(A/B)-Phase 신호.
    // dwSource -->  0x01 : Z-Phase 신호.(방향성 없음.)
    function AxcSignalSetEncSource (lChannelNo : LongInt; dwSource : DWord) : DWord; stdcall;

    // 카운터 모듈의 Encoder 입력 신호 선택 설정을 확인한다.
    function AxcSignalGetEncSource (lChannelNo : LongInt; dwpSource : PDWord) : DWord; stdcall;

    // 카운터 모듈의 트리거 출력 범위 중 하한 값을 설정한다.
    // 위치 주기 트리거 제품의 경우 위치 주기로 트리거 출력을 발생시킬 범위 중 하한 값을 설정한다.
    // 절대 위치 트리거 제품의 경우 Ram 시작 번지의 트리거 정보의 적용 기준 위치를 설정한다.
    // 단위 : AxcMotSetMoveUnitPerPulse로 설정한 단위.
    // Note : 하한값은 상한값보다 작은값을 설정하여야 합니다.
    function AxcTriggerSetBlockLowerPos (lChannelNo : LongInt; dLowerPosition : Double) : DWord; stdcall;

    // 카운터 모듈의 트리거 출력 범위 중 하한 값을 확인한다.
    function AxcTriggerGetBlockLowerPos (lChannelNo : LongInt; dpLowerPosition : PDouble) : DWord; stdcall;

    // 카운터 모듈의 트리거 출력 범위 중 상한 값을 설정한다.
    // 위치 주기 트리거 제품의 경우 위치 주기로 트리거 출력을 발생시킬 범위 중 상한 값을 설정한다.
    // 절대 위치 트리거 제품의 경우 트리거 정보가 설정된 Ram 의 마지막 번지의 트리거 정보가 적용되는 위치로 사용된다.
    // 단위 : AxcMotSetMoveUnitPerPulse로 설정한 단위.
    // Note : 상한값은 하한값보다 큰값을 설정하여야 합니다.
    function AxcTriggerSetBlockUpperPos (lChannelNo : LongInt; dUpperPosition : Double) : DWord; stdcall;
    // 카운터 모듈의 트리거 출력 범위 중 하한 값을 설정한다.
    function AxcTriggerGetBlockUpperPos (lChannelNo : LongInt; dpUpperrPosition : PDouble) : DWord; stdcall;

    // 카운터 모듈의 위치 주기 모드 트리거에 사용되는 위치 주기를 설정한다.
    // 단위 : AxcMotSetMoveUnitPerPulse로 설정한 단위.
    function AxcTriggerSetPosPeriod (lChannelNo : LongInt; dPeriod : Double) : DWord; stdcall;

    // 카운터 모듈의 위치 주기 모드 트리거에 사용되는 위치 주기를 확인한다.
    function AxcTriggerGetPosPeriod (lChannelNo : LongInt; dpPeriod : PDouble) : DWord; stdcall;

    // 카운터 모듈의 위치 주기 모드 트리거 사용시 위치 증감에 대한 유효기능을 설정한다.
    // dwDirection -->  0x00 : 카운터의 증/감에 대하여 트리거 주기 마다 출력.
    // dwDirection -->  0x01 : 카운터가 증가 할때만 트리거 주기 마다 출력.
    // dwDirection -->  0x01 : 카운터가 감소 할때만 트리거 주기 마다 출력.
    function AxcTriggerSetDirectionCheck (lChannelNo : LongInt; dwDirection : DWord) : DWord; stdcall;
    // 카운터 모듈의 위치 주기 모드 트리거 사용시 위치 증감에 대한 유효기능 설정을 확인한다.
    function AxcTriggerGetDirectionCheck (lChannelNo : LongInt; dwpDirection : PDWord) : DWord; stdcall;

    // 카운터 모듈의 위치 주기 모드 트리거 기능의 범위, 위치 주기를 한번에 설정한다.
    // 위치 설정 단위 :  AxcMotSetMoveUnitPerPulse로 설정한 단위.
    function AxcTriggerSetBlock (lChannelNo : LongInt; dLower : Double; dUpper : Double; dABSod : Double) : DWord; stdcall;

    // 카운터 모듈의 위치 주기 모드 트리거 기능의 범위, 위치 주기를 설정을 한번에 확인한다.
    function AxcTriggerGetBlock (lChannelNo : LongInt; dpLower : PDouble; dpUpper : PDouble; dpABSod : PDouble) : DWord; stdcall;

    // 카운터 모듈의 트리거 출력 펄스 폭을 설정한다.
    // 단위 : uSec
    function AxcTriggerSetTime (lChannelNo : LongInt; dTrigTime : Double) : DWord; stdcall;

    // 카운터 모듈의 트리거 출력 펄스 폭 설정을 확인한다.
    function AxcTriggerGetTime (lChannelNo : LongInt; dpTrigTime : PDouble) : DWord; stdcall;

    // 카운터 모듈의 트리거 출력 펄스의 출력 레벨을 설정한다.
    // dwLevel -->  0x00 : 트리거 출력시 'Low' 레벨 출력.
    // dwLevel -->  0x01 : 트리거 출력시 'High' 레벨 출력.
    function AxcTriggerSetLevel (lChannelNo : LongInt; dwLevel : DWord) : DWord; stdcall;
    // 카운터 모듈의 트리거 출력 펄스의 출력 레벨 설정을 확인한다.
    function AxcTriggerGetLevel (lChannelNo : LongInt; dwpLevel : PDWord) : DWord; stdcall;

    // 카운터 모듈의 주파수 트리거 출력 기능에 필요한 주파수를 설정한다.
    // 단위 : Hz, 범위 : 1Hz ~ 500 kHz
    function AxcTriggerSetFreq (lChannelNo : LongInt; dwFreqency : DWord) : DWord; stdcall;
    // 카운터 모듈의 주파수 트리거 출력 기능에 필요한 주파수를 설정을 확인한다.
    function AxcTriggerGetFreq (lChannelNo : LongInt; dwpFreqency : PDWord) : DWord; stdcall;

    // 카운터 모듈의 지정 채널에 대한 범용 출력 값을 설정한다.
    // dwOutput 범위 : 0x00 ~ 0x0F, 각 채널당 4개의 범용 출력
    function AxcSignalWriteOutput (lChannelNo : LongInt; dwOutput : DWord) : DWord; stdcall;

    // 카운터 모듈의 지정 채널에 대한 범용 출력 값을 확인한다.
    function AxcSignalReadOutput (lChannelNo : LongInt; dwpOutput : PDWord) : DWord; stdcall;

    // 카운터 모듈의 지정 채널에 대한 범용 출력 값을 비트 별로 설정한다.
    // lBitNo 범위 : 0 ~ 3, 각 채널당 4개의 범용 출력
    function AxcSignalWriteOutputBit (lChannelNo : LongInt; lBitNo : LongInt; uOnOff : DWord) : DWord; stdcall;
    // 카운터 모듈의 지정 채널에 대한 범용 출력 값을 비트 별로 확인 한다.
    // lBitNo 범위 : 0 ~ 3
    function AxcSignalReadOutputBit (lChannelNo : LongInt; lBitNo : LongInt; upOnOff : PDWord) : DWord; stdcall;

    // 카운터 모듈의 지정 채널에 대한 범용 입력 값을 확인한다.
    function AxcSignalReadInput (lChannelNo : LongInt; dwpInput : PDWord) : DWord; stdcall;

    // 카운터 모듈의 지정 채널에 대한 범용 입력 값을 비트 별로 확인 한다.
    // lBitNo 범위 : 0 ~ 3
    function AxcSignalReadInputBit (lChannelNo : LongInt; lBitNo : LongInt; upOnOff : PDWord) : DWord; stdcall;

    // 카운터 모듈의 트리거 출력을 활성화 한다.
    // 현재 설정된 기능에 따라 트리거 출력이 최종적으로 출력할 것인지 설정한다.
    function AxcTriggerSetEnable (lChannelNo : LongInt; dwUsage : DWord) : DWord; stdcall;

    // 카운터 모듈의 트리거 출력 활설화 설정 내용을 확인하다.
    function AxcTriggerGetEnable (lChannelNo : LongInt; dwpUsage : PDWord) : DWord; stdcall;

    // 카운터 모듈의 절대위치 트리거 기능을 위해 설정된 RAM 내용을 확인한다.
    // dwAddr 범위 : 0x0000 ~ 0x1FFFF;
    function AxcTriggerReadAbsRamData (lChannelNo : LongInt; dwAddr : DWord; dwpData : PDWord) : DWord; stdcall;

    // 카운터 모듈의 절대위치 트리거 기능을 위해 필요한 RAM 내용을 설정한다.
    // dwAddr 범위 : 0x0000 ~ 0x1FFFF;
    function AxcTriggerWriteAbsRamData (lChannelNo : LongInt; dwAddr : DWord; dwData : DWord) : DWord; stdcall;

    // 지정 CNT 채널의 절대 위치 트리거 기능을 위한 DWORD형 위치 정보를 설정한다.
    //----------------------------------------------------------------------------------------------------------------------------------
    // 1. AXT_SIO_CN2CH인 경우
    // dwTrigNum --> 131072(=0x20000) 개까지 설정 가능
    // dwTrigPos --> DWORD형 Data 입력 가능
    // dwDirection --> 0x0(default) : dwTrigPos[0], dwTrigPos[1] ..., dwTrigPos[dwTrigNum - 1] 순으로 Data를 Write 한다.
    //     0x1    : dwTrigPos[dwTrigNum - 1], dwTrigPos[dwTrigNum - 2], ..., dwTrigPos[0] 순으로 Data를 Write 한다.
    // *참고* 1) dwDirection: Data Write 순서만 다를 뿐 기능상의 차이 없음
    //    2) AXC Manual의 AxcTriggerSetAbs - Description을 참고하여 data를 가공 후 사용해야 함
    //----------------------------------------------------------------------------------------------------------------------------------
    // 2. AXT_SIO_HPC4인 경우
    // dwTrigNum --> 500 개까지 설정 가능
    // dwTrigPos --> DWORD형 Data 입력 가능
    // dwDirection --> 0x0(default) : 사용되지 않는 변수로, 입력하지 않아도 된다.
    //----------------------------------------------------------------------------------------------------------------------------------
    // 3. AXT_SIO_RCNT2RTEX, AXT_SIO_RCNT2MLIII, AXT_SIO_RCNT2SIIIH, AXT_SIO_RCNT2SIIIH_R인 경우
    // dwTrigNum --> 0x200(=512) 개까지 설정 가능
    // dwTrigPos --> DWORD형 data 입력 가능
    // dwDirection --> 0x0(default) : 사용되지 않는 변수로, 입력하지 않아도 된다.
    //----------------------------------------------------------------------------------------------------------------------------------
    function AxcTriggerSetAbs (lChannelNo : LongInt; dwTrigNum : DWord; dwTrigPos : PDWord; 0 : DWORD dwDirection =) : DWord; stdcall;


    // 지정 CNT 채널의 절대 위치 트리거 기능을 위한 double형 위치 정보를 설정한다.
    //----------------------------------------------------------------------------------------------------------------------------------
    // 1. AXT_SIO_CN2CH인 경우
    // dwTrigNum --> 4194304(=0x20000*32) 개까지 설정 가능
    // dTrigPos  --> double형 data 입력 가능
    // dwDirection --> 0x0(default) : dTrigPos[0], dTrigPos[1] ..., dTrigPos[dwTrigNum - 1] 순으로 Data를 Write 한다.
    //     0x1    : dTrigPos[dwTrigNum - 1], dTrigPos[dwTrigNum - 2], ..., dTrigPos[0] 순으로 Data를 Write 한다.
    // *참고* 1) dwDirection: Data Write 순서만 다를 뿐 기능상의 차이 없음
    //----------------------------------------------------------------------------------------------------------------------------------
    // 2. AXT_SIO_RCNT2RTEX, AXT_SIO_RCNT2MLIII, AXT_SIO_RCNT2SIIIH_R인 경우
    // dwTrigNum --> 0x200(=512) 개까지 설정 가능
    // dTrigPos  --> double형 data 입력 가능
    // dwDirection --> 0x0(default) : 사용되지 않는 변수로, 입력하지 않아도 된다.
    //----------------------------------------------------------------------------------------------------------------------------------
    function AxcTriggerSetAbsDouble (lChannelNo : LongInt; dwTrigNum : DWord; dTrigPos : PDouble; 0 : DWORD dwDirection =) : DWord; stdcall;

    ////////////////// LCM4_10_Version/////////////////////////////////////////////////////////////

    // 카운터 모듈의 PWM 출력을 활성화한다.
    function AxcTriggerSetPwmEnable (lChannelNo : LongInt; bEnable : Boolean) : DWord; stdcall;
    // 카운터 모듈의 PWM 출력 활성화 상태를 확인한다.
    function AxcTriggerGetPwmEnable (lChannelNo : LongInt; bEnable : bool*) : DWord; stdcall;
    // 카운터 모듈의 PWM 출력모드를 설정한다.
    // dwMode : PWM 출력모드
    // [0] : Manual (Manual로 설정된 PWM Data)
    // [1] : Auto (속도 Table)
    function AxcTriggerSetPwmOutMode (lChannelNo : LongInt; dwMode : DWord) : DWord; stdcall;
    // 카운터 모듈의 PWM 출력모드를 확인한다.
    // dwMode : PWM 출력모드
    // [0] : Manual (Manual로 설정된 PWM Data)
    // [1] : Auto (속도 Table)
    function AxcTriggerGetPwmOutMode (lChannelNo : LongInt; dwpMode : PDWord) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 2-D 절대속도에서 PWM 신호를 출력하기 위해 필요한 속도 정보를 설정한다.
    // dMinVel : dMinVel
    // dMaxVel : dMaxVel
    // dVelInterval : 속도 테이블에서의 구간별 속도 Interval
    // ※주의 : dMinVel부터 dVelInterval 간격으로 최대 5000개의 속두구간이 나뉜다.
    //          (((dMaxVel-dMinVel) / dVelInterval) <= 5000)이 만족하여야 한다.
    function AxcTriggerSetPwmVelInfo (lChannelNo : LongInt; dMinVel : Double; dMaxVel : Double; dVelInterval : Double) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 2-D 절대속도에서 PWM 신호를 출력하기 위해 필요한 속도 정보를 확인한다.
    function AxcTriggerGetPwmVelInfo (lChannelNo : LongInt; dpMinVel : PDouble; dpMaxVel : PDouble; dpVelInterval : PDouble) : DWord; stdcall;
    // 카운터 모듈의 PWM 출력에서 Pulse 폭 제어방식을 설정한다.
    // dwMode : Pulse 폭 제어
    // [0] : DutyRatio
    // [1] : PulseWidth
    function AxcTriggerSetPwmPulseControl (lChannelNo : LongInt; dwMode : DWord) : DWord; stdcall;
    //  카운터 모듈의 PWM 출력에서 Pulse 조절방식을 확인다.
    // dwpMode : Pulse 폭 제어
    // [0] : DutyRatio
    // [1] : PulseWidth
    function AxcTriggerGetPwmPulseControl (lChannelNo : LongInt; dwpMode : PDWord) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 2-D 절대속도에서 PWM 신호를 출력하기 위해 필요한 정보를 설정한다.
    // pwm 출력모드가 Manual 인 경우에만 유효하다
    // dFrequency :  (0.017 ~ 1M) 까지 설정이 가능하다. (Hz 단위)
    // dData : Pulse 폭 관련 Data 를 입력하며 Pulse Control 방식에 따라 Data 형식이 다르다.
    // Pulse 폭 제어방식이 DutyRatio인 경우 DutyRatio
    // Pulse 폭 제어방식이 PulseWidth 인 경우 PulseWidth (us단위)
    function AxcTriggerSetPwmManualData (lChannelNo : LongInt; dFrequency : Double; dData : Double) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 2-D 절대속도에서 PWM 신호를 출력하기 위해 필요한 정보를 확인한다.
    function AxcTriggerGetPwmManualData (lChannelNo : LongInt; dpFrequency : PDouble; dpData : PDouble) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 2-D 절대속도에서 PWM 신호를 출력하기 위해 필요한 정보를 설정한다.
    // lDataCnt : 설정 할 트리거 정보의 전체 개수
    // dpVel : dpVel[0],dpVel[1]....dpVel[DataCnt -1] 순서로 입력 가능
    // dwpFrequency : dwpFrequency[0],dwpFrequency[1]....dwpFrequency[DataCnt-1] 순서로 입력 가능(0.017 ~ 1M) 까지 설정이 가능하다.
    // dData : Pulse 폭 관련 Data 를 입력하며 Pulse Control 방식에 따라 Data 형식이 다르다.
    // Pulse 폭 제어방식이 DutyRatio인 경우 DutyRatio
    // Pulse 폭 제어방식이 PulseWidth 인 경우 PulseWidth (us단위)
    // ※주의 :
    //    1) dpVel, dwpFrequency, dwpDutyRatio 의 배열 개수를 주의하여 사용해야한다.
    //  - 속도가 0인 구간에서는 PWM 출력이 불가하다.
    //    3) PWM Enable 상태에서는 사용할 수 없다.
    function AxcTriggerSetPwmPatternData (lChannelNo : LongInt; lDataCnt : LongInt; dpVel : PDouble; dpFrequency : PDouble; dpData : PDouble) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 2-D 절대속도에서 PWM 신호를 출력하기 위해 필요한 정보를 설정한다.
    function AxcTriggerSetPwmData (lChannelNo : LongInt; dVel : Double; dFrequency : Double; dData : Double) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 2-D 절대속도에서 PWM 신호를 출력하기 위해 필요한 정보를 확인한다.
    function AxcTriggerGetPwmData (lChannelNo : LongInt; dVel : Double; dpFrequency : PDouble; dpData : PDouble) : DWord; stdcall;
    // 카운터 모듈의 속도 값을 확인 합니다.
    function AxcStatusReadActVel (lChannelNo : LongInt; dpActVel : PDouble) : DWord; stdcall;
    // 카운터 모듈의 2D 속도 값을 확인 합니다.
    function AxcStatusRead2DActVel (lChannelNo : LongInt; dpActVel : PDouble) : DWord; stdcall;
    // 카운터 모듈의 Position 값을 초기화 한다.
    function AxcStatusSetActPosClear (lChannelNo : LongInt) : DWord; stdcall;
    ////////////////// HPC4_30_Version
    // 카운터 모듈의 각 테이블에 할당된 트리거 출력의 레벨을 설정한다.
    // uLevel : 트리거 출력 신호의 Active Level
    //   [0]  : 트리거 출력시 'Low' 레벨 출력.
    //   [1]  : 트리거 출력시 'High' 레벨 출력.
    function AxcTableSetTriggerLevel (lModuleNo : LongInt; lTablePos : LongInt; uLevel : DWord) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 지정된 트리거 출력의 레벨 설정값을 확인한다.
    function AxcTableGetTriggerLevel (lModuleNo : LongInt; lTablePos : LongInt; upLevel : PDWord) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 할당된 트리거 출력의 펄스 폭을 설정한다.
    // dTriggerTimeUSec : [Default 500ms], us단위로 지정
    function AxcTableSetTriggerTime (lModuleNo : LongInt; lTablePos : LongInt; dTriggerTimeUSec : Double) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 지정된 트리거 출력의 펄스 폭 설정값을 확인한다.
    function AxcTableGetTriggerTime (lModuleNo : LongInt; lTablePos : LongInt; dpTriggerTimeUSec : PDouble) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 할당 할 2개의 엔코더 입력 신호를 설정한다.
    // uEncoderInput1 [0-3]: 카운터 모듈에 입력되는 4개의 엔코더 신호중 하나
    // uEncoderInput2 [0-3]: 카운터 모듈에 입력되는 4개의 엔코더 신호중 하나
    function AxcTableSetEncoderInput (lModuleNo : LongInt; lTablePos : LongInt; uEncoderInput1 : DWord; uEncoderInput2 : DWord) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 할당 된 2개의 엔코더 입력 신호를 확인한다.
    function AxcTableGetEncoderInput (lModuleNo : LongInt; lTablePos : LongInt; upEncoderInput1 : PDWord; upEncoderInput2 : PDWord) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 할당 할 트리거 출력 포트를 설정한다.
    // uTriggerOutport [0x0-0xF]: Bit0: 트리거 출력 0, Bit1: 트리거 출력 1, Bit2: 트리거 출력 2, Bit3: 트리거 출력 3
    // Ex) 0x3(3)   : 출력 0, 1에 트리거 신호를 출력하는 경우
    //     0xF(255) : 출력 0, 1, 2, 3에 트리거 신호를 출력하는 경우
    function AxcTableSetTriggerOutport (lModuleNo : LongInt; lTablePos : LongInt; uTriggerOutport : DWord) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 할당 된 트리거 출력 포트를 확인한다.
    function AxcTableGetTriggerOutport (lModuleNo : LongInt; lTablePos : LongInt; upTriggerOutport : PDWord) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 설정된 트리거 위치에 대한 허용 오차 범위를 설정한다.
    // dErrorRange  : 지정 축의 Unit단위로 트리거 위치에 대한 허용 오차 범위를 설정
    function AxcTableSetErrorRange (lModuleNo : LongInt; lTablePos : LongInt; dErrorRange : Double) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 설정된 트리거 위치에 대한 허용 오차 범위를 확인한다.
    function AxcTableGetErrorRange (lModuleNo : LongInt; lTablePos : LongInt; dpErrorRange : PDouble) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 설정된 정보로(트리거 출력 Port, 트리거 펄스 폭) 트리거를 1개 발생시킨다.
    // ※ 주의 : 1) 트리거가 Disable되어 있으면 이 함수는 자동으로 Enable시켜 트리거를 발생시킴
    //           2) Trigger Mode가 HPC4_PATTERN_TRIGGER 모드일 경우 이 함수는 자동으로 트리거 모드를 HPC4_RANGE_TRIGGER로 변경 함(하나의 트리거만 발생시키기 위해)
    function AxcTableTriggerOneShot (lModuleNo : LongInt; lTablePos : LongInt) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 설정된 정보로(트리거 출력 Port, 트리거 펄스 폭), 지정한 개수만큼 설정한 주파수로 트리거를 발생시킨다.
    // lTriggerCount     : 지정한 주파수를 유지하며 발생시킬 트리거 출력 개수
    // uTriggerFrequency : 트리거를 발생시킬 주파수
    // ※ 주의 : 1) 트리거가 Disable되어 있으면 이 함수는 자동으로 Enable시켜 패턴을 가진 트리거를 발생시킴
    //           2) Trigger Mode가 HPC4_PATTERN_TRIGGER 모드가 아닐 경우 이 함수는 자동으로 트리거 모드를 HPC4_PATTERN_TRIGGER로 변경 함
    function AxcTableTriggerPatternShot (lModuleNo : LongInt; lTablePos : LongInt; lTriggerCount : LongInt; uTriggerFrequency : DWord) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 설정된 패턴 트리거 설정 정보를(주파수, 카운터) 확인한다.
    function AxcTableGetPatternShotData (lModuleNo : LongInt; lTablePos : LongInt; lpTriggerCount : PLongInt; upTriggerFrequency : PDWord) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 트리거를 출력하는 방식을 설정한다.
    // uTrigMode : 트리거를 출력하는 방식을 설정한다.
    //   [0] HPC4_RANGE_TRIGGER   : 지정한 트리거 위치에 설정한 허용 범위안에 위치할 때 트리거를 출력하는 모드
    //   [1] HPC4_VECTOR_TRIGGER  : 지한 트리거 위치에 설정한 허용 범위와 벡터 방향이 일치할 때 트리거를 출력하는 모드
    //   [3] HPC4_PATTERN_TRIGGER : 위치와 무관하게 지정한 개수만큼 설정한 주파수로 트리거를 출력하는 모드
    function AxcTableSetTriggerMode (lModuleNo : LongInt; lTablePos : LongInt; uTrigMode : DWord) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 설정된 트리거를 출력하는 방식을 확인한다
    function AxcTableGetTriggerMode (lModuleNo : LongInt; lTablePos : LongInt; upTrigMode : PDWord) : DWord; stdcall;
    // 카운터 모듈의 각 테이블 별로 출력된 누적 트리거 갯수를 초기화 한다.
    function AxcTableSetTriggerCountClear (lModuleNo : LongInt; lTablePos : LongInt) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 2-D 절대위치에서 트리거 신호를 출력하기 위해 필요한 정보를 설정한다.
    // lTriggerDataCount : 설정 할 트리거 정보의 전체 개수
    //   [-1, 0]         : 등록된 트리거 정보 데이타 초기화
    // dpTriggerData     : 2-D 절대위치 트리거 정보(해당 배열의 개수는 lTriggerDataCount * 2가 되어야됨)
    //   *[0, 1]         : X[0], Y[0]
    // lpTriggerCount    : 입력한 2-D 절대 트리거 위치에서 트리거 조건 만족 시 발생시킬 트리거 갯수를 배열로 설정(해당 배열의 개수는 lTriggerDataCount)
    // dpTriggerInterval : TriggerCount 만큼 연속해서 트리거를 발생시킬때 유지 할 간격을 주파수 단위로 설정(해당 배열의 개수는 lTriggerDataCount)
    // ※주의 :
    //    1) 각 전달인자의 배열 개수를 주의하여 사용해야됩니다. 내부에서 사용되는 인자 보다 적은 배열을 지정하면 메모리 참조 오류가 발생 될 수 있음.
    //    2) Trigger Mode는 HPC4_RANGE_TRIGGER로 자동 변경됨
    //    3) 함수 내부에서 Trigger를 Disable한 후 모든 설정을 진행하며 완료 후 다시 Enable 시킴
    function AxcTableSetTriggerData (lModuleNo : LongInt; lTablePos : LongInt; lTriggerDataCount : LongInt; dpTriggerData : PDouble; lpTriggerCount : PLongInt; dpTriggerInterval : PDouble) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 트리거 신호를 출력하기 위해 설정한 트리거 설정 정보를 확인한다.
    // ※ 주의 : 각 테이블에 등록된 최대 트리거 데이타 개수를 모를 때는 아래와 같이 트리거 데이타 개수를 미리 파악한 후 사용하십시요.
    // Ex)      1) AxcTableGetTriggerData(lModuleNo, lTablePos, &lTriggerDataCount, NULL, NULL, NULL);
    //          2) dpTriggerData     = new double[lTriggerDataCount * 2];
    //          3) lpTriggerCount    = new long[lTriggerDataCount];
    //          4) dpTriggerInterval = new double[lTriggerDataCount];
    function AxcTableGetTriggerData (lModuleNo : LongInt; lTablePos : LongInt; lpTriggerDataCount : PLongInt; dpTriggerData : PDouble; lpTriggerCount : PLongInt; dpTriggerInterval : PDouble) : DWord; stdcall;

    // 카운터 모듈의 각 테이블에 2-D 절대위치에서 트리거 신호를 출력하기 위해 필요한 정보를 AxcTableSetTriggerData함수와 다른 방식으로 설정한다.
    // lTriggerDataCount : 설정 할 트리거 정보의 전체 개수
    // uOption : dpTriggerData 배열의 데이타 입력 방식을 지정
    //   [0]   : dpTriggerData 배열에 X Pos[0], Y Pos[0], X Pos[1], Y Pos[1] 순서로 입력
    //   [1]   : dpTriggerData 배열에 X Pos[0], Y Pos[0], Count, Inteval, X Pos[1], Y Pos[1], Count, Inteval 순서로 입력
    // ※주의 :
    //    1) dpTriggerData의 배열 개수를 주의하여 사용해야됩니다. 내부에서 사용되는 인자 보다 적은 배열을 지정하면 메모리 참조 오류가 발생 될 수 있음.
    //    2) Trigger Mode는 HPC4_RANGE_TRIGGER로 자동 변경됨
    //    3) 함수 내부에서 Trigger를 Disable한 후 모든 설정을 진행하며 완료 후 다시 Enable 시킴
    function AxcTableSetTriggerDataEx (lModuleNo : LongInt; lTablePos : LongInt; lTriggerDataCount : LongInt; uOption : DWord; dpTriggerData : PDouble) : DWord; stdcall;
    // 카운터 모듈의 각 테이블에 트리거 신호를 출력하기 위해 설정한 트리거 설정 정보를 확인한다.
    // ※ 주의 : 각 테이블에 등록된 최대 트리거 데이타 개수를 모를 때는 아래와 같이 트리거 데이타 개수를 미리 파악한 후 사용.
    // Ex)      1) AxcTableGetTriggerDataEx(lModuleNo, lTablePos, &lTriggerDataCount, &uOption, NULL);
    //          2) if(uOption == 0) : dpTriggerData     = new double[lTriggerDataCount * 2];
    //          3) if(uOption == 1) : dpTriggerData     = new double[lTriggerDataCount * 4];
    //          4) dpTriggerInterval = new double[lTriggerDataCount];
    function AxcTableGetTriggerDataEx (lModuleNo : LongInt; lTablePos : LongInt; lpTriggerDataCount : PLongInt; upOption : PDWord; dpTriggerData : PDouble) : DWord; stdcall;

    // 카운터 모듈의 지정한 테이블에 설정된 모든 트리거 데이타와 H/W FIFO의 데이타를 모두 삭제한다.
    function AxcTableSetTriggerDataClear (lModuleNo : LongInt; lTablePos : LongInt) : DWord; stdcall;

    // 카운터 모듈의 지정한 테이블의 트리거 출력 기능을 동작시킴.
    // uEnable : 트리거를 출력 기능의 사용여부를 설정
    // ※ 주의 : 1) 트리거 출력 중 DISABLE하면 출력이 바로 멈춤
    //           2) AxcTableTriggerOneShot, AxcTableGetPatternShotData,AxcTableSetTriggerData, AxcTableGetTriggerDataEx 함수 호출시 자동으로 ENABLE됨
    function AxcTableSetEnable (lModuleNo : LongInt; lTablePos : LongInt; uEnable : DWord) : DWord; stdcall;
    // 카운터 모듈의 지정한 테이블의 트리거 출력 기능의 동작 여부를 확인함.
    function AxcTableGetEnable (lModuleNo : LongInt; lTablePos : LongInt; upEnable : PDWord) : DWord; stdcall;

    // 카운터 모듈의 지정한 테이블을 이용해 발생된 트리거 개수를 확인.
    // lpTriggerCount : 현재까지 출력된 트리거 출력 개수를 반환, AxcTableSetTriggerCountClear 함수로 초기화
    function AxcTableReadTriggerCount (lModuleNo : LongInt; lTablePos : LongInt; lpTriggerCount : PLongInt) : DWord; stdcall;

    // 카운터 모듈의 지정한 테이블에 할당된 H/W 트리거 데이타 FIFO의 상태를 확인.
    // lpCount1[0~500] : 2D 트리거 위치 데이타 중 첫번째(X) 위치를 저정하고 있는 H/W FIFO에 입력된 데이타 개수
    // upStatus1 : 2D 트리거 위치 데이타 중 첫번째(X) 위치를 저정하고 있는 H/W FIFO의 상태
    //   [Bit 0] : Data Empty
    //   [Bit 1] : Data Full
    //   [Bit 2] : Data Valid
    // lpCount2[0~500] : 2D 트리거 위치 데이타 중 두번째(Y) 위치를 저정하고 있는 H/W FIFO에 입력된 데이타 개수
    // upStatus2 : 2D 트리거 위치 데이타 중 두번째(Y) 위치를 저정하고 있는 H/W FIFO의 상태
    //   [Bit 0] : Data Empty
    //   [Bit 1] : Data Full
    //   [Bit 2] : Data Valid
    function AxcTableReadFifoStatus (lModuleNo : LongInt; lTablePos : LongInt; lpCount1 : PLongInt; upStatus1 : PDWord; lpCount2 : PLongInt; upStatus2 : PDWord) : DWord; stdcall;

    // 카운터 모듈의 지정한 테이블에 할당된 H/W 트리거 데이타 FIFO의 현재 위치 데이타값을 확인.
    // dpTopData1 : 2D H/W 트리거 데이타 FIFO의 현재 데이타 중 첫번째(X) 위치 데이타를 확인 함
    // dpTopData1 : 2D H/W 트리거 데이타 FIFO의 현재 데이타 중 두번째(Y) 위치 데이타를 확인 함
    function AxcTableReadFifoData (lModuleNo : LongInt; lTablePos : LongInt; dpTopData1 : PDouble; dpTopData2 : PDouble) : DWord; stdcall;

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////



implementation

const

    dll_name    = 'AXL.dll';
    function AxcInfoIsCNTModule; external dll_name name 'AxcInfoIsCNTModule';
    function AxcInfoGetModuleNo; external dll_name name 'AxcInfoGetModuleNo';
    function AxcInfoGetModuleCount; external dll_name name 'AxcInfoGetModuleCount';
    function AxcInfoGetChannelCount; external dll_name name 'AxcInfoGetChannelCount';
    function AxcInfoGetTotalChannelCount; external dll_name name 'AxcInfoGetTotalChannelCount';
    function AxcInfoGetModule; external dll_name name 'AxcInfoGetModule';
    function AxcInfoGetModuleStatus; external dll_name name 'AxcInfoGetModuleStatus';
    function AxcInfoGetFirstChannelNoOfModuleNo; external dll_name name 'AxcInfoGetFirstChannelNoOfModuleNo';
    function AxcInfoGetModuleNoOfChannelNo; external dll_name name 'AxcInfoGetModuleNoOfChannelNo';
    function AxcSignalSetEncInputMethod; external dll_name name 'AxcSignalSetEncInputMethod';
    function AxcSignalGetEncInputMethod; external dll_name name 'AxcSignalGetEncInputMethod';
    function AxcTriggerSetFunction; external dll_name name 'AxcTriggerSetFunction';
    function AxcTriggerGetFunction; external dll_name name 'AxcTriggerGetFunction';
    function AxcTriggerSetNotchEnable; external dll_name name 'AxcTriggerSetNotchEnable';
    function AxcTriggerGetNotchEnable; external dll_name name 'AxcTriggerGetNotchEnable';
    function AxcSignalSetCaptureFunction; external dll_name name 'AxcSignalSetCaptureFunction';
    function AxcSignalGetCaptureFunction; external dll_name name 'AxcSignalGetCaptureFunction';
    function AxcSignalGetCapturePos; external dll_name name 'AxcSignalGetCapturePos';
    function AxcStatusGetActPos; external dll_name name 'AxcStatusGetActPos';
    function AxcStatusSetActPos; external dll_name name 'AxcStatusSetActPos';
    function AxcTriggerSetNotchPos; external dll_name name 'AxcTriggerSetNotchPos';
    function AxcTriggerGetNotchPos; external dll_name name 'AxcTriggerGetNotchPos';
    function AxcTriggerSetOutput; external dll_name name 'AxcTriggerSetOutput';
    function AxcStatusGetChannel; external dll_name name 'AxcStatusGetChannel';
    function AxcMotSetMoveUnitPerPulse; external dll_name name 'AxcMotSetMoveUnitPerPulse';
    function AxcMotGetMoveUnitPerPulse; external dll_name name 'AxcMotGetMoveUnitPerPulse';
    function AxcSignalSetEncReverse; external dll_name name 'AxcSignalSetEncReverse';
    function AxcSignalGetEncReverse; external dll_name name 'AxcSignalGetEncReverse';
    function AxcSignalSetEncSource; external dll_name name 'AxcSignalSetEncSource';
    function AxcSignalGetEncSource; external dll_name name 'AxcSignalGetEncSource';
    function AxcTriggerSetBlockLowerPos; external dll_name name 'AxcTriggerSetBlockLowerPos';
    function AxcTriggerGetBlockLowerPos; external dll_name name 'AxcTriggerGetBlockLowerPos';
    function AxcTriggerSetBlockUpperPos; external dll_name name 'AxcTriggerSetBlockUpperPos';
    function AxcTriggerGetBlockUpperPos; external dll_name name 'AxcTriggerGetBlockUpperPos';
    function AxcTriggerSetPosPeriod; external dll_name name 'AxcTriggerSetPosPeriod';
    function AxcTriggerGetPosPeriod; external dll_name name 'AxcTriggerGetPosPeriod';
    function AxcTriggerSetDirectionCheck; external dll_name name 'AxcTriggerSetDirectionCheck';
    function AxcTriggerGetDirectionCheck; external dll_name name 'AxcTriggerGetDirectionCheck';
    function AxcTriggerSetBlock; external dll_name name 'AxcTriggerSetBlock';
    function AxcTriggerGetBlock; external dll_name name 'AxcTriggerGetBlock';
    function AxcTriggerSetTime; external dll_name name 'AxcTriggerSetTime';
    function AxcTriggerGetTime; external dll_name name 'AxcTriggerGetTime';
    function AxcTriggerSetLevel; external dll_name name 'AxcTriggerSetLevel';
    function AxcTriggerGetLevel; external dll_name name 'AxcTriggerGetLevel';
    function AxcTriggerSetFreq; external dll_name name 'AxcTriggerSetFreq';
    function AxcTriggerGetFreq; external dll_name name 'AxcTriggerGetFreq';
    function AxcSignalWriteOutput; external dll_name name 'AxcSignalWriteOutput';
    function AxcSignalReadOutput; external dll_name name 'AxcSignalReadOutput';
    function AxcSignalWriteOutputBit; external dll_name name 'AxcSignalWriteOutputBit';
    function AxcSignalReadOutputBit; external dll_name name 'AxcSignalReadOutputBit';
    function AxcSignalReadInput; external dll_name name 'AxcSignalReadInput';
    function AxcSignalReadInputBit; external dll_name name 'AxcSignalReadInputBit';
    function AxcTriggerSetEnable; external dll_name name 'AxcTriggerSetEnable';
    function AxcTriggerGetEnable; external dll_name name 'AxcTriggerGetEnable';
    function AxcTriggerReadAbsRamData; external dll_name name 'AxcTriggerReadAbsRamData';
    function AxcTriggerWriteAbsRamData; external dll_name name 'AxcTriggerWriteAbsRamData';
    function AxcTriggerSetAbs; external dll_name name 'AxcTriggerSetAbs';
    function AxcTriggerSetAbsDouble; external dll_name name 'AxcTriggerSetAbsDouble';
    function AxcTriggerSetPwmEnable; external dll_name name 'AxcTriggerSetPwmEnable';
    function AxcTriggerGetPwmEnable; external dll_name name 'AxcTriggerGetPwmEnable';
    function AxcTriggerSetPwmOutMode; external dll_name name 'AxcTriggerSetPwmOutMode';
    function AxcTriggerGetPwmOutMode; external dll_name name 'AxcTriggerGetPwmOutMode';
    function AxcTriggerSetPwmVelInfo; external dll_name name 'AxcTriggerSetPwmVelInfo';
    function AxcTriggerGetPwmVelInfo; external dll_name name 'AxcTriggerGetPwmVelInfo';
    function AxcTriggerSetPwmPulseControl; external dll_name name 'AxcTriggerSetPwmPulseControl';
    function AxcTriggerGetPwmPulseControl; external dll_name name 'AxcTriggerGetPwmPulseControl';
    function AxcTriggerSetPwmManualData; external dll_name name 'AxcTriggerSetPwmManualData';
    function AxcTriggerGetPwmManualData; external dll_name name 'AxcTriggerGetPwmManualData';
    function AxcTriggerSetPwmPatternData; external dll_name name 'AxcTriggerSetPwmPatternData';
    function AxcTriggerSetPwmData; external dll_name name 'AxcTriggerSetPwmData';
    function AxcTriggerGetPwmData; external dll_name name 'AxcTriggerGetPwmData';
    function AxcStatusReadActVel; external dll_name name 'AxcStatusReadActVel';
    function AxcStatusRead2DActVel; external dll_name name 'AxcStatusRead2DActVel';
    function AxcStatusSetActPosClear; external dll_name name 'AxcStatusSetActPosClear';
    function AxcTableSetTriggerLevel; external dll_name name 'AxcTableSetTriggerLevel';
    function AxcTableGetTriggerLevel; external dll_name name 'AxcTableGetTriggerLevel';
    function AxcTableSetTriggerTime; external dll_name name 'AxcTableSetTriggerTime';
    function AxcTableGetTriggerTime; external dll_name name 'AxcTableGetTriggerTime';
    function AxcTableSetEncoderInput; external dll_name name 'AxcTableSetEncoderInput';
    function AxcTableGetEncoderInput; external dll_name name 'AxcTableGetEncoderInput';
    function AxcTableSetTriggerOutport; external dll_name name 'AxcTableSetTriggerOutport';
    function AxcTableGetTriggerOutport; external dll_name name 'AxcTableGetTriggerOutport';
    function AxcTableSetErrorRange; external dll_name name 'AxcTableSetErrorRange';
    function AxcTableGetErrorRange; external dll_name name 'AxcTableGetErrorRange';
    function AxcTableTriggerOneShot; external dll_name name 'AxcTableTriggerOneShot';
    function AxcTableTriggerPatternShot; external dll_name name 'AxcTableTriggerPatternShot';
    function AxcTableGetPatternShotData; external dll_name name 'AxcTableGetPatternShotData';
    function AxcTableSetTriggerMode; external dll_name name 'AxcTableSetTriggerMode';
    function AxcTableGetTriggerMode; external dll_name name 'AxcTableGetTriggerMode';
    function AxcTableSetTriggerCountClear; external dll_name name 'AxcTableSetTriggerCountClear';
    function AxcTableSetTriggerData; external dll_name name 'AxcTableSetTriggerData';
    function AxcTableGetTriggerData; external dll_name name 'AxcTableGetTriggerData';
    function AxcTableSetTriggerDataEx; external dll_name name 'AxcTableSetTriggerDataEx';
    function AxcTableGetTriggerDataEx; external dll_name name 'AxcTableGetTriggerDataEx';
    function AxcTableSetTriggerDataClear; external dll_name name 'AxcTableSetTriggerDataClear';
    function AxcTableSetEnable; external dll_name name 'AxcTableSetEnable';
    function AxcTableGetEnable; external dll_name name 'AxcTableGetEnable';
    function AxcTableReadTriggerCount; external dll_name name 'AxcTableReadTriggerCount';
    function AxcTableReadFifoStatus; external dll_name name 'AxcTableReadFifoStatus';
    function AxcTableReadFifoData; external dll_name name 'AxcTableReadFifoData';
