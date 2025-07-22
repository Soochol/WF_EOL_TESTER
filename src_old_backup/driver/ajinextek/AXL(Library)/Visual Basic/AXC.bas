'*****************************************************************************
'/****************************************************************************
'*****************************************************************************
'**
'** File Name
'** ----------
'**
'** AXC.BAS
'**
'** COPYRIGHT (c) AJINEXTEK Co., LTD
'**
'*****************************************************************************
'*****************************************************************************
'**
'** Description
'** -----------
'** Ajinextek Counter Library Header File
'** 
'**
'*****************************************************************************
'*****************************************************************************
'**
'** Source Change Indices
'** ---------------------
'** 
'** (None)
'**
'**
'*****************************************************************************
'*****************************************************************************
'**
'** Website
'** ---------------------
'**
'** http://www.ajinextek.com
'**
'*****************************************************************************
'*****************************************************************************
'*/
'

Attribute VB_Name = "AXC"


    '========== ���� �� ��� ����
    ' CNT ����� �ִ��� Ȯ��
    Public Declare Function AxcInfoIsCNTModule Lib "AXL.dll" (ByRef upStatus As Long) As Long

    ' CNT ��� No Ȯ��
    Public Declare Function AxcInfoGetModuleNo Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef lpModuleNo As Long) As Long

    ' CNT ����� ����� ���� Ȯ��
    Public Declare Function AxcInfoGetModuleCount Lib "AXL.dll" (ByRef lpModuleCount As Long) As Long

    ' ������ ����� ī���� �Է� ä�� ���� Ȯ��
    Public Declare Function AxcInfoGetChannelCount Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef lpCount As Long) As Long

    ' �ý��ۿ� ������ ī������ �� ä�� ���� Ȯ��
    Public Declare Function AxcInfoGetTotalChannelCount Lib "AXL.dll" (ByRef lpChannelCount As Long) As Long

    ' ������ ��� ��ȣ�� ���̽� ���� ��ȣ, ��� ��ġ, ��� ID Ȯ��
    Public Declare Function AxcInfoGetModule Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef lpBoardNo As Long, ByRef lpModulePos As Long, ByRef upModuleID As Long) As Long

    ' �ش� ����� ��� ������ �������� ��ȯ�Ѵ�.
    Public Declare Function AxcInfoGetModuleStatus Lib "AXL.dll" (ByVal lModuleNo As Long) As Long

    Public Declare Function AxcInfoGetFirstChannelNoOfModuleNo Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef lpChannelNo As Long) As Long
    Public Declare Function AxcInfoGetModuleNoOfChannelNo Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef lpModuleNo As Long) As Long

    ' ī���� ����� Encoder �Է� ����� ���� �մϴ�.
    ' dwMethod --> 0x00 : Sign and pulse, x1 multiplication
    ' dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    ' dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    ' dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    ' dwMethod --> 0x08 : Sign and pulse, x2 multiplication
    ' dwMethod --> 0x09 : Increment and decrement pulses, x1 multiplication
    ' dwMethod --> 0x0A : Increment and decrement pulses, x2 multiplication
    ' SIO-CN2CH/HPC4�� ���
    ' dwMethod --> 0x00 : Up/Down ���, A phase : �޽�, B phase : ����
    ' dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    ' dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    ' dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    ' SIO-LCM4�� ���
    ' dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    ' dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    ' dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    Public Declare Function AxcSignalSetEncInputMethod Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwMethod As Long) As Long

    ' ī���� ����� Encoder �Է� ����� ���� �մϴ�.
    ' *dwpUpMethod --> 0x00 : Sign and pulse, x1 multiplication
    ' *dwpUpMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    ' *dwpUpMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    ' *dwpUpMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    ' *dwpUpMethod --> 0x08 : Sign and pulse, x2 multiplication
    ' *dwpUpMethod --> 0x09 : Increment and decrement pulses, x1 multiplication
    ' *dwpUpMethod --> 0x0A : Increment and decrement pulses, x2 multiplication
    ' SIO-CN2CH/HPC4�� ���
    ' dwMethod --> 0x00 : Up/Down ���, A phase : �޽�, B phase : ����
    ' dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    ' dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    ' dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    ' SIO-LCM4�� ���
    ' dwMethod --> 0x01 : Phase-A and phase-B pulses, x1 multiplication
    ' dwMethod --> 0x02 : Phase-A and phase-B pulses, x2 multiplication
    ' dwMethod --> 0x03 : Phase-A and phase-B pulses, x4 multiplication
    Public Declare Function AxcSignalGetEncInputMethod Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpUpMethod As Long) As Long

    ' ī���� ����� Ʈ���Ÿ� ���� �մϴ�.
    ' dwMode -->  0x00 : Latch
    ' dwMode -->  0x01 : State
    ' dwMode -->  0x02 : Special State    --> SIO-CN2CH ����
    ' SIO-CN2CH�� ���
    ' dwMode -->  0x00 : ���� ��ġ Ʈ���� �Ǵ� �ֱ� ��ġ Ʈ����.
    ' ���� : ��ǰ���� ����� ���� �ٸ��� ������ �����Ͽ� ��� �ʿ�.
    ' dwMode -->  0x01 : �ð� �ֱ� Ʈ����(AxcTriggerSetFreq�� ����)
    ' SIO-HPC4�� ���
    ' dwMode -->  0x00 : timer mode with counter & frequncy.
    ' dwMode -->  0x01 : timer mode.
    ' dwMode -->  0x02 : absolute mode[with fifo].
    ' dwMode -->  0x03 : periodic mode.[Default]
    Public Declare Function AxcTriggerSetFunction Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwMode As Long) As Long

    ' ī���� ����� Ʈ���� ������ Ȯ�� �մϴ�.
    ' *dwMode -->  0x00 : Latch
    ' *dwMode -->  0x01 : State
    ' *dwMode -->  0x02 : Special State
    ' SIO-CN2CH�� ���
    ' *dwMode -->  0x00 : ���� ��ġ Ʈ���� �Ǵ� �ֱ� ��ġ Ʈ����.
    ' ���� : ��ǰ���� ����� ���� �ٸ��� ������ �����Ͽ� ��� �ʿ�.
    ' *dwMode -->  0x01 : �ð� �ֱ� Ʈ����(AxcTriggerSetFreq�� ����)
    ' SIO-HPC4�� ���
    ' *dwMode -->  0x00 : timer mode with counter & frequncy.
    ' *dwMode -->  0x01 : timer mode.
    ' *dwMode -->  0x02 : absolute mode[with fifo].
    ' *dwMode -->  0x03 : periodic mode.[Default]
    Public Declare Function AxcTriggerGetFunction Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpMode As Long) As Long

    ' dwUsage --> 0x00 : Trigger Not use
    ' dwUsage --> 0x01 : Trigger use
    Public Declare Function AxcTriggerSetNotchEnable Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwUsage As Long) As Long

    ' *dwUsage --> 0x00 : Trigger Not use
    ' *dwUsage --> 0x01 : Trigger use
    Public Declare Function AxcTriggerGetNotchEnable Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpUsage As Long) As Long


    ' ī���� ����� Capture �ؼ��� ���� �մϴ�.(External latch input polarity)
    ' dwCapturePol --> 0x00 : Signal OFF -> ON
    ' dwCapturePol --> 0x01 : Signal ON -> OFF
    Public Declare Function AxcSignalSetCaptureFunction Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwCapturePol As Long) As Long

    ' ī���� ����� Capture �ؼ� ������ Ȯ�� �մϴ�.(External latch input polarity)
    ' *dwCapturePol --> 0x00 : Signal OFF -> ON
    ' *dwCapturePol --> 0x01 : Signal ON -> OFF
    Public Declare Function AxcSignalGetCaptureFunction Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpCapturePol As Long) As Long

    ' ī���� ����� Capture ��ġ�� Ȯ�� �մϴ�.(External latch)
    ' *dbpCapturePos --> Capture position ��ġ
    Public Declare Function AxcSignalGetCapturePos Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dbpCapturePos As Double) As Long

    ' ī���� ����� ī���� ���� Ȯ�� �մϴ�.
    ' *dbpActPos --> ī���� ��
    Public Declare Function AxcStatusGetActPos Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dbpActPos As Double) As Long

    ' ī���� ����� ī���� ���� dbActPos ������ ���� �մϴ�.
    Public Declare Function AxcStatusSetActPos Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dbActPos As Double) As Long

    ' ī���� ����� Ʈ���� ��ġ�� �����մϴ�.
    ' ī���� ����� Ʈ���� ��ġ�� 2�������� ���� �� �� �ֽ��ϴ�.
    Public Declare Function AxcTriggerSetNotchPos Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dbLowerPos As Double, ByVal dbUpperPos As Double) As Long

    ' ī���� ����� ������ Ʈ���� ��ġ�� Ȯ�� �մϴ�.
    Public Declare Function AxcTriggerGetNotchPos Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dbpLowerPos As Double, ByRef dbpUpperPos As Double) As Long

    ' ī���� ����� Ʈ���� ����� ������ �մϴ�.
    ' dwOutVal --> 0x00 : Ʈ���� ��� '0'
    ' dwOutVal --> 0x01 : Ʈ���� ��� '1'
    Public Declare Function AxcTriggerSetOutput Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwOutVal As Long) As Long

    ' ī���� ����� ���¸� Ȯ���մϴ�.
    ' Bit '0' : Carry (ī���� ����ġ�� ���� �޽��� ���� ī���� ����ġ�� �Ѿ� 0�� �ٲ���� �� 1��ĵ�� ON���� �մϴ�.)
    ' Bit '1' : Borrow (ī���� ����ġ�� ���� �޽��� ���� 0�� �Ѿ� ī���� ����ġ�� �ٲ���� �� 1��ĵ�� ON���� �մϴ�.)
    ' Bit '2' : Trigger output status
    ' Bit '3' : Latch input status
    Public Declare Function AxcStatusGetChannel Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpChannelStatus As Long) As Long


    ' SIO-CN2CH ���� �Լ���
    '
    ' ī���� ����� ��ġ ������ �����Ѵ�.
    ' ���� ��ġ �̵����� ���� �޽� ������ �����ϴµ�,
    ' ex) 1mm �̵��� 1000�� �ʿ��ϴٸ�dMoveUnitPerPulse = 0.001�� �Է��ϰ�,
    '     ���� ��� �Լ��� ��ġ�� ���õ� ���� mm ������ �����ϸ� �ȴ�.
    Public Declare Function AxcMotSetMoveUnitPerPulse Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dMoveUnitPerPulse As Double) As Long

    ' ī���� ����� ��ġ ������ Ȯ���Ѵ�.
    Public Declare Function AxcMotGetMoveUnitPerPulse Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dpMoveUnitPerPuls As Double) As Long

    ' ī���� ����� ���ڴ� �Է� ī���͸� ���� ����� �����Ѵ�.
    ' dwReverse --> 0x00 : �������� ����.
    ' dwReverse --> 0x01 : ����.
    Public Declare Function AxcSignalSetEncReverse Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwReverse As Long) As Long

    ' ī���� ����� ���ڴ� �Է� ī���͸� ���� ����� ������ Ȯ���Ѵ�.
    Public Declare Function AxcSignalGetEncReverse Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpReverse As Long) As Long

    ' ī���� ����� Encoder �Է� ��ȣ�� �����Ѵ�.
    ' dwSource -->  0x00 : 2(A/B)-Phase ��ȣ.
    ' dwSource -->  0x01 : Z-Phase ��ȣ.(���⼺ ����.)
    Public Declare Function AxcSignalSetEncSource Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwSource As Long) As Long

    ' ī���� ����� Encoder �Է� ��ȣ ���� ������ Ȯ���Ѵ�.
    Public Declare Function AxcSignalGetEncSource Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpSource As Long) As Long

    ' ī���� ����� Ʈ���� ��� ���� �� ���� ���� �����Ѵ�.
    ' ��ġ �ֱ� Ʈ���� ��ǰ�� ��� ��ġ �ֱ�� Ʈ���� ����� �߻���ų ���� �� ���� ���� �����Ѵ�.
    ' ���� ��ġ Ʈ���� ��ǰ�� ��� Ram ���� ������ Ʈ���� ������ ���� ���� ��ġ�� �����Ѵ�.
    ' ���� : AxcMotSetMoveUnitPerPulse�� ������ ����.
    ' Note : ���Ѱ��� ���Ѱ����� �������� �����Ͽ��� �մϴ�.
    Public Declare Function AxcTriggerSetBlockLowerPos Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dLowerPosition As Double) As Long

    ' ī���� ����� Ʈ���� ��� ���� �� ���� ���� Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetBlockLowerPos Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dpLowerPosition As Double) As Long

    ' ī���� ����� Ʈ���� ��� ���� �� ���� ���� �����Ѵ�.
    ' ��ġ �ֱ� Ʈ���� ��ǰ�� ��� ��ġ �ֱ�� Ʈ���� ����� �߻���ų ���� �� ���� ���� �����Ѵ�.
    ' ���� ��ġ Ʈ���� ��ǰ�� ��� Ʈ���� ������ ������ Ram �� ������ ������ Ʈ���� ������ ����Ǵ� ��ġ�� ���ȴ�.
    ' ���� : AxcMotSetMoveUnitPerPulse�� ������ ����.
    ' Note : ���Ѱ��� ���Ѱ����� ū���� �����Ͽ��� �մϴ�.
    Public Declare Function AxcTriggerSetBlockUpperPos Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dUpperPosition As Double) As Long
    ' ī���� ����� Ʈ���� ��� ���� �� ���� ���� �����Ѵ�.
    Public Declare Function AxcTriggerGetBlockUpperPos Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dpUpperrPosition As Double) As Long

    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���ſ� ���Ǵ� ��ġ �ֱ⸦ �����Ѵ�.
    ' ���� : AxcMotSetMoveUnitPerPulse�� ������ ����.
    Public Declare Function AxcTriggerSetPosPeriod Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dPeriod As Double) As Long

    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���ſ� ���Ǵ� ��ġ �ֱ⸦ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPosPeriod Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dpPeriod As Double) As Long

    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���� ���� ��ġ ������ ���� ��ȿ����� �����Ѵ�.
    ' dwDirection -->  0x00 : ī������ ��/���� ���Ͽ� Ʈ���� �ֱ� ���� ���.
    ' dwDirection -->  0x01 : ī���Ͱ� ���� �Ҷ��� Ʈ���� �ֱ� ���� ���.
    ' dwDirection -->  0x01 : ī���Ͱ� ���� �Ҷ��� Ʈ���� �ֱ� ���� ���.
    Public Declare Function AxcTriggerSetDirectionCheck Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwDirection As Long) As Long
    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���� ���� ��ġ ������ ���� ��ȿ��� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetDirectionCheck Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpDirection As Long) As Long

    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���� ����� ����, ��ġ �ֱ⸦ �ѹ��� �����Ѵ�.
    ' ��ġ ���� ���� :  AxcMotSetMoveUnitPerPulse�� ������ ����.
    Public Declare Function AxcTriggerSetBlock Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dLower As Double, ByVal dUpper As Double, ByVal dABSod As Double) As Long

    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���� ����� ����, ��ġ �ֱ⸦ ������ �ѹ��� Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetBlock Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dpLower As Double, ByRef dpUpper As Double, ByRef dpABSod As Double) As Long

    ' ī���� ����� Ʈ���� ��� �޽� ���� �����Ѵ�.
    ' ���� : uSec
    Public Declare Function AxcTriggerSetTime Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dTrigTime As Double) As Long

    ' ī���� ����� Ʈ���� ��� �޽� �� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetTime Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dpTrigTime As Double) As Long

    ' ī���� ����� Ʈ���� ��� �޽��� ��� ������ �����Ѵ�.
    ' dwLevel -->  0x00 : Ʈ���� ��½� 'Low' ���� ���.
    ' dwLevel -->  0x01 : Ʈ���� ��½� 'High' ���� ���.
    Public Declare Function AxcTriggerSetLevel Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwLevel As Long) As Long
    ' ī���� ����� Ʈ���� ��� �޽��� ��� ���� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetLevel Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpLevel As Long) As Long

    ' ī���� ����� ���ļ� Ʈ���� ��� ��ɿ� �ʿ��� ���ļ��� �����Ѵ�.
    ' ���� : Hz, ���� : 1Hz ~ 500 kHz
    Public Declare Function AxcTriggerSetFreq Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwFreqency As Long) As Long
    ' ī���� ����� ���ļ� Ʈ���� ��� ��ɿ� �ʿ��� ���ļ��� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetFreq Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpFreqency As Long) As Long

    ' ī���� ����� ���� ä�ο� ���� ���� ��� ���� �����Ѵ�.
    ' dwOutput ���� : 0x00 ~ 0x0F, �� ä�δ� 4���� ���� ���
    Public Declare Function AxcSignalWriteOutput Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwOutput As Long) As Long

    ' ī���� ����� ���� ä�ο� ���� ���� ��� ���� Ȯ���Ѵ�.
    Public Declare Function AxcSignalReadOutput Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpOutput As Long) As Long

    ' ī���� ����� ���� ä�ο� ���� ���� ��� ���� ��Ʈ ���� �����Ѵ�.
    ' lBitNo ���� : 0 ~ 3, �� ä�δ� 4���� ���� ���
    Public Declare Function AxcSignalWriteOutputBit Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal lBitNo As Long, ByVal uOnOff As Long) As Long
    ' ī���� ����� ���� ä�ο� ���� ���� ��� ���� ��Ʈ ���� Ȯ�� �Ѵ�.
    ' lBitNo ���� : 0 ~ 3
    Public Declare Function AxcSignalReadOutputBit Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal lBitNo As Long, ByRef upOnOff As Long) As Long

    ' ī���� ����� ���� ä�ο� ���� ���� �Է� ���� Ȯ���Ѵ�.
    Public Declare Function AxcSignalReadInput Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpInput As Long) As Long

    ' ī���� ����� ���� ä�ο� ���� ���� �Է� ���� ��Ʈ ���� Ȯ�� �Ѵ�.
    ' lBitNo ���� : 0 ~ 3
    Public Declare Function AxcSignalReadInputBit Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal lBitNo As Long, ByRef upOnOff As Long) As Long

    ' ī���� ����� Ʈ���� ����� Ȱ��ȭ �Ѵ�.
    ' ���� ������ ��ɿ� ���� Ʈ���� ����� ���������� ����� ������ �����Ѵ�.
    Public Declare Function AxcTriggerSetEnable Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwUsage As Long) As Long

    ' ī���� ����� Ʈ���� ��� Ȱ��ȭ ���� ������ Ȯ���ϴ�.
    Public Declare Function AxcTriggerGetEnable Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpUsage As Long) As Long

    ' ī���� ����� ������ġ Ʈ���� ����� ���� ������ RAM ������ Ȯ���Ѵ�.
    ' dwAddr ���� : 0x0000 ~ 0x1FFFF;
    Public Declare Function AxcTriggerReadAbsRamData Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwAddr As Long, ByRef dwpData As Long) As Long

    ' ī���� ����� ������ġ Ʈ���� ����� ���� �ʿ��� RAM ������ �����Ѵ�.
    ' dwAddr ���� : 0x0000 ~ 0x1FFFF;
    Public Declare Function AxcTriggerWriteAbsRamData Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwAddr As Long, ByVal dwData As Long) As Long

    ' ���� CNT ä���� ���� ��ġ Ʈ���� ����� ���� DWORD�� ��ġ ������ �����Ѵ�.
    '----------------------------------------------------------------------------------------------------------------------------------
    ' 1. AXT_SIO_CN2CH�� ���
    ' dwTrigNum --> 131072(=0x20000) ������ ���� ����
    ' dwTrigPos --> DWORD�� Data �Է� ����
    ' dwDirection --> 0x0(default) : dwTrigPos[0], dwTrigPos[1] ..., dwTrigPos[dwTrigNum - 1] ������ Data�� Write �Ѵ�.
    '     0x1    : dwTrigPos[dwTrigNum - 1], dwTrigPos[dwTrigNum - 2], ..., dwTrigPos[0] ������ Data�� Write �Ѵ�.
    ' *����* 1) dwDirection: Data Write ������ �ٸ� �� ��ɻ��� ���� ����
    '    2) AXC Manual�� AxcTriggerSetAbs - Description�� �����Ͽ� data�� ���� �� ����ؾ� ��
    '----------------------------------------------------------------------------------------------------------------------------------
    ' 2. AXT_SIO_HPC4�� ���
    ' dwTrigNum --> 500 ������ ���� ����
    ' dwTrigPos --> DWORD�� Data �Է� ����
    ' dwDirection --> 0x0(default) : ������ �ʴ� ������, �Է����� �ʾƵ� �ȴ�.
    '----------------------------------------------------------------------------------------------------------------------------------
    ' 3. AXT_SIO_RCNT2RTEX, AXT_SIO_RCNT2MLIII, AXT_SIO_RCNT2SIIIH, AXT_SIO_RCNT2SIIIH_R�� ���
    ' dwTrigNum --> 0x200(=512) ������ ���� ����
    ' dwTrigPos --> DWORD�� data �Է� ����
    ' dwDirection --> 0x0(default) : ������ �ʴ� ������, �Է����� �ʾƵ� �ȴ�.
    '----------------------------------------------------------------------------------------------------------------------------------
    Public Declare Function AxcTriggerSetAbs Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwTrigNum As Long, ByRef dwTrigPos As Long, ByVal 0 As DWORD dwDirection =) As Long


    ' ���� CNT ä���� ���� ��ġ Ʈ���� ����� ���� double�� ��ġ ������ �����Ѵ�.
    '----------------------------------------------------------------------------------------------------------------------------------
    ' 1. AXT_SIO_CN2CH�� ���
    ' dwTrigNum --> 4194304(=0x20000*32) ������ ���� ����
    ' dTrigPos  --> double�� data �Է� ����
    ' dwDirection --> 0x0(default) : dTrigPos[0], dTrigPos[1] ..., dTrigPos[dwTrigNum - 1] ������ Data�� Write �Ѵ�.
    '     0x1    : dTrigPos[dwTrigNum - 1], dTrigPos[dwTrigNum - 2], ..., dTrigPos[0] ������ Data�� Write �Ѵ�.
    ' *����* 1) dwDirection: Data Write ������ �ٸ� �� ��ɻ��� ���� ����
    '----------------------------------------------------------------------------------------------------------------------------------
    ' 2. AXT_SIO_RCNT2RTEX, AXT_SIO_RCNT2MLIII, AXT_SIO_RCNT2SIIIH_R�� ���
    ' dwTrigNum --> 0x200(=512) ������ ���� ����
    ' dTrigPos  --> double�� data �Է� ����
    ' dwDirection --> 0x0(default) : ������ �ʴ� ������, �Է����� �ʾƵ� �ȴ�.
    '----------------------------------------------------------------------------------------------------------------------------------
    Public Declare Function AxcTriggerSetAbsDouble Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwTrigNum As Long, ByRef dTrigPos As Double, ByVal 0 As DWORD dwDirection =) As Long

    ' LCM4_10_Version/

    ' ī���� ����� PWM ����� Ȱ��ȭ�Ѵ�.
    Public Declare Function AxcTriggerSetPwmEnable Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal bEnable As Byte) As Long
    ' ī���� ����� PWM ��� Ȱ��ȭ ���¸� Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPwmEnable Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef bEnable As bool*) As Long
    ' ī���� ����� PWM ��¸�带 �����Ѵ�.
    ' dwMode : PWM ��¸��
    ' [0] : Manual (Manual�� ������ PWM Data)
    ' [1] : Auto (�ӵ� Table)
    Public Declare Function AxcTriggerSetPwmOutMode Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwMode As Long) As Long
    ' ī���� ����� PWM ��¸�带 Ȯ���Ѵ�.
    ' dwMode : PWM ��¸��
    ' [0] : Manual (Manual�� ������ PWM Data)
    ' [1] : Auto (�ӵ� Table)
    Public Declare Function AxcTriggerGetPwmOutMode Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpMode As Long) As Long

    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� �ӵ� ������ �����Ѵ�.
    ' dMinVel : dMinVel
    ' dMaxVel : dMaxVel
    ' dVelInterval : �ӵ� ���̺����� ������ �ӵ� Interval
    ' ������ : dMinVel���� dVelInterval �������� �ִ� 5000���� �ӵα����� ������.
    '          (((dMaxVel-dMinVel) / dVelInterval) <= 5000)�� �����Ͽ��� �Ѵ�.
    Public Declare Function AxcTriggerSetPwmVelInfo Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dMinVel As Double, ByVal dMaxVel As Double, ByVal dVelInterval As Double) As Long
    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� �ӵ� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPwmVelInfo Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dpMinVel As Double, ByRef dpMaxVel As Double, ByRef dpVelInterval As Double) As Long
    ' ī���� ����� PWM ��¿��� Pulse �� �������� �����Ѵ�.
    ' dwMode : Pulse �� ����
    ' [0] : DutyRatio
    ' [1] : PulseWidth
    Public Declare Function AxcTriggerSetPwmPulseControl Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwMode As Long) As Long
    '  ī���� ����� PWM ��¿��� Pulse ��������� Ȯ�δ�.
    ' dwpMode : Pulse �� ����
    ' [0] : DutyRatio
    ' [1] : PulseWidth
    Public Declare Function AxcTriggerGetPwmPulseControl Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpMode As Long) As Long

    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ �����Ѵ�.
    ' pwm ��¸�尡 Manual �� ��쿡�� ��ȿ�ϴ�
    ' dFrequency :  (0.017 ~ 1M) ���� ������ �����ϴ�. (Hz ����)
    ' dData : Pulse �� ���� Data �� �Է��ϸ� Pulse Control ��Ŀ� ���� Data ������ �ٸ���.
    ' Pulse �� �������� DutyRatio�� ��� DutyRatio
    ' Pulse �� �������� PulseWidth �� ��� PulseWidth (us����)
    Public Declare Function AxcTriggerSetPwmManualData Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dFrequency As Double, ByVal dData As Double) As Long
    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPwmManualData Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dpFrequency As Double, ByRef dpData As Double) As Long
    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ �����Ѵ�.
    ' lDataCnt : ���� �� Ʈ���� ������ ��ü ����
    ' dpVel : dpVel[0],dpVel[1]....dpVel[DataCnt -1] ������ �Է� ����
    ' dwpFrequency : dwpFrequency[0],dwpFrequency[1]....dwpFrequency[DataCnt-1] ������ �Է� ����(0.017 ~ 1M) ���� ������ �����ϴ�.
    ' dData : Pulse �� ���� Data �� �Է��ϸ� Pulse Control ��Ŀ� ���� Data ������ �ٸ���.
    ' Pulse �� �������� DutyRatio�� ��� DutyRatio
    ' Pulse �� �������� PulseWidth �� ��� PulseWidth (us����)
    ' ������ :
    '    1) dpVel, dwpFrequency, dwpDutyRatio �� �迭 ������ �����Ͽ� ����ؾ��Ѵ�.
    '  - �ӵ��� 0�� ���������� PWM ����� �Ұ��ϴ�.
    '    3) PWM Enable ���¿����� ����� �� ����.
    Public Declare Function AxcTriggerSetPwmPatternData Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal lDataCnt As Long, ByRef dpVel As Double, ByRef dpFrequency As Double, ByRef dpData As Double) As Long
    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ �����Ѵ�.
    Public Declare Function AxcTriggerSetPwmData Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dVel As Double, ByVal dFrequency As Double, ByVal dData As Double) As Long
    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPwmData Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dVel As Double, ByRef dpFrequency As Double, ByRef dpData As Double) As Long
    ' ī���� ����� �ӵ� ���� Ȯ�� �մϴ�.
    Public Declare Function AxcStatusReadActVel Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dpActVel As Double) As Long
    ' ī���� ����� 2D �ӵ� ���� Ȯ�� �մϴ�.
    Public Declare Function AxcStatusRead2DActVel Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dpActVel As Double) As Long
    ' ī���� ����� Position ���� �ʱ�ȭ �Ѵ�.
    Public Declare Function AxcStatusSetActPosClear Lib "AXL.dll" (ByVal lChannelNo As Long) As Long
    ' HPC4_30_Version
    ' ī���� ����� �� ���̺� �Ҵ�� Ʈ���� ����� ������ �����Ѵ�.
    ' uLevel : Ʈ���� ��� ��ȣ�� Active Level
    '   [0]  : Ʈ���� ��½� 'Low' ���� ���.
    '   [1]  : Ʈ���� ��½� 'High' ���� ���.
    Public Declare Function AxcTableSetTriggerLevel Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByVal uLevel As Long) As Long
    ' ī���� ����� �� ���̺� ������ Ʈ���� ����� ���� �������� Ȯ���Ѵ�.
    Public Declare Function AxcTableGetTriggerLevel Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef upLevel As Long) As Long

    ' ī���� ����� �� ���̺� �Ҵ�� Ʈ���� ����� �޽� ���� �����Ѵ�.
    ' dTriggerTimeUSec : [Default 500ms], us������ ����
    Public Declare Function AxcTableSetTriggerTime Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByVal dTriggerTimeUSec As Double) As Long
    ' ī���� ����� �� ���̺� ������ Ʈ���� ����� �޽� �� �������� Ȯ���Ѵ�.
    Public Declare Function AxcTableGetTriggerTime Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef dpTriggerTimeUSec As Double) As Long

    ' ī���� ����� �� ���̺� �Ҵ� �� 2���� ���ڴ� �Է� ��ȣ�� �����Ѵ�.
    ' uEncoderInput1 [0-3]: ī���� ��⿡ �ԷµǴ� 4���� ���ڴ� ��ȣ�� �ϳ�
    ' uEncoderInput2 [0-3]: ī���� ��⿡ �ԷµǴ� 4���� ���ڴ� ��ȣ�� �ϳ�
    Public Declare Function AxcTableSetEncoderInput Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByVal uEncoderInput1 As Long, ByVal uEncoderInput2 As Long) As Long
    ' ī���� ����� �� ���̺� �Ҵ� �� 2���� ���ڴ� �Է� ��ȣ�� Ȯ���Ѵ�.
    Public Declare Function AxcTableGetEncoderInput Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef upEncoderInput1 As Long, ByRef upEncoderInput2 As Long) As Long

    ' ī���� ����� �� ���̺� �Ҵ� �� Ʈ���� ��� ��Ʈ�� �����Ѵ�.
    ' uTriggerOutport [0x0-0xF]: Bit0: Ʈ���� ��� 0, Bit1: Ʈ���� ��� 1, Bit2: Ʈ���� ��� 2, Bit3: Ʈ���� ��� 3
    ' Ex) 0x3(3)   : ��� 0, 1�� Ʈ���� ��ȣ�� ����ϴ� ���
    '     0xF(255) : ��� 0, 1, 2, 3�� Ʈ���� ��ȣ�� ����ϴ� ���
    Public Declare Function AxcTableSetTriggerOutport Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByVal uTriggerOutport As Long) As Long
    ' ī���� ����� �� ���̺� �Ҵ� �� Ʈ���� ��� ��Ʈ�� Ȯ���Ѵ�.
    Public Declare Function AxcTableGetTriggerOutport Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef upTriggerOutport As Long) As Long

    ' ī���� ����� �� ���̺� ������ Ʈ���� ��ġ�� ���� ��� ���� ������ �����Ѵ�.
    ' dErrorRange  : ���� ���� Unit������ Ʈ���� ��ġ�� ���� ��� ���� ������ ����
    Public Declare Function AxcTableSetErrorRange Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByVal dErrorRange As Double) As Long
    ' ī���� ����� �� ���̺� ������ Ʈ���� ��ġ�� ���� ��� ���� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTableGetErrorRange Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef dpErrorRange As Double) As Long

    ' ī���� ����� �� ���̺� ������ ������(Ʈ���� ��� Port, Ʈ���� �޽� ��) Ʈ���Ÿ� 1�� �߻���Ų��.
    ' �� ���� : 1) Ʈ���Ű� Disable�Ǿ� ������ �� �Լ��� �ڵ����� Enable���� Ʈ���Ÿ� �߻���Ŵ
    '           2) Trigger Mode�� HPC4_PATTERN_TRIGGER ����� ��� �� �Լ��� �ڵ����� Ʈ���� ��带 HPC4_RANGE_TRIGGER�� ���� ��(�ϳ��� Ʈ���Ÿ� �߻���Ű�� ����)
    Public Declare Function AxcTableTriggerOneShot Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long) As Long

    ' ī���� ����� �� ���̺� ������ ������(Ʈ���� ��� Port, Ʈ���� �޽� ��), ������ ������ŭ ������ ���ļ��� Ʈ���Ÿ� �߻���Ų��.
    ' lTriggerCount     : ������ ���ļ��� �����ϸ� �߻���ų Ʈ���� ��� ����
    ' uTriggerFrequency : Ʈ���Ÿ� �߻���ų ���ļ�
    ' �� ���� : 1) Ʈ���Ű� Disable�Ǿ� ������ �� �Լ��� �ڵ����� Enable���� ������ ���� Ʈ���Ÿ� �߻���Ŵ
    '           2) Trigger Mode�� HPC4_PATTERN_TRIGGER ��尡 �ƴ� ��� �� �Լ��� �ڵ����� Ʈ���� ��带 HPC4_PATTERN_TRIGGER�� ���� ��
    Public Declare Function AxcTableTriggerPatternShot Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByVal lTriggerCount As Long, ByVal uTriggerFrequency As Long) As Long
    ' ī���� ����� �� ���̺� ������ ���� Ʈ���� ���� ������(���ļ�, ī����) Ȯ���Ѵ�.
    Public Declare Function AxcTableGetPatternShotData Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef lpTriggerCount As Long, ByRef upTriggerFrequency As Long) As Long

    ' ī���� ����� �� ���̺� Ʈ���Ÿ� ����ϴ� ����� �����Ѵ�.
    ' uTrigMode : Ʈ���Ÿ� ����ϴ� ����� �����Ѵ�.
    '   [0] HPC4_RANGE_TRIGGER   : ������ Ʈ���� ��ġ�� ������ ��� �����ȿ� ��ġ�� �� Ʈ���Ÿ� ����ϴ� ���
    '   [1] HPC4_VECTOR_TRIGGER  : ���� Ʈ���� ��ġ�� ������ ��� ������ ���� ������ ��ġ�� �� Ʈ���Ÿ� ����ϴ� ���
    '   [3] HPC4_PATTERN_TRIGGER : ��ġ�� �����ϰ� ������ ������ŭ ������ ���ļ��� Ʈ���Ÿ� ����ϴ� ���
    Public Declare Function AxcTableSetTriggerMode Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByVal uTrigMode As Long) As Long
    ' ī���� ����� �� ���̺� ������ Ʈ���Ÿ� ����ϴ� ����� Ȯ���Ѵ�
    Public Declare Function AxcTableGetTriggerMode Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef upTrigMode As Long) As Long
    ' ī���� ����� �� ���̺� ���� ��µ� ���� Ʈ���� ������ �ʱ�ȭ �Ѵ�.
    Public Declare Function AxcTableSetTriggerCountClear Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long) As Long

    ' ī���� ����� �� ���̺� 2-D ������ġ���� Ʈ���� ��ȣ�� ����ϱ� ���� �ʿ��� ������ �����Ѵ�.
    ' lTriggerDataCount : ���� �� Ʈ���� ������ ��ü ����
    '   [-1, 0]         : ��ϵ� Ʈ���� ���� ����Ÿ �ʱ�ȭ
    ' dpTriggerData     : 2-D ������ġ Ʈ���� ����(�ش� �迭�� ������ lTriggerDataCount * 2�� �Ǿ�ߵ�)
    '   *[0, 1]         : X[0], Y[0]
    ' lpTriggerCount    : �Է��� 2-D ���� Ʈ���� ��ġ���� Ʈ���� ���� ���� �� �߻���ų Ʈ���� ������ �迭�� ����(�ش� �迭�� ������ lTriggerDataCount)
    ' dpTriggerInterval : TriggerCount ��ŭ �����ؼ� Ʈ���Ÿ� �߻���ų�� ���� �� ������ ���ļ� ������ ����(�ش� �迭�� ������ lTriggerDataCount)
    ' ������ :
    '    1) �� ���������� �迭 ������ �����Ͽ� ����ؾߵ˴ϴ�. ���ο��� ���Ǵ� ���� ���� ���� �迭�� �����ϸ� �޸� ���� ������ �߻� �� �� ����.
    '    2) Trigger Mode�� HPC4_RANGE_TRIGGER�� �ڵ� �����
    '    3) �Լ� ���ο��� Trigger�� Disable�� �� ��� ������ �����ϸ� �Ϸ� �� �ٽ� Enable ��Ŵ
    Public Declare Function AxcTableSetTriggerData Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByVal lTriggerDataCount As Long, ByRef dpTriggerData As Double, ByRef lpTriggerCount As Long, ByRef dpTriggerInterval As Double) As Long
    ' ī���� ����� �� ���̺� Ʈ���� ��ȣ�� ����ϱ� ���� ������ Ʈ���� ���� ������ Ȯ���Ѵ�.
    ' �� ���� : �� ���̺� ��ϵ� �ִ� Ʈ���� ����Ÿ ������ �� ���� �Ʒ��� ���� Ʈ���� ����Ÿ ������ �̸� �ľ��� �� ����Ͻʽÿ�.
    ' Ex)      1) AxcTableGetTriggerData(lModuleNo, lTablePos, &lTriggerDataCount, NULL, NULL, NULL);
    '          2) dpTriggerData     = new double[lTriggerDataCount * 2];
    '          3) lpTriggerCount    = new long[lTriggerDataCount];
    '          4) dpTriggerInterval = new double[lTriggerDataCount];
    Public Declare Function AxcTableGetTriggerData Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef lpTriggerDataCount As Long, ByRef dpTriggerData As Double, ByRef lpTriggerCount As Long, ByRef dpTriggerInterval As Double) As Long

    ' ī���� ����� �� ���̺� 2-D ������ġ���� Ʈ���� ��ȣ�� ����ϱ� ���� �ʿ��� ������ AxcTableSetTriggerData�Լ��� �ٸ� ������� �����Ѵ�.
    ' lTriggerDataCount : ���� �� Ʈ���� ������ ��ü ����
    ' uOption : dpTriggerData �迭�� ����Ÿ �Է� ����� ����
    '   [0]   : dpTriggerData �迭�� X Pos[0], Y Pos[0], X Pos[1], Y Pos[1] ������ �Է�
    '   [1]   : dpTriggerData �迭�� X Pos[0], Y Pos[0], Count, Inteval, X Pos[1], Y Pos[1], Count, Inteval ������ �Է�
    ' ������ :
    '    1) dpTriggerData�� �迭 ������ �����Ͽ� ����ؾߵ˴ϴ�. ���ο��� ���Ǵ� ���� ���� ���� �迭�� �����ϸ� �޸� ���� ������ �߻� �� �� ����.
    '    2) Trigger Mode�� HPC4_RANGE_TRIGGER�� �ڵ� �����
    '    3) �Լ� ���ο��� Trigger�� Disable�� �� ��� ������ �����ϸ� �Ϸ� �� �ٽ� Enable ��Ŵ
    Public Declare Function AxcTableSetTriggerDataEx Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByVal lTriggerDataCount As Long, ByVal uOption As Long, ByRef dpTriggerData As Double) As Long
    ' ī���� ����� �� ���̺� Ʈ���� ��ȣ�� ����ϱ� ���� ������ Ʈ���� ���� ������ Ȯ���Ѵ�.
    ' �� ���� : �� ���̺� ��ϵ� �ִ� Ʈ���� ����Ÿ ������ �� ���� �Ʒ��� ���� Ʈ���� ����Ÿ ������ �̸� �ľ��� �� ���.
    ' Ex)      1) AxcTableGetTriggerDataEx(lModuleNo, lTablePos, &lTriggerDataCount, &uOption, NULL);
    '          2) if(uOption == 0) : dpTriggerData     = new double[lTriggerDataCount * 2];
    '          3) if(uOption == 1) : dpTriggerData     = new double[lTriggerDataCount * 4];
    '          4) dpTriggerInterval = new double[lTriggerDataCount];
    Public Declare Function AxcTableGetTriggerDataEx Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef lpTriggerDataCount As Long, ByRef upOption As Long, ByRef dpTriggerData As Double) As Long

    ' ī���� ����� ������ ���̺� ������ ��� Ʈ���� ����Ÿ�� H/W FIFO�� ����Ÿ�� ��� �����Ѵ�.
    Public Declare Function AxcTableSetTriggerDataClear Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long) As Long

    ' ī���� ����� ������ ���̺��� Ʈ���� ��� ����� ���۽�Ŵ.
    ' uEnable : Ʈ���Ÿ� ��� ����� ��뿩�θ� ����
    ' �� ���� : 1) Ʈ���� ��� �� DISABLE�ϸ� ����� �ٷ� ����
    '           2) AxcTableTriggerOneShot, AxcTableGetPatternShotData,AxcTableSetTriggerData, AxcTableGetTriggerDataEx �Լ� ȣ��� �ڵ����� ENABLE��
    Public Declare Function AxcTableSetEnable Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByVal uEnable As Long) As Long
    ' ī���� ����� ������ ���̺��� Ʈ���� ��� ����� ���� ���θ� Ȯ����.
    Public Declare Function AxcTableGetEnable Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef upEnable As Long) As Long

    ' ī���� ����� ������ ���̺��� �̿��� �߻��� Ʈ���� ������ Ȯ��.
    ' lpTriggerCount : ������� ��µ� Ʈ���� ��� ������ ��ȯ, AxcTableSetTriggerCountClear �Լ��� �ʱ�ȭ
    Public Declare Function AxcTableReadTriggerCount Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef lpTriggerCount As Long) As Long

    ' ī���� ����� ������ ���̺� �Ҵ�� H/W Ʈ���� ����Ÿ FIFO�� ���¸� Ȯ��.
    ' lpCount1[0~500] : 2D Ʈ���� ��ġ ����Ÿ �� ù��°(X) ��ġ�� �����ϰ� �ִ� H/W FIFO�� �Էµ� ����Ÿ ����
    ' upStatus1 : 2D Ʈ���� ��ġ ����Ÿ �� ù��°(X) ��ġ�� �����ϰ� �ִ� H/W FIFO�� ����
    '   [Bit 0] : Data Empty
    '   [Bit 1] : Data Full
    '   [Bit 2] : Data Valid
    ' lpCount2[0~500] : 2D Ʈ���� ��ġ ����Ÿ �� �ι�°(Y) ��ġ�� �����ϰ� �ִ� H/W FIFO�� �Էµ� ����Ÿ ����
    ' upStatus2 : 2D Ʈ���� ��ġ ����Ÿ �� �ι�°(Y) ��ġ�� �����ϰ� �ִ� H/W FIFO�� ����
    '   [Bit 0] : Data Empty
    '   [Bit 1] : Data Full
    '   [Bit 2] : Data Valid
    Public Declare Function AxcTableReadFifoStatus Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef lpCount1 As Long, ByRef upStatus1 As Long, ByRef lpCount2 As Long, ByRef upStatus2 As Long) As Long

    ' ī���� ����� ������ ���̺� �Ҵ�� H/W Ʈ���� ����Ÿ FIFO�� ���� ��ġ ����Ÿ���� Ȯ��.
    ' dpTopData1 : 2D H/W Ʈ���� ����Ÿ FIFO�� ���� ����Ÿ �� ù��°(X) ��ġ ����Ÿ�� Ȯ�� ��
    ' dpTopData1 : 2D H/W Ʈ���� ����Ÿ FIFO�� ���� ����Ÿ �� �ι�°(Y) ��ġ ����Ÿ�� Ȯ�� ��
    Public Declare Function AxcTableReadFifoData Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lTablePos As Long, ByRef dpTopData1 As Double, ByRef dpTopData2 As Double) As Long

    '/



