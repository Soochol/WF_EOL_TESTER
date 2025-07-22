
Attribute VB_Name = "AXDev"


    ' Board Number�� �̿��Ͽ� Board Address ã��
    Public Declare Function AxlGetBoardAddress Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef upBoardAddress As Long) As Long
    ' Board Number�� �̿��Ͽ� Board ID ã��
    Public Declare Function AxlGetBoardID Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef upBoardID As Long) As Long
    ' Board Number�� �̿��Ͽ� Board Version ã��
    Public Declare Function AxlGetBoardVersion Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef upBoardVersion As Long) As Long
    ' Board Number�� Module Position�� �̿��Ͽ� Module ID ã��
    Public Declare Function AxlGetModuleID Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef upModuleID As Long) As Long
    ' Board Number�� Module Position�� �̿��Ͽ� Module Version ã��
    Public Declare Function AxlGetModuleVersion Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef upModuleVersion As Long) As Long
    ' Board Number�� Module Position�� �̿��Ͽ� Network Node ���� Ȯ��
    Public Declare Function AxlGetModuleNodeInfo Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef upNetNo As Long, ByRef upNodeAddr As Long) As Long

    ' Board�� ����� ���� Data Flash Write (PCI-R1604[RTEX master board]����)
    ' lPageAddr(0 ~ 199)
    ' lByteNum(1 ~ 120)
    ' ����) Flash�� ����Ÿ�� ������ ���� ���� �ð�(�ִ� 17mSec)�� �ҿ�Ǳ⶧���� ���� ����� ���� �ð��� �ʿ���.
    Public Declare Function AxlSetDataFlash Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lPageAddr As Long, ByVal lBytesNum As Long, ByRef bpSetData As Byte) As Long

    ' Board�� ����� ESTOP �ܺ� �Է� ��ȣ�� �̿��� InterLock ��� ��� ���� �� ������ ���� ����� ���� (PCI-Rxx00[MLIII master board]����)
    ' 1. ��� ����
    '   ����: ��� ��� ������ �ܺο��� ESTOP ��ȣ �ΰ��� ���忡 ����� ��� ���� ��忡 ���ؼ� ESTOP ���� ��� ����
    '    0: ��� ������� ����(�⺻ ������)
    '    1: ��� ���
    ' 2. ������ ���� ��
    '      �Է� ���� ��� ���� ���� 1 ~ 40, ���� ��� Cyclic time
    ' Board �� dwInterLock, dwDigFilterVal�� �̿��Ͽ� EstopInterLock ��� ����
    Public Declare Function AxlSetEStopInterLock Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwInterLock As Long, ByVal dwDigFilterVal As Long) As Long
    ' Board�� ������ dwInterLock, dwDigFilterVal ������ ��������
    Public Declare Function AxlGetEStopInterLock Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwInterLock As Long, ByRef dwDigFilterVal As Long) As Long
    ' Board�� �Էµ� EstopInterLock ��ȣ�� �д´�.
    Public Declare Function AxlReadEStopInterLock Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwInterLock As Long) As Long

    ' Board�� ����� ���� Data Flash Read(PCI-R1604[RTEX master board]����)
    ' lPageAddr(0 ~ 199)
    ' lByteNum(1 ~ 120)
    Public Declare Function AxlGetDataFlash Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lPageAddr As Long, ByVal lBytesNum As Long, ByRef bpGetData As Byte) As Long

    ' Board Number�� Module Position�� �̿��Ͽ� AIO Module Number ã��
    Public Declare Function AxaInfoGetModuleNo Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef lpModuleNo As Long) As Long
    ' Board Number�� Module Position�� �̿��Ͽ� DIO Module Number ã��
    Public Declare Function AxdInfoGetModuleNo Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef lpModuleNo As Long) As Long

    ' ���� �࿡ IPCOMMAND Setting
    Public Declare Function AxmSetCommand Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte) As Long
    ' ���� �࿡ 8bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData08 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' ���� �࿡ 8bit IPCOMMAND ��������
    Public Declare Function AxmGetCommandData08 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' ���� �࿡ 16bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData16 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' ���� �࿡ 16bit IPCOMMAND ��������
    Public Declare Function AxmGetCommandData16 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' ���� �࿡ 24bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData24 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' ���� �࿡ 24bit IPCOMMAND ��������
    Public Declare Function AxmGetCommandData24 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' ���� �࿡ 32bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData32 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' ���� �࿡ 32bit IPCOMMAND ��������
    Public Declare Function AxmGetCommandData32 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long

    ' ���� �࿡ QICOMMAND Setting
    Public Declare Function AxmSetCommandQi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte) As Long
    ' ���� �࿡ 8bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData08Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' ���� �࿡ 8bit QICOMMAND ��������
    Public Declare Function AxmGetCommandData08Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' ���� �࿡ 16bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData16Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' ���� �࿡ 16bit QICOMMAND ��������
    Public Declare Function AxmGetCommandData16Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' ���� �࿡ 24bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData24Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' ���� �࿡ 24bit QICOMMAND ��������
    Public Declare Function AxmGetCommandData24Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' ���� �࿡ 32bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData32Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' ���� �࿡ 32bit QICOMMAND ��������
    Public Declare Function AxmGetCommandData32Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long

    ' ���� �࿡ Port Data �������� - IP
    Public Declare Function AxmGetPortData Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wOffset As Long, ByRef upData As Long) As Long
    ' ���� �࿡ Port Data Setting - IP
    Public Declare Function AxmSetPortData Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wOffset As Long, ByVal dwData As Long) As Long
    ' ���� �࿡ Port Data �������� - QI
    Public Declare Function AxmGetPortDataQi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal byOffset As Long, ByRef wData As Long) As Long
    ' ���� �࿡ Port Data Setting - QI
    Public Declare Function AxmSetPortDataQi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal byOffset As Long, ByVal wData As Long) As Long

    ' ���� �࿡ ��ũ��Ʈ�� �����Ѵ�. - IP
    ' sc    : ��ũ��Ʈ ��ȣ (1 - 4)
    ' event : �߻��� �̺�Ʈ SCRCON �� �����Ѵ�.
    '         �̺�Ʈ ���� �హ������, �̺�Ʈ �߻��� ��, �̺�Ʈ ���� 1,2 �Ӽ� �����Ѵ�.
    ' cmd   : � ������ �ٲܰ����� ���� SCRCMD�� �����Ѵ�.
    ' data  : � Data�� �ٲܰ����� ����
    Public Declare Function AxmSetScriptCaptionIp Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sc As Long, ByVal event As Long, ByVal data As Long) As Long
    ' ���� �࿡ ��ũ��Ʈ�� ��ȯ�Ѵ�. - IP
    Public Declare Function AxmGetScriptCaptionIp Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sc As Long, ByRef event As Long, ByRef data As Long) As Long

    ' ���� �࿡ ��ũ��Ʈ�� �����Ѵ�. - QI
    ' sc    : ��ũ��Ʈ ��ȣ (1 - 4)
    ' event : �߻��� �̺�Ʈ SCRCON �� �����Ѵ�.
    '         �̺�Ʈ ���� �హ������, �̺�Ʈ �߻��� ��, �̺�Ʈ ���� 1,2 �Ӽ� �����Ѵ�.
    ' cmd   : � ������ �ٲܰ����� ���� SCRCMD�� �����Ѵ�.
    ' data  : � Data�� �ٲܰ����� ����
    Public Declare Function AxmSetScriptCaptionQi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sc As Long, ByVal event As Long, ByVal cmd As Long, ByVal data As Long) As Long
    ' ���� �࿡ ��ũ��Ʈ�� ��ȯ�Ѵ�. - QI
    Public Declare Function AxmGetScriptCaptionQi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sc As Long, ByRef event As Long, ByRef cmd As Long, ByRef data As Long) As Long

    ' ���� �࿡ ��ũ��Ʈ ���� Queue Index�� Clear ��Ų��.
    ' uSelect IP.
    ' uSelect(0): ��ũ��Ʈ Queue Index �� Clear�Ѵ�.
    '        (1): ĸ�� Queue�� Index Clear�Ѵ�.
    ' uSelect QI.
    ' uSelect(0): ��ũ��Ʈ Queue 1 Index �� Clear�Ѵ�.
    '        (1): ��ũ��Ʈ Queue 2 Index �� Clear�Ѵ�.
    Public Declare Function AxmSetScriptCaptionQueueClear Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal uSelect As Long) As Long

    ' ���� �࿡ ��ũ��Ʈ ���� Queue�� Index ��ȯ�Ѵ�.
    ' uSelect IP
    ' uSelect(0): ��ũ��Ʈ Queue Index�� �о�´�.
    '        (1): ĸ�� Queue Index�� �о�´�.
    ' uSelect QI.
    ' uSelect(0): ��ũ��Ʈ Queue 1 Index�� �о�´�.
    '        (1): ��ũ��Ʈ Queue 2 Index�� �о�´�.
    Public Declare Function AxmGetScriptCaptionQueueCount Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef updata As Long, ByVal uSelect As Long) As Long

    ' ���� �࿡ ��ũ��Ʈ ���� Queue�� Data���� ��ȯ�Ѵ�.
    ' uSelect IP
    ' uSelect(0): ��ũ��Ʈ Queue Data �� �о�´�.
    '        (1): ĸ�� Queue Data�� �о�´�.
    ' uSelect QI.
    ' uSelect(0): ��ũ��Ʈ Queue 1 Data �о�´�.
    '        (1): ��ũ��Ʈ Queue 2 Data �о�´�.
    Public Declare Function AxmGetScriptCaptionQueueDataCount Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef updata As Long, ByVal uSelect As Long) As Long

    ' ���� ����Ÿ�� �о�´�.
    Public Declare Function AxmGetOptimizeDriveData Lib "AXL.dll" () As Long


    ' ���峻�� �������͸� Byte������ ���� �� Ȯ���Ѵ�.
    Public Declare Function AxmBoardWriteByte Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByVal byData As Byte) As Long
    Public Declare Function AxmBoardReadByte Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByRef byData As Byte) As Long

    ' ���峻�� �������͸� Word������ ���� �� Ȯ���Ѵ�.
    Public Declare Function AxmBoardWriteWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByVal wData As Long) As Long
    Public Declare Function AxmBoardReadWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByRef wData As Long) As Long

    ' ���峻�� �������͸� DWord������ ���� �� Ȯ���Ѵ�.
    Public Declare Function AxmBoardWriteDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByVal dwData As Long) As Long
    Public Declare Function AxmBoardReadDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByRef dwData As Long) As Long

    ' ���峻�� ��⿡ �������͸� Byte���� �� Ȯ���Ѵ�.
    Public Declare Function AxmModuleWriteByte Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByVal byData As Byte) As Long
    Public Declare Function AxmModuleReadByte Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByRef byData As Byte) As Long

    ' ���峻�� ��⿡ �������͸� Word���� �� Ȯ���Ѵ�.
    Public Declare Function AxmModuleWriteWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByVal wData As Long) As Long
    Public Declare Function AxmModuleReadWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByRef wData As Long) As Long

    ' ���峻�� ��⿡ �������͸� DWord���� �� Ȯ���Ѵ�.
    Public Declare Function AxmModuleWriteDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByVal dwData As Long) As Long
    Public Declare Function AxmModuleReadDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByRef dwData As Long) As Long

    ' �ܺ� ��ġ �񱳱⿡ ���� �����Ѵ�.(Pos = Unit)
    Public Declare Function AxmStatusSetActComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPos As Double) As Long
    ' �ܺ� ��ġ �񱳱⿡ ���� ��ȯ�Ѵ�.(Positon = Unit)
    Public Declare Function AxmStatusGetActComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dpPos As Double) As Long

    ' ���� ��ġ �񱳱⿡ ���� �����Ѵ�.(Pos = Unit)
    Public Declare Function AxmStatusSetCmdComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPos As Double) As Long
    ' ���� ��ġ �񱳱⿡ ���� ��ȯ�Ѵ�.(Pos = Unit)
    Public Declare Function AxmStatusGetCmdComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dpPos As Double) As Long
    ' ABS Position �� Flash �� �����Ѵ�.
    Public Declare Function AxmStatusSetFlashAbsOffset Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPosition As Long) As Long
    ' Flash �� ���� �� ABS Position �� ��ȯ�Ѵ�.
    ' dReadType  : Value in Flash Memory (0), Real used Value in memory(1)
    Public Declare Function AxmStatusGetFlashAbsOffset Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dPosition As Long, ByVal dReadType As Long) As Long
    ' ����ڰ� Flash �� ABS Position ������ �� �ִ� �ɼ��� �����Ѵ�.
    Public Declare Function AxmStatusSetAbsOffsetWriteEnable Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bStatus As Byte) As Long
    ' ABS Position ���� �ɼ��� ���¸� ��ȯ�Ѵ�.
    Public Declare Function AxmStatusGetAbsOffsetWriteEnable Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef bpStatus As bool*) As Long

    '========== �߰� �Լ� =========================================================================================================
    ' ���� ���� �� �ӵ��� ������ ���Ѵ�� �����Ѵ�.
    ' �ӵ� ������� �Ÿ��� �־��־�� �Ѵ�.
    Public Declare Function AxmLineMoveVel Lib "AXL.dll" (ByVal lCoord As Long, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Long

    '========= ���� ��ġ ���� �Լ�( �ʵ�: IP������ , QI���� ��ɾ���)==============================================================
    ' ���� ���� Sensor ��ȣ�� ��� ���� �� ��ȣ �Է� ������ �����Ѵ�.
    ' ��� ���� LOW(0), HIGH(1), UNUSED(2), USED(3)
    Public Declare Function AxmSensorSetSignal Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal uLevel As Long) As Long
    ' ���� ���� Sensor ��ȣ�� ��� ���� �� ��ȣ �Է� ������ ��ȯ�Ѵ�.
    Public Declare Function AxmSensorGetSignal Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upLevel As Long) As Long
    ' ���� ���� Sensor ��ȣ�� �Է� ���¸� ��ȯ�Ѵ�
    Public Declare Function AxmSensorReadSignal Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upStatus As Long) As Long

    ' ���� ���� ������ �ӵ��� �������� ���� ��ġ ����̹��� �����Ѵ�.
    ' Sensor ��ȣ�� Active level�Է� ���� ��� ��ǥ�� ������ �Ÿ���ŭ ������ �����Ѵ�.
    ' �޽��� ��µǴ� �������� �Լ��� �����.
    ' lMethod :  0 - �Ϲ� ����, 1 - ���� ��ȣ ���� ���� ���� ����. ��ȣ ���� �� �Ϲ� ����
    '            2 - ���� ����
    Public Declare Function AxmSensorMovePos Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPos As Double, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal lMethod As Long) As Long

    ' ���� ���� ������ �ӵ��� �������� ���� ��ġ ����̹��� �����Ѵ�.
    ' Sensor ��ȣ�� Active level�Է� ���� ��� ��ǥ�� ������ �Ÿ���ŭ ������ �����Ѵ�.
    ' �޽� ����� ����Ǵ� �������� �Լ��� �����.
    Public Declare Function AxmSensorStartMovePos Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPos As Double, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal lMethod As Long) As Long

    ' �����˻� ���ེ�� ��ȭ�� ����� ��ȯ�Ѵ�.
    ' *lpStepCount      : ��ϵ� Step�� ����
    ' *upMainStepNumber : ��ϵ� MainStepNumber ������ �迭����Ʈ
    ' *upStepNumber     : ��ϵ� StepNumber ������ �迭����Ʈ
    ' *upStepBranch     : ��ϵ� Step�� Branch ������ �迭����Ʈ
    ' ����: �迭������ 50���� ����
    Public Declare Function AxmHomeGetStepTrace Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef lpStepCount As Long, ByRef upMainStepNumber As Long, ByRef upStepNumber As Long, ByRef upStepBranch As Long) As Long

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
    Public Declare Function AxmHomeSetConfig Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal uZphasCount As Long, ByVal lHomeMode As Long, ByVal lClearSet As Long, ByVal dOrgVel As Double, ByVal dLastVel As Double, ByVal dLeavePos As Double) As Long
    ' ����ڰ� ������ ���� Ȩ���� �Ķ��Ÿ�� ��ȯ�Ѵ�.
    Public Declare Function AxmHomeGetConfig Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upZphasCount As Long, ByRef lpHomeMode As Long, ByRef lpClearSet As Long, ByRef dpOrgVel As Double, ByRef dpLastVel As Double, ByRef dpLeavePos As Double) As Long

    ' ����ڰ� ������ ���� Ȩ ��ġ�� �����Ѵ�.
    ' lHomeMode ���� ���� : 0 - 5 ���� (Move Return�Ŀ� Search��  �����Ѵ�.)
    ' lHomeMode -1�� �״�� ���� HomeConfig���� ����Ѵ�� �״�� ������.
    ' ��������      : Vel���� ����̸� CW, �����̸� CCW.
    Public Declare Function AxmHomeSetMoveSearch Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Long

    ' ����ڰ� ������ ���� Ȩ ������ �����Ѵ�.
    ' lHomeMode ���� ���� : 0 - 12 ����
    ' lHomeMode -1�� �״�� ���� HomeConfig���� ����Ѵ�� �״�� ������.
    ' ��������      : Vel���� ����̸� CW, �����̸� CCW.
    Public Declare Function AxmHomeSetMoveReturn Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Long

    ' ����ڰ� ������ ���� Ȩ ��Ż�� �����Ѵ�.
    ' ��������      : Vel���� ����̸� CW, �����̸� CCW.
    Public Declare Function AxmHomeSetMoveLeave Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Long

    ' ����ڰ� ������ ������ Ȩ ��ġ�� �����Ѵ�.
    ' lHomeMode ���� ���� : 0 - 5 ���� (Move Return�Ŀ� Search��  �����Ѵ�.)
    ' lHomeMode -1�� �״�� ���� HomeConfig���� ����Ѵ�� �״�� ������.
    ' ��������      : Vel���� ����̸� CW, �����̸� CCW.
    Public Declare Function AxmHomeSetMultiMoveSearch Lib "AXL.dll" (ByVal lArraySize As Long, ByRef lpAxesNo As Long, ByRef dpVel As Double, ByRef dpAccel As Double, ByRef dpDecel As Double) As Long

    '������ ��ǥ���� ���� �ӵ� �������� ��带 �����Ѵ�.
    ' (������ : �ݵ�� ����� �ϰ� ��밡��)
    ' ProfileMode : '0' - ��Ī Trapezode
    '               '1' - ���Ī Trapezode
    '               '2' - ��Ī Quasi-S Curve
    '               '3' - ��Ī S Curve
    '               '4' - ���Ī S Curve
    Public Declare Function AxmContiSetProfileMode Lib "AXL.dll" (ByVal lCoord As Long, ByVal uProfileMode As Long) As Long
    ' ������ ��ǥ���� ���� �ӵ� �������� ��带 ��ȯ�Ѵ�.
    Public Declare Function AxmContiGetProfileMode Lib "AXL.dll" (ByVal lCoord As Long, ByRef upProfileMode As Long) As Long

    '========== DIO ���ͷ�Ʈ �÷��� ������Ʈ �б�
    ' ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� bit ������ ���ͷ�Ʈ �߻� ���� ���� ����
    Public Declare Function AxdiInterruptFlagReadBit Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lOffset As Long, ByRef upValue As Long) As Long
    ' ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� byte ������ ���ͷ�Ʈ �߻� ���� ���� ����
    Public Declare Function AxdiInterruptFlagReadByte Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lOffset As Long, ByRef upValue As Long) As Long
    ' ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� word ������ ���ͷ�Ʈ �߻� ���� ���� ����
    Public Declare Function AxdiInterruptFlagReadWord Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lOffset As Long, ByRef upValue As Long) As Long
    ' ������ �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� double word ������ ���ͷ�Ʈ �߻� ���� ���� ����
    Public Declare Function AxdiInterruptFlagReadDword Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lOffset As Long, ByRef upValue As Long) As Long
    ' ��ü �Է� ���� ���, Interrupt Flag Register�� Offset ��ġ���� bit ������ ���ͷ�Ʈ �߻� ���� ���� ����
    Public Declare Function AxdiInterruptFlagRead Lib "AXL.dll" (ByVal lOffset As Long, ByRef upValue As Long) As Long

    '========= �α� ���� �Լ� ==========================================================================================
    ' ���� �ڵ����� ������.
    ' ���� ���� �Լ� ���� ����� EzSpy���� ����͸� �� �� �ֵ��� ���� �Ǵ� �����ϴ� �Լ��̴�.
    ' uUse : ��� ���� => DISABLE(0), ENABLE(1)
    Public Declare Function AxmLogSetAxis Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal uUse As Long) As Long

    ' EzSpy������ ���� �� �Լ� ���� ��� ����͸� ���θ� Ȯ���ϴ� �Լ��̴�.
    Public Declare Function AxmLogGetAxis Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upUse As Long) As Long

    '=========== �α� ��� ���� �Լ�
    '������ �Է� ä���� EzSpy�� �α� ��� ���θ� �����Ѵ�.
    Public Declare Function AxaiLogSetChannel Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal uUse As Long) As Long
    '������ �Է� ä���� EzSpy�� �α� ��� ���θ� Ȯ���Ѵ�.
    Public Declare Function AxaiLogGetChannel Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef upUse As Long) As Long

    '==������ ��� ä���� EzSpy �α� ���
    '������ ��� ä���� EzSpy�� �α� ��� ���θ� �����Ѵ�.
    Public Declare Function AxaoLogSetChannel Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal uUse As Long) As Long
    '������ ��� ä���� EzSpy�� �α� ��� ���θ� Ȯ���Ѵ�.
    Public Declare Function AxaoLogGetChannel Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef upUse As Long) As Long

    '==Log
    ' ������ ����� EzSpy�� �α� ��� ���� ����
    Public Declare Function AxdLogSetModule Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal uUse As Long) As Long
    ' ������ ����� EzSpy�� �α� ��� ���� Ȯ��
    Public Declare Function AxdLogGetModule Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef upUse As Long) As Long

    ' ������ ���尡 RTEX ����� �� �� ������ firmware ������ Ȯ���Ѵ�.
    Public Declare Function AxlGetFirmwareVersion Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef szVersion As String) As Long
    ' ������ ����� Firmware�� ���� �Ѵ�.
    Public Declare Function AxlSetFirmwareCopy Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef wData As Long, ByRef wCmdData As Long) As Long
    ' ������ ����� Firmware Update�� �����Ѵ�.
    Public Declare Function AxlSetFirmwareUpdate Lib "AXL.dll" (ByVal lBoardNo As Long) As Long
    ' ������ ������ ���� RTEX �ʱ�ȭ ���¸� Ȯ�� �Ѵ�.
    Public Declare Function AxlCheckStatus Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwStatus As Long) As Long
    ' ������ �࿡ RTEX Master board�� ���� ����� ���� �մϴ�.
    Public Declare Function AxlRtexUniversalCmd Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wCmd As Long, ByVal wOffset As Long, ByRef wData As Long) As Long
    ' ������ ���� RTEX ��� ����� �����Ѵ�.
    Public Declare Function AxmRtexSlaveCmd Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwCmdCode As Long, ByVal dwTypeCode As Long, ByVal dwIndexCode As Long, ByVal dwCmdConfigure As Long, ByVal dwValue As Long) As Long
    ' ������ �࿡ ������ RTEX ��� ����� ������� Ȯ���Ѵ�.
    Public Declare Function AxmRtexGetSlaveCmdResult Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwIndex As Long, ByRef dwValue As Long) As Long
    ' ������ �࿡ ������ RTEX ��� ����� ������� Ȯ���Ѵ�. PCIE-Rxx04-RTEX ����
    Public Declare Function AxmRtexGetSlaveCmdResultEx Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpCommand As Long, ByRef dwpType As Long, ByRef dwpIndex As Long, ByRef dwpValue As Long) As Long
    ' ������ �࿡ RTEX ���� ������ Ȯ���Ѵ�.
    Public Declare Function AxmRtexGetAxisStatus Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwStatus As Long) As Long
    ' ������ �࿡ RTEX ��� ���� ������ Ȯ���Ѵ�.(Actual position, Velocity, Torque)
    Public Declare Function AxmRtexGetAxisReturnData Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwReturn1 As Long, ByRef dwReturn2 As Long, ByRef dwReturn3 As Long) As Long
    ' ������ �࿡ RTEX Slave ���� ���� ���� ������ Ȯ���Ѵ�.(mechanical, Inposition and etc)
    Public Declare Function AxmRtexGetAxisSlaveStatus Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwStatus As Long) As Long

    ' ������ �࿡ MLII Slave �࿡ ���� ��Ʈ�� ��ɾ �����Ѵ�.
    Public Declare Function AxmSetAxisCmd Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef tagCommand As Long) As Long
    ' ������ �࿡ MLII Slave �࿡ ���� ��Ʈ�� ����� ����� Ȯ���Ѵ�.
    Public Declare Function AxmGetAxisCmdResult Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef tagCommand As Long) As Long

    ' ������ SIIIH Slave ��⿡ ��Ʈ�� ����� ����� �����ϰ� ��ȯ �Ѵ�.
    Public Declare Function AxdSetAndGetSlaveCmdResult Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef tagSetCommand As Long, ByRef tagGetCommand As Long) As Long
    Public Declare Function AxaSetAndGetSlaveCmdResult Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef tagSetCommand As Long, ByRef tagGetCommand As Long) As Long
    Public Declare Function AxcSetAndGetSlaveCmdResult Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef tagSetCommand As Long, ByRef tagGetCommand As Long) As Long

    ' DPRAM �����͸� Ȯ���Ѵ�.
    Public Declare Function AxlGetDpRamData Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wAddress As Long, ByRef dwpRdData As Long) As Long
    ' DPRAM �����͸� Word������ Ȯ���Ѵ�.
    Public Declare Function AxlBoardReadDpramWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByRef dwpRdData As Long) As Long
    ' DPRAM �����͸� Word������ �����Ѵ�.
    Public Declare Function AxlBoardWriteDpramWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByVal dwWrData As Long) As Long

    ' �� ������ �� SLAVE���� ����� �����Ѵ�.
    Public Declare Function AxlSetSendBoardEachCommand Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwCommand As Long, ByRef dwpSendData As Long, ByVal dwLength As Long) As Long
    ' �� ����� ����� �����Ѵ�.
    Public Declare Function AxlSetSendBoardCommand Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwCommand As Long, ByRef dwpSendData As Long, ByVal dwLength As Long) As Long
    ' �� ������ ������ Ȯ���Ѵ�.
    Public Declare Function AxlGetResponseBoardCommand Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwpReadData As Long) As Long

    ' Network Type Master ���忡�� Slave ���� Firmware Version�� �о� ���� �Լ�.
    ' ucaFirmwareVersion unsigned char ���� Array�� �����ϰ� ũ�Ⱑ 4�̻��� �ǵ��� ���� �ؾ� �Ѵ�.
    Public Declare Function AxmInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef ucaFirmwareVersion As Long) As Long
    Public Declare Function AxaInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef ucaFirmwareVersion As Long) As Long
    Public Declare Function AxdInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef ucaFirmwareVersion As Long) As Long
    Public Declare Function AxcInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef ucaFirmwareVersion As Long) As Long

    '======== PCI-R1604-MLII ���� �Լ�===========================================================================
    ' INTERPOLATE and LATCH Command�� Option Field�� Torq Feed Forward�� ���� ���� �ϵ��� �մϴ�.
    ' �⺻���� MAX�� �����Ǿ� �ֽ��ϴ�.
    ' �������� 0 ~ 4000H���� ���� �� �� �ֽ��ϴ�.
    ' �������� 4000H�̻����� �����ϸ� ������ �� �̻����� �����ǳ� ������ 4000H���� ���� �˴ϴ�.
    Public Declare Function AxmSetTorqFeedForward Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwTorqFeedForward As Long) As Long

    ' INTERPOLATE and LATCH Command�� Option Field�� Torq Feed Forward�� ���� �о���� �Լ� �Դϴ�.
    ' �⺻���� MAX�� �����Ǿ� �ֽ��ϴ�.
    Public Declare Function AxmGetTorqFeedForward Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpTorqFeedForward As Long) As Long

    ' INTERPOLATE and LATCH Command�� VFF Field�� Velocity Feed Forward�� ���� ���� �ϵ��� �մϴ�.
    ' �⺻���� '0'�� �����Ǿ� �ֽ��ϴ�.
    ' �������� 0 ~ FFFFH���� ���� �� �� �ֽ��ϴ�.
    Public Declare Function AxmSetVelocityFeedForward Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwVelocityFeedForward As Long) As Long

    ' INTERPOLATE and LATCH Command�� VFF Field�� Velocity Feed Forward�� ���� �о���� �Լ� �Դϴ�.
    Public Declare Function AxmGetVelocityFeedForward Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpVelocityFeedForward As Long) As Long

    ' Encoder type�� �����Ѵ�.
    ' �⺻���� 0(TYPE_INCREMENTAL)�� �����Ǿ� �ֽ��ϴ�.
    ' �������� 0 ~ 1���� ���� �� �� �ֽ��ϴ�.
    ' ������ : 0(TYPE_INCREMENTAL), 1(TYPE_ABSOLUTE).
    Public Declare Function AxmSignalSetEncoderType Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwEncoderType As Long) As Long

    ' Encoder type�� Ȯ���Ѵ�.
    Public Declare Function AxmSignalGetEncoderType Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpEncoderType As Long) As Long
    '========================================================================================================

    ' Slave Firmware Update�� ���� �߰�
    'DWORD   __stdcall AxmSetSendAxisCommand(long lAxisNo, WORD wCommand, WORD* wpSendData, WORD wLength);

    '======== PCI-R1604-RTEX, RTEX-PM ���� �Լ�==============================================================
    ' ���� �Է� 2,3�� �Է½� JOG ���� �ӵ��� �����Ѵ�.
    ' ������ ���õ� ��� ����(Ex, PulseOutMethod, MoveUnitPerPulse ��)���� �Ϸ�� ���� �ѹ��� �����Ͽ��� �Ѵ�.
    Public Declare Function AxmMotSetUserMotion Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Long

    ' ���� �Է� 2,3�� �Է½� JOG ���� ���� ��� ���θ� �����Ѵ�.
    ' ������ :  0(DISABLE), 1(ENABLE)
    Public Declare Function AxmMotSetUserMotionUsage Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwUsage As Long) As Long

    ' MPGP �Է��� ����Ͽ� Load/UnLoad ��ġ�� �ڵ����� �̵��ϴ� ��� ����.
    Public Declare Function AxmMotSetUserPosMotion Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal dLoadPos As Double, ByVal dUnLoadPos As Double, ByVal dwFilter As Long, ByVal dwDelay As Long) As Long

    ' MPGP �Է��� ����Ͽ� Load/UnLoad ��ġ�� �ڵ����� �̵��ϴ� ��� ����.
    ' ������ :  0(DISABLE), 1(Position ��� A ���), 2(Position ��� B ���)
    Public Declare Function AxmMotSetUserPosMotionUsage Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwUsage As Long) As Long
    '========================================================================================================

    '======== SIO-CN2CH/HPC4, ���� ��ġ Ʈ���� ��� ��� ���� �Լ�================================================
    ' �޸� ������ ���� �Լ�
    Public Declare Function AxcKeWriteRamDataAddr Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwAddr As Long, ByVal dwData As Long) As Long
    ' �޸� ������ �б� �Լ�
    Public Declare Function AxcKeReadRamDataAddr Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwAddr As Long, ByRef dwpData As Long) As Long
    ' �޸� �ʱ�ȭ �Լ�
    Public Declare Function AxcKeResetRamDataAll Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal dwData As Long) As Long
    ' Ʈ���� Ÿ�� �ƿ� ���� �Լ�
    Public Declare Function AxcTriggerSetTimeout Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwTimeout As Long) As Long
    ' Ʈ���� Ÿ�� �ƿ� Ȯ�� �Լ�
    Public Declare Function AxcTriggerGetTimeout Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpTimeout As Long) As Long
    ' Ʈ���� ��� ���� Ȯ�� �Լ�
    Public Declare Function AxcStatusGetWaitState Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpState As Long) As Long
    ' Ʈ���� ��� ���� ���� �Լ�
    Public Declare Function AxcStatusSetWaitState Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwState As Long) As Long

    ' ���� ä�ο� ��ɾ� ����.
    Public Declare Function AxcKeSetCommandData32 Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwCommand As Long, ByVal dwData As Long) As Long
    ' ���� ä�ο� ��ɾ� ����.
    Public Declare Function AxcKeSetCommandData16 Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwCommand As Long, ByVal wData As Long) As Long
    ' ���� ä���� �������� Ȯ��.
    Public Declare Function AxcKeGetCommandData32 Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwCommand As Long, ByRef dwpData As Long) As Long
    ' ���� ä���� �������� Ȯ��.
    Public Declare Function AxcKeGetCommandData16 Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwCommand As Long, ByRef wpData As Long) As Long
    '========================================================================================================

    '======== PCI-N804/N404 ����, Sequence Motion ===================================================================
    ' Sequence Motion�� �� ������ ���� �մϴ�. (�ּ� 1��)
    ' lSeqMapNo : �� ��ȣ ������ ��� Sequence Motion Index Point
    ' lSeqMapSize : �� ��ȣ ����
    ' long* LSeqAxesNo : �� ��ȣ �迭
    Public Declare Function AxmSeqSetAxisMap Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByVal lSeqMapSize As Long, ByRef lSeqAxesNo As Long) As Long
    Public Declare Function AxmSeqGetAxisMap Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByRef lSeqMapSize As Long, ByRef lSeqAxesNo As Long) As Long

    ' Sequence Motion�� ����(Master) ���� ���� �մϴ�.
    ' �ݵ�� AxmSeqSetAxisMap(...) �� ������ �� ������ �����Ͽ��� �մϴ�.
    Public Declare Function AxmSeqSetMasterAxisNo Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByVal lMasterAxisNo As Long) As Long

    ' Sequence Motion�� Node ���� ������ ���̺귯���� �˸��ϴ�.
    Public Declare Function AxmSeqBeginNode Lib "AXL.dll" (ByVal lSeqMapNo As Long) As Long

    ' Sequence Motion�� Node ���� ���Ḧ ���̺귯���� �˸��ϴ�.
    Public Declare Function AxmSeqEndNode Lib "AXL.dll" (ByVal lSeqMapNo As Long) As Long

    ' Sequence Motion�� ������ ���� �մϴ�.
    Public Declare Function AxmSeqStart Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByVal dwStartOption As Long) As Long

    ' Sequence Motion�� �� Profile Node ������ ���̺귯���� �Է� �մϴ�.
    ' ���� 1�� Sequence Motion�� ����ϴ���, *dPosition�� 1���� Array�� �����Ͽ� �ֽñ� �ٶ��ϴ�.
    Public Declare Function AxmSeqAddNode Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByRef dPosition As Double, ByVal dVelocity As Double, ByVal dAcceleration As Double, ByVal dDeceleration As Double, ByVal dNextVelocity As Double) As Long

    ' Sequence Motion�� ���� �� ���� ���� ���� Node Index�� �˷� �ݴϴ�.
    Public Declare Function AxmSeqGetNodeNum Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByRef lCurNodeNo As Long) As Long

    ' Sequence Motion�� �� Node Count�� Ȯ�� �մϴ�.
    Public Declare Function AxmSeqGetTotalNodeNum Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByRef lTotalNodeCnt As Long) As Long

    ' Sequence Motion�� ���� ���� ������ Ȯ�� �մϴ�.
    ' dwInMotion : 0(���� ����), 1(���� ��)
    Public Declare Function AxmSeqIsMotion Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByRef dwInMotion As Long) As Long

    ' Sequence Motion�� Memory�� Clear �մϴ�.
    ' AxmSeqSetAxisMap(...), AxmSeqSetMasterAxisNo(...) ���� ������ ���� �����˴ϴ�.
    Public Declare Function AxmSeqWriteClear Lib "AXL.dll" (ByVal lSeqMapNo As Long) As Long

    ' Sequence Motion�� ������ ���� �մϴ�.
    ' dwStopMode : 0(EMERGENCY_STOP), 1(SLOWDOWN_STOP)
    Public Declare Function AxmSeqStop Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByVal dwStopMode As Long) As Long
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
    Public Declare Function AxmStatusSetMon Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwParaNo1 As Long, ByVal dwParaNo2 As Long, ByVal dwParaNo3 As Long, ByVal dwParaNo4 As Long, ByVal dwUse As Long) As Long
    Public Declare Function AxmStatusGetMon Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpParaNo1 As Long, ByRef dwpParaNo2 As Long, ByRef dwpParaNo3 As Long, ByRef dwpParaNo4 As Long, ByRef dwpUse As Long) As Long
    Public Declare Function AxmStatusReadMon Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpParaNo1 As Long, ByRef dwpParaNo2 As Long, ByRef dwpParaNo3 As Long, ByRef dwpParaNo4 As Long, ByRef dwDataVaild As Long) As Long
    Public Declare Function AxmStatusReadMonEx Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef lpDataCnt As Long, ByRef dwpReadData As Long) As Long
    '=============================================================================================================

    '======== PCI-R32IOEV-RTEX ���� �Լ�===========================================================================
    ' I/O ��Ʈ�� �Ҵ�� HPI register �� �а� �������� API �Լ�.
    ' I/O Registers for HOST interface.
    ' I/O 00h Host status register (HSR)
    ' I/O 04h Host-to-DSP control register (HDCR)
    ' I/O 08h DSP page register (DSPP)
    ' I/O 0Ch Reserved
    Public Declare Function AxlSetIoPort Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwAddr As Long, ByVal dwData As Long) As Long
    Public Declare Function AxlGetIoPort Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwAddr As Long, ByRef dwpData As Long) As Long

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
    Public Declare Function AxlM3SetFWUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwTotalPacketSize As Long, ByVal dwProcTotalStepNo As Long) As Long
    ' M-III Master ���� �߿��� ������Ʈ �⺻ ���� ���� ��� Ȯ�� �Լ�
    Public Declare Function AxlM3GetFWUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwTotalPacketSize As Long, ByRef dwProcTotalStepNo As Long) As Long

    ' M-III Master ���� �߿��� ������Ʈ �ڷ� ���� �Լ�
    Public Declare Function AxlM3SetFWUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef pdwPacketData As Long, ByVal dwPacketSize As Long) As Long
    ' M-III Master ���� �߿��� ������Ʈ �ڷ� ���� ��� Ȯ�� �Լ�
    Public Declare Function AxlM3GetFWUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwPacketSize As Long) As Long

    ' M-III Master ���� �߿��� ������Ʈ ����
    Public Declare Function AxlM3SetFWUpdate Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwFlashBurnStepNo As Long) As Long
    ' M-III Master ���� �߿��� ������Ʈ ���� ��� Ȯ��
    Public Declare Function AxlM3GetFWUpdate Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwFlashBurnStepNo As Long, ByRef dwIsFlashBurnDone As Long) As Long

    ' M-III Master ���� EEPROM ������ ���� �Լ�
    Public Declare Function AxlM3SetCFGData Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef pCmdData As Long, ByVal CmdDataSize As Long) As Long
    ' M-III Master ���� EEPROM ������ �������� �Լ�
    Public Declare Function AxlM3GetCFGData Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef pCmdData As Long, ByVal CmdDataSize As Long) As Long

    ' M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� �Լ�
    Public Declare Function AxlM3SetMCParaUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wCh0Slaves As Long, ByVal wCh1Slaves As Long, ByVal dwCh0CycTime As Long, ByVal dwCh1CycTime As Long, ByVal dwChInfoMaxRetry As Long) As Long
    ' M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� ��� Ȯ�� �Լ�
    Public Declare Function AxlM3GetMCParaUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef wCh0Slaves As Long, ByRef wCh1Slaves As Long, ByRef dwCh0CycTime As Long, ByRef dwCh1CycTime As Long, ByRef dwChInfoMaxRetry As Long) As Long
    ' M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� �Լ�
    Public Declare Function AxlM3SetMCParaUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wIdx As Long, ByVal wChannel As Long, ByVal wSlaveAddr As Long, ByVal dwProtoCalType As Long, ByVal dwTransBytes As Long, ByVal dwDeviceCode As Long) As Long
    ' M-III Master ���� CONNECT PARAMETER �⺻ ���� ���� ��� Ȯ�� �Լ�
    Public Declare Function AxlM3GetMCParaUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wIdx As Long, ByRef wChannel As Long, ByRef wSlaveAddr As Long, ByRef dwProtoCalType As Long, ByRef dwTransBytes As Long, ByRef dwDeviceCode As Long) As Long

    ' M-III Master ���峻�� �������͸� DWord������ Ȯ�� �Լ�
    Public Declare Function AxlBoardReadDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByRef dwData As Long) As Long
    ' M-III Master ���峻�� �������͸� DWord������ ���� �Լ�
    Public Declare Function AxlBoardWriteDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByVal dwData As Long) As Long

    ' ���峻�� Ȯ�� �������͸� DWord������ ���� �� Ȯ���Ѵ�.
    Public Declare Function AxlBoardReadDWordEx Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwOffset As Long, ByRef dwData As Long) As Long
    Public Declare Function AxlBoardWriteDWordEx Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwOffset As Long, ByVal dwData As Long) As Long

    ' ������ ���� ���� ���� �Լ�
    Public Declare Function AxmM3ServoSetCtrlStopMode Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bStopMode As Byte) As Long
    ' ������ Lt ���� ���·� ���� �Լ�
    Public Declare Function AxmM3ServoSetCtrlLtSel Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bLtSel1 As Byte, ByVal bLtSel2 As Byte) As Long
    ' ������ IO �Է� ���¸� Ȯ�� �Լ�
    Public Declare Function AxmStatusReadServoCmdIOInput Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upStatus As Long) As Long
    ' ������ ���� ���� �Լ�
    Public Declare Function AxmM3ServoExInterpolate Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwTPOS As Long, ByVal dwVFF As Long, ByVal dwTFF As Long, ByVal dwTLIM As Long, ByVal dwExSig1 As Long, ByVal dwExSig2 As Long) As Long
    ' ���� �������� ���̾ ���� �Լ�
    Public Declare Function AxmM3ServoSetExpoAccBias Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wBias As Long) As Long
    ' ���� �������� �ð� ���� �Լ�
    Public Declare Function AxmM3ServoSetExpoAccTime Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wTime As Long) As Long
    ' ������ �̵� �ð��� ���� �Լ�
    Public Declare Function AxmM3ServoSetMoveAvrTime Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wTime As Long) As Long
    ' ������ Acc ���� ���� �Լ�
    Public Declare Function AxmM3ServoSetAccFilter Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bAccFil As Byte) As Long
    ' ������ ���� �����1 ���� �Լ�
    Public Declare Function AxmM3ServoSetCprmMonitor1 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bMonSel As Byte) As Long
    ' ������ ���� �����2 ���� �Լ�
    Public Declare Function AxmM3ServoSetCprmMonitor2 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bMonSel As Byte) As Long
    ' ������ ���� �����1 Ȯ�� �Լ�
    Public Declare Function AxmM3ServoStatusReadCprmMonitor1 Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upStatus As Long) As Long
    ' ������ ���� �����2 Ȯ�� �Լ�
    Public Declare Function AxmM3ServoStatusReadCprmMonitor2 Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upStatus As Long) As Long
    ' ���� �������� Dec ���� �Լ�
    Public Declare Function AxmM3ServoSetAccDec Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wAcc1 As Long, ByVal wAcc2 As Long, ByVal wAccSW As Long, ByVal wDec1 As Long, ByVal wDec2 As Long, ByVal wDecSW As Long) As Long
    ' ���� ���� ���� �Լ�
    Public Declare Function AxmM3ServoSetStop Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal lMaxDecel As Long) As Long

    '========== ǥ�� I/O ��� ���� Ŀ�ǵ� =========================================================================
    ' Network��ǰ �� �����̺� ����� �Ķ���� ���� ���� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationParameter Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wNo As Long, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Long
    ' Network��ǰ �� �����̺� ����� �Ķ���� ���� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationParameter Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wNo As Long, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Long
    ' Network��ǰ �� �����̺� ����� ID���� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationIdRd Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bIdCode As Byte, ByVal bOffset As Byte, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Long
    ' Network��ǰ �� �����̺� ����� ��ȿ Ŀ�ǵ�� ����ϴ� �Լ�
    Public Declare Function AxlM3SetStationNop Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte) As Long
    ' Network��ǰ �� �����̺� ����� �¾��� �ǽ��ϴ� �Լ�
    Public Declare Function AxlM3SetStationConfig Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bConfigMode As Byte, ByVal bModuleType As Byte) As Long
    ' Network��ǰ �� �����̺� ����� �˶� �� ��� ���� ���� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationAlarm Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wAlarmRdMod As Long, ByVal wAlarmIndex As Long, ByVal bModuleType As Byte, ByRef pwAlarmData As Long) As Long
    ' Network��ǰ �� �����̺� ����� �˶� �� ��� ���¸� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationAlarmClear Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wAlarmClrMod As Long, ByVal bModuleType As Byte) As Long
    ' Network��ǰ �� �����̺� ������ ��������� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationSyncSet Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte) As Long
    ' Network��ǰ �� �����̺� ������ ������ �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationConnect Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bVer As Byte, ByVal bComMode As Byte, ByVal bComTime As Byte, ByVal bProfileType As Byte, ByVal bModuleType As Byte) As Long
    ' Network��ǰ �� �����̺� ������ ���� ������ �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationDisConnect Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte) As Long
    ' Network��ǰ �� �����̺� ����� ���ֹ߼� �Ķ���� ���� ���� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationStoredParameter Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wNo As Long, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Long
    ' Network��ǰ �� �����̺� ����� ���ֹ߼� �Ķ���� ���� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationStoredParameter Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wNo As Long, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Long
    ' Network��ǰ �� �����̺� ����� �޸� ���� ���� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationMemory Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wSize As Long, ByVal dwAddress As Long, ByVal bModuleType As Byte, ByVal bMode As Byte, ByVal bDataType As Byte, ByRef pbData As Byte) As Long
    ' Network��ǰ �� �����̺� ����� �޸� ���� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationMemory Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wSize As Long, ByVal dwAddress As Long, ByVal bModuleType As Byte, ByVal bMode As Byte, ByVal bDataType As Byte, ByRef pbData As Byte) As Long

    '========== ǥ�� I/O ��� Ŀ�ؼ� Ŀ�ǵ� =========================================================================
    ' Network��ǰ �� �������� �����̺� ����� �ڵ� �＼�� ��� ���� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationAccessMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByVal bRWSMode As Byte) As Long
    ' Network��ǰ �� �������� �����̺� ����� �ڵ� �＼�� ��� �������� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationAccessMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef bRWSMode As Byte) As Long
    ' Network��ǰ �� �����̺� ����� ���� �ڵ� ���� ��带 �����ϴ� �Լ�
    Public Declare Function AxlM3SetAutoSyncConnectMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByVal dwAutoSyncConnectMode As Long) As Long
    ' Network��ǰ �� �����̺� ����� ���� �ڵ� ���� ��� �������� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetAutoSyncConnectMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef dwpAutoSyncConnectMode As Long) As Long
    ' Network��ǰ �� �����̺� ��⿡ ���� ���� ����ȭ ������ �����ϴ� �Լ�
    Public Declare Function AxlM3SyncConnectSingle Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte) As Long
    ' Network��ǰ �� �����̺� ��⿡ ���� ���� ����ȭ ���� ������ �����ϴ� �Լ�
    Public Declare Function AxlM3SyncDisconnectSingle Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte) As Long
    ' Network��ǰ �� �����̺� ������ ���� ���¸� Ȯ���ϴ� �Լ�
    Public Declare Function AxlM3IsOnLine Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByRef dwData As Long) As Long

    '========== ǥ�� I/O �������� Ŀ�ǵ� =========================================================================
    ' Network��ǰ �� ����ȭ ������ �����̺� I/O ��⿡ ���� ������ �������� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationRWS Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef pdwParam As Long, ByVal bSize As Byte) As Long
    ' Network��ǰ �� ����ȭ ������ �����̺� I/O ��⿡ ���� �����Ͱ��� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationRWS Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef pdwParam As Long, ByVal bSize As Byte) As Long
    ' Network��ǰ �� �񵿱�ȭ ������ �����̺� I/O ��⿡ ���� ������ �������� ��ȯ�ϴ� �Լ�
    Public Declare Function AxlM3GetStationRWA Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef pdwParam As Long, ByVal bSize As Byte) As Long
    ' Network��ǰ �� �񵿱�ȭ ������ �����̺� I/O ��⿡ ���� �����Ͱ��� �����ϴ� �Լ�
    Public Declare Function AxlM3SetStationRWA Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef pdwParam As Long, ByVal bSize As Byte) As Long

    ' MLIII adjustment operation�� ���� �Ѵ�.
    ' dwReqCode == 0x1005 : parameter initialization : 20sec
    ' dwReqCode == 0x1008 : absolute encoder reset   : 5sec
    ' dwReqCode == 0x100E : automatic offset adjustment of motor current detection signals  : 5sec
    ' dwReqCode == 0x1013 : Multiturn limit setting  : 5sec
    Public Declare Function AxmM3AdjustmentOperation Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwReqCode As Long) As Long

    ' M3 ���� ���� �˻� ���� ���� ���ܿ� �Լ��̴�.
    Public Declare Function AxmHomeGetM3FWRealRate Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upHomeMainStepNumber As Long, ByRef upHomeSubStepNumber As Long, ByRef upHomeLastMainStepNumber As Long, ByRef upHomeLastSubStepNumber As Long) As Long
    ' M3 ���� ���� �˻��� ���������� Ż��� �����Ǵ� ��ġ ���� ��ȯ�ϴ� �Լ��̴�.
    Public Declare Function AxmHomeGetM3OffsetAvoideSenArea Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dPos As Double) As Long
    ' M3 ���� ���� �˻��� ���������� Ż��� �����Ǵ� ��ġ ���� �����ϴ� �Լ��̴�.
    ' dPos ���� ���� 0�̸� �ڵ����� Ż��� �����Ǵ� ��ġ ���� �ڵ����� �����ȴ�.
    ' dPos ���� ���� ����� ���� �Է��Ѵ�.
    Public Declare Function AxmHomeSetM3OffsetAvoideSenArea Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPos As Double) As Long

    ' M3 ����, ����ġ ���ڴ� ��� ����, �����˻� �Ϸ� �� CMD/ACT POS �ʱ�ȭ ���� ����
    ' dwSel: 0, ���� �˻��� CMD/ACTPOS 0���� ������.[�ʱⰪ]
    ' dwSel: 1, ���� �˻��� CMD/ACTPOS ���� �������� ����.
    Public Declare Function AxmM3SetAbsEncOrgResetDisable Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwSel As Long) As Long

    ' M3 ����, ����ġ ���ڴ� ��� ����, �����˻� �Ϸ� �� CMD/ACT POS �ʱ�ȭ ���� ������ ��������
    ' upSel: 0, ���� �˻��� CMD/ACTPOS 0���� ������.[�ʱⰪ]
    ' upSel: 1, ���� �˻��� CMD/ACTPOS ���� �������� ����.
    Public Declare Function AxmM3GetAbsEncOrgResetDisable Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upSel As Long) As Long

    ' M3 ����, �����̺� OFFLINE ��ȯ�� �˶� ���� ��� ��� ���� ����
    ' dwSel: 0, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ������� ����.[�ʱⰪ]
    ' dwSel: 1, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ���

    Public Declare Function AxmM3SetOfflineAlarmEnable Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwSel As Long) As Long
    ' M3 ����, �����̺� OFFLINE ��ȯ�� �˶� ���� ��� ��� ���� ���� �� ��������
    ' upSel: 0, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ������� ����.[�ʱⰪ]
    ' upSel: 1, ML3 �����̺� ONLINE->OFFLINE �˶� ó�� ���

    Public Declare Function AxmM3GetOfflineAlarmEnable Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upSel As Long) As Long

    ' M3 ����, �����̺� OFFLINE ��ȯ ���� ���� �� ��������
    ' upSel: 0, ML3 �����̺� ONLINE->OFFLINE ��ȯ���� ����
    ' upSel: 1, ML3 �����̺� ONLINE->OFFLINE ��ȯ�Ǿ���.
    Public Declare Function AxmM3ReadOnlineToOfflineStatus Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upStatus As Long) As Long

    ' Network ��ǰ�� Configuration Lock ���¸� �����Ѵ�.
    ' wLockMode  : DISABLE(0), ENABLE(1)
    Public Declare Function AxlSetLockMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wLockMode As Long) As Long

    ' Lock ������ ����
    Public Declare Function AxlSetLockData Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwTotalNodeNum As Long, ByRef dwpNodeNo As Long, ByRef dwpNodeID As Long, ByRef dwpLockData As Long) As Long

    Public Declare Function AxmMoveStartPosWithAVC Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPosition As Double, ByVal dMaxVelocity As Double, ByVal dMaxAccel As Double, ByVal dMinJerk As Double, ByRef dpMoveVelocity As Double, ByRef dpMoveAccel As Double, ByRef dpMoveJerk As Double) As Long
    ' ī���� ����� 2-D ������ġ Ʈ���� ����� ���� �ʿ��� Ʈ���� ��ġ ������ �����Ѵ�.
    ' lChannelNo : 0,1 channel �� ��� 0, 2,3 channel �� ��� 2 �� ����.
    ' nDataCnt :
    '  nDataCnt > 0 : ������ ���, nDataCnt <= 0 : ��ϵ� ������ �ʱ�ȭ.
    ' dwOption : Reserved.
    ' dpPatternData : (X1, Y1)
    Public Declare Function AxcTriggerSetPatternData Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal nDataCnt As Long, ByVal dwOption As Long, ByRef dpPatternData As Double) As Long
    ' ī���� ����� 2-D ������ġ Ʈ���� ����� ���� �ʿ��� Ʈ���� ��ġ ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPatternData Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef npDataCnt As Long, ByRef dwpOption As Long, ByRef dpPatternData As Double) As Long

    '���� ���� �����Ͽ� AxmContiEndNode �Լ������� ������������ Node �� Data Queue �� �̸� ä������ �� �ֵ����ϴ� ����� Ȱ��ȭ �Ѵ�.
    'bPushPrevContiQueue : 1  �ش� ��� Ȱ��ȭ
    'bPushPrevContiQueue : 0  �ش� ��� ��Ȱ��ȭ
    Public Declare Function AxmContiSetPushPrevContiQueueEnable Lib "AXL.dll" (ByVal lCoordinate As Long, ByVal bPushPrevContiQueue As Byte) As Long
    '�����ص� AxmContiSetPushPrevContiQueueEnable Flag���� ��ȯ�Ѵ�.
    Public Declare Function AxmContiGetPushPrevContiQueueEnable Lib "AXL.dll" (ByVal lCoordinate As Long, ByRef bPushPrevContiQueue As BOOL*) As Long

    ' ���Ӻ��� ���� �� Data Queue �� Node ������ ����Ǿ����� ���¸� ��ȯ�Ѵ�.
    ' AxmContiSetPushPrevContiQueueEnable(long lCoordinate, 1) �� �����Ǿ����� ��츸 ��ȿ
    ' bPushPrevContiQueueComplete : 1  Node Data ���� �Ϸ�
    ' bPushPrevContiQueueComplete : 0  Node Data ���� �Ǿ���������
    Public Declare Function AxmContiGetPushPrevContiQueueComplete Lib "AXL.dll" (ByVal lCoordinate As Long, ByRef bPushPrevContiQueueComplete As BOOL*) As Long

    ' ���Ӻ��� ���� �� ù ��� ���� �� ������ ��� ���� �� �����ð� ���� ������ ��ǥ���� ������ ���� OutputBit On/Off ����
    ' AxmContiBeginNode �տ� ȣ���ؾ� �Ѵ�. �ѹ� �����ϸ� Flag�� �ʱ�ȭ�Ǿ� �ٽ� ȣ���ؾ� ����� �� �ִ�.
    ' StartTime/EndTime ������ [Sec]�̸�, 0 ~ 6.5�ʱ��� ���� �����ϴ�.
    ' uOnoff : 0 - ���� ��ġ���� Bit On ���� ��ġ���� Bit Off
    '          : 1 - ���� ��ġ���� Bit Off ���� ��ġ���� Bit On
    ' lEndMode : 0 - ������ ��� ���� ���� �� ��� OutputBit Off/On
    '   : 1 - ������ ��� ���� ���� �� �Է��� EndTime ���� OutputBit Off/On
    '   : 2 - ���� ���� �� OutputBit On/Off �� �Է��� EndTime ���� OutputBit Off/On
    Public Declare Function AxmContiSetWriteOutputBit Lib "AXL.dll" (ByVal lCoordinate As Long, ByVal dStartTime As Double, ByVal dEndTime As Double, ByVal lBitNo As Long, ByVal uOnoff As Long, ByVal lEndMode As Long) As Long

    ' AxmContiSetWriteOutputBit�� ������ ������ ��ȯ�Ѵ�.
    Public Declare Function AxmContiGetWriteOutputBit Lib "AXL.dll" (ByVal lCoordinate As Long, ByRef dpStartTime As Double, ByRef dpEndTime As Double, ByRef lpBitNo As Long, ByRef lpOnoff As Long, ByRef lpEndMode As Long) As Long

    ' AxmContiSetWriteOutputBit�� ������ ������ �����Ѵ�.
    Public Declare Function AxmContiResetWriteOutputBit Lib "AXL.dll" (ByVal lCoordinate As Long) As Long

    ' AxmMoveTorqueStop �Լ��� ��ũ ���� ���� �� CmdPos ���� ActPos ���� ��ġ��Ű�� ���������� ��� �ð��� �����Ѵ�.
    ' dwSettlingTime
    '  1) ����: [msec]
    '  2) �Է� ���� ����: 0 ~ 10000
    '  *����* AxmMoveTorqueSetStopSettlingTime �Լ��� ��� �ð��� �������� ������, dafault ���� 10[msec]�� ����ȴ�.
    Public Declare Function AxmMoveTorqueSetStopSettlingTime Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwSettlingTime As Long) As Long
    ' AxmMoveTorqueStop �Լ��� ��ũ ���� ���� �� CmdPos ���� ActPos ���� ��ġ��Ű�� ���������� ��� �ð��� ��ȯ�Ѵ�.
    Public Declare Function AxmMoveTorqueGetStopSettlingTime Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpSettlingTime As Long) As Long

    '
    ' Monitor
    ' �����͸� ������ ������ �׸��� �߰��մϴ�.
    Public Declare Function AxlMonitorSetItem Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lItemIndex As Long, ByVal dwSignalType As Long, ByVal lSignalNo As Long, ByVal lSubSignalNo As Long) As Long

    ' ������ ������ ������ �׸�鿡 ���� ������ �����ɴϴ�.
    Public Declare Function AxlMonitorGetIndexInfo Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef lpItemSize As Long, ByRef lpItemIndex As Long) As Long

    ' ������ ������ ������ �� �׸��� ���� ������ �����ɴϴ�.
    Public Declare Function AxlMonitorGetItemInfo Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lItemIndex As Long, ByRef dwpSignalType As Long, ByRef lpSignalNo As Long, ByRef lpSubSignalNo As Long) As Long

    ' ��� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorResetAllItem Lib "AXL.dll" (ByVal lBoardNo As Long) As Long

    ' ���õ� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorResetItem Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lItemIndex As Long) As Long

    ' ������ ������ Ʈ���� ������ �����մϴ�.
    Public Declare Function AxlMonitorSetTriggerOption Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwSignalType As Long, ByVal lSignalNo As Long, ByVal lSubSignalNo As Long, ByVal dwOperatorType As Long, ByVal dValue1 As Double, ByVal dValue2 As Double) As Long

    ' ������ ������ Ʈ���� ������ �����ɴϴ�.
    'DWORD  __stdcall AxlMonitorGetTriggerOption(DWORD* dwpSignalType, long* lpSignalNo, long* lpSubSignalNo, DWORD* dwpOperatorType, double* dpValue1, double* dpValue2);

    ' ������ ������ Ʈ���� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorResetTriggerOption Lib "AXL.dll" (ByVal lBoardNo As Long) As Long

    ' ������ ������ �����մϴ�.
    Public Declare Function AxlMonitorStart Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwStartOption As Long, ByVal dwOverflowOption As Long) As Long

    ' ������ ������ �����մϴ�.
    Public Declare Function AxlMonitorStop Lib "AXL.dll" (ByVal lBoardNo As Long) As Long

    ' ������ �����͸� �����ɴϴ�.
    Public Declare Function AxlMonitorReadData Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef lpItemSize As Long, ByRef lpDataCount As Long, ByRef dpReadData As Double) As Long

    ' ������ ������ �ֱ⸦ �����ɴϴ�.
    Public Declare Function AxlMonitorReadPeriod Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwpPeriod As Long) As Long
    '


    '
    ' MonitorEx
    ' �����͸� ������ ������ �׸��� �߰��մϴ�.
    Public Declare Function AxlMonitorExSetItem Lib "AXL.dll" (ByVal lItemIndex As Long, ByVal dwSignalType As Long, ByVal lSignalNo As Long, ByVal lSubSignalNo As Long) As Long

    ' ������ ������ ������ �׸�鿡 ���� ������ �����ɴϴ�.
    Public Declare Function AxlMonitorExGetIndexInfo Lib "AXL.dll" (ByRef lpItemSize As Long, ByRef lpItemIndex As Long) As Long

    ' ������ ������ ������ �� �׸��� ���� ������ �����ɴϴ�.
    Public Declare Function AxlMonitorExGetItemInfo Lib "AXL.dll" (ByVal lItemIndex As Long, ByRef dwpSignalType As Long, ByRef lpSignalNo As Long, ByRef lpSubSignalNo As Long) As Long

    ' ��� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorExResetAllItem Lib "AXL.dll" () As Long

    ' ���õ� ������ ���� �׸��� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorExResetItem Lib "AXL.dll" (ByVal lItemIndex As Long) As Long

    ' ������ ������ Ʈ���� ������ �����մϴ�.
    Public Declare Function AxlMonitorExSetTriggerOption Lib "AXL.dll" (ByVal dwSignalType As Long, ByVal lSignalNo As Long, ByVal lSubSignalNo As Long, ByVal dwOperatorType As Long, ByVal dValue1 As Double, ByVal dValue2 As Double) As Long

    ' ������ ������ Ʈ���� ������ �����ɴϴ�.
    'DWORD  __stdcall AxlMonitorExGetTriggerOption(DWORD* dwpSignalType, long* lpSignalNo, long* lpSubSignalNo, DWORD* dwpOperatorType, double* dpValue1, double* dpValue2);

    ' ������ ������ Ʈ���� ������ �ʱ�ȭ�մϴ�.
    Public Declare Function AxlMonitorExResetTriggerOption Lib "AXL.dll" () As Long

    ' ������ ������ �����մϴ�.
    Public Declare Function AxlMonitorExStart Lib "AXL.dll" (ByVal dwStartOption As Long, ByVal dwOverflowOption As Long) As Long

    ' ������ ������ �����մϴ�.
    Public Declare Function AxlMonitorExStop Lib "AXL.dll" () As Long

    ' ������ �����͸� �����ɴϴ�.
    Public Declare Function AxlMonitorExReadData Lib "AXL.dll" (ByRef lpItemSize As Long, ByRef lpDataCount As Long, ByRef dpReadData As Double) As Long

    ' ������ ������ �ֱ⸦ �����ɴϴ�.
    Public Declare Function AxlMonitorExReadPeriod Lib "AXL.dll" (ByRef dwpPeriod As Long) As Long
    '

    ' X2, Y2 �࿡ ���� Offset ��ġ ������ ������ 2�� ���� ���� #01.
    Public Declare Function AxmLineMoveDual01 Lib "AXL.dll" (ByVal lCoordNo As Long, ByRef dpEndPosition As Double, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal dOffsetLength As Double, ByVal dTotalLength As Double, ByRef dpStartOffsetPosition As Double, ByRef dpEndOffsetPosition As Double) As Long
    ' X2, Y2 �࿡ ���� Offset ��ġ ������ ������ 2�� ��ȣ ���� #01.
    Public Declare Function AxmCircleCenterMoveDual01 Lib "AXL.dll" (ByVal lCoordNo As Long, ByRef lpAxes As Long, ByRef dpCenterPosition As Double, ByRef dpEndPosition As Double, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal dwCWDir As Long, ByVal dOffsetLength As Double, ByVal dTotalLength As Double, ByRef dpStartOffsetPosition As Double, ByRef dpEndOffsetPosition As Double) As Long

    ' �ش纸���� connect mode �� ��ȯ�Ѵ�.
    ' dpMode : 1 Auto Connect Mode
    ' dpMode : 0 Manual Connect Mode
    Public Declare Function AxlGetBoardConnectMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwpMode As Long) As Long
    ' �ش纸���� connect mode �� �����Ѵ�.
    ' dMode : 1 Auto Connect Mode
    ' dMode : 0 Manual Connect Mode
    Public Declare Function AxlSetBoardConnectMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwMode As Long) As Long

    '������ ���� Command Queue �� �ʱ�ȭ �Ѵ�.
    Public Declare Function AxmStatusSetCmdQueueClear Lib "AXL.dll" (ByVal lAxisNo As Long) As Long

    ' ������ ���� ��� �������ݰ��� Data �� Ȯ���Ѵ�.
    Public Declare Function AxmStatusGetControlBits Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpTxData As Long, ByRef dwpRxData As Long) As Long

    ' ��� ���� AXL�� �ִ��� Ȯ��(Shared Memory�� �����ϴ��� Ȯ��)
    Public Declare Function AxlIsUsing Lib "AXL.dll" () As Byte
    Public Declare Function AxlRescanExternalDevice Lib "AXL.dll" () As Long
    Public Declare Function AxlGetExternalDeviceInfo Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef devInfo As void*) As Long


