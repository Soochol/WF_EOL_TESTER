
unit AXDev;

interface

uses Windows, Messages, AXHS;


    // Board Number�� �̿��Ͽ� Board Address ã��
    function AxlGetBoardAddress (lBoardNo : LongInt; upBoardAddress : PDWord) : DWord; stdcall;
    // Board Number�� �̿��Ͽ� Board ID ã��
    function AxlGetBoardID (lBoardNo : LongInt; upBoardID : PDWord) : DWord; stdcall;
    // Board Number�� �̿��Ͽ� Board Version ã��
    function AxlGetBoardVersion (lBoardNo : LongInt; upBoardVersion : PDWord) : DWord; stdcall;
    // Board Number�� Module Position�� �̿��Ͽ� Module ID ã��
    function AxlGetModuleID (lBoardNo : LongInt; lModulePos : LongInt; upModuleID : PDWord) : DWord; stdcall;
    // Board Number�� Module Position�� �̿��Ͽ� Module Version ã��
    function AxlGetModuleVersion (lBoardNo : LongInt; lModulePos : LongInt; upModuleVersion : PDWord) : DWord; stdcall;
    // Board Number�� Module Position�� �̿��Ͽ� Network Node ���� Ȯ��
    function AxlGetModuleNodeInfo (lBoardNo : LongInt; lModulePos : LongInt; upNetNo : PLongInt; upNodeAddr : PDWord) : DWord; stdcall;

    // Board�� ����� ���� Data Flash Write (PCI-R1604[RTEX master board]����)
    // lPageAddr(0 ~ 199)
    // lByteNum(1 ~ 120)
    // ����) Flash�� ����Ÿ�� ������ ���� ���� �ð�(�ִ� 17mSec)�� �ҿ�Ǳ⶧���� ���� ����� ���� �ð��� �ʿ���.
    function AxlSetDataFlash (lBoardNo : LongInt; lPageAddr : LongInt; lBytesNum : LongInt; bpSetData : PByte) : DWord; stdcall;

    // Board�� ����� ESTOP �ܺ� �Է� ��ȣ�� �̿��� InterLock ��� ��� ���� �� ������ ���� ����� ���� (PCI-Rxx00[MLIII master board]����)
    // 1. ��� ����
    //   ����: ��� ��� ������ �ܺο��� ESTOP ��ȣ �ΰ��� ���忡 ����� ��� ���� ��忡 ���ؼ� ESTOP ���� ��� ����
    //    0: ��� ������� ����(�⺻ ������)
    //    1: ��� ���
    // 2. ������ ���� ��
    //      �Է� ���� ��� ���� ���� 1 ~ 40, ���� ��� Cyclic time
    // Board �� dwInterLock, dwDigFilterVal�� �̿��Ͽ� EstopInterLock ��� ����
    function AxlSetEStopInterLock (lBoardNo : LongInt; dwInterLock : DWord; dwDigFilterVal : DWord) : DWord; stdcall;
    // Board�� ������ dwInterLock, dwDigFilterVal ������ ��������
    function AxlGetEStopInterLock (lBoardNo : LongInt; dwInterLock : PDWord; dwDigFilterVal : PDWord) : DWord; stdcall;
    // Board�� �Էµ� EstopInterLock ��ȣ�� �д´�.
    function AxlReadEStopInterLock (lBoardNo : LongInt; dwInterLock : PDWord) : DWord; stdcall;

    // Board�� ����� ���� Data Flash Read(PCI-R1604[RTEX master board]����)
    // lPageAddr(0 ~ 199)
    // lByteNum(1 ~ 120)
    function AxlGetDataFlash (lBoardNo : LongInt; lPageAddr : LongInt; lBytesNum : LongInt; bpGetData : PByte) : DWord; stdcall;

    // Board Number�� Module Position�� �̿��Ͽ� AIO Module Number ã��
    function AxaInfoGetModuleNo (lBoardNo : LongInt; lModulePos : LongInt; lpModuleNo : PLongInt) : DWord; stdcall;
    // Board Number�� Module Position�� �̿��Ͽ� DIO Module Number ã��
    function AxdInfoGetModuleNo (lBoardNo : LongInt; lModulePos : LongInt; lpModuleNo : PLongInt) : DWord; stdcall;

    // ���� �࿡ IPCOMMAND Setting
    function AxmSetCommand (lAxisNo : LongInt; sCommand : Byte) : DWord; stdcall;
    // ���� �࿡ 8bit IPCOMMAND Setting
    function AxmSetCommandData08 (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // ���� �࿡ 8bit IPCOMMAND ��������
    function AxmGetCommandData08 (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // ���� �࿡ 16bit IPCOMMAND Setting
    function AxmSetCommandData16 (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // ���� �࿡ 16bit IPCOMMAND ��������
    function AxmGetCommandData16 (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // ���� �࿡ 24bit IPCOMMAND Setting
    function AxmSetCommandData24 (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // ���� �࿡ 24bit IPCOMMAND ��������
    function AxmGetCommandData24 (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // ���� �࿡ 32bit IPCOMMAND Setting
    function AxmSetCommandData32 (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // ���� �࿡ 32bit IPCOMMAND ��������
    function AxmGetCommandData32 (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;

    // ���� �࿡ QICOMMAND Setting
    function AxmSetCommandQi (lAxisNo : LongInt; sCommand : Byte) : DWord; stdcall;
    // ���� �࿡ 8bit QICOMMAND Setting
    function AxmSetCommandData08Qi (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // ���� �࿡ 8bit QICOMMAND ��������
    function AxmGetCommandData08Qi (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // ���� �࿡ 16bit QICOMMAND Setting
    function AxmSetCommandData16Qi (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // ���� �࿡ 16bit QICOMMAND ��������
    function AxmGetCommandData16Qi (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // ���� �࿡ 24bit QICOMMAND Setting
    function AxmSetCommandData24Qi (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // ���� �࿡ 24bit QICOMMAND ��������
    function AxmGetCommandData24Qi (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // ���� �࿡ 32bit QICOMMAND Setting
    function AxmSetCommandData32Qi (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // ���� �࿡ 32bit QICOMMAND ��������
    function AxmGetCommandData32Qi (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;

    // ���� �࿡ Port Data �������� - IP
    function AxmGetPortData (lAxisNo : LongInt; wOffset : Word; upData : PDWord) : DWord; stdcall;
    // ���� �࿡ Port Data Setting - IP
    function AxmSetPortData (lAxisNo : LongInt; wOffset : Word; dwData : DWord) : DWord; stdcall;
    // ���� �࿡ Port Data �������� - QI
    function AxmGetPortDataQi (lAxisNo : LongInt; byOffset : Word; wData : PWord) : DWord; stdcall;
    // ���� �࿡ Port Data Setting - QI
    function AxmSetPortDataQi (lAxisNo : LongInt; byOffset : Word; wData : Word) : DWord; stdcall;

    // ���� �࿡ ��ũ��Ʈ�� �����Ѵ�. - IP
    // sc    : ��ũ��Ʈ ��ȣ (1 - 4)
    // event : �߻��� �̺�Ʈ SCRCON �� �����Ѵ�.
    //         �̺�Ʈ ���� �హ������, �̺�Ʈ �߻��� ��, �̺�Ʈ ���� 1,2 �Ӽ� �����Ѵ�.
    // cmd   : � ������ �ٲܰ����� ���� SCRCMD�� �����Ѵ�.
    // data  : � Data�� �ٲܰ����� ����
    function AxmSetScriptCaptionIp (lAxisNo : LongInt; sc : LongInt; event : DWord; data : DWord) : DWord; stdcall;
    // ���� �࿡ ��ũ��Ʈ�� ��ȯ�Ѵ�. - IP
    function AxmGetScriptCaptionIp (lAxisNo : LongInt; sc : LongInt; event : PDWord; data : PDWord) : DWord; stdcall;

    // ���� �࿡ ��ũ��Ʈ�� �����Ѵ�. - QI
    // sc    : ��ũ��Ʈ ��ȣ (1 - 4)
    // event : �߻��� �̺�Ʈ SCRCON �� �����Ѵ�.
    //         �̺�Ʈ ���� �హ������, �̺�Ʈ �߻��� ��, �̺�Ʈ ���� 1,2 �Ӽ� �����Ѵ�.
    // cmd   : � ������ �ٲܰ����� ���� SCRCMD�� �����Ѵ�.
    // data  : � Data�� �ٲܰ����� ����
    function AxmSetScriptCaptionQi (lAxisNo : LongInt; sc : LongInt; event : DWord; cmd : DWord; data : DWord) : DWord; stdcall;
    // ���� �࿡ ��ũ��Ʈ�� ��ȯ�Ѵ�. - QI
    function AxmGetScriptCaptionQi (lAxisNo : LongInt; sc : LongInt; event : PDWord; cmd : PDWord; data : PDWord) : DWord; stdcall;

    // ���� �࿡ ��ũ��Ʈ ���� Queue Index�� Clear ��Ų��.
    // uSelect IP.
    // uSelect(0): ��ũ��Ʈ Queue Index �� Clear�Ѵ�.
    //        (1): ĸ�� Queue�� Index Clear�Ѵ�.
    // uSelect QI.
    // uSelect(0): ��ũ��Ʈ Queue 1 Index �� Clear�Ѵ�.
    //        (1): ��ũ��Ʈ Queue 2 Index �� Clear�Ѵ�.
    function AxmSetScriptCaptionQueueClear (lAxisNo : LongInt; uSelect : DWord) : DWord; stdcall;

    // ���� �࿡ ��ũ��Ʈ ���� Queue�� Index ��ȯ�Ѵ�.
    // uSelect IP
    // uSelect(0): ��ũ��Ʈ Queue Index�� �о�´�.
    //        (1): ĸ�� Queue Index�� �о�´�.
    // uSelect QI.
    // uSelect(0): ��ũ��Ʈ Queue 1 Index�� �о�´�.
    //        (1): ��ũ��Ʈ Queue 2 Index�� �о�´�.
    function AxmGetScriptCaptionQueueCount (lAxisNo : LongInt; updata : PDWord; uSelect : DWord) : DWord; stdcall;

    // ���� �࿡ ��ũ��Ʈ ���� Queue�� Data���� ��ȯ�Ѵ�.
    // uSelect IP
    // uSelect(0): ��ũ��Ʈ Queue Data �� �о�´�.
    //        (1): ĸ�� Queue Data�� �о�´�.
    // uSelect QI.
    // uSelect(0): ��ũ��Ʈ Queue 1 Data �о�´�.
    //        (1): ��ũ��Ʈ Queue 2 Data �о�´�.
    function AxmGetScriptCaptionQueueDataCount (lAxisNo : LongInt; updata : PDWord; uSelect : DWord) : DWord; stdcall;

    // ���� ����Ÿ�� �о�´�.
    function AxmGetOptimizeDriveData () : DWord; stdcall;


    // ���峻�� �������͸� Byte������ ���� �� Ȯ���Ѵ�.
    function AxmBoardWriteByte (lBoardNo : LongInt; wOffset : Word; byData : Byte) : DWord; stdcall;
    function AxmBoardReadByte (lBoardNo : LongInt; wOffset : Word; byData : PByte) : DWord; stdcall;

    // ���峻�� �������͸� Word������ ���� �� Ȯ���Ѵ�.
    function AxmBoardWriteWord (lBoardNo : LongInt; wOffset : Word; wData : Word) : DWord; stdcall;
    function AxmBoardReadWord (lBoardNo : LongInt; wOffset : Word; wData : PWord) : DWord; stdcall;

    // ���峻�� �������͸� DWord������ ���� �� Ȯ���Ѵ�.
    function AxmBoardWriteDWord (lBoardNo : LongInt; wOffset : Word; dwData : DWord) : DWord; stdcall;
    function AxmBoardReadDWord (lBoardNo : LongInt; wOffset : Word; dwData : PDWord) : DWord; stdcall;

    // ���峻�� ��⿡ �������͸� Byte���� �� Ȯ���Ѵ�.
    function AxmModuleWriteByte (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; byData : Byte) : DWord; stdcall;
    function AxmModuleReadByte (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; byData : PByte) : DWord; stdcall;

    // ���峻�� ��⿡ �������͸� Word���� �� Ȯ���Ѵ�.
    function AxmModuleWriteWord (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; wData : Word) : DWord; stdcall;
    function AxmModuleReadWord (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; wData : PWord) : DWord; stdcall;

    // ���峻�� ��⿡ �������͸� DWord���� �� Ȯ���Ѵ�.
    function AxmModuleWriteDWord (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; dwData : DWord) : DWord; stdcall;
    function AxmModuleReadDWord (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; dwData : PDWord) : DWord; stdcall;

    // �ܺ� ��ġ �񱳱⿡ ���� �����Ѵ�.(Pos = Unit)
    function AxmStatusSetActComparatorPos (lAxisNo : LongInt; dPos : Double) : DWord; stdcall;
    // �ܺ� ��ġ �񱳱⿡ ���� ��ȯ�Ѵ�.(Positon = Unit)
    function AxmStatusGetActComparatorPos (lAxisNo : LongInt; dpPos : PDouble) : DWord; stdcall;

    // ���� ��ġ �񱳱⿡ ���� �����Ѵ�.(Pos = Unit)
    function AxmStatusSetCmdComparatorPos (lAxisNo : LongInt; dPos : Double) : DWord; stdcall;
    // ���� ��ġ �񱳱⿡ ���� ��ȯ�Ѵ�.(Pos = Unit)
    function AxmStatusGetCmdComparatorPos (lAxisNo : LongInt; dpPos : PDouble) : DWord; stdcall;
    // ABS Position �� Flash �� �����Ѵ�.
    function AxmStatusSetFlashAbsOffset (lAxisNo : LongInt; dPosition : LongInt) : DWord; stdcall;
    // Flash �� ���� �� ABS Position �� ��ȯ�Ѵ�.
    // dReadType  : Value in Flash Memory (0), Real used Value in memory(1)
    function AxmStatusGetFlashAbsOffset (lAxisNo : LongInt; dPosition : PLongInt; dReadType : DWord) : DWord; stdcall;
    // ����ڰ� Flash �� ABS Position ������ �� �ִ� �ɼ��� �����Ѵ�.
    function AxmStatusSetAbsOffsetWriteEnable (lAxisNo : LongInt; bStatus : Boolean) : DWord; stdcall;
    // ABS Position ���� �ɼ��� ���¸� ��ȯ�Ѵ�.
    function AxmStatusGetAbsOffsetWriteEnable (lAxisNo : LongInt; bpStatus : bool*) : DWord; stdcall;

    //========== �߰� �Լ� =========================================================================================================
    // ���� ���� �� �ӵ��� ������ ���Ѵ�� �����Ѵ�.
    // �ӵ� ������� �Ÿ��� �־��־�� �Ѵ�.
    function AxmLineMoveVel (lCoord : LongInt; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    //========= ���� ��ġ ���� �Լ�( �ʵ�: IP������ , QI���� ��ɾ���)==============================================================
    // ���� ���� Sensor ��ȣ�� ��� ���� �� ��ȣ �Է� ������ �����Ѵ�.
    // ��� ���� LOW(0), HIGH(1), UNUSED(2), USED(3)
    function AxmSensorSetSignal (lAxisNo : LongInt; uLevel : DWord) : DWord; stdcall;
    // ���� ���� Sensor ��ȣ�� ��� ���� �� ��ȣ �Է� ������ ��ȯ�Ѵ�.
    function AxmSensorGetSignal (lAxisNo : LongInt; upLevel : PDWord) : DWord; stdcall;
    // ���� ���� Sensor ��ȣ�� �Է� ���¸� ��ȯ�Ѵ�
    function AxmSensorReadSignal (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // ���� ���� ������ �ӵ��� �������� ���� ��ġ ����̹��� �����Ѵ�.
    // Sensor ��ȣ�� Active level�Է� ���� ��� ��ǥ�� ������ �Ÿ���ŭ ������ �����Ѵ�.
    // �޽��� ��µǴ� �������� �Լ��� �����.
    // lMethod :  0 - �Ϲ� ����, 1 - ���� ��ȣ ���� ���� ���� ����. ��ȣ ���� �� �Ϲ� ����
    //            2 - ���� ����
    function AxmSensorMovePos (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; lMethod : LongInt) : DWord; stdcall;

    // ���� ���� ������ �ӵ��� �������� ���� ��ġ ����̹��� �����Ѵ�.
    // Sensor ��ȣ�� Active level�Է� ���� ��� ��ǥ�� ������ �Ÿ���ŭ ������ �����Ѵ�.
    // �޽� ����� ����Ǵ� �������� �Լ��� �����.
    function AxmSensorStartMovePos (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; lMethod : LongInt) : DWord; stdcall;

    // �����˻� ���ེ�� ��ȭ�� ����� ��ȯ�Ѵ�.
    // *lpStepCount      : ��ϵ� Step�� ����
    // *upMainStepNumber : ��ϵ� MainStepNumber ������ �迭����Ʈ
    // *upStepNumber     : ��ϵ� StepNumber ������ �迭����Ʈ
    // *upStepBranch     : ��ϵ� Step�� Branch ������ �迭����Ʈ
    // ����: �迭������ 50���� ����
    function AxmHomeGetStepTrace (lAxisNo : LongInt; lpStepCount : PLongInt; upMainStepNumber : PDWord; upStepNumber : PDWord; upStepBranch : PDWord) : DWord; stdcall;

    //=======�߰� Ȩ ��ġ (PI-N804/404���� �ش��.)=================================================================================
    // ����ڰ� ������ ���� Ȩ���� �Ķ��Ÿ�� �����Ѵ�.(QIĨ ���� �������� �̿�).
    // uZphasCount : Ȩ �Ϸ��Ŀ� Z�� ī��Ʈ(0 - 15)
    // lHomeMode   : Ȩ ���� ���( 0 - 12)
    // lClearSet   : ��ġ Ŭ���� , �ܿ��޽� Ŭ���� ��� ���� (0 - 3)
    //               0: ��ġŬ���� ������, �ܿ��޽� Ŭ���� ��� ����
    //                 1: ��ġŬ���� �����, �ܿ��޽� Ŭ���� ��� ����
    //               2: ��ġŬ���� ������, �ܿ��޽� Ŭ���� �����
    //               3: ��ġŬ���� �����, �ܿ��޽� Ŭ���� �����.
    // dOrgVel : Ȩ���� Org  Speed ����
    // dLastVel: Ȩ���� Last Speed ����
    function AxmHomeSetConfig (lAxisNo : LongInt; uZphasCount : DWord; lHomeMode : LongInt; lClearSet : LongInt; dOrgVel : Double; dLastVel : Double; dLeavePos : Double) : DWord; stdcall;
    // ����ڰ� ������ ���� Ȩ���� �Ķ��Ÿ�� ��ȯ�Ѵ�.
    function AxmHomeGetConfig (lAxisNo : LongInt; upZphasCount : PDWord; lpHomeMode : PLongInt; lpClearSet : PLongInt; dpOrgVel : PDouble; dpLastVel : PDouble; dpLeavePos : PDouble) : DWord; stdcall;

    // ����ڰ� ������ ���� Ȩ ��ġ�� �����Ѵ�.
    // lHomeMode ���� ���� : 0 - 5 ���� (Move Return�Ŀ� Search��  �����Ѵ�.)
    // lHomeMode -1�� �״�� ���� HomeConfig���� ����Ѵ�� �״�� ������.
    // ��������      : Vel���� ����̸� CW, �����̸� CCW.
    function AxmHomeSetMoveSearch (lAxisNo : LongInt; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // ����ڰ� ������ ���� Ȩ ������ �����Ѵ�.
    // lHomeMode ���� ���� : 0 - 12 ����
    // lHomeMode -1�� �״�� ���� HomeConfig���� ����Ѵ�� �״�� ������.
    // ��������      : Vel���� ����̸� CW, �����̸� CCW.
    function AxmHomeSetMoveReturn (lAxisNo : LongInt; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // ����ڰ� ������ ���� Ȩ ��Ż�� �����Ѵ�.
    // ��������      : Vel���� ����̸� CW, �����̸� CCW.
    function AxmHomeSetMoveLeave (lAxisNo : LongInt; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // ����ڰ� ������ ������ Ȩ ��ġ�� �����Ѵ�.
    // lHomeMode ���� ���� : 0 - 5 ���� (Move Return�Ŀ� Search��  �����Ѵ�.)
    // lHomeMode -1�� �״�� ���� HomeConfig���� ����Ѵ�� �״�� ������.
    // ��������      : Vel���� ����̸� CW, �����̸� CCW.
    function AxmHomeSetMultiMoveSearch (lArraySize : LongInt; lpAxesNo : PLongInt; dpVel : PDouble; dpAccel : PDouble; dpDecel : PDouble) : DWord; stdcall;

    //������ ��ǥ���� ���� �ӵ� �������� ��带 �����Ѵ�.
    // (������ : �ݵ�� ����� �ϰ� ��밡��)
    // ProfileMode : '0' - ��Ī Trapezode
    //               '1' - ���Ī Trapezode
    //               '2' - ��Ī Quasi-S Curve
    //               '3' - ��Ī S Curve
    //               '4' - ���Ī S Curve
    function AxmContiSetProfileMode (lCoord : LongInt; uProfileMode : DWord) : DWord; stdcall;
    // ������ ��ǥ���� ���� �ӵ� �������� ��带 ��ȯ�Ѵ�.
    function AxmContiGetProfileMode (lCoord : LongInt; upProfileMode : PDWord) : DWord; stdcall;

    //========== DIO ���ͷ�Ʈ �÷��� ������Ʈ �б�
    // ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� bit ������ ���ͷ�Ʈ �߻� ���� ���� ����
    function AxdiInterruptFlagReadBit (lModuleNo : LongInt; lOffset : LongInt; upValue : PDWord) : DWord; stdcall;
    // ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� byte ������ ���ͷ�Ʈ �߻� ���� ���� ����
    function AxdiInterruptFlagReadByte (lModuleNo : LongInt; lOffset : LongInt; upValue : PDWord) : DWord; stdcall;
    // ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� word ������ ���ͷ�Ʈ �߻� ���� ���� ����
    function AxdiInterruptFlagReadWord (lModuleNo : LongInt; lOffset : LongInt; upValue : PDWord) : DWord; stdcall;
    // ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� double word ������ ���ͷ�Ʈ �߻� ���� ���� ����
    function AxdiInterruptFlagReadDword (lModuleNo : LongInt; lOffset : LongInt; upValue : PDWord) : DWord; stdcall;
    // ��ü �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� bit ������ ���ͷ�Ʈ �߻� ���� ���� ����
    function AxdiInterruptFlagRead (lOffset : LongInt; upValue : PDWord) : DWord; stdcall;

    //========= �α� ���� �Լ� ==========================================================================================
    // ���� �ڵ����� ������.
    // ���� ���� �Լ� ���� ����� EzSpy���� ����͸� �� �� �ֵ��� ���� �Ǵ� �����ϴ� �Լ��̴�.
    // uUse : ��� ���� => DISABLE(0), ENABLE(1)
    function AxmLogSetAxis (lAxisNo : LongInt; uUse : DWord) : DWord; stdcall;

    // EzSpy������ ���� �� �Լ� ���� ��� ����͸� ���θ� Ȯ���ϴ� �Լ��̴�.
    function AxmLogGetAxis (lAxisNo : LongInt; upUse : PDWord) : DWord; stdcall;

    //=========== �α� ��� ���� �Լ�
    //������ �Է� ä���� EzSpy�� �α� ��� ���θ� �����Ѵ�.
    function AxaiLogSetChannel (lChannelNo : LongInt; uUse : DWord) : DWord; stdcall;
    //������ �Է� ä���� EzSpy�� �α� ��� ���θ� Ȯ���Ѵ�.
    function AxaiLogGetChannel (lChannelNo : LongInt; upUse : PDWord) : DWord; stdcall;

    //==������ ��� ä���� EzSpy �α� ���
    //������ ��� ä���� EzSpy�� �α� ��� ���θ� �����Ѵ�.
    function AxaoLogSetChannel (lChannelNo : LongInt; uUse : DWord) : DWord; stdcall;
    //������ ��� ä���� EzSpy�� �α� ��� ���θ� Ȯ���Ѵ�.
    function AxaoLogGetChannel (lChannelNo : LongInt; upUse : PDWord) : DWord; stdcall;

    //==Log
    // ������ ����� EzSpy�� �α� ��� ���� ����
    function AxdLogSetModule (lModuleNo : LongInt; uUse : DWord) : DWord; stdcall;
    // ������ ����� EzSpy�� �α� ��� ���� Ȯ��
    function AxdLogGetModule (lModuleNo : LongInt; upUse : PDWord) : DWord; stdcall;

    // ������ ���尡 RTEX ����� �� �� ������ firmware ������ Ȯ���Ѵ�.
    function AxlGetFirmwareVersion (lBoardNo : LongInt; szVersion : PChar) : DWord; stdcall;
    // ������ ����� Firmware�� ���� �Ѵ�.
    function AxlSetFirmwareCopy (lBoardNo : LongInt; wData : PWord; wCmdData : PWord) : DWord; stdcall;
    // ������ ����� Firmware Update�� �����Ѵ�.
    function AxlSetFirmwareUpdate (lBoardNo : LongInt) : DWord; stdcall;
    // ������ ������ ���� RTEX �ʱ�ȭ ���¸� Ȯ�� �Ѵ�.
    function AxlCheckStatus (lBoardNo : LongInt; dwStatus : PDWord) : DWord; stdcall;
    // ������ �࿡ RTEX Master board�� ���� ����� ���� �մϴ�.
    function AxlRtexUniversalCmd (lBoardNo : LongInt; wCmd : Word; wOffset : Word; wData : PWord) : DWord; stdcall;
    // ������ ���� RTEX ��� ����� �����Ѵ�.
    function AxmRtexSlaveCmd (lAxisNo : LongInt; dwCmdCode : DWord; dwTypeCode : DWord; dwIndexCode : DWord; dwCmdConfigure : DWord; dwValue : DWord) : DWord; stdcall;
    // ������ �࿡ ������ RTEX ��� ����� ������� Ȯ���Ѵ�.
    function AxmRtexGetSlaveCmdResult (lAxisNo : LongInt; dwIndex : PDWord; dwValue : PDWord) : DWord; stdcall;
    // ������ �࿡ ������ RTEX ��� ����� ������� Ȯ���Ѵ�. PCIE-Rxx04-RTEX ����
    function AxmRtexGetSlaveCmdResultEx (lAxisNo : LongInt; dwpCommand : PDWord; dwpType : PDWord; dwpIndex : PDWord; dwpValue : PDWord) : DWord; stdcall;
    // ������ �࿡ RTEX ���� ������ Ȯ���Ѵ�.
    function AxmRtexGetAxisStatus (lAxisNo : LongInt; dwStatus : PDWord) : DWord; stdcall;
    // ������ �࿡ RTEX ��� ���� ������ Ȯ���Ѵ�.(Actual position, Velocity, Torque)
    function AxmRtexGetAxisReturnData (lAxisNo : LongInt; dwReturn1 : PDWord; dwReturn2 : PDWord; dwReturn3 : PDWord) : DWord; stdcall;
    // ������ �࿡ RTEX Slave ���� ���� ���� ������ Ȯ���Ѵ�.(mechanical, Inposition and etc)
    function AxmRtexGetAxisSlaveStatus (lAxisNo : LongInt; dwStatus : PDWord) : DWord; stdcall;

    // ������ �࿡ MLII Slave �࿡ ���� ��Ʈ�� ��ɾ �����Ѵ�.
    function AxmSetAxisCmd (lAxisNo : LongInt; tagCommand : PDWord) : DWord; stdcall;
    // ������ �࿡ MLII Slave �࿡ ���� ��Ʈ�� ����� ����� Ȯ���Ѵ�.
    function AxmGetAxisCmdResult (lAxisNo : LongInt; tagCommand : PDWord) : DWord; stdcall;

    // ������ SIIIH Slave ��⿡ ��Ʈ�� ����� ����� �����ϰ� ��ȯ �Ѵ�.
    function AxdSetAndGetSlaveCmdResult (lModuleNo : LongInt; tagSetCommand : PDWord; tagGetCommand : PDWord) : DWord; stdcall;
    function AxaSetAndGetSlaveCmdResult (lModuleNo : LongInt; tagSetCommand : PDWord; tagGetCommand : PDWord) : DWord; stdcall;
    function AxcSetAndGetSlaveCmdResult (lModuleNo : LongInt; tagSetCommand : PDWord; tagGetCommand : PDWord) : DWord; stdcall;

    // DPRAM �����͸� Ȯ���Ѵ�.
    function AxlGetDpRamData (lBoardNo : LongInt; wAddress : Word; dwpRdData : PDWord) : DWord; stdcall;
    // DPRAM �����͸� Word������ Ȯ���Ѵ�.
    function AxlBoardReadDpramWord (lBoardNo : LongInt; wOffset : Word; dwpRdData : PDWord) : DWord; stdcall;
    // DPRAM �����͸� Word������ �����Ѵ�.
    function AxlBoardWriteDpramWord (lBoardNo : LongInt; wOffset : Word; dwWrData : DWord) : DWord; stdcall;

    // �� ������ �� SLAVE���� ����� �����Ѵ�.
    function AxlSetSendBoardEachCommand (lBoardNo : LongInt; dwCommand : DWord; dwpSendData : PDWord; dwLength : DWord) : DWord; stdcall;
    // �� ����� ����� �����Ѵ�.
    function AxlSetSendBoardCommand (lBoardNo : LongInt; dwCommand : DWord; dwpSendData : PDWord; dwLength : DWord) : DWord; stdcall;
    // �� ������ ������ Ȯ���Ѵ�.
    function AxlGetResponseBoardCommand (lBoardNo : LongInt; dwpReadData : PDWord) : DWord; stdcall;

    // Network Type Master ���忡�� Slave ���� Firmware Version�� �о� ���� �Լ�.
    // ucaFirmwareVersion unsigned char ���� Array�� �����ϰ� ũ�Ⱑ 4�̻��� �ǵ��� ���� �ؾ� �Ѵ�.
    function AxmInfoGetFirmwareVersion (lAxisNo : LongInt; ucaFirmwareVersion : PWord) : DWord; stdcall;
    function AxaInfoGetFirmwareVersion (lModuleNo : LongInt; ucaFirmwareVersion : PWord) : DWord; stdcall;
    function AxdInfoGetFirmwareVersion (lModuleNo : LongInt; ucaFirmwareVersion : PWord) : DWord; stdcall;
    function AxcInfoGetFirmwareVersion (lModuleNo : LongInt; ucaFirmwareVersion : PWord) : DWord; stdcall;

    //======== PCI-R1604-MLII ���� �Լ�===========================================================================
    // INTERPOLATE and LATCH Command�� Option Field�� Torq Feed Forward�� ���� ���� �ϵ��� �մϴ�.
    // �⺻���� MAX�� �����Ǿ� �ֽ��ϴ�.
    // �������� 0 ~ 4000H���� ���� �� �� �ֽ��ϴ�.
    // �������� 4000H�̻����� �����ϸ� ������ �� �̻����� �����ǳ� ������ 4000H���� ���� �˴ϴ�.
    function AxmSetTorqFeedForward (lAxisNo : LongInt; dwTorqFeedForward : DWord) : DWord; stdcall;

    // INTERPOLATE and LATCH Command�� Option Field�� Torq Feed Forward�� ���� �о���� �Լ� �Դϴ�.
    // �⺻���� MAX�� �����Ǿ� �ֽ��ϴ�.
    function AxmGetTorqFeedForward (lAxisNo : LongInt; dwpTorqFeedForward : PDWord) : DWord; stdcall;

    // INTERPOLATE and LATCH Command�� VFF Field�� Velocity Feed Forward�� ���� ���� �ϵ��� �մϴ�.
    // �⺻���� '0'�� �����Ǿ� �ֽ��ϴ�.
    // �������� 0 ~ FFFFH���� ���� �� �� �ֽ��ϴ�.
    function AxmSetVelocityFeedForward (lAxisNo : LongInt; dwVelocityFeedForward : DWord) : DWord; stdcall;

    // INTERPOLATE and LATCH Command�� VFF Field�� Velocity Feed Forward�� ���� �о���� �Լ� �Դϴ�.
    function AxmGetVelocityFeedForward (lAxisNo : LongInt; dwpVelocityFeedForward : PDWord) : DWord; stdcall;

    // Encoder type�� �����Ѵ�.
    // �⺻���� 0(TYPE_INCREMENTAL)�� �����Ǿ� �ֽ��ϴ�.
    // �������� 0 ~ 1���� ���� �� �� �ֽ��ϴ�.
    // ������ : 0(TYPE_INCREMENTAL), 1(TYPE_ABSOLUTE).
    function AxmSignalSetEncoderType (lAxisNo : LongInt; dwEncoderType : DWord) : DWord; stdcall;

    // Encoder type�� Ȯ���Ѵ�.
    function AxmSignalGetEncoderType (lAxisNo : LongInt; dwpEncoderType : PDWord) : DWord; stdcall;
    //========================================================================================================

    // Slave Firmware Update�� ���� �߰�
    //DWORD   __stdcall AxmSetSendAxisCommand(long lAxisNo, WORD wCommand, WORD* wpSendData, WORD wLength);

    //======== PCI-R1604-RTEX, RTEX-PM ���� �Լ�==============================================================
    // ���� �Է� 2,3�� �Է½� JOG ���� �ӵ��� �����Ѵ�.
    // ������ ���õ� ��� ����(Ex, PulseOutMethod, MoveUnitPerPulse ��)���� �Ϸ�� ���� �ѹ��� �����Ͽ��� �Ѵ�.
    function AxmMotSetUserMotion (lAxisNo : LongInt; dVelocity : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // ���� �Է� 2,3�� �Է½� JOG ���� ���� ��� ���θ� �����Ѵ�.
    // ������ :  0(DISABLE), 1(ENABLE)
    function AxmMotSetUserMotionUsage (lAxisNo : LongInt; dwUsage : DWord) : DWord; stdcall;

    // MPGP �Է��� ����Ͽ� Load/UnLoad ��ġ�� �ڵ����� �̵��ϴ� ��� ����.
    function AxmMotSetUserPosMotion (lAxisNo : LongInt; dVelocity : Double; dAccel : Double; dDecel : Double; dLoadPos : Double; dUnLoadPos : Double; dwFilter : DWord; dwDelay : DWord) : DWord; stdcall;

    // MPGP �Է��� ����Ͽ� Load/UnLoad ��ġ�� �ڵ����� �̵��ϴ� ��� ����.
    // ������ :  0(DISABLE), 1(Position ��� A ���), 2(Position ��� B ���)
    function AxmMotSetUserPosMotionUsage (lAxisNo : LongInt; dwUsage : DWord) : DWord; stdcall;
    //========================================================================================================

    //======== SIO-CN2CH/HPC4, ���� ��ġ Ʈ���� ��� ��� ���� �Լ�================================================
    // �޸� ������ ���� �Լ�
    function AxcKeWriteRamDataAddr (lChannelNo : LongInt; dwAddr : DWord; dwData : DWord) : DWord; stdcall;
    // �޸� ������ �б� �Լ�
    function AxcKeReadRamDataAddr (lChannelNo : LongInt; dwAddr : DWord; dwpData : PDWord) : DWord; stdcall;
    // �޸� �ʱ�ȭ �Լ�
    function AxcKeResetRamDataAll (lModuleNo : LongInt; dwData : DWord) : DWord; stdcall;
    // Ʈ���� Ÿ�� �ƿ� ���� �Լ�
    function AxcTriggerSetTimeout (lChannelNo : LongInt; dwTimeout : DWord) : DWord; stdcall;
    // Ʈ���� Ÿ�� �ƿ� Ȯ�� �Լ�
    function AxcTriggerGetTimeout (lChannelNo : LongInt; dwpTimeout : PDWord) : DWord; stdcall;
    // Ʈ���� ��� ���� Ȯ�� �Լ�
    function AxcStatusGetWaitState (lChannelNo : LongInt; dwpState : PDWord) : DWord; stdcall;
    // Ʈ���� ��� ���� ���� �Լ�
    function AxcStatusSetWaitState (lChannelNo : LongInt; dwState : DWord) : DWord; stdcall;

    // ���� ä�ο� ��ɾ� ����.
    function AxcKeSetCommandData32 (lChannelNo : LongInt; dwCommand : DWord; dwData : DWord) : DWord; stdcall;
    // ���� ä�ο� ��ɾ� ����.
    function AxcKeSetCommandData16 (lChannelNo : LongInt; dwCommand : DWord; wData : Word) : DWord; stdcall;
    // ���� ä���� �������� Ȯ��.
    function AxcKeGetCommandData32 (lChannelNo : LongInt; dwCommand : DWord; dwpData : PDWord) : DWord; stdcall;
    // ���� ä���� �������� Ȯ��.
    function AxcKeGetCommandData16 (lChannelNo : LongInt; dwCommand : DWord; wpData : PWord) : DWord; stdcall;
    //========================================================================================================

    //======== PCI-N804/N404 ����, Sequence Motion ===================================================================
    // Sequence Motion�� �� ������ ���� �մϴ�. (�ּ� 1��)
    // lSeqMapNo : �� ��ȣ ������ ��� Sequence Motion Index Point
    // lSeqMapSize : �� ��ȣ ����
    // long* LSeqAxesNo : �� ��ȣ �迭
    function AxmSeqSetAxisMap (lSeqMapNo : LongInt; lSeqMapSize : LongInt; lSeqAxesNo : PLongInt) : DWord; stdcall;
    function AxmSeqGetAxisMap (lSeqMapNo : LongInt; lSeqMapSize : PLongInt; lSeqAxesNo : PLongInt) : DWord; stdcall;

    // Sequence Motion�� ����(Master) ���� ���� �մϴ�.
    // �ݵ�� AxmSeqSetAxisMap(...) �� ������ �� ������ �����Ͽ��� �մϴ�.
    function AxmSeqSetMasterAxisNo (lSeqMapNo : LongInt; lMasterAxisNo : LongInt) : DWord; stdcall;

    // Sequence Motion�� Node ���� ������ ���̺귯���� �˸��ϴ�.
    function AxmSeqBeginNode (lSeqMapNo : LongInt) : DWord; stdcall;

    // Sequence Motion�� Node ���� ���Ḧ ���̺귯���� �˸��ϴ�.
    function AxmSeqEndNode (lSeqMapNo : LongInt) : DWord; stdcall;

    // Sequence Motion�� ������ ���� �մϴ�.
    function AxmSeqStart (lSeqMapNo : LongInt; dwStartOption : DWord) : DWord; stdcall;

    // Sequence Motion�� �� Profile Node ������ ���̺귯���� �Է� �մϴ�.
    // ���� 1�� Sequence Motion�� ����ϴ���, *dPosition�� 1���� Array�� �����Ͽ� �ֽñ� �ٶ��ϴ�.
    function AxmSeqAddNode (lSeqMapNo : LongInt; dPosition : PDouble; dVelocity : Double; dAcceleration : Double; dDeceleration : Double; dNextVelocity : Double) : DWord; stdcall;

    // Sequence Motion�� ���� �� ���� ���� ���� Node Index�� �˷� �ݴϴ�.
    function AxmSeqGetNodeNum (lSeqMapNo : LongInt; lCurNodeNo : PLongInt) : DWord; stdcall;

    // Sequence Motion�� �� Node Count�� Ȯ�� �մϴ�.
    function AxmSeqGetTotalNodeNum (lSeqMapNo : LongInt; lTotalNodeCnt : PLongInt) : DWord; stdcall;

    // Sequence Motion�� ���� ���� ������ Ȯ�� �մϴ�.
    // dwInMotion : 0(���� ����), 1(���� ��)
    function AxmSeqIsMotion (lSeqMapNo : LongInt; dwInMotion : PDWord) : DWord; stdcall;

    // Sequence Motion�� Memory�� Clear �մϴ�.
    // AxmSeqSetAxisMap(...), AxmSeqSetMasterAxisNo(...) ���� ������ ���� �����˴ϴ�.
    function AxmSeqWriteClear (lSeqMapNo : LongInt) : DWord; stdcall;

    // Sequence Motion�� ������ ���� �մϴ�.
    // dwStopMode : 0(EMERGENCY_STOP), 1(SLOWDOWN_STOP)
    function AxmSeqStop (lSeqMapNo : LongInt; dwStopMode : DWord) : DWord; stdcall;
    //========================================================================================================


    //======== PCIe-Rxx04-SIIIH ���� �Լ�==========================================================================
    // (SIIIH, MR_J4_xxB, Para : 0 ~ 8) ==
    //     [0] : Command Position
    //     [1] : Actual Position
    //     [2] : Actual Velocity
    //     [3] : Mechanical Signal
    //     [4] : Regeneration load factor(%)
    //     [5] : Effective load factor(%)
    //     [6] : Peak load factor(%)
    //     [7] : Current Feedback
    //     [8] : Command Velocity
    function AxmStatusSetMon (lAxisNo : LongInt; dwParaNo1 : DWord; dwParaNo2 : DWord; dwParaNo3 : DWord; dwParaNo4 : DWord; dwUse : DWord) : DWord; stdcall;
    function AxmStatusGetMon (lAxisNo : LongInt; dwpParaNo1 : PDWord; dwpParaNo2 : PDWord; dwpParaNo3 : PDWord; dwpParaNo4 : PDWord; dwpUse : PDWord) : DWord; stdcall;
    function AxmStatusReadMon (lAxisNo : LongInt; dwpParaNo1 : PDWord; dwpParaNo2 : PDWord; dwpParaNo3 : PDWord; dwpParaNo4 : PDWord; dwDataVaild : PDWord) : DWord; stdcall;
    function AxmStatusReadMonEx (lAxisNo : LongInt; lpDataCnt : PLongInt; dwpReadData : PDWord) : DWord; stdcall;
    //=============================================================================================================

    //======== PCI-R32IOEV-RTEX ���� �Լ�===========================================================================
    // I/O ��Ʈ�� �Ҵ�� HPI register �� �а� �������� API �Լ�.
    // I/O Registers for HOST interface.
    // I/O 00h Host status register (HSR)
    // I/O 04h Host-to-DSP control register (HDCR)
    // I/O 08h DSP page register (DSPP)
    // I/O 0Ch Reserved
    function AxlSetIoPort (lBoardNo : LongInt; dwAddr : DWord; dwData : DWord) : DWord; stdcall;
    function AxlGetIoPort (lBoardNo : LongInt; dwAddr : DWord; dwpData : PDWord) : DWord; stdcall;

    //======== PCI-R3200-MLIII ���� �Լ�===========================================================================
    /*
    // M-III Master ���� �߿��� ������Ʈ �⺻ ���� ���� �Լ�
    DWORD   __stdcall AxlM3SetFWUpdateInit(long lBoardNo, DWORD dwTotalPacketSize);
    // M-III Master ���� �߿��� ������Ʈ �⺻ ���� ���� ��� Ȯ�� �Լ�
    DWORD   __stdcall AxlM3GetFWUpdateInit(long lBoardNo, DWORD *dwTotalPacketSize);
    // M-III Master ���� �߿��� ������Ʈ �ڷ� ���� �Լ�
    DWORD   __stdcall AxlM3SetFWUpdateCopy(long lBoardNo, DWORD *lFWUpdataData, DWORD dwLength);
    // M-III Master ���� �߿��� ������Ʈ �ڷ� ���� ��� Ȯ�� �Լ�
    DWORD   __stdcall AxlM3GetFWUpdateCopy(long lBoardNo, BYTE bCrcData, DWORD *lFWUpdataResult);
    // M-III Master ���� �߿��� ������Ʈ ����
    DWORD   __stdcall AxlM3SetFWUpdate(long lBoardNo, DWORD dwSectorNo);
    // M-III Master ���� �߿��� ������Ʈ ���� ��� Ȯ��
    DWORD   __stdcall AxlM3GetFWUpdate(long lBoardNo, DWORD *dwSectorNo, DWORD *dwIsDone);
    */
    // M-III Master ���� �߿��� ������Ʈ �⺻ ���� ���� �Լ�
    function AxlM3SetFWUpdateInit (lBoardNo : LongInt; dwTotalPacketSize : DWord; dwProcTotalStepNo : DWord) : DWord; stdcall;
    // M-III Master ���� �߿��� ������Ʈ �⺻ ���� ���� ��� Ȯ�� �Լ�
    function AxlM3GetFWUpdateInit (lBoardNo : LongInt; dwTotalPacketSize : PDWord; dwProcTotalStepNo : PDWord) : DWord; stdcall;

    // M-III Master ���� �߿��� ������Ʈ �ڷ� ���� �Լ�
    function AxlM3SetFWUpdateCopy (lBoardNo : LongInt; pdwPacketData : PDWord; dwPacketSize : DWord) : DWord; stdcall;
    // M-III Master ���� �߿��� ������Ʈ �ڷ� ���� ��� Ȯ�� �Լ�
    function AxlM3GetFWUpdateCopy (lBoardNo : LongInt; dwPacketSize : PDWord) : DWord; stdcall;

    // M-III Master ���� �߿��� ������Ʈ ����
    function AxlM3SetFWUpdate (lBoardNo : LongInt; dwFlashBurnStepNo : DWord) : DWord; stdcall;
    // M-III Master ���� �߿��� ������Ʈ ���� ��� Ȯ��
    function AxlM3GetFWUpdate (lBoardNo : LongInt; dwFlashBurnStepNo : PDWord; dwIsFlashBurnDone : PDWord) : DWord; stdcall;

    // M-III Master ���� EEPROM ������ ���� �Լ�
    function AxlM3SetCFGData (lBoardNo : LongInt; pCmdData : PDWord; CmdDataSize : DWord) : DWord; stdcall;
    // M-III Master ���� EEPROM ������ �������� �Լ�
    function AxlM3GetCFGData (lBoardNo : LongInt; pCmdData : PDWord; CmdDataSize : DWord) : DWord; stdcall;

    // M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� �Լ�
    function AxlM3SetMCParaUpdateInit (lBoardNo : LongInt; wCh0Slaves : Word; wCh1Slaves : Word; dwCh0CycTime : DWord; dwCh1CycTime : DWord; dwChInfoMaxRetry : DWord) : DWord; stdcall;
    // M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� ��� Ȯ�� �Լ�
    function AxlM3GetMCParaUpdateInit (lBoardNo : LongInt; wCh0Slaves : PWord; wCh1Slaves : PWord; dwCh0CycTime : PDWord; dwCh1CycTime : PDWord; dwChInfoMaxRetry : PDWord) : DWord; stdcall;
    // M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� �Լ�
    function AxlM3SetMCParaUpdateCopy (lBoardNo : LongInt; wIdx : Word; wChannel : Word; wSlaveAddr : Word; dwProtoCalType : DWord; dwTransBytes : DWord; dwDeviceCode : DWord) : DWord; stdcall;
    // M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� ��� Ȯ�� �Լ�
    function AxlM3GetMCParaUpdateCopy (lBoardNo : LongInt; wIdx : Word; wChannel : PWord; wSlaveAddr : PWord; dwProtoCalType : PDWord; dwTransBytes : PDWord; dwDeviceCode : PDWord) : DWord; stdcall;

    // M-III Master ���峻�� �������͸� DWord������ Ȯ�� �Լ�
    function AxlBoardReadDWord (lBoardNo : LongInt; wOffset : Word; dwData : PDWord) : DWord; stdcall;
    // M-III Master ���峻�� �������͸� DWord������ ���� �Լ�
    function AxlBoardWriteDWord (lBoardNo : LongInt; wOffset : Word; dwData : DWord) : DWord; stdcall;

    // ���峻�� Ȯ�� �������͸� DWord������ ���� �� Ȯ���Ѵ�.
    function AxlBoardReadDWordEx (lBoardNo : LongInt; dwOffset : DWord; dwData : PDWord) : DWord; stdcall;
    function AxlBoardWriteDWordEx (lBoardNo : LongInt; dwOffset : DWord; dwData : DWord) : DWord; stdcall;

    // ������ ���� ���� ���� �Լ�
    function AxmM3ServoSetCtrlStopMode (lAxisNo : LongInt; bStopMode : Byte) : DWord; stdcall;
    // ������ Lt ���� ���·� ���� �Լ�
    function AxmM3ServoSetCtrlLtSel (lAxisNo : LongInt; bLtSel1 : Byte; bLtSel2 : Byte) : DWord; stdcall;
    // ������ IO �Է� ���¸� Ȯ�� �Լ�
    function AxmStatusReadServoCmdIOInput (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;
    // ������ ���� ���� �Լ�
    function AxmM3ServoExInterpolate (lAxisNo : LongInt; dwTPOS : DWord; dwVFF : DWord; dwTFF : DWord; dwTLIM : DWord; dwExSig1 : DWord; dwExSig2 : DWord) : DWord; stdcall;
    // ���� �������� ���̾ ���� �Լ�
    function AxmM3ServoSetExpoAccBias (lAxisNo : LongInt; wBias : Word) : DWord; stdcall;
    // ���� �������� �ð� ���� �Լ�
    function AxmM3ServoSetExpoAccTime (lAxisNo : LongInt; wTime : Word) : DWord; stdcall;
    // ������ �̵� �ð��� ���� �Լ�
    function AxmM3ServoSetMoveAvrTime (lAxisNo : LongInt; wTime : Word) : DWord; stdcall;
    // ������ Acc ���� ���� �Լ�
    function AxmM3ServoSetAccFilter (lAxisNo : LongInt; bAccFil : Byte) : DWord; stdcall;
    // ������ ���� �����1 ���� �Լ�
    function AxmM3ServoSetCprmMonitor1 (lAxisNo : LongInt; bMonSel : Byte) : DWord; stdcall;
    // ������ ���� �����2 ���� �Լ�
    function AxmM3ServoSetCprmMonitor2 (lAxisNo : LongInt; bMonSel : Byte) : DWord; stdcall;
    // ������ ���� �����1 Ȯ�� �Լ�
    function AxmM3ServoStatusReadCprmMonitor1 (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;
    // ������ ���� �����2 Ȯ�� �Լ�
    function AxmM3ServoStatusReadCprmMonitor2 (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;
    // ���� �������� Dec ���� �Լ�
    function AxmM3ServoSetAccDec (lAxisNo : LongInt; wAcc1 : Word; wAcc2 : Word; wAccSW : Word; wDec1 : Word; wDec2 : Word; wDecSW : Word) : DWord; stdcall;
    // ���� ���� ���� �Լ�
    function AxmM3ServoSetStop (lAxisNo : LongInt; lMaxDecel : LongInt) : DWord; stdcall;

    //========== ǥ�� I/O ��� ���� Ŀ�ǵ� =========================================================================
    // Network��ǰ �� �����̺� ����� �Ķ���� ���� ���� ��ȯ�ϴ� �Լ�
    function AxlM3GetStationParameter (lBoardNo : LongInt; lModuleNo : LongInt; wNo : Word; bSize : Byte; bModuleType : Byte; pbParam : PByte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� �Ķ���� ���� �����ϴ� �Լ�
    function AxlM3SetStationParameter (lBoardNo : LongInt; lModuleNo : LongInt; wNo : Word; bSize : Byte; bModuleType : Byte; pbParam : PByte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� ID���� ��ȯ�ϴ� �Լ�
    function AxlM3GetStationIdRd (lBoardNo : LongInt; lModuleNo : LongInt; bIdCode : Byte; bOffset : Byte; bSize : Byte; bModuleType : Byte; pbParam : PByte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� ��ȿ Ŀ�ǵ�� ����ϴ� �Լ�
    function AxlM3SetStationNop (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� �¾��� �ǽ��ϴ� �Լ�
    function AxlM3SetStationConfig (lBoardNo : LongInt; lModuleNo : LongInt; bConfigMode : Byte; bModuleType : Byte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� �˶� �� ��� ���� ���� ��ȯ�ϴ� �Լ�
    function AxlM3GetStationAlarm (lBoardNo : LongInt; lModuleNo : LongInt; wAlarmRdMod : Word; wAlarmIndex : Word; bModuleType : Byte; pwAlarmData : PWord) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� �˶� �� ��� ���¸� �����ϴ� �Լ�
    function AxlM3SetStationAlarmClear (lBoardNo : LongInt; lModuleNo : LongInt; wAlarmClrMod : Word; bModuleType : Byte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ������ ��������� �����ϴ� �Լ�
    function AxlM3SetStationSyncSet (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ������ ������ �����ϴ� �Լ�
    function AxlM3SetStationConnect (lBoardNo : LongInt; lModuleNo : LongInt; bVer : Byte; bComMode : Byte; bComTime : Byte; bProfileType : Byte; bModuleType : Byte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ������ ���� ������ �����ϴ� �Լ�
    function AxlM3SetStationDisConnect (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� ���ֹ߼� �Ķ���� ���� ���� ��ȯ�ϴ� �Լ�
    function AxlM3GetStationStoredParameter (lBoardNo : LongInt; lModuleNo : LongInt; wNo : Word; bSize : Byte; bModuleType : Byte; pbParam : PByte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� ���ֹ߼� �Ķ���� ���� �����ϴ� �Լ�
    function AxlM3SetStationStoredParameter (lBoardNo : LongInt; lModuleNo : LongInt; wNo : Word; bSize : Byte; bModuleType : Byte; pbParam : PByte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� �޸� ���� ���� ��ȯ�ϴ� �Լ�
    function AxlM3GetStationMemory (lBoardNo : LongInt; lModuleNo : LongInt; wSize : Word; dwAddress : DWord; bModuleType : Byte; bMode : Byte; bDataType : Byte; pbData : PByte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� �޸� ���� �����ϴ� �Լ�
    function AxlM3SetStationMemory (lBoardNo : LongInt; lModuleNo : LongInt; wSize : Word; dwAddress : DWord; bModuleType : Byte; bMode : Byte; bDataType : Byte; pbData : PByte) : DWord; stdcall;

    //========== ǥ�� I/O ��� Ŀ�ؼ� Ŀ�ǵ� =========================================================================
    // Network��ǰ �� �������� �����̺� ����� �ڵ� �＼�� ��� ���� �����ϴ� �Լ�
    function AxlM3SetStationAccessMode (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; bRWSMode : Byte) : DWord; stdcall;
    // Network��ǰ �� �������� �����̺� ����� �ڵ� �＼�� ��� �������� ��ȯ�ϴ� �Լ�
    function AxlM3GetStationAccessMode (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; bRWSMode : PByte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� ���� �ڵ� ���� ��带 �����ϴ� �Լ�
    function AxlM3SetAutoSyncConnectMode (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; dwAutoSyncConnectMode : DWord) : DWord; stdcall;
    // Network��ǰ �� �����̺� ����� ���� �ڵ� ���� ��� �������� ��ȯ�ϴ� �Լ�
    function AxlM3GetAutoSyncConnectMode (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; dwpAutoSyncConnectMode : PDWord) : DWord; stdcall;
    // Network��ǰ �� �����̺� ��⿡ ���� ���� ����ȭ ������ �����ϴ� �Լ�
    function AxlM3SyncConnectSingle (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ��⿡ ���� ���� ����ȭ ���� ������ �����ϴ� �Լ�
    function AxlM3SyncDisconnectSingle (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte) : DWord; stdcall;
    // Network��ǰ �� �����̺� ������ ���� ���¸� Ȯ���ϴ� �Լ�
    function AxlM3IsOnLine (lBoardNo : LongInt; lModuleNo : LongInt; dwData : PDWord) : DWord; stdcall;

    //========== ǥ�� I/O �������� Ŀ�ǵ� =========================================================================
    // Network��ǰ �� ����ȭ ������ �����̺� I/O ��⿡ ���� ������ �������� ��ȯ�ϴ� �Լ�
    function AxlM3GetStationRWS (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; pdwParam : PDWord; bSize : Byte) : DWord; stdcall;
    // Network��ǰ �� ����ȭ ������ �����̺� I/O ��⿡ ���� �����Ͱ��� �����ϴ� �Լ�
    function AxlM3SetStationRWS (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; pdwParam : PDWord; bSize : Byte) : DWord; stdcall;
    // Network��ǰ �� �񵿱�ȭ ������ �����̺� I/O ��⿡ ���� ������ �������� ��ȯ�ϴ� �Լ�
    function AxlM3GetStationRWA (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; pdwParam : PDWord; bSize : Byte) : DWord; stdcall;
    // Network��ǰ �� �񵿱�ȭ ������ �����̺� I/O ��⿡ ���� �����Ͱ��� �����ϴ� �Լ�
    function AxlM3SetStationRWA (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; pdwParam : PDWord; bSize : Byte) : DWord; stdcall;

    // MLIII adjustment operation�� ���� �Ѵ�.
    // dwReqCode == 0x1005 : parameter initialization : 20sec
    // dwReqCode == 0x1008 : absolute encoder reset   : 5sec
    // dwReqCode == 0x100E : automatic offset adjustment of motor current detection signals  : 5sec
    // dwReqCode == 0x1013 : Multiturn limit setting  : 5sec
    function AxmM3AdjustmentOperation (lAxisNo : LongInt; dwReqCode : DWord) : DWord; stdcall;

    // M3 ���� ���� �˻� ���� ���� ���ܿ� �Լ��̴�.
    function AxmHomeGetM3FWRealRate (lAxisNo : LongInt; upHomeMainStepNumber : PDWord; upHomeSubStepNumber : PDWord; upHomeLastMainStepNumber : PDWord; upHomeLastSubStepNumber : PDWord) : DWord; stdcall;
    // M3 ���� ���� �˻��� ���������� Ż��� �����Ǵ� ��ġ ���� ��ȯ�ϴ� �Լ��̴�.
    function AxmHomeGetM3OffsetAvoideSenArea (lAxisNo : LongInt; dPos : PDouble) : DWord; stdcall;
    // M3 ���� ���� �˻��� ���������� Ż��� �����Ǵ� ��ġ ���� �����ϴ� �Լ��̴�.
    // dPos ���� ���� 0�̸� �ڵ����� Ż��� �����Ǵ� ��ġ ���� �ڵ����� �����ȴ�.
    // dPos ���� ���� ����� ���� �Է��Ѵ�.
    function AxmHomeSetM3OffsetAvoideSenArea (lAxisNo : LongInt; dPos : Double) : DWord; stdcall;

    // M3 ����, ����ġ ���ڴ� ��� ����, �����˻� �Ϸ� �� CMD/ACT POS �ʱ�ȭ ���� ����
    // dwSel: 0, ���� �˻��� CMD/ACTPOS 0���� ������.[�ʱⰪ]
    // dwSel: 1, ���� �˻��� CMD/ACTPOS ���� �������� ����.
    function AxmM3SetAbsEncOrgResetDisable (lAxisNo : LongInt; dwSel : DWord) : DWord; stdcall;

    // M3 ����, ����ġ ���ڴ� ��� ����, �����˻� �Ϸ� �� CMD/ACT POS �ʱ�ȭ ���� ������ ��������
    // upSel: 0, ���� �˻��� CMD/ACTPOS 0���� ������.[�ʱⰪ]
    // upSel: 1, ���� �˻��� CMD/ACTPOS ���� �������� ����.
    function AxmM3GetAbsEncOrgResetDisable (lAxisNo : LongInt; upSel : PDWord) : DWord; stdcall;

    // M3 ����, �����̺� OFFLINE ��ȯ�� �˶� ���� ��� ��� ���� ����
    // dwSel: 0, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ������� ����.[�ʱⰪ]
    // dwSel: 1, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ���

    function AxmM3SetOfflineAlarmEnable (lAxisNo : LongInt; dwSel : DWord) : DWord; stdcall;
    // M3 ����, �����̺� OFFLINE ��ȯ�� �˶� ���� ��� ��� ���� ���� �� ��������
    // upSel: 0, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ������� ����.[�ʱⰪ]
    // upSel: 1, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ���

    function AxmM3GetOfflineAlarmEnable (lAxisNo : LongInt; upSel : PDWord) : DWord; stdcall;

    // M3 ����, �����̺� OFFLINE ��ȯ ���� ���� �� ��������
    // upSel: 0, ML3 �����̺� ONLINE->OFFLINE ��ȯ���� ����
    // upSel: 1, ML3 �����̺� ONLINE->OFFLINE ��ȯ�Ǿ���.
    function AxmM3ReadOnlineToOfflineStatus (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // Network ��ǰ�� Configuration Lock ���¸� �����Ѵ�.
    // wLockMode  : DISABLE(0), ENABLE(1)
    function AxlSetLockMode (lBoardNo : LongInt; wLockMode : Word) : DWord; stdcall;

    // Lock ������ ����
    function AxlSetLockData (lBoardNo : LongInt; dwTotalNodeNum : DWord; dwpNodeNo : PDWord; dwpNodeID : PDWord; dwpLockData : PDWord) : DWord; stdcall;

    function AxmMoveStartPosWithAVC (lAxisNo : LongInt; dPosition : Double; dMaxVelocity : Double; dMaxAccel : Double; dMinJerk : Double; dpMoveVelocity : PDouble; dpMoveAccel : PDouble; dpMoveJerk : PDouble) : DWord; stdcall;
    // ī���� ����� 2-D ������ġ Ʈ���� ����� ���� �ʿ��� Ʈ���� ��ġ ������ �����Ѵ�.
    // lChannelNo : 0,1 channel �� ��� 0, 2,3 channel �� ��� 2 �� ����.
    // nDataCnt :
    //  nDataCnt > 0 : ������ ���, nDataCnt <= 0 : ��ϵ� ������ �ʱ�ȭ.
    // dwOption : Reserved.
    // dpPatternData : (X1, Y1)
    function AxcTriggerSetPatternData (lChannelNo : LongInt; nDataCnt : LongInt; dwOption : DWord; dpPatternData : PDouble) : DWord; stdcall;
    // ī���� ����� 2-D ������ġ Ʈ���� ����� ���� �ʿ��� Ʈ���� ��ġ ������ Ȯ���Ѵ�.
    function AxcTriggerGetPatternData (lChannelNo : LongInt; npDataCnt : PLongInt; dwpOption : PDWord; dpPatternData : PDouble) : DWord; stdcall;

    //���� ���� �����Ͽ� AxmContiEndNode �Լ������� ������������ Node �� Data Queue �� �̸� ä������ �� �ֵ����ϴ� ����� Ȱ��ȭ �Ѵ�.
    //bPushPrevContiQueue : 1 // �ش� ��� Ȱ��ȭ
    //bPushPrevContiQueue : 0 // �ش� ��� ��Ȱ��ȭ
    function AxmContiSetPushPrevContiQueueEnable (lCoordinate : LongInt; bPushPrevContiQueue : Boolean) : DWord; stdcall;
    //�����ص� AxmContiSetPushPrevContiQueueEnable Flag���� ��ȯ�Ѵ�.
    function AxmContiGetPushPrevContiQueueEnable (lCoordinate : LongInt; bPushPrevContiQueue : BOOL*) : DWord; stdcall;

    // ���Ӻ��� ���� �� Data Queue �� Node ������ ����Ǿ����� ���¸� ��ȯ�Ѵ�.
    // AxmContiSetPushPrevContiQueueEnable(long lCoordinate, 1) �� �����Ǿ����� ��츸 ��ȿ
    // bPushPrevContiQueueComplete : 1 // Node Data ���� �Ϸ�
    // bPushPrevContiQueueComplete : 0 // Node Data ���� �Ǿ���������
    function AxmContiGetPushPrevContiQueueComplete (lCoordinate : LongInt; bPushPrevContiQueueComplete : BOOL*) : DWord; stdcall;

    // ���Ӻ��� ���� �� ù ��� ���� �� ������ ��� ���� �� �����ð� ���� ������ ��ǥ���� ������ ���� OutputBit On/Off ����
    // AxmContiBeginNode �տ� ȣ���ؾ� �Ѵ�. �ѹ� �����ϸ� Flag�� �ʱ�ȭ�Ǿ� �ٽ� ȣ���ؾ� ����� �� �ִ�.
    // StartTime/EndTime ������ [Sec]�̸�, 0 ~ 6.5�ʱ��� ���� �����ϴ�.
    // uOnoff : 0 - ���� ��ġ���� Bit On ���� ��ġ���� Bit Off
    //          : 1 - ���� ��ġ���� Bit Off ���� ��ġ���� Bit On
    // lEndMode : 0 - ������ ��� ���� ���� �� ��� OutputBit Off/On
    //   : 1 - ������ ��� ���� ���� �� �Է��� EndTime ���� OutputBit Off/On
    //   : 2 - ���� ���� �� OutputBit On/Off �� �Է��� EndTime ���� OutputBit Off/On
    function AxmContiSetWriteOutputBit (lCoordinate : LongInt; dStartTime : Double; dEndTime : Double; lBitNo : LongInt; uOnoff : LongInt; lEndMode : LongInt) : DWord; stdcall;

    // AxmContiSetWriteOutputBit�� ������ ������ ��ȯ�Ѵ�.
    function AxmContiGetWriteOutputBit (lCoordinate : LongInt; dpStartTime : PDouble; dpEndTime : PDouble; lpBitNo : PLongInt; lpOnoff : PLongInt; lpEndMode : PLongInt) : DWord; stdcall;

    // AxmContiSetWriteOutputBit�� ������ ������ �����Ѵ�.
    function AxmContiResetWriteOutputBit (lCoordinate : LongInt) : DWord; stdcall;

    // AxmMoveTorqueStop �Լ��� ��ũ ���� ���� �� CmdPos ���� ActPos ���� ��ġ��Ű�� ���������� ��� �ð��� �����Ѵ�.
    // dwSettlingTime
    //  1) ����: [msec]
    //  2) �Է� ���� ����: 0 ~ 10000
    //  *����* AxmMoveTorqueSetStopSettlingTime �Լ��� ��� �ð��� �������� ������, dafault ���� 10[msec]�� ����ȴ�.
    function AxmMoveTorqueSetStopSettlingTime (lAxisNo : LongInt; dwSettlingTime : DWord) : DWord; stdcall;
    // AxmMoveTorqueStop �Լ��� ��ũ ���� ���� �� CmdPos ���� ActPos ���� ��ġ��Ű�� ���������� ��� �ð��� ��ȯ�Ѵ�.
    function AxmMoveTorqueGetStopSettlingTime (lAxisNo : LongInt; dwpSettlingTime : PDWord) : DWord; stdcall;

    //////////////////////////////////////////////////////////////////////////
    // Monitor
    // �����͸� ������ ������ �׸��� �߰��մϴ�.
    function AxlMonitorSetItem (lBoardNo : LongInt; lItemIndex : LongInt; dwSignalType : DWord; lSignalNo : LongInt; lSubSignalNo : LongInt) : DWord; stdcall;

    // ������ ������ ������ �׸�鿡 ���� ������ �����ɴϴ�.
    function AxlMonitorGetIndexInfo (lBoardNo : LongInt; lpItemSize : PLongInt; lpItemIndex : PLongInt) : DWord; stdcall;

    // ������ ������ ������ �� �׸��� ���� ������ �����ɴϴ�.
    function AxlMonitorGetItemInfo (lBoardNo : LongInt; lItemIndex : LongInt; dwpSignalType : PDWord; lpSignalNo : PLongInt; lpSubSignalNo : PLongInt) : DWord; stdcall;

    // ��� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    function AxlMonitorResetAllItem (lBoardNo : LongInt) : DWord; stdcall;

    // ���õ� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    function AxlMonitorResetItem (lBoardNo : LongInt; lItemIndex : LongInt) : DWord; stdcall;

    // ������ ������ Ʈ���� ������ �����մϴ�.
    function AxlMonitorSetTriggerOption (lBoardNo : LongInt; dwSignalType : DWord; lSignalNo : LongInt; lSubSignalNo : LongInt; dwOperatorType : DWord; dValue1 : Double; dValue2 : Double) : DWord; stdcall;

    // ������ ������ Ʈ���� ������ �����ɴϴ�.
    //DWORD  __stdcall AxlMonitorGetTriggerOption(DWORD* dwpSignalType, long* lpSignalNo, long* lpSubSignalNo, DWORD* dwpOperatorType, double* dpValue1, double* dpValue2);

    // ������ ������ Ʈ���� ������ �ʱ�ȭ�մϴ�.
    function AxlMonitorResetTriggerOption (lBoardNo : LongInt) : DWord; stdcall;

    // ������ ������ �����մϴ�.
    function AxlMonitorStart (lBoardNo : LongInt; dwStartOption : DWord; dwOverflowOption : DWord) : DWord; stdcall;

    // ������ ������ �����մϴ�.
    function AxlMonitorStop (lBoardNo : LongInt) : DWord; stdcall;

    // ������ �����͸� �����ɴϴ�.
    function AxlMonitorReadData (lBoardNo : LongInt; lpItemSize : PLongInt; lpDataCount : PLongInt; dpReadData : PDouble) : DWord; stdcall;

    // ������ ������ �ֱ⸦ �����ɴϴ�.
    function AxlMonitorReadPeriod (lBoardNo : LongInt; dwpPeriod : PDWord) : DWord; stdcall;
    //////////////////////////////////////////////////////////////////////////


    //////////////////////////////////////////////////////////////////////////
    // MonitorEx
    // �����͸� ������ ������ �׸��� �߰��մϴ�.
    function AxlMonitorExSetItem (lItemIndex : LongInt; dwSignalType : DWord; lSignalNo : LongInt; lSubSignalNo : LongInt) : DWord; stdcall;

    // ������ ������ ������ �׸�鿡 ���� ������ �����ɴϴ�.
    function AxlMonitorExGetIndexInfo (lpItemSize : PLongInt; lpItemIndex : PLongInt) : DWord; stdcall;

    // ������ ������ ������ �� �׸��� ���� ������ �����ɴϴ�.
    function AxlMonitorExGetItemInfo (lItemIndex : LongInt; dwpSignalType : PDWord; lpSignalNo : PLongInt; lpSubSignalNo : PLongInt) : DWord; stdcall;

    // ��� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    function AxlMonitorExResetAllItem () : DWord; stdcall;

    // ���õ� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    function AxlMonitorExResetItem (lItemIndex : LongInt) : DWord; stdcall;

    // ������ ������ Ʈ���� ������ �����մϴ�.
    function AxlMonitorExSetTriggerOption (dwSignalType : DWord; lSignalNo : LongInt; lSubSignalNo : LongInt; dwOperatorType : DWord; dValue1 : Double; dValue2 : Double) : DWord; stdcall;

    // ������ ������ Ʈ���� ������ �����ɴϴ�.
    //DWORD  __stdcall AxlMonitorExGetTriggerOption(DWORD* dwpSignalType, long* lpSignalNo, long* lpSubSignalNo, DWORD* dwpOperatorType, double* dpValue1, double* dpValue2);

    // ������ ������ Ʈ���� ������ �ʱ�ȭ�մϴ�.
    function AxlMonitorExResetTriggerOption () : DWord; stdcall;

    // ������ ������ �����մϴ�.
    function AxlMonitorExStart (dwStartOption : DWord; dwOverflowOption : DWord) : DWord; stdcall;

    // ������ ������ �����մϴ�.
    function AxlMonitorExStop () : DWord; stdcall;

    // ������ �����͸� �����ɴϴ�.
    function AxlMonitorExReadData (lpItemSize : PLongInt; lpDataCount : PLongInt; dpReadData : PDouble) : DWord; stdcall;

    // ������ ������ �ֱ⸦ �����ɴϴ�.
    function AxlMonitorExReadPeriod (dwpPeriod : PDWord) : DWord; stdcall;
    //////////////////////////////////////////////////////////////////////////

    // X2, Y2 �࿡ ���� Offset ��ġ ������ ������ 2�� ���� ���� #01.
    function AxmLineMoveDual01 (lCoordNo : LongInt; dpEndPosition : PDouble; dVelocity : Double; dAccel : Double; dDecel : Double; dOffsetLength : Double; dTotalLength : Double; dpStartOffsetPosition : PDouble; dpEndOffsetPosition : PDouble) : DWord; stdcall;
    // X2, Y2 �࿡ ���� Offset ��ġ ������ ������ 2�� ��ȣ ���� #01.
    function AxmCircleCenterMoveDual01 (lCoordNo : LongInt; lpAxes : PLongInt; dpCenterPosition : PDouble; dpEndPosition : PDouble; dVelocity : Double; dAccel : Double; dDecel : Double; dwCWDir : DWord; dOffsetLength : Double; dTotalLength : Double; dpStartOffsetPosition : PDouble; dpEndOffsetPosition : PDouble) : DWord; stdcall;

    // �ش纸���� connect mode �� ��ȯ�Ѵ�.
    // dpMode : 1 Auto Connect Mode
    // dpMode : 0 Manual Connect Mode
    function AxlGetBoardConnectMode (lBoardNo : LongInt; dwpMode : PDWord) : DWord; stdcall;
    // �ش纸���� connect mode �� �����Ѵ�.
    // dMode : 1 Auto Connect Mode
    // dMode : 0 Manual Connect Mode
    function AxlSetBoardConnectMode (lBoardNo : LongInt; dwMode : DWord) : DWord; stdcall;

    //������ ���� Command Queue �� �ʱ�ȭ �Ѵ�.
    function AxmStatusSetCmdQueueClear (lAxisNo : LongInt) : DWord; stdcall;

    // ������ ���� ��� �������ݰ��� Data �� Ȯ���Ѵ�.
    function AxmStatusGetControlBits (lAxisNo : LongInt; dwpTxData : PDWord; dwpRxData : PDWord) : DWord; stdcall;

    // ��� ���� AXL�� �ִ��� Ȯ��(Shared Memory�� �����ϴ��� Ȯ��)
    function AxlIsUsing () : Boolean; stdcall;
    function AxlRescanExternalDevice () : DWord; stdcall;
    function AxlGetExternalDeviceInfo (lBoardNo : LongInt; devInfo : void*) : DWord; stdcall;


implementation

const

    dll_name    = 'AXL.dll';
    function AxlGetBoardAddress; external dll_name name 'AxlGetBoardAddress';
    function AxlGetBoardID; external dll_name name 'AxlGetBoardID';
    function AxlGetBoardVersion; external dll_name name 'AxlGetBoardVersion';
    function AxlGetModuleID; external dll_name name 'AxlGetModuleID';
    function AxlGetModuleVersion; external dll_name name 'AxlGetModuleVersion';
    function AxlGetModuleNodeInfo; external dll_name name 'AxlGetModuleNodeInfo';
    function AxlSetDataFlash; external dll_name name 'AxlSetDataFlash';
    function AxlSetEStopInterLock; external dll_name name 'AxlSetEStopInterLock';
    function AxlGetEStopInterLock; external dll_name name 'AxlGetEStopInterLock';
    function AxlReadEStopInterLock; external dll_name name 'AxlReadEStopInterLock';
    function AxlGetDataFlash; external dll_name name 'AxlGetDataFlash';
    function AxaInfoGetModuleNo; external dll_name name 'AxaInfoGetModuleNo';
    function AxdInfoGetModuleNo; external dll_name name 'AxdInfoGetModuleNo';
    function AxmSetCommand; external dll_name name 'AxmSetCommand';
    function AxmSetCommandData08; external dll_name name 'AxmSetCommandData08';
    function AxmGetCommandData08; external dll_name name 'AxmGetCommandData08';
    function AxmSetCommandData16; external dll_name name 'AxmSetCommandData16';
    function AxmGetCommandData16; external dll_name name 'AxmGetCommandData16';
    function AxmSetCommandData24; external dll_name name 'AxmSetCommandData24';
    function AxmGetCommandData24; external dll_name name 'AxmGetCommandData24';
    function AxmSetCommandData32; external dll_name name 'AxmSetCommandData32';
    function AxmGetCommandData32; external dll_name name 'AxmGetCommandData32';
    function AxmSetCommandQi; external dll_name name 'AxmSetCommandQi';
    function AxmSetCommandData08Qi; external dll_name name 'AxmSetCommandData08Qi';
    function AxmGetCommandData08Qi; external dll_name name 'AxmGetCommandData08Qi';
    function AxmSetCommandData16Qi; external dll_name name 'AxmSetCommandData16Qi';
    function AxmGetCommandData16Qi; external dll_name name 'AxmGetCommandData16Qi';
    function AxmSetCommandData24Qi; external dll_name name 'AxmSetCommandData24Qi';
    function AxmGetCommandData24Qi; external dll_name name 'AxmGetCommandData24Qi';
    function AxmSetCommandData32Qi; external dll_name name 'AxmSetCommandData32Qi';
    function AxmGetCommandData32Qi; external dll_name name 'AxmGetCommandData32Qi';
    function AxmGetPortData; external dll_name name 'AxmGetPortData';
    function AxmSetPortData; external dll_name name 'AxmSetPortData';
    function AxmGetPortDataQi; external dll_name name 'AxmGetPortDataQi';
    function AxmSetPortDataQi; external dll_name name 'AxmSetPortDataQi';
    function AxmSetScriptCaptionIp; external dll_name name 'AxmSetScriptCaptionIp';
    function AxmGetScriptCaptionIp; external dll_name name 'AxmGetScriptCaptionIp';
    function AxmSetScriptCaptionQi; external dll_name name 'AxmSetScriptCaptionQi';
    function AxmGetScriptCaptionQi; external dll_name name 'AxmGetScriptCaptionQi';
    function AxmSetScriptCaptionQueueClear; external dll_name name 'AxmSetScriptCaptionQueueClear';
    function AxmGetScriptCaptionQueueCount; external dll_name name 'AxmGetScriptCaptionQueueCount';
    function AxmGetScriptCaptionQueueDataCount; external dll_name name 'AxmGetScriptCaptionQueueDataCount';
    function AxmGetOptimizeDriveData; external dll_name name 'AxmGetOptimizeDriveData';
    function AxmBoardWriteByte; external dll_name name 'AxmBoardWriteByte';
    function AxmBoardReadByte; external dll_name name 'AxmBoardReadByte';
    function AxmBoardWriteWord; external dll_name name 'AxmBoardWriteWord';
    function AxmBoardReadWord; external dll_name name 'AxmBoardReadWord';
    function AxmBoardWriteDWord; external dll_name name 'AxmBoardWriteDWord';
    function AxmBoardReadDWord; external dll_name name 'AxmBoardReadDWord';
    function AxmModuleWriteByte; external dll_name name 'AxmModuleWriteByte';
    function AxmModuleReadByte; external dll_name name 'AxmModuleReadByte';
    function AxmModuleWriteWord; external dll_name name 'AxmModuleWriteWord';
    function AxmModuleReadWord; external dll_name name 'AxmModuleReadWord';
    function AxmModuleWriteDWord; external dll_name name 'AxmModuleWriteDWord';
    function AxmModuleReadDWord; external dll_name name 'AxmModuleReadDWord';
    function AxmStatusSetActComparatorPos; external dll_name name 'AxmStatusSetActComparatorPos';
    function AxmStatusGetActComparatorPos; external dll_name name 'AxmStatusGetActComparatorPos';
    function AxmStatusSetCmdComparatorPos; external dll_name name 'AxmStatusSetCmdComparatorPos';
    function AxmStatusGetCmdComparatorPos; external dll_name name 'AxmStatusGetCmdComparatorPos';
    function AxmStatusSetFlashAbsOffset; external dll_name name 'AxmStatusSetFlashAbsOffset';
    function AxmStatusGetFlashAbsOffset; external dll_name name 'AxmStatusGetFlashAbsOffset';
    function AxmStatusSetAbsOffsetWriteEnable; external dll_name name 'AxmStatusSetAbsOffsetWriteEnable';
    function AxmStatusGetAbsOffsetWriteEnable; external dll_name name 'AxmStatusGetAbsOffsetWriteEnable';
    function AxmLineMoveVel; external dll_name name 'AxmLineMoveVel';
    function AxmSensorSetSignal; external dll_name name 'AxmSensorSetSignal';
    function AxmSensorGetSignal; external dll_name name 'AxmSensorGetSignal';
    function AxmSensorReadSignal; external dll_name name 'AxmSensorReadSignal';
    function AxmSensorMovePos; external dll_name name 'AxmSensorMovePos';
    function AxmSensorStartMovePos; external dll_name name 'AxmSensorStartMovePos';
    function AxmHomeGetStepTrace; external dll_name name 'AxmHomeGetStepTrace';
    function AxmHomeSetConfig; external dll_name name 'AxmHomeSetConfig';
    function AxmHomeGetConfig; external dll_name name 'AxmHomeGetConfig';
    function AxmHomeSetMoveSearch; external dll_name name 'AxmHomeSetMoveSearch';
    function AxmHomeSetMoveReturn; external dll_name name 'AxmHomeSetMoveReturn';
    function AxmHomeSetMoveLeave; external dll_name name 'AxmHomeSetMoveLeave';
    function AxmHomeSetMultiMoveSearch; external dll_name name 'AxmHomeSetMultiMoveSearch';
    function AxmContiSetProfileMode; external dll_name name 'AxmContiSetProfileMode';
    function AxmContiGetProfileMode; external dll_name name 'AxmContiGetProfileMode';
    function AxdiInterruptFlagReadBit; external dll_name name 'AxdiInterruptFlagReadBit';
    function AxdiInterruptFlagReadByte; external dll_name name 'AxdiInterruptFlagReadByte';
    function AxdiInterruptFlagReadWord; external dll_name name 'AxdiInterruptFlagReadWord';
    function AxdiInterruptFlagReadDword; external dll_name name 'AxdiInterruptFlagReadDword';
    function AxdiInterruptFlagRead; external dll_name name 'AxdiInterruptFlagRead';
    function AxmLogSetAxis; external dll_name name 'AxmLogSetAxis';
    function AxmLogGetAxis; external dll_name name 'AxmLogGetAxis';
    function AxaiLogSetChannel; external dll_name name 'AxaiLogSetChannel';
    function AxaiLogGetChannel; external dll_name name 'AxaiLogGetChannel';
    function AxaoLogSetChannel; external dll_name name 'AxaoLogSetChannel';
    function AxaoLogGetChannel; external dll_name name 'AxaoLogGetChannel';
    function AxdLogSetModule; external dll_name name 'AxdLogSetModule';
    function AxdLogGetModule; external dll_name name 'AxdLogGetModule';
    function AxlGetFirmwareVersion; external dll_name name 'AxlGetFirmwareVersion';
    function AxlSetFirmwareCopy; external dll_name name 'AxlSetFirmwareCopy';
    function AxlSetFirmwareUpdate; external dll_name name 'AxlSetFirmwareUpdate';
    function AxlCheckStatus; external dll_name name 'AxlCheckStatus';
    function AxlRtexUniversalCmd; external dll_name name 'AxlRtexUniversalCmd';
    function AxmRtexSlaveCmd; external dll_name name 'AxmRtexSlaveCmd';
    function AxmRtexGetSlaveCmdResult; external dll_name name 'AxmRtexGetSlaveCmdResult';
    function AxmRtexGetSlaveCmdResultEx; external dll_name name 'AxmRtexGetSlaveCmdResultEx';
    function AxmRtexGetAxisStatus; external dll_name name 'AxmRtexGetAxisStatus';
    function AxmRtexGetAxisReturnData; external dll_name name 'AxmRtexGetAxisReturnData';
    function AxmRtexGetAxisSlaveStatus; external dll_name name 'AxmRtexGetAxisSlaveStatus';
    function AxmSetAxisCmd; external dll_name name 'AxmSetAxisCmd';
    function AxmGetAxisCmdResult; external dll_name name 'AxmGetAxisCmdResult';
    function AxdSetAndGetSlaveCmdResult; external dll_name name 'AxdSetAndGetSlaveCmdResult';
    function AxaSetAndGetSlaveCmdResult; external dll_name name 'AxaSetAndGetSlaveCmdResult';
    function AxcSetAndGetSlaveCmdResult; external dll_name name 'AxcSetAndGetSlaveCmdResult';
    function AxlGetDpRamData; external dll_name name 'AxlGetDpRamData';
    function AxlBoardReadDpramWord; external dll_name name 'AxlBoardReadDpramWord';
    function AxlBoardWriteDpramWord; external dll_name name 'AxlBoardWriteDpramWord';
    function AxlSetSendBoardEachCommand; external dll_name name 'AxlSetSendBoardEachCommand';
    function AxlSetSendBoardCommand; external dll_name name 'AxlSetSendBoardCommand';
    function AxlGetResponseBoardCommand; external dll_name name 'AxlGetResponseBoardCommand';
    function AxmInfoGetFirmwareVersion; external dll_name name 'AxmInfoGetFirmwareVersion';
    function AxaInfoGetFirmwareVersion; external dll_name name 'AxaInfoGetFirmwareVersion';
    function AxdInfoGetFirmwareVersion; external dll_name name 'AxdInfoGetFirmwareVersion';
    function AxcInfoGetFirmwareVersion; external dll_name name 'AxcInfoGetFirmwareVersion';
    function AxmSetTorqFeedForward; external dll_name name 'AxmSetTorqFeedForward';
    function AxmGetTorqFeedForward; external dll_name name 'AxmGetTorqFeedForward';
    function AxmSetVelocityFeedForward; external dll_name name 'AxmSetVelocityFeedForward';
    function AxmGetVelocityFeedForward; external dll_name name 'AxmGetVelocityFeedForward';
    function AxmSignalSetEncoderType; external dll_name name 'AxmSignalSetEncoderType';
    function AxmSignalGetEncoderType; external dll_name name 'AxmSignalGetEncoderType';
    function AxmMotSetUserMotion; external dll_name name 'AxmMotSetUserMotion';
    function AxmMotSetUserMotionUsage; external dll_name name 'AxmMotSetUserMotionUsage';
    function AxmMotSetUserPosMotion; external dll_name name 'AxmMotSetUserPosMotion';
    function AxmMotSetUserPosMotionUsage; external dll_name name 'AxmMotSetUserPosMotionUsage';
    function AxcKeWriteRamDataAddr; external dll_name name 'AxcKeWriteRamDataAddr';
    function AxcKeReadRamDataAddr; external dll_name name 'AxcKeReadRamDataAddr';
    function AxcKeResetRamDataAll; external dll_name name 'AxcKeResetRamDataAll';
    function AxcTriggerSetTimeout; external dll_name name 'AxcTriggerSetTimeout';
    function AxcTriggerGetTimeout; external dll_name name 'AxcTriggerGetTimeout';
    function AxcStatusGetWaitState; external dll_name name 'AxcStatusGetWaitState';
    function AxcStatusSetWaitState; external dll_name name 'AxcStatusSetWaitState';
    function AxcKeSetCommandData32; external dll_name name 'AxcKeSetCommandData32';
    function AxcKeSetCommandData16; external dll_name name 'AxcKeSetCommandData16';
    function AxcKeGetCommandData32; external dll_name name 'AxcKeGetCommandData32';
    function AxcKeGetCommandData16; external dll_name name 'AxcKeGetCommandData16';
    function AxmSeqSetAxisMap; external dll_name name 'AxmSeqSetAxisMap';
    function AxmSeqGetAxisMap; external dll_name name 'AxmSeqGetAxisMap';
    function AxmSeqSetMasterAxisNo; external dll_name name 'AxmSeqSetMasterAxisNo';
    function AxmSeqBeginNode; external dll_name name 'AxmSeqBeginNode';
    function AxmSeqEndNode; external dll_name name 'AxmSeqEndNode';
    function AxmSeqStart; external dll_name name 'AxmSeqStart';
    function AxmSeqAddNode; external dll_name name 'AxmSeqAddNode';
    function AxmSeqGetNodeNum; external dll_name name 'AxmSeqGetNodeNum';
    function AxmSeqGetTotalNodeNum; external dll_name name 'AxmSeqGetTotalNodeNum';
    function AxmSeqIsMotion; external dll_name name 'AxmSeqIsMotion';
    function AxmSeqWriteClear; external dll_name name 'AxmSeqWriteClear';
    function AxmSeqStop; external dll_name name 'AxmSeqStop';
    function AxmStatusSetMon; external dll_name name 'AxmStatusSetMon';
    function AxmStatusGetMon; external dll_name name 'AxmStatusGetMon';
    function AxmStatusReadMon; external dll_name name 'AxmStatusReadMon';
    function AxmStatusReadMonEx; external dll_name name 'AxmStatusReadMonEx';
    function AxlSetIoPort; external dll_name name 'AxlSetIoPort';
    function AxlGetIoPort; external dll_name name 'AxlGetIoPort';
    function AxlM3SetFWUpdateInit; external dll_name name 'AxlM3SetFWUpdateInit';
    function AxlM3GetFWUpdateInit; external dll_name name 'AxlM3GetFWUpdateInit';
    function AxlM3SetFWUpdateCopy; external dll_name name 'AxlM3SetFWUpdateCopy';
    function AxlM3GetFWUpdateCopy; external dll_name name 'AxlM3GetFWUpdateCopy';
    function AxlM3SetFWUpdate; external dll_name name 'AxlM3SetFWUpdate';
    function AxlM3GetFWUpdate; external dll_name name 'AxlM3GetFWUpdate';
    function AxlM3SetCFGData; external dll_name name 'AxlM3SetCFGData';
    function AxlM3GetCFGData; external dll_name name 'AxlM3GetCFGData';
    function AxlM3SetMCParaUpdateInit; external dll_name name 'AxlM3SetMCParaUpdateInit';
    function AxlM3GetMCParaUpdateInit; external dll_name name 'AxlM3GetMCParaUpdateInit';
    function AxlM3SetMCParaUpdateCopy; external dll_name name 'AxlM3SetMCParaUpdateCopy';
    function AxlM3GetMCParaUpdateCopy; external dll_name name 'AxlM3GetMCParaUpdateCopy';
    function AxlBoardReadDWord; external dll_name name 'AxlBoardReadDWord';
    function AxlBoardWriteDWord; external dll_name name 'AxlBoardWriteDWord';
    function AxlBoardReadDWordEx; external dll_name name 'AxlBoardReadDWordEx';
    function AxlBoardWriteDWordEx; external dll_name name 'AxlBoardWriteDWordEx';
    function AxmM3ServoSetCtrlStopMode; external dll_name name 'AxmM3ServoSetCtrlStopMode';
    function AxmM3ServoSetCtrlLtSel; external dll_name name 'AxmM3ServoSetCtrlLtSel';
    function AxmStatusReadServoCmdIOInput; external dll_name name 'AxmStatusReadServoCmdIOInput';
    function AxmM3ServoExInterpolate; external dll_name name 'AxmM3ServoExInterpolate';
    function AxmM3ServoSetExpoAccBias; external dll_name name 'AxmM3ServoSetExpoAccBias';
    function AxmM3ServoSetExpoAccTime; external dll_name name 'AxmM3ServoSetExpoAccTime';
    function AxmM3ServoSetMoveAvrTime; external dll_name name 'AxmM3ServoSetMoveAvrTime';
    function AxmM3ServoSetAccFilter; external dll_name name 'AxmM3ServoSetAccFilter';
    function AxmM3ServoSetCprmMonitor1; external dll_name name 'AxmM3ServoSetCprmMonitor1';
    function AxmM3ServoSetCprmMonitor2; external dll_name name 'AxmM3ServoSetCprmMonitor2';
    function AxmM3ServoStatusReadCprmMonitor1; external dll_name name 'AxmM3ServoStatusReadCprmMonitor1';
    function AxmM3ServoStatusReadCprmMonitor2; external dll_name name 'AxmM3ServoStatusReadCprmMonitor2';
    function AxmM3ServoSetAccDec; external dll_name name 'AxmM3ServoSetAccDec';
    function AxmM3ServoSetStop; external dll_name name 'AxmM3ServoSetStop';
    function AxlM3GetStationParameter; external dll_name name 'AxlM3GetStationParameter';
    function AxlM3SetStationParameter; external dll_name name 'AxlM3SetStationParameter';
    function AxlM3GetStationIdRd; external dll_name name 'AxlM3GetStationIdRd';
    function AxlM3SetStationNop; external dll_name name 'AxlM3SetStationNop';
    function AxlM3SetStationConfig; external dll_name name 'AxlM3SetStationConfig';
    function AxlM3GetStationAlarm; external dll_name name 'AxlM3GetStationAlarm';
    function AxlM3SetStationAlarmClear; external dll_name name 'AxlM3SetStationAlarmClear';
    function AxlM3SetStationSyncSet; external dll_name name 'AxlM3SetStationSyncSet';
    function AxlM3SetStationConnect; external dll_name name 'AxlM3SetStationConnect';
    function AxlM3SetStationDisConnect; external dll_name name 'AxlM3SetStationDisConnect';
    function AxlM3GetStationStoredParameter; external dll_name name 'AxlM3GetStationStoredParameter';
    function AxlM3SetStationStoredParameter; external dll_name name 'AxlM3SetStationStoredParameter';
    function AxlM3GetStationMemory; external dll_name name 'AxlM3GetStationMemory';
    function AxlM3SetStationMemory; external dll_name name 'AxlM3SetStationMemory';
    function AxlM3SetStationAccessMode; external dll_name name 'AxlM3SetStationAccessMode';
    function AxlM3GetStationAccessMode; external dll_name name 'AxlM3GetStationAccessMode';
    function AxlM3SetAutoSyncConnectMode; external dll_name name 'AxlM3SetAutoSyncConnectMode';
    function AxlM3GetAutoSyncConnectMode; external dll_name name 'AxlM3GetAutoSyncConnectMode';
    function AxlM3SyncConnectSingle; external dll_name name 'AxlM3SyncConnectSingle';
    function AxlM3SyncDisconnectSingle; external dll_name name 'AxlM3SyncDisconnectSingle';
    function AxlM3IsOnLine; external dll_name name 'AxlM3IsOnLine';
    function AxlM3GetStationRWS; external dll_name name 'AxlM3GetStationRWS';
    function AxlM3SetStationRWS; external dll_name name 'AxlM3SetStationRWS';
    function AxlM3GetStationRWA; external dll_name name 'AxlM3GetStationRWA';
    function AxlM3SetStationRWA; external dll_name name 'AxlM3SetStationRWA';
    function AxmM3AdjustmentOperation; external dll_name name 'AxmM3AdjustmentOperation';
    function AxmHomeGetM3FWRealRate; external dll_name name 'AxmHomeGetM3FWRealRate';
    function AxmHomeGetM3OffsetAvoideSenArea; external dll_name name 'AxmHomeGetM3OffsetAvoideSenArea';
    function AxmHomeSetM3OffsetAvoideSenArea; external dll_name name 'AxmHomeSetM3OffsetAvoideSenArea';
    function AxmM3SetAbsEncOrgResetDisable; external dll_name name 'AxmM3SetAbsEncOrgResetDisable';
    function AxmM3GetAbsEncOrgResetDisable; external dll_name name 'AxmM3GetAbsEncOrgResetDisable';
    function AxmM3SetOfflineAlarmEnable; external dll_name name 'AxmM3SetOfflineAlarmEnable';
    function AxmM3GetOfflineAlarmEnable; external dll_name name 'AxmM3GetOfflineAlarmEnable';
    function AxmM3ReadOnlineToOfflineStatus; external dll_name name 'AxmM3ReadOnlineToOfflineStatus';
    function AxlSetLockMode; external dll_name name 'AxlSetLockMode';
    function AxlSetLockData; external dll_name name 'AxlSetLockData';
    function AxmMoveStartPosWithAVC; external dll_name name 'AxmMoveStartPosWithAVC';
    function AxcTriggerSetPatternData; external dll_name name 'AxcTriggerSetPatternData';
    function AxcTriggerGetPatternData; external dll_name name 'AxcTriggerGetPatternData';
    function AxmContiSetPushPrevContiQueueEnable; external dll_name name 'AxmContiSetPushPrevContiQueueEnable';
    function AxmContiGetPushPrevContiQueueEnable; external dll_name name 'AxmContiGetPushPrevContiQueueEnable';
    function AxmContiGetPushPrevContiQueueComplete; external dll_name name 'AxmContiGetPushPrevContiQueueComplete';
    function AxmContiSetWriteOutputBit; external dll_name name 'AxmContiSetWriteOutputBit';
    function AxmContiGetWriteOutputBit; external dll_name name 'AxmContiGetWriteOutputBit';
    function AxmContiResetWriteOutputBit; external dll_name name 'AxmContiResetWriteOutputBit';
    function AxmMoveTorqueSetStopSettlingTime; external dll_name name 'AxmMoveTorqueSetStopSettlingTime';
    function AxmMoveTorqueGetStopSettlingTime; external dll_name name 'AxmMoveTorqueGetStopSettlingTime';
    function AxlMonitorSetItem; external dll_name name 'AxlMonitorSetItem';
    function AxlMonitorGetIndexInfo; external dll_name name 'AxlMonitorGetIndexInfo';
    function AxlMonitorGetItemInfo; external dll_name name 'AxlMonitorGetItemInfo';
    function AxlMonitorResetAllItem; external dll_name name 'AxlMonitorResetAllItem';
    function AxlMonitorResetItem; external dll_name name 'AxlMonitorResetItem';
    function AxlMonitorSetTriggerOption; external dll_name name 'AxlMonitorSetTriggerOption';
    function AxlMonitorResetTriggerOption; external dll_name name 'AxlMonitorResetTriggerOption';
    function AxlMonitorStart; external dll_name name 'AxlMonitorStart';
    function AxlMonitorStop; external dll_name name 'AxlMonitorStop';
    function AxlMonitorReadData; external dll_name name 'AxlMonitorReadData';
    function AxlMonitorReadPeriod; external dll_name name 'AxlMonitorReadPeriod';
    function AxlMonitorExSetItem; external dll_name name 'AxlMonitorExSetItem';
    function AxlMonitorExGetIndexInfo; external dll_name name 'AxlMonitorExGetIndexInfo';
    function AxlMonitorExGetItemInfo; external dll_name name 'AxlMonitorExGetItemInfo';
    function AxlMonitorExResetAllItem; external dll_name name 'AxlMonitorExResetAllItem';
    function AxlMonitorExResetItem; external dll_name name 'AxlMonitorExResetItem';
    function AxlMonitorExSetTriggerOption; external dll_name name 'AxlMonitorExSetTriggerOption';
    function AxlMonitorExResetTriggerOption; external dll_name name 'AxlMonitorExResetTriggerOption';
    function AxlMonitorExStart; external dll_name name 'AxlMonitorExStart';
    function AxlMonitorExStop; external dll_name name 'AxlMonitorExStop';
    function AxlMonitorExReadData; external dll_name name 'AxlMonitorExReadData';
    function AxlMonitorExReadPeriod; external dll_name name 'AxlMonitorExReadPeriod';
    function AxmLineMoveDual01; external dll_name name 'AxmLineMoveDual01';
    function AxmCircleCenterMoveDual01; external dll_name name 'AxmCircleCenterMoveDual01';
    function AxlGetBoardConnectMode; external dll_name name 'AxlGetBoardConnectMode';
    function AxlSetBoardConnectMode; external dll_name name 'AxlSetBoardConnectMode';
    function AxmStatusSetCmdQueueClear; external dll_name name 'AxmStatusSetCmdQueueClear';
    function AxmStatusGetControlBits; external dll_name name 'AxmStatusGetControlBits';
    function AxlIsUsing; external dll_name name 'AxlIsUsing';
    function AxlRescanExternalDevice; external dll_name name 'AxlRescanExternalDevice';
    function AxlGetExternalDeviceInfo; external dll_name name 'AxlGetExternalDeviceInfo';
