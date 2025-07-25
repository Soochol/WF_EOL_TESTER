//****************************************************************************
///****************************************************************************
//*****************************************************************************
//**
//** File Name
//** ----------
//**
//** AXL.PAS
//**
//** COPYRIGHT (c) AJINEXTEK Co., LTD
//**
//*****************************************************************************
//*****************************************************************************
//**
//** Description
//** -----------
//** Ajinextek Library Header File
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

unit AXL;

interface

uses Windows, Messages, AXHS, AXA, AXD, AXM;


    //========== 라이브러리 초기화 =========================================================================

    // 라이브러리 초기화
    function AxlOpen (lIrqNo : LongInt) : DWord; stdcall;

    // 라이브러리 초기화시 하드웨어 칩에 리셋을 하지 않음.
    function AxlOpenNoReset (lIrqNo : LongInt) : DWord; stdcall;

    // 라이브러리 사용을 종료
    function AxlClose () : Boolean; stdcall;

    // 라이브러리가 초기화 되어 있는 지 확인
    function AxlIsOpened () : Boolean; stdcall;

    // 인터럽트를 사용한다.
    function AxlInterruptEnable () : DWord; stdcall;

    // 인터럽트를 사용안한다.
    function AxlInterruptDisable () : DWord; stdcall;

    //========== 라이브러리 및 베이스 보드 정보 ============================================================
    // 등록된 베이스 보드의 개수 확인
    function AxlGetBoardCount (lpBoardCount : PLongInt) : DWord; stdcall;
    // 라이브러리 버전 확인, szVersion[64]
    function AxlGetLibVersion (szVersion : char*) : DWord; stdcall;

    // Network제품의 각 모듈별 연결상태를 확인하는 함수
    function AxlGetModuleNodeStatus (lBoardNo : LongInt; lModulePos : LongInt) : DWord; stdcall;

    // 해당 보드가 제어 가능한 상태인지 반환한다.
    function AxlGetBoardStatus (lBoardNo : LongInt) : DWord; stdcall;

    // Network 제품의 Configuration Lock 상태를 반환한다.
    // *wpLockMode  : DISABLE(0), ENABLE(1)
    function AxlGetLockMode (lBoardNo : LongInt; wpLockMode : PWord) : DWord; stdcall;

    // 반환값에 대한 설명을 반환한다.
    function AxlGetReturnCodeInfo (dwReturnCode : DWord; lReturnInfoSize : LongInt; lpRecivedSize : PLongInt; szReturnInfo : char*) : DWord; stdcall;

    //========== 로그 레벨 =================================================================================
    // EzSpy에 출력할 메시지 레벨 설정
    // uLevel : 0 - 3 설정
    // LEVEL_NONE(0)    : 모든 메시지를 출력하지 않는다.
    // LEVEL_ERROR(1)   : 에러가 발생한 메시지만 출력한다.
    // LEVEL_RUNSTOP(2) : 모션에서 Run / Stop 관련 메시지를 출력한다.
    // LEVEL_FUNCTION(3): 모든 메시지를 출력한다.
    function AxlSetLogLevel (uLevel : DWord) : DWord; stdcall;
    // EzSpy에 출력할 메시지 레벨 확인
    function AxlGetLogLevel (upLevel : PDWord) : DWord; stdcall;

    //========== MLIII =================================================================================
    // Network제품의 각 모듈을 검색을 시작하는 함수
    function AxlScanStart (lBoardNo : LongInt; lNet : LongInt) : DWord; stdcall;
    // Network제품 각 보드의 모든 모듈을 connect하는 함수
    function AxlBoardConnect (lBoardNo : LongInt; lNet : LongInt) : DWord; stdcall;
    // Network제품 각 보드의 모든 모듈을 Disconnect하는 함수
    function AxlBoardDisconnect (lBoardNo : LongInt; lNet : LongInt) : DWord; stdcall;

    //========== SIIIH =================================================================================
    // SIIIH 마스터 보드에 연결된 모듈에 대한 검색을 시작하는 함수(SIIIH 마스터 보드 전용)
    function AxlScanStartSIIIH (pScanResult = NULL : SCAN_RESULT*) : DWord; stdcall;

    //========== Fan Control ===============================================================================
    // 보드에 장착되어 있는 Fan의 속도(rpm)를 확인한다.
    function AxlReadFanSpeed (lBoardNo : LongInt; dpFanSpeed : PDouble) : DWord; stdcall;

    //========== EzSpy =================================================================================
    // EzSpy User Log(Max length : 200 Bytes)
    function AxlEzSpyUserLog (szUserLog : char*) : DWord; stdcall;


implementation

const

    dll_name    = 'AXL.dll';
    function AxlOpen; external dll_name name 'AxlOpen';
    function AxlOpenNoReset; external dll_name name 'AxlOpenNoReset';
    function AxlClose; external dll_name name 'AxlClose';
    function AxlIsOpened; external dll_name name 'AxlIsOpened';
    function AxlInterruptEnable; external dll_name name 'AxlInterruptEnable';
    function AxlInterruptDisable; external dll_name name 'AxlInterruptDisable';
    function AxlGetBoardCount; external dll_name name 'AxlGetBoardCount';
    function AxlGetLibVersion; external dll_name name 'AxlGetLibVersion';
    function AxlGetModuleNodeStatus; external dll_name name 'AxlGetModuleNodeStatus';
    function AxlGetBoardStatus; external dll_name name 'AxlGetBoardStatus';
    function AxlGetLockMode; external dll_name name 'AxlGetLockMode';
    function AxlGetReturnCodeInfo; external dll_name name 'AxlGetReturnCodeInfo';
    function AxlSetLogLevel; external dll_name name 'AxlSetLogLevel';
    function AxlGetLogLevel; external dll_name name 'AxlGetLogLevel';
    function AxlScanStart; external dll_name name 'AxlScanStart';
    function AxlBoardConnect; external dll_name name 'AxlBoardConnect';
    function AxlBoardDisconnect; external dll_name name 'AxlBoardDisconnect';
    function AxlScanStartSIIIH; external dll_name name 'AxlScanStartSIIIH';
    function AxlReadFanSpeed; external dll_name name 'AxlReadFanSpeed';
    function AxlEzSpyUserLog; external dll_name name 'AxlEzSpyUserLog';
