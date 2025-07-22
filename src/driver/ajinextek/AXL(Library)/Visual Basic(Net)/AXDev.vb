Option Strict Off
Option Explicit On
Module AXDev



    ' Board Number�� �̿��Ͽ� Board Address ã��
    Public Declare Function AxlGetBoardAddress Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef upBoardAddress As Integer) As Integer
    ' Board Number�� �̿��Ͽ� Board ID ã��
    Public Declare Function AxlGetBoardID Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef upBoardID As Integer) As Integer
    ' Board Number�� �̿��Ͽ� Board Version ã��
    Public Declare Function AxlGetBoardVersion Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef upBoardVersion As Integer) As Integer
    ' Board Number�� Module Position�� �̿��Ͽ� Module ID ã��
    Public Declare Function AxlGetModuleID Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByRef upModuleID As Integer) As Integer
    ' Board Number�� Module Position�� �̿��Ͽ� Module Version ã��
    Public Declare Function AxlGetModuleVersion Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByRef upModuleVersion As Integer) As Integer
    ' Board Number�� Module Position�� �̿��Ͽ� Network Node ���� Ȯ��
    Public Declare Function AxlGetModuleNodeInfo Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByRef upNetNo As Integer, ByRef upNodeAddr As Integer) As Integer

    ' Board�� ����� ���� Data Flash Write (PCI-R1604[RTEX master board]����)
    ' lPageAddr(0 ~ 199)
    ' lByteNum(1 ~ 120)
    ' ����) Flash�� ����Ÿ�� ������ ���� ���� �ð�(�ִ� 17mSec)�� �ҿ�Ǳ⶧���� ���� ����� ���� �ð��� �ʿ���.
    Public Declare Function AxlSetDataFlash Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lPageAddr As Integer, ByVal lBytesNum As Integer, ByRef bpSetData As Byte) As Integer

    ' Board�� ����� ESTOP �ܺ� �Է� ��ȣ�� �̿��� InterLock ��� ��� ���� �� ������ ���� ����� ���� (PCI-Rxx00[MLIII master board]����)
    ' 1. ��� ����
    '   ����: ��� ��� ������ �ܺο��� ESTOP ��ȣ �ΰ��� ���忡 ����� ��� ���� ��忡 ���ؼ� ESTOP ���� ��� ����
    '    0: ��� ������� ����(�⺻ ������)
    '    1: ��� ���
    ' 2. ������ ���� ��
    '      �Է� ���� ��� ���� ���� 1 ~ 40, ���� ��� Cyclic time
    ' Board �� dwInterLock, dwDigFilterVal�� �̿��Ͽ� EstopInterLock ��� ����
    Public Declare Function AxlSetEStopInterLock Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwInterLock As Integer, ByVal dwDigFilterVal As Integer) As Integer
    ' Board�� ������ dwInterLock, dwDigFilterVal ������ ��������
    Public Declare Function AxlGetEStopInterLock Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef dwInterLock As Integer, ByRef dwDigFilterVal As Integer) As Integer
    ' Board�� �Էµ� EstopInterLock ��ȣ�� �д´�.
    Public Declare Function AxlReadEStopInterLock Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef dwInterLock As Integer) As Integer

    ' Board�� ����� ���� Data Flash Read(PCI-R1604[RTEX master board]����)
    ' lPageAddr(0 ~ 199)
    ' lByteNum(1 ~ 120)
    Public Declare Function AxlGetDataFlash Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lPageAddr As Integer, ByVal lBytesNum As Integer, ByRef bpGetData As Byte) As Integer

    ' Board Number�� Module Position�� �̿��Ͽ� AIO Module Number ã��
    Public Declare Function AxaInfoGetModuleNo Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByRef lpModuleNo As Integer) As Integer
    ' Board Number�� Module Position�� �̿��Ͽ� DIO Module Number ã��
    Public Declare Function AxdInfoGetModuleNo Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByRef lpModuleNo As Integer) As Integer

    ' ���� �࿡ IPCOMMAND Setting
    Public Declare Function AxmSetCommand Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte) As Integer
    ' ���� �࿡ 8bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData08 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByVal uData As Integer) As Integer
    ' ���� �࿡ 8bit IPCOMMAND ��������
    Public Declare Function AxmGetCommandData08 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByRef upData As Integer) As Integer
    ' ���� �࿡ 16bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData16 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByVal uData As Integer) As Integer
    ' ���� �࿡ 16bit IPCOMMAND ��������
    Public Declare Function AxmGetCommandData16 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByRef upData As Integer) As Integer
    ' ���� �࿡ 24bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData24 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByVal uData As Integer) As Integer
    ' ���� �࿡ 24bit IPCOMMAND ��������
    Public Declare Function AxmGetCommandData24 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByRef upData As Integer) As Integer
    ' ���� �࿡ 32bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData32 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByVal uData As Integer) As Integer
    ' ���� �࿡ 32bit IPCOMMAND ��������
    Public Declare Function AxmGetCommandData32 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByRef upData As Integer) As Integer

    ' ���� �࿡ QICOMMAND Setting
    Public Declare Function AxmSetCommandQi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte) As Integer
    ' ���� �࿡ 8bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData08Qi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByVal uData As Integer) As Integer
    ' ���� �࿡ 8bit QICOMMAND ��������
    Public Declare Function AxmGetCommandData08Qi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByRef upData As Integer) As Integer
    ' ���� �࿡ 16bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData16Qi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByVal uData As Integer) As Integer
    ' ���� �࿡ 16bit QICOMMAND ��������
    Public Declare Function AxmGetCommandData16Qi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByRef upData As Integer) As Integer
    ' ���� �࿡ 24bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData24Qi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByVal uData As Integer) As Integer
    ' ���� �࿡ 24bit QICOMMAND ��������
    Public Declare Function AxmGetCommandData24Qi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByRef upData As Integer) As Integer
    ' ���� �࿡ 32bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData32Qi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByVal uData As Integer) As Integer
    ' ���� �࿡ 32bit QICOMMAND ��������
    Public Declare Function AxmGetCommandData32Qi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sCommand As Byte, ByRef upData As Integer) As Integer

    ' ���� �࿡ Port Data �������� - IP
    Public Declare Function AxmGetPortData Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal wOffset As Integer, ByRef upData As Integer) As Integer
    ' ���� �࿡ Port Data Setting - IP
    Public Declare Function AxmSetPortData Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal wOffset As Integer, ByVal dwData As Integer) As Integer
    ' ���� �࿡ Port Data �������� - QI
    Public Declare Function AxmGetPortDataQi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal byOffset As Integer, ByRef wData As Integer) As Integer
    ' ���� �࿡ Port Data Setting - QI
    Public Declare Function AxmSetPortDataQi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal byOffset As Integer, ByVal wData As Integer) As Integer

    ' ���� �࿡ ��ũ��Ʈ�� �����Ѵ�. - IP
    ' sc    : ��ũ��Ʈ ��ȣ (1 - 4)
    ' event : �߻��� �̺�Ʈ SCRCON �� �����Ѵ�.
    '         �̺�Ʈ ���� �హ������, �̺�Ʈ �߻��� ��, �̺�Ʈ ���� 1,2 �Ӽ� �����Ѵ�.
    ' cmd   : � ������ �ٲܰ����� ���� SCRCMD�� �����Ѵ�.
    ' data  : � Data�� �ٲܰ����� ����
    Public Declare Function AxmSetScriptCaptionIp Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sc As Integer, ByVal event As Integer, ByVal data As Integer) As Integer
    ' ���� �࿡ ��ũ��Ʈ�� ��ȯ�Ѵ�. - IP
    Public Declare Function AxmGetScriptCaptionIp Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sc As Integer, ByRef event As Integer, ByRef data As Integer) As Integer

    ' ���� �࿡ ��ũ��Ʈ�� �����Ѵ�. - QI
    ' sc    : ��ũ��Ʈ ��ȣ (1 - 4)
    ' event : �߻��� �̺�Ʈ SCRCON �� �����Ѵ�.
    '         �̺�Ʈ ���� �హ������, �̺�Ʈ �߻��� ��, �̺�Ʈ ���� 1,2 �Ӽ� �����Ѵ�.
    ' cmd   : � ������ �ٲܰ����� ���� SCRCMD�� �����Ѵ�.
    ' data  : � Data�� �ٲܰ����� ����
    Public Declare Function AxmSetScriptCaptionQi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sc As Integer, ByVal event As Integer, ByVal cmd As Integer, ByVal data As Integer) As Integer
    ' ���� �࿡ ��ũ��Ʈ�� ��ȯ�Ѵ�. - QI
    Public Declare Function AxmGetScriptCaptionQi Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal sc As Integer, ByRef event As Integer, ByRef cmd As Integer, ByRef data As Integer) As Integer

    ' ���� �࿡ ��ũ��Ʈ ���� Queue Index�� Clear ��Ų��.
    ' uSelect IP.
    ' uSelect(0): ��ũ��Ʈ Queue Index �� Clear�Ѵ�.
    '        (1): ĸ�� Queue�� Index Clear�Ѵ�.
    ' uSelect QI.
    ' uSelect(0): ��ũ��Ʈ Queue 1 Index �� Clear�Ѵ�.
    '        (1): ��ũ��Ʈ Queue 2 Index �� Clear�Ѵ�.
    Public Declare Function AxmSetScriptCaptionQueueClear Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal uSelect As Integer) As Integer

    ' ���� �࿡ ��ũ��Ʈ ���� Queue�� Index ��ȯ�Ѵ�.
    ' uSelect IP
    ' uSelect(0): ��ũ��Ʈ Queue Index�� �о�´�.
    '        (1): ĸ�� Queue Index�� �о�´�.
    ' uSelect QI.
    ' uSelect(0): ��ũ��Ʈ Queue 1 Index�� �о�´�.
    '        (1): ��ũ��Ʈ Queue 2 Index�� �о�´�.
    Public Declare Function AxmGetScriptCaptionQueueCount Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef updata As Integer, ByVal uSelect As Integer) As Integer

    ' ���� �࿡ ��ũ��Ʈ ���� Queue�� Data���� ��ȯ�Ѵ�.
    ' uSelect IP
    ' uSelect(0): ��ũ��Ʈ Queue Data �� �о�´�.
    '        (1): ĸ�� Queue Data�� �о�´�.
    ' uSelect QI.
    ' uSelect(0): ��ũ��Ʈ Queue 1 Data �о�´�.
    '        (1): ��ũ��Ʈ Queue 2 Data �о�´�.
    Public Declare Function AxmGetScriptCaptionQueueDataCount Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef updata As Integer, ByVal uSelect As Integer) As Integer

    ' ���� ����Ÿ�� �о�´�.
    Public Declare Function AxmGetOptimizeDriveData Lib "AXL.dll" () As Integer


    ' ���峻�� �������͸� Byte������ ���� �� Ȯ���Ѵ�.
    Public Declare Function AxmBoardWriteByte Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wOffset As Integer, ByVal byData As Byte) As Integer
    Public Declare Function AxmBoardReadByte Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wOffset As Integer, ByRef byData As Byte) As Integer

    ' ���峻�� �������͸� Word������ ���� �� Ȯ���Ѵ�.
    Public Declare Function AxmBoardWriteWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wOffset As Integer, ByVal wData As Integer) As Integer
    Public Declare Function AxmBoardReadWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wOffset As Integer, ByRef wData As Integer) As Integer

    ' ���峻�� �������͸� DWord������ ���� �� Ȯ���Ѵ�.
    Public Declare Function AxmBoardWriteDWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wOffset As Integer, ByVal dwData As Integer) As Integer
    Public Declare Function AxmBoardReadDWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wOffset As Integer, ByRef dwData As Integer) As Integer

    ' ���峻�� ��⿡ �������͸� Byte���� �� Ȯ���Ѵ�.
    Public Declare Function AxmModuleWriteByte Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByVal wOffset As Integer, ByVal byData As Byte) As Integer
    Public Declare Function AxmModuleReadByte Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByVal wOffset As Integer, ByRef byData As Byte) As Integer

    ' ���峻�� ��⿡ �������͸� Word���� �� Ȯ���Ѵ�.
    Public Declare Function AxmModuleWriteWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByVal wOffset As Integer, ByVal wData As Integer) As Integer
    Public Declare Function AxmModuleReadWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByVal wOffset As Integer, ByRef wData As Integer) As Integer

    ' ���峻�� ��⿡ �������͸� DWord���� �� Ȯ���Ѵ�.
    Public Declare Function AxmModuleWriteDWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByVal wOffset As Integer, ByVal dwData As Integer) As Integer
    Public Declare Function AxmModuleReadDWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByVal wOffset As Integer, ByRef dwData As Integer) As Integer

    ' �ܺ� ��ġ �񱳱⿡ ���� �����Ѵ�.(Pos = Unit)
    Public Declare Function AxmStatusSetActComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dPos As Double) As Integer
    ' �ܺ� ��ġ �񱳱⿡ ���� ��ȯ�Ѵ�.(Positon = Unit)
    Public Declare Function AxmStatusGetActComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dpPos As Double) As Integer

    ' ���� ��ġ �񱳱⿡ ���� �����Ѵ�.(Pos = Unit)
    Public Declare Function AxmStatusSetCmdComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dPos As Double) As Integer
    ' ���� ��ġ �񱳱⿡ ���� ��ȯ�Ѵ�.(Pos = Unit)
    Public Declare Function AxmStatusGetCmdComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dpPos As Double) As Integer
    ' ABS Position �� Flash �� �����Ѵ�.
    Public Declare Function AxmStatusSetFlashAbsOffset Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dPosition As Integer) As Integer
    ' Flash �� ���� �� ABS Position �� ��ȯ�Ѵ�.
    ' dReadType  : Value in Flash Memory (0), Real used Value in memory(1)
    Public Declare Function AxmStatusGetFlashAbsOffset Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dPosition As Integer, ByVal dReadType As Integer) As Integer
    ' ����ڰ� Flash �� ABS Position ������ �� �ִ� �ɼ��� �����Ѵ�.
    Public Declare Function AxmStatusSetAbsOffsetWriteEnable Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal bStatus As Byte) As Integer
    ' ABS Position ���� �ɼ��� ���¸� ��ȯ�Ѵ�.
    Public Declare Function AxmStatusGetAbsOffsetWriteEnable Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef bpStatus As bool*) As Integer

    '========== �߰� �Լ� =========================================================================================================
    ' ���� ���� �� �ӵ��� ������ ���Ѵ�� �����Ѵ�.
    ' �ӵ� ������� �Ÿ��� �־��־�� �Ѵ�.
    Public Declare Function AxmLineMoveVel Lib "AXL.dll" (ByVal lCoord As Integer, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Integer

    '========= ���� ��ġ ���� �Լ�( �ʵ�: IP������ , QI���� ��ɾ���)==============================================================
    ' ���� ���� Sensor ��ȣ�� ��� ���� �� ��ȣ �Է� ������ �����Ѵ�.
    ' ��� ���� LOW(0), HIGH(1), UNUSED(2), USED(3)
    Public Declare Function AxmSensorSetSignal Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal uLevel As Integer) As Integer
    ' ���� ���� Sensor ��ȣ�� ��� ���� �� ��ȣ �Է� ������ ��ȯ�Ѵ�.
    Public Declare Function AxmSensorGetSignal Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upLevel As Integer) As Integer
    ' ���� ���� Sensor ��ȣ�� �Է� ���¸� ��ȯ�Ѵ�
    Public Declare Function AxmSensorReadSignal Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upStatus As Integer) As Integer

    ' ���� ���� ������ �ӵ��� �������� ���� ��ġ ����̹��� �����Ѵ�.
    ' Sensor ��ȣ�� Active level�Է� ���� ��� ��ǥ�� ������ �Ÿ���ŭ ������ �����Ѵ�.
    ' �޽��� ��µǴ� �������� �Լ��� �����.
    ' lMethod :  0 - �Ϲ� ����, 1 - ���� ��ȣ ���� ���� ���� ����. ��ȣ ���� �� �Ϲ� ����
    '            2 - ���� ����
    Public Declare Function AxmSensorMovePos Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dPos As Double, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal lMethod As Integer) As Integer

    ' ���� ���� ������ �ӵ��� �������� ���� ��ġ ����̹��� �����Ѵ�.
    ' Sensor ��ȣ�� Active level�Է� ���� ��� ��ǥ�� ������ �Ÿ���ŭ ������ �����Ѵ�.
    ' �޽� ����� ����Ǵ� �������� �Լ��� �����.
    Public Declare Function AxmSensorStartMovePos Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dPos As Double, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal lMethod As Integer) As Integer

    ' �����˻� ���ེ�� ��ȭ�� ����� ��ȯ�Ѵ�.
    ' *lpStepCount      : ��ϵ� Step�� ����
    ' *upMainStepNumber : ��ϵ� MainStepNumber ������ �迭����Ʈ
    ' *upStepNumber     : ��ϵ� StepNumber ������ �迭����Ʈ
    ' *upStepBranch     : ��ϵ� Step�� Branch ������ �迭����Ʈ
    ' ����: �迭������ 50���� ����
    Public Declare Function AxmHomeGetStepTrace Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef lpStepCount As Integer, ByRef upMainStepNumber As Integer, ByRef upStepNumber As Integer, ByRef upStepBranch As Integer) As Integer

    '=======�߰� Ȩ ��ġ (PI-N804/404���� �ش��.)=================================================================================
    ' ����ڰ� ������ ���� Ȩ���� �Ķ��Ÿ�� �����Ѵ�.(QIĨ ���� �������� �̿�).
    ' uZphasCount : Ȩ �Ϸ��Ŀ� Z�� ī��Ʈ(0 - 15)
    ' lHomeMode   : Ȩ ���� ���( 0 - 12)
    ' lClearSet   : ��ġ Ŭ���� , �ܿ��޽� Ŭ���� ��� ���� (0 - 3)
    '               0: ��ġŬ���� ������, �ܿ��޽� Ŭ���� ��� ����
    '                 1: ��ġŬ���� �����, �ܿ��޽� Ŭ���� ��� ����
    '               2: ��ġŬ���� ������, �ܿ��޽� Ŭ���� �����
    '               3: ��ġŬ���� �����, �ܿ��޽� Ŭ���� �����.
    ' dOrgVel : Ȩ���� Org  Speed ����
    ' dLastVel: Ȩ���� Last Speed ����
    Public Declare Function AxmHomeSetConfig Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal uZphasCount As Integer, ByVal lHomeMode As Integer, ByVal lClearSet As Integer, ByVal dOrgVel As Double, ByVal dLastVel As Double, ByVal dLeavePos As Double) As Integer
    ' ����ڰ� ������ ���� Ȩ���� �Ķ��Ÿ�� ��ȯ�Ѵ�.
    Public Declare Function AxmHomeGetConfig Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upZphasCount As Integer, ByRef lpHomeMode As Integer, ByRef lpClearSet As Integer, ByRef dpOrgVel As Double, ByRef dpLastVel As Double, ByRef dpLeavePos As Double) As Integer

    ' ����ڰ� ������ ���� Ȩ ��ġ�� �����Ѵ�.
    ' lHomeMode ���� ���� : 0 - 5 ���� (Move Return�Ŀ� Search��  �����Ѵ�.)
    ' lHomeMode -1�� �״�� ���� HomeConfig���� ����Ѵ�� �״�� ������.
    ' ��������      : Vel���� ����̸� CW, �����̸� CCW.
    Public Declare Function AxmHomeSetMoveSearch Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Integer

    ' ����ڰ� ������ ���� Ȩ ������ �����Ѵ�.
    ' lHomeMode ���� ���� : 0 - 12 ����
    ' lHomeMode -1�� �״�� ���� HomeConfig���� ����Ѵ�� �״�� ������.
    ' ��������      : Vel���� ����̸� CW, �����̸� CCW.
    Public Declare Function AxmHomeSetMoveReturn Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Integer

    ' ����ڰ� ������ ���� Ȩ ��Ż�� �����Ѵ�.
    ' ��������      : Vel���� ����̸� CW, �����̸� CCW.
    Public Declare Function AxmHomeSetMoveLeave Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Integer

    ' ����ڰ� ������ ������ Ȩ ��ġ�� �����Ѵ�.
    ' lHomeMode ���� ���� : 0 - 5 ���� (Move Return�Ŀ� Search��  �����Ѵ�.)
    ' lHomeMode -1�� �״�� ���� HomeConfig���� ����Ѵ�� �״�� ������.
    ' ��������      : Vel���� ����̸� CW, �����̸� CCW.
    Public Declare Function AxmHomeSetMultiMoveSearch Lib "AXL.dll" (ByVal lArraySize As Integer, ByRef lpAxesNo As Integer, ByRef dpVel As Double, ByRef dpAccel As Double, ByRef dpDecel As Double) As Integer

    '������ ��ǥ���� ���� �ӵ� �������� ��带 �����Ѵ�.
    ' (������ : �ݵ�� ����� �ϰ� ��밡��)
    ' ProfileMode : '0' - ��Ī Trapezode
    '               '1' - ���Ī Trapezode
    '               '2' - ��Ī Quasi-S Curve
    '               '3' - ��Ī S Curve
    '               '4' - ���Ī S Curve
    Public Declare Function AxmContiSetProfileMode Lib "AXL.dll" (ByVal lCoord As Integer, ByVal uProfileMode As Integer) As Integer
    ' ������ ��ǥ���� ���� �ӵ� �������� ��带 ��ȯ�Ѵ�.
    Public Declare Function AxmContiGetProfileMode Lib "AXL.dll" (ByVal lCoord As Integer, ByRef upProfileMode As Integer) As Integer

    '========== DIO ���ͷ�Ʈ �÷��� ������Ʈ �б�
    ' ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� bit ������ ���ͷ�Ʈ �߻� ���� ���� ����
    Public Declare Function AxdiInterruptFlagReadBit Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lOffset As Integer, ByRef upValue As Integer) As Integer
    ' ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� byte ������ ���ͷ�Ʈ �߻� ���� ���� ����
    Public Declare Function AxdiInterruptFlagReadByte Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lOffset As Integer, ByRef upValue As Integer) As Integer
    ' ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� word ������ ���ͷ�Ʈ �߻� ���� ���� ����
    Public Declare Function AxdiInterruptFlagReadWord Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lOffset As Integer, ByRef upValue As Integer) As Integer
    ' ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� double word ������ ���ͷ�Ʈ �߻� ���� ���� ����
    Public Declare Function AxdiInterruptFlagReadDword Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lOffset As Integer, ByRef upValue As Integer) As Integer
    ' ��ü �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� bit ������ ���ͷ�Ʈ �߻� ���� ���� ����
    Public Declare Function AxdiInterruptFlagRead Lib "AXL.dll" (ByVal lOffset As Integer, ByRef upValue As Integer) As Integer

    '========= �α� ���� �Լ� ==========================================================================================
    ' ���� �ڵ����� ������.
    ' ���� ���� �Լ� ���� ����� EzSpy���� ����͸� �� �� �ֵ��� ���� �Ǵ� �����ϴ� �Լ��̴�.
    ' uUse : ��� ���� => DISABLE(0), ENABLE(1)
    Public Declare Function AxmLogSetAxis Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal uUse As Integer) As Integer

    ' EzSpy������ ���� �� �Լ� ���� ��� ����͸� ���θ� Ȯ���ϴ� �Լ��̴�.
    Public Declare Function AxmLogGetAxis Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upUse As Integer) As Integer

    '=========== �α� ��� ���� �Լ�
    '������ �Է� ä���� EzSpy�� �α� ��� ���θ� �����Ѵ�.
    Public Declare Function AxaiLogSetChannel Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal uUse As Integer) As Integer
    '������ �Է� ä���� EzSpy�� �α� ��� ���θ� Ȯ���Ѵ�.
    Public Declare Function AxaiLogGetChannel Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef upUse As Integer) As Integer

    '==������ ��� ä���� EzSpy �α� ���
    '������ ��� ä���� EzSpy�� �α� ��� ���θ� �����Ѵ�.
    Public Declare Function AxaoLogSetChannel Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal uUse As Integer) As Integer
    '������ ��� ä���� EzSpy�� �α� ��� ���θ� Ȯ���Ѵ�.
    Public Declare Function AxaoLogGetChannel Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef upUse As Integer) As Integer

    '==Log
    ' ������ ����� EzSpy�� �α� ��� ���� ����
    Public Declare Function AxdLogSetModule Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal uUse As Integer) As Integer
    ' ������ ����� EzSpy�� �α� ��� ���� Ȯ��
    Public Declare Function AxdLogGetModule Lib "AXL.dll" (ByVal lModuleNo As Integer, ByRef upUse As Integer) As Integer

    ' ������ ���尡 RTEX ����� �� �� ������ firmware ������ Ȯ���Ѵ�.
    Public Declare Function AxlGetFirmwareVersion Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef szVersion As String) As Integer
    ' ������ ����� Firmware�� ���� �Ѵ�.
    Public Declare Function AxlSetFirmwareCopy Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef wData As Integer, ByRef wCmdData As Integer) As Integer
    ' ������ ����� Firmware Update�� �����Ѵ�.
    Public Declare Function AxlSetFirmwareUpdate Lib "AXL.dll" (ByVal lBoardNo As Integer) As Integer
    ' ������ ������ ���� RTEX �ʱ�ȭ ���¸� Ȯ�� �Ѵ�.
    Public Declare Function AxlCheckStatus Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef dwStatus As Integer) As Integer
    ' ������ �࿡ RTEX Master board�� ���� ����� ���� �մϴ�.
    Public Declare Function AxlRtexUniversalCmd Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wCmd As Integer, ByVal wOffset As Integer, ByRef wData As Integer) As Integer
    ' ������ ���� RTEX ��� ����� �����Ѵ�.
    Public Declare Function AxmRtexSlaveCmd Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwCmdCode As Integer, ByVal dwTypeCode As Integer, ByVal dwIndexCode As Integer, ByVal dwCmdConfigure As Integer, ByVal dwValue As Integer) As Integer
    ' ������ �࿡ ������ RTEX ��� ����� ������� Ȯ���Ѵ�.
    Public Declare Function AxmRtexGetSlaveCmdResult Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwIndex As Integer, ByRef dwValue As Integer) As Integer
    ' ������ �࿡ ������ RTEX ��� ����� ������� Ȯ���Ѵ�. PCIE-Rxx04-RTEX ����
    Public Declare Function AxmRtexGetSlaveCmdResultEx Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwpCommand As Integer, ByRef dwpType As Integer, ByRef dwpIndex As Integer, ByRef dwpValue As Integer) As Integer
    ' ������ �࿡ RTEX ���� ������ Ȯ���Ѵ�.
    Public Declare Function AxmRtexGetAxisStatus Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwStatus As Integer) As Integer
    ' ������ �࿡ RTEX ��� ���� ������ Ȯ���Ѵ�.(Actual position, Velocity, Torque)
    Public Declare Function AxmRtexGetAxisReturnData Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwReturn1 As Integer, ByRef dwReturn2 As Integer, ByRef dwReturn3 As Integer) As Integer
    ' ������ �࿡ RTEX Slave ���� ���� ���� ������ Ȯ���Ѵ�.(mechanical, Inposition and etc)
    Public Declare Function AxmRtexGetAxisSlaveStatus Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwStatus As Integer) As Integer

    ' ������ �࿡ MLII Slave �࿡ ���� ��Ʈ�� ��ɾ �����Ѵ�.
    Public Declare Function AxmSetAxisCmd Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef tagCommand As Integer) As Integer
    ' ������ �࿡ MLII Slave �࿡ ���� ��Ʈ�� ����� ����� Ȯ���Ѵ�.
    Public Declare Function AxmGetAxisCmdResult Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef tagCommand As Integer) As Integer

    ' ������ SIIIH Slave ��⿡ ��Ʈ�� ����� ����� �����ϰ� ��ȯ �Ѵ�.
    Public Declare Function AxdSetAndGetSlaveCmdResult Lib "AXL.dll" (ByVal lModuleNo As Integer, ByRef tagSetCommand As Integer, ByRef tagGetCommand As Integer) As Integer
    Public Declare Function AxaSetAndGetSlaveCmdResult Lib "AXL.dll" (ByVal lModuleNo As Integer, ByRef tagSetCommand As Integer, ByRef tagGetCommand As Integer) As Integer
    Public Declare Function AxcSetAndGetSlaveCmdResult Lib "AXL.dll" (ByVal lModuleNo As Integer, ByRef tagSetCommand As Integer, ByRef tagGetCommand As Integer) As Integer

    ' DPRAM �����͸� Ȯ���Ѵ�.
    Public Declare Function AxlGetDpRamData Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wAddress As Integer, ByRef dwpRdData As Integer) As Integer
    ' DPRAM �����͸� Word������ Ȯ���Ѵ�.
    Public Declare Function AxlBoardReadDpramWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wOffset As Integer, ByRef dwpRdData As Integer) As Integer
    ' DPRAM �����͸� Word������ �����Ѵ�.
    Public Declare Function AxlBoardWriteDpramWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wOffset As Integer, ByVal dwWrData As Integer) As Integer

    ' �� ������ �� SLAVE���� ����� �����Ѵ�.
    Public Declare Function AxlSetSendBoardEachCommand Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwCommand As Integer, ByRef dwpSendData As Integer, ByVal dwLength As Integer) As Integer
    ' �� ����� ����� �����Ѵ�.
    Public Declare Function AxlSetSendBoardCommand Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwCommand As Integer, ByRef dwpSendData As Integer, ByVal dwLength As Integer) As Integer
    ' �� ������ ������ Ȯ���Ѵ�.
    Public Declare Function AxlGetResponseBoardCommand Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef dwpReadData As Integer) As Integer

    ' Network Type Master ���忡�� Slave ���� Firmware Version�� �о� ���� �Լ�.
    ' ucaFirmwareVersion unsigned char ���� Array�� �����ϰ� ũ�Ⱑ 4�̻��� �ǵ��� ���� �ؾ� �Ѵ�.
    Public Declare Function AxmInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef ucaFirmwareVersion As Integer) As Integer
    Public Declare Function AxaInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lModuleNo As Integer, ByRef ucaFirmwareVersion As Integer) As Integer
    Public Declare Function AxdInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lModuleNo As Integer, ByRef ucaFirmwareVersion As Integer) As Integer
    Public Declare Function AxcInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lModuleNo As Integer, ByRef ucaFirmwareVersion As Integer) As Integer

    '======== PCI-R1604-MLII ���� �Լ�===========================================================================
    ' INTERPOLATE and LATCH Command�� Option Field�� Torq Feed Forward�� ���� ���� �ϵ��� �մϴ�.
    ' �⺻���� MAX�� �����Ǿ� �ֽ��ϴ�.
    ' �������� 0 ~ 4000H���� ���� �� �� �ֽ��ϴ�.
    ' �������� 4000H�̻����� �����ϸ� ������ �� �̻����� �����ǳ� ������ 4000H���� ���� �˴ϴ�.
    Public Declare Function AxmSetTorqFeedForward Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwTorqFeedForward As Integer) As Integer

    ' INTERPOLATE and LATCH Command�� Option Field�� Torq Feed Forward�� ���� �о���� �Լ� �Դϴ�.
    ' �⺻���� MAX�� �����Ǿ� �ֽ��ϴ�.
    Public Declare Function AxmGetTorqFeedForward Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwpTorqFeedForward As Integer) As Integer

    ' INTERPOLATE and LATCH Command�� VFF Field�� Velocity Feed Forward�� ���� ���� �ϵ��� �մϴ�.
    ' �⺻���� '0'�� �����Ǿ� �ֽ��ϴ�.
    ' �������� 0 ~ FFFFH���� ���� �� �� �ֽ��ϴ�.
    Public Declare Function AxmSetVelocityFeedForward Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwVelocityFeedForward As Integer) As Integer

    ' INTERPOLATE and LATCH Command�� VFF Field�� Velocity Feed Forward�� ���� �о���� �Լ� �Դϴ�.
    Public Declare Function AxmGetVelocityFeedForward Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwpVelocityFeedForward As Integer) As Integer

    ' Encoder type�� �����Ѵ�.
    ' �⺻���� 0(TYPE_INCREMENTAL)�� �����Ǿ� �ֽ��ϴ�.
    ' �������� 0 ~ 1���� ���� �� �� �ֽ��ϴ�.
    ' ������ : 0(TYPE_INCREMENTAL), 1(TYPE_ABSOLUTE).
    Public Declare Function AxmSignalSetEncoderType Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwEncoderType As Integer) As Integer

    ' Encoder type�� Ȯ���Ѵ�.
    Public Declare Function AxmSignalGetEncoderType Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwpEncoderType As Integer) As Integer
    '========================================================================================================

    ' Slave Firmware Update�� ���� �߰�
    'DWORD   __stdcall AxmSetSendAxisCommand(long lAxisNo, WORD wCommand, WORD* wpSendData, WORD wLength);

    '======== PCI-R1604-RTEX, RTEX-PM ���� �Լ�==============================================================
    ' ���� �Է� 2,3�� �Է½� JOG ���� �ӵ��� �����Ѵ�.
    ' ������ ���õ� ��� ����(Ex, PulseOutMethod, MoveUnitPerPulse ��)���� �Ϸ�� ���� �ѹ��� �����Ͽ��� �Ѵ�.
    Public Declare Function AxmMotSetUserMotion Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Integer

    ' ���� �Է� 2,3�� �Է½� JOG ���� ���� ��� ���θ� �����Ѵ�.
    ' ������ :  0(DISABLE), 1(ENABLE)
    Public Declare Function AxmMotSetUserMotionUsage Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwUsage As Integer) As Integer

    ' MPGP �Է��� ����Ͽ� Load/UnLoad ��ġ�� �ڵ����� �̵��ϴ� ��� ����.
    Public Declare Function AxmMotSetUserPosMotion Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal dLoadPos As Double, ByVal dUnLoadPos As Double, ByVal dwFilter As Integer, ByVal dwDelay As Integer) As Integer

    ' MPGP �Է��� ����Ͽ� Load/UnLoad ��ġ�� �ڵ����� �̵��ϴ� ��� ����.
    ' ������ :  0(DISABLE), 1(Position ��� A ���), 2(Position ��� B ���)
    Public Declare Function AxmMotSetUserPosMotionUsage Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwUsage As Integer) As Integer
    '========================================================================================================

    '======== SIO-CN2CH/HPC4, ���� ��ġ Ʈ���� ��� ��� ���� �Լ�================================================
    ' �޸� ������ ���� �Լ�
    Public Declare Function AxcKeWriteRamDataAddr Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwAddr As Integer, ByVal dwData As Integer) As Integer
    ' �޸� ������ �б� �Լ�
    Public Declare Function AxcKeReadRamDataAddr Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwAddr As Integer, ByRef dwpData As Integer) As Integer
    ' �޸� �ʱ�ȭ �Լ�
    Public Declare Function AxcKeResetRamDataAll Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal dwData As Integer) As Integer
    ' Ʈ���� Ÿ�� �ƿ� ���� �Լ�
    Public Declare Function AxcTriggerSetTimeout Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwTimeout As Integer) As Integer
    ' Ʈ���� Ÿ�� �ƿ� Ȯ�� �Լ�
    Public Declare Function AxcTriggerGetTimeout Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpTimeout As Integer) As Integer
    ' Ʈ���� ��� ���� Ȯ�� �Լ�
    Public Declare Function AxcStatusGetWaitState Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpState As Integer) As Integer
    ' Ʈ���� ��� ���� ���� �Լ�
    Public Declare Function AxcStatusSetWaitState Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwState As Integer) As Integer

    ' ���� ä�ο� ��ɾ� ����.
    Public Declare Function AxcKeSetCommandData32 Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwCommand As Integer, ByVal dwData As Integer) As Integer
    ' ���� ä�ο� ��ɾ� ����.
    Public Declare Function AxcKeSetCommandData16 Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwCommand As Integer, ByVal wData As Integer) As Integer
    ' ���� ä���� �������� Ȯ��.
    Public Declare Function AxcKeGetCommandData32 Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwCommand As Integer, ByRef dwpData As Integer) As Integer
    ' ���� ä���� �������� Ȯ��.
    Public Declare Function AxcKeGetCommandData16 Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwCommand As Integer, ByRef wpData As Integer) As Integer
    '========================================================================================================

    '======== PCI-N804/N404 ����, Sequence Motion ===================================================================
    ' Sequence Motion�� �� ������ ���� �մϴ�. (�ּ� 1��)
    ' lSeqMapNo : �� ��ȣ ������ ��� Sequence Motion Index Point
    ' lSeqMapSize : �� ��ȣ ����
    ' long* LSeqAxesNo : �� ��ȣ �迭
    Public Declare Function AxmSeqSetAxisMap Lib "AXL.dll" (ByVal lSeqMapNo As Integer, ByVal lSeqMapSize As Integer, ByRef lSeqAxesNo As Integer) As Integer
    Public Declare Function AxmSeqGetAxisMap Lib "AXL.dll" (ByVal lSeqMapNo As Integer, ByRef lSeqMapSize As Integer, ByRef lSeqAxesNo As Integer) As Integer

    ' Sequence Motion�� ����(Master) ���� ���� �մϴ�.
    ' �ݵ�� AxmSeqSetAxisMap(...) �� ������ �� ������ �����Ͽ��� �մϴ�.
    Public Declare Function AxmSeqSetMasterAxisNo Lib "AXL.dll" (ByVal lSeqMapNo As Integer, ByVal lMasterAxisNo As Integer) As Integer

    ' Sequence Motion�� Node ���� ������ ���̺귯���� �˸��ϴ�.
    Public Declare Function AxmSeqBeginNode Lib "AXL.dll" (ByVal lSeqMapNo As Integer) As Integer

    ' Sequence Motion�� Node ���� ���Ḧ ���̺귯���� �˸��ϴ�.
    Public Declare Function AxmSeqEndNode Lib "AXL.dll" (ByVal lSeqMapNo As Integer) As Integer

    ' Sequence Motion�� ������ ���� �մϴ�.
    Public Declare Function AxmSeqStart Lib "AXL.dll" (ByVal lSeqMapNo As Integer, ByVal dwStartOption As Integer) As Integer

    ' Sequence Motion�� �� Profile Node ������ ���̺귯���� �Է� �մϴ�.
    ' ���� 1�� Sequence Motion�� ����ϴ���, *dPosition�� 1���� Array�� �����Ͽ� �ֽñ� �ٶ��ϴ�.
    Public Declare Function AxmSeqAddNode Lib "AXL.dll" (ByVal lSeqMapNo As Integer, ByRef dPosition As Double, ByVal dVelocity As Double, ByVal dAcceleration As Double, ByVal dDeceleration As Double, ByVal dNextVelocity As Double) As Integer

    ' Sequence Motion�� ���� �� ���� ���� ���� Node Index�� �˷� �ݴϴ�.
    Public Declare Function AxmSeqGetNodeNum Lib "AXL.dll" (ByVal lSeqMapNo As Integer, ByRef lCurNodeNo As Integer) As Integer

    ' Sequence Motion�� �� Node Count�� Ȯ�� �մϴ�.
    Public Declare Function AxmSeqGetTotalNodeNum Lib "AXL.dll" (ByVal lSeqMapNo As Integer, ByRef lTotalNodeCnt As Integer) As Integer

    ' Sequence Motion�� ���� ���� ������ Ȯ�� �մϴ�.
    ' dwInMotion : 0(���� ����), 1(���� ��)
    Public Declare Function AxmSeqIsMotion Lib "AXL.dll" (ByVal lSeqMapNo As Integer, ByRef dwInMotion As Integer) As Integer

    ' Sequence Motion�� Memory�� Clear �մϴ�.
    ' AxmSeqSetAxisMap(...), AxmSeqSetMasterAxisNo(...) ���� ������ ���� �����˴ϴ�.
    Public Declare Function AxmSeqWriteClear Lib "AXL.dll" (ByVal lSeqMapNo As Integer) As Integer

    ' Sequence Motion�� ������ ���� �մϴ�.
    ' dwStopMode : 0(EMERGENCY_STOP), 1(SLOWDOWN_STOP)
    Public Declare Function AxmSeqStop Lib "AXL.dll" (ByVal lSeqMapNo As Integer, ByVal dwStopMode As Integer) As Integer
    '========================================================================================================


    '======== PCIe-Rxx04-SIIIH ���� �Լ�==========================================================================
    ' (SIIIH, MR_J4_xxB, Para : 0 ~ 8) ==
    '     [0] : Command Position
    '     [1] : Actual Position
    '     [2] : Actual Velocity
    '     [3] : Mechanical Signal
    '     [4] : Regeneration load factor(%)
    '     [5] : Effective load factor(%)
    '     [6] : Peak load factor(%)
    '     [7] : Current Feedback
    '     [8] : Command Velocity
    Public Declare Function AxmStatusSetMon Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwParaNo1 As Integer, ByVal dwParaNo2 As Integer, ByVal dwParaNo3 As Integer, ByVal dwParaNo4 As Integer, ByVal dwUse As Integer) As Integer
    Public Declare Function AxmStatusGetMon Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwpParaNo1 As Integer, ByRef dwpParaNo2 As Integer, ByRef dwpParaNo3 As Integer, ByRef dwpParaNo4 As Integer, ByRef dwpUse As Integer) As Integer
    Public Declare Function AxmStatusReadMon Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwpParaNo1 As Integer, ByRef dwpParaNo2 As Integer, ByRef dwpParaNo3 As Integer, ByRef dwpParaNo4 As Integer, ByRef dwDataVaild As Integer) As Integer
    Public Declare Function AxmStatusReadMonEx Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef lpDataCnt As Integer, ByRef dwpReadData As Integer) As Integer
    '=============================================================================================================

    '======== PCI-R32IOEV-RTEX ���� �Լ�===========================================================================
    ' I/O ��Ʈ�� �Ҵ�� HPI register �� �а� �������� API �Լ�.
    ' I/O Registers for HOST interface.
    ' I/O 00h Host status register (HSR)
    ' I/O 04h Host-to-DSP control register (HDCR)
    ' I/O 08h DSP page register (DSPP)
    ' I/O 0Ch Reserved
    Public Declare Function AxlSetIoPort Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwAddr As Integer, ByVal dwData As Integer) As Integer
    Public Declare Function AxlGetIoPort Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwAddr As Integer, ByRef dwpData As Integer) As Integer

    '======== PCI-R3200-MLIII ���� �Լ�===========================================================================
    '/*
    ' M-III Master ���� �߿��� ������Ʈ �⺻ ���� ���� �Լ�
    'DWORD   __stdcall AxlM3SetFWUpdateInit(long lBoardNo, DWORD dwTotalPacketSize);
    ' M-III Master ���� �߿��� ������Ʈ �⺻ ���� ���� ��� Ȯ�� �Լ�
    'DWORD   __stdcall AxlM3GetFWUpdateInit(long lBoardNo, DWORD *dwTotalPacketSize);
    ' M-III Master ���� �߿��� ������Ʈ �ڷ� ���� �Լ�
    'DWORD   __stdcall AxlM3SetFWUpdateCopy(long lBoardNo, DWORD *lFWUpdataData, DWORD dwLength);
    ' M-III Master ���� �߿��� ������Ʈ �ڷ� ���� ��� Ȯ�� �Լ�
    'DWORD   __stdcall AxlM3GetFWUpdateCopy(long lBoardNo, BYTE bCrcData, DWORD *lFWUpdataResult);
    ' M-III Master ���� �߿��� ������Ʈ ����
    'DWORD   __stdcall AxlM3SetFWUpdate(long lBoardNo, DWORD dwSectorNo);
    ' M-III Master ���� �߿��� ������Ʈ ���� ��� Ȯ��
    'DWORD   __stdcall AxlM3GetFWUpdate(long lBoardNo, DWORD *dwSectorNo, DWORD *dwIsDone);
    '*/
    ' M-III Master ���� �߿��� ������Ʈ �⺻ ���� ���� �Լ�
    Public Declare Function AxlM3SetFWUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwTotalPacketSize As Integer, ByVal dwProcTotalStepNo As Integer) As Integer
    ' M-III Master ���� �߿��� ������Ʈ �⺻ ���� ���� ��� Ȯ�� �Լ�
    Public Declare Function AxlM3GetFWUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef dwTotalPacketSize As Integer, ByRef dwProcTotalStepNo As Integer) As Integer

    ' M-III Master ���� �߿��� ������Ʈ �ڷ� ���� �Լ�
    Public Declare Function AxlM3SetFWUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef pdwPacketData As Integer, ByVal dwPacketSize As Integer) As Integer
    ' M-III Master ���� �߿��� ������Ʈ �ڷ� ���� ��� Ȯ�� �Լ�
    Public Declare Function AxlM3GetFWUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef dwPacketSize As Integer) As Integer

    ' M-III Master ���� �߿��� ������Ʈ ����
    Public Declare Function AxlM3SetFWUpdate Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwFlashBurnStepNo As Integer) As Integer
    ' M-III Master ���� �߿��� ������Ʈ ���� ��� Ȯ��
    Public Declare Function AxlM3GetFWUpdate Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef dwFlashBurnStepNo As Integer, ByRef dwIsFlashBurnDone As Integer) As Integer

    ' M-III Master ���� EEPROM ������ ���� �Լ�
    Public Declare Function AxlM3SetCFGData Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef pCmdData As Integer, ByVal CmdDataSize As Integer) As Integer
    ' M-III Master ���� EEPROM ������ �������� �Լ�
    Public Declare Function AxlM3GetCFGData Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef pCmdData As Integer, ByVal CmdDataSize As Integer) As Integer

    ' M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� �Լ�
    Public Declare Function AxlM3SetMCParaUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wCh0Slaves As Integer, ByVal wCh1Slaves As Integer, ByVal dwCh0CycTime As Integer, ByVal dwCh1CycTime As Integer, ByVal dwChInfoMaxRetry As Integer) As Integer
    ' M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� ��� Ȯ�� �Լ�
    Public Declare Function AxlM3GetMCParaUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef wCh0Slaves As Integer, ByRef wCh1Slaves As Integer, ByRef dwCh0CycTime As Integer, ByRef dwCh1CycTime As Integer, ByRef dwChInfoMaxRetry As Integer) As Integer
    ' M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� �Լ�
    Public Declare Function AxlM3SetMCParaUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wIdx As Integer, ByVal wChannel As Integer, ByVal wSlaveAddr As Integer, ByVal dwProtoCalType As Integer, ByVal dwTransBytes As Integer, ByVal dwDeviceCode As Integer) As Integer
    ' M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� ��� Ȯ�� �Լ�
    Public Declare Function AxlM3GetMCParaUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wIdx As Integer, ByRef wChannel As Integer, ByRef wSlaveAddr As Integer, ByRef dwProtoCalType As Integer, ByRef dwTransBytes As Integer, ByRef dwDeviceCode As Integer) As Integer

    ' M-III Master ���峻�� �������͸� DWord������ Ȯ�� �Լ�
    Public Declare Function AxlBoardReadDWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wOffset As Integer, ByRef dwData As Integer) As Integer
    ' M-III Master ���峻�� �������͸� DWord������ ���� �Լ�
    Public Declare Function AxlBoardWriteDWord Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wOffset As Integer, ByVal dwData As Integer) As Integer

    ' ���峻�� Ȯ�� �������͸� DWord������ ���� �� Ȯ���Ѵ�.
    Public Declare Function AxlBoardReadDWordEx Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwOffset As Integer, ByRef dwData As Integer) As Integer
    Public Declare Function AxlBoardWriteDWordEx Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwOffset As Integer, ByVal dwData As Integer) As Integer

    ' ������ ���� ���� ���� �Լ�
    Public Declare Function AxmM3ServoSetCtrlStopMode Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal bStopMode As Byte) As Integer
    ' ������ Lt ���� ���·� ���� �Լ�
    Public Declare Function AxmM3ServoSetCtrlLtSel Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal bLtSel1 As Byte, ByVal bLtSel2 As Byte) As Integer
    ' ������ IO �Է� ���¸� Ȯ�� �Լ�
    Public Declare Function AxmStatusReadServoCmdIOInput Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upStatus As Integer) As Integer
    ' ������ ���� ���� �Լ�
    Public Declare Function AxmM3ServoExInterpolate Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwTPOS As Integer, ByVal dwVFF As Integer, ByVal dwTFF As Integer, ByVal dwTLIM As Integer, ByVal dwExSig1 As Integer, ByVal dwExSig2 As Integer) As Integer
    ' ���� �������� ���̾ ���� �Լ�
    Public Declare Function AxmM3ServoSetExpoAccBias Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal wBias As Integer) As Integer
    ' ���� �������� �ð� ���� �Լ�
    Public Declare Function AxmM3ServoSetExpoAccTime Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal wTime As Integer) As Integer
    ' ������ �̵� �ð��� ���� �Լ�
    Public Declare Function AxmM3ServoSetMoveAvrTime Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal wTime As Integer) As Integer
    ' ������ Acc ���� ���� �Լ�
    Public Declare Function AxmM3ServoSetAccFilter Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal bAccFil As Byte) As Integer
    ' ������ ���� �����1 ���� �Լ�
    Public Declare Function AxmM3ServoSetCprmMonitor1 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal bMonSel As Byte) As Integer
    ' ������ ���� �����2 ���� �Լ�
    Public Declare Function AxmM3ServoSetCprmMonitor2 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal bMonSel As Byte) As Integer
    ' ������ ���� �����1 Ȯ�� �Լ�
    Public Declare Function AxmM3ServoStatusReadCprmMonitor1 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upStatus As Integer) As Integer
    ' ������ ���� �����2 Ȯ�� �Լ�
    Public Declare Function AxmM3ServoStatusReadCprmMonitor2 Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upStatus As Integer) As Integer
    ' ���� �������� Dec ���� �Լ�
    Public Declare Function AxmM3ServoSetAccDec Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal wAcc1 As Integer, ByVal wAcc2 As Integer, ByVal wAccSW As Integer, ByVal wDec1 As Integer, ByVal wDec2 As Integer, ByVal wDecSW As Integer) As Integer
    ' ���� ���� ���� �Լ�
    Public Declare Function AxmM3ServoSetStop Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal lMaxDecel As Integer) As Integer

    '========== ǥ�� I/O ��� ���� Ŀ�ǵ� =========================================================================
    ' Network��ǰ �� �����̺� ����� �Ķ���� ���� ���� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationParameter Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal wNo As Integer, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Integer
    ' Network��ǰ �� �����̺� ����� �Ķ���� ���� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationParameter Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal wNo As Integer, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Integer
    ' Network��ǰ �� �����̺� ����� ID���� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationIdRd Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bIdCode As Byte, ByVal bOffset As Byte, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Integer
    ' Network��ǰ �� �����̺� ����� ��ȿ Ŀ�ǵ�� ����ϴ� �Լ�
    Public Declare Function AxlM3SetStationNop Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte) As Integer
    ' Network��ǰ �� �����̺� ����� �¾��� �ǽ��ϴ� �Լ�
    Public Declare Function AxlM3SetStationConfig Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bConfigMode As Byte, ByVal bModuleType As Byte) As Integer
    ' Network��ǰ �� �����̺� ����� �˶� �� ��� ���� ���� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationAlarm Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal wAlarmRdMod As Integer, ByVal wAlarmIndex As Integer, ByVal bModuleType As Byte, ByRef pwAlarmData As Integer) As Integer
    ' Network��ǰ �� �����̺� ����� �˶� �� ��� ���¸� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationAlarmClear Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal wAlarmClrMod As Integer, ByVal bModuleType As Byte) As Integer
    ' Network��ǰ �� �����̺� ������ ��������� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationSyncSet Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte) As Integer
    ' Network��ǰ �� �����̺� ������ ������ �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationConnect Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bVer As Byte, ByVal bComMode As Byte, ByVal bComTime As Byte, ByVal bProfileType As Byte, ByVal bModuleType As Byte) As Integer
    ' Network��ǰ �� �����̺� ������ ���� ������ �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationDisConnect Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte) As Integer
    ' Network��ǰ �� �����̺� ����� ���ֹ߼� �Ķ���� ���� ���� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationStoredParameter Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal wNo As Integer, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Integer
    ' Network��ǰ �� �����̺� ����� ���ֹ߼� �Ķ���� ���� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationStoredParameter Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal wNo As Integer, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Integer
    ' Network��ǰ �� �����̺� ����� �޸� ���� ���� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationMemory Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal wSize As Integer, ByVal dwAddress As Integer, ByVal bModuleType As Byte, ByVal bMode As Byte, ByVal bDataType As Byte, ByRef pbData As Byte) As Integer
    ' Network��ǰ �� �����̺� ����� �޸� ���� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationMemory Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal wSize As Integer, ByVal dwAddress As Integer, ByVal bModuleType As Byte, ByVal bMode As Byte, ByVal bDataType As Byte, ByRef pbData As Byte) As Integer

    '========== ǥ�� I/O ��� Ŀ�ؼ� Ŀ�ǵ� =========================================================================
    ' Network��ǰ �� �������� �����̺� ����� �ڵ� �＼�� ��� ���� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationAccessMode Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte, ByVal bRWSMode As Byte) As Integer
    ' Network��ǰ �� �������� �����̺� ����� �ڵ� �＼�� ��� �������� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationAccessMode Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte, ByRef bRWSMode As Byte) As Integer
    ' Network��ǰ �� �����̺� ����� ���� �ڵ� ���� ��带 �����ϴ� �Լ�
    Public Declare Function AxlM3SetAutoSyncConnectMode Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte, ByVal dwAutoSyncConnectMode As Integer) As Integer
    ' Network��ǰ �� �����̺� ����� ���� �ڵ� ���� ��� �������� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetAutoSyncConnectMode Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte, ByRef dwpAutoSyncConnectMode As Integer) As Integer
    ' Network��ǰ �� �����̺� ��⿡ ���� ���� ����ȭ ������ �����ϴ� �Լ�
    Public Declare Function AxlM3SyncConnectSingle Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte) As Integer
    ' Network��ǰ �� �����̺� ��⿡ ���� ���� ����ȭ ���� ������ �����ϴ� �Լ�
    Public Declare Function AxlM3SyncDisconnectSingle Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte) As Integer
    ' Network��ǰ �� �����̺� ������ ���� ���¸� Ȯ���ϴ� �Լ�
    Public Declare Function AxlM3IsOnLine Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByRef dwData As Integer) As Integer

    '========== ǥ�� I/O �������� Ŀ�ǵ� =========================================================================
    ' Network��ǰ �� ����ȭ ������ �����̺� I/O ��⿡ ���� ������ �������� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationRWS Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte, ByRef pdwParam As Integer, ByVal bSize As Byte) As Integer
    ' Network��ǰ �� ����ȭ ������ �����̺� I/O ��⿡ ���� �����Ͱ��� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationRWS Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte, ByRef pdwParam As Integer, ByVal bSize As Byte) As Integer
    ' Network��ǰ �� �񵿱�ȭ ������ �����̺� I/O ��⿡ ���� ������ �������� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationRWA Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte, ByRef pdwParam As Integer, ByVal bSize As Byte) As Integer
    ' Network��ǰ �� �񵿱�ȭ ������ �����̺� I/O ��⿡ ���� �����Ͱ��� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationRWA Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModuleNo As Integer, ByVal bModuleType As Byte, ByRef pdwParam As Integer, ByVal bSize As Byte) As Integer

    ' MLIII adjustment operation�� ���� �Ѵ�.
    ' dwReqCode == 0x1005 : parameter initialization : 20sec
    ' dwReqCode == 0x1008 : absolute encoder reset   : 5sec
    ' dwReqCode == 0x100E : automatic offset adjustment of motor current detection signals  : 5sec
    ' dwReqCode == 0x1013 : Multiturn limit setting  : 5sec
    Public Declare Function AxmM3AdjustmentOperation Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwReqCode As Integer) As Integer

    ' M3 ���� ���� �˻� ���� ���� ���ܿ� �Լ��̴�.
    Public Declare Function AxmHomeGetM3FWRealRate Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upHomeMainStepNumber As Integer, ByRef upHomeSubStepNumber As Integer, ByRef upHomeLastMainStepNumber As Integer, ByRef upHomeLastSubStepNumber As Integer) As Integer
    ' M3 ���� ���� �˻��� ���������� Ż��� �����Ǵ� ��ġ ���� ��ȯ�ϴ� �Լ��̴�.
    Public Declare Function AxmHomeGetM3OffsetAvoideSenArea Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dPos As Double) As Integer
    ' M3 ���� ���� �˻��� ���������� Ż��� �����Ǵ� ��ġ ���� �����ϴ� �Լ��̴�.
    ' dPos ���� ���� 0�̸� �ڵ����� Ż��� �����Ǵ� ��ġ ���� �ڵ����� �����ȴ�.
    ' dPos ���� ���� ����� ���� �Է��Ѵ�.
    Public Declare Function AxmHomeSetM3OffsetAvoideSenArea Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dPos As Double) As Integer

    ' M3 ����, ����ġ ���ڴ� ��� ����, �����˻� �Ϸ� �� CMD/ACT POS �ʱ�ȭ ���� ����
    ' dwSel: 0, ���� �˻��� CMD/ACTPOS 0���� ������.[�ʱⰪ]
    ' dwSel: 1, ���� �˻��� CMD/ACTPOS ���� �������� ����.
    Public Declare Function AxmM3SetAbsEncOrgResetDisable Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwSel As Integer) As Integer

    ' M3 ����, ����ġ ���ڴ� ��� ����, �����˻� �Ϸ� �� CMD/ACT POS �ʱ�ȭ ���� ������ ��������
    ' upSel: 0, ���� �˻��� CMD/ACTPOS 0���� ������.[�ʱⰪ]
    ' upSel: 1, ���� �˻��� CMD/ACTPOS ���� �������� ����.
    Public Declare Function AxmM3GetAbsEncOrgResetDisable Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upSel As Integer) As Integer

    ' M3 ����, �����̺� OFFLINE ��ȯ�� �˶� ���� ��� ��� ���� ����
    ' dwSel: 0, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ������� ����.[�ʱⰪ]
    ' dwSel: 1, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ���

    Public Declare Function AxmM3SetOfflineAlarmEnable Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwSel As Integer) As Integer
    ' M3 ����, �����̺� OFFLINE ��ȯ�� �˶� ���� ��� ��� ���� ���� �� ��������
    ' upSel: 0, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ������� ����.[�ʱⰪ]
    ' upSel: 1, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ���

    Public Declare Function AxmM3GetOfflineAlarmEnable Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upSel As Integer) As Integer

    ' M3 ����, �����̺� OFFLINE ��ȯ ���� ���� �� ��������
    ' upSel: 0, ML3 �����̺� ONLINE->OFFLINE ��ȯ���� ����
    ' upSel: 1, ML3 �����̺� ONLINE->OFFLINE ��ȯ�Ǿ���.
    Public Declare Function AxmM3ReadOnlineToOfflineStatus Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef upStatus As Integer) As Integer

    ' Network ��ǰ�� Configuration Lock ���¸� �����Ѵ�.
    ' wLockMode  : DISABLE(0), ENABLE(1)
    Public Declare Function AxlSetLockMode Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal wLockMode As Integer) As Integer

    ' Lock ������ ����
    Public Declare Function AxlSetLockData Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwTotalNodeNum As Integer, ByRef dwpNodeNo As Integer, ByRef dwpNodeID As Integer, ByRef dwpLockData As Integer) As Integer

    Public Declare Function AxmMoveStartPosWithAVC Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dPosition As Double, ByVal dMaxVelocity As Double, ByVal dMaxAccel As Double, ByVal dMinJerk As Double, ByRef dpMoveVelocity As Double, ByRef dpMoveAccel As Double, ByRef dpMoveJerk As Double) As Integer
    ' ī���� ����� 2-D ������ġ Ʈ���� ����� ���� �ʿ��� Ʈ���� ��ġ ������ �����Ѵ�.
    ' lChannelNo : 0,1 channel �� ��� 0, 2,3 channel �� ��� 2 �� ����.
    ' nDataCnt :
    '  nDataCnt > 0 : ������ ���, nDataCnt <= 0 : ��ϵ� ������ �ʱ�ȭ.
    ' dwOption : Reserved.
    ' dpPatternData : (X1, Y1)
    Public Declare Function AxcTriggerSetPatternData Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal nDataCnt As Integer, ByVal dwOption As Integer, ByRef dpPatternData As Double) As Integer
    ' ī���� ����� 2-D ������ġ Ʈ���� ����� ���� �ʿ��� Ʈ���� ��ġ ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPatternData Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef npDataCnt As Integer, ByRef dwpOption As Integer, ByRef dpPatternData As Double) As Integer

    '���� ���� �����Ͽ� AxmContiEndNode �Լ������� ������������ Node �� Data Queue �� �̸� ä������ �� �ֵ����ϴ� ����� Ȱ��ȭ �Ѵ�.
    'bPushPrevContiQueue : 1  �ش� ��� Ȱ��ȭ
    'bPushPrevContiQueue : 0  �ش� ��� ��Ȱ��ȭ
    Public Declare Function AxmContiSetPushPrevContiQueueEnable Lib "AXL.dll" (ByVal lCoordinate As Integer, ByVal bPushPrevContiQueue As Byte) As Integer
    '�����ص� AxmContiSetPushPrevContiQueueEnable Flag���� ��ȯ�Ѵ�.
    Public Declare Function AxmContiGetPushPrevContiQueueEnable Lib "AXL.dll" (ByVal lCoordinate As Integer, ByRef bPushPrevContiQueue As BOOL*) As Integer

    ' ���Ӻ��� ���� �� Data Queue �� Node ������ ����Ǿ����� ���¸� ��ȯ�Ѵ�.
    ' AxmContiSetPushPrevContiQueueEnable(long lCoordinate, 1) �� �����Ǿ����� ��츸 ��ȿ
    ' bPushPrevContiQueueComplete : 1  Node Data ���� �Ϸ�
    ' bPushPrevContiQueueComplete : 0  Node Data ���� �Ǿ���������
    Public Declare Function AxmContiGetPushPrevContiQueueComplete Lib "AXL.dll" (ByVal lCoordinate As Integer, ByRef bPushPrevContiQueueComplete As BOOL*) As Integer

    ' ���Ӻ��� ���� �� ù ��� ���� �� ������ ��� ���� �� �����ð� ���� ������ ��ǥ���� ������ ���� OutputBit On/Off ����
    ' AxmContiBeginNode �տ� ȣ���ؾ� �Ѵ�. �ѹ� �����ϸ� Flag�� �ʱ�ȭ�Ǿ� �ٽ� ȣ���ؾ� ����� �� �ִ�.
    ' StartTime/EndTime ������ [Sec]�̸�, 0 ~ 6.5�ʱ��� ���� �����ϴ�.
    ' uOnoff : 0 - ���� ��ġ���� Bit On ���� ��ġ���� Bit Off
    '          : 1 - ���� ��ġ���� Bit Off ���� ��ġ���� Bit On
    ' lEndMode : 0 - ������ ��� ���� ���� �� ��� OutputBit Off/On
    '   : 1 - ������ ��� ���� ���� �� �Է��� EndTime ���� OutputBit Off/On
    '   : 2 - ���� ���� �� OutputBit On/Off �� �Է��� EndTime ���� OutputBit Off/On
    Public Declare Function AxmContiSetWriteOutputBit Lib "AXL.dll" (ByVal lCoordinate As Integer, ByVal dStartTime As Double, ByVal dEndTime As Double, ByVal lBitNo As Integer, ByVal uOnoff As Integer, ByVal lEndMode As Integer) As Integer

    ' AxmContiSetWriteOutputBit�� ������ ������ ��ȯ�Ѵ�.
    Public Declare Function AxmContiGetWriteOutputBit Lib "AXL.dll" (ByVal lCoordinate As Integer, ByRef dpStartTime As Double, ByRef dpEndTime As Double, ByRef lpBitNo As Integer, ByRef lpOnoff As Integer, ByRef lpEndMode As Integer) As Integer

    ' AxmContiSetWriteOutputBit�� ������ ������ �����Ѵ�.
    Public Declare Function AxmContiResetWriteOutputBit Lib "AXL.dll" (ByVal lCoordinate As Integer) As Integer

    ' AxmMoveTorqueStop �Լ��� ��ũ ���� ���� �� CmdPos ���� ActPos ���� ��ġ��Ű�� ���������� ��� �ð��� �����Ѵ�.
    ' dwSettlingTime
    '  1) ����: [msec]
    '  2) �Է� ���� ����: 0 ~ 10000
    '  *����* AxmMoveTorqueSetStopSettlingTime �Լ��� ��� �ð��� �������� ������, dafault ���� 10[msec]�� ����ȴ�.
    Public Declare Function AxmMoveTorqueSetStopSettlingTime Lib "AXL.dll" (ByVal lAxisNo As Integer, ByVal dwSettlingTime As Integer) As Integer
    ' AxmMoveTorqueStop �Լ��� ��ũ ���� ���� �� CmdPos ���� ActPos ���� ��ġ��Ű�� ���������� ��� �ð��� ��ȯ�Ѵ�.
    Public Declare Function AxmMoveTorqueGetStopSettlingTime Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwpSettlingTime As Integer) As Integer

    '
    ' Monitor
    ' �����͸� ������ ������ �׸��� �߰��մϴ�.
    Public Declare Function AxlMonitorSetItem Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lItemIndex As Integer, ByVal dwSignalType As Integer, ByVal lSignalNo As Integer, ByVal lSubSignalNo As Integer) As Integer

    ' ������ ������ ������ �׸�鿡 ���� ������ �����ɴϴ�.
    Public Declare Function AxlMonitorGetIndexInfo Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef lpItemSize As Integer, ByRef lpItemIndex As Integer) As Integer

    ' ������ ������ ������ �� �׸��� ���� ������ �����ɴϴ�.
    Public Declare Function AxlMonitorGetItemInfo Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lItemIndex As Integer, ByRef dwpSignalType As Integer, ByRef lpSignalNo As Integer, ByRef lpSubSignalNo As Integer) As Integer

    ' ��� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorResetAllItem Lib "AXL.dll" (ByVal lBoardNo As Integer) As Integer

    ' ���õ� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorResetItem Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lItemIndex As Integer) As Integer

    ' ������ ������ Ʈ���� ������ �����մϴ�.
    Public Declare Function AxlMonitorSetTriggerOption Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwSignalType As Integer, ByVal lSignalNo As Integer, ByVal lSubSignalNo As Integer, ByVal dwOperatorType As Integer, ByVal dValue1 As Double, ByVal dValue2 As Double) As Integer

    ' ������ ������ Ʈ���� ������ �����ɴϴ�.
    'DWORD  __stdcall AxlMonitorGetTriggerOption(DWORD* dwpSignalType, long* lpSignalNo, long* lpSubSignalNo, DWORD* dwpOperatorType, double* dpValue1, double* dpValue2);

    ' ������ ������ Ʈ���� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorResetTriggerOption Lib "AXL.dll" (ByVal lBoardNo As Integer) As Integer

    ' ������ ������ �����մϴ�.
    Public Declare Function AxlMonitorStart Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwStartOption As Integer, ByVal dwOverflowOption As Integer) As Integer

    ' ������ ������ �����մϴ�.
    Public Declare Function AxlMonitorStop Lib "AXL.dll" (ByVal lBoardNo As Integer) As Integer

    ' ������ �����͸� �����ɴϴ�.
    Public Declare Function AxlMonitorReadData Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef lpItemSize As Integer, ByRef lpDataCount As Integer, ByRef dpReadData As Double) As Integer

    ' ������ ������ �ֱ⸦ �����ɴϴ�.
    Public Declare Function AxlMonitorReadPeriod Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef dwpPeriod As Integer) As Integer
    '


    '
    ' MonitorEx
    ' �����͸� ������ ������ �׸��� �߰��մϴ�.
    Public Declare Function AxlMonitorExSetItem Lib "AXL.dll" (ByVal lItemIndex As Integer, ByVal dwSignalType As Integer, ByVal lSignalNo As Integer, ByVal lSubSignalNo As Integer) As Integer

    ' ������ ������ ������ �׸�鿡 ���� ������ �����ɴϴ�.
    Public Declare Function AxlMonitorExGetIndexInfo Lib "AXL.dll" (ByRef lpItemSize As Integer, ByRef lpItemIndex As Integer) As Integer

    ' ������ ������ ������ �� �׸��� ���� ������ �����ɴϴ�.
    Public Declare Function AxlMonitorExGetItemInfo Lib "AXL.dll" (ByVal lItemIndex As Integer, ByRef dwpSignalType As Integer, ByRef lpSignalNo As Integer, ByRef lpSubSignalNo As Integer) As Integer

    ' ��� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorExResetAllItem Lib "AXL.dll" () As Integer

    ' ���õ� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorExResetItem Lib "AXL.dll" (ByVal lItemIndex As Integer) As Integer

    ' ������ ������ Ʈ���� ������ �����մϴ�.
    Public Declare Function AxlMonitorExSetTriggerOption Lib "AXL.dll" (ByVal dwSignalType As Integer, ByVal lSignalNo As Integer, ByVal lSubSignalNo As Integer, ByVal dwOperatorType As Integer, ByVal dValue1 As Double, ByVal dValue2 As Double) As Integer

    ' ������ ������ Ʈ���� ������ �����ɴϴ�.
    'DWORD  __stdcall AxlMonitorExGetTriggerOption(DWORD* dwpSignalType, long* lpSignalNo, long* lpSubSignalNo, DWORD* dwpOperatorType, double* dpValue1, double* dpValue2);

    ' ������ ������ Ʈ���� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorExResetTriggerOption Lib "AXL.dll" () As Integer

    ' ������ ������ �����մϴ�.
    Public Declare Function AxlMonitorExStart Lib "AXL.dll" (ByVal dwStartOption As Integer, ByVal dwOverflowOption As Integer) As Integer

    ' ������ ������ �����մϴ�.
    Public Declare Function AxlMonitorExStop Lib "AXL.dll" () As Integer

    ' ������ �����͸� �����ɴϴ�.
    Public Declare Function AxlMonitorExReadData Lib "AXL.dll" (ByRef lpItemSize As Integer, ByRef lpDataCount As Integer, ByRef dpReadData As Double) As Integer

    ' ������ ������ �ֱ⸦ �����ɴϴ�.
    Public Declare Function AxlMonitorExReadPeriod Lib "AXL.dll" (ByRef dwpPeriod As Integer) As Integer
    '

    ' X2, Y2 �࿡ ���� Offset ��ġ ������ ������ 2�� ���� ���� #01.
    Public Declare Function AxmLineMoveDual01 Lib "AXL.dll" (ByVal lCoordNo As Integer, ByRef dpEndPosition As Double, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal dOffsetLength As Double, ByVal dTotalLength As Double, ByRef dpStartOffsetPosition As Double, ByRef dpEndOffsetPosition As Double) As Integer
    ' X2, Y2 �࿡ ���� Offset ��ġ ������ ������ 2�� ��ȣ ���� #01.
    Public Declare Function AxmCircleCenterMoveDual01 Lib "AXL.dll" (ByVal lCoordNo As Integer, ByRef lpAxes As Integer, ByRef dpCenterPosition As Double, ByRef dpEndPosition As Double, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal dwCWDir As Integer, ByVal dOffsetLength As Double, ByVal dTotalLength As Double, ByRef dpStartOffsetPosition As Double, ByRef dpEndOffsetPosition As Double) As Integer

    ' �ش纸���� connect mode �� ��ȯ�Ѵ�.
    ' dpMode : 1 Auto Connect Mode
    ' dpMode : 0 Manual Connect Mode
    Public Declare Function AxlGetBoardConnectMode Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef dwpMode As Integer) As Integer
    ' �ش纸���� connect mode �� �����Ѵ�.
    ' dMode : 1 Auto Connect Mode
    ' dMode : 0 Manual Connect Mode
    Public Declare Function AxlSetBoardConnectMode Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal dwMode As Integer) As Integer

    '������ ���� Command Queue �� �ʱ�ȭ �Ѵ�.
    Public Declare Function AxmStatusSetCmdQueueClear Lib "AXL.dll" (ByVal lAxisNo As Integer) As Integer

    ' ������ ���� ��� �������ݰ��� Data �� Ȯ���Ѵ�.
    Public Declare Function AxmStatusGetControlBits Lib "AXL.dll" (ByVal lAxisNo As Integer, ByRef dwpTxData As Integer, ByRef dwpRxData As Integer) As Integer

    ' ��� ���� AXL�� �ִ��� Ȯ��(Shared Memory�� �����ϴ��� Ȯ��)
    Public Declare Function AxlIsUsing Lib "AXL.dll" () As Byte
    Public Declare Function AxlRescanExternalDevice Lib "AXL.dll" () As Integer
    Public Declare Function AxlGetExternalDeviceInfo Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef devInfo As void*) As Integer


End Module
