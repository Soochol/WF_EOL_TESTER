
unit AXDev;

interface

uses Windows, Messages, AXHS;


    // Board Number를 이용하여 Board Address 찾기
    function AxlGetBoardAddress (lBoardNo : LongInt; upBoardAddress : PDWord) : DWord; stdcall;
    // Board Number를 이용하여 Board ID 찾기
    function AxlGetBoardID (lBoardNo : LongInt; upBoardID : PDWord) : DWord; stdcall;
    // Board Number를 이용하여 Board Version 찾기
    function AxlGetBoardVersion (lBoardNo : LongInt; upBoardVersion : PDWord) : DWord; stdcall;
    // Board Number와 Module Position을 이용하여 Module ID 찾기
    function AxlGetModuleID (lBoardNo : LongInt; lModulePos : LongInt; upModuleID : PDWord) : DWord; stdcall;
    // Board Number와 Module Position을 이용하여 Module Version 찾기
    function AxlGetModuleVersion (lBoardNo : LongInt; lModulePos : LongInt; upModuleVersion : PDWord) : DWord; stdcall;
    // Board Number와 Module Position을 이용하여 Network Node 정보 확인
    function AxlGetModuleNodeInfo (lBoardNo : LongInt; lModulePos : LongInt; upNetNo : PLongInt; upNodeAddr : PDWord) : DWord; stdcall;

    // Board에 내장된 범용 Data Flash Write (PCI-R1604[RTEX master board]전용)
    // lPageAddr(0 ~ 199)
    // lByteNum(1 ~ 120)
    // 주의) Flash에 데이타를 기입할 때는 일정 시간(최대 17mSec)이 소요되기때문에 연속 쓰기시 지연 시간이 필요함.
    function AxlSetDataFlash (lBoardNo : LongInt; lPageAddr : LongInt; lBytesNum : LongInt; bpSetData : PByte) : DWord; stdcall;

    // Board에 내장된 ESTOP 외부 입력 신호를 이용한 InterLock 기능 사용 유무 및 디지털 필터 상수값 정의 (PCI-Rxx00[MLIII master board]전용)
    // 1. 사용 유무
    //   설명: 기능 사용 설정후 외부에서 ESTOP 신호 인가시 보드에 연결된 모션 제어 노드에 대해서 ESTOP 구동 명령 실행
    //    0: 기능 사용하지 않음(기본 설정값)
    //    1: 기능 사용
    // 2. 디지털 필터 값
    //      입력 필터 상수 설정 범위 1 ~ 40, 단위 통신 Cyclic time
    // Board 에 dwInterLock, dwDigFilterVal을 이용하여 EstopInterLock 기능 설정
    function AxlSetEStopInterLock (lBoardNo : LongInt; dwInterLock : DWord; dwDigFilterVal : DWord) : DWord; stdcall;
    // Board에 설정된 dwInterLock, dwDigFilterVal 정보를 가져오기
    function AxlGetEStopInterLock (lBoardNo : LongInt; dwInterLock : PDWord; dwDigFilterVal : PDWord) : DWord; stdcall;
    // Board에 입력된 EstopInterLock 신호를 읽는다.
    function AxlReadEStopInterLock (lBoardNo : LongInt; dwInterLock : PDWord) : DWord; stdcall;

    // Board에 내장된 범용 Data Flash Read(PCI-R1604[RTEX master board]전용)
    // lPageAddr(0 ~ 199)
    // lByteNum(1 ~ 120)
    function AxlGetDataFlash (lBoardNo : LongInt; lPageAddr : LongInt; lBytesNum : LongInt; bpGetData : PByte) : DWord; stdcall;

    // Board Number와 Module Position을 이용하여 AIO Module Number 찾기
    function AxaInfoGetModuleNo (lBoardNo : LongInt; lModulePos : LongInt; lpModuleNo : PLongInt) : DWord; stdcall;
    // Board Number와 Module Position을 이용하여 DIO Module Number 찾기
    function AxdInfoGetModuleNo (lBoardNo : LongInt; lModulePos : LongInt; lpModuleNo : PLongInt) : DWord; stdcall;

    // 지정 축에 IPCOMMAND Setting
    function AxmSetCommand (lAxisNo : LongInt; sCommand : Byte) : DWord; stdcall;
    // 지정 축에 8bit IPCOMMAND Setting
    function AxmSetCommandData08 (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // 지정 축에 8bit IPCOMMAND 가져오기
    function AxmGetCommandData08 (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // 지정 축에 16bit IPCOMMAND Setting
    function AxmSetCommandData16 (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // 지정 축에 16bit IPCOMMAND 가져오기
    function AxmGetCommandData16 (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // 지정 축에 24bit IPCOMMAND Setting
    function AxmSetCommandData24 (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // 지정 축에 24bit IPCOMMAND 가져오기
    function AxmGetCommandData24 (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // 지정 축에 32bit IPCOMMAND Setting
    function AxmSetCommandData32 (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // 지정 축에 32bit IPCOMMAND 가져오기
    function AxmGetCommandData32 (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;

    // 지정 축에 QICOMMAND Setting
    function AxmSetCommandQi (lAxisNo : LongInt; sCommand : Byte) : DWord; stdcall;
    // 지정 축에 8bit QICOMMAND Setting
    function AxmSetCommandData08Qi (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // 지정 축에 8bit QICOMMAND 가져오기
    function AxmGetCommandData08Qi (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // 지정 축에 16bit QICOMMAND Setting
    function AxmSetCommandData16Qi (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // 지정 축에 16bit QICOMMAND 가져오기
    function AxmGetCommandData16Qi (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // 지정 축에 24bit QICOMMAND Setting
    function AxmSetCommandData24Qi (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // 지정 축에 24bit QICOMMAND 가져오기
    function AxmGetCommandData24Qi (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;
    // 지정 축에 32bit QICOMMAND Setting
    function AxmSetCommandData32Qi (lAxisNo : LongInt; sCommand : Byte; uData : DWord) : DWord; stdcall;
    // 지정 축에 32bit QICOMMAND 가져오기
    function AxmGetCommandData32Qi (lAxisNo : LongInt; sCommand : Byte; upData : PDWord) : DWord; stdcall;

    // 지정 축에 Port Data 가져오기 - IP
    function AxmGetPortData (lAxisNo : LongInt; wOffset : Word; upData : PDWord) : DWord; stdcall;
    // 지정 축에 Port Data Setting - IP
    function AxmSetPortData (lAxisNo : LongInt; wOffset : Word; dwData : DWord) : DWord; stdcall;
    // 지정 축에 Port Data 가져오기 - QI
    function AxmGetPortDataQi (lAxisNo : LongInt; byOffset : Word; wData : PWord) : DWord; stdcall;
    // 지정 축에 Port Data Setting - QI
    function AxmSetPortDataQi (lAxisNo : LongInt; byOffset : Word; wData : Word) : DWord; stdcall;

    // 지정 축에 스크립트를 설정한다. - IP
    // sc    : 스크립트 번호 (1 - 4)
    // event : 발생할 이벤트 SCRCON 을 정의한다.
    //         이벤트 설정 축갯수설정, 이벤트 발생할 축, 이벤트 내용 1,2 속성 설정한다.
    // cmd   : 어떤 내용을 바꿀것인지 선택 SCRCMD를 정의한다.
    // data  : 어떤 Data를 바꿀것인지 선택
    function AxmSetScriptCaptionIp (lAxisNo : LongInt; sc : LongInt; event : DWord; data : DWord) : DWord; stdcall;
    // 지정 축에 스크립트를 반환한다. - IP
    function AxmGetScriptCaptionIp (lAxisNo : LongInt; sc : LongInt; event : PDWord; data : PDWord) : DWord; stdcall;

    // 지정 축에 스크립트를 설정한다. - QI
    // sc    : 스크립트 번호 (1 - 4)
    // event : 발생할 이벤트 SCRCON 을 정의한다.
    //         이벤트 설정 축갯수설정, 이벤트 발생할 축, 이벤트 내용 1,2 속성 설정한다.
    // cmd   : 어떤 내용을 바꿀것인지 선택 SCRCMD를 정의한다.
    // data  : 어떤 Data를 바꿀것인지 선택
    function AxmSetScriptCaptionQi (lAxisNo : LongInt; sc : LongInt; event : DWord; cmd : DWord; data : DWord) : DWord; stdcall;
    // 지정 축에 스크립트를 반환한다. - QI
    function AxmGetScriptCaptionQi (lAxisNo : LongInt; sc : LongInt; event : PDWord; cmd : PDWord; data : PDWord) : DWord; stdcall;

    // 지정 축에 스크립트 내부 Queue Index를 Clear 시킨다.
    // uSelect IP.
    // uSelect(0): 스크립트 Queue Index 를 Clear한다.
    //        (1): 캡션 Queue를 Index Clear한다.
    // uSelect QI.
    // uSelect(0): 스크립트 Queue 1 Index 을 Clear한다.
    //        (1): 스크립트 Queue 2 Index 를 Clear한다.
    function AxmSetScriptCaptionQueueClear (lAxisNo : LongInt; uSelect : DWord) : DWord; stdcall;

    // 지정 축에 스크립트 내부 Queue의 Index 반환한다.
    // uSelect IP
    // uSelect(0): 스크립트 Queue Index를 읽어온다.
    //        (1): 캡션 Queue Index를 읽어온다.
    // uSelect QI.
    // uSelect(0): 스크립트 Queue 1 Index을 읽어온다.
    //        (1): 스크립트 Queue 2 Index를 읽어온다.
    function AxmGetScriptCaptionQueueCount (lAxisNo : LongInt; updata : PDWord; uSelect : DWord) : DWord; stdcall;

    // 지정 축에 스크립트 내부 Queue의 Data갯수 반환한다.
    // uSelect IP
    // uSelect(0): 스크립트 Queue Data 를 읽어온다.
    //        (1): 캡션 Queue Data를 읽어온다.
    // uSelect QI.
    // uSelect(0): 스크립트 Queue 1 Data 읽어온다.
    //        (1): 스크립트 Queue 2 Data 읽어온다.
    function AxmGetScriptCaptionQueueDataCount (lAxisNo : LongInt; updata : PDWord; uSelect : DWord) : DWord; stdcall;

    // 내부 데이타를 읽어온다.
    function AxmGetOptimizeDriveData () : DWord; stdcall;


    // 보드내에 레지스터를 Byte단위로 설정 및 확인한다.
    function AxmBoardWriteByte (lBoardNo : LongInt; wOffset : Word; byData : Byte) : DWord; stdcall;
    function AxmBoardReadByte (lBoardNo : LongInt; wOffset : Word; byData : PByte) : DWord; stdcall;

    // 보드내에 레지스터를 Word단위로 설정 및 확인한다.
    function AxmBoardWriteWord (lBoardNo : LongInt; wOffset : Word; wData : Word) : DWord; stdcall;
    function AxmBoardReadWord (lBoardNo : LongInt; wOffset : Word; wData : PWord) : DWord; stdcall;

    // 보드내에 레지스터를 DWord단위로 설정 및 확인한다.
    function AxmBoardWriteDWord (lBoardNo : LongInt; wOffset : Word; dwData : DWord) : DWord; stdcall;
    function AxmBoardReadDWord (lBoardNo : LongInt; wOffset : Word; dwData : PDWord) : DWord; stdcall;

    // 보드내에 모듈에 레지스터를 Byte설정 및 확인한다.
    function AxmModuleWriteByte (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; byData : Byte) : DWord; stdcall;
    function AxmModuleReadByte (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; byData : PByte) : DWord; stdcall;

    // 보드내에 모듈에 레지스터를 Word설정 및 확인한다.
    function AxmModuleWriteWord (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; wData : Word) : DWord; stdcall;
    function AxmModuleReadWord (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; wData : PWord) : DWord; stdcall;

    // 보드내에 모듈에 레지스터를 DWord설정 및 확인한다.
    function AxmModuleWriteDWord (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; dwData : DWord) : DWord; stdcall;
    function AxmModuleReadDWord (lBoardNo : LongInt; lModulePos : LongInt; wOffset : Word; dwData : PDWord) : DWord; stdcall;

    // 외부 위치 비교기에 값을 설정한다.(Pos = Unit)
    function AxmStatusSetActComparatorPos (lAxisNo : LongInt; dPos : Double) : DWord; stdcall;
    // 외부 위치 비교기에 값을 반환한다.(Positon = Unit)
    function AxmStatusGetActComparatorPos (lAxisNo : LongInt; dpPos : PDouble) : DWord; stdcall;

    // 내부 위치 비교기에 값을 설정한다.(Pos = Unit)
    function AxmStatusSetCmdComparatorPos (lAxisNo : LongInt; dPos : Double) : DWord; stdcall;
    // 내부 위치 비교기에 값을 반환한다.(Pos = Unit)
    function AxmStatusGetCmdComparatorPos (lAxisNo : LongInt; dpPos : PDouble) : DWord; stdcall;
    // ABS Position 을 Flash 에 설정한다.
    function AxmStatusSetFlashAbsOffset (lAxisNo : LongInt; dPosition : LongInt) : DWord; stdcall;
    // Flash 에 저장 된 ABS Position 을 반환한다.
    // dReadType  : Value in Flash Memory (0), Real used Value in memory(1)
    function AxmStatusGetFlashAbsOffset (lAxisNo : LongInt; dPosition : PLongInt; dReadType : DWord) : DWord; stdcall;
    // 사용자가 Flash 에 ABS Position 저장할 수 있는 옵션을 설정한다.
    function AxmStatusSetAbsOffsetWriteEnable (lAxisNo : LongInt; bStatus : Boolean) : DWord; stdcall;
    // ABS Position 설정 옵션의 상태를 반환한다.
    function AxmStatusGetAbsOffsetWriteEnable (lAxisNo : LongInt; bpStatus : bool*) : DWord; stdcall;

    //========== 추가 함수 =========================================================================================================
    // 직선 보간 을 속도만 가지고 무한대로 증가한다.
    // 속도 비율대로 거리를 넣어주어야 한다.
    function AxmLineMoveVel (lCoord : LongInt; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    //========= 센서 위치 구동 함수( 필독: IP만가능 , QI에는 기능없음)==============================================================
    // 지정 축의 Sensor 신호의 사용 유무 및 신호 입력 레벨을 설정한다.
    // 사용 유무 LOW(0), HIGH(1), UNUSED(2), USED(3)
    function AxmSensorSetSignal (lAxisNo : LongInt; uLevel : DWord) : DWord; stdcall;
    // 지정 축의 Sensor 신호의 사용 유무 및 신호 입력 레벨을 반환한다.
    function AxmSensorGetSignal (lAxisNo : LongInt; upLevel : PDWord) : DWord; stdcall;
    // 지정 축의 Sensor 신호의 입력 상태를 반환한다
    function AxmSensorReadSignal (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // 지정 축의 설정된 속도와 가속율로 센서 위치 드라이버를 구동한다.
    // Sensor 신호의 Active level입력 이후 상대 좌표로 설정된 거리만큼 구동후 정지한다.
    // 펄스가 출력되는 시점에서 함수를 벗어난다.
    // lMethod :  0 - 일반 구동, 1 - 센서 신호 검출 전은 저속 구동. 신호 검출 후 일반 구동
    //            2 - 저속 구동
    function AxmSensorMovePos (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; lMethod : LongInt) : DWord; stdcall;

    // 지정 축의 설정된 속도와 가속율로 센서 위치 드라이버를 구동한다.
    // Sensor 신호의 Active level입력 이후 상대 좌표로 설정된 거리만큼 구동후 정지한다.
    // 펄스 출력이 종료되는 시점에서 함수를 벗어난다.
    function AxmSensorStartMovePos (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; lMethod : LongInt) : DWord; stdcall;

    // 원점검색 진행스탭 변화의 기록을 반환한다.
    // *lpStepCount      : 기록된 Step의 개수
    // *upMainStepNumber : 기록된 MainStepNumber 정보의 배열포인트
    // *upStepNumber     : 기록된 StepNumber 정보의 배열포인트
    // *upStepBranch     : 기록된 Step별 Branch 정보의 배열포인트
    // 주의: 배열개수는 50개로 고정
    function AxmHomeGetStepTrace (lAxisNo : LongInt; lpStepCount : PLongInt; upMainStepNumber : PDWord; upStepNumber : PDWord; upStepBranch : PDWord) : DWord; stdcall;

    //=======추가 홈 서치 (PI-N804/404에만 해당됨.)=================================================================================
    // 사용자가 지정한 축의 홈설정 파라메타를 설정한다.(QI칩 전용 레지스터 이용).
    // uZphasCount : 홈 완료후에 Z상 카운트(0 - 15)
    // lHomeMode   : 홈 설정 모드( 0 - 12)
    // lClearSet   : 위치 클리어 , 잔여펄스 클리어 사용 선택 (0 - 3)
    //               0: 위치클리어 사용않함, 잔여펄스 클리어 사용 안함
    //                 1: 위치클리어 사용함, 잔여펄스 클리어 사용 안함
    //               2: 위치클리어 사용안함, 잔여펄스 클리어 사용함
    //               3: 위치클리어 사용함, 잔여펄스 클리어 사용함.
    // dOrgVel : 홈관련 Org  Speed 설정
    // dLastVel: 홈관련 Last Speed 설정
    function AxmHomeSetConfig (lAxisNo : LongInt; uZphasCount : DWord; lHomeMode : LongInt; lClearSet : LongInt; dOrgVel : Double; dLastVel : Double; dLeavePos : Double) : DWord; stdcall;
    // 사용자가 지정한 축의 홈설정 파라메타를 반환한다.
    function AxmHomeGetConfig (lAxisNo : LongInt; upZphasCount : PDWord; lpHomeMode : PLongInt; lpClearSet : PLongInt; dpOrgVel : PDouble; dpLastVel : PDouble; dpLeavePos : PDouble) : DWord; stdcall;

    // 사용자가 지정한 축의 홈 서치를 시작한다.
    // lHomeMode 사용시 설정 : 0 - 5 설정 (Move Return후에 Search를  시작한다.)
    // lHomeMode -1로 그대로 사용시 HomeConfig에서 사용한대로 그대로 설정됨.
    // 구동방향      : Vel값이 양수이면 CW, 음수이면 CCW.
    function AxmHomeSetMoveSearch (lAxisNo : LongInt; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 사용자가 지정한 축의 홈 리턴을 시작한다.
    // lHomeMode 사용시 설정 : 0 - 12 설정
    // lHomeMode -1로 그대로 사용시 HomeConfig에서 사용한대로 그대로 설정됨.
    // 구동방향      : Vel값이 양수이면 CW, 음수이면 CCW.
    function AxmHomeSetMoveReturn (lAxisNo : LongInt; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 사용자가 지정한 축의 홈 이탈을 시작한다.
    // 구동방향      : Vel값이 양수이면 CW, 음수이면 CCW.
    function AxmHomeSetMoveLeave (lAxisNo : LongInt; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 사용자가 지정한 다축의 홈 서치을 시작한다.
    // lHomeMode 사용시 설정 : 0 - 5 설정 (Move Return후에 Search를  시작한다.)
    // lHomeMode -1로 그대로 사용시 HomeConfig에서 사용한대로 그대로 설정됨.
    // 구동방향      : Vel값이 양수이면 CW, 음수이면 CCW.
    function AxmHomeSetMultiMoveSearch (lArraySize : LongInt; lpAxesNo : PLongInt; dpVel : PDouble; dpAccel : PDouble; dpDecel : PDouble) : DWord; stdcall;

    //지정된 좌표계의 구동 속도 프로파일 모드를 설정한다.
    // (주의점 : 반드시 축맵핑 하고 사용가능)
    // ProfileMode : '0' - 대칭 Trapezode
    //               '1' - 비대칭 Trapezode
    //               '2' - 대칭 Quasi-S Curve
    //               '3' - 대칭 S Curve
    //               '4' - 비대칭 S Curve
    function AxmContiSetProfileMode (lCoord : LongInt; uProfileMode : DWord) : DWord; stdcall;
    // 지정된 좌표계의 구동 속도 프로파일 모드를 반환한다.
    function AxmContiGetProfileMode (lCoord : LongInt; upProfileMode : PDWord) : DWord; stdcall;

    //========== DIO 인터럽트 플래그 레지스트 읽기
    // 지정한 입력 접점 모듈, Interrupt Flag Register의 Offset 위치에서 bit 단위로 인터럽트 발생 상태 값을 읽음
    function AxdiInterruptFlagReadBit (lModuleNo : LongInt; lOffset : LongInt; upValue : PDWord) : DWord; stdcall;
    // 지정한 입력 접점 모듈, Interrupt Flag Register의 Offset 위치에서 byte 단위로 인터럽트 발생 상태 값을 읽음
    function AxdiInterruptFlagReadByte (lModuleNo : LongInt; lOffset : LongInt; upValue : PDWord) : DWord; stdcall;
    // 지정한 입력 접점 모듈, Interrupt Flag Register의 Offset 위치에서 word 단위로 인터럽트 발생 상태 값을 읽음
    function AxdiInterruptFlagReadWord (lModuleNo : LongInt; lOffset : LongInt; upValue : PDWord) : DWord; stdcall;
    // 지정한 입력 접점 모듈, Interrupt Flag Register의 Offset 위치에서 double word 단위로 인터럽트 발생 상태 값을 읽음
    function AxdiInterruptFlagReadDword (lModuleNo : LongInt; lOffset : LongInt; upValue : PDWord) : DWord; stdcall;
    // 전체 입력 접점 모듈, Interrupt Flag Register의 Offset 위치에서 bit 단위로 인터럽트 발생 상태 값을 읽음
    function AxdiInterruptFlagRead (lOffset : LongInt; upValue : PDWord) : DWord; stdcall;

    //========= 로그 관련 함수 ==========================================================================================
    // 현재 자동으로 설정됨.
    // 설정 축의 함수 실행 결과를 EzSpy에서 모니터링 할 수 있도록 설정 또는 해제하는 함수이다.
    // uUse : 사용 유무 => DISABLE(0), ENABLE(1)
    function AxmLogSetAxis (lAxisNo : LongInt; uUse : DWord) : DWord; stdcall;

    // EzSpy에서의 설정 축 함수 실행 결과 모니터링 여부를 확인하는 함수이다.
    function AxmLogGetAxis (lAxisNo : LongInt; upUse : PDWord) : DWord; stdcall;

    //=========== 로그 출력 관련 함수
    //지정한 입력 채널의 EzSpy에 로그 출력 여부를 설정한다.
    function AxaiLogSetChannel (lChannelNo : LongInt; uUse : DWord) : DWord; stdcall;
    //지정한 입력 채널의 EzSpy에 로그 출력 여부를 확인한다.
    function AxaiLogGetChannel (lChannelNo : LongInt; upUse : PDWord) : DWord; stdcall;

    //==지정한 출력 채널의 EzSpy 로그 출력
    //지정한 출력 채널의 EzSpy에 로그 출력 여부를 설정한다.
    function AxaoLogSetChannel (lChannelNo : LongInt; uUse : DWord) : DWord; stdcall;
    //지정한 출력 채널의 EzSpy에 로그 출력 여부를 확인한다.
    function AxaoLogGetChannel (lChannelNo : LongInt; upUse : PDWord) : DWord; stdcall;

    //==Log
    // 지정한 모듈의 EzSpy에 로그 출력 여부 설정
    function AxdLogSetModule (lModuleNo : LongInt; uUse : DWord) : DWord; stdcall;
    // 지정한 모듈의 EzSpy에 로그 출력 여부 확인
    function AxdLogGetModule (lModuleNo : LongInt; upUse : PDWord) : DWord; stdcall;

    // 지정한 보드가 RTEX 모드일 때 그 보드의 firmware 버전을 확인한다.
    function AxlGetFirmwareVersion (lBoardNo : LongInt; szVersion : PChar) : DWord; stdcall;
    // 지정한 보드로 Firmware를 전송 한다.
    function AxlSetFirmwareCopy (lBoardNo : LongInt; wData : PWord; wCmdData : PWord) : DWord; stdcall;
    // 지정한 보드로 Firmware Update를 수행한다.
    function AxlSetFirmwareUpdate (lBoardNo : LongInt) : DWord; stdcall;
    // 지정한 보드의 현재 RTEX 초기화 상태를 확인 한다.
    function AxlCheckStatus (lBoardNo : LongInt; dwStatus : PDWord) : DWord; stdcall;
    // 지정한 축에 RTEX Master board에 범용 명령을 실행 합니다.
    function AxlRtexUniversalCmd (lBoardNo : LongInt; wCmd : Word; wOffset : Word; wData : PWord) : DWord; stdcall;
    // 지정한 축의 RTEX 통신 명령을 실행한다.
    function AxmRtexSlaveCmd (lAxisNo : LongInt; dwCmdCode : DWord; dwTypeCode : DWord; dwIndexCode : DWord; dwCmdConfigure : DWord; dwValue : DWord) : DWord; stdcall;
    // 지정한 축에 실행한 RTEX 통신 명령의 결과값을 확인한다.
    function AxmRtexGetSlaveCmdResult (lAxisNo : LongInt; dwIndex : PDWord; dwValue : PDWord) : DWord; stdcall;
    // 지정한 축에 실행한 RTEX 통신 명령의 결과값을 확인한다. PCIE-Rxx04-RTEX 전용
    function AxmRtexGetSlaveCmdResultEx (lAxisNo : LongInt; dwpCommand : PDWord; dwpType : PDWord; dwpIndex : PDWord; dwpValue : PDWord) : DWord; stdcall;
    // 지정한 축에 RTEX 상태 정보를 확인한다.
    function AxmRtexGetAxisStatus (lAxisNo : LongInt; dwStatus : PDWord) : DWord; stdcall;
    // 지정한 축에 RTEX 통신 리턴 정보를 확인한다.(Actual position, Velocity, Torque)
    function AxmRtexGetAxisReturnData (lAxisNo : LongInt; dwReturn1 : PDWord; dwReturn2 : PDWord; dwReturn3 : PDWord) : DWord; stdcall;
    // 지정한 축에 RTEX Slave 축의 현재 상태 정보를 확인한다.(mechanical, Inposition and etc)
    function AxmRtexGetAxisSlaveStatus (lAxisNo : LongInt; dwStatus : PDWord) : DWord; stdcall;

    // 지정한 축에 MLII Slave 축에 범용 네트웍 명령어를 기입한다.
    function AxmSetAxisCmd (lAxisNo : LongInt; tagCommand : PDWord) : DWord; stdcall;
    // 지정한 축에 MLII Slave 축에 범용 네트웍 명령의 결과를 확인한다.
    function AxmGetAxisCmdResult (lAxisNo : LongInt; tagCommand : PDWord) : DWord; stdcall;

    // 지정한 SIIIH Slave 모듈에 네트웍 명령의 결과를 기입하고 반환 한다.
    function AxdSetAndGetSlaveCmdResult (lModuleNo : LongInt; tagSetCommand : PDWord; tagGetCommand : PDWord) : DWord; stdcall;
    function AxaSetAndGetSlaveCmdResult (lModuleNo : LongInt; tagSetCommand : PDWord; tagGetCommand : PDWord) : DWord; stdcall;
    function AxcSetAndGetSlaveCmdResult (lModuleNo : LongInt; tagSetCommand : PDWord; tagGetCommand : PDWord) : DWord; stdcall;

    // DPRAM 데이터를 확인한다.
    function AxlGetDpRamData (lBoardNo : LongInt; wAddress : Word; dwpRdData : PDWord) : DWord; stdcall;
    // DPRAM 데이터를 Word단위로 확인한다.
    function AxlBoardReadDpramWord (lBoardNo : LongInt; wOffset : Word; dwpRdData : PDWord) : DWord; stdcall;
    // DPRAM 데이터를 Word단위로 설정한다.
    function AxlBoardWriteDpramWord (lBoardNo : LongInt; wOffset : Word; dwWrData : DWord) : DWord; stdcall;

    // 각 보드의 각 SLAVE별로 명령을 전송한다.
    function AxlSetSendBoardEachCommand (lBoardNo : LongInt; dwCommand : DWord; dwpSendData : PDWord; dwLength : DWord) : DWord; stdcall;
    // 각 보드로 명령을 전송한다.
    function AxlSetSendBoardCommand (lBoardNo : LongInt; dwCommand : DWord; dwpSendData : PDWord; dwLength : DWord) : DWord; stdcall;
    // 각 보드의 응답을 확인한다.
    function AxlGetResponseBoardCommand (lBoardNo : LongInt; dwpReadData : PDWord) : DWord; stdcall;

    // Network Type Master 보드에서 Slave 들의 Firmware Version을 읽어 오는 함수.
    // ucaFirmwareVersion unsigned char 형의 Array로 선언하고 크기가 4이상이 되도록 선언 해야 한다.
    function AxmInfoGetFirmwareVersion (lAxisNo : LongInt; ucaFirmwareVersion : PWord) : DWord; stdcall;
    function AxaInfoGetFirmwareVersion (lModuleNo : LongInt; ucaFirmwareVersion : PWord) : DWord; stdcall;
    function AxdInfoGetFirmwareVersion (lModuleNo : LongInt; ucaFirmwareVersion : PWord) : DWord; stdcall;
    function AxcInfoGetFirmwareVersion (lModuleNo : LongInt; ucaFirmwareVersion : PWord) : DWord; stdcall;

    //======== PCI-R1604-MLII 전용 함수===========================================================================
    // INTERPOLATE and LATCH Command의 Option Field의 Torq Feed Forward의 값을 설정 하도록 합니다.
    // 기본값은 MAX로 설정되어 있습니다.
    // 설정값은 0 ~ 4000H까지 설정 할 수 있습니다.
    // 설정값은 4000H이상으로 설정하면 설정은 그 이상으로 설정되나 동작은 4000H값이 적용 됩니다.
    function AxmSetTorqFeedForward (lAxisNo : LongInt; dwTorqFeedForward : DWord) : DWord; stdcall;

    // INTERPOLATE and LATCH Command의 Option Field의 Torq Feed Forward의 값을 읽어오는 함수 입니다.
    // 기본값은 MAX로 설정되어 있습니다.
    function AxmGetTorqFeedForward (lAxisNo : LongInt; dwpTorqFeedForward : PDWord) : DWord; stdcall;

    // INTERPOLATE and LATCH Command의 VFF Field의 Velocity Feed Forward의 값을 설정 하도록 합니다.
    // 기본값은 '0'로 설정되어 있습니다.
    // 설정값은 0 ~ FFFFH까지 설정 할 수 있습니다.
    function AxmSetVelocityFeedForward (lAxisNo : LongInt; dwVelocityFeedForward : DWord) : DWord; stdcall;

    // INTERPOLATE and LATCH Command의 VFF Field의 Velocity Feed Forward의 값을 읽어오는 함수 입니다.
    function AxmGetVelocityFeedForward (lAxisNo : LongInt; dwpVelocityFeedForward : PDWord) : DWord; stdcall;

    // Encoder type을 설정한다.
    // 기본값은 0(TYPE_INCREMENTAL)로 설정되어 있습니다.
    // 설정값은 0 ~ 1까지 설정 할 수 있습니다.
    // 설정값 : 0(TYPE_INCREMENTAL), 1(TYPE_ABSOLUTE).
    function AxmSignalSetEncoderType (lAxisNo : LongInt; dwEncoderType : DWord) : DWord; stdcall;

    // Encoder type을 확인한다.
    function AxmSignalGetEncoderType (lAxisNo : LongInt; dwpEncoderType : PDWord) : DWord; stdcall;
    //========================================================================================================

    // Slave Firmware Update를 위해 추가
    //DWORD   __stdcall AxmSetSendAxisCommand(long lAxisNo, WORD wCommand, WORD* wpSendData, WORD wLength);

    //======== PCI-R1604-RTEX, RTEX-PM 전용 함수==============================================================
    // 범용 입력 2,3번 입력시 JOG 구동 속도를 설정한다.
    // 구동에 관련된 모든 설정(Ex, PulseOutMethod, MoveUnitPerPulse 등)들이 완료된 이후 한번만 실행하여야 한다.
    function AxmMotSetUserMotion (lAxisNo : LongInt; dVelocity : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 범용 입력 2,3번 입력시 JOG 구동 동작 사용 가부를 설정한다.
    // 설정값 :  0(DISABLE), 1(ENABLE)
    function AxmMotSetUserMotionUsage (lAxisNo : LongInt; dwUsage : DWord) : DWord; stdcall;

    // MPGP 입력을 사용하여 Load/UnLoad 위치를 자동으로 이동하는 기능 설정.
    function AxmMotSetUserPosMotion (lAxisNo : LongInt; dVelocity : Double; dAccel : Double; dDecel : Double; dLoadPos : Double; dUnLoadPos : Double; dwFilter : DWord; dwDelay : DWord) : DWord; stdcall;

    // MPGP 입력을 사용하여 Load/UnLoad 위치를 자동으로 이동하는 기능 설정.
    // 설정값 :  0(DISABLE), 1(Position 기능 A 사용), 2(Position 기능 B 사용)
    function AxmMotSetUserPosMotionUsage (lAxisNo : LongInt; dwUsage : DWord) : DWord; stdcall;
    //========================================================================================================

    //======== SIO-CN2CH/HPC4, 절대 위치 트리거 기능 모듈 전용 함수================================================
    // 메모리 데이터 쓰기 함수
    function AxcKeWriteRamDataAddr (lChannelNo : LongInt; dwAddr : DWord; dwData : DWord) : DWord; stdcall;
    // 메모리 데이터 읽기 함수
    function AxcKeReadRamDataAddr (lChannelNo : LongInt; dwAddr : DWord; dwpData : PDWord) : DWord; stdcall;
    // 메모리 초기화 함수
    function AxcKeResetRamDataAll (lModuleNo : LongInt; dwData : DWord) : DWord; stdcall;
    // 트리거 타임 아웃 설정 함수
    function AxcTriggerSetTimeout (lChannelNo : LongInt; dwTimeout : DWord) : DWord; stdcall;
    // 트리거 타임 아웃 확인 함수
    function AxcTriggerGetTimeout (lChannelNo : LongInt; dwpTimeout : PDWord) : DWord; stdcall;
    // 트리거 대기 상태 확인 함수
    function AxcStatusGetWaitState (lChannelNo : LongInt; dwpState : PDWord) : DWord; stdcall;
    // 트리거 대기 상태 설정 함수
    function AxcStatusSetWaitState (lChannelNo : LongInt; dwState : DWord) : DWord; stdcall;

    // 지정 채널에 명령어 기입.
    function AxcKeSetCommandData32 (lChannelNo : LongInt; dwCommand : DWord; dwData : DWord) : DWord; stdcall;
    // 지정 채널에 명령어 기입.
    function AxcKeSetCommandData16 (lChannelNo : LongInt; dwCommand : DWord; wData : Word) : DWord; stdcall;
    // 지정 채널의 레지스터 확인.
    function AxcKeGetCommandData32 (lChannelNo : LongInt; dwCommand : DWord; dwpData : PDWord) : DWord; stdcall;
    // 지정 채널의 레지스터 확인.
    function AxcKeGetCommandData16 (lChannelNo : LongInt; dwCommand : DWord; wpData : PWord) : DWord; stdcall;
    //========================================================================================================

    //======== PCI-N804/N404 전용, Sequence Motion ===================================================================
    // Sequence Motion의 축 정보를 설정 합니다. (최소 1축)
    // lSeqMapNo : 축 번호 정보를 담는 Sequence Motion Index Point
    // lSeqMapSize : 축 번호 갯수
    // long* LSeqAxesNo : 축 번호 배열
    function AxmSeqSetAxisMap (lSeqMapNo : LongInt; lSeqMapSize : LongInt; lSeqAxesNo : PLongInt) : DWord; stdcall;
    function AxmSeqGetAxisMap (lSeqMapNo : LongInt; lSeqMapSize : PLongInt; lSeqAxesNo : PLongInt) : DWord; stdcall;

    // Sequence Motion의 기준(Master) 축을 설정 합니다.
    // 반드시 AxmSeqSetAxisMap(...) 에 설정된 축 내에서 설정하여야 합니다.
    function AxmSeqSetMasterAxisNo (lSeqMapNo : LongInt; lMasterAxisNo : LongInt) : DWord; stdcall;

    // Sequence Motion의 Node 적재 시작을 라이브러리에 알립니다.
    function AxmSeqBeginNode (lSeqMapNo : LongInt) : DWord; stdcall;

    // Sequence Motion의 Node 적재 종료를 라이브러리에 알립니다.
    function AxmSeqEndNode (lSeqMapNo : LongInt) : DWord; stdcall;

    // Sequence Motion의 구동을 시작 합니다.
    function AxmSeqStart (lSeqMapNo : LongInt; dwStartOption : DWord) : DWord; stdcall;

    // Sequence Motion의 각 Profile Node 정보를 라이브러리에 입력 합니다.
    // 만약 1축 Sequence Motion을 사용하더라도, *dPosition는 1개의 Array로 지정하여 주시기 바랍니다.
    function AxmSeqAddNode (lSeqMapNo : LongInt; dPosition : PDouble; dVelocity : Double; dAcceleration : Double; dDeceleration : Double; dNextVelocity : Double) : DWord; stdcall;

    // Sequence Motion이 구동 시 현재 실행 중인 Node Index를 알려 줍니다.
    function AxmSeqGetNodeNum (lSeqMapNo : LongInt; lCurNodeNo : PLongInt) : DWord; stdcall;

    // Sequence Motion의 총 Node Count를 확인 합니다.
    function AxmSeqGetTotalNodeNum (lSeqMapNo : LongInt; lTotalNodeCnt : PLongInt) : DWord; stdcall;

    // Sequence Motion이 현재 구동 중인지 확인 합니다.
    // dwInMotion : 0(구동 종료), 1(구동 중)
    function AxmSeqIsMotion (lSeqMapNo : LongInt; dwInMotion : PDWord) : DWord; stdcall;

    // Sequence Motion의 Memory를 Clear 합니다.
    // AxmSeqSetAxisMap(...), AxmSeqSetMasterAxisNo(...) 에서 설정된 값은 유지됩니다.
    function AxmSeqWriteClear (lSeqMapNo : LongInt) : DWord; stdcall;

    // Sequence Motion의 구동을 종료 합니다.
    // dwStopMode : 0(EMERGENCY_STOP), 1(SLOWDOWN_STOP)
    function AxmSeqStop (lSeqMapNo : LongInt; dwStopMode : DWord) : DWord; stdcall;
    //========================================================================================================


    //======== PCIe-Rxx04-SIIIH 전용 함수==========================================================================
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

    //======== PCI-R32IOEV-RTEX 전용 함수===========================================================================
    // I/O 포트로 할당된 HPI register 를 읽고 쓰기위한 API 함수.
    // I/O Registers for HOST interface.
    // I/O 00h Host status register (HSR)
    // I/O 04h Host-to-DSP control register (HDCR)
    // I/O 08h DSP page register (DSPP)
    // I/O 0Ch Reserved
    function AxlSetIoPort (lBoardNo : LongInt; dwAddr : DWord; dwData : DWord) : DWord; stdcall;
    function AxlGetIoPort (lBoardNo : LongInt; dwAddr : DWord; dwpData : PDWord) : DWord; stdcall;

    //======== PCI-R3200-MLIII 전용 함수===========================================================================
    /*
    // M-III Master 보드 펌웨어 업데이트 기본 정보 설정 함수
    DWORD   __stdcall AxlM3SetFWUpdateInit(long lBoardNo, DWORD dwTotalPacketSize);
    // M-III Master 보드 펌웨어 업데이트 기본 정보 설정 결과 확인 함수
    DWORD   __stdcall AxlM3GetFWUpdateInit(long lBoardNo, DWORD *dwTotalPacketSize);
    // M-III Master 보드 펌웨어 업데이트 자료 전달 함수
    DWORD   __stdcall AxlM3SetFWUpdateCopy(long lBoardNo, DWORD *lFWUpdataData, DWORD dwLength);
    // M-III Master 보드 펌웨어 업데이트 자료 전달 결과 확인 함수
    DWORD   __stdcall AxlM3GetFWUpdateCopy(long lBoardNo, BYTE bCrcData, DWORD *lFWUpdataResult);
    // M-III Master 보드 펌웨어 업데이트 실행
    DWORD   __stdcall AxlM3SetFWUpdate(long lBoardNo, DWORD dwSectorNo);
    // M-III Master 보드 펌웨어 업데이트 실행 결과 확인
    DWORD   __stdcall AxlM3GetFWUpdate(long lBoardNo, DWORD *dwSectorNo, DWORD *dwIsDone);
    */
    // M-III Master 보드 펌웨어 업데이트 기본 정보 설정 함수
    function AxlM3SetFWUpdateInit (lBoardNo : LongInt; dwTotalPacketSize : DWord; dwProcTotalStepNo : DWord) : DWord; stdcall;
    // M-III Master 보드 펌웨어 업데이트 기본 정보 설정 결과 확인 함수
    function AxlM3GetFWUpdateInit (lBoardNo : LongInt; dwTotalPacketSize : PDWord; dwProcTotalStepNo : PDWord) : DWord; stdcall;

    // M-III Master 보드 펌웨어 업데이트 자료 전달 함수
    function AxlM3SetFWUpdateCopy (lBoardNo : LongInt; pdwPacketData : PDWord; dwPacketSize : DWord) : DWord; stdcall;
    // M-III Master 보드 펌웨어 업데이트 자료 전달 결과 확인 함수
    function AxlM3GetFWUpdateCopy (lBoardNo : LongInt; dwPacketSize : PDWord) : DWord; stdcall;

    // M-III Master 보드 펌웨어 업데이트 실행
    function AxlM3SetFWUpdate (lBoardNo : LongInt; dwFlashBurnStepNo : DWord) : DWord; stdcall;
    // M-III Master 보드 펌웨어 업데이트 실행 결과 확인
    function AxlM3GetFWUpdate (lBoardNo : LongInt; dwFlashBurnStepNo : PDWord; dwIsFlashBurnDone : PDWord) : DWord; stdcall;

    // M-III Master 보드 EEPROM 데이터 설정 함수
    function AxlM3SetCFGData (lBoardNo : LongInt; pCmdData : PDWord; CmdDataSize : DWord) : DWord; stdcall;
    // M-III Master 보드 EEPROM 데이터 가져오기 함수
    function AxlM3GetCFGData (lBoardNo : LongInt; pCmdData : PDWord; CmdDataSize : DWord) : DWord; stdcall;

    // M-III Master 보드 CONNECT PARAMETER 기본 정보 설정 함수
    function AxlM3SetMCParaUpdateInit (lBoardNo : LongInt; wCh0Slaves : Word; wCh1Slaves : Word; dwCh0CycTime : DWord; dwCh1CycTime : DWord; dwChInfoMaxRetry : DWord) : DWord; stdcall;
    // M-III Master 보드 CONNECT PARAMETER 기본 정보 설정 결과 확인 함수
    function AxlM3GetMCParaUpdateInit (lBoardNo : LongInt; wCh0Slaves : PWord; wCh1Slaves : PWord; dwCh0CycTime : PDWord; dwCh1CycTime : PDWord; dwChInfoMaxRetry : PDWord) : DWord; stdcall;
    // M-III Master 보드 CONNECT PARAMETER 기본 정보 전달 함수
    function AxlM3SetMCParaUpdateCopy (lBoardNo : LongInt; wIdx : Word; wChannel : Word; wSlaveAddr : Word; dwProtoCalType : DWord; dwTransBytes : DWord; dwDeviceCode : DWord) : DWord; stdcall;
    // M-III Master 보드 CONNECT PARAMETER 기본 정보 전달 결과 확인 함수
    function AxlM3GetMCParaUpdateCopy (lBoardNo : LongInt; wIdx : Word; wChannel : PWord; wSlaveAddr : PWord; dwProtoCalType : PDWord; dwTransBytes : PDWord; dwDeviceCode : PDWord) : DWord; stdcall;

    // M-III Master 보드내에 레지스터를 DWord단위로 확인 함수
    function AxlBoardReadDWord (lBoardNo : LongInt; wOffset : Word; dwData : PDWord) : DWord; stdcall;
    // M-III Master 보드내에 레지스터를 DWord단위로 설정 함수
    function AxlBoardWriteDWord (lBoardNo : LongInt; wOffset : Word; dwData : DWord) : DWord; stdcall;

    // 보드내에 확장 레지스터를 DWord단위로 설정 및 확인한다.
    function AxlBoardReadDWordEx (lBoardNo : LongInt; dwOffset : DWord; dwData : PDWord) : DWord; stdcall;
    function AxlBoardWriteDWordEx (lBoardNo : LongInt; dwOffset : DWord; dwData : DWord) : DWord; stdcall;

    // 서보를 정지 모드로 설정 함수
    function AxmM3ServoSetCtrlStopMode (lAxisNo : LongInt; bStopMode : Byte) : DWord; stdcall;
    // 서보를 Lt 선택 상태로 설정 함수
    function AxmM3ServoSetCtrlLtSel (lAxisNo : LongInt; bLtSel1 : Byte; bLtSel2 : Byte) : DWord; stdcall;
    // 서보의 IO 입력 상태를 확인 함수
    function AxmStatusReadServoCmdIOInput (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;
    // 서보의 보간 구동 함수
    function AxmM3ServoExInterpolate (lAxisNo : LongInt; dwTPOS : DWord; dwVFF : DWord; dwTFF : DWord; dwTLIM : DWord; dwExSig1 : DWord; dwExSig2 : DWord) : DWord; stdcall;
    // 서보 엑츄레이터 바이어스 설정 함수
    function AxmM3ServoSetExpoAccBias (lAxisNo : LongInt; wBias : Word) : DWord; stdcall;
    // 서보 엑츄레이터 시간 설정 함수
    function AxmM3ServoSetExpoAccTime (lAxisNo : LongInt; wTime : Word) : DWord; stdcall;
    // 서보의 이동 시간을 설정 함수
    function AxmM3ServoSetMoveAvrTime (lAxisNo : LongInt; wTime : Word) : DWord; stdcall;
    // 서보의 Acc 필터 설정 함수
    function AxmM3ServoSetAccFilter (lAxisNo : LongInt; bAccFil : Byte) : DWord; stdcall;
    // 서보의 상태 모니터1 설정 함수
    function AxmM3ServoSetCprmMonitor1 (lAxisNo : LongInt; bMonSel : Byte) : DWord; stdcall;
    // 서보의 상태 모니터2 설정 함수
    function AxmM3ServoSetCprmMonitor2 (lAxisNo : LongInt; bMonSel : Byte) : DWord; stdcall;
    // 서보의 상태 모니터1 확인 함수
    function AxmM3ServoStatusReadCprmMonitor1 (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;
    // 서보의 상태 모니터2 확인 함수
    function AxmM3ServoStatusReadCprmMonitor2 (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;
    // 서보 엑츄레이터 Dec 설정 함수
    function AxmM3ServoSetAccDec (lAxisNo : LongInt; wAcc1 : Word; wAcc2 : Word; wAccSW : Word; wDec1 : Word; wDec2 : Word; wDecSW : Word) : DWord; stdcall;
    // 서보 정지 설정 함수
    function AxmM3ServoSetStop (lAxisNo : LongInt; lMaxDecel : LongInt) : DWord; stdcall;

    //========== 표준 I/O 기기 공통 커맨드 =========================================================================
    // Network제품 각 슬레이브 기기의 파라미터 설정 값을 반환하는 함수
    function AxlM3GetStationParameter (lBoardNo : LongInt; lModuleNo : LongInt; wNo : Word; bSize : Byte; bModuleType : Byte; pbParam : PByte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 파라미터 값을 설정하는 함수
    function AxlM3SetStationParameter (lBoardNo : LongInt; lModuleNo : LongInt; wNo : Word; bSize : Byte; bModuleType : Byte; pbParam : PByte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 ID값을 반환하는 함수
    function AxlM3GetStationIdRd (lBoardNo : LongInt; lModuleNo : LongInt; bIdCode : Byte; bOffset : Byte; bSize : Byte; bModuleType : Byte; pbParam : PByte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 무효 커맨드로 사용하는 함수
    function AxlM3SetStationNop (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 셋업을 실시하는 함수
    function AxlM3SetStationConfig (lBoardNo : LongInt; lModuleNo : LongInt; bConfigMode : Byte; bModuleType : Byte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 알람 및 경고 상태 값을 반환하는 함수
    function AxlM3GetStationAlarm (lBoardNo : LongInt; lModuleNo : LongInt; wAlarmRdMod : Word; wAlarmIndex : Word; bModuleType : Byte; pwAlarmData : PWord) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 알람 및 경고 상태를 해제하는 함수
    function AxlM3SetStationAlarmClear (lBoardNo : LongInt; lModuleNo : LongInt; wAlarmClrMod : Word; bModuleType : Byte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기와의 동기통신을 설정하는 함수
    function AxlM3SetStationSyncSet (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기와의 연결을 설정하는 함수
    function AxlM3SetStationConnect (lBoardNo : LongInt; lModuleNo : LongInt; bVer : Byte; bComMode : Byte; bComTime : Byte; bProfileType : Byte; bModuleType : Byte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기와의 연결 끊음을 설정하는 함수
    function AxlM3SetStationDisConnect (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 비휘발성 파라미터 설정 값을 반환하는 함수
    function AxlM3GetStationStoredParameter (lBoardNo : LongInt; lModuleNo : LongInt; wNo : Word; bSize : Byte; bModuleType : Byte; pbParam : PByte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 비휘발성 파라미터 값을 설정하는 함수
    function AxlM3SetStationStoredParameter (lBoardNo : LongInt; lModuleNo : LongInt; wNo : Word; bSize : Byte; bModuleType : Byte; pbParam : PByte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 메모리 설정 값을 반환하는 함수
    function AxlM3GetStationMemory (lBoardNo : LongInt; lModuleNo : LongInt; wSize : Word; dwAddress : DWord; bModuleType : Byte; bMode : Byte; bDataType : Byte; pbData : PByte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 메모리 값을 설정하는 함수
    function AxlM3SetStationMemory (lBoardNo : LongInt; lModuleNo : LongInt; wSize : Word; dwAddress : DWord; bModuleType : Byte; bMode : Byte; bDataType : Byte; pbData : PByte) : DWord; stdcall;

    //========== 표준 I/O 기기 커넥션 커맨드 =========================================================================
    // Network제품 각 재정열된 슬레이브 기기의 자동 억세스 모드 값을 설정하는 함수
    function AxlM3SetStationAccessMode (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; bRWSMode : Byte) : DWord; stdcall;
    // Network제품 각 재정열된 슬레이브 기기의 자동 억세스 모드 설정값을 반환하는 함수
    function AxlM3GetStationAccessMode (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; bRWSMode : PByte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 동기 자동 연결 모드를 설정하는 함수
    function AxlM3SetAutoSyncConnectMode (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; dwAutoSyncConnectMode : DWord) : DWord; stdcall;
    // Network제품 각 슬레이브 기기의 동기 자동 연결 모드 설정값을 반환하는 함수
    function AxlM3GetAutoSyncConnectMode (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; dwpAutoSyncConnectMode : PDWord) : DWord; stdcall;
    // Network제품 각 슬레이브 기기에 대한 단일 동기화 연결을 설정하는 함수
    function AxlM3SyncConnectSingle (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기에 대한 단일 동기화 연결 끊음을 설정하는 함수
    function AxlM3SyncDisconnectSingle (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte) : DWord; stdcall;
    // Network제품 각 슬레이브 기기와의 연결 상태를 확인하는 함수
    function AxlM3IsOnLine (lBoardNo : LongInt; lModuleNo : LongInt; dwData : PDWord) : DWord; stdcall;

    //========== 표준 I/O 프로파일 커맨드 =========================================================================
    // Network제품 각 동기화 상태의 슬레이브 I/O 기기에 대한 데이터 설정값을 반환하는 함수
    function AxlM3GetStationRWS (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; pdwParam : PDWord; bSize : Byte) : DWord; stdcall;
    // Network제품 각 동기화 상태의 슬레이브 I/O 기기에 대한 데이터값을 설정하는 함수
    function AxlM3SetStationRWS (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; pdwParam : PDWord; bSize : Byte) : DWord; stdcall;
    // Network제품 각 비동기화 상태의 슬레이브 I/O 기기에 대한 데이터 설정값을 반환하는 함수
    function AxlM3GetStationRWA (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; pdwParam : PDWord; bSize : Byte) : DWord; stdcall;
    // Network제품 각 비동기화 상태의 슬레이브 I/O 기기에 대한 데이터값을 설정하는 함수
    function AxlM3SetStationRWA (lBoardNo : LongInt; lModuleNo : LongInt; bModuleType : Byte; pdwParam : PDWord; bSize : Byte) : DWord; stdcall;

    // MLIII adjustment operation을 설정 한다.
    // dwReqCode == 0x1005 : parameter initialization : 20sec
    // dwReqCode == 0x1008 : absolute encoder reset   : 5sec
    // dwReqCode == 0x100E : automatic offset adjustment of motor current detection signals  : 5sec
    // dwReqCode == 0x1013 : Multiturn limit setting  : 5sec
    function AxmM3AdjustmentOperation (lAxisNo : LongInt; dwReqCode : DWord) : DWord; stdcall;

    // M3 전용 원점 검색 진행 상태 진단용 함수이다.
    function AxmHomeGetM3FWRealRate (lAxisNo : LongInt; upHomeMainStepNumber : PDWord; upHomeSubStepNumber : PDWord; upHomeLastMainStepNumber : PDWord; upHomeLastSubStepNumber : PDWord) : DWord; stdcall;
    // M3 전용 원점 검색시 센서존에서 탈출시 보정되는 위치 값을 반환하는 함수이다.
    function AxmHomeGetM3OffsetAvoideSenArea (lAxisNo : LongInt; dPos : PDouble) : DWord; stdcall;
    // M3 전용 원점 검색시 센서존에서 탈출시 보정되는 위치 값을 설정하는 함수이다.
    // dPos 설정 값이 0이면 자동으로 탈출시 보정되는 위치 값은 자동으로 설정된다.
    // dPos 설정 값은 양수의 값만 입력한다.
    function AxmHomeSetM3OffsetAvoideSenArea (lAxisNo : LongInt; dPos : Double) : DWord; stdcall;

    // M3 전용, 절대치 엔코더 사용 기준, 원점검색 완료 후 CMD/ACT POS 초기화 여부 설정
    // dwSel: 0, 원점 검색후 CMD/ACTPOS 0으로 설정됨.[초기값]
    // dwSel: 1, 원점 검색후 CMD/ACTPOS 값이 설정되지 않음.
    function AxmM3SetAbsEncOrgResetDisable (lAxisNo : LongInt; dwSel : DWord) : DWord; stdcall;

    // M3 전용, 절대치 엔코더 사용 기준, 원점검색 완료 후 CMD/ACT POS 초기화 여부 설정값 가져오기
    // upSel: 0, 원점 검색후 CMD/ACTPOS 0으로 설정됨.[초기값]
    // upSel: 1, 원점 검색후 CMD/ACTPOS 값이 설정되지 않음.
    function AxmM3GetAbsEncOrgResetDisable (lAxisNo : LongInt; upSel : PDWord) : DWord; stdcall;

    // M3 전용, 슬레이브 OFFLINE 전환시 알람 유지 기능 사용 유무 설정
    // dwSel: 0, ML3 슬레이브 ONLINE->OFFLINE 알람 처리 사용하지 않음.[초기값]
    // dwSel: 1, ML3 슬레이브 ONLINE->OFFLINE 알람 처리 사용

    function AxmM3SetOfflineAlarmEnable (lAxisNo : LongInt; dwSel : DWord) : DWord; stdcall;
    // M3 전용, 슬레이브 OFFLINE 전환시 알람 유지 기능 사용 유무 설정 값 가져오기
    // upSel: 0, ML3 슬레이브 ONLINE->OFFLINE 알람 처리 사용하지 않음.[초기값]
    // upSel: 1, ML3 슬레이브 ONLINE->OFFLINE 알람 처리 사용

    function AxmM3GetOfflineAlarmEnable (lAxisNo : LongInt; upSel : PDWord) : DWord; stdcall;

    // M3 전용, 슬레이브 OFFLINE 전환 여부 상태 값 가져오기
    // upSel: 0, ML3 슬레이브 ONLINE->OFFLINE 전환되지 않음
    // upSel: 1, ML3 슬레이브 ONLINE->OFFLINE 전환되었음.
    function AxmM3ReadOnlineToOfflineStatus (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // Network 제품의 Configuration Lock 상태를 설정한다.
    // wLockMode  : DISABLE(0), ENABLE(1)
    function AxlSetLockMode (lBoardNo : LongInt; wLockMode : Word) : DWord; stdcall;

    // Lock 정보를 설정
    function AxlSetLockData (lBoardNo : LongInt; dwTotalNodeNum : DWord; dwpNodeNo : PDWord; dwpNodeID : PDWord; dwpLockData : PDWord) : DWord; stdcall;

    function AxmMoveStartPosWithAVC (lAxisNo : LongInt; dPosition : Double; dMaxVelocity : Double; dMaxAccel : Double; dMinJerk : Double; dpMoveVelocity : PDouble; dpMoveAccel : PDouble; dpMoveJerk : PDouble) : DWord; stdcall;
    // 카운터 모듈의 2-D 절대위치 트리거 기능을 위해 필요한 트리거 위치 정보를 설정한다.
    // lChannelNo : 0,1 channel 일 경우 0, 2,3 channel 의 경우 2 를 설정.
    // nDataCnt :
    //  nDataCnt > 0 : 데이터 등록, nDataCnt <= 0 : 등록된 데이터 초기화.
    // dwOption : Reserved.
    // dpPatternData : (X1, Y1)
    function AxcTriggerSetPatternData (lChannelNo : LongInt; nDataCnt : LongInt; dwOption : DWord; dpPatternData : PDouble) : DWord; stdcall;
    // 카운터 모듈의 2-D 절대위치 트리거 기능을 위해 필요한 트리거 위치 정보를 확인한다.
    function AxcTriggerGetPatternData (lChannelNo : LongInt; npDataCnt : PLongInt; dwpOption : PDWord; dpPatternData : PDouble) : DWord; stdcall;

    //연속 보간 관련하여 AxmContiEndNode 함수내에서 보간구동관련 Node 를 Data Queue 에 미리 채워넣을 수 있도록하는 기능을 활성화 한다.
    //bPushPrevContiQueue : 1 // 해당 기능 활성화
    //bPushPrevContiQueue : 0 // 해당 기능 비활성화
    function AxmContiSetPushPrevContiQueueEnable (lCoordinate : LongInt; bPushPrevContiQueue : Boolean) : DWord; stdcall;
    //설정해둔 AxmContiSetPushPrevContiQueueEnable Flag값을 반환한다.
    function AxmContiGetPushPrevContiQueueEnable (lCoordinate : LongInt; bPushPrevContiQueue : BOOL*) : DWord; stdcall;

    // 연속보간 구동 시 Data Queue 에 Node 정보가 적재되었는지 상태를 반환한다.
    // AxmContiSetPushPrevContiQueueEnable(long lCoordinate, 1) 로 설정되어있을 경우만 유효
    // bPushPrevContiQueueComplete : 1 // Node Data 적재 완료
    // bPushPrevContiQueueComplete : 0 // Node Data 적재 되어있지않음
    function AxmContiGetPushPrevContiQueueComplete (lCoordinate : LongInt; bPushPrevContiQueueComplete : BOOL*) : DWord; stdcall;

    // 연속보간 구동 시 첫 노드 시작 및 마지막 노드 시작 시 일정시간 이후 지정된 좌표계의 마스터 축의 OutputBit On/Off 제어
    // AxmContiBeginNode 앞에 호출해야 한다. 한번 구동하면 Flag가 초기화되어 다시 호출해야 사용할 수 있다.
    // StartTime/EndTime 단위는 [Sec]이며, 0 ~ 6.5초까지 설정 가능하다.
    // uOnoff : 0 - 시작 위치에서 Bit On 종료 위치에서 Bit Off
    //          : 1 - 시작 위치에서 Bit Off 종료 위치에서 Bit On
    // lEndMode : 0 - 마지막 노드 구동 종료 후 즉시 OutputBit Off/On
    //   : 1 - 마지막 노드 구동 시작 후 입력한 EndTime 이후 OutputBit Off/On
    //   : 2 - 구동 시작 시 OutputBit On/Off 및 입력한 EndTime 이후 OutputBit Off/On
    function AxmContiSetWriteOutputBit (lCoordinate : LongInt; dStartTime : Double; dEndTime : Double; lBitNo : LongInt; uOnoff : LongInt; lEndMode : LongInt) : DWord; stdcall;

    // AxmContiSetWriteOutputBit로 설정한 값들을 반환한다.
    function AxmContiGetWriteOutputBit (lCoordinate : LongInt; dpStartTime : PDouble; dpEndTime : PDouble; lpBitNo : PLongInt; lpOnoff : PLongInt; lpEndMode : PLongInt) : DWord; stdcall;

    // AxmContiSetWriteOutputBit로 설정한 값들을 리셋한다.
    function AxmContiResetWriteOutputBit (lCoordinate : LongInt) : DWord; stdcall;

    // AxmMoveTorqueStop 함수로 토크 구동 정지 시 CmdPos 값을 ActPos 값과 일치시키는 시점까지의 대기 시간을 설정한다.
    // dwSettlingTime
    //  1) 단위: [msec]
    //  2) 입력 가능 범위: 0 ~ 10000
    //  *참고* AxmMoveTorqueSetStopSettlingTime 함수로 대기 시간을 설정하지 않으면, dafault 값인 10[msec]가 적용된다.
    function AxmMoveTorqueSetStopSettlingTime (lAxisNo : LongInt; dwSettlingTime : DWord) : DWord; stdcall;
    // AxmMoveTorqueStop 함수로 토크 구동 정지 시 CmdPos 값을 ActPos 값과 일치시키는 시점까지의 대기 시간을 반환한다.
    function AxmMoveTorqueGetStopSettlingTime (lAxisNo : LongInt; dwpSettlingTime : PDWord) : DWord; stdcall;

    //////////////////////////////////////////////////////////////////////////
    // Monitor
    // 데이터를 수집을 진행할 항목을 추가합니다.
    function AxlMonitorSetItem (lBoardNo : LongInt; lItemIndex : LongInt; dwSignalType : DWord; lSignalNo : LongInt; lSubSignalNo : LongInt) : DWord; stdcall;

    // 데이터 수집을 진행할 항목들에 관한 정보를 가져옵니다.
    function AxlMonitorGetIndexInfo (lBoardNo : LongInt; lpItemSize : PLongInt; lpItemIndex : PLongInt) : DWord; stdcall;

    // 데이터 수집을 진행할 각 항목의 세부 설정을 가져옵니다.
    function AxlMonitorGetItemInfo (lBoardNo : LongInt; lItemIndex : LongInt; dwpSignalType : PDWord; lpSignalNo : PLongInt; lpSubSignalNo : PLongInt) : DWord; stdcall;

    // 모든 데이터 수집 항목의 설정을 초기화합니다.
    function AxlMonitorResetAllItem (lBoardNo : LongInt) : DWord; stdcall;

    // 선택된 데이터 수집 항목의 설정을 초기화합니다.
    function AxlMonitorResetItem (lBoardNo : LongInt; lItemIndex : LongInt) : DWord; stdcall;

    // 데이터 수집의 트리거 조건을 설정합니다.
    function AxlMonitorSetTriggerOption (lBoardNo : LongInt; dwSignalType : DWord; lSignalNo : LongInt; lSubSignalNo : LongInt; dwOperatorType : DWord; dValue1 : Double; dValue2 : Double) : DWord; stdcall;

    // 데이터 수집의 트리거 조건을 가져옵니다.
    //DWORD  __stdcall AxlMonitorGetTriggerOption(DWORD* dwpSignalType, long* lpSignalNo, long* lpSubSignalNo, DWORD* dwpOperatorType, double* dpValue1, double* dpValue2);

    // 데이터 수집의 트리거 조건을 초기화합니다.
    function AxlMonitorResetTriggerOption (lBoardNo : LongInt) : DWord; stdcall;

    // 데이터 수집을 시작합니다.
    function AxlMonitorStart (lBoardNo : LongInt; dwStartOption : DWord; dwOverflowOption : DWord) : DWord; stdcall;

    // 데이터 수집을 정지합니다.
    function AxlMonitorStop (lBoardNo : LongInt) : DWord; stdcall;

    // 수집된 데이터를 가져옵니다.
    function AxlMonitorReadData (lBoardNo : LongInt; lpItemSize : PLongInt; lpDataCount : PLongInt; dpReadData : PDouble) : DWord; stdcall;

    // 데이터 수집의 주기를 가져옵니다.
    function AxlMonitorReadPeriod (lBoardNo : LongInt; dwpPeriod : PDWord) : DWord; stdcall;
    //////////////////////////////////////////////////////////////////////////


    //////////////////////////////////////////////////////////////////////////
    // MonitorEx
    // 데이터를 수집을 진행할 항목을 추가합니다.
    function AxlMonitorExSetItem (lItemIndex : LongInt; dwSignalType : DWord; lSignalNo : LongInt; lSubSignalNo : LongInt) : DWord; stdcall;

    // 데이터 수집을 진행할 항목들에 관한 정보를 가져옵니다.
    function AxlMonitorExGetIndexInfo (lpItemSize : PLongInt; lpItemIndex : PLongInt) : DWord; stdcall;

    // 데이터 수집을 진행할 각 항목의 세부 설정을 가져옵니다.
    function AxlMonitorExGetItemInfo (lItemIndex : LongInt; dwpSignalType : PDWord; lpSignalNo : PLongInt; lpSubSignalNo : PLongInt) : DWord; stdcall;

    // 모든 데이터 수집 항목의 설정을 초기화합니다.
    function AxlMonitorExResetAllItem () : DWord; stdcall;

    // 선택된 데이터 수집 항목의 설정을 초기화합니다.
    function AxlMonitorExResetItem (lItemIndex : LongInt) : DWord; stdcall;

    // 데이터 수집의 트리거 조건을 설정합니다.
    function AxlMonitorExSetTriggerOption (dwSignalType : DWord; lSignalNo : LongInt; lSubSignalNo : LongInt; dwOperatorType : DWord; dValue1 : Double; dValue2 : Double) : DWord; stdcall;

    // 데이터 수집의 트리거 조건을 가져옵니다.
    //DWORD  __stdcall AxlMonitorExGetTriggerOption(DWORD* dwpSignalType, long* lpSignalNo, long* lpSubSignalNo, DWORD* dwpOperatorType, double* dpValue1, double* dpValue2);

    // 데이터 수집의 트리거 조건을 초기화합니다.
    function AxlMonitorExResetTriggerOption () : DWord; stdcall;

    // 데이터 수집을 시작합니다.
    function AxlMonitorExStart (dwStartOption : DWord; dwOverflowOption : DWord) : DWord; stdcall;

    // 데이터 수집을 정지합니다.
    function AxlMonitorExStop () : DWord; stdcall;

    // 수집된 데이터를 가져옵니다.
    function AxlMonitorExReadData (lpItemSize : PLongInt; lpDataCount : PLongInt; dpReadData : PDouble) : DWord; stdcall;

    // 데이터 수집의 주기를 가져옵니다.
    function AxlMonitorExReadPeriod (dwpPeriod : PDWord) : DWord; stdcall;
    //////////////////////////////////////////////////////////////////////////

    // X2, Y2 축에 대한 Offset 위치 정보를 포함한 2축 직선 보간 #01.
    function AxmLineMoveDual01 (lCoordNo : LongInt; dpEndPosition : PDouble; dVelocity : Double; dAccel : Double; dDecel : Double; dOffsetLength : Double; dTotalLength : Double; dpStartOffsetPosition : PDouble; dpEndOffsetPosition : PDouble) : DWord; stdcall;
    // X2, Y2 축에 대한 Offset 위치 정보를 포함한 2축 원호 보간 #01.
    function AxmCircleCenterMoveDual01 (lCoordNo : LongInt; lpAxes : PLongInt; dpCenterPosition : PDouble; dpEndPosition : PDouble; dVelocity : Double; dAccel : Double; dDecel : Double; dwCWDir : DWord; dOffsetLength : Double; dTotalLength : Double; dpStartOffsetPosition : PDouble; dpEndOffsetPosition : PDouble) : DWord; stdcall;

    // 해당보드의 connect mode 를 반환한다.
    // dpMode : 1 Auto Connect Mode
    // dpMode : 0 Manual Connect Mode
    function AxlGetBoardConnectMode (lBoardNo : LongInt; dwpMode : PDWord) : DWord; stdcall;
    // 해당보드의 connect mode 를 설정한다.
    // dMode : 1 Auto Connect Mode
    // dMode : 0 Manual Connect Mode
    function AxlSetBoardConnectMode (lBoardNo : LongInt; dwMode : DWord) : DWord; stdcall;

    //지정된 축의 Command Queue 를 초기화 한다.
    function AxmStatusSetCmdQueueClear (lAxisNo : LongInt) : DWord; stdcall;

    // 지정된 축의 통신 프로토콜관련 Data 를 확인한다.
    function AxmStatusGetControlBits (lAxisNo : LongInt; dwpTxData : PDWord; dwpRxData : PDWord) : DWord; stdcall;

    // 사용 중인 AXL이 있는지 확인(Shared Memory가 존재하는지 확인)
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
