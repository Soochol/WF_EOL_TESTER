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


    //========== ���̺귯�� �ʱ�ȭ =========================================================================

    // ���̺귯�� �ʱ�ȭ
    function AxlOpen (lIrqNo : LongInt) : DWord; stdcall;

    // ���̺귯�� �ʱ�ȭ�� �ϵ���� Ĩ�� ������ ���� ����.
    function AxlOpenNoReset (lIrqNo : LongInt) : DWord; stdcall;

    // ���̺귯�� ����� ����
    function AxlClose () : Boolean; stdcall;

    // ���̺귯���� �ʱ�ȭ �Ǿ� �ִ� �� Ȯ��
    function AxlIsOpened () : Boolean; stdcall;

    // ���ͷ�Ʈ�� ����Ѵ�.
    function AxlInterruptEnable () : DWord; stdcall;

    // ���ͷ�Ʈ�� �����Ѵ�.
    function AxlInterruptDisable () : DWord; stdcall;

    //========== ���̺귯�� �� ���̽� ���� ���� ============================================================
    // ��ϵ� ���̽� ������ ���� Ȯ��
    function AxlGetBoardCount (lpBoardCount : PLongInt) : DWord; stdcall;
    // ���̺귯�� ���� Ȯ��, szVersion[64]
    function AxlGetLibVersion (szVersion : char*) : DWord; stdcall;

    // Network��ǰ�� �� ��⺰ ������¸� Ȯ���ϴ� �Լ�
    function AxlGetModuleNodeStatus (lBoardNo : LongInt; lModulePos : LongInt) : DWord; stdcall;

    // �ش� ���尡 ���� ������ �������� ��ȯ�Ѵ�.
    function AxlGetBoardStatus (lBoardNo : LongInt) : DWord; stdcall;

    // Network ��ǰ�� Configuration Lock ���¸� ��ȯ�Ѵ�.
    // *wpLockMode  : DISABLE(0), ENABLE(1)
    function AxlGetLockMode (lBoardNo : LongInt; wpLockMode : PWord) : DWord; stdcall;

    // ��ȯ���� ���� ������ ��ȯ�Ѵ�.
    function AxlGetReturnCodeInfo (dwReturnCode : DWord; lReturnInfoSize : LongInt; lpRecivedSize : PLongInt; szReturnInfo : char*) : DWord; stdcall;

    //========== �α� ���� =================================================================================
    // EzSpy�� ����� �޽��� ���� ����
    // uLevel : 0 - 3 ����
    // LEVEL_NONE(0)    : ��� �޽����� ������� �ʴ´�.
    // LEVEL_ERROR(1)   : ������ �߻��� �޽����� ����Ѵ�.
    // LEVEL_RUNSTOP(2) : ��ǿ��� Run / Stop ���� �޽����� ����Ѵ�.
    // LEVEL_FUNCTION(3): ��� �޽����� ����Ѵ�.
    function AxlSetLogLevel (uLevel : DWord) : DWord; stdcall;
    // EzSpy�� ����� �޽��� ���� Ȯ��
    function AxlGetLogLevel (upLevel : PDWord) : DWord; stdcall;

    //========== MLIII =================================================================================
    // Network��ǰ�� �� ����� �˻��� �����ϴ� �Լ�
    function AxlScanStart (lBoardNo : LongInt; lNet : LongInt) : DWord; stdcall;
    // Network��ǰ �� ������ ��� ����� connect�ϴ� �Լ�
    function AxlBoardConnect (lBoardNo : LongInt; lNet : LongInt) : DWord; stdcall;
    // Network��ǰ �� ������ ��� ����� Disconnect�ϴ� �Լ�
    function AxlBoardDisconnect (lBoardNo : LongInt; lNet : LongInt) : DWord; stdcall;

    //========== SIIIH =================================================================================
    // SIIIH ������ ���忡 ����� ��⿡ ���� �˻��� �����ϴ� �Լ�(SIIIH ������ ���� ����)
    function AxlScanStartSIIIH (pScanResult = NULL : SCAN_RESULT*) : DWord; stdcall;

    //========== Fan Control ===============================================================================
    // ���忡 �����Ǿ� �ִ� Fan�� �ӵ�(rpm)�� Ȯ���Ѵ�.
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
