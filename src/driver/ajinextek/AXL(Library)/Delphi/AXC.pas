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


    //========== ���� �� ��� ����
    // CNT ����� �ִ��� Ȯ��
    function AxcInfoIsCNTModule (upStatus : PDWord) : DWord; stdcall;

    // CNT ��� No Ȯ��
    function AxcInfoGetModuleNo (lBoardNo : LongInt; lModulePos : LongInt; lpModuleNo : PLongInt) : DWord; stdcall;

    // CNT ����� ����� ���� Ȯ��
    function AxcInfoGetModuleCount (lpModuleCount : PLongInt) : DWord; stdcall;

    // ������ ����� ī���� �Է� ä�� ���� Ȯ��
    function AxcInfoGetChannelCount (lModuleNo : LongInt; lpCount : PLongInt) : DWord; stdcall;

    // �ý��ۿ� ������ ī������ �� ä�� ���� Ȯ��
    function AxcInfoGetTotalChannelCount (lpChannelCount : PLongInt) : DWord; stdcall;

    // ������ ��� ��ȣ�� ���̽� ���� ��ȣ, ��� ��ġ, ��� ID Ȯ��
    function AxcInfoGetModule (lModuleNo : LongInt; lpBoardNo : PLongInt; lpModulePos : PLongInt; upModuleID : PDWord) : DWord; stdcall;

    // �ش� ����� ��� ������ �������� ��ȯ�Ѵ�.
    function AxcInfoGetModuleStatus (lModuleNo : LongInt) : DWord; stdcall;

    function AxcInfoGetFirstChannelNoOfModuleNo (lModuleNo : LongInt; lpChannelNo : PLongInt) : DWord; stdcall;
    function AxcInfoGetModuleNoOfChannelNo (lChannelNo : LongInt; lpModuleNo : PLongInt) : DWord; stdcall;

    // ī���� ����� Encoder �Է� ����� ���� �մϴ�.
    // dwMethod --> 0x00 : Sign and pulse, x1 multiplication
    // dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    // dwMethod --> 0x08 : Sign and pulse, x2 multiplication
    // dwMethod --> 0x09 : Increment and decrement pulses, x1 multiplication
    // dwMethod --> 0x0A : Increment and decrement pulses, x2 multiplication
    // SIO-CN2CH/HPC4�� ���
    // dwMethod --> 0x00 : Up/Down ���, A phase : �޽�, B phase : ����
    // dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    // SIO-LCM4�� ���
    // dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    function AxcSignalSetEncInputMethod (lChannelNo : LongInt; dwMethod : DWord) : DWord; stdcall;

    // ī���� ����� Encoder �Է� ����� ���� �մϴ�.
    // *dwpUpMethod --> 0x00 : Sign and pulse, x1 multiplication
    // *dwpUpMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // *dwpUpMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // *dwpUpMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    // *dwpUpMethod --> 0x08 : Sign and pulse, x2 multiplication
    // *dwpUpMethod --> 0x09 : Increment and decrement pulses, x1 multiplication
    // *dwpUpMethod --> 0x0A : Increment and decrement pulses, x2 multiplication
    // SIO-CN2CH/HPC4�� ���
    // dwMethod --> 0x00 : Up/Down ���, A phase : �޽�, B phase : ����
    // dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    // SIO-LCM4�� ���
    // dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    // dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    // dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    function AxcSignalGetEncInputMethod (lChannelNo : LongInt; dwpUpMethod : PDWord) : DWord; stdcall;

    // ī���� ����� Ʈ���Ÿ� ���� �մϴ�.
    // dwMode -->  0x00 : Latch
    // dwMode -->  0x01 : State
    // dwMode -->  0x02 : Special State    --> SIO-CN2CH ����
    // SIO-CN2CH�� ���
    // dwMode -->  0x00 : ���� ��ġ Ʈ���� �Ǵ� �ֱ� ��ġ Ʈ����.
    // ���� : ��ǰ���� ����� ���� �ٸ��� ������ �����Ͽ� ��� �ʿ�.
    // dwMode -->  0x01 : �ð� �ֱ� Ʈ����(AxcTriggerSetFreq�� ����)
    // SIO-HPC4�� ���
    // dwMode -->  0x00 : timer mode with counter & frequncy.
    // dwMode -->  0x01 : timer mode.
    // dwMode -->  0x02 : absolute mode[with fifo].
    // dwMode -->  0x03 : periodic mode.[Default]
    function AxcTriggerSetFunction (lChannelNo : LongInt; dwMode : DWord) : DWord; stdcall;

    // ī���� ����� Ʈ���� ������ Ȯ�� �մϴ�.
    // *dwMode -->  0x00 : Latch
    // *dwMode -->  0x01 : State
    // *dwMode -->  0x02 : Special State
    // SIO-CN2CH�� ���
    // *dwMode -->  0x00 : ���� ��ġ Ʈ���� �Ǵ� �ֱ� ��ġ Ʈ����.
    // ���� : ��ǰ���� ����� ���� �ٸ��� ������ �����Ͽ� ��� �ʿ�.
    // *dwMode -->  0x01 : �ð� �ֱ� Ʈ����(AxcTriggerSetFreq�� ����)
    // SIO-HPC4�� ���
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


    // ī���� ����� Capture �ؼ��� ���� �մϴ�.(External latch input polarity)
    // dwCapturePol --> 0x00 : Signal OFF -> ON
    // dwCapturePol --> 0x01 : Signal ON -> OFF
    function AxcSignalSetCaptureFunction (lChannelNo : LongInt; dwCapturePol : DWord) : DWord; stdcall;

    // ī���� ����� Capture �ؼ� ������ Ȯ�� �մϴ�.(External latch input polarity)
    // *dwCapturePol --> 0x00 : Signal OFF -> ON
    // *dwCapturePol --> 0x01 : Signal ON -> OFF
    function AxcSignalGetCaptureFunction (lChannelNo : LongInt; dwpCapturePol : PDWord) : DWord; stdcall;

    // ī���� ����� Capture ��ġ�� Ȯ�� �մϴ�.(External latch)
    // *dbpCapturePos --> Capture position ��ġ
    function AxcSignalGetCapturePos (lChannelNo : LongInt; dbpCapturePos : PDouble) : DWord; stdcall;

    // ī���� ����� ī���� ���� Ȯ�� �մϴ�.
    // *dbpActPos --> ī���� ��
    function AxcStatusGetActPos (lChannelNo : LongInt; dbpActPos : PDouble) : DWord; stdcall;

    // ī���� ����� ī���� ���� dbActPos ������ ���� �մϴ�.
    function AxcStatusSetActPos (lChannelNo : LongInt; dbActPos : Double) : DWord; stdcall;

    // ī���� ����� Ʈ���� ��ġ�� �����մϴ�.
    // ī���� ����� Ʈ���� ��ġ�� 2�������� ���� �� �� �ֽ��ϴ�.
    function AxcTriggerSetNotchPos (lChannelNo : LongInt; dbLowerPos : Double; dbUpperPos : Double) : DWord; stdcall;

    // ī���� ����� ������ Ʈ���� ��ġ�� Ȯ�� �մϴ�.
    function AxcTriggerGetNotchPos (lChannelNo : LongInt; dbpLowerPos : PDouble; dbpUpperPos : PDouble) : DWord; stdcall;

    // ī���� ����� Ʈ���� ����� ������ �մϴ�.
    // dwOutVal --> 0x00 : Ʈ���� ��� '0'
    // dwOutVal --> 0x01 : Ʈ���� ��� '1'
    function AxcTriggerSetOutput (lChannelNo : LongInt; dwOutVal : DWord) : DWord; stdcall;

    // ī���� ����� ���¸� Ȯ���մϴ�.
    // Bit '0' : Carry (ī���� ����ġ�� ���� �޽��� ���� ī���� ����ġ�� �Ѿ� 0�� �ٲ���� �� 1��ĵ�� ON���� �մϴ�.)
    // Bit '1' : Borrow (ī���� ����ġ�� ���� �޽��� ���� 0�� �Ѿ� ī���� ����ġ�� �ٲ���� �� 1��ĵ�� ON���� �մϴ�.)
    // Bit '2' : Trigger output status
    // Bit '3' : Latch input status
    function AxcStatusGetChannel (lChannelNo : LongInt; dwpChannelStatus : PDWord) : DWord; stdcall;


    // SIO-CN2CH ���� �Լ���
    //
    // ī���� ����� ��ġ ������ �����Ѵ�.
    // ���� ��ġ �̵����� ���� �޽� ������ �����ϴµ�,
    // ex) 1mm �̵��� 1000�� �ʿ��ϴٸ�dMoveUnitPerPulse = 0.001�� �Է��ϰ�,
    //     ���� ��� �Լ��� ��ġ�� ���õ� ���� mm ������ �����ϸ� �ȴ�.
    function AxcMotSetMoveUnitPerPulse (lChannelNo : LongInt; dMoveUnitPerPulse : Double) : DWord; stdcall;

    // ī���� ����� ��ġ ������ Ȯ���Ѵ�.
    function AxcMotGetMoveUnitPerPulse (lChannelNo : LongInt; dpMoveUnitPerPuls : PDouble) : DWord; stdcall;

    // ī���� ����� ���ڴ� �Է� ī���͸� ���� ����� �����Ѵ�.
    // dwReverse --> 0x00 : �������� ����.
    // dwReverse --> 0x01 : ����.
    function AxcSignalSetEncReverse (lChannelNo : LongInt; dwReverse : DWord) : DWord; stdcall;

    // ī���� ����� ���ڴ� �Է� ī���͸� ���� ����� ������ Ȯ���Ѵ�.
    function AxcSignalGetEncReverse (lChannelNo : LongInt; dwpReverse : PDWord) : DWord; stdcall;

    // ī���� ����� Encoder �Է� ��ȣ�� �����Ѵ�.
    // dwSource -->  0x00 : 2(A/B)-Phase ��ȣ.
    // dwSource -->  0x01 : Z-Phase ��ȣ.(���⼺ ����.)
    function AxcSignalSetEncSource (lChannelNo : LongInt; dwSource : DWord) : DWord; stdcall;

    // ī���� ����� Encoder �Է� ��ȣ ���� ������ Ȯ���Ѵ�.
    function AxcSignalGetEncSource (lChannelNo : LongInt; dwpSource : PDWord) : DWord; stdcall;

    // ī���� ����� Ʈ���� ��� ���� �� ���� ���� �����Ѵ�.
    // ��ġ �ֱ� Ʈ���� ��ǰ�� ��� ��ġ �ֱ�� Ʈ���� ����� �߻���ų ���� �� ���� ���� �����Ѵ�.
    // ���� ��ġ Ʈ���� ��ǰ�� ��� Ram ���� ������ Ʈ���� ������ ���� ���� ��ġ�� �����Ѵ�.
    // ���� : AxcMotSetMoveUnitPerPulse�� ������ ����.
    // Note : ���Ѱ��� ���Ѱ����� �������� �����Ͽ��� �մϴ�.
    function AxcTriggerSetBlockLowerPos (lChannelNo : LongInt; dLowerPosition : Double) : DWord; stdcall;

    // ī���� ����� Ʈ���� ��� ���� �� ���� ���� Ȯ���Ѵ�.
    function AxcTriggerGetBlockLowerPos (lChannelNo : LongInt; dpLowerPosition : PDouble) : DWord; stdcall;

    // ī���� ����� Ʈ���� ��� ���� �� ���� ���� �����Ѵ�.
    // ��ġ �ֱ� Ʈ���� ��ǰ�� ��� ��ġ �ֱ�� Ʈ���� ����� �߻���ų ���� �� ���� ���� �����Ѵ�.
    // ���� ��ġ Ʈ���� ��ǰ�� ��� Ʈ���� ������ ������ Ram �� ������ ������ Ʈ���� ������ ����Ǵ� ��ġ�� ���ȴ�.
    // ���� : AxcMotSetMoveUnitPerPulse�� ������ ����.
    // Note : ���Ѱ��� ���Ѱ����� ū���� �����Ͽ��� �մϴ�.
    function AxcTriggerSetBlockUpperPos (lChannelNo : LongInt; dUpperPosition : Double) : DWord; stdcall;
    // ī���� ����� Ʈ���� ��� ���� �� ���� ���� �����Ѵ�.
    function AxcTriggerGetBlockUpperPos (lChannelNo : LongInt; dpUpperrPosition : PDouble) : DWord; stdcall;

    // ī���� ����� ��ġ �ֱ� ��� Ʈ���ſ� ���Ǵ� ��ġ �ֱ⸦ �����Ѵ�.
    // ���� : AxcMotSetMoveUnitPerPulse�� ������ ����.
    function AxcTriggerSetPosPeriod (lChannelNo : LongInt; dPeriod : Double) : DWord; stdcall;

    // ī���� ����� ��ġ �ֱ� ��� Ʈ���ſ� ���Ǵ� ��ġ �ֱ⸦ Ȯ���Ѵ�.
    function AxcTriggerGetPosPeriod (lChannelNo : LongInt; dpPeriod : PDouble) : DWord; stdcall;

    // ī���� ����� ��ġ �ֱ� ��� Ʈ���� ���� ��ġ ������ ���� ��ȿ����� �����Ѵ�.
    // dwDirection -->  0x00 : ī������ ��/���� ���Ͽ� Ʈ���� �ֱ� ���� ���.
    // dwDirection -->  0x01 : ī���Ͱ� ���� �Ҷ��� Ʈ���� �ֱ� ���� ���.
    // dwDirection -->  0x01 : ī���Ͱ� ���� �Ҷ��� Ʈ���� �ֱ� ���� ���.
    function AxcTriggerSetDirectionCheck (lChannelNo : LongInt; dwDirection : DWord) : DWord; stdcall;
    // ī���� ����� ��ġ �ֱ� ��� Ʈ���� ���� ��ġ ������ ���� ��ȿ��� ������ Ȯ���Ѵ�.
    function AxcTriggerGetDirectionCheck (lChannelNo : LongInt; dwpDirection : PDWord) : DWord; stdcall;

    // ī���� ����� ��ġ �ֱ� ��� Ʈ���� ����� ����, ��ġ �ֱ⸦ �ѹ��� �����Ѵ�.
    // ��ġ ���� ���� :  AxcMotSetMoveUnitPerPulse�� ������ ����.
    function AxcTriggerSetBlock (lChannelNo : LongInt; dLower : Double; dUpper : Double; dABSod : Double) : DWord; stdcall;

    // ī���� ����� ��ġ �ֱ� ��� Ʈ���� ����� ����, ��ġ �ֱ⸦ ������ �ѹ��� Ȯ���Ѵ�.
    function AxcTriggerGetBlock (lChannelNo : LongInt; dpLower : PDouble; dpUpper : PDouble; dpABSod : PDouble) : DWord; stdcall;

    // ī���� ����� Ʈ���� ��� �޽� ���� �����Ѵ�.
    // ���� : uSec
    function AxcTriggerSetTime (lChannelNo : LongInt; dTrigTime : Double) : DWord; stdcall;

    // ī���� ����� Ʈ���� ��� �޽� �� ������ Ȯ���Ѵ�.
    function AxcTriggerGetTime (lChannelNo : LongInt; dpTrigTime : PDouble) : DWord; stdcall;

    // ī���� ����� Ʈ���� ��� �޽��� ��� ������ �����Ѵ�.
    // dwLevel -->  0x00 : Ʈ���� ��½� 'Low' ���� ���.
    // dwLevel -->  0x01 : Ʈ���� ��½� 'High' ���� ���.
    function AxcTriggerSetLevel (lChannelNo : LongInt; dwLevel : DWord) : DWord; stdcall;
    // ī���� ����� Ʈ���� ��� �޽��� ��� ���� ������ Ȯ���Ѵ�.
    function AxcTriggerGetLevel (lChannelNo : LongInt; dwpLevel : PDWord) : DWord; stdcall;

    // ī���� ����� ���ļ� Ʈ���� ��� ��ɿ� �ʿ��� ���ļ��� �����Ѵ�.
    // ���� : Hz, ���� : 1Hz ~ 500 kHz
    function AxcTriggerSetFreq (lChannelNo : LongInt; dwFreqency : DWord) : DWord; stdcall;
    // ī���� ����� ���ļ� Ʈ���� ��� ��ɿ� �ʿ��� ���ļ��� ������ Ȯ���Ѵ�.
    function AxcTriggerGetFreq (lChannelNo : LongInt; dwpFreqency : PDWord) : DWord; stdcall;

    // ī���� ����� ���� ä�ο� ���� ���� ��� ���� �����Ѵ�.
    // dwOutput ���� : 0x00 ~ 0x0F, �� ä�δ� 4���� ���� ���
    function AxcSignalWriteOutput (lChannelNo : LongInt; dwOutput : DWord) : DWord; stdcall;

    // ī���� ����� ���� ä�ο� ���� ���� ��� ���� Ȯ���Ѵ�.
    function AxcSignalReadOutput (lChannelNo : LongInt; dwpOutput : PDWord) : DWord; stdcall;

    // ī���� ����� ���� ä�ο� ���� ���� ��� ���� ��Ʈ ���� �����Ѵ�.
    // lBitNo ���� : 0 ~ 3, �� ä�δ� 4���� ���� ���
    function AxcSignalWriteOutputBit (lChannelNo : LongInt; lBitNo : LongInt; uOnOff : DWord) : DWord; stdcall;
    // ī���� ����� ���� ä�ο� ���� ���� ��� ���� ��Ʈ ���� Ȯ�� �Ѵ�.
    // lBitNo ���� : 0 ~ 3
    function AxcSignalReadOutputBit (lChannelNo : LongInt; lBitNo : LongInt; upOnOff : PDWord) : DWord; stdcall;

    // ī���� ����� ���� ä�ο� ���� ���� �Է� ���� Ȯ���Ѵ�.
    function AxcSignalReadInput (lChannelNo : LongInt; dwpInput : PDWord) : DWord; stdcall;

    // ī���� ����� ���� ä�ο� ���� ���� �Է� ���� ��Ʈ ���� Ȯ�� �Ѵ�.
    // lBitNo ���� : 0 ~ 3
    function AxcSignalReadInputBit (lChannelNo : LongInt; lBitNo : LongInt; upOnOff : PDWord) : DWord; stdcall;

    // ī���� ����� Ʈ���� ����� Ȱ��ȭ �Ѵ�.
    // ���� ������ ��ɿ� ���� Ʈ���� ����� ���������� ����� ������ �����Ѵ�.
    function AxcTriggerSetEnable (lChannelNo : LongInt; dwUsage : DWord) : DWord; stdcall;

    // ī���� ����� Ʈ���� ��� Ȱ��ȭ ���� ������ Ȯ���ϴ�.
    function AxcTriggerGetEnable (lChannelNo : LongInt; dwpUsage : PDWord) : DWord; stdcall;

    // ī���� ����� ������ġ Ʈ���� ����� ���� ������ RAM ������ Ȯ���Ѵ�.
    // dwAddr ���� : 0x0000 ~ 0x1FFFF;
    function AxcTriggerReadAbsRamData (lChannelNo : LongInt; dwAddr : DWord; dwpData : PDWord) : DWord; stdcall;

    // ī���� ����� ������ġ Ʈ���� ����� ���� �ʿ��� RAM ������ �����Ѵ�.
    // dwAddr ���� : 0x0000 ~ 0x1FFFF;
    function AxcTriggerWriteAbsRamData (lChannelNo : LongInt; dwAddr : DWord; dwData : DWord) : DWord; stdcall;

    // ���� CNT ä���� ���� ��ġ Ʈ���� ����� ���� DWORD�� ��ġ ������ �����Ѵ�.
    //----------------------------------------------------------------------------------------------------------------------------------
    // 1. AXT_SIO_CN2CH�� ���
    // dwTrigNum --> 131072(=0x20000) ������ ���� ����
    // dwTrigPos --> DWORD�� Data �Է� ����
    // dwDirection --> 0x0(default) : dwTrigPos[0], dwTrigPos[1] ..., dwTrigPos[dwTrigNum - 1] ������ Data�� Write �Ѵ�.
    //     0x1    : dwTrigPos[dwTrigNum - 1], dwTrigPos[dwTrigNum - 2], ..., dwTrigPos[0] ������ Data�� Write �Ѵ�.
    // *����* 1) dwDirection: Data Write ������ �ٸ� �� ��ɻ��� ���� ����
    //    2) AXC Manual�� AxcTriggerSetAbs - Description�� �����Ͽ� data�� ���� �� ����ؾ� ��
    //----------------------------------------------------------------------------------------------------------------------------------
    // 2. AXT_SIO_HPC4�� ���
    // dwTrigNum --> 500 ������ ���� ����
    // dwTrigPos --> DWORD�� Data �Է� ����
    // dwDirection --> 0x0(default) : ������ �ʴ� ������, �Է����� �ʾƵ� �ȴ�.
    //----------------------------------------------------------------------------------------------------------------------------------
    // 3. AXT_SIO_RCNT2RTEX, AXT_SIO_RCNT2MLIII, AXT_SIO_RCNT2SIIIH, AXT_SIO_RCNT2SIIIH_R�� ���
    // dwTrigNum --> 0x200(=512) ������ ���� ����
    // dwTrigPos --> DWORD�� data �Է� ����
    // dwDirection --> 0x0(default) : ������ �ʴ� ������, �Է����� �ʾƵ� �ȴ�.
    //----------------------------------------------------------------------------------------------------------------------------------
    function AxcTriggerSetAbs (lChannelNo : LongInt; dwTrigNum : DWord; dwTrigPos : PDWord; 0 : DWORD dwDirection =) : DWord; stdcall;


    // ���� CNT ä���� ���� ��ġ Ʈ���� ����� ���� double�� ��ġ ������ �����Ѵ�.
    //----------------------------------------------------------------------------------------------------------------------------------
    // 1. AXT_SIO_CN2CH�� ���
    // dwTrigNum --> 4194304(=0x20000*32) ������ ���� ����
    // dTrigPos  --> double�� data �Է� ����
    // dwDirection --> 0x0(default) : dTrigPos[0], dTrigPos[1] ..., dTrigPos[dwTrigNum - 1] ������ Data�� Write �Ѵ�.
    //     0x1    : dTrigPos[dwTrigNum - 1], dTrigPos[dwTrigNum - 2], ..., dTrigPos[0] ������ Data�� Write �Ѵ�.
    // *����* 1) dwDirection: Data Write ������ �ٸ� �� ��ɻ��� ���� ����
    //----------------------------------------------------------------------------------------------------------------------------------
    // 2. AXT_SIO_RCNT2RTEX, AXT_SIO_RCNT2MLIII, AXT_SIO_RCNT2SIIIH_R�� ���
    // dwTrigNum --> 0x200(=512) ������ ���� ����
    // dTrigPos  --> double�� data �Է� ����
    // dwDirection --> 0x0(default) : ������ �ʴ� ������, �Է����� �ʾƵ� �ȴ�.
    //----------------------------------------------------------------------------------------------------------------------------------
    function AxcTriggerSetAbsDouble (lChannelNo : LongInt; dwTrigNum : DWord; dTrigPos : PDouble; 0 : DWORD dwDirection =) : DWord; stdcall;

    ////////////////// LCM4_10_Version/////////////////////////////////////////////////////////////

    // ī���� ����� PWM ����� Ȱ��ȭ�Ѵ�.
    function AxcTriggerSetPwmEnable (lChannelNo : LongInt; bEnable : Boolean) : DWord; stdcall;
    // ī���� ����� PWM ��� Ȱ��ȭ ���¸� Ȯ���Ѵ�.
    function AxcTriggerGetPwmEnable (lChannelNo : LongInt; bEnable : bool*) : DWord; stdcall;
    // ī���� ����� PWM ��¸�带 �����Ѵ�.
    // dwMode : PWM ��¸��
    // [0] : Manual (Manual�� ������ PWM Data)
    // [1] : Auto (�ӵ� Table)
    function AxcTriggerSetPwmOutMode (lChannelNo : LongInt; dwMode : DWord) : DWord; stdcall;
    // ī���� ����� PWM ��¸�带 Ȯ���Ѵ�.
    // dwMode : PWM ��¸��
    // [0] : Manual (Manual�� ������ PWM Data)
    // [1] : Auto (�ӵ� Table)
    function AxcTriggerGetPwmOutMode (lChannelNo : LongInt; dwpMode : PDWord) : DWord; stdcall;

    // ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� �ӵ� ������ �����Ѵ�.
    // dMinVel : dMinVel
    // dMaxVel : dMaxVel
    // dVelInterval : �ӵ� ���̺����� ������ �ӵ� Interval
    // ������ : dMinVel���� dVelInterval �������� �ִ� 5000���� �ӵα����� ������.
    //          (((dMaxVel-dMinVel) / dVelInterval) <= 5000)�� �����Ͽ��� �Ѵ�.
    function AxcTriggerSetPwmVelInfo (lChannelNo : LongInt; dMinVel : Double; dMaxVel : Double; dVelInterval : Double) : DWord; stdcall;
    // ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� �ӵ� ������ Ȯ���Ѵ�.
    function AxcTriggerGetPwmVelInfo (lChannelNo : LongInt; dpMinVel : PDouble; dpMaxVel : PDouble; dpVelInterval : PDouble) : DWord; stdcall;
    // ī���� ����� PWM ��¿��� Pulse �� �������� �����Ѵ�.
    // dwMode : Pulse �� ����
    // [0] : DutyRatio
    // [1] : PulseWidth
    function AxcTriggerSetPwmPulseControl (lChannelNo : LongInt; dwMode : DWord) : DWord; stdcall;
    //  ī���� ����� PWM ��¿��� Pulse ��������� Ȯ�δ�.
    // dwpMode : Pulse �� ����
    // [0] : DutyRatio
    // [1] : PulseWidth
    function AxcTriggerGetPwmPulseControl (lChannelNo : LongInt; dwpMode : PDWord) : DWord; stdcall;

    // ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ �����Ѵ�.
    // pwm ��¸�尡 Manual �� ��쿡�� ��ȿ�ϴ�
    // dFrequency :  (0.017 ~ 1M) ���� ������ �����ϴ�. (Hz ����)
    // dData : Pulse �� ���� Data �� �Է��ϸ� Pulse Control ��Ŀ� ���� Data ������ �ٸ���.
    // Pulse �� �������� DutyRatio�� ��� DutyRatio
    // Pulse �� �������� PulseWidth �� ��� PulseWidth (us����)
    function AxcTriggerSetPwmManualData (lChannelNo : LongInt; dFrequency : Double; dData : Double) : DWord; stdcall;
    // ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ Ȯ���Ѵ�.
    function AxcTriggerGetPwmManualData (lChannelNo : LongInt; dpFrequency : PDouble; dpData : PDouble) : DWord; stdcall;
    // ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ �����Ѵ�.
    // lDataCnt : ���� �� Ʈ���� ������ ��ü ����
    // dpVel : dpVel[0],dpVel[1]....dpVel[DataCnt -1] ������ �Է� ����
    // dwpFrequency : dwpFrequency[0],dwpFrequency[1]....dwpFrequency[DataCnt-1] ������ �Է� ����(0.017 ~ 1M) ���� ������ �����ϴ�.
    // dData : Pulse �� ���� Data �� �Է��ϸ� Pulse Control ��Ŀ� ���� Data ������ �ٸ���.
    // Pulse �� �������� DutyRatio�� ��� DutyRatio
    // Pulse �� �������� PulseWidth �� ��� PulseWidth (us����)
    // ������ :
    //    1) dpVel, dwpFrequency, dwpDutyRatio �� �迭 ������ �����Ͽ� ����ؾ��Ѵ�.
    //  - �ӵ��� 0�� ���������� PWM ����� �Ұ��ϴ�.
    //    3) PWM Enable ���¿����� ����� �� ����.
    function AxcTriggerSetPwmPatternData (lChannelNo : LongInt; lDataCnt : LongInt; dpVel : PDouble; dpFrequency : PDouble; dpData : PDouble) : DWord; stdcall;
    // ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ �����Ѵ�.
    function AxcTriggerSetPwmData (lChannelNo : LongInt; dVel : Double; dFrequency : Double; dData : Double) : DWord; stdcall;
    // ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ Ȯ���Ѵ�.
    function AxcTriggerGetPwmData (lChannelNo : LongInt; dVel : Double; dpFrequency : PDouble; dpData : PDouble) : DWord; stdcall;
    // ī���� ����� �ӵ� ���� Ȯ�� �մϴ�.
    function AxcStatusReadActVel (lChannelNo : LongInt; dpActVel : PDouble) : DWord; stdcall;
    // ī���� ����� 2D �ӵ� ���� Ȯ�� �մϴ�.
    function AxcStatusRead2DActVel (lChannelNo : LongInt; dpActVel : PDouble) : DWord; stdcall;
    // ī���� ����� Position ���� �ʱ�ȭ �Ѵ�.
    function AxcStatusSetActPosClear (lChannelNo : LongInt) : DWord; stdcall;
    ////////////////// HPC4_30_Version
    // ī���� ����� �� ���̺� �Ҵ�� Ʈ���� ����� ������ �����Ѵ�.
    // uLevel : Ʈ���� ��� ��ȣ�� Active Level
    //   [0]  : Ʈ���� ��½� 'Low' ���� ���.
    //   [1]  : Ʈ���� ��½� 'High' ���� ���.
    function AxcTableSetTriggerLevel (lModuleNo : LongInt; lTablePos : LongInt; uLevel : DWord) : DWord; stdcall;
    // ī���� ����� �� ���̺� ������ Ʈ���� ����� ���� �������� Ȯ���Ѵ�.
    function AxcTableGetTriggerLevel (lModuleNo : LongInt; lTablePos : LongInt; upLevel : PDWord) : DWord; stdcall;

    // ī���� ����� �� ���̺� �Ҵ�� Ʈ���� ����� �޽� ���� �����Ѵ�.
    // dTriggerTimeUSec : [Default 500ms], us������ ����
    function AxcTableSetTriggerTime (lModuleNo : LongInt; lTablePos : LongInt; dTriggerTimeUSec : Double) : DWord; stdcall;
    // ī���� ����� �� ���̺� ������ Ʈ���� ����� �޽� �� �������� Ȯ���Ѵ�.
    function AxcTableGetTriggerTime (lModuleNo : LongInt; lTablePos : LongInt; dpTriggerTimeUSec : PDouble) : DWord; stdcall;

    // ī���� ����� �� ���̺� �Ҵ� �� 2���� ���ڴ� �Է� ��ȣ�� �����Ѵ�.
    // uEncoderInput1 [0-3]: ī���� ��⿡ �ԷµǴ� 4���� ���ڴ� ��ȣ�� �ϳ�
    // uEncoderInput2 [0-3]: ī���� ��⿡ �ԷµǴ� 4���� ���ڴ� ��ȣ�� �ϳ�
    function AxcTableSetEncoderInput (lModuleNo : LongInt; lTablePos : LongInt; uEncoderInput1 : DWord; uEncoderInput2 : DWord) : DWord; stdcall;
    // ī���� ����� �� ���̺� �Ҵ� �� 2���� ���ڴ� �Է� ��ȣ�� Ȯ���Ѵ�.
    function AxcTableGetEncoderInput (lModuleNo : LongInt; lTablePos : LongInt; upEncoderInput1 : PDWord; upEncoderInput2 : PDWord) : DWord; stdcall;

    // ī���� ����� �� ���̺� �Ҵ� �� Ʈ���� ��� ��Ʈ�� �����Ѵ�.
    // uTriggerOutport [0x0-0xF]: Bit0: Ʈ���� ��� 0, Bit1: Ʈ���� ��� 1, Bit2: Ʈ���� ��� 2, Bit3: Ʈ���� ��� 3
    // Ex) 0x3(3)   : ��� 0, 1�� Ʈ���� ��ȣ�� ����ϴ� ���
    //     0xF(255) : ��� 0, 1, 2, 3�� Ʈ���� ��ȣ�� ����ϴ� ���
    function AxcTableSetTriggerOutport (lModuleNo : LongInt; lTablePos : LongInt; uTriggerOutport : DWord) : DWord; stdcall;
    // ī���� ����� �� ���̺� �Ҵ� �� Ʈ���� ��� ��Ʈ�� Ȯ���Ѵ�.
    function AxcTableGetTriggerOutport (lModuleNo : LongInt; lTablePos : LongInt; upTriggerOutport : PDWord) : DWord; stdcall;

    // ī���� ����� �� ���̺� ������ Ʈ���� ��ġ�� ���� ��� ���� ������ �����Ѵ�.
    // dErrorRange  : ���� ���� Unit������ Ʈ���� ��ġ�� ���� ��� ���� ������ ����
    function AxcTableSetErrorRange (lModuleNo : LongInt; lTablePos : LongInt; dErrorRange : Double) : DWord; stdcall;
    // ī���� ����� �� ���̺� ������ Ʈ���� ��ġ�� ���� ��� ���� ������ Ȯ���Ѵ�.
    function AxcTableGetErrorRange (lModuleNo : LongInt; lTablePos : LongInt; dpErrorRange : PDouble) : DWord; stdcall;

    // ī���� ����� �� ���̺� ������ ������(Ʈ���� ��� Port, Ʈ���� �޽� ��) Ʈ���Ÿ� 1�� �߻���Ų��.
    // �� ���� : 1) Ʈ���Ű� Disable�Ǿ� ������ �� �Լ��� �ڵ����� Enable���� Ʈ���Ÿ� �߻���Ŵ
    //           2) Trigger Mode�� HPC4_PATTERN_TRIGGER ����� ��� �� �Լ��� �ڵ����� Ʈ���� ��带 HPC4_RANGE_TRIGGER�� ���� ��(�ϳ��� Ʈ���Ÿ� �߻���Ű�� ����)
    function AxcTableTriggerOneShot (lModuleNo : LongInt; lTablePos : LongInt) : DWord; stdcall;

    // ī���� ����� �� ���̺� ������ ������(Ʈ���� ��� Port, Ʈ���� �޽� ��), ������ ������ŭ ������ ���ļ��� Ʈ���Ÿ� �߻���Ų��.
    // lTriggerCount     : ������ ���ļ��� �����ϸ� �߻���ų Ʈ���� ��� ����
    // uTriggerFrequency : Ʈ���Ÿ� �߻���ų ���ļ�
    // �� ���� : 1) Ʈ���Ű� Disable�Ǿ� ������ �� �Լ��� �ڵ����� Enable���� ������ ���� Ʈ���Ÿ� �߻���Ŵ
    //           2) Trigger Mode�� HPC4_PATTERN_TRIGGER ��尡 �ƴ� ��� �� �Լ��� �ڵ����� Ʈ���� ��带 HPC4_PATTERN_TRIGGER�� ���� ��
    function AxcTableTriggerPatternShot (lModuleNo : LongInt; lTablePos : LongInt; lTriggerCount : LongInt; uTriggerFrequency : DWord) : DWord; stdcall;
    // ī���� ����� �� ���̺� ������ ���� Ʈ���� ���� ������(���ļ�, ī����) Ȯ���Ѵ�.
    function AxcTableGetPatternShotData (lModuleNo : LongInt; lTablePos : LongInt; lpTriggerCount : PLongInt; upTriggerFrequency : PDWord) : DWord; stdcall;

    // ī���� ����� �� ���̺� Ʈ���Ÿ� ����ϴ� ����� �����Ѵ�.
    // uTrigMode : Ʈ���Ÿ� ����ϴ� ����� �����Ѵ�.
    //   [0] HPC4_RANGE_TRIGGER   : ������ Ʈ���� ��ġ�� ������ ��� �����ȿ� ��ġ�� �� Ʈ���Ÿ� ����ϴ� ���
    //   [1] HPC4_VECTOR_TRIGGER  : ���� Ʈ���� ��ġ�� ������ ��� ������ ���� ������ ��ġ�� �� Ʈ���Ÿ� ����ϴ� ���
    //   [3] HPC4_PATTERN_TRIGGER : ��ġ�� �����ϰ� ������ ������ŭ ������ ���ļ��� Ʈ���Ÿ� ����ϴ� ���
    function AxcTableSetTriggerMode (lModuleNo : LongInt; lTablePos : LongInt; uTrigMode : DWord) : DWord; stdcall;
    // ī���� ����� �� ���̺� ������ Ʈ���Ÿ� ����ϴ� ����� Ȯ���Ѵ�
    function AxcTableGetTriggerMode (lModuleNo : LongInt; lTablePos : LongInt; upTrigMode : PDWord) : DWord; stdcall;
    // ī���� ����� �� ���̺� ���� ��µ� ���� Ʈ���� ������ �ʱ�ȭ �Ѵ�.
    function AxcTableSetTriggerCountClear (lModuleNo : LongInt; lTablePos : LongInt) : DWord; stdcall;

    // ī���� ����� �� ���̺� 2-D ������ġ���� Ʈ���� ��ȣ�� ����ϱ� ���� �ʿ��� ������ �����Ѵ�.
    // lTriggerDataCount : ���� �� Ʈ���� ������ ��ü ����
    //   [-1, 0]         : ��ϵ� Ʈ���� ���� ����Ÿ �ʱ�ȭ
    // dpTriggerData     : 2-D ������ġ Ʈ���� ����(�ش� �迭�� ������ lTriggerDataCount * 2�� �Ǿ�ߵ�)
    //   *[0, 1]         : X[0], Y[0]
    // lpTriggerCount    : �Է��� 2-D ���� Ʈ���� ��ġ���� Ʈ���� ���� ���� �� �߻���ų Ʈ���� ������ �迭�� ����(�ش� �迭�� ������ lTriggerDataCount)
    // dpTriggerInterval : TriggerCount ��ŭ �����ؼ� Ʈ���Ÿ� �߻���ų�� ���� �� ������ ���ļ� ������ ����(�ش� �迭�� ������ lTriggerDataCount)
    // ������ :
    //    1) �� ���������� �迭 ������ �����Ͽ� ����ؾߵ˴ϴ�. ���ο��� ���Ǵ� ���� ���� ���� �迭�� �����ϸ� �޸� ���� ������ �߻� �� �� ����.
    //    2) Trigger Mode�� HPC4_RANGE_TRIGGER�� �ڵ� �����
    //    3) �Լ� ���ο��� Trigger�� Disable�� �� ��� ������ �����ϸ� �Ϸ� �� �ٽ� Enable ��Ŵ
    function AxcTableSetTriggerData (lModuleNo : LongInt; lTablePos : LongInt; lTriggerDataCount : LongInt; dpTriggerData : PDouble; lpTriggerCount : PLongInt; dpTriggerInterval : PDouble) : DWord; stdcall;
    // ī���� ����� �� ���̺� Ʈ���� ��ȣ�� ����ϱ� ���� ������ Ʈ���� ���� ������ Ȯ���Ѵ�.
    // �� ���� : �� ���̺� ��ϵ� �ִ� Ʈ���� ����Ÿ ������ �� ���� �Ʒ��� ���� Ʈ���� ����Ÿ ������ �̸� �ľ��� �� ����Ͻʽÿ�.
    // Ex)      1) AxcTableGetTriggerData(lModuleNo, lTablePos, &lTriggerDataCount, NULL, NULL, NULL);
    //          2) dpTriggerData     = new double[lTriggerDataCount * 2];
    //          3) lpTriggerCount    = new long[lTriggerDataCount];
    //          4) dpTriggerInterval = new double[lTriggerDataCount];
    function AxcTableGetTriggerData (lModuleNo : LongInt; lTablePos : LongInt; lpTriggerDataCount : PLongInt; dpTriggerData : PDouble; lpTriggerCount : PLongInt; dpTriggerInterval : PDouble) : DWord; stdcall;

    // ī���� ����� �� ���̺� 2-D ������ġ���� Ʈ���� ��ȣ�� ����ϱ� ���� �ʿ��� ������ AxcTableSetTriggerData�Լ��� �ٸ� ������� �����Ѵ�.
    // lTriggerDataCount : ���� �� Ʈ���� ������ ��ü ����
    // uOption : dpTriggerData �迭�� ����Ÿ �Է� ����� ����
    //   [0]   : dpTriggerData �迭�� X Pos[0], Y Pos[0], X Pos[1], Y Pos[1] ������ �Է�
    //   [1]   : dpTriggerData �迭�� X Pos[0], Y Pos[0], Count, Inteval, X Pos[1], Y Pos[1], Count, Inteval ������ �Է�
    // ������ :
    //    1) dpTriggerData�� �迭 ������ �����Ͽ� ����ؾߵ˴ϴ�. ���ο��� ���Ǵ� ���� ���� ���� �迭�� �����ϸ� �޸� ���� ������ �߻� �� �� ����.
    //    2) Trigger Mode�� HPC4_RANGE_TRIGGER�� �ڵ� �����
    //    3) �Լ� ���ο��� Trigger�� Disable�� �� ��� ������ �����ϸ� �Ϸ� �� �ٽ� Enable ��Ŵ
    function AxcTableSetTriggerDataEx (lModuleNo : LongInt; lTablePos : LongInt; lTriggerDataCount : LongInt; uOption : DWord; dpTriggerData : PDouble) : DWord; stdcall;
    // ī���� ����� �� ���̺� Ʈ���� ��ȣ�� ����ϱ� ���� ������ Ʈ���� ���� ������ Ȯ���Ѵ�.
    // �� ���� : �� ���̺� ��ϵ� �ִ� Ʈ���� ����Ÿ ������ �� ���� �Ʒ��� ���� Ʈ���� ����Ÿ ������ �̸� �ľ��� �� ���.
    // Ex)      1) AxcTableGetTriggerDataEx(lModuleNo, lTablePos, &lTriggerDataCount, &uOption, NULL);
    //          2) if(uOption == 0) : dpTriggerData     = new double[lTriggerDataCount * 2];
    //          3) if(uOption == 1) : dpTriggerData     = new double[lTriggerDataCount * 4];
    //          4) dpTriggerInterval = new double[lTriggerDataCount];
    function AxcTableGetTriggerDataEx (lModuleNo : LongInt; lTablePos : LongInt; lpTriggerDataCount : PLongInt; upOption : PDWord; dpTriggerData : PDouble) : DWord; stdcall;

    // ī���� ����� ������ ���̺� ������ ��� Ʈ���� ����Ÿ�� H/W FIFO�� ����Ÿ�� ��� �����Ѵ�.
    function AxcTableSetTriggerDataClear (lModuleNo : LongInt; lTablePos : LongInt) : DWord; stdcall;

    // ī���� ����� ������ ���̺��� Ʈ���� ��� ����� ���۽�Ŵ.
    // uEnable : Ʈ���Ÿ� ��� ����� ��뿩�θ� ����
    // �� ���� : 1) Ʈ���� ��� �� DISABLE�ϸ� ����� �ٷ� ����
    //           2) AxcTableTriggerOneShot, AxcTableGetPatternShotData,AxcTableSetTriggerData, AxcTableGetTriggerDataEx �Լ� ȣ��� �ڵ����� ENABLE��
    function AxcTableSetEnable (lModuleNo : LongInt; lTablePos : LongInt; uEnable : DWord) : DWord; stdcall;
    // ī���� ����� ������ ���̺��� Ʈ���� ��� ����� ���� ���θ� Ȯ����.
    function AxcTableGetEnable (lModuleNo : LongInt; lTablePos : LongInt; upEnable : PDWord) : DWord; stdcall;

    // ī���� ����� ������ ���̺��� �̿��� �߻��� Ʈ���� ������ Ȯ��.
    // lpTriggerCount : ������� ��µ� Ʈ���� ��� ������ ��ȯ, AxcTableSetTriggerCountClear �Լ��� �ʱ�ȭ
    function AxcTableReadTriggerCount (lModuleNo : LongInt; lTablePos : LongInt; lpTriggerCount : PLongInt) : DWord; stdcall;

    // ī���� ����� ������ ���̺� �Ҵ�� H/W Ʈ���� ����Ÿ FIFO�� ���¸� Ȯ��.
    // lpCount1[0~500] : 2D Ʈ���� ��ġ ����Ÿ �� ù��°(X) ��ġ�� �����ϰ� �ִ� H/W FIFO�� �Էµ� ����Ÿ ����
    // upStatus1 : 2D Ʈ���� ��ġ ����Ÿ �� ù��°(X) ��ġ�� �����ϰ� �ִ� H/W FIFO�� ����
    //   [Bit 0] : Data Empty
    //   [Bit 1] : Data Full
    //   [Bit 2] : Data Valid
    // lpCount2[0~500] : 2D Ʈ���� ��ġ ����Ÿ �� �ι�°(Y) ��ġ�� �����ϰ� �ִ� H/W FIFO�� �Էµ� ����Ÿ ����
    // upStatus2 : 2D Ʈ���� ��ġ ����Ÿ �� �ι�°(Y) ��ġ�� �����ϰ� �ִ� H/W FIFO�� ����
    //   [Bit 0] : Data Empty
    //   [Bit 1] : Data Full
    //   [Bit 2] : Data Valid
    function AxcTableReadFifoStatus (lModuleNo : LongInt; lTablePos : LongInt; lpCount1 : PLongInt; upStatus1 : PDWord; lpCount2 : PLongInt; upStatus2 : PDWord) : DWord; stdcall;

    // ī���� ����� ������ ���̺� �Ҵ�� H/W Ʈ���� ����Ÿ FIFO�� ���� ��ġ ����Ÿ���� Ȯ��.
    // dpTopData1 : 2D H/W Ʈ���� ����Ÿ FIFO�� ���� ����Ÿ �� ù��°(X) ��ġ ����Ÿ�� Ȯ�� ��
    // dpTopData1 : 2D H/W Ʈ���� ����Ÿ FIFO�� ���� ����Ÿ �� �ι�°(Y) ��ġ ����Ÿ�� Ȯ�� ��
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
