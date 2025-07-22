Option Strict Off
Option Explicit On
Module AXC

    '*****************************************************************************
    '/****************************************************************************
    '*****************************************************************************
    '**
    '** File Name
    '** ----------
    '**
    '** AXC.VB
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


    '========== ���� �� ��� ����
    ' CNT ����� �ִ��� Ȯ��
    Public Declare Function AxcInfoIsCNTModule Lib "AXL.dll" (ByRef upStatus As Integer) As Integer

    ' CNT ��� No Ȯ��
    Public Declare Function AxcInfoGetModuleNo Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer, ByRef lpModuleNo As Integer) As Integer

    ' CNT ����� ����� ���� Ȯ��
    Public Declare Function AxcInfoGetModuleCount Lib "AXL.dll" (ByRef lpModuleCount As Integer) As Integer

    ' ������ ����� ī���� �Է� ä�� ���� Ȯ��
    Public Declare Function AxcInfoGetChannelCount Lib "AXL.dll" (ByVal lModuleNo As Integer, ByRef lpCount As Integer) As Integer

    ' �ý��ۿ� ������ ī������ �� ä�� ���� Ȯ��
    Public Declare Function AxcInfoGetTotalChannelCount Lib "AXL.dll" (ByRef lpChannelCount As Integer) As Integer

    ' ������ ��� ��ȣ�� ���̽� ���� ��ȣ, ��� ��ġ, ��� ID Ȯ��
    Public Declare Function AxcInfoGetModule Lib "AXL.dll" (ByVal lModuleNo As Integer, ByRef lpBoardNo As Integer, ByRef lpModulePos As Integer, ByRef upModuleID As Integer) As Integer

    ' �ش� ����� ��� ������ �������� ��ȯ�Ѵ�.
    Public Declare Function AxcInfoGetModuleStatus Lib "AXL.dll" (ByVal lModuleNo As Integer) As Integer

    Public Declare Function AxcInfoGetFirstChannelNoOfModuleNo Lib "AXL.dll" (ByVal lModuleNo As Integer, ByRef lpChannelNo As Integer) As Integer
    Public Declare Function AxcInfoGetModuleNoOfChannelNo Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef lpModuleNo As Integer) As Integer

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
    Public Declare Function AxcSignalSetEncInputMethod Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwMethod As Integer) As Integer

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
    Public Declare Function AxcSignalGetEncInputMethod Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpUpMethod As Integer) As Integer

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
    Public Declare Function AxcTriggerSetFunction Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwMode As Integer) As Integer

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
    Public Declare Function AxcTriggerGetFunction Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpMode As Integer) As Integer

    ' dwUsage --> 0x00 : Trigger Not use
    ' dwUsage --> 0x01 : Trigger use
    Public Declare Function AxcTriggerSetNotchEnable Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwUsage As Integer) As Integer

    ' *dwUsage --> 0x00 : Trigger Not use
    ' *dwUsage --> 0x01 : Trigger use
    Public Declare Function AxcTriggerGetNotchEnable Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpUsage As Integer) As Integer


    ' ī���� ����� Capture �ؼ��� ���� �մϴ�.(External latch input polarity)
    ' dwCapturePol --> 0x00 : Signal OFF -> ON
    ' dwCapturePol --> 0x01 : Signal ON -> OFF
    Public Declare Function AxcSignalSetCaptureFunction Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwCapturePol As Integer) As Integer

    ' ī���� ����� Capture �ؼ� ������ Ȯ�� �մϴ�.(External latch input polarity)
    ' *dwCapturePol --> 0x00 : Signal OFF -> ON
    ' *dwCapturePol --> 0x01 : Signal ON -> OFF
    Public Declare Function AxcSignalGetCaptureFunction Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpCapturePol As Integer) As Integer

    ' ī���� ����� Capture ��ġ�� Ȯ�� �մϴ�.(External latch)
    ' *dbpCapturePos --> Capture position ��ġ
    Public Declare Function AxcSignalGetCapturePos Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dbpCapturePos As Double) As Integer

    ' ī���� ����� ī���� ���� Ȯ�� �մϴ�.
    ' *dbpActPos --> ī���� ��
    Public Declare Function AxcStatusGetActPos Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dbpActPos As Double) As Integer

    ' ī���� ����� ī���� ���� dbActPos ������ ���� �մϴ�.
    Public Declare Function AxcStatusSetActPos Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dbActPos As Double) As Integer

    ' ī���� ����� Ʈ���� ��ġ�� �����մϴ�.
    ' ī���� ����� Ʈ���� ��ġ�� 2�������� ���� �� �� �ֽ��ϴ�.
    Public Declare Function AxcTriggerSetNotchPos Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dbLowerPos As Double, ByVal dbUpperPos As Double) As Integer

    ' ī���� ����� ������ Ʈ���� ��ġ�� Ȯ�� �մϴ�.
    Public Declare Function AxcTriggerGetNotchPos Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dbpLowerPos As Double, ByRef dbpUpperPos As Double) As Integer

    ' ī���� ����� Ʈ���� ����� ������ �մϴ�.
    ' dwOutVal --> 0x00 : Ʈ���� ��� '0'
    ' dwOutVal --> 0x01 : Ʈ���� ��� '1'
    Public Declare Function AxcTriggerSetOutput Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwOutVal As Integer) As Integer

    ' ī���� ����� ���¸� Ȯ���մϴ�.
    ' Bit '0' : Carry (ī���� ����ġ�� ���� �޽��� ���� ī���� ����ġ�� �Ѿ� 0�� �ٲ���� �� 1��ĵ�� ON���� �մϴ�.)
    ' Bit '1' : Borrow (ī���� ����ġ�� ���� �޽��� ���� 0�� �Ѿ� ī���� ����ġ�� �ٲ���� �� 1��ĵ�� ON���� �մϴ�.)
    ' Bit '2' : Trigger output status
    ' Bit '3' : Latch input status
    Public Declare Function AxcStatusGetChannel Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpChannelStatus As Integer) As Integer


    ' SIO-CN2CH ���� �Լ���
    '
    ' ī���� ����� ��ġ ������ �����Ѵ�.
    ' ���� ��ġ �̵����� ���� �޽� ������ �����ϴµ�,
    ' ex) 1mm �̵��� 1000�� �ʿ��ϴٸ�dMoveUnitPerPulse = 0.001�� �Է��ϰ�,
    '     ���� ��� �Լ��� ��ġ�� ���õ� ���� mm ������ �����ϸ� �ȴ�.
    Public Declare Function AxcMotSetMoveUnitPerPulse Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dMoveUnitPerPulse As Double) As Integer

    ' ī���� ����� ��ġ ������ Ȯ���Ѵ�.
    Public Declare Function AxcMotGetMoveUnitPerPulse Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dpMoveUnitPerPuls As Double) As Integer

    ' ī���� ����� ���ڴ� �Է� ī���͸� ���� ����� �����Ѵ�.
    ' dwReverse --> 0x00 : �������� ����.
    ' dwReverse --> 0x01 : ����.
    Public Declare Function AxcSignalSetEncReverse Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwReverse As Integer) As Integer

    ' ī���� ����� ���ڴ� �Է� ī���͸� ���� ����� ������ Ȯ���Ѵ�.
    Public Declare Function AxcSignalGetEncReverse Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpReverse As Integer) As Integer

    ' ī���� ����� Encoder �Է� ��ȣ�� �����Ѵ�.
    ' dwSource -->  0x00 : 2(A/B)-Phase ��ȣ.
    ' dwSource -->  0x01 : Z-Phase ��ȣ.(���⼺ ����.)
    Public Declare Function AxcSignalSetEncSource Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwSource As Integer) As Integer

    ' ī���� ����� Encoder �Է� ��ȣ ���� ������ Ȯ���Ѵ�.
    Public Declare Function AxcSignalGetEncSource Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpSource As Integer) As Integer

    ' ī���� ����� Ʈ���� ��� ���� �� ���� ���� �����Ѵ�.
    ' ��ġ �ֱ� Ʈ���� ��ǰ�� ��� ��ġ �ֱ�� Ʈ���� ����� �߻���ų ���� �� ���� ���� �����Ѵ�.
    ' ���� ��ġ Ʈ���� ��ǰ�� ��� Ram ���� ������ Ʈ���� ������ ���� ���� ��ġ�� �����Ѵ�.
    ' ���� : AxcMotSetMoveUnitPerPulse�� ������ ����.
    ' Note : ���Ѱ��� ���Ѱ����� �������� �����Ͽ��� �մϴ�.
    Public Declare Function AxcTriggerSetBlockLowerPos Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dLowerPosition As Double) As Integer

    ' ī���� ����� Ʈ���� ��� ���� �� ���� ���� Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetBlockLowerPos Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dpLowerPosition As Double) As Integer

    ' ī���� ����� Ʈ���� ��� ���� �� ���� ���� �����Ѵ�.
    ' ��ġ �ֱ� Ʈ���� ��ǰ�� ��� ��ġ �ֱ�� Ʈ���� ����� �߻���ų ���� �� ���� ���� �����Ѵ�.
    ' ���� ��ġ Ʈ���� ��ǰ�� ��� Ʈ���� ������ ������ Ram �� ������ ������ Ʈ���� ������ ����Ǵ� ��ġ�� ���ȴ�.
    ' ���� : AxcMotSetMoveUnitPerPulse�� ������ ����.
    ' Note : ���Ѱ��� ���Ѱ����� ū���� �����Ͽ��� �մϴ�.
    Public Declare Function AxcTriggerSetBlockUpperPos Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dUpperPosition As Double) As Integer
    ' ī���� ����� Ʈ���� ��� ���� �� ���� ���� �����Ѵ�.
    Public Declare Function AxcTriggerGetBlockUpperPos Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dpUpperrPosition As Double) As Integer

    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���ſ� ���Ǵ� ��ġ �ֱ⸦ �����Ѵ�.
    ' ���� : AxcMotSetMoveUnitPerPulse�� ������ ����.
    Public Declare Function AxcTriggerSetPosPeriod Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dPeriod As Double) As Integer

    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���ſ� ���Ǵ� ��ġ �ֱ⸦ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPosPeriod Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dpPeriod As Double) As Integer

    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���� ���� ��ġ ������ ���� ��ȿ����� �����Ѵ�.
    ' dwDirection -->  0x00 : ī������ ��/���� ���Ͽ� Ʈ���� �ֱ� ���� ���.
    ' dwDirection -->  0x01 : ī���Ͱ� ���� �Ҷ��� Ʈ���� �ֱ� ���� ���.
    ' dwDirection -->  0x01 : ī���Ͱ� ���� �Ҷ��� Ʈ���� �ֱ� ���� ���.
    Public Declare Function AxcTriggerSetDirectionCheck Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwDirection As Integer) As Integer
    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���� ���� ��ġ ������ ���� ��ȿ��� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetDirectionCheck Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpDirection As Integer) As Integer

    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���� ����� ����, ��ġ �ֱ⸦ �ѹ��� �����Ѵ�.
    ' ��ġ ���� ���� :  AxcMotSetMoveUnitPerPulse�� ������ ����.
    Public Declare Function AxcTriggerSetBlock Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dLower As Double, ByVal dUpper As Double, ByVal dABSod As Double) As Integer

    ' ī���� ����� ��ġ �ֱ� ��� Ʈ���� ����� ����, ��ġ �ֱ⸦ ������ �ѹ��� Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetBlock Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dpLower As Double, ByRef dpUpper As Double, ByRef dpABSod As Double) As Integer

    ' ī���� ����� Ʈ���� ��� �޽� ���� �����Ѵ�.
    ' ���� : uSec
    Public Declare Function AxcTriggerSetTime Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dTrigTime As Double) As Integer

    ' ī���� ����� Ʈ���� ��� �޽� �� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetTime Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dpTrigTime As Double) As Integer

    ' ī���� ����� Ʈ���� ��� �޽��� ��� ������ �����Ѵ�.
    ' dwLevel -->  0x00 : Ʈ���� ��½� 'Low' ���� ���.
    ' dwLevel -->  0x01 : Ʈ���� ��½� 'High' ���� ���.
    Public Declare Function AxcTriggerSetLevel Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwLevel As Integer) As Integer
    ' ī���� ����� Ʈ���� ��� �޽��� ��� ���� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetLevel Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpLevel As Integer) As Integer

    ' ī���� ����� ���ļ� Ʈ���� ��� ��ɿ� �ʿ��� ���ļ��� �����Ѵ�.
    ' ���� : Hz, ���� : 1Hz ~ 500 kHz
    Public Declare Function AxcTriggerSetFreq Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwFreqency As Integer) As Integer
    ' ī���� ����� ���ļ� Ʈ���� ��� ��ɿ� �ʿ��� ���ļ��� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetFreq Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpFreqency As Integer) As Integer

    ' ī���� ����� ���� ä�ο� ���� ���� ��� ���� �����Ѵ�.
    ' dwOutput ���� : 0x00 ~ 0x0F, �� ä�δ� 4���� ���� ���
    Public Declare Function AxcSignalWriteOutput Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwOutput As Integer) As Integer

    ' ī���� ����� ���� ä�ο� ���� ���� ��� ���� Ȯ���Ѵ�.
    Public Declare Function AxcSignalReadOutput Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpOutput As Integer) As Integer

    ' ī���� ����� ���� ä�ο� ���� ���� ��� ���� ��Ʈ ���� �����Ѵ�.
    ' lBitNo ���� : 0 ~ 3, �� ä�δ� 4���� ���� ���
    Public Declare Function AxcSignalWriteOutputBit Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal lBitNo As Integer, ByVal uOnOff As Integer) As Integer
    ' ī���� ����� ���� ä�ο� ���� ���� ��� ���� ��Ʈ ���� Ȯ�� �Ѵ�.
    ' lBitNo ���� : 0 ~ 3
    Public Declare Function AxcSignalReadOutputBit Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal lBitNo As Integer, ByRef upOnOff As Integer) As Integer

    ' ī���� ����� ���� ä�ο� ���� ���� �Է� ���� Ȯ���Ѵ�.
    Public Declare Function AxcSignalReadInput Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpInput As Integer) As Integer

    ' ī���� ����� ���� ä�ο� ���� ���� �Է� ���� ��Ʈ ���� Ȯ�� �Ѵ�.
    ' lBitNo ���� : 0 ~ 3
    Public Declare Function AxcSignalReadInputBit Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal lBitNo As Integer, ByRef upOnOff As Integer) As Integer

    ' ī���� ����� Ʈ���� ����� Ȱ��ȭ �Ѵ�.
    ' ���� ������ ��ɿ� ���� Ʈ���� ����� ���������� ����� ������ �����Ѵ�.
    Public Declare Function AxcTriggerSetEnable Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwUsage As Integer) As Integer

    ' ī���� ����� Ʈ���� ��� Ȱ��ȭ ���� ������ Ȯ���ϴ�.
    Public Declare Function AxcTriggerGetEnable Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpUsage As Integer) As Integer

    ' ī���� ����� ������ġ Ʈ���� ����� ���� ������ RAM ������ Ȯ���Ѵ�.
    ' dwAddr ���� : 0x0000 ~ 0x1FFFF;
    Public Declare Function AxcTriggerReadAbsRamData Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwAddr As Integer, ByRef dwpData As Integer) As Integer

    ' ī���� ����� ������ġ Ʈ���� ����� ���� �ʿ��� RAM ������ �����Ѵ�.
    ' dwAddr ���� : 0x0000 ~ 0x1FFFF;
    Public Declare Function AxcTriggerWriteAbsRamData Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwAddr As Integer, ByVal dwData As Integer) As Integer

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
    Public Declare Function AxcTriggerSetAbs Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwTrigNum As Integer, ByRef dwTrigPos As Integer, ByVal 0 As DWORD dwDirection =) As Integer


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
    Public Declare Function AxcTriggerSetAbsDouble Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwTrigNum As Integer, ByRef dTrigPos As Double, ByVal 0 As DWORD dwDirection =) As Integer

    ' LCM4_10_Version/

    ' ī���� ����� PWM ����� Ȱ��ȭ�Ѵ�.
    Public Declare Function AxcTriggerSetPwmEnable Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal bEnable As Byte) As Integer
    ' ī���� ����� PWM ��� Ȱ��ȭ ���¸� Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPwmEnable Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef bEnable As bool*) As Integer
    ' ī���� ����� PWM ��¸�带 �����Ѵ�.
    ' dwMode : PWM ��¸��
    ' [0] : Manual (Manual�� ������ PWM Data)
    ' [1] : Auto (�ӵ� Table)
    Public Declare Function AxcTriggerSetPwmOutMode Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwMode As Integer) As Integer
    ' ī���� ����� PWM ��¸�带 Ȯ���Ѵ�.
    ' dwMode : PWM ��¸��
    ' [0] : Manual (Manual�� ������ PWM Data)
    ' [1] : Auto (�ӵ� Table)
    Public Declare Function AxcTriggerGetPwmOutMode Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpMode As Integer) As Integer

    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� �ӵ� ������ �����Ѵ�.
    ' dMinVel : dMinVel
    ' dMaxVel : dMaxVel
    ' dVelInterval : �ӵ� ���̺����� ������ �ӵ� Interval
    ' ������ : dMinVel���� dVelInterval �������� �ִ� 5000���� �ӵα����� ������.
    '          (((dMaxVel-dMinVel) / dVelInterval) <= 5000)�� �����Ͽ��� �Ѵ�.
    Public Declare Function AxcTriggerSetPwmVelInfo Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dMinVel As Double, ByVal dMaxVel As Double, ByVal dVelInterval As Double) As Integer
    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� �ӵ� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPwmVelInfo Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dpMinVel As Double, ByRef dpMaxVel As Double, ByRef dpVelInterval As Double) As Integer
    ' ī���� ����� PWM ��¿��� Pulse �� �������� �����Ѵ�.
    ' dwMode : Pulse �� ����
    ' [0] : DutyRatio
    ' [1] : PulseWidth
    Public Declare Function AxcTriggerSetPwmPulseControl Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dwMode As Integer) As Integer
    '  ī���� ����� PWM ��¿��� Pulse ��������� Ȯ�δ�.
    ' dwpMode : Pulse �� ����
    ' [0] : DutyRatio
    ' [1] : PulseWidth
    Public Declare Function AxcTriggerGetPwmPulseControl Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dwpMode As Integer) As Integer

    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ �����Ѵ�.
    ' pwm ��¸�尡 Manual �� ��쿡�� ��ȿ�ϴ�
    ' dFrequency :  (0.017 ~ 1M) ���� ������ �����ϴ�. (Hz ����)
    ' dData : Pulse �� ���� Data �� �Է��ϸ� Pulse Control ��Ŀ� ���� Data ������ �ٸ���.
    ' Pulse �� �������� DutyRatio�� ��� DutyRatio
    ' Pulse �� �������� PulseWidth �� ��� PulseWidth (us����)
    Public Declare Function AxcTriggerSetPwmManualData Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dFrequency As Double, ByVal dData As Double) As Integer
    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPwmManualData Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dpFrequency As Double, ByRef dpData As Double) As Integer
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
    Public Declare Function AxcTriggerSetPwmPatternData Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal lDataCnt As Integer, ByRef dpVel As Double, ByRef dpFrequency As Double, ByRef dpData As Double) As Integer
    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ �����Ѵ�.
    Public Declare Function AxcTriggerSetPwmData Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dVel As Double, ByVal dFrequency As Double, ByVal dData As Double) As Integer
    ' ī���� ����� �� ���̺� 2-D ����ӵ����� PWM ��ȣ�� ����ϱ� ���� �ʿ��� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTriggerGetPwmData Lib "AXL.dll" (ByVal lChannelNo As Integer, ByVal dVel As Double, ByRef dpFrequency As Double, ByRef dpData As Double) As Integer
    ' ī���� ����� �ӵ� ���� Ȯ�� �մϴ�.
    Public Declare Function AxcStatusReadActVel Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dpActVel As Double) As Integer
    ' ī���� ����� 2D �ӵ� ���� Ȯ�� �մϴ�.
    Public Declare Function AxcStatusRead2DActVel Lib "AXL.dll" (ByVal lChannelNo As Integer, ByRef dpActVel As Double) As Integer
    ' ī���� ����� Position ���� �ʱ�ȭ �Ѵ�.
    Public Declare Function AxcStatusSetActPosClear Lib "AXL.dll" (ByVal lChannelNo As Integer) As Integer
    ' HPC4_30_Version
    ' ī���� ����� �� ���̺� �Ҵ�� Ʈ���� ����� ������ �����Ѵ�.
    ' uLevel : Ʈ���� ��� ��ȣ�� Active Level
    '   [0]  : Ʈ���� ��½� 'Low' ���� ���.
    '   [1]  : Ʈ���� ��½� 'High' ���� ���.
    Public Declare Function AxcTableSetTriggerLevel Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByVal uLevel As Integer) As Integer
    ' ī���� ����� �� ���̺� ������ Ʈ���� ����� ���� �������� Ȯ���Ѵ�.
    Public Declare Function AxcTableGetTriggerLevel Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef upLevel As Integer) As Integer

    ' ī���� ����� �� ���̺� �Ҵ�� Ʈ���� ����� �޽� ���� �����Ѵ�.
    ' dTriggerTimeUSec : [Default 500ms], us������ ����
    Public Declare Function AxcTableSetTriggerTime Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByVal dTriggerTimeUSec As Double) As Integer
    ' ī���� ����� �� ���̺� ������ Ʈ���� ����� �޽� �� �������� Ȯ���Ѵ�.
    Public Declare Function AxcTableGetTriggerTime Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef dpTriggerTimeUSec As Double) As Integer

    ' ī���� ����� �� ���̺� �Ҵ� �� 2���� ���ڴ� �Է� ��ȣ�� �����Ѵ�.
    ' uEncoderInput1 [0-3]: ī���� ��⿡ �ԷµǴ� 4���� ���ڴ� ��ȣ�� �ϳ�
    ' uEncoderInput2 [0-3]: ī���� ��⿡ �ԷµǴ� 4���� ���ڴ� ��ȣ�� �ϳ�
    Public Declare Function AxcTableSetEncoderInput Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByVal uEncoderInput1 As Integer, ByVal uEncoderInput2 As Integer) As Integer
    ' ī���� ����� �� ���̺� �Ҵ� �� 2���� ���ڴ� �Է� ��ȣ�� Ȯ���Ѵ�.
    Public Declare Function AxcTableGetEncoderInput Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef upEncoderInput1 As Integer, ByRef upEncoderInput2 As Integer) As Integer

    ' ī���� ����� �� ���̺� �Ҵ� �� Ʈ���� ��� ��Ʈ�� �����Ѵ�.
    ' uTriggerOutport [0x0-0xF]: Bit0: Ʈ���� ��� 0, Bit1: Ʈ���� ��� 1, Bit2: Ʈ���� ��� 2, Bit3: Ʈ���� ��� 3
    ' Ex) 0x3(3)   : ��� 0, 1�� Ʈ���� ��ȣ�� ����ϴ� ���
    '     0xF(255) : ��� 0, 1, 2, 3�� Ʈ���� ��ȣ�� ����ϴ� ���
    Public Declare Function AxcTableSetTriggerOutport Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByVal uTriggerOutport As Integer) As Integer
    ' ī���� ����� �� ���̺� �Ҵ� �� Ʈ���� ��� ��Ʈ�� Ȯ���Ѵ�.
    Public Declare Function AxcTableGetTriggerOutport Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef upTriggerOutport As Integer) As Integer

    ' ī���� ����� �� ���̺� ������ Ʈ���� ��ġ�� ���� ��� ���� ������ �����Ѵ�.
    ' dErrorRange  : ���� ���� Unit������ Ʈ���� ��ġ�� ���� ��� ���� ������ ����
    Public Declare Function AxcTableSetErrorRange Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByVal dErrorRange As Double) As Integer
    ' ī���� ����� �� ���̺� ������ Ʈ���� ��ġ�� ���� ��� ���� ������ Ȯ���Ѵ�.
    Public Declare Function AxcTableGetErrorRange Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef dpErrorRange As Double) As Integer

    ' ī���� ����� �� ���̺� ������ ������(Ʈ���� ��� Port, Ʈ���� �޽� ��) Ʈ���Ÿ� 1�� �߻���Ų��.
    ' �� ���� : 1) Ʈ���Ű� Disable�Ǿ� ������ �� �Լ��� �ڵ����� Enable���� Ʈ���Ÿ� �߻���Ŵ
    '           2) Trigger Mode�� HPC4_PATTERN_TRIGGER ����� ��� �� �Լ��� �ڵ����� Ʈ���� ��带 HPC4_RANGE_TRIGGER�� ���� ��(�ϳ��� Ʈ���Ÿ� �߻���Ű�� ����)
    Public Declare Function AxcTableTriggerOneShot Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer) As Integer

    ' ī���� ����� �� ���̺� ������ ������(Ʈ���� ��� Port, Ʈ���� �޽� ��), ������ ������ŭ ������ ���ļ��� Ʈ���Ÿ� �߻���Ų��.
    ' lTriggerCount     : ������ ���ļ��� �����ϸ� �߻���ų Ʈ���� ��� ����
    ' uTriggerFrequency : Ʈ���Ÿ� �߻���ų ���ļ�
    ' �� ���� : 1) Ʈ���Ű� Disable�Ǿ� ������ �� �Լ��� �ڵ����� Enable���� ������ ���� Ʈ���Ÿ� �߻���Ŵ
    '           2) Trigger Mode�� HPC4_PATTERN_TRIGGER ��尡 �ƴ� ��� �� �Լ��� �ڵ����� Ʈ���� ��带 HPC4_PATTERN_TRIGGER�� ���� ��
    Public Declare Function AxcTableTriggerPatternShot Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByVal lTriggerCount As Integer, ByVal uTriggerFrequency As Integer) As Integer
    ' ī���� ����� �� ���̺� ������ ���� Ʈ���� ���� ������(���ļ�, ī����) Ȯ���Ѵ�.
    Public Declare Function AxcTableGetPatternShotData Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef lpTriggerCount As Integer, ByRef upTriggerFrequency As Integer) As Integer

    ' ī���� ����� �� ���̺� Ʈ���Ÿ� ����ϴ� ����� �����Ѵ�.
    ' uTrigMode : Ʈ���Ÿ� ����ϴ� ����� �����Ѵ�.
    '   [0] HPC4_RANGE_TRIGGER   : ������ Ʈ���� ��ġ�� ������ ��� �����ȿ� ��ġ�� �� Ʈ���Ÿ� ����ϴ� ���
    '   [1] HPC4_VECTOR_TRIGGER  : ���� Ʈ���� ��ġ�� ������ ��� ������ ���� ������ ��ġ�� �� Ʈ���Ÿ� ����ϴ� ���
    '   [3] HPC4_PATTERN_TRIGGER : ��ġ�� �����ϰ� ������ ������ŭ ������ ���ļ��� Ʈ���Ÿ� ����ϴ� ���
    Public Declare Function AxcTableSetTriggerMode Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByVal uTrigMode As Integer) As Integer
    ' ī���� ����� �� ���̺� ������ Ʈ���Ÿ� ����ϴ� ����� Ȯ���Ѵ�
    Public Declare Function AxcTableGetTriggerMode Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef upTrigMode As Integer) As Integer
    ' ī���� ����� �� ���̺� ���� ��µ� ���� Ʈ���� ������ �ʱ�ȭ �Ѵ�.
    Public Declare Function AxcTableSetTriggerCountClear Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer) As Integer

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
    Public Declare Function AxcTableSetTriggerData Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByVal lTriggerDataCount As Integer, ByRef dpTriggerData As Double, ByRef lpTriggerCount As Integer, ByRef dpTriggerInterval As Double) As Integer
    ' ī���� ����� �� ���̺� Ʈ���� ��ȣ�� ����ϱ� ���� ������ Ʈ���� ���� ������ Ȯ���Ѵ�.
    ' �� ���� : �� ���̺� ��ϵ� �ִ� Ʈ���� ����Ÿ ������ �� ���� �Ʒ��� ���� Ʈ���� ����Ÿ ������ �̸� �ľ��� �� ����Ͻʽÿ�.
    ' Ex)      1) AxcTableGetTriggerData(lModuleNo, lTablePos, &lTriggerDataCount, NULL, NULL, NULL);
    '          2) dpTriggerData     = new double[lTriggerDataCount * 2];
    '          3) lpTriggerCount    = new long[lTriggerDataCount];
    '          4) dpTriggerInterval = new double[lTriggerDataCount];
    Public Declare Function AxcTableGetTriggerData Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef lpTriggerDataCount As Integer, ByRef dpTriggerData As Double, ByRef lpTriggerCount As Integer, ByRef dpTriggerInterval As Double) As Integer

    ' ī���� ����� �� ���̺� 2-D ������ġ���� Ʈ���� ��ȣ�� ����ϱ� ���� �ʿ��� ������ AxcTableSetTriggerData�Լ��� �ٸ� ������� �����Ѵ�.
    ' lTriggerDataCount : ���� �� Ʈ���� ������ ��ü ����
    ' uOption : dpTriggerData �迭�� ����Ÿ �Է� ����� ����
    '   [0]   : dpTriggerData �迭�� X Pos[0], Y Pos[0], X Pos[1], Y Pos[1] ������ �Է�
    '   [1]   : dpTriggerData �迭�� X Pos[0], Y Pos[0], Count, Inteval, X Pos[1], Y Pos[1], Count, Inteval ������ �Է�
    ' ������ :
    '    1) dpTriggerData�� �迭 ������ �����Ͽ� ����ؾߵ˴ϴ�. ���ο��� ���Ǵ� ���� ���� ���� �迭�� �����ϸ� �޸� ���� ������ �߻� �� �� ����.
    '    2) Trigger Mode�� HPC4_RANGE_TRIGGER�� �ڵ� �����
    '    3) �Լ� ���ο��� Trigger�� Disable�� �� ��� ������ �����ϸ� �Ϸ� �� �ٽ� Enable ��Ŵ
    Public Declare Function AxcTableSetTriggerDataEx Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByVal lTriggerDataCount As Integer, ByVal uOption As Integer, ByRef dpTriggerData As Double) As Integer
    ' ī���� ����� �� ���̺� Ʈ���� ��ȣ�� ����ϱ� ���� ������ Ʈ���� ���� ������ Ȯ���Ѵ�.
    ' �� ���� : �� ���̺� ��ϵ� �ִ� Ʈ���� ����Ÿ ������ �� ���� �Ʒ��� ���� Ʈ���� ����Ÿ ������ �̸� �ľ��� �� ���.
    ' Ex)      1) AxcTableGetTriggerDataEx(lModuleNo, lTablePos, &lTriggerDataCount, &uOption, NULL);
    '          2) if(uOption == 0) : dpTriggerData     = new double[lTriggerDataCount * 2];
    '          3) if(uOption == 1) : dpTriggerData     = new double[lTriggerDataCount * 4];
    '          4) dpTriggerInterval = new double[lTriggerDataCount];
    Public Declare Function AxcTableGetTriggerDataEx Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef lpTriggerDataCount As Integer, ByRef upOption As Integer, ByRef dpTriggerData As Double) As Integer

    ' ī���� ����� ������ ���̺� ������ ��� Ʈ���� ����Ÿ�� H/W FIFO�� ����Ÿ�� ��� �����Ѵ�.
    Public Declare Function AxcTableSetTriggerDataClear Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer) As Integer

    ' ī���� ����� ������ ���̺��� Ʈ���� ��� ����� ���۽�Ŵ.
    ' uEnable : Ʈ���Ÿ� ��� ����� ��뿩�θ� ����
    ' �� ���� : 1) Ʈ���� ��� �� DISABLE�ϸ� ����� �ٷ� ����
    '           2) AxcTableTriggerOneShot, AxcTableGetPatternShotData,AxcTableSetTriggerData, AxcTableGetTriggerDataEx �Լ� ȣ��� �ڵ����� ENABLE��
    Public Declare Function AxcTableSetEnable Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByVal uEnable As Integer) As Integer
    ' ī���� ����� ������ ���̺��� Ʈ���� ��� ����� ���� ���θ� Ȯ����.
    Public Declare Function AxcTableGetEnable Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef upEnable As Integer) As Integer

    ' ī���� ����� ������ ���̺��� �̿��� �߻��� Ʈ���� ������ Ȯ��.
    ' lpTriggerCount : ������� ��µ� Ʈ���� ��� ������ ��ȯ, AxcTableSetTriggerCountClear �Լ��� �ʱ�ȭ
    Public Declare Function AxcTableReadTriggerCount Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef lpTriggerCount As Integer) As Integer

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
    Public Declare Function AxcTableReadFifoStatus Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef lpCount1 As Integer, ByRef upStatus1 As Integer, ByRef lpCount2 As Integer, ByRef upStatus2 As Integer) As Integer

    ' ī���� ����� ������ ���̺� �Ҵ�� H/W Ʈ���� ����Ÿ FIFO�� ���� ��ġ ����Ÿ���� Ȯ��.
    ' dpTopData1 : 2D H/W Ʈ���� ����Ÿ FIFO�� ���� ����Ÿ �� ù��°(X) ��ġ ����Ÿ�� Ȯ�� ��
    ' dpTopData1 : 2D H/W Ʈ���� ����Ÿ FIFO�� ���� ����Ÿ �� �ι�°(Y) ��ġ ����Ÿ�� Ȯ�� ��
    Public Declare Function AxcTableReadFifoData Lib "AXL.dll" (ByVal lModuleNo As Integer, ByVal lTablePos As Integer, ByRef dpTopData1 As Double, ByRef dpTopData2 As Double) As Integer

    '/



End Module
