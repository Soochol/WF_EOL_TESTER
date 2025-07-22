
Attribute VB_Name = "AXDev"


    ' Board Number를 이용하여 Board Address 찾기
    Public Declare Function AxlGetBoardAddress Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef upBoardAddress As Long) As Long
    ' Board Number를 이용하여 Board ID 찾기
    Public Declare Function AxlGetBoardID Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef upBoardID As Long) As Long
    ' Board Number를 이용하여 Board Version 찾기
    Public Declare Function AxlGetBoardVersion Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef upBoardVersion As Long) As Long
    ' Board Number와 Module Position을 이용하여 Module ID 찾기
    Public Declare Function AxlGetModuleID Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef upModuleID As Long) As Long
    ' Board Number와 Module Position을 이용하여 Module Version 찾기
    Public Declare Function AxlGetModuleVersion Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef upModuleVersion As Long) As Long
    ' Board Number와 Module Position을 이용하여 Network Node 정보 확인
    Public Declare Function AxlGetModuleNodeInfo Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef upNetNo As Long, ByRef upNodeAddr As Long) As Long

    ' Board에 내장된 범용 Data Flash Write (PCI-R1604[RTEX master board]전용)
    ' lPageAddr(0 ~ 199)
    ' lByteNum(1 ~ 120)
    ' 주의) Flash에 데이타를 기입할 때는 일정 시간(최대 17mSec)이 소요되기때문에 연속 쓰기시 지연 시간이 필요함.
    Public Declare Function AxlSetDataFlash Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lPageAddr As Long, ByVal lBytesNum As Long, ByRef bpSetData As Byte) As Long

    ' Board에 내장된 ESTOP 외부 입력 신호를 이용한 InterLock 기능 사용 유무 및 디지털 필터 상수값 정의 (PCI-Rxx00[MLIII master board]전용)
    ' 1. 사용 유무
    '   설명: 기능 사용 설정후 외부에서 ESTOP 신호 인가시 보드에 연결된 모션 제어 노드에 대해서 ESTOP 구동 명령 실행
    '    0: 기능 사용하지 않음(기본 설정값)
    '    1: 기능 사용
    ' 2. 디지털 필터 값
    '      입력 필터 상수 설정 범위 1 ~ 40, 단위 통신 Cyclic time
    ' Board 에 dwInterLock, dwDigFilterVal을 이용하여 EstopInterLock 기능 설정
    Public Declare Function AxlSetEStopInterLock Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwInterLock As Long, ByVal dwDigFilterVal As Long) As Long
    ' Board에 설정된 dwInterLock, dwDigFilterVal 정보를 가져오기
    Public Declare Function AxlGetEStopInterLock Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwInterLock As Long, ByRef dwDigFilterVal As Long) As Long
    ' Board에 입력된 EstopInterLock 신호를 읽는다.
    Public Declare Function AxlReadEStopInterLock Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwInterLock As Long) As Long

    ' Board에 내장된 범용 Data Flash Read(PCI-R1604[RTEX master board]전용)
    ' lPageAddr(0 ~ 199)
    ' lByteNum(1 ~ 120)
    Public Declare Function AxlGetDataFlash Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lPageAddr As Long, ByVal lBytesNum As Long, ByRef bpGetData As Byte) As Long

    ' Board Number와 Module Position을 이용하여 AIO Module Number 찾기
    Public Declare Function AxaInfoGetModuleNo Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef lpModuleNo As Long) As Long
    ' Board Number와 Module Position을 이용하여 DIO Module Number 찾기
    Public Declare Function AxdInfoGetModuleNo Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByRef lpModuleNo As Long) As Long

    ' 지정 축에 IPCOMMAND Setting
    Public Declare Function AxmSetCommand Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte) As Long
    ' 지정 축에 8bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData08 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' 지정 축에 8bit IPCOMMAND 가져오기
    Public Declare Function AxmGetCommandData08 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' 지정 축에 16bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData16 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' 지정 축에 16bit IPCOMMAND 가져오기
    Public Declare Function AxmGetCommandData16 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' 지정 축에 24bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData24 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' 지정 축에 24bit IPCOMMAND 가져오기
    Public Declare Function AxmGetCommandData24 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' 지정 축에 32bit IPCOMMAND Setting
    Public Declare Function AxmSetCommandData32 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' 지정 축에 32bit IPCOMMAND 가져오기
    Public Declare Function AxmGetCommandData32 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long

    ' 지정 축에 QICOMMAND Setting
    Public Declare Function AxmSetCommandQi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte) As Long
    ' 지정 축에 8bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData08Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' 지정 축에 8bit QICOMMAND 가져오기
    Public Declare Function AxmGetCommandData08Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' 지정 축에 16bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData16Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' 지정 축에 16bit QICOMMAND 가져오기
    Public Declare Function AxmGetCommandData16Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' 지정 축에 24bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData24Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' 지정 축에 24bit QICOMMAND 가져오기
    Public Declare Function AxmGetCommandData24Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long
    ' 지정 축에 32bit QICOMMAND Setting
    Public Declare Function AxmSetCommandData32Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByVal uData As Long) As Long
    ' 지정 축에 32bit QICOMMAND 가져오기
    Public Declare Function AxmGetCommandData32Qi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sCommand As Byte, ByRef upData As Long) As Long

    ' 지정 축에 Port Data 가져오기 - IP
    Public Declare Function AxmGetPortData Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wOffset As Long, ByRef upData As Long) As Long
    ' 지정 축에 Port Data Setting - IP
    Public Declare Function AxmSetPortData Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wOffset As Long, ByVal dwData As Long) As Long
    ' 지정 축에 Port Data 가져오기 - QI
    Public Declare Function AxmGetPortDataQi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal byOffset As Long, ByRef wData As Long) As Long
    ' 지정 축에 Port Data Setting - QI
    Public Declare Function AxmSetPortDataQi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal byOffset As Long, ByVal wData As Long) As Long

    ' 지정 축에 스크립트를 설정한다. - IP
    ' sc    : 스크립트 번호 (1 - 4)
    ' event : 발생할 이벤트 SCRCON 을 정의한다.
    '         이벤트 설정 축갯수설정, 이벤트 발생할 축, 이벤트 내용 1,2 속성 설정한다.
    ' cmd   : 어떤 내용을 바꿀것인지 선택 SCRCMD를 정의한다.
    ' data  : 어떤 Data를 바꿀것인지 선택
    Public Declare Function AxmSetScriptCaptionIp Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sc As Long, ByVal event As Long, ByVal data As Long) As Long
    ' 지정 축에 스크립트를 반환한다. - IP
    Public Declare Function AxmGetScriptCaptionIp Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sc As Long, ByRef event As Long, ByRef data As Long) As Long

    ' 지정 축에 스크립트를 설정한다. - QI
    ' sc    : 스크립트 번호 (1 - 4)
    ' event : 발생할 이벤트 SCRCON 을 정의한다.
    '         이벤트 설정 축갯수설정, 이벤트 발생할 축, 이벤트 내용 1,2 속성 설정한다.
    ' cmd   : 어떤 내용을 바꿀것인지 선택 SCRCMD를 정의한다.
    ' data  : 어떤 Data를 바꿀것인지 선택
    Public Declare Function AxmSetScriptCaptionQi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sc As Long, ByVal event As Long, ByVal cmd As Long, ByVal data As Long) As Long
    ' 지정 축에 스크립트를 반환한다. - QI
    Public Declare Function AxmGetScriptCaptionQi Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal sc As Long, ByRef event As Long, ByRef cmd As Long, ByRef data As Long) As Long

    ' 지정 축에 스크립트 내부 Queue Index를 Clear 시킨다.
    ' uSelect IP.
    ' uSelect(0): 스크립트 Queue Index 를 Clear한다.
    '        (1): 캡션 Queue를 Index Clear한다.
    ' uSelect QI.
    ' uSelect(0): 스크립트 Queue 1 Index 을 Clear한다.
    '        (1): 스크립트 Queue 2 Index 를 Clear한다.
    Public Declare Function AxmSetScriptCaptionQueueClear Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal uSelect As Long) As Long

    ' 지정 축에 스크립트 내부 Queue의 Index 반환한다.
    ' uSelect IP
    ' uSelect(0): 스크립트 Queue Index를 읽어온다.
    '        (1): 캡션 Queue Index를 읽어온다.
    ' uSelect QI.
    ' uSelect(0): 스크립트 Queue 1 Index을 읽어온다.
    '        (1): 스크립트 Queue 2 Index를 읽어온다.
    Public Declare Function AxmGetScriptCaptionQueueCount Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef updata As Long, ByVal uSelect As Long) As Long

    ' 지정 축에 스크립트 내부 Queue의 Data갯수 반환한다.
    ' uSelect IP
    ' uSelect(0): 스크립트 Queue Data 를 읽어온다.
    '        (1): 캡션 Queue Data를 읽어온다.
    ' uSelect QI.
    ' uSelect(0): 스크립트 Queue 1 Data 읽어온다.
    '        (1): 스크립트 Queue 2 Data 읽어온다.
    Public Declare Function AxmGetScriptCaptionQueueDataCount Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef updata As Long, ByVal uSelect As Long) As Long

    ' 내부 데이타를 읽어온다.
    Public Declare Function AxmGetOptimizeDriveData Lib "AXL.dll" () As Long


    ' 보드내에 레지스터를 Byte단위로 설정 및 확인한다.
    Public Declare Function AxmBoardWriteByte Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByVal byData As Byte) As Long
    Public Declare Function AxmBoardReadByte Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByRef byData As Byte) As Long

    ' 보드내에 레지스터를 Word단위로 설정 및 확인한다.
    Public Declare Function AxmBoardWriteWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByVal wData As Long) As Long
    Public Declare Function AxmBoardReadWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByRef wData As Long) As Long

    ' 보드내에 레지스터를 DWord단위로 설정 및 확인한다.
    Public Declare Function AxmBoardWriteDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByVal dwData As Long) As Long
    Public Declare Function AxmBoardReadDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByRef dwData As Long) As Long

    ' 보드내에 모듈에 레지스터를 Byte설정 및 확인한다.
    Public Declare Function AxmModuleWriteByte Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByVal byData As Byte) As Long
    Public Declare Function AxmModuleReadByte Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByRef byData As Byte) As Long

    ' 보드내에 모듈에 레지스터를 Word설정 및 확인한다.
    Public Declare Function AxmModuleWriteWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByVal wData As Long) As Long
    Public Declare Function AxmModuleReadWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByRef wData As Long) As Long

    ' 보드내에 모듈에 레지스터를 DWord설정 및 확인한다.
    Public Declare Function AxmModuleWriteDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByVal dwData As Long) As Long
    Public Declare Function AxmModuleReadDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModulePos As Long, ByVal wOffset As Long, ByRef dwData As Long) As Long

    ' 외부 위치 비교기에 값을 설정한다.(Pos = Unit)
    Public Declare Function AxmStatusSetActComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPos As Double) As Long
    ' 외부 위치 비교기에 값을 반환한다.(Positon = Unit)
    Public Declare Function AxmStatusGetActComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dpPos As Double) As Long

    ' 내부 위치 비교기에 값을 설정한다.(Pos = Unit)
    Public Declare Function AxmStatusSetCmdComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPos As Double) As Long
    ' 내부 위치 비교기에 값을 반환한다.(Pos = Unit)
    Public Declare Function AxmStatusGetCmdComparatorPos Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dpPos As Double) As Long
    ' ABS Position 을 Flash 에 설정한다.
    Public Declare Function AxmStatusSetFlashAbsOffset Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPosition As Long) As Long
    ' Flash 에 저장 된 ABS Position 을 반환한다.
    ' dReadType  : Value in Flash Memory (0), Real used Value in memory(1)
    Public Declare Function AxmStatusGetFlashAbsOffset Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dPosition As Long, ByVal dReadType As Long) As Long
    ' 사용자가 Flash 에 ABS Position 저장할 수 있는 옵션을 설정한다.
    Public Declare Function AxmStatusSetAbsOffsetWriteEnable Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bStatus As Byte) As Long
    ' ABS Position 설정 옵션의 상태를 반환한다.
    Public Declare Function AxmStatusGetAbsOffsetWriteEnable Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef bpStatus As bool*) As Long

    '========== 추가 함수 =========================================================================================================
    ' 직선 보간 을 속도만 가지고 무한대로 증가한다.
    ' 속도 비율대로 거리를 넣어주어야 한다.
    Public Declare Function AxmLineMoveVel Lib "AXL.dll" (ByVal lCoord As Long, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Long

    '========= 센서 위치 구동 함수( 필독: IP만가능 , QI에는 기능없음)==============================================================
    ' 지정 축의 Sensor 신호의 사용 유무 및 신호 입력 레벨을 설정한다.
    ' 사용 유무 LOW(0), HIGH(1), UNUSED(2), USED(3)
    Public Declare Function AxmSensorSetSignal Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal uLevel As Long) As Long
    ' 지정 축의 Sensor 신호의 사용 유무 및 신호 입력 레벨을 반환한다.
    Public Declare Function AxmSensorGetSignal Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upLevel As Long) As Long
    ' 지정 축의 Sensor 신호의 입력 상태를 반환한다
    Public Declare Function AxmSensorReadSignal Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upStatus As Long) As Long

    ' 지정 축의 설정된 속도와 가속율로 센서 위치 드라이버를 구동한다.
    ' Sensor 신호의 Active level입력 이후 상대 좌표로 설정된 거리만큼 구동후 정지한다.
    ' 펄스가 출력되는 시점에서 함수를 벗어난다.
    ' lMethod :  0 - 일반 구동, 1 - 센서 신호 검출 전은 저속 구동. 신호 검출 후 일반 구동
    '            2 - 저속 구동
    Public Declare Function AxmSensorMovePos Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPos As Double, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal lMethod As Long) As Long

    ' 지정 축의 설정된 속도와 가속율로 센서 위치 드라이버를 구동한다.
    ' Sensor 신호의 Active level입력 이후 상대 좌표로 설정된 거리만큼 구동후 정지한다.
    ' 펄스 출력이 종료되는 시점에서 함수를 벗어난다.
    Public Declare Function AxmSensorStartMovePos Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPos As Double, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal lMethod As Long) As Long

    ' 원점검색 진행스탭 변화의 기록을 반환한다.
    ' *lpStepCount      : 기록된 Step의 개수
    ' *upMainStepNumber : 기록된 MainStepNumber 정보의 배열포인트
    ' *upStepNumber     : 기록된 StepNumber 정보의 배열포인트
    ' *upStepBranch     : 기록된 Step별 Branch 정보의 배열포인트
    ' 주의: 배열개수는 50개로 고정
    Public Declare Function AxmHomeGetStepTrace Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef lpStepCount As Long, ByRef upMainStepNumber As Long, ByRef upStepNumber As Long, ByRef upStepBranch As Long) As Long

    '=======추가 홈 서치 (PI-N804/404에만 해당됨.)=================================================================================
    ' 사용자가 지정한 축의 홈설정 파라메타를 설정한다.(QI칩 전용 레지스터 이용).
    ' uZphasCount : 홈 완료후에 Z상 카운트(0 - 15)
    ' lHomeMode   : 홈 설정 모드( 0 - 12)
    ' lClearSet   : 위치 클리어 , 잔여펄스 클리어 사용 선택 (0 - 3)
    '               0: 위치클리어 사용않함, 잔여펄스 클리어 사용 안함
    '                 1: 위치클리어 사용함, 잔여펄스 클리어 사용 안함
    '               2: 위치클리어 사용안함, 잔여펄스 클리어 사용함
    '               3: 위치클리어 사용함, 잔여펄스 클리어 사용함.
    ' dOrgVel : 홈관련 Org  Speed 설정
    ' dLastVel: 홈관련 Last Speed 설정
    Public Declare Function AxmHomeSetConfig Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal uZphasCount As Long, ByVal lHomeMode As Long, ByVal lClearSet As Long, ByVal dOrgVel As Double, ByVal dLastVel As Double, ByVal dLeavePos As Double) As Long
    ' 사용자가 지정한 축의 홈설정 파라메타를 반환한다.
    Public Declare Function AxmHomeGetConfig Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upZphasCount As Long, ByRef lpHomeMode As Long, ByRef lpClearSet As Long, ByRef dpOrgVel As Double, ByRef dpLastVel As Double, ByRef dpLeavePos As Double) As Long

    ' 사용자가 지정한 축의 홈 서치를 시작한다.
    ' lHomeMode 사용시 설정 : 0 - 5 설정 (Move Return후에 Search를  시작한다.)
    ' lHomeMode -1로 그대로 사용시 HomeConfig에서 사용한대로 그대로 설정됨.
    ' 구동방향      : Vel값이 양수이면 CW, 음수이면 CCW.
    Public Declare Function AxmHomeSetMoveSearch Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Long

    ' 사용자가 지정한 축의 홈 리턴을 시작한다.
    ' lHomeMode 사용시 설정 : 0 - 12 설정
    ' lHomeMode -1로 그대로 사용시 HomeConfig에서 사용한대로 그대로 설정됨.
    ' 구동방향      : Vel값이 양수이면 CW, 음수이면 CCW.
    Public Declare Function AxmHomeSetMoveReturn Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Long

    ' 사용자가 지정한 축의 홈 이탈을 시작한다.
    ' 구동방향      : Vel값이 양수이면 CW, 음수이면 CCW.
    Public Declare Function AxmHomeSetMoveLeave Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dVel As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Long

    ' 사용자가 지정한 다축의 홈 서치을 시작한다.
    ' lHomeMode 사용시 설정 : 0 - 5 설정 (Move Return후에 Search를  시작한다.)
    ' lHomeMode -1로 그대로 사용시 HomeConfig에서 사용한대로 그대로 설정됨.
    ' 구동방향      : Vel값이 양수이면 CW, 음수이면 CCW.
    Public Declare Function AxmHomeSetMultiMoveSearch Lib "AXL.dll" (ByVal lArraySize As Long, ByRef lpAxesNo As Long, ByRef dpVel As Double, ByRef dpAccel As Double, ByRef dpDecel As Double) As Long

    '지정된 좌표계의 구동 속도 프로파일 모드를 설정한다.
    ' (주의점 : 반드시 축맵핑 하고 사용가능)
    ' ProfileMode : '0' - 대칭 Trapezode
    '               '1' - 비대칭 Trapezode
    '               '2' - 대칭 Quasi-S Curve
    '               '3' - 대칭 S Curve
    '               '4' - 비대칭 S Curve
    Public Declare Function AxmContiSetProfileMode Lib "AXL.dll" (ByVal lCoord As Long, ByVal uProfileMode As Long) As Long
    ' 지정된 좌표계의 구동 속도 프로파일 모드를 반환한다.
    Public Declare Function AxmContiGetProfileMode Lib "AXL.dll" (ByVal lCoord As Long, ByRef upProfileMode As Long) As Long

    '========== DIO 인터럽트 플래그 레지스트 읽기
    ' 지정한 입력 접점 모듈, Interrupt Flag Register의 Offset 위치에서 bit 단위로 인터럽트 발생 상태 값을 읽음
    Public Declare Function AxdiInterruptFlagReadBit Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lOffset As Long, ByRef upValue As Long) As Long
    ' 지정한 입력 접점 모듈, Interrupt Flag Register의 Offset 위치에서 byte 단위로 인터럽트 발생 상태 값을 읽음
    Public Declare Function AxdiInterruptFlagReadByte Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lOffset As Long, ByRef upValue As Long) As Long
    ' 지정한 입력 접점 모듈, Interrupt Flag Register의 Offset 위치에서 word 단위로 인터럽트 발생 상태 값을 읽음
    Public Declare Function AxdiInterruptFlagReadWord Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lOffset As Long, ByRef upValue As Long) As Long
    ' 지정한 입력 접점 모듈, Interrupt Flag Register의 Offset 위치에서 double word 단위로 인터럽트 발생 상태 값을 읽음
    Public Declare Function AxdiInterruptFlagReadDword Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal lOffset As Long, ByRef upValue As Long) As Long
    ' 전체 입력 접점 모듈, Interrupt Flag Register의 Offset 위치에서 bit 단위로 인터럽트 발생 상태 값을 읽음
    Public Declare Function AxdiInterruptFlagRead Lib "AXL.dll" (ByVal lOffset As Long, ByRef upValue As Long) As Long

    '========= 로그 관련 함수 ==========================================================================================
    ' 현재 자동으로 설정됨.
    ' 설정 축의 함수 실행 결과를 EzSpy에서 모니터링 할 수 있도록 설정 또는 해제하는 함수이다.
    ' uUse : 사용 유무 => DISABLE(0), ENABLE(1)
    Public Declare Function AxmLogSetAxis Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal uUse As Long) As Long

    ' EzSpy에서의 설정 축 함수 실행 결과 모니터링 여부를 확인하는 함수이다.
    Public Declare Function AxmLogGetAxis Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upUse As Long) As Long

    '=========== 로그 출력 관련 함수
    '지정한 입력 채널의 EzSpy에 로그 출력 여부를 설정한다.
    Public Declare Function AxaiLogSetChannel Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal uUse As Long) As Long
    '지정한 입력 채널의 EzSpy에 로그 출력 여부를 확인한다.
    Public Declare Function AxaiLogGetChannel Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef upUse As Long) As Long

    '==지정한 출력 채널의 EzSpy 로그 출력
    '지정한 출력 채널의 EzSpy에 로그 출력 여부를 설정한다.
    Public Declare Function AxaoLogSetChannel Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal uUse As Long) As Long
    '지정한 출력 채널의 EzSpy에 로그 출력 여부를 확인한다.
    Public Declare Function AxaoLogGetChannel Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef upUse As Long) As Long

    '==Log
    ' 지정한 모듈의 EzSpy에 로그 출력 여부 설정
    Public Declare Function AxdLogSetModule Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal uUse As Long) As Long
    ' 지정한 모듈의 EzSpy에 로그 출력 여부 확인
    Public Declare Function AxdLogGetModule Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef upUse As Long) As Long

    ' 지정한 보드가 RTEX 모드일 때 그 보드의 firmware 버전을 확인한다.
    Public Declare Function AxlGetFirmwareVersion Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef szVersion As String) As Long
    ' 지정한 보드로 Firmware를 전송 한다.
    Public Declare Function AxlSetFirmwareCopy Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef wData As Long, ByRef wCmdData As Long) As Long
    ' 지정한 보드로 Firmware Update를 수행한다.
    Public Declare Function AxlSetFirmwareUpdate Lib "AXL.dll" (ByVal lBoardNo As Long) As Long
    ' 지정한 보드의 현재 RTEX 초기화 상태를 확인 한다.
    Public Declare Function AxlCheckStatus Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwStatus As Long) As Long
    ' 지정한 축에 RTEX Master board에 범용 명령을 실행 합니다.
    Public Declare Function AxlRtexUniversalCmd Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wCmd As Long, ByVal wOffset As Long, ByRef wData As Long) As Long
    ' 지정한 축의 RTEX 통신 명령을 실행한다.
    Public Declare Function AxmRtexSlaveCmd Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwCmdCode As Long, ByVal dwTypeCode As Long, ByVal dwIndexCode As Long, ByVal dwCmdConfigure As Long, ByVal dwValue As Long) As Long
    ' 지정한 축에 실행한 RTEX 통신 명령의 결과값을 확인한다.
    Public Declare Function AxmRtexGetSlaveCmdResult Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwIndex As Long, ByRef dwValue As Long) As Long
    ' 지정한 축에 실행한 RTEX 통신 명령의 결과값을 확인한다. PCIE-Rxx04-RTEX 전용
    Public Declare Function AxmRtexGetSlaveCmdResultEx Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpCommand As Long, ByRef dwpType As Long, ByRef dwpIndex As Long, ByRef dwpValue As Long) As Long
    ' 지정한 축에 RTEX 상태 정보를 확인한다.
    Public Declare Function AxmRtexGetAxisStatus Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwStatus As Long) As Long
    ' 지정한 축에 RTEX 통신 리턴 정보를 확인한다.(Actual position, Velocity, Torque)
    Public Declare Function AxmRtexGetAxisReturnData Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwReturn1 As Long, ByRef dwReturn2 As Long, ByRef dwReturn3 As Long) As Long
    ' 지정한 축에 RTEX Slave 축의 현재 상태 정보를 확인한다.(mechanical, Inposition and etc)
    Public Declare Function AxmRtexGetAxisSlaveStatus Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwStatus As Long) As Long

    ' 지정한 축에 MLII Slave 축에 범용 네트웍 명령어를 기입한다.
    Public Declare Function AxmSetAxisCmd Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef tagCommand As Long) As Long
    ' 지정한 축에 MLII Slave 축에 범용 네트웍 명령의 결과를 확인한다.
    Public Declare Function AxmGetAxisCmdResult Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef tagCommand As Long) As Long

    ' 지정한 SIIIH Slave 모듈에 네트웍 명령의 결과를 기입하고 반환 한다.
    Public Declare Function AxdSetAndGetSlaveCmdResult Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef tagSetCommand As Long, ByRef tagGetCommand As Long) As Long
    Public Declare Function AxaSetAndGetSlaveCmdResult Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef tagSetCommand As Long, ByRef tagGetCommand As Long) As Long
    Public Declare Function AxcSetAndGetSlaveCmdResult Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef tagSetCommand As Long, ByRef tagGetCommand As Long) As Long

    ' DPRAM 데이터를 확인한다.
    Public Declare Function AxlGetDpRamData Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wAddress As Long, ByRef dwpRdData As Long) As Long
    ' DPRAM 데이터를 Word단위로 확인한다.
    Public Declare Function AxlBoardReadDpramWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByRef dwpRdData As Long) As Long
    ' DPRAM 데이터를 Word단위로 설정한다.
    Public Declare Function AxlBoardWriteDpramWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByVal dwWrData As Long) As Long

    ' 각 보드의 각 SLAVE별로 명령을 전송한다.
    Public Declare Function AxlSetSendBoardEachCommand Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwCommand As Long, ByRef dwpSendData As Long, ByVal dwLength As Long) As Long
    ' 각 보드로 명령을 전송한다.
    Public Declare Function AxlSetSendBoardCommand Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwCommand As Long, ByRef dwpSendData As Long, ByVal dwLength As Long) As Long
    ' 각 보드의 응답을 확인한다.
    Public Declare Function AxlGetResponseBoardCommand Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwpReadData As Long) As Long

    ' Network Type Master 보드에서 Slave 들의 Firmware Version을 읽어 오는 함수.
    ' ucaFirmwareVersion unsigned char 형의 Array로 선언하고 크기가 4이상이 되도록 선언 해야 한다.
    Public Declare Function AxmInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef ucaFirmwareVersion As Long) As Long
    Public Declare Function AxaInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef ucaFirmwareVersion As Long) As Long
    Public Declare Function AxdInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef ucaFirmwareVersion As Long) As Long
    Public Declare Function AxcInfoGetFirmwareVersion Lib "AXL.dll" (ByVal lModuleNo As Long, ByRef ucaFirmwareVersion As Long) As Long

    '======== PCI-R1604-MLII 전용 함수===========================================================================
    ' INTERPOLATE and LATCH Command의 Option Field의 Torq Feed Forward의 값을 설정 하도록 합니다.
    ' 기본값은 MAX로 설정되어 있습니다.
    ' 설정값은 0 ~ 4000H까지 설정 할 수 있습니다.
    ' 설정값은 4000H이상으로 설정하면 설정은 그 이상으로 설정되나 동작은 4000H값이 적용 됩니다.
    Public Declare Function AxmSetTorqFeedForward Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwTorqFeedForward As Long) As Long

    ' INTERPOLATE and LATCH Command의 Option Field의 Torq Feed Forward의 값을 읽어오는 함수 입니다.
    ' 기본값은 MAX로 설정되어 있습니다.
    Public Declare Function AxmGetTorqFeedForward Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpTorqFeedForward As Long) As Long

    ' INTERPOLATE and LATCH Command의 VFF Field의 Velocity Feed Forward의 값을 설정 하도록 합니다.
    ' 기본값은 '0'로 설정되어 있습니다.
    ' 설정값은 0 ~ FFFFH까지 설정 할 수 있습니다.
    Public Declare Function AxmSetVelocityFeedForward Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwVelocityFeedForward As Long) As Long

    ' INTERPOLATE and LATCH Command의 VFF Field의 Velocity Feed Forward의 값을 읽어오는 함수 입니다.
    Public Declare Function AxmGetVelocityFeedForward Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpVelocityFeedForward As Long) As Long

    ' Encoder type을 설정한다.
    ' 기본값은 0(TYPE_INCREMENTAL)로 설정되어 있습니다.
    ' 설정값은 0 ~ 1까지 설정 할 수 있습니다.
    ' 설정값 : 0(TYPE_INCREMENTAL), 1(TYPE_ABSOLUTE).
    Public Declare Function AxmSignalSetEncoderType Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwEncoderType As Long) As Long

    ' Encoder type을 확인한다.
    Public Declare Function AxmSignalGetEncoderType Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpEncoderType As Long) As Long
    '========================================================================================================

    ' Slave Firmware Update를 위해 추가
    'DWORD   __stdcall AxmSetSendAxisCommand(long lAxisNo, WORD wCommand, WORD* wpSendData, WORD wLength);

    '======== PCI-R1604-RTEX, RTEX-PM 전용 함수==============================================================
    ' 범용 입력 2,3번 입력시 JOG 구동 속도를 설정한다.
    ' 구동에 관련된 모든 설정(Ex, PulseOutMethod, MoveUnitPerPulse 등)들이 완료된 이후 한번만 실행하여야 한다.
    Public Declare Function AxmMotSetUserMotion Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double) As Long

    ' 범용 입력 2,3번 입력시 JOG 구동 동작 사용 가부를 설정한다.
    ' 설정값 :  0(DISABLE), 1(ENABLE)
    Public Declare Function AxmMotSetUserMotionUsage Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwUsage As Long) As Long

    ' MPGP 입력을 사용하여 Load/UnLoad 위치를 자동으로 이동하는 기능 설정.
    Public Declare Function AxmMotSetUserPosMotion Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal dLoadPos As Double, ByVal dUnLoadPos As Double, ByVal dwFilter As Long, ByVal dwDelay As Long) As Long

    ' MPGP 입력을 사용하여 Load/UnLoad 위치를 자동으로 이동하는 기능 설정.
    ' 설정값 :  0(DISABLE), 1(Position 기능 A 사용), 2(Position 기능 B 사용)
    Public Declare Function AxmMotSetUserPosMotionUsage Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwUsage As Long) As Long
    '========================================================================================================

    '======== SIO-CN2CH/HPC4, 절대 위치 트리거 기능 모듈 전용 함수================================================
    ' 메모리 데이터 쓰기 함수
    Public Declare Function AxcKeWriteRamDataAddr Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwAddr As Long, ByVal dwData As Long) As Long
    ' 메모리 데이터 읽기 함수
    Public Declare Function AxcKeReadRamDataAddr Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwAddr As Long, ByRef dwpData As Long) As Long
    ' 메모리 초기화 함수
    Public Declare Function AxcKeResetRamDataAll Lib "AXL.dll" (ByVal lModuleNo As Long, ByVal dwData As Long) As Long
    ' 트리거 타임 아웃 설정 함수
    Public Declare Function AxcTriggerSetTimeout Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwTimeout As Long) As Long
    ' 트리거 타임 아웃 확인 함수
    Public Declare Function AxcTriggerGetTimeout Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpTimeout As Long) As Long
    ' 트리거 대기 상태 확인 함수
    Public Declare Function AxcStatusGetWaitState Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef dwpState As Long) As Long
    ' 트리거 대기 상태 설정 함수
    Public Declare Function AxcStatusSetWaitState Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwState As Long) As Long

    ' 지정 채널에 명령어 기입.
    Public Declare Function AxcKeSetCommandData32 Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwCommand As Long, ByVal dwData As Long) As Long
    ' 지정 채널에 명령어 기입.
    Public Declare Function AxcKeSetCommandData16 Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwCommand As Long, ByVal wData As Long) As Long
    ' 지정 채널의 레지스터 확인.
    Public Declare Function AxcKeGetCommandData32 Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwCommand As Long, ByRef dwpData As Long) As Long
    ' 지정 채널의 레지스터 확인.
    Public Declare Function AxcKeGetCommandData16 Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal dwCommand As Long, ByRef wpData As Long) As Long
    '========================================================================================================

    '======== PCI-N804/N404 전용, Sequence Motion ===================================================================
    ' Sequence Motion의 축 정보를 설정 합니다. (최소 1축)
    ' lSeqMapNo : 축 번호 정보를 담는 Sequence Motion Index Point
    ' lSeqMapSize : 축 번호 갯수
    ' long* LSeqAxesNo : 축 번호 배열
    Public Declare Function AxmSeqSetAxisMap Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByVal lSeqMapSize As Long, ByRef lSeqAxesNo As Long) As Long
    Public Declare Function AxmSeqGetAxisMap Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByRef lSeqMapSize As Long, ByRef lSeqAxesNo As Long) As Long

    ' Sequence Motion의 기준(Master) 축을 설정 합니다.
    ' 반드시 AxmSeqSetAxisMap(...) 에 설정된 축 내에서 설정하여야 합니다.
    Public Declare Function AxmSeqSetMasterAxisNo Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByVal lMasterAxisNo As Long) As Long

    ' Sequence Motion의 Node 적재 시작을 라이브러리에 알립니다.
    Public Declare Function AxmSeqBeginNode Lib "AXL.dll" (ByVal lSeqMapNo As Long) As Long

    ' Sequence Motion의 Node 적재 종료를 라이브러리에 알립니다.
    Public Declare Function AxmSeqEndNode Lib "AXL.dll" (ByVal lSeqMapNo As Long) As Long

    ' Sequence Motion의 구동을 시작 합니다.
    Public Declare Function AxmSeqStart Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByVal dwStartOption As Long) As Long

    ' Sequence Motion의 각 Profile Node 정보를 라이브러리에 입력 합니다.
    ' 만약 1축 Sequence Motion을 사용하더라도, *dPosition는 1개의 Array로 지정하여 주시기 바랍니다.
    Public Declare Function AxmSeqAddNode Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByRef dPosition As Double, ByVal dVelocity As Double, ByVal dAcceleration As Double, ByVal dDeceleration As Double, ByVal dNextVelocity As Double) As Long

    ' Sequence Motion이 구동 시 현재 실행 중인 Node Index를 알려 줍니다.
    Public Declare Function AxmSeqGetNodeNum Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByRef lCurNodeNo As Long) As Long

    ' Sequence Motion의 총 Node Count를 확인 합니다.
    Public Declare Function AxmSeqGetTotalNodeNum Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByRef lTotalNodeCnt As Long) As Long

    ' Sequence Motion이 현재 구동 중인지 확인 합니다.
    ' dwInMotion : 0(구동 종료), 1(구동 중)
    Public Declare Function AxmSeqIsMotion Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByRef dwInMotion As Long) As Long

    ' Sequence Motion의 Memory를 Clear 합니다.
    ' AxmSeqSetAxisMap(...), AxmSeqSetMasterAxisNo(...) 에서 설정된 값은 유지됩니다.
    Public Declare Function AxmSeqWriteClear Lib "AXL.dll" (ByVal lSeqMapNo As Long) As Long

    ' Sequence Motion의 구동을 종료 합니다.
    ' dwStopMode : 0(EMERGENCY_STOP), 1(SLOWDOWN_STOP)
    Public Declare Function AxmSeqStop Lib "AXL.dll" (ByVal lSeqMapNo As Long, ByVal dwStopMode As Long) As Long
    '========================================================================================================


    '======== PCIe-Rxx04-SIIIH 전용 함수==========================================================================
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

    '======== PCI-R32IOEV-RTEX 전용 함수===========================================================================
    ' I/O 포트로 할당된 HPI register 를 읽고 쓰기위한 API 함수.
    ' I/O Registers for HOST interface.
    ' I/O 00h Host status register (HSR)
    ' I/O 04h Host-to-DSP control register (HDCR)
    ' I/O 08h DSP page register (DSPP)
    ' I/O 0Ch Reserved
    Public Declare Function AxlSetIoPort Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwAddr As Long, ByVal dwData As Long) As Long
    Public Declare Function AxlGetIoPort Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwAddr As Long, ByRef dwpData As Long) As Long

    '======== PCI-R3200-MLIII 전용 함수===========================================================================
    '/*
    ' M-III Master 보드 펌웨어 업데이트 기본 정보 설정 함수
    'DWORD   __stdcall AxlM3SetFWUpdateInit(long lBoardNo, DWORD dwTotalPacketSize);
    ' M-III Master 보드 펌웨어 업데이트 기본 정보 설정 결과 확인 함수
    'DWORD   __stdcall AxlM3GetFWUpdateInit(long lBoardNo, DWORD *dwTotalPacketSize);
    ' M-III Master 보드 펌웨어 업데이트 자료 전달 함수
    'DWORD   __stdcall AxlM3SetFWUpdateCopy(long lBoardNo, DWORD *lFWUpdataData, DWORD dwLength);
    ' M-III Master 보드 펌웨어 업데이트 자료 전달 결과 확인 함수
    'DWORD   __stdcall AxlM3GetFWUpdateCopy(long lBoardNo, BYTE bCrcData, DWORD *lFWUpdataResult);
    ' M-III Master 보드 펌웨어 업데이트 실행
    'DWORD   __stdcall AxlM3SetFWUpdate(long lBoardNo, DWORD dwSectorNo);
    ' M-III Master 보드 펌웨어 업데이트 실행 결과 확인
    'DWORD   __stdcall AxlM3GetFWUpdate(long lBoardNo, DWORD *dwSectorNo, DWORD *dwIsDone);
    '*/
    ' M-III Master 보드 펌웨어 업데이트 기본 정보 설정 함수
    Public Declare Function AxlM3SetFWUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwTotalPacketSize As Long, ByVal dwProcTotalStepNo As Long) As Long
    ' M-III Master 보드 펌웨어 업데이트 기본 정보 설정 결과 확인 함수
    Public Declare Function AxlM3GetFWUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwTotalPacketSize As Long, ByRef dwProcTotalStepNo As Long) As Long

    ' M-III Master 보드 펌웨어 업데이트 자료 전달 함수
    Public Declare Function AxlM3SetFWUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef pdwPacketData As Long, ByVal dwPacketSize As Long) As Long
    ' M-III Master 보드 펌웨어 업데이트 자료 전달 결과 확인 함수
    Public Declare Function AxlM3GetFWUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwPacketSize As Long) As Long

    ' M-III Master 보드 펌웨어 업데이트 실행
    Public Declare Function AxlM3SetFWUpdate Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwFlashBurnStepNo As Long) As Long
    ' M-III Master 보드 펌웨어 업데이트 실행 결과 확인
    Public Declare Function AxlM3GetFWUpdate Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwFlashBurnStepNo As Long, ByRef dwIsFlashBurnDone As Long) As Long

    ' M-III Master 보드 EEPROM 데이터 설정 함수
    Public Declare Function AxlM3SetCFGData Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef pCmdData As Long, ByVal CmdDataSize As Long) As Long
    ' M-III Master 보드 EEPROM 데이터 가져오기 함수
    Public Declare Function AxlM3GetCFGData Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef pCmdData As Long, ByVal CmdDataSize As Long) As Long

    ' M-III Master 보드 CONNECT PARAMETER 기본 정보 설정 함수
    Public Declare Function AxlM3SetMCParaUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wCh0Slaves As Long, ByVal wCh1Slaves As Long, ByVal dwCh0CycTime As Long, ByVal dwCh1CycTime As Long, ByVal dwChInfoMaxRetry As Long) As Long
    ' M-III Master 보드 CONNECT PARAMETER 기본 정보 설정 결과 확인 함수
    Public Declare Function AxlM3GetMCParaUpdateInit Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef wCh0Slaves As Long, ByRef wCh1Slaves As Long, ByRef dwCh0CycTime As Long, ByRef dwCh1CycTime As Long, ByRef dwChInfoMaxRetry As Long) As Long
    ' M-III Master 보드 CONNECT PARAMETER 기본 정보 전달 함수
    Public Declare Function AxlM3SetMCParaUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wIdx As Long, ByVal wChannel As Long, ByVal wSlaveAddr As Long, ByVal dwProtoCalType As Long, ByVal dwTransBytes As Long, ByVal dwDeviceCode As Long) As Long
    ' M-III Master 보드 CONNECT PARAMETER 기본 정보 전달 결과 확인 함수
    Public Declare Function AxlM3GetMCParaUpdateCopy Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wIdx As Long, ByRef wChannel As Long, ByRef wSlaveAddr As Long, ByRef dwProtoCalType As Long, ByRef dwTransBytes As Long, ByRef dwDeviceCode As Long) As Long

    ' M-III Master 보드내에 레지스터를 DWord단위로 확인 함수
    Public Declare Function AxlBoardReadDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByRef dwData As Long) As Long
    ' M-III Master 보드내에 레지스터를 DWord단위로 설정 함수
    Public Declare Function AxlBoardWriteDWord Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wOffset As Long, ByVal dwData As Long) As Long

    ' 보드내에 확장 레지스터를 DWord단위로 설정 및 확인한다.
    Public Declare Function AxlBoardReadDWordEx Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwOffset As Long, ByRef dwData As Long) As Long
    Public Declare Function AxlBoardWriteDWordEx Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwOffset As Long, ByVal dwData As Long) As Long

    ' 서보를 정지 모드로 설정 함수
    Public Declare Function AxmM3ServoSetCtrlStopMode Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bStopMode As Byte) As Long
    ' 서보를 Lt 선택 상태로 설정 함수
    Public Declare Function AxmM3ServoSetCtrlLtSel Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bLtSel1 As Byte, ByVal bLtSel2 As Byte) As Long
    ' 서보의 IO 입력 상태를 확인 함수
    Public Declare Function AxmStatusReadServoCmdIOInput Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upStatus As Long) As Long
    ' 서보의 보간 구동 함수
    Public Declare Function AxmM3ServoExInterpolate Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwTPOS As Long, ByVal dwVFF As Long, ByVal dwTFF As Long, ByVal dwTLIM As Long, ByVal dwExSig1 As Long, ByVal dwExSig2 As Long) As Long
    ' 서보 엑츄레이터 바이어스 설정 함수
    Public Declare Function AxmM3ServoSetExpoAccBias Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wBias As Long) As Long
    ' 서보 엑츄레이터 시간 설정 함수
    Public Declare Function AxmM3ServoSetExpoAccTime Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wTime As Long) As Long
    ' 서보의 이동 시간을 설정 함수
    Public Declare Function AxmM3ServoSetMoveAvrTime Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wTime As Long) As Long
    ' 서보의 Acc 필터 설정 함수
    Public Declare Function AxmM3ServoSetAccFilter Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bAccFil As Byte) As Long
    ' 서보의 상태 모니터1 설정 함수
    Public Declare Function AxmM3ServoSetCprmMonitor1 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bMonSel As Byte) As Long
    ' 서보의 상태 모니터2 설정 함수
    Public Declare Function AxmM3ServoSetCprmMonitor2 Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal bMonSel As Byte) As Long
    ' 서보의 상태 모니터1 확인 함수
    Public Declare Function AxmM3ServoStatusReadCprmMonitor1 Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upStatus As Long) As Long
    ' 서보의 상태 모니터2 확인 함수
    Public Declare Function AxmM3ServoStatusReadCprmMonitor2 Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upStatus As Long) As Long
    ' 서보 엑츄레이터 Dec 설정 함수
    Public Declare Function AxmM3ServoSetAccDec Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal wAcc1 As Long, ByVal wAcc2 As Long, ByVal wAccSW As Long, ByVal wDec1 As Long, ByVal wDec2 As Long, ByVal wDecSW As Long) As Long
    ' 서보 정지 설정 함수
    Public Declare Function AxmM3ServoSetStop Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal lMaxDecel As Long) As Long

    '========== 표준 I/O 기기 공통 커맨드 =========================================================================
    ' Network제품 각 슬레이브 기기의 파라미터 설정 값을 반환하는 함수
    Public Declare Function AxlM3GetStationParameter Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wNo As Long, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Long
    ' Network제품 각 슬레이브 기기의 파라미터 값을 설정하는 함수
    Public Declare Function AxlM3SetStationParameter Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wNo As Long, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Long
    ' Network제품 각 슬레이브 기기의 ID값을 반환하는 함수
    Public Declare Function AxlM3GetStationIdRd Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bIdCode As Byte, ByVal bOffset As Byte, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Long
    ' Network제품 각 슬레이브 기기의 무효 커맨드로 사용하는 함수
    Public Declare Function AxlM3SetStationNop Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte) As Long
    ' Network제품 각 슬레이브 기기의 셋업을 실시하는 함수
    Public Declare Function AxlM3SetStationConfig Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bConfigMode As Byte, ByVal bModuleType As Byte) As Long
    ' Network제품 각 슬레이브 기기의 알람 및 경고 상태 값을 반환하는 함수
    Public Declare Function AxlM3GetStationAlarm Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wAlarmRdMod As Long, ByVal wAlarmIndex As Long, ByVal bModuleType As Byte, ByRef pwAlarmData As Long) As Long
    ' Network제품 각 슬레이브 기기의 알람 및 경고 상태를 해제하는 함수
    Public Declare Function AxlM3SetStationAlarmClear Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wAlarmClrMod As Long, ByVal bModuleType As Byte) As Long
    ' Network제품 각 슬레이브 기기와의 동기통신을 설정하는 함수
    Public Declare Function AxlM3SetStationSyncSet Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte) As Long
    ' Network제품 각 슬레이브 기기와의 연결을 설정하는 함수
    Public Declare Function AxlM3SetStationConnect Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bVer As Byte, ByVal bComMode As Byte, ByVal bComTime As Byte, ByVal bProfileType As Byte, ByVal bModuleType As Byte) As Long
    ' Network제품 각 슬레이브 기기와의 연결 끊음을 설정하는 함수
    Public Declare Function AxlM3SetStationDisConnect Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte) As Long
    ' Network제품 각 슬레이브 기기의 비휘발성 파라미터 설정 값을 반환하는 함수
    Public Declare Function AxlM3GetStationStoredParameter Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wNo As Long, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Long
    ' Network제품 각 슬레이브 기기의 비휘발성 파라미터 값을 설정하는 함수
    Public Declare Function AxlM3SetStationStoredParameter Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wNo As Long, ByVal bSize As Byte, ByVal bModuleType As Byte, ByRef pbParam As Byte) As Long
    ' Network제품 각 슬레이브 기기의 메모리 설정 값을 반환하는 함수
    Public Declare Function AxlM3GetStationMemory Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wSize As Long, ByVal dwAddress As Long, ByVal bModuleType As Byte, ByVal bMode As Byte, ByVal bDataType As Byte, ByRef pbData As Byte) As Long
    ' Network제품 각 슬레이브 기기의 메모리 값을 설정하는 함수
    Public Declare Function AxlM3SetStationMemory Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal wSize As Long, ByVal dwAddress As Long, ByVal bModuleType As Byte, ByVal bMode As Byte, ByVal bDataType As Byte, ByRef pbData As Byte) As Long

    '========== 표준 I/O 기기 커넥션 커맨드 =========================================================================
    ' Network제품 각 재정열된 슬레이브 기기의 자동 억세스 모드 값을 설정하는 함수
    Public Declare Function AxlM3SetStationAccessMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByVal bRWSMode As Byte) As Long
    ' Network제품 각 재정열된 슬레이브 기기의 자동 억세스 모드 설정값을 반환하는 함수
    Public Declare Function AxlM3GetStationAccessMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef bRWSMode As Byte) As Long
    ' Network제품 각 슬레이브 기기의 동기 자동 연결 모드를 설정하는 함수
    Public Declare Function AxlM3SetAutoSyncConnectMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByVal dwAutoSyncConnectMode As Long) As Long
    ' Network제품 각 슬레이브 기기의 동기 자동 연결 모드 설정값을 반환하는 함수
    Public Declare Function AxlM3GetAutoSyncConnectMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef dwpAutoSyncConnectMode As Long) As Long
    ' Network제품 각 슬레이브 기기에 대한 단일 동기화 연결을 설정하는 함수
    Public Declare Function AxlM3SyncConnectSingle Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte) As Long
    ' Network제품 각 슬레이브 기기에 대한 단일 동기화 연결 끊음을 설정하는 함수
    Public Declare Function AxlM3SyncDisconnectSingle Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte) As Long
    ' Network제품 각 슬레이브 기기와의 연결 상태를 확인하는 함수
    Public Declare Function AxlM3IsOnLine Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByRef dwData As Long) As Long

    '========== 표준 I/O 프로파일 커맨드 =========================================================================
    ' Network제품 각 동기화 상태의 슬레이브 I/O 기기에 대한 데이터 설정값을 반환하는 함수
    Public Declare Function AxlM3GetStationRWS Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef pdwParam As Long, ByVal bSize As Byte) As Long
    ' Network제품 각 동기화 상태의 슬레이브 I/O 기기에 대한 데이터값을 설정하는 함수
    Public Declare Function AxlM3SetStationRWS Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef pdwParam As Long, ByVal bSize As Byte) As Long
    ' Network제품 각 비동기화 상태의 슬레이브 I/O 기기에 대한 데이터 설정값을 반환하는 함수
    Public Declare Function AxlM3GetStationRWA Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef pdwParam As Long, ByVal bSize As Byte) As Long
    ' Network제품 각 비동기화 상태의 슬레이브 I/O 기기에 대한 데이터값을 설정하는 함수
    Public Declare Function AxlM3SetStationRWA Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lModuleNo As Long, ByVal bModuleType As Byte, ByRef pdwParam As Long, ByVal bSize As Byte) As Long

    ' MLIII adjustment operation을 설정 한다.
    ' dwReqCode == 0x1005 : parameter initialization : 20sec
    ' dwReqCode == 0x1008 : absolute encoder reset   : 5sec
    ' dwReqCode == 0x100E : automatic offset adjustment of motor current detection signals  : 5sec
    ' dwReqCode == 0x1013 : Multiturn limit setting  : 5sec
    Public Declare Function AxmM3AdjustmentOperation Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwReqCode As Long) As Long

    ' M3 전용 원점 검색 진행 상태 진단용 함수이다.
    Public Declare Function AxmHomeGetM3FWRealRate Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upHomeMainStepNumber As Long, ByRef upHomeSubStepNumber As Long, ByRef upHomeLastMainStepNumber As Long, ByRef upHomeLastSubStepNumber As Long) As Long
    ' M3 전용 원점 검색시 센서존에서 탈출시 보정되는 위치 값을 반환하는 함수이다.
    Public Declare Function AxmHomeGetM3OffsetAvoideSenArea Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dPos As Double) As Long
    ' M3 전용 원점 검색시 센서존에서 탈출시 보정되는 위치 값을 설정하는 함수이다.
    ' dPos 설정 값이 0이면 자동으로 탈출시 보정되는 위치 값은 자동으로 설정된다.
    ' dPos 설정 값은 양수의 값만 입력한다.
    Public Declare Function AxmHomeSetM3OffsetAvoideSenArea Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPos As Double) As Long

    ' M3 전용, 절대치 엔코더 사용 기준, 원점검색 완료 후 CMD/ACT POS 초기화 여부 설정
    ' dwSel: 0, 원점 검색후 CMD/ACTPOS 0으로 설정됨.[초기값]
    ' dwSel: 1, 원점 검색후 CMD/ACTPOS 값이 설정되지 않음.
    Public Declare Function AxmM3SetAbsEncOrgResetDisable Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwSel As Long) As Long

    ' M3 전용, 절대치 엔코더 사용 기준, 원점검색 완료 후 CMD/ACT POS 초기화 여부 설정값 가져오기
    ' upSel: 0, 원점 검색후 CMD/ACTPOS 0으로 설정됨.[초기값]
    ' upSel: 1, 원점 검색후 CMD/ACTPOS 값이 설정되지 않음.
    Public Declare Function AxmM3GetAbsEncOrgResetDisable Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upSel As Long) As Long

    ' M3 전용, 슬레이브 OFFLINE 전환시 알람 유지 기능 사용 유무 설정
    ' dwSel: 0, ML3 슬레이브 ONLINE->OFFLINE 알람 처리 사용하지 않음.[초기값]
    ' dwSel: 1, ML3 슬레이브 ONLINE->OFFLINE 알람 처리 사용

    Public Declare Function AxmM3SetOfflineAlarmEnable Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwSel As Long) As Long
    ' M3 전용, 슬레이브 OFFLINE 전환시 알람 유지 기능 사용 유무 설정 값 가져오기
    ' upSel: 0, ML3 슬레이브 ONLINE->OFFLINE 알람 처리 사용하지 않음.[초기값]
    ' upSel: 1, ML3 슬레이브 ONLINE->OFFLINE 알람 처리 사용

    Public Declare Function AxmM3GetOfflineAlarmEnable Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upSel As Long) As Long

    ' M3 전용, 슬레이브 OFFLINE 전환 여부 상태 값 가져오기
    ' upSel: 0, ML3 슬레이브 ONLINE->OFFLINE 전환되지 않음
    ' upSel: 1, ML3 슬레이브 ONLINE->OFFLINE 전환되었음.
    Public Declare Function AxmM3ReadOnlineToOfflineStatus Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef upStatus As Long) As Long

    ' Network 제품의 Configuration Lock 상태를 설정한다.
    ' wLockMode  : DISABLE(0), ENABLE(1)
    Public Declare Function AxlSetLockMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal wLockMode As Long) As Long

    ' Lock 정보를 설정
    Public Declare Function AxlSetLockData Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwTotalNodeNum As Long, ByRef dwpNodeNo As Long, ByRef dwpNodeID As Long, ByRef dwpLockData As Long) As Long

    Public Declare Function AxmMoveStartPosWithAVC Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dPosition As Double, ByVal dMaxVelocity As Double, ByVal dMaxAccel As Double, ByVal dMinJerk As Double, ByRef dpMoveVelocity As Double, ByRef dpMoveAccel As Double, ByRef dpMoveJerk As Double) As Long
    ' 카운터 모듈의 2-D 절대위치 트리거 기능을 위해 필요한 트리거 위치 정보를 설정한다.
    ' lChannelNo : 0,1 channel 일 경우 0, 2,3 channel 의 경우 2 를 설정.
    ' nDataCnt :
    '  nDataCnt > 0 : 데이터 등록, nDataCnt <= 0 : 등록된 데이터 초기화.
    ' dwOption : Reserved.
    ' dpPatternData : (X1, Y1)
    Public Declare Function AxcTriggerSetPatternData Lib "AXL.dll" (ByVal lChannelNo As Long, ByVal nDataCnt As Long, ByVal dwOption As Long, ByRef dpPatternData As Double) As Long
    ' 카운터 모듈의 2-D 절대위치 트리거 기능을 위해 필요한 트리거 위치 정보를 확인한다.
    Public Declare Function AxcTriggerGetPatternData Lib "AXL.dll" (ByVal lChannelNo As Long, ByRef npDataCnt As Long, ByRef dwpOption As Long, ByRef dpPatternData As Double) As Long

    '연속 보간 관련하여 AxmContiEndNode 함수내에서 보간구동관련 Node 를 Data Queue 에 미리 채워넣을 수 있도록하는 기능을 활성화 한다.
    'bPushPrevContiQueue : 1  해당 기능 활성화
    'bPushPrevContiQueue : 0  해당 기능 비활성화
    Public Declare Function AxmContiSetPushPrevContiQueueEnable Lib "AXL.dll" (ByVal lCoordinate As Long, ByVal bPushPrevContiQueue As Byte) As Long
    '설정해둔 AxmContiSetPushPrevContiQueueEnable Flag값을 반환한다.
    Public Declare Function AxmContiGetPushPrevContiQueueEnable Lib "AXL.dll" (ByVal lCoordinate As Long, ByRef bPushPrevContiQueue As BOOL*) As Long

    ' 연속보간 구동 시 Data Queue 에 Node 정보가 적재되었는지 상태를 반환한다.
    ' AxmContiSetPushPrevContiQueueEnable(long lCoordinate, 1) 로 설정되어있을 경우만 유효
    ' bPushPrevContiQueueComplete : 1  Node Data 적재 완료
    ' bPushPrevContiQueueComplete : 0  Node Data 적재 되어있지않음
    Public Declare Function AxmContiGetPushPrevContiQueueComplete Lib "AXL.dll" (ByVal lCoordinate As Long, ByRef bPushPrevContiQueueComplete As BOOL*) As Long

    ' 연속보간 구동 시 첫 노드 시작 및 마지막 노드 시작 시 일정시간 이후 지정된 좌표계의 마스터 축의 OutputBit On/Off 제어
    ' AxmContiBeginNode 앞에 호출해야 한다. 한번 구동하면 Flag가 초기화되어 다시 호출해야 사용할 수 있다.
    ' StartTime/EndTime 단위는 [Sec]이며, 0 ~ 6.5초까지 설정 가능하다.
    ' uOnoff : 0 - 시작 위치에서 Bit On 종료 위치에서 Bit Off
    '          : 1 - 시작 위치에서 Bit Off 종료 위치에서 Bit On
    ' lEndMode : 0 - 마지막 노드 구동 종료 후 즉시 OutputBit Off/On
    '   : 1 - 마지막 노드 구동 시작 후 입력한 EndTime 이후 OutputBit Off/On
    '   : 2 - 구동 시작 시 OutputBit On/Off 및 입력한 EndTime 이후 OutputBit Off/On
    Public Declare Function AxmContiSetWriteOutputBit Lib "AXL.dll" (ByVal lCoordinate As Long, ByVal dStartTime As Double, ByVal dEndTime As Double, ByVal lBitNo As Long, ByVal uOnoff As Long, ByVal lEndMode As Long) As Long

    ' AxmContiSetWriteOutputBit로 설정한 값들을 반환한다.
    Public Declare Function AxmContiGetWriteOutputBit Lib "AXL.dll" (ByVal lCoordinate As Long, ByRef dpStartTime As Double, ByRef dpEndTime As Double, ByRef lpBitNo As Long, ByRef lpOnoff As Long, ByRef lpEndMode As Long) As Long

    ' AxmContiSetWriteOutputBit로 설정한 값들을 리셋한다.
    Public Declare Function AxmContiResetWriteOutputBit Lib "AXL.dll" (ByVal lCoordinate As Long) As Long

    ' AxmMoveTorqueStop 함수로 토크 구동 정지 시 CmdPos 값을 ActPos 값과 일치시키는 시점까지의 대기 시간을 설정한다.
    ' dwSettlingTime
    '  1) 단위: [msec]
    '  2) 입력 가능 범위: 0 ~ 10000
    '  *참고* AxmMoveTorqueSetStopSettlingTime 함수로 대기 시간을 설정하지 않으면, dafault 값인 10[msec]가 적용된다.
    Public Declare Function AxmMoveTorqueSetStopSettlingTime Lib "AXL.dll" (ByVal lAxisNo As Long, ByVal dwSettlingTime As Long) As Long
    ' AxmMoveTorqueStop 함수로 토크 구동 정지 시 CmdPos 값을 ActPos 값과 일치시키는 시점까지의 대기 시간을 반환한다.
    Public Declare Function AxmMoveTorqueGetStopSettlingTime Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpSettlingTime As Long) As Long

    '
    ' Monitor
    ' 데이터를 수집을 진행할 항목을 추가합니다.
    Public Declare Function AxlMonitorSetItem Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lItemIndex As Long, ByVal dwSignalType As Long, ByVal lSignalNo As Long, ByVal lSubSignalNo As Long) As Long

    ' 데이터 수집을 진행할 항목들에 관한 정보를 가져옵니다.
    Public Declare Function AxlMonitorGetIndexInfo Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef lpItemSize As Long, ByRef lpItemIndex As Long) As Long

    ' 데이터 수집을 진행할 각 항목의 세부 설정을 가져옵니다.
    Public Declare Function AxlMonitorGetItemInfo Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lItemIndex As Long, ByRef dwpSignalType As Long, ByRef lpSignalNo As Long, ByRef lpSubSignalNo As Long) As Long

    ' 모든 데이터 수집 항목의 설정을 초기화합니다.
    Public Declare Function AxlMonitorResetAllItem Lib "AXL.dll" (ByVal lBoardNo As Long) As Long

    ' 선택된 데이터 수집 항목의 설정을 초기화합니다.
    Public Declare Function AxlMonitorResetItem Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal lItemIndex As Long) As Long

    ' 데이터 수집의 트리거 조건을 설정합니다.
    Public Declare Function AxlMonitorSetTriggerOption Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwSignalType As Long, ByVal lSignalNo As Long, ByVal lSubSignalNo As Long, ByVal dwOperatorType As Long, ByVal dValue1 As Double, ByVal dValue2 As Double) As Long

    ' 데이터 수집의 트리거 조건을 가져옵니다.
    'DWORD  __stdcall AxlMonitorGetTriggerOption(DWORD* dwpSignalType, long* lpSignalNo, long* lpSubSignalNo, DWORD* dwpOperatorType, double* dpValue1, double* dpValue2);

    ' 데이터 수집의 트리거 조건을 초기화합니다.
    Public Declare Function AxlMonitorResetTriggerOption Lib "AXL.dll" (ByVal lBoardNo As Long) As Long

    ' 데이터 수집을 시작합니다.
    Public Declare Function AxlMonitorStart Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwStartOption As Long, ByVal dwOverflowOption As Long) As Long

    ' 데이터 수집을 정지합니다.
    Public Declare Function AxlMonitorStop Lib "AXL.dll" (ByVal lBoardNo As Long) As Long

    ' 수집된 데이터를 가져옵니다.
    Public Declare Function AxlMonitorReadData Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef lpItemSize As Long, ByRef lpDataCount As Long, ByRef dpReadData As Double) As Long

    ' 데이터 수집의 주기를 가져옵니다.
    Public Declare Function AxlMonitorReadPeriod Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwpPeriod As Long) As Long
    '


    '
    ' MonitorEx
    ' 데이터를 수집을 진행할 항목을 추가합니다.
    Public Declare Function AxlMonitorExSetItem Lib "AXL.dll" (ByVal lItemIndex As Long, ByVal dwSignalType As Long, ByVal lSignalNo As Long, ByVal lSubSignalNo As Long) As Long

    ' 데이터 수집을 진행할 항목들에 관한 정보를 가져옵니다.
    Public Declare Function AxlMonitorExGetIndexInfo Lib "AXL.dll" (ByRef lpItemSize As Long, ByRef lpItemIndex As Long) As Long

    ' 데이터 수집을 진행할 각 항목의 세부 설정을 가져옵니다.
    Public Declare Function AxlMonitorExGetItemInfo Lib "AXL.dll" (ByVal lItemIndex As Long, ByRef dwpSignalType As Long, ByRef lpSignalNo As Long, ByRef lpSubSignalNo As Long) As Long

    ' 모든 데이터 수집 항목의 설정을 초기화합니다.
    Public Declare Function AxlMonitorExResetAllItem Lib "AXL.dll" () As Long

    ' 선택된 데이터 수집 항목의 설정을 초기화합니다.
    Public Declare Function AxlMonitorExResetItem Lib "AXL.dll" (ByVal lItemIndex As Long) As Long

    ' 데이터 수집의 트리거 조건을 설정합니다.
    Public Declare Function AxlMonitorExSetTriggerOption Lib "AXL.dll" (ByVal dwSignalType As Long, ByVal lSignalNo As Long, ByVal lSubSignalNo As Long, ByVal dwOperatorType As Long, ByVal dValue1 As Double, ByVal dValue2 As Double) As Long

    ' 데이터 수집의 트리거 조건을 가져옵니다.
    'DWORD  __stdcall AxlMonitorExGetTriggerOption(DWORD* dwpSignalType, long* lpSignalNo, long* lpSubSignalNo, DWORD* dwpOperatorType, double* dpValue1, double* dpValue2);

    ' 데이터 수집의 트리거 조건을 초기화합니다.
    Public Declare Function AxlMonitorExResetTriggerOption Lib "AXL.dll" () As Long

    ' 데이터 수집을 시작합니다.
    Public Declare Function AxlMonitorExStart Lib "AXL.dll" (ByVal dwStartOption As Long, ByVal dwOverflowOption As Long) As Long

    ' 데이터 수집을 정지합니다.
    Public Declare Function AxlMonitorExStop Lib "AXL.dll" () As Long

    ' 수집된 데이터를 가져옵니다.
    Public Declare Function AxlMonitorExReadData Lib "AXL.dll" (ByRef lpItemSize As Long, ByRef lpDataCount As Long, ByRef dpReadData As Double) As Long

    ' 데이터 수집의 주기를 가져옵니다.
    Public Declare Function AxlMonitorExReadPeriod Lib "AXL.dll" (ByRef dwpPeriod As Long) As Long
    '

    ' X2, Y2 축에 대한 Offset 위치 정보를 포함한 2축 직선 보간 #01.
    Public Declare Function AxmLineMoveDual01 Lib "AXL.dll" (ByVal lCoordNo As Long, ByRef dpEndPosition As Double, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal dOffsetLength As Double, ByVal dTotalLength As Double, ByRef dpStartOffsetPosition As Double, ByRef dpEndOffsetPosition As Double) As Long
    ' X2, Y2 축에 대한 Offset 위치 정보를 포함한 2축 원호 보간 #01.
    Public Declare Function AxmCircleCenterMoveDual01 Lib "AXL.dll" (ByVal lCoordNo As Long, ByRef lpAxes As Long, ByRef dpCenterPosition As Double, ByRef dpEndPosition As Double, ByVal dVelocity As Double, ByVal dAccel As Double, ByVal dDecel As Double, ByVal dwCWDir As Long, ByVal dOffsetLength As Double, ByVal dTotalLength As Double, ByRef dpStartOffsetPosition As Double, ByRef dpEndOffsetPosition As Double) As Long

    ' 해당보드의 connect mode 를 반환한다.
    ' dpMode : 1 Auto Connect Mode
    ' dpMode : 0 Manual Connect Mode
    Public Declare Function AxlGetBoardConnectMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef dwpMode As Long) As Long
    ' 해당보드의 connect mode 를 설정한다.
    ' dMode : 1 Auto Connect Mode
    ' dMode : 0 Manual Connect Mode
    Public Declare Function AxlSetBoardConnectMode Lib "AXL.dll" (ByVal lBoardNo As Long, ByVal dwMode As Long) As Long

    '지정된 축의 Command Queue 를 초기화 한다.
    Public Declare Function AxmStatusSetCmdQueueClear Lib "AXL.dll" (ByVal lAxisNo As Long) As Long

    ' 지정된 축의 통신 프로토콜관련 Data 를 확인한다.
    Public Declare Function AxmStatusGetControlBits Lib "AXL.dll" (ByVal lAxisNo As Long, ByRef dwpTxData As Long, ByRef dwpRxData As Long) As Long

    ' 사용 중인 AXL이 있는지 확인(Shared Memory가 존재하는지 확인)
    Public Declare Function AxlIsUsing Lib "AXL.dll" () As Byte
    Public Declare Function AxlRescanExternalDevice Lib "AXL.dll" () As Long
    Public Declare Function AxlGetExternalDeviceInfo Lib "AXL.dll" (ByVal lBoardNo As Long, ByRef devInfo As void*) As Long


