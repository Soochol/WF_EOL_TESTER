Option Strict Off
Option Explicit On
Module AXL

    '*****************************************************************************
    '/****************************************************************************
    '*****************************************************************************
    '**
    '** File Name
    '** ----------
    '**
    '** AXL.VB
    '**
    '** COPYRIGHT (c) AJINEXTEK Co., LTD
    '**
    '*****************************************************************************
    '*****************************************************************************
    '**
    '** Description
    '** -----------
    '** Ajinextek Library Header File
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


    '========== ���̺귯�� �ʱ�ȭ =========================================================================

    ' ���̺귯�� �ʱ�ȭ
    Public Declare Function AxlOpen Lib "AXL.dll" (ByVal lIrqNo As Integer) As Integer

    ' ���̺귯�� �ʱ�ȭ�� �ϵ���� Ĩ�� ������ ���� ����.
    Public Declare Function AxlOpenNoReset Lib "AXL.dll" (ByVal lIrqNo As Integer) As Integer

    ' ���̺귯�� ����� ����
    Public Declare Function AxlClose Lib "AXL.dll" () As Byte

    ' ���̺귯���� �ʱ�ȭ �Ǿ� �ִ� �� Ȯ��
    Public Declare Function AxlIsOpened Lib "AXL.dll" () As Byte

    ' ���ͷ�Ʈ�� ����Ѵ�.
    Public Declare Function AxlInterruptEnable Lib "AXL.dll" () As Integer

    ' ���ͷ�Ʈ�� �����Ѵ�.
    Public Declare Function AxlInterruptDisable Lib "AXL.dll" () As Integer

    '========== ���̺귯�� �� ���̽� ���� ���� ============================================================
    ' ��ϵ� ���̽� ������ ���� Ȯ��
    Public Declare Function AxlGetBoardCount Lib "AXL.dll" (ByRef lpBoardCount As Integer) As Integer
    ' ���̺귯�� ���� Ȯ��, szVersion[64]
    Public Declare Function AxlGetLibVersion Lib "AXL.dll" (ByRef szVersion As char*) As Integer

    ' Network��ǰ�� �� ��⺰ ������¸� Ȯ���ϴ� �Լ�
    Public Declare Function AxlGetModuleNodeStatus Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lModulePos As Integer) As Integer

    ' �ش� ���尡 ���� ������ �������� ��ȯ�Ѵ�.
    Public Declare Function AxlGetBoardStatus Lib "AXL.dll" (ByVal lBoardNo As Integer) As Integer

    ' Network ��ǰ�� Configuration Lock ���¸� ��ȯ�Ѵ�.
    ' *wpLockMode  : DISABLE(0), ENABLE(1)
    Public Declare Function AxlGetLockMode Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef wpLockMode As Integer) As Integer

    ' ��ȯ���� ���� ������ ��ȯ�Ѵ�.
    Public Declare Function AxlGetReturnCodeInfo Lib "AXL.dll" (ByVal dwReturnCode As Integer, ByVal lReturnInfoSize As Integer, ByRef lpRecivedSize As Integer, ByRef szReturnInfo As char*) As Integer

    '========== �α� ���� =================================================================================
    ' EzSpy�� ����� �޽��� ���� ����
    ' uLevel : 0 - 3 ����
    ' LEVEL_NONE(0)    : ��� �޽����� ������� �ʴ´�.
    ' LEVEL_ERROR(1)   : ������ �߻��� �޽����� ����Ѵ�.
    ' LEVEL_RUNSTOP(2) : ��ǿ��� Run / Stop ���� �޽����� ����Ѵ�.
    ' LEVEL_FUNCTION(3): ��� �޽����� ����Ѵ�.
    Public Declare Function AxlSetLogLevel Lib "AXL.dll" (ByVal uLevel As Integer) As Integer
    ' EzSpy�� ����� �޽��� ���� Ȯ��
    Public Declare Function AxlGetLogLevel Lib "AXL.dll" (ByRef upLevel As Integer) As Integer

    '========== MLIII =================================================================================
    ' Network��ǰ�� �� ����� �˻��� �����ϴ� �Լ�
    Public Declare Function AxlScanStart Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lNet As Integer) As Integer
    ' Network��ǰ �� ������ ��� ����� connect�ϴ� �Լ�
    Public Declare Function AxlBoardConnect Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lNet As Integer) As Integer
    ' Network��ǰ �� ������ ��� ����� Disconnect�ϴ� �Լ�
    Public Declare Function AxlBoardDisconnect Lib "AXL.dll" (ByVal lBoardNo As Integer, ByVal lNet As Integer) As Integer

    '========== SIIIH =================================================================================
    ' SIIIH ������ ���忡 ����� ��⿡ ���� �˻��� �����ϴ� �Լ�(SIIIH ������ ���� ����)
    Public Declare Function AxlScanStartSIIIH Lib "AXL.dll" (ByRef pScanResult = NULL As SCAN_RESULT*) As Integer

    '========== Fan Control ===============================================================================
    ' ���忡 �����Ǿ� �ִ� Fan�� �ӵ�(rpm)�� Ȯ���Ѵ�.
    Public Declare Function AxlReadFanSpeed Lib "AXL.dll" (ByVal lBoardNo As Integer, ByRef dpFanSpeed As Double) As Integer

    '========== EzSpy =================================================================================
    ' EzSpy User Log(Max length : 200 Bytes)
    Public Declare Function AxlEzSpyUserLog Lib "AXL.dll" (ByRef szUserLog As char*) As Integer


End Module
