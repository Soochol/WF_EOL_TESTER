'*****************************************************************************
'/****************************************************************************
'*****************************************************************************
'**
'** File Name
'** ----------
'**
'** AXL.BAS
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

Attribute VB_Name = "AXL"


    '========== 라이브러리 초기화 =========================================================================

    ' 라이브러리 초기화
    Public Declare Function AxlOpen Lib "AXL.dll" (ByVal lIrqNo As Long) As Long

    ' 라이브러리 초기화시 하드웨어 칩에 리셋을 하지 않음.
    Public Declare Function AxlOpenNoReset Lib "AXL.dll" (ByVal lIrqNo As Long) As Long

    ' 라이브러리 사용을 종료
    Public Declare Function AxlClose Lib "AXL.dll" () As Byte

    ' 라이브러리가 초기화 되어 있는 지 확인
    Public Declare Function AxlIsOpened Lib "AXL.dll" () As Byte

    ' 인터럽트를 사용한다.
    Public Declare Function AxlInterruptEnable Lib "AXL.dll" () As Long

    ' 인터럽트를 사용안한다.
    Public Declare Function AxlInterruptDisable Lib "AXL.dll" () As Long

    '========== 라이브러리 및 베이스 보드 정보 ============================================================
    ' 등록된 베이스 보드의 개수 확인
    Public Declare Function AxlGetBoardCount Lib "AXL.dll" (ByRef lpBoardCount As Long) As Long
    ' 라이브러리 버전 확인, szVersion[64]
    Public Declare Function AxlGetLibVersion Lib "AXL.dll" (ByRef szVersion As char*) As Long

    ' Network제품의 각 모듈별 연결상태를 확인하는 함수
    Public Declare Function AxlGetModuleNodeStatus Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long) As Long

    ' 해당 보드가 제어 가능한 상태인지 반환한다.
    Public Declare Function AxlGetBoardStatus Lib "AXL.dll" (ByVal lBoardNo As Long) As Long

    ' Network 제품의 Configuration Lock 상태를 반환한다.
    ' *wpLockMode  : DISABLE(0), ENABLE(1)
    Public Declare Function AxlGetLockMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef wpLockMode As Long) As Long

    ' 반환값에 대한 설명을 반환한다.
    Public Declare Function AxlGetReturnCodeInfo Lib "AXL.dll" (ByVal dwReturnCode As Long, ByVal lReturnInfoSize As Long, ByRef lpRecivedSize As Long, ByRef szReturnInfo As char*) As Long

    '========== 로그 레벨 =================================================================================
    ' EzSpy에 출력할 메시지 레벨 설정
    ' uLevel : 0 - 3 설정
    ' LEVEL_NONE(0)    : 모든 메시지를 출력하지 않는다.
    ' LEVEL_ERROR(1)   : 에러가 발생한 메시지만 출력한다.
    ' LEVEL_RUNSTOP(2) : 모션에서 Run / Stop 관련 메시지를 출력한다.
    ' LEVEL_FUNCTION(3): 모든 메시지를 출력한다.
    Public Declare Function AxlSetLogLevel Lib "AXL.dll" (ByVal uLevel As Long) As Long
    ' EzSpy에 출력할 메시지 레벨 확인
    Public Declare Function AxlGetLogLevel Lib "AXL.dll" (ByRef upLevel As Long) As Long

    '========== MLIII =================================================================================
    ' Network제품의 각 모듈을 검색을 시작하는 함수
    Public Declare Function AxlScanStart Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lNet As Long) As Long
    ' Network제품 각 보드의 모든 모듈을 connect하는 함수
    Public Declare Function AxlBoardConnect Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lNet As Long) As Long
    ' Network제품 각 보드의 모든 모듈을 Disconnect하는 함수
    Public Declare Function AxlBoardDisconnect Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lNet As Long) As Long

    '========== SIIIH =================================================================================
    ' SIIIH 마스터 보드에 연결된 모듈에 대한 검색을 시작하는 함수(SIIIH 마스터 보드 전용)
    Public Declare Function AxlScanStartSIIIH Lib "AXL.dll" (ByRef pScanResult = NULL As SCAN_RESULT*) As Long

    '========== Fan Control ===============================================================================
    ' 보드에 장착되어 있는 Fan의 속도(rpm)를 확인한다.
    Public Declare Function AxlReadFanSpeed Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dpFanSpeed As Double) As Long

    '========== EzSpy =================================================================================
    ' EzSpy User Log(Max length : 200 Bytes)
    Public Declare Function AxlEzSpyUserLog Lib "AXL.dll" (ByRef szUserLog As char*) As Long


