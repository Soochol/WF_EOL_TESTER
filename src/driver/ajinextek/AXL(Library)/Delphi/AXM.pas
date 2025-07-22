//****************************************************************************
///****************************************************************************
//*****************************************************************************
//**
//** File Name
//** ---------
//**
//** AXM.PAS
//**
//** COPYRIGHT (c) AJINEXTEK Co., LTD
//**
//*****************************************************************************
//*****************************************************************************
//**
//** Description
//** -----------
//** Ajinextek Motion Library Header File
//** 
//**
//*****************************************************************************
//*****************************************************************************
//**
//** Source Change Indices
//** ----------------------
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

unit AXM;

interface

uses Windows, Messages, AXHS;


    //========== 보드 및 모듈 확인함수(Info) - Information ===============================================================
    // 해당 축의 보드번호, 모듈 위치, 모듈 아이디를 반환한다.
    function AxmInfoGetAxis (lAxisNo : LongInt; lpBoardNo : PLongInt; lpModulePos : PLongInt; upModuleID : PDWord) : DWord; stdcall;
    // 모션 모듈이 존재하는지 반환한다.
    function AxmInfoIsMotionModule (upStatus : PDWord) : DWord; stdcall;
    // 해당 축이 유효한지 반환한다.
    function AxmInfoIsInvalidAxisNo (lAxisNo : LongInt) : DWord; stdcall;
    // 해당 축이 제어가 가능한 상태인지 반환한다.
    function AxmInfoGetAxisStatus (lAxisNo : LongInt) : DWord; stdcall;
    // 시스템내 유효한 모션 축수를 반환한다.
    function AxmInfoGetAxisCount (lpAxisCount : PLongInt) : DWord; stdcall;
    // 해당 보드/모듈의 첫번째 축번호를 반환한다.
    function AxmInfoGetFirstAxisNo (lBoardNo : LongInt; lModulePos : LongInt; lpAxisNo : PLongInt) : DWord; stdcall;
    // 해당 보드의 첫번째 축번호를 반환한다.
    function AxmInfoGetBoardFirstAxisNo (lBoardNo : LongInt; lModulePos : LongInt; lpAxisNo : PLongInt) : DWord; stdcall;

    //========= 가상 축 함수 ============================================================================================
    // 초기 상태에서 AXM 모든 함수의 축번호 설정은 0 ~ (실제 시스템에 장착된 축수 - 1) 범위에서 유효하지만
    // 이 함수를 사용하여 실제 장착된 축번호 대신 임의의 축번호로 바꿀 수 있다.
    // 이 함수는 제어 시스템의 H/W 변경사항 발생시 기존 프로그램에 할당된 축번호를 그대로 유지하고 실제 제어 축의
    // 물리적인 위치를 변경하여 사용을 위해 만들어진 함수이다.
    // 주의사항 : 여러 개의 실제 축번호에 대하여 같은 번호로 가상 축을 중복해서 맵핑하지 말아야 한다.
    //            중복 맵핑된 경우 실제 축번호가 낮은 축만 가상 축번호로 제어 할 수 있으며,
    //            나머지 같은 가상축 번호로 맵핑된 축은 제어가 불가능하다.

    // 가상축을 설정한다.
    function AxmVirtualSetAxisNoMap (lRealAxisNo : LongInt; lVirtualAxisNo : LongInt) : DWord; stdcall;
    // 설정한 가상축 번호를 반환한다.
    function AxmVirtualGetAxisNoMap (lRealAxisNo : LongInt; lpVirtualAxisNo : PLongInt) : DWord; stdcall;
    // 멀티 가상축을 설정한다.
    function AxmVirtualSetMultiAxisNoMap (lSize : LongInt; lpRealAxesNo : PLongInt; lpVirtualAxesNo : PLongInt) : DWord; stdcall;
    // 설정한 멀티 가상축 번호를 반환한다.
    function AxmVirtualGetMultiAxisNoMap (lSize : LongInt; lpRealAxesNo : PLongInt; lpVirtualAxesNo : PLongInt) : DWord; stdcall;
    // 가상축 설정을 해지한다.
    function AxmVirtualResetAxisMap () : DWord; stdcall;

    //========= 인터럽트 관련 함수 ======================================================================================
    // 콜백 함수 방식은 이벤트 발생 시점에 즉시 콜백 함수가 호출 됨으로 가장 빠르게 이벤트를 통지받을 수 있는 장점이 있으나
    // 콜백 함수가 완전히 종료 될 때까지 메인 프로세스가 정체되어 있게 된다.
    // 즉, 콜백 함수 내에 부하가 걸리는 작업이 있을 경우에는 사용에 주의를 요한다.
    // 이벤트 방식은 쓰레드등을 이용하여 인터럽트 발생여부를 지속적으로 감시하고 있다가 인터럽트가 발생하면
    // 처리해주는 방법으로, 쓰레드 등으로 인해 시스템 자원을 점유하고 있는 단점이 있지만
    // 가장 빠르게 인터럽트를 검출하고 처리해줄 수 있는 장점이 있다.
    // 일반적으로는 많이 쓰이지 않지만, 인터럽트의 빠른처리가 주요 관심사인 경우에 사용된다.
    // 이벤트 방식은 이벤트의 발생 여부를 감시하는 특정 쓰레드를 사용하여 메인 프로세스와 별개로 동작되므로
    // MultiProcessor 시스템등에서 자원을 가장 효율적으로 사용할 수 있게 되어 특히 권장하는 방식이다.
    // 인터럽트 메시지를 받아오기 위하여 윈도우 메시지 또는 콜백 함수를 사용한다.
    // (메시지 핸들, 메시지 ID, 콜백함수, 인터럽트 이벤트)
    //    hWnd    : 윈도우 핸들, 윈도우 메세지를 받을때 사용. 사용하지 않으면 NULL을 입력.
    //    wMsg    : 윈도우 핸들의 메세지, 사용하지 않거나 디폴트값을 사용하려면 0을 입력.
    //    proc    : 인터럽트 발생시 호출될 함수의 포인터, 사용하지 않으면 NULL을 입력.
    //    pEvent  : 이벤트 방법사용시 이벤트 핸들
    // Ex)
    // AxmInterruptSetAxis(0, Null, 0, AxtInterruptProc, NULL);
    // void __stdcall AxtInterruptProc(long lAxisNo, DWORD dwFlag){
    //     ... ;
    // }
    function AxmInterruptSetAxis (lAxisNo : LongInt; hWnd : HWND; uMessage : DWord; pProc : AXT_INTERRUPT_PROC; pEvent : PDWord) : DWord; stdcall;

    // 설정 축의 인터럽트 사용 여부를 설정한다
    // 해당 축에 인터럽트 설정 / 확인
    // uUse : 사용 유무 => DISABLE(0), ENABLE(1)
    function AxmInterruptSetAxisEnable (lAxisNo : LongInt; uUse : DWord) : DWord; stdcall;
    // 설정 축의 인터럽트 사용 여부를 반환한다
    function AxmInterruptGetAxisEnable (lAxisNo : LongInt; upUse : PDWord) : DWord; stdcall;

    //인터럽트를 이벤트 방식으로 사용할 경우 해당 인터럽트 정보 읽는다.
    function AxmInterruptRead (lpAxisNo : PLongInt; upFlag : PDWord) : DWord; stdcall;
    // 해당 축의 인터럽트 플래그 값을 반환한다.
    function AxmInterruptReadAxisFlag (lAxisNo : LongInt; lBank : LongInt; upFlag : PDWord) : DWord; stdcall;

    // 지정 축의 사용자가 설정한 인터럽트 발생 여부를 설정한다.
    // lBank         : 인터럽트 뱅크 번호 (0 - 1) 설정가능.
    // uInterruptNum : 인터럽트 번호 설정 비트번호로 설정 hex값 혹은 define된값을 설정
    // AXHS.h에서 IP, QI INTERRUPT_BANK1, 2 DEF를 확인한다.
    function AxmInterruptSetUserEnable (lAxisNo : LongInt; lBank : LongInt; uInterruptNum : DWord) : DWord; stdcall;
    // 지정 축의 사용자가 설정한 인터럽트 발생 여부를 확인한다.
    function AxmInterruptGetUserEnable (lAxisNo : LongInt; lBank : LongInt; upInterruptNum : PDWord) : DWord; stdcall;
    // 카운터 비교기 이벤트를 사용하기 위해 비교기에 값을 설정한다.
    // lComparatorNo : 0(CNTC1 : Command)
    //     1(CNTC2 : Actual)
    //     2 ~ 4(CNTC3 ~ CNTC5)
    // dPosition : 비교기 위치 값
    function AxmInterruptSetCNTComparator (lAxisNo : LongInt; lComparatorNo : LongInt; dPosition : Double) : DWord; stdcall;
    // 카운터 비교기에 설정된 위치값을 확인한다.
    // lComparatorNo : 0(CNTC1 : Command)
    //     1(CNTC2 : Actual)
    //     2 ~ 4(CNTC3 ~ CNTC5)
    // dpPosition : 비교기 위치 값
    function AxmInterruptGetCNTComparator (lAxisNo : LongInt; lComparatorNo : LongInt; dpPosition : PDouble) : DWord; stdcall;

    //======== 모션 파라메타 설정 =======================================================================================
    // AxmMotLoadParaAll로 파일을 Load 시키지 않으면 초기 파라메타 설정시 기본 파라메타 설정.
    // 현재 PC에 사용되는 모든축에 똑같이 적용된다. 기본파라메타는 아래와 같다.
    // 00:AXIS_NO.             =0          01:PULSE_OUT_METHOD.    =4         02:ENC_INPUT_METHOD.    =3     03:INPOSITION.          =2
    // 04:ALARM.               =1          05:NEG_END_LIMIT.       =1         06:POS_END_LIMIT.       =1     07:MIN_VELOCITY.        =1
    // 08:MAX_VELOCITY.        =700000     09:HOME_SIGNAL.         =4         10:HOME_LEVEL.          =1     11:HOME_DIR.            =0
    // 12:ZPHASE_LEVEL.        =1          13:ZPHASE_USE.          =0         14:STOP_SIGNAL_MODE.    =0     15:STOP_SIGNAL_LEVEL.   =1
    // 16:HOME_FIRST_VELOCITY. =100        17:HOME_SECOND_VELOCITY.=100       18:HOME_THIRD_VELOCITY. =20    19:HOME_LAST_VELOCITY.  =1
    // 20:HOME_FIRST_ACCEL.    =400        21:HOME_SECOND_ACCEL.   =400       22:HOME_END_CLEAR_TIME. =1000  23:HOME_END_OFFSET.     =0
    // 24:NEG_SOFT_LIMIT.      =-134217728 25:POS_SOFT_LIMIT.      =134217727 26:MOVE_PULSE.          =1     27:MOVE_UNIT.           =1
    // 28:INIT_POSITION.       =1000       29:INIT_VELOCITY.       =200       30:INIT_ACCEL.          =400   31:INIT_DECEL.          =400
    // 32:INIT_ABSRELMODE.     =0          33:INIT_PROFILEMODE.    =4         34:SVON_LEVEL.          =1     35:ALARM_RESET_LEVEL.   =1
    // 36:ENCODER_TYPE.        =1          37:SOFT_LIMIT_SEL.      =0         38:SOFT_LIMIT_STOP_MODE.=0     39:SOFT_LIMIT_ENABLE.   =0

    // 00=[AXIS_NO             ]: 축 (0축 부터 시작함)
    // 01=[PULSE_OUT_METHOD    ]: Pulse out method TwocwccwHigh = 6
    // 02=[ENC_INPUT_METHOD    ]: disable = 0, 1체배 = 1, 2체배 = 2, 4체배 = 3, 결선 관련방향 교체시(-).1체배 = 11  2체배 = 12  4체배 = 13
    // 03=[INPOSITION          ], 04=[ALARM     ], 05,06 =[END_LIMIT   ]  : 0 = B접점, 1= A접점, 2 = 사용안함, 3 = 기존상태 유지
    // 07=[MIN_VELOCITY        ]: 시작 속도(START VELOCITY)
    // 08=[MAX_VELOCITY        ]: 드라이버가 지령을 받아들일수 있는 지령 속도. 보통 일반 Servo는 700k
    // Ex> screw : 20mm pitch drive: 10000 pulse 모터: 400w
    // 09=[HOME_SIGNAL         ]: 4 - Home in0 , 0 :PosEndLimit , 1 : NegEndLimit // _HOME_SIGNAL참조.
    // 10=[HOME_LEVEL          ]: 0 = B접점, 1 = A접점, 2 = 사용안함, 3 = 기존상태 유지
    // 11=[HOME_DIR            ]: 홈 방향(HOME DIRECTION) 1:+방향, 0:-방향
    // 12=[ZPHASE_LEVEL        ]: 0 = B접점, 1 = B접점, 2 = 사용안함, 3 = 기존상태 유지
    // 13=[ZPHASE_USE          ]: Z상사용여부. 0: 사용안함 , 1: +방향, 2: -방향
    // 14=[STOP_SIGNAL_MODE    ]: ESTOP, SSTOP 사용시 모드 0:감속정지, 1:급정지
    // 15=[STOP_SIGNAL_LEVEL   ]: ESTOP, SSTOP 사용 레벨.  0 = B접점, 1 = A접점, 2 = 사용안함, 3 = 기존상태 유지
    // 16=[HOME_FIRST_VELOCITY ]: 1차구동속도
    // 17=[HOME_SECOND_VELOCITY]: 검출후속도
    // 18=[HOME_THIRD_VELOCITY ]: 마지막 속도
    // 19=[HOME_LAST_VELOCITY  ]: index검색및 정밀하게 검색하기위한 속도.
    // 20=[HOME_FIRST_ACCEL    ]: 1차 가속도 , 21=[HOME_SECOND_ACCEL   ] : 2차 가속도
    // 22=[HOME_END_CLEAR_TIME ]: 원점 검색 Enc 값 Set하기 위한 대기시간,  23=[HOME_END_OFFSET] : 원점검출후 Offset만큼 이동.
    // 24=[NEG_SOFT_LIMIT      ]: - SoftWare Limit 같게 설정하면 사용안함, 25=[POS_SOFT_LIMIT ]: + SoftWare Limit 같게 설정하면 사용안함.
    // 26=[MOVE_PULSE          ]: 드라이버의 1회전당 펄스량              , 27=[MOVE_UNIT  ]: 드라이버 1회전당 이동량 즉:스크류 Pitch
    // 28=[INIT_POSITION       ]: 에이젼트 사용시 초기위치  , 사용자가 임의로 사용가능
    // 29=[INIT_VELOCITY       ]: 에이젼트 사용시 초기속도  , 사용자가 임의로 사용가능
    // 30=[INIT_ACCEL          ]: 에이젼트 사용시 초기가속도, 사용자가 임의로 사용가능
    // 31=[INIT_DECEL          ]: 에이젼트 사용시 초기감속도, 사용자가 임의로 사용가능
    // 32=[INIT_ABSRELMODE     ]: 절대(0)/상대(1) 위치 설정
    // 33=[INIT_PROFILEMODE    ]: 프로파일모드(0 - 4) 까지 설정
    //                            '0': 대칭 Trapezode, '1': 비대칭 Trapezode, '2': 대칭 Quasi-S Curve, '3':대칭 S Curve, '4':비대칭 S Curve
    // 34=[SVON_LEVEL          ]: 0 = B접점, 1 = A접점
    // 35=[ALARM_RESET_LEVEL   ]: 0 = B접점, 1 = A접점
    // 36=[ENCODER_TYPE        ]: 0 = TYPE_INCREMENTAL, 1 = TYPE_ABSOLUTE
    // 37=[SOFT_LIMIT_SEL      ]: 0 = COMMAND, 1 = ACTUAL
    // 38=[SOFT_LIMIT_STOP_MODE]: 0 = EMERGENCY_STOP, 1 = SLOWDOWN_STOP
    // 39=[SOFT_LIMIT_ENABLE   ]: 0 = DISABLE, 1 = ENABLE

    // AxmMotSaveParaAll로 저장 되어진 .mot파일을 불러온다. 해당 파일은 사용자가 Edit 하여 사용 가능하다.
    function AxmMotLoadParaAll (szFilePath : char*) : DWord; stdcall;
    // 모든축에 대한 모든 파라메타를 축별로 저장한다. .mot파일로 저장한다.
    function AxmMotSaveParaAll (szFilePath : char*) : DWord; stdcall;

    // 파라메타 28 - 31번까지 사용자가 프로그램내에서  이 함수를 이용해 설정 한다
    function AxmMotSetParaLoad (lAxisNo : LongInt; dInitPos : Double; dInitVel : Double; dInitAccel : Double; dInitDecel : Double) : DWord; stdcall;
    // 파라메타 28 - 31번까지 사용자가 프로그램내에서  이 함수를 이용해 확인 한다.
    function AxmMotGetParaLoad (lAxisNo : LongInt; dpInitPos : PDouble; dpInitVel : PDouble; dpInitAccel : PDouble; dpInitDecel : PDouble) : DWord; stdcall;

    // 지정 축의 펄스 출력 방식을 설정한다.
    //uMethod  0 :OneHighLowHigh, 1 :OneHighHighLow, 2 :OneLowLowHigh, 3 :OneLowHighLow, 4 :TwoCcwCwHigh
    //         5 :TwoCcwCwLow,    6 :TwoCwCcwHigh,   7 :TwoCwCcwLow,   8 :TwoPhase,      9 :TwoPhaseReverse
    //    OneHighLowHigh      = 0x0,           // 1펄스 방식, PULSE(Active High), 정방향(DIR=Low)  / 역방향(DIR=High)
    //    OneHighHighLow      = 0x1,           // 1펄스 방식, PULSE(Active High), 정방향(DIR=High) / 역방향(DIR=Low)
    //    OneLowLowHigh       = 0x2,           // 1펄스 방식, PULSE(Active Low),  정방향(DIR=Low)  / 역방향(DIR=High)
    //    OneLowHighLow       = 0x3,           // 1펄스 방식, PULSE(Active Low),  정방향(DIR=High) / 역방향(DIR=Low)
    //    TwoCcwCwHigh        = 0x4,           // 2펄스 방식, PULSE(CCW:역방향),  DIR(CW:정방향),  Active High
    //    TwoCcwCwLow         = 0x5,           // 2펄스 방식, PULSE(CCW:역방향),  DIR(CW:정방향),  Active Low
    //    TwoCwCcwHigh        = 0x6,           // 2펄스 방식, PULSE(CW:정방향),   DIR(CCW:역방향), Active High
    //    TwoCwCcwLow         = 0x7,           // 2펄스 방식, PULSE(CW:정방향),   DIR(CCW:역방향), Active Low
    //    TwoPhase            = 0x8,           // 2상(90' 위상차),  PULSE lead DIR(CW: 정방향), PULSE lag DIR(CCW:역방향)
    //    TwoPhaseReverse     = 0x9            // 2상(90' 위상차),  PULSE lead DIR(CCW: 정방향), PULSE lag DIR(CW:역방향)
    function AxmMotSetPulseOutMethod (lAxisNo : LongInt; uMethod : DWord) : DWord; stdcall;
    // 지정 축의 펄스 출력 방식 설정을 반환한다,
    function AxmMotGetPulseOutMethod (lAxisNo : LongInt; upMethod : PDWord) : DWord; stdcall;

    // 지정 축의 외부(Actual) 카운트의 증가 방향 설정을 포함하여 지정 축의 Encoder 입력 방식을 설정한다.
    // uMethod : 0 - 7 설정.
    // ObverseUpDownMode    = 0x0,            // 정방향 Up/Down
    // ObverseSqr1Mode      = 0x1,            // 정방향 1체배
    // ObverseSqr2Mode      = 0x2,            // 정방향 2체배
    // ObverseSqr4Mode      = 0x3,            // 정방향 4체배
    // ReverseUpDownMode    = 0x4,            // 역방향 Up/Down
    // ReverseSqr1Mode      = 0x5,            // 역방향 1체배
    // ReverseSqr2Mode      = 0x6,            // 역방향 2체배
    // ReverseSqr4Mode      = 0x7             // 역방향 4체배
    function AxmMotSetEncInputMethod (lAxisNo : LongInt; uMethod : DWord) : DWord; stdcall;
    // 지정 축의 외부(Actual) 카운트의 증가 방향 설정을 포함하여 지정 축의 Encoder 입력 방식을 반환한다.
    function AxmMotGetEncInputMethod (lAxisNo : LongInt; upMethod : PDWord) : DWord; stdcall;

    // 설정 속도 단위가 RPM(Revolution Per Minute)으로 맞추고 싶다면.
    // ex>    rpm 계산:
    // 4500 rpm ?
    // unit/ pulse = 1 : 1이면      pulse/ sec 초당 펄스수가 되는데
    // 4500 rpm에 맞추고 싶다면     4500 / 60 초 : 75회전/ 1초
    // 모터가 1회전에 몇 펄스인지 알아야 된다. 이것은 Encoder에 Z상을 검색해보면 알수있다.
    // 1회전:1800 펄스라면 75 x 1800 = 135000 펄스가 필요하게 된다.
    // AxmMotSetMoveUnitPerPulse에 Unit = 1, Pulse = 1800 넣어 동작시킨다.
    // 주의사항 : rpm으로 제어하게 된다면 속도와 가속도 도 rpm단위 값으로 생각하여야 한다.

    // 지정 축의 펄스 당 움직이는 거리를 설정한다.
    function AxmMotSetMoveUnitPerPulse (lAxisNo : LongInt; dUnit : Double; lPulse : LongInt) : DWord; stdcall;
    // 지정 축의 펄스 당 움직이는 거리를 반환한다.
    function AxmMotGetMoveUnitPerPulse (lAxisNo : LongInt; dpUnit : PDouble; lpPulse : PLongInt) : DWord; stdcall;

    // 지정 축에 감속 시작 포인트 검출 방식을 설정한다.
    // uMethod : 0 -1 설정
    // AutoDetect = 0x0 : 자동 가감속.
    // RestPulse  = 0x1 : 수동 가감속."
    function AxmMotSetDecelMode (lAxisNo : LongInt; uMethod : DWord) : DWord; stdcall;
    // 지정 축의 감속 시작 포인트 검출 방식을 반환한다
    function AxmMotGetDecelMode (lAxisNo : LongInt; upMethod : PDWord) : DWord; stdcall;

    // 지정 축에 수동 감속 모드에서 잔량 펄스를 설정한다.
    // 사용방법: 만약 AxmMotSetRemainPulse를 500 펄스를 설정
    //           AxmMoveStartPos를 위치 10000을 보냈을경우에 9500펄스부터
    //           남은 펄스 500은  AxmMotSetMinVel로 설정한 속도로 유지하면서 감속 된다.
    function AxmMotSetRemainPulse (lAxisNo : LongInt; uData : DWord) : DWord; stdcall;
    // 지정 축의 수동 감속 모드에서 잔량 펄스를 반환한다.
    function AxmMotGetRemainPulse (lAxisNo : LongInt; upData : PDWord) : DWord; stdcall;

    // 지정 축에 대한 모든 구동 함수의 최고 속도 제한 값 UNIT 기준으로 설정한다.
    // 주의사항 : 입력 최대 속도 값이 PPS가 아니라 UNIT 이다.
    // ex) 최대 출력 주파수(PCI-N804/404 : 10 MPPS)
    // ex) 최대 출력 Unit/Sec(PCI-N804/404 : 10MPPS * Unit/Pulse)
    function AxmMotSetMaxVel (lAxisNo : LongInt; dVel : Double) : DWord; stdcall;
    // 지정 축에 대한 모든 구동 함수의 최고 속도 제한 설정 값을 UNIT 기준으로 반환한다.
    function AxmMotGetMaxVel (lAxisNo : LongInt; dpVel : PDouble) : DWord; stdcall;

    // 지정 축의 이동 거리 계산 모드를 설정한다.
    //uAbsRelMode : POS_ABS_MODE '0' - 절대 좌표계
    //              POS_REL_MODE '1' - 상대 좌표계
    function AxmMotSetAbsRelMode (lAxisNo : LongInt; uAbsRelMode : DWord) : DWord; stdcall;
    // 지정 축의 설정된 이동 거리 계산 모드를 반환한다
    function AxmMotGetAbsRelMode (lAxisNo : LongInt; upAbsRelMode : PDWord) : DWord; stdcall;

    // 지정 축의 구동 속도 프로파일 모드를 설정한다.
    // ProfileMode : SYM_TRAPEZOIDE_MODE    '0' - 대칭 Trapezode
    //               ASYM_TRAPEZOIDE_MODE   '1' - 비대칭 Trapezode
    //               QUASI_S_CURVE_MODE     '2' - 대칭 Quasi-S Curve
    //               SYM_S_CURVE_MODE       '3' - 대칭 S Curve
    //               ASYM_S_CURVE_MODE      '4' - 비대칭 S Curve
    //               SYM_TRAP_M3_SW_MODE    '5' - 대칭 Trapezode : MLIII 내부 S/W Profile
    //               ASYM_TRAP_M3_SW_MODE   '6' - 비대칭 Trapezode : MLIII 내부 S/W Profile
    //               SYM_S_M3_SW_MODE       '7' - 대칭 S Curve : MLIII 내부 S/W Profile
    //               ASYM_S_M3_SW_MODE      '8' - asymmetric S Curve : MLIII 내부 S/W Profile
    function AxmMotSetProfileMode (lAxisNo : LongInt; uProfileMode : DWord) : DWord; stdcall;
    // 지정 축의 설정한 구동 속도 프로파일 모드를 반환한다.
    function AxmMotGetProfileMode (lAxisNo : LongInt; upProfileMode : PDWord) : DWord; stdcall;

    //지정 축의 가속도 단위를 설정한다.
    //AccelUnit : UNIT_SEC2   '0' - 가감속 단위를 unit/sec2 사용
    //            SEC         '1' - 가감속 단위를 sec 사용
    function AxmMotSetAccelUnit (lAxisNo : LongInt; uAccelUnit : DWord) : DWord; stdcall;
    // 지정 축의 설정된 가속도단위를 반환한다.
    function AxmMotGetAccelUnit (lAxisNo : LongInt; upAccelUnit : PDWord) : DWord; stdcall;

    // 주의사항: 최소속도를 UNIT/PULSE 보다 작게할 경우 최소단위가 UNIT/PULSE로 맞추어지기때문에 최소 속도가 UNIT/PULSE 가 된다.
    // 지정 축에 초기 속도를 설정한다.
    function AxmMotSetMinVel (lAxisNo : LongInt; dMinVel : Double) : DWord; stdcall;
    // 지정 축의 초기 속도를 반환한다.
    function AxmMotGetMinVel (lAxisNo : LongInt; dpMinVel : PDouble) : DWord; stdcall;

    // 지정 축의 가속 저크값을 설정한다.[%].
    function AxmMotSetAccelJerk (lAxisNo : LongInt; dAccelJerk : Double) : DWord; stdcall;
    // 지정 축의 설정된 가속 저크값을 반환한다.
    function AxmMotGetAccelJerk (lAxisNo : LongInt; dpAccelJerk : PDouble) : DWord; stdcall;

    // 지정 축의 감속 저크값을 설정한다.[%].
    function AxmMotSetDecelJerk (lAxisNo : LongInt; dDecelJerk : Double) : DWord; stdcall;
    // 지정 축의 설정된 감속 저크값을 반환한다.
    function AxmMotGetDecelJerk (lAxisNo : LongInt; dpDecelJerk : PDouble) : DWord; stdcall;

    // 지정 축의 속도 Profile결정시 우선순위(속도 Or 가속도)를 설정한다.
    // Priority : PRIORITY_VELOCITY   '0' - 속도 Profile결정시 지정한 속도값에 가깝도록 계산함(일반장비 및 Spinner에 사용).
    //            PRIORITY_ACCELTIME  '1' - 속도 Profile결정시 지정한 가감속시간에 가깝도록 계산함(고속 장비에 사용).
    // 5번째 Bit의 입력 값으로 삼각구동 시 프로파일 생성 방법을 선택할 수 있다.
    // [0]      : Old Profile(프로파일 패치 전)
    // [1]      : New Profile(프로파일 패치 후)
    function AxmMotSetProfilePriority (lAxisNo : LongInt; uPriority : DWord) : DWord; stdcall;
    // 지정 축의 속도 Profile결정시 우선순위(속도 Or 가속도)를 반환한다.
    function AxmMotGetProfilePriority (lAxisNo : LongInt; upPriority : PDWord) : DWord; stdcall;

    //=========== 입출력 신호 관련 설정함수 =============================================================================
    // 지정 축의 Z 상 Level을 설정한다.
    // uLevel : LOW(0), HIGH(1)
    function AxmSignalSetZphaseLevel (lAxisNo : LongInt; uLevel : DWord) : DWord; stdcall;
    // 지정 축의 Z 상 Level을 반환한다.
    function AxmSignalGetZphaseLevel (lAxisNo : LongInt; upLevel : PDWord) : DWord; stdcall;

    // 지정 축의 Servo-On신호의 출력 레벨을 설정한다.
    // uLevel : LOW(0), HIGH(1)
    function AxmSignalSetServoOnLevel (lAxisNo : LongInt; uLevel : DWord) : DWord; stdcall;
    // 지정 축의 Servo-On신호의 출력 레벨 설정을 반환한다.
    function AxmSignalGetServoOnLevel (lAxisNo : LongInt; upLevel : PDWord) : DWord; stdcall;

    // 지정 축의 Servo-Alarm Reset 신호의 출력 레벨을 설정한다.
    // uLevel : LOW(0), HIGH(1)
    function AxmSignalSetServoAlarmResetLevel (lAxisNo : LongInt; uLevel : DWord) : DWord; stdcall;
    // 지정 축의 Servo-Alarm Reset 신호의 출력 레벨을 설정을 반환한다.
    function AxmSignalGetServoAlarmResetLevel (lAxisNo : LongInt; upLevel : PDWord) : DWord; stdcall;

    // 지정 축의 Inpositon 신호 사용 여부 및 신호 입력 레벨을 설정한다
    // uLevel : LOW(0), HIGH(1), UNUSED(2), USED(3)
    function AxmSignalSetInpos (lAxisNo : LongInt; uUse : DWord) : DWord; stdcall;
    // 지정 축의 Inpositon 신호 사용 여부 및 신호 입력 레벨을 반환한다.
    function AxmSignalGetInpos (lAxisNo : LongInt; upUse : PDWord) : DWord; stdcall;
    // 지정 축의 Inpositon 신호 입력 상태를 반환한다.
    function AxmSignalReadInpos (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // 지정 축의 알람 신호 입력 시 비상 정지의 사용 여부 및 신호 입력 레벨을 설정한다.
    // uLevel : LOW(0), HIGH(1), UNUSED(2), USED(3)
    function AxmSignalSetServoAlarm (lAxisNo : LongInt; uUse : DWord) : DWord; stdcall;
    // 지정 축의 알람 신호 입력 시 비상 정지의 사용 여부 및 신호 입력 레벨을 반환한다.
    function AxmSignalGetServoAlarm (lAxisNo : LongInt; upUse : PDWord) : DWord; stdcall;
    // 지정 축의 알람 신호의 입력 레벨을 반환한다.
    function AxmSignalReadServoAlarm (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // 지정 축의 end limit sensor의 사용 유무 및 신호의 입력 레벨을 설정한다.
    // end limit sensor 신호 입력 시 감속정지 또는 급정지에 대한 설정도 가능하다.
    // uStopMode: EMERGENCY_STOP(0), SLOWDOWN_STOP(1)
    // uPositiveLevel, uNegativeLevel : LOW(0), HIGH(1), UNUSED(2), USED(3)
    function AxmSignalSetLimit (lAxisNo : LongInt; uStopMode : DWord; uPositiveLevel : DWord; uNegativeLevel : DWord) : DWord; stdcall;
    // 지정 축의 end limit sensor의 사용 유무 및 신호의 입력 레벨, 신호 입력 시 정지모드를 반환한다
    function AxmSignalGetLimit (lAxisNo : LongInt; upStopMode : PDWord; upPositiveLevel : PDWord; upNegativeLevel : PDWord) : DWord; stdcall;
    // 지정축의 end limit sensor의 입력 상태를 반환한다.
    function AxmSignalReadLimit (lAxisNo : LongInt; upPositiveStatus : PDWord; upNegativeStatus : PDWord) : DWord; stdcall;

    // 지정 축의 Software limit의 사용 유무, 사용할 카운트, 그리고 정지방법을 설정한다.
    // uUse       : DISABLE(0), ENABLE(1)
    // uStopMode  : EMERGENCY_STOP(0), SLOWDOWN_STOP(1)
    // uSelection : COMMAND(0), ACTUAL(1)
    // 주의사항: 원점검색시 위 함수를 이용하여 소프트웨어 리밋을 미리 설정해서 구동시 원점검색시 원점검색을 도중에 멈추어졌을경우에도  Enable된다.
    function AxmSignalSetSoftLimit (lAxisNo : LongInt; uUse : DWord; uStopMode : DWord; uSelection : DWord; dPositivePos : Double; dNegativePos : Double) : DWord; stdcall;
    // 지정 축의 Software limit의 사용 유무, 사용할 카운트, 그리고 정지 방법을 반환한다.
    function AxmSignalGetSoftLimit (lAxisNo : LongInt; upUse : PDWord; upStopMode : PDWord; upSelection : PDWord; dpPositivePos : PDouble; dpNegativePos : PDouble) : DWord; stdcall;
    // 지정 축의 Software limit의 현재 상태를 반환한다.
    function AxmSignalReadSoftLimit (lAxisNo : LongInt; upPositiveStatus : PDWord; upNegativeStatus : PDWord) : DWord; stdcall;

    // 비상 정지 신호의 정지 방법 (급정지/감속정지) 또는 사용 유무를 설정한다.
    // uStopMode  : EMERGENCY_STOP(0), SLOWDOWN_STOP(1)
    // uLevel : LOW(0), HIGH(1), UNUSED(2), USED(3)
    function AxmSignalSetStop (lAxisNo : LongInt; uStopMode : DWord; uLevel : DWord) : DWord; stdcall;
    // 비상 정지 신호의 정지 방법 (급정지/감속정지) 또는 사용 유무를 반환한다.
    function AxmSignalGetStop (lAxisNo : LongInt; upStopMode : PDWord; upLevel : PDWord) : DWord; stdcall;
    // 비상 정지 신호의 입력 상태를 반환한다.
    function AxmSignalReadStop (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // 지정 축의 Servo-On 신호를 출력한다.
    // uOnOff : FALSE(0), TRUE(1) ( 범용 0출력에 해당됨)
    function AxmSignalServoOn (lAxisNo : LongInt; uOnOff : DWord) : DWord; stdcall;
    // 지정 축의 Servo-On 신호의 출력 상태를 반환한다.
    function AxmSignalIsServoOn (lAxisNo : LongInt; upOnOff : PDWord) : DWord; stdcall;

    // 지정 축의 Servo-Alarm Reset 신호를 출력한다.
    // uOnOff : FALSE(0), TRUE(1) ( 범용 1출력에 해당됨)
    function AxmSignalServoAlarmReset (lAxisNo : LongInt; uOnOff : DWord) : DWord; stdcall;

    // 범용 출력값을 설정한다.
    // uValue : Hex Value 0x00
    function AxmSignalWriteOutput (lAxisNo : LongInt; uValue : DWord) : DWord; stdcall;
    // 범용 출력값을 반환한다.
    function AxmSignalReadOutput (lAxisNo : LongInt; upValue : PDWord) : DWord; stdcall;

    // ML3 전용 함수
    // 지정축의 Brake sensor의 상태를 반환한다.
    function AxmSignalReadBrakeOn (lAxisNo : LongInt; upOnOff : PDWord) : DWord; stdcall;

    // lBitNo : Bit Number(0 - 4)
    // uOnOff : FALSE(0), TRUE(1)
    // 범용 출력값을 비트별로 설정한다.
    function AxmSignalWriteOutputBit (lAxisNo : LongInt; lBitNo : LongInt; uOnOff : DWord) : DWord; stdcall;
    // 범용 출력값을 비트별로 반환한다.
    function AxmSignalReadOutputBit (lAxisNo : LongInt; lBitNo : LongInt; upOnOff : PDWord) : DWord; stdcall;

    // 범용 입력값을 Hex값으로 반환한다.
    function AxmSignalReadInput (lAxisNo : LongInt; upValue : PDWord) : DWord; stdcall;
    // lBitNo : Bit Number(0 - 4)
    // 범용 입력값을 비트별로 반환한다.
    function AxmSignalReadInputBit (lAxisNo : LongInt; lBitNo : LongInt; upOn : PDWord) : DWord; stdcall;

    // 입력신호들의 디지털 필터계수를 설정한다.
    // uSignal: END_LIMIT(0), INP_ALARM(1), UIN_00_01(2), UIN_02_04(3)
    // dBandwidthUsec: 0.2uSec~26666usec
    function AxmSignalSetFilterBandwidth (lAxisNo : LongInt; uSignal : DWord; dBandwidthUsec : Double) : DWord; stdcall;

    // Universal Output을 mSec 동안 On 유지하다가 Off 시킨다
    // lArraySize : 동작시킬 OutputBit배열의 수
    // lmSec : 0 ~ 30000
    function AxmSignalOutputOn (lAxisNo : LongInt; lArraySize : LongInt; lpBitNo : PLongInt; lmSec : LongInt) : DWord; stdcall;

    // Universal Output을 mSec 동안 Off 유지하다가 On 시킨다
    // lArraySize : 동작시킬 OutputBit배열의 수
    // lmSec : 0 ~ 30000
    function AxmSignalOutputOff (lAxisNo : LongInt; lArraySize : LongInt; lpBitNo : PLongInt; lmSec : LongInt) : DWord; stdcall;

    //========== 모션 구동중 및 구동후에 상태 확인하는 함수==============================================================
    // (구동상태)지정 축의 펄스 출력 상태를 반환한다.
    function AxmStatusReadInMotion (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // (펄스 카운트 값)구동시작 이후 지정 축의 구동 펄스 카운터 값을 반환한다.
    function AxmStatusReadDrivePulseCount (lAxisNo : LongInt; lpPulse : PLongInt) : DWord; stdcall;

    // 지정 축의 DriveStatus(모션중 상태) 레지스터를 반환한다
    // 주의사항 : 각 제품별로 하드웨어적인 신호가 다르기때문에 매뉴얼 및 AXHS.xxx 파일을 참고해야한다.
    function AxmStatusReadMotion (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // 지정 축의 EndStatus(정지 상태) 레지스터를 반환한다.
    // 주의사항 : 각 제품별로 하드웨어적인 신호가 다르기때문에 매뉴얼 및 AXHS.xxx 파일을 참고해야한다.
    function AxmStatusReadStop (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // 지정 축의 Mechanical Signal Data(현재 기계적인 신호상태) 를 반환한다.
    // 주의사항 : 각 제품별로 하드웨어적인 신호가 다르기때문에 매뉴얼 및 AXHS.xxx 파일을 참고해야한다.
    function AxmStatusReadMechanical (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // 지정 축의 현재 구동 속도를 읽어온다.
    function AxmStatusReadVel (lAxisNo : LongInt; dpVel : PDouble) : DWord; stdcall;

    // 지정 축의 Command Pos과 Actual Pos의 차를 반환한다.
    function AxmStatusReadPosError (lAxisNo : LongInt; dpError : PDouble) : DWord; stdcall;

    // 최종 드라이브로 이동하는(이동한) 거리를 확인 한다
    function AxmStatusReadDriveDistance (lAxisNo : LongInt; dpUnit : PDouble) : DWord; stdcall;

    // 지정 축의 위치 정보 사용 방법에 대하여 설정한다.
    // uPosType  : Actual position 과 Command position 의 표시 방법
    //    POSITION_LIMIT '0' - 기본 동작, 전체 범위 내에서 동작
    //    POSITION_BOUND '1' - 위치 범위 주기형, dNegativePos ~ dPositivePos 범위로 동작
    // 주의사항(PCI-Nx04해당)
    // - BOUNT설정시 카운트 값이 Max값을 초과 할 때 Min값이되며 반대로 Min값을 초과 할 때 Max값이 된다.
    // - 다시말해 현재 위치값이 설정한 값 밖에서 카운트 될 때는 위의 Min, Max값이 적용되지 않는다.
    // dPositivePos 설정 범위: 0 ~ 양수
    // dNegativePos 설정 범위: 음수 ~ 0
    function AxmStatusSetPosType (lAxisNo : LongInt; uPosType : DWord; dPositivePos : Double; dNegativePos : Double) : DWord; stdcall;
    // 지정 축의 위치 정보 사용 방법에 대하여 반환한다.
    function AxmStatusGetPosType (lAxisNo : LongInt; upPosType : PDWord; dpPositivePos : PDouble; dpNegativePos : PDouble) : DWord; stdcall;
    // 지정 축의 절대치 엔코더 원점 Offset 위치를 설정한다.[PCI-R1604-MLII 전용]
    function AxmStatusSetAbsOrgOffset (lAxisNo : LongInt; dOrgOffsetPos : Double) : DWord; stdcall;

    // 지정 축의 Actual 위치를 설정한다.
    function AxmStatusSetActPos (lAxisNo : LongInt; dPos : Double) : DWord; stdcall;
    // 지정 축의 Actual 위치를 반환한다.
    function AxmStatusGetActPos (lAxisNo : LongInt; dpPos : PDouble) : DWord; stdcall;
    // 서보측에서 올라오는 지정 축의 Actual 위치를 반환한다.
    function AxmStatusGetAmpActPos (lAxisNo : LongInt; dpPos : PDouble) : DWord; stdcall;

    // 지정 축의 Command 위치를 설정한다.
    function AxmStatusSetCmdPos (lAxisNo : LongInt; dPos : Double) : DWord; stdcall;
    // 지정 축의 Command 위치를 반환한다.
    function AxmStatusGetCmdPos (lAxisNo : LongInt; dpPos : PDouble) : DWord; stdcall;
    // 지정 축의 Command 위치와 Actual 위치를 dPos 값으로 일치 시킨다.
    function AxmStatusSetPosMatch (lAxisNo : LongInt; dPos : Double) : DWord; stdcall;

    // 지정 축의 모션 상태(Cmd, Act, Driver Status, Mechanical Signal, Universal Signal)를 한번에 확인 할 수 있다.
    // MOTION_INFO 구조체의 dwMask 설정으로 모션 상태 정보를 지정한다.
    // dwMask : 모션 상태 표시(6bit) - ex) dwMask = 0x1F 설정 시 모든 상태를 표시함.
    // 사용자가 설정한 Level(In/Out)은 반영되지 않음.
    //    [0]        |    Command Position Read
    //    [1]        |    Actual Position Read
    //    [2]        |    Mechanical Signal Read
    //    [3]        |    Driver Status Read
    //    [4]        |    Universal Signal Input Read
    //               |    Universal Signal Output Read
    function AxmStatusReadMotionInfo (lAxisNo : LongInt; pMI : PMOTION_INFO) : DWord; stdcall;

    // Network 제품 전용함수.
    // 지정한 축의 서보팩에 AlarmCode를 읽어오도록 명령하는 함수.
    function AxmStatusRequestServoAlarm (lAxisNo : LongInt) : DWord; stdcall;
    // 지정한 축의 서보팩 AlarmCode를 읽어오는 함수.
    // upAlarmCode      : 해당 서보팩의 Alarm Code참조
    // MR_J4_xxB  : 상위 16Bit : 알람코드 2 digit의 10진수 값, 하위 16Bit : 알람 상세 코드 1 digit 10진수 값
    // uReturnMode      : 함수의 반환 동작조건을 설정[SIIIH(MR-J4-xxB)는 사용하지 않음]
    // [0-Immediate]    : 함수 실행 후 바로 반환
    // [1-Blocking]     : 서보팩으로 부터 알람 코드를 읽을 대 까지 반환하지않음
    // [2-Non Blocking] : 서보팩으로 부터 알람 코드를 읽을 대 까지 반환하지않으나 프로그램 Blocking되지않음
    function AxmStatusReadServoAlarm (lAxisNo : LongInt; uReturnMode : DWord; upAlarmCode : PDWord) : DWord; stdcall;
    // 지정한 에러코드에 해당하는 Alarm String을 받아오는 함수
    function AxmStatusGetServoAlarmString (lAxisNo : LongInt; uAlarmCode : DWord; lAlarmStringSize : LongInt; szAlarmString : char*) : DWord; stdcall;

    // 지정한 축의 서보팩에 Alarm History를 읽어오도록 명령하는 함수
    function AxmStatusRequestServoAlarmHistory (lAxisNo : LongInt) : DWord; stdcall;
    // 지정한 축의 서보팩 Alarm History를 읽어오는 함수.
    // lpCount          : 읽은 Alarm History 개수
    // upAlarmCode      : Alarm History를 반환할 배열
    // uReturnMode      : 함수의 반환 동작조건을 설정
    // [0-Immediate]    : 함수 실행 후 바로 반환
    // [1-Blocking]     : 서보팩으로 부터 알람 코드를 읽을 대 까지 반환하지않음
    // [2-Non Blocking] : 서보팩으로 부터 알람 코드를 읽을 대 까지 반환하지않으나 프로그램 Blocking되지않음
    function AxmStatusReadServoAlarmHistory (lAxisNo : LongInt; uReturnMode : DWord; lpCount : PLongInt; upAlarmCode : PDWord) : DWord; stdcall;
    // 지정한 축의 서보팩 Alarm History를 Clear한다.
    function AxmStatusClearServoAlarmHistory (lAxisNo : LongInt) : DWord; stdcall;

    //======== 홈관련 함수===============================================================================================
    // 지정 축의 Home 센서 Level 을 설정한다.
    // uLevel : LOW(0), HIGH(1)
    function AxmHomeSetSignalLevel (lAxisNo : LongInt; uLevel : DWord) : DWord; stdcall;
    // 지정 축의 Home 센서 Level 을 반환한다.
    function AxmHomeGetSignalLevel (lAxisNo : LongInt; upLevel : PDWord) : DWord; stdcall;
    // 현재 홈 신호 입력상태를 확인한다. 홈신호는 사용자가 임의로 AxmHomeSetMethod 함수를 이용하여 설정할수있다.
    // 일반적으로 홈신호는 범용 입력 0를 사용하고있지만 AxmHomeSetMethod 이용해서 바꾸면 + , - Limit를 사용할수도있다.
    // upStatus : OFF(0), ON(1)
    function AxmHomeReadSignal (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // 해당 축의 원점검색을 수행하기 위해서는 반드시 원점 검색관련 파라메타들이 설정되어 있어야 됩니다.
    // 만약 MotionPara설정 파일을 이용해 초기화가 정상적으로 수행됐다면 별도의 설정은 필요하지 않다.
    // 원점검색 방법 설정에는 검색 진행방향, 원점으로 사용할 신호, 원점센서 Active Level, 엔코더 Z상 검출 여부 등을 설정 한다.
    // 주의사항 : 레벨을 잘못 설정시 -방향으로 설정해도  +방향으로 동작할수 있으며, 홈을 찾는데 있어 문제가 될수있다.
    // (자세한 내용은 AxmMotSaveParaAll 설명 부분 참조)
    // 홈레벨은 AxmSignalSetHomeLevel 사용한다.
    // HClrTim : HomeClear Time : 원점 검색 Encoder 값 Set하기 위한 대기시간
    // HmDir(홈 방향): DIR_CCW (0) -방향 , DIR_CW(1) +방향
    // HOffset - 원점검출후 이동거리.
    // uZphas: 1차 원점검색 완료 후 엔코더 Z상 검출 유무 설정  0: 사용안함 , 1: HmDir과 반대 방향, 2: HmDir과 같은 방향
    // HmSig :  PosEndLimit(0) -> +Limit
    //          NegEndLimit(1) -> -Limit
    //          HomeSensor (4) -> 원점센서(범용 입력 0)
    function AxmHomeSetMethod (lAxisNo : LongInt; lHmDir : LongInt; uHomeSignal : DWord; uZphas : DWord; dHomeClrTime : Double; dHomeOffset : Double) : DWord; stdcall;
    // 설정되어있는 홈 관련 파라메타들을 반환한다.
    function AxmHomeGetMethod (lAxisNo : LongInt; lpHmDir : PLongInt; upHomeSignal : PDWord; upZphas : PDWord; dpHomeClrTime : PDouble; dpHomeOffset : PDouble) : DWord; stdcall;

    // 원점검색 방법의 미세조정을 하는 함수(기본적으로 설정하지 않아도됨).
    // dHomeDogDistance[500 pulse]: 첫번째 Step에서 HomeDog가 센서를 지나쳤는지 확인하기위한 Dog길이를 입력.(단위는 AxmMotSetMoveUnitPerPulse함수로 설정한 단위)
    // lLevelScanTime[100msec]: 2번째 Step(원점센서를 빠져나가는 동작)에서 Level상태를 확인할 Scan시간을 설정(단위는 msec[1~1000]).
    // dwFineSearchUse[USE]: 기본 원점검색시 5 Step를 사용하는데 3 Step만 사용하도록 변경할때 0으로 설정.
    // dwHomeClrUse[USE]: 원점검색 후 지령값과 Encoder값을 0으로 자동 설정여부를 설정.
    function AxmHomeSetFineAdjust (lAxisNo : LongInt; dHomeDogLength : Double; lLevelScanTime : LongInt; uFineSearchUse : DWord; uHomeClrUse : DWord) : DWord; stdcall;
    // 설정되어있는 홈 관련 미세조정 파라메타들을 반환한다.
    function AxmHomeGetFineAdjust (lAxisNo : LongInt; dpHomeDogLength : PDouble; lpLevelScanTime : PLongInt; upFineSearchUse : PDWord; upHomeClrUse : PDWord) : DWord; stdcall;

    // 원점 검색시 Interlock을 설정하는 함수(기본적으로 설정하지 않아도됨).
    // uInterlockMode : Interlock 설정 모드
    //   (0) HOME_INTERLOCK_UNUSED          : Home Interlock 사용하지 않음
    //   [1] HOME_INTERLOCK_SENSOR_CHECK    : 원점검색 진행 방향에 설치된 리미트 센서가 감지 되었을 때 원점 센서가 같이 감지되지 않은 경우 INTERLOCK 에러 발생
    //   [2] HOME_INTERLOCK_DISTANCE        : 원점검색 진행 방향에 설치된 리미트 센서가 감지 된 후 원점 센서까지의 거리가 지정한 거리보다 클 경우 INTERLOCK 에러 발생
    // dInterlockData : Interlock Mode에 대한 설정값
    //   (0) HOME_INTERLOCK_UNUSED          : 사용안함
    //   [1] HOME_INTERLOCK_SENSOR_CHECK    : 사용안함
    //   [2] HOME_INTERLOCK_DISTANCE        : 원점검색 진행 방향에 설치된 리미트와 원점 센서까지의 거리(실제 거리보다 약간 크게 설정 함)
    function AxmHomeSetInterlock (lAxisNo : LongInt; uInterlockMode : DWord; dInterlockData : Double) : DWord; stdcall;
    // 원점 검색시 사용되는 Interlock 설정값을 반환한다.
    function AxmHomeGetInterlock (lAxisNo : LongInt; upInterlockMode : PDWord; dpInterlockData : PDouble) : DWord; stdcall;

    // 원점을 빠르고 정밀하게 검색하기 위해 여러 단계의 스탭으로 검출한다. 이때 각 스탭에 사용 될 속도를 설정한다.
    // 이 속도들의 설정값에 따라 원점검색 시간과, 원점검색 정밀도가 결정된다.
    // 각 스탭별 속도들을 적절히 바꿔가면서 각 축의 원점검색 속도를 설정하면 된다.
    // (자세한 내용은 AxmMotSaveParaAll 설명 부분 참조)
    // 원점검색시 사용될 속도를 설정하는 함수
    // [dVelFirst]- 1차구동속도   [dVelSecond]-검출후속도   [dVelThird]- 마지막 속도  [dvelLast]- index검색및 정밀하게 검색하기위해.
    // [dAccFirst]- 1차구동가속도 [dAccSecond]-검출후가속도
    function AxmHomeSetVel (lAxisNo : LongInt; dVelFirst : Double; dVelSecond : Double; dVelThird : Double; dVelLast : Double; dAccFirst : Double; dAccSecond : Double) : DWord; stdcall;
    // 설정되어있는 원점검색시 사용될 속도를 반환한다.
    function AxmHomeGetVel (lAxisNo : LongInt; dpVelFirst : PDouble; dpVelSecond : PDouble; dpVelThird : PDouble; dpVelLast : PDouble; dpAccFirst : PDouble; dpAccSecond : PDouble) : DWord; stdcall;

    // 원점검색을 시작한다.
    // 원점검색 시작함수를 실행하면 라이브러리 내부에서 해당축의 원점검색을 수행 할 쓰레드가 자동 생성되어 원점검색을 순차적으로 수행한 후 자동 종료된다.
    // 주의사항 : 진행방향과 반대방향의 리미트 센서가 들어와도 진행방향의 센서가 ACTIVE되지않으면 동작한다.
    //            원점 검색이 시작되어 진행방향이 리밋트 센서가 들어오면 리밋트 센서가 감지되었다고 생각하고 다음단계로 진행된다.
    function AxmHomeSetStart (lAxisNo : LongInt) : DWord; stdcall;
    // 원점검색 결과를 사용자가 임의로 설정한다.
    // 원점검색 함수를 이용해 성공적으로 원점검색이 수행되고나면 검색 결과가 HOME_SUCCESS로 설정됩니다.
    // 이 함수는 사용자가 원점검색을 수행하지않고 결과를 임의로 설정할 수 있다.
    // uHomeResult 설정
    // HOME_SUCCESS          = 0x01    // 홈 완료
    // HOME_SEARCHING        = 0x02    // 홈검색중
    // HOME_ERR_GNT_RANGE    = 0x10    // 홈 검색 범위를 벗어났을경우
    // HOME_ERR_USER_BREAK   = 0x11    // 속도 유저가 임의로 정지명령을 내렸을경우
    // HOME_ERR_VELOCITY     = 0x12    // 속도 설정 잘못했을경우
    // HOME_ERR_AMP_FAULT    = 0x13    // 서보팩 알람 발생 에러
    // HOME_ERR_NEG_LIMIT    = 0x14    // (-)방향 구동중 (+)리미트 센서 감지 에러
    // HOME_ERR_POS_LIMIT    = 0x15    // (+)방향 구동중 (-)리미트 센서 감지 에러
    // HOME_ERR_NOT_DETECT   = 0x16    // 지정한 신호 검출하지 못 할 경우 에러
    // HOME_ERR_UNKNOWN      = 0xFF
    function AxmHomeSetResult (lAxisNo : LongInt; uHomeResult : DWord) : DWord; stdcall;
    // 원점검색 결과를 반환한다.
    // 원점검색 함수의 검색 결과를 확인한다. 원점검색이 시작되면 HOME_SEARCHING으로 설정되며 원점검색에 실패하면 실패원인이 설정된다. 실패 원인을 제거한 후 다시 원점검색을 진행하면 된다.
    function AxmHomeGetResult (lAxisNo : LongInt; upHomeResult : PDWord) : DWord; stdcall;

    // 원점검색 진행률을 반환한다.
    // 원점검색 시작되면 진행율을 확인할 수 있다. 원점검색이 완료되면 성공여부와 관계없이 100을 반환하게 된다. 원점검색 성공여부는 GetHome Result함수를 이용해 확인할 수 있다.
    // upHomeMainStepNumber                        : Main Step 진행율이다.
    // 겐트리 FALSE일 경우upHomeMainStepNumber     : 0 일때면 선택한 축만 진행사항이고 홈 진행율은 upHomeStepNumber 표시한다.
    // 겐트리 TRUE일 경우 upHomeMainStepNumber     : 0 일때면 마스터 홈을 진행사항이고 마스터 홈 진행율은 upHomeStepNumber 표시한다.
    // 겐트리 TRUE일 경우 upHomeMainStepNumber     : 10 일때면 슬레이브 홈을 진행사항이고 마스터 홈 진행율은 upHomeStepNumber 표시한다.
    // upHomeStepNumber                            : 선택한 축에대한 진행율을 표시한다.
    // 겐트리 FALSE일 경우                         : 선택한 축만 진행율을 표시한다.
    // 겐트리 TRUE일 경우 마스터축, 슬레이브축 순서로 진행율을 표시된다.
    function AxmHomeGetRate (lAxisNo : LongInt; upHomeMainStepNumber : PDWord; upHomeStepNumber : PDWord) : DWord; stdcall;

    //========= 위치 구동함수 ===========================================================================================
    // 주의사항: 위치를 설정할경우 반드시 UNIT/PULSE의 맞추어서 설정한다.
    //           위치를 UNIT/PULSE 보다 작게할 경우 최소단위가 UNIT/PULSE로 맞추어지기때문에 그위치까지 구동이 될수없다.

    // 설정 속도 단위가 RPM(Revolution Per Minute)으로 맞추고 싶다면.
    // ex>    rpm 계산:
    // 4500 rpm ?
    // unit/ pulse = 1 : 1이면      pulse/ sec 초당 펄스수가 되는데
    // 4500 rpm에 맞추고 싶다면     4500 / 60 초 : 75회전/ 1초
    // 모터가 1회전에 몇 펄스인지 알아야 된다. 이것은 Encoder에 Z상을 검색해보면 알수있다.
    // 1회전:1800 펄스라면 75 x 1800 = 135000 펄스가 필요하게 된다.
    // AxmMotSetMoveUnitPerPulse에 Unit = 1, Pulse = 1800 넣어 동작시킨다.

    // 설정한 거리만큼 또는 위치까지 이동한다.
    // 지정 축의 절대 좌표/ 상대좌표 로 설정된 위치까지 설정된 속도와 가속율로 구동을 한다.
    // 속도 프로파일은 AxmMotSetProfileMode 함수에서 설정한다.
    // 펄스가 출력되는 시점에서 함수를 벗어난다.
    // AxmMotSetAccelUnit(lAxisNo, 1) 일경우 dAccel -> dAccelTime , dDecel -> dDecelTime 으로 바뀐다.
    function AxmMoveStartPos (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 설정한 거리만큼 또는 위치까지 이동한다.
    // 지정 축의 절대 좌표/상대좌표로 설정된 위치까지 설정된 속도와 가속율로 구동을 한다.
    // 속도 프로파일은 AxmMotSetProfileMode 함수에서 설정한다.
    // 펄스 출력이 종료되는 시점에서 함수를 벗어난다
    function AxmMovePos (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 설정한 속도로 구동한다.
    // 지정 축에 대하여 설정된 속도와 가속율로 지속적으로 속도 모드 구동을 한다.
    // 펄스 출력이 시작되는 시점에서 함수를 벗어난다.
    // Vel값이 양수이면 CW, 음수이면 CCW 방향으로 구동.
    function AxmMoveVel (lAxisNo : LongInt; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 지정된 다축에 대하여 설정된 속도와 가속율로 지속적으로 속도 모드 구동을 한다.
    // 펄스 출력이 시작되는 시점에서 함수를 벗어난다.
    // Vel값이 양수이면 CW, 음수이면 CCW 방향으로 구동.
    function AxmMoveStartMultiVel (lArraySize : LongInt; lpAxesNo : PLongInt; dpVel : PDouble; dpAccel : PDouble; dpDecel : PDouble) : DWord; stdcall;

    // 지정된 다축에 대하여 설정된 속도와 가속율, SyncMode에 따라 지속적으로 속도 모드 구동을 한다.
    // 펄스 출력이 시작되는 시점에서 함수를 벗어난다.
    // Vel값이 양수이면 CW, 음수이면 CCW 방향으로 구동.
    // dwSyncMode    : 동기정지기능 사용안함(0), 동기정지 기능만 사용(1), 알람에 대해서도 동기 정기기능 사용(2)
    function AxmMoveStartMultiVelEx (lArraySize : LongInt; lpAxesNo : PLongInt; dpVel : PDouble; dpAccel : PDouble; dpDecel : PDouble; dwSyncMode : DWord) : DWord; stdcall;

    // 지정된 다축에 대하여 설정된 속도와 가속율로 지속적으로 속도 모드 구동을 한다.
    // 펄스 출력이 시작되는 시점에서 함수를 벗어나며 Master축은(Distance가 가장 큰) dVel속도로 움직이며, 나머지 축들의 Distance비율로 움직인다.
    // 속도는 해당 Chip중 축 번호가 가장 낮은 축의 속도만 읽힘
    function AxmMoveStartLineVel (lArraySize : LongInt; lpAxesNo : PLongInt; dpDis : PDouble; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 특정 Input 신호의 Edge를 검출하여 즉정지 또는 감속정지하는 함수.
    // lDetect Signal : edge 검출할 입력 신호 선택.
    // lDetectSignal  : PosEndLimit(0), NegEndLimit(1), HomeSensor(4), EncodZPhase(5), UniInput02(6), UniInput03(7)
    // Signal Edge    : 선택한 입력 신호의 edge 방향 선택 (rising or falling edge).
    //                  SIGNAL_DOWN_EDGE(0), SIGNAL_UP_EDGE(1)
    // 구동방향       : Vel값이 양수이면 CW, 음수이면 CCW.
    // SignalMethod   : 급정지 EMERGENCY_STOP(0), 감속정지 SLOWDOWN_STOP(1)
    // 주의사항: SignalMethod를 EMERGENCY_STOP(0)로 사용할경우 가감속이 무시되며 지정된 속도로 가속 급정지하게된다.
    //           PCI-Nx04를 사용할 경우 lDetectSignal이 PosEndLimit , NegEndLimit(0,1) 을 찾을경우 신호의레벨 Active 상태를 검출하게된다.
    function AxmMoveSignalSearch (lAxisNo : LongInt; dVel : Double; dAccel : Double; lDetectSignal : LongInt; lSignalEdge : LongInt; lSignalMethod : LongInt) : DWord; stdcall;

    // 특정 Input 신호의 Edge를 검출하여 사용자가 지정함 위치 값만큼 이동하는 함수.(MLIII : Sigma-5/7 전용)
    // dVel           : 구동 속도 설정, 양수이면 CW, 음수이면 CCW.
    // dAccel         : 구동 가속도 설정
    // dDecel         : 구동 감속도 설정, 일반적으로 dAccel의 50배로 설정함.
    // lDetectSignal  : HomeSensor(4)
    // dDis           : 입력 신호의 검출 위치를 기준으로 사용자가 지정한 위치만큼 상대 구동됨.
    // 주의사항:
    //          - 구동방향과 반대 방향으로 dDis 값 입력시 역방향으로 구동 될 수 있음.
    //          - 속도가 빠르고, dDis 값이 작은 경우 모터가 신호 감지해서 정지한 이후에 최종 위치로 가기 위해서 역방향으로 구동될 수 있음
    //          - 해당 함수를 사용하기 전에 원점 센서는 반드시 LOW 또는 HIGH로 설정되어 있어야함.
    function AxmMoveSignalSearchAtDis (lAxisNo : LongInt; dVel : Double; dAccel : Double; dDecel : Double; lDetectSignal : LongInt; dDis : Double) : DWord; stdcall;

    // 지정 축에서 설정된 신호를 검출하고 그 위치를 저장하기 위해 이동하는 함수이다.
    // 원하는 신호를 골라 찾아 움직이는 함수 찾을 경우 그 위치를 저장시켜놓고 AxmGetCapturePos사용하여 그값을 읽는다.
    // Signal Edge   : 선택한 입력 신호의 edge 방향 선택 (rising or falling edge).
    //                 SIGNAL_DOWN_EDGE(0), SIGNAL_UP_EDGE(1)
    // 구동방향      : Vel값이 양수이면 CW, 음수이면 CCW.
    // SignalMethod  : 급정지 EMERGENCY_STOP(0), 감속정지 SLOWDOWN_STOP(1)
    // lDetect Signal: edge 검출할 입력 신호 선택.SIGNAL_DOWN_EDGE(0), SIGNAL_UP_EDGE(1)
    //                 상위 8bit에 대하여 기본 구동(0), Software 구동(1) 을 선택할 수 있다. SMP Board(PCIe-Rxx05-MLIII) 전용
    // lDetectSignal : PosEndLimit(0), NegEndLimit(1), HomeSensor(4), EncodZPhase(5), UniInput02(6), UniInput03(7)
    // lTarget       : COMMAND(0), ACTUAL(1)
    // 주의사항: SignalMethod를 EMERGENCY_STOP(0)로 사용할경우 가감속이 무시되며 지정된 속도로 가속 급정지하게된다.
    //           PCI-Nx04를 사용할 경우 lDetectSignal이 PosEndLimit , NegEndLimit(0,1) 을 찾을경우 신호의레벨 Active 상태를 검출하게된다.
    function AxmMoveSignalCapture (lAxisNo : LongInt; dVel : Double; dAccel : Double; lDetectSignal : LongInt; lSignalEdge : LongInt; lTarget : LongInt; lSignalMethod : LongInt) : DWord; stdcall;
    // 'AxmMoveSignalCapture' 함수에서 저장된 위치값을 확인하는 함수이다.
    // 주의사항: 함수 실행 결과가 "AXT_RT_SUCCESS"일때 저장된 위치가 유효하며, 이 함수를 한번 실행하면 저장 위치값이 초기화된다.
    function AxmMoveGetCapturePos (lAxisNo : LongInt; dpCapPotition : PDouble) : DWord; stdcall;

    // 설정한 거리만큼 또는 위치까지 이동하는 함수.
    // 함수를 실행하면 해당 Motion 동작을 시작한 후 Motion 이 완료될때까지 기다리지 않고 바로 함수를 빠져나간다."
    function AxmMoveStartMultiPos (lArraySize : LongInt; lpAxisNo : PLongInt; dpPos : PDouble; dpVel : PDouble; dpAccel : PDouble; dpDecel : PDouble) : DWord; stdcall;

    // 다축을 설정한 거리만큼 또는 위치까지 이동한다.
    // 지정 축들의 절대 좌표로 설정된 위치까지 설정된 속도와 가속율로 구동을 한다.
    function AxmMoveMultiPos (lArraySize : LongInt; lpAxisNo : PLongInt; dpPos : PDouble; dpVel : PDouble; dpAccel : PDouble; dpDecel : PDouble) : DWord; stdcall;

    // 설정한 토크 및 속도 값으로 모터를 구동한다.(PCI-R1604-MLII/SIIIH, PCIe-Rxx04-SIIIH  전용 함수)
    // dTroque        : 최대 출력 토크에 대한 %값.
    // 구동방향       : dTroque값이 양수이면 CW, 음수이면 CCW.
    // dVel           : 최대 모터 구동 속도에 대한 %값.
    // dwAccFilterSel : LINEAR_ACCDCEL(0), EXPO_ACCELDCEL(1), SCURVE_ACCELDECEL(2)
    // dwGainSel      : GAIN_1ST(0), GAIN_2ND(1)
    // dwSpdLoopSel   : PI_LOOP(0), P_LOOP(1)

    // PCIe-Rxx05-MLIII(지원 제품: Sigma-5, Sigma-7)
    // dTorque        : 정격 토크에 대한 %값 (설정 허용 범위: -300.0 ~ 300.0)
    //                  dTorque 값이 양수면 CW, 음수면 CCW 방향으로 구동
    // dVel           : 구동 속도 (단위: pps)
    // dwAccFilterSel : 사용하지 않음
    // dwGainSel      : 사용하지 않음
    // dwSpdLoopSel   : 사용하지 않음
    function AxmMoveStartTorque (lAxisNo : LongInt; dTorque : Double; dVel : Double; dwAccFilterSel : DWord; dwGainSel : DWord; dwSpdLoopSel : DWord) : DWord; stdcall;

    // 지정 축의 토크 구동을 정지 한다.
    // AxmMoveStartTorque후 반드시 AxmMoveTorqueStop를 실행하여야 한다.
    function AxmMoveTorqueStop (lAxisNo : LongInt; dwMethod : DWord) : DWord; stdcall;

    // 설정한 거리만큼 또는 위치까지 이동한다.
    // 지정 축의 절대 좌표/상대좌표로 설정된 위치까지 설정된 속도/가속율로 구동을 한다.
    // 속도 프로파일은 비대칭 사다리꼴로 고정됩니다.
    // 가감속도 설정 단위는 기울기로 고정됩니다.
    // dAccel != 0.0 이고 dDecel == 0.0 일 경우 이전 속도에서 감속 없이 지정 속도까지 가속.
    // dAccel != 0.0 이고 dDecel != 0.0 일 경우 이전 속도에서 지정 속도까지 가속후 등속 이후 감속.
    // dAccel == 0.0 이고 dDecel != 0.0 일 경우 이전 속도에서 다음 속도까지 감속.

    // 다음의 조건을 만족하여야 합니다.
    // dVel[1] == dVel[3]을 반드시 만족하여야 한다.
    // dVel[2]로 정속 구동 구간이 발생할 수 있도록 dPosition이 충분히 큰값이어야 한다.
    // Ex) dPosition = 10000;
    // dVel[0] = 300., dAccel[0] = 200., dDecel[0] = 0.;    <== 가속
    // dVel[1] = 500., dAccel[1] = 100., dDecel[1] = 0.;    <== 가속
    // dVel[2] = 700., dAccel[2] = 200., dDecel[2] = 250.;  <== 가속, 등속, 감속
    // dVel[3] = 500., dAccel[3] = 0.,   dDecel[3] = 150.;  <== 감속
    // dVel[4] = 200., dAccel[4] = 0.,   dDecel[4] = 350.;  <== 감속
    // 펄스 출력이 종료되는 시점에서 함수를 벗어난다
    function AxmMoveStartPosWithList (lAxisNo : LongInt; dPosition : Double; dpVel : PDouble; dpAccel : PDouble; dpDecel : PDouble; lListNum : LongInt) : DWord; stdcall;


    // 설정한 거리만큼 또는 위치까지 대상 축의 위치가 증감할 때 이동을 시작한다.
    // lEvnetAxisNo    : 시작 조건 발생 축
    // dComparePosition: 시작 조건 발생 축의 조건 발생 위치.
    // uPositionSource : 시작 조건 발생 축의 조건 발생 위치 기준 선택 => COMMAND(0), ACTUAL(1)
    // 예약 후 취소는 AxmMoveStop, AxmMoveEStop, AxmMoveSStop를 사용
    // 이동 축과 시작 조건 발생 축은 4축 단위 하나의 그룹(2V04의 경우 같은 모듈)에 존재하여야 합니다.
    function AxmMoveStartPosWithPosEvent (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; lEventAxisNo : LongInt; dComparePosition : Double; uPositionSource : DWord) : DWord; stdcall;

    // 지정 축을 설정한 감속도로 감속 정지 한다.
    // dDecel : 정지 시 감속율값
    function AxmMoveStop (lAxisNo : LongInt; dDecel : Double) : DWord; stdcall;
    // 지정 축을 설정한 감속도로 감속 정지 한다.(PCI-Nx04 전용)
    // 현재 가감속 상태와 관계없이 즉시 감속 가능 함수이며 제한된 구동에 대하여 사용 가능하다.
    // -- 사용 가능 구동 : AxmMoveStartPos, AxmMoveVel, AxmLineMoveEx2.
    // dDecel : 정지 시 감속율값
    // 주의 : 감속율값은 최초 설정 감속율보다 크거나 같아야 한다.
    // 주의 : 감속 설정을 시간으로 하였을 경우 최초 설정 감속 시간보다 작거나 같아야 한다.
    function AxmMoveStopEx (lAxisNo : LongInt; dDecel : Double) : DWord; stdcall;
    // 지정 축을 급 정지 한다.
    function AxmMoveEStop (lAxisNo : LongInt) : DWord; stdcall;
    // 지정 축을 감속 정지한다.
    function AxmMoveSStop (lAxisNo : LongInt) : DWord; stdcall;

    //========= 오버라이드 함수 =========================================================================================
    // 위치 오버라이드 한다.
    // 지정 축의 구동이 종료되기 전 지정된 출력 펄스 수를 조정한다.
    // PCI-Nx04 / PCI(e)-Rxx04 type 사용 시 주의사항
    // : 오버라이드 할 위치를 넣을 때는 구동 시점의 위치를 기준으로 한 Relative 형태의 위치값으로 넣어준다.
    //   구동 시작 후 같은 방향의 경우 오버라이드를 계속할 수 있지만 반대 방향으로 오버라이드 할 경우에는 오버라이드를 계속할 수 없다.
    function AxmOverridePos (lAxisNo : LongInt; dOverridePos : Double) : DWord; stdcall;

    // 지정 축의 속도오버라이드 하기전에 오버라이드할 최고속도를 설정한다.
    // 주의점 : 속도오버라이드를 5번한다면 그중에 최고 속도를 설정해야된다.
    function AxmOverrideSetMaxVel (lAxisNo : LongInt; dOverrideMaxVel : Double) : DWord; stdcall;
    // 속도 오버라이드 한다.
    // 지정 축의 구동 중에 속도를 가변 설정한다. (반드시 모션 중에 가변 설정한다.)
    // 주의점: AxmOverrideVel 함수를 사용하기전에. AxmOverrideMaxVel 최고로 설정할수있는 속도를 설정해놓는다.
    // EX> 속도오버라이드를 두번한다면
    // 1. 두개중에 높은 속도를 AxmOverrideMaxVel 설정 최고 속도값 설정.
    // 2. AxmMoveStartPos 실행 지정 축의 구동 중(Move함수 모두 포함)에 속도를 첫번째 속도로 AxmOverrideVel 가변 설정한다.
    // 3. 지정 축의 구동 중(Move함수 모두 포함)에 속도를 두번째 속도로 AxmOverrideVel 가변 설정한다.
    function AxmOverrideVel (lAxisNo : LongInt; dOverrideVel : Double) : DWord; stdcall;
    // 가속도, 속도, 감속도를  오버라이드 한다.
    // 지정 축의 구동 중에 가속도, 속도, 감속도를 가변 설정한다. (반드시 모션 중에 가변 설정한다.)
    // 주의점: AxmOverrideAccelVelDecel 함수를 사용하기전에. AxmOverrideMaxVel 최고로 설정할수있는 속도를 설정해놓는다.
    // EX> 속도오버라이드를 두번한다면
    // 1. 두개중에 높은 속도를 AxmOverrideMaxVel 설정 최고 속도값 설정.
    // 2. AxmMoveStartPos 실행 지정 축의 구동 중(Move함수 모두 포함)에 가속도, 속도, 감속도를 첫번째 속도로 AxmOverrideAccelVelDecel 가변 설정한다.
    // 3. 지정 축의 구동 중(Move함수 모두 포함)에 가속도, 속도, 감속도를 두번째 속도로 AxmOverrideAccelVelDecel 가변 설정한다.
    function AxmOverrideAccelVelDecel (lAxisNo : LongInt; dOverrideVelocity : Double; dMaxAccel : Double; dMaxDecel : Double) : DWord; stdcall;
    // 어느 시점에서 속도 오버라이드 한다.
    // 어느 위치 지점과 오버라이드할 속도를 입력시켜 그위치에서 속도오버라이드 되는 함수
    // lTarget : COMMAND(0), ACTUAL(1)
    // 주의점  : AxmOverrideVelAtPos 함수를 사용하기전에. AxmOverrideMaxVel 최고로 설정할수있는 속도를 설정해놓는다.
    function AxmOverrideVelAtPos (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; dOverridePos : Double; dOverrideVel : Double; lTarget : LongInt) : DWord; stdcall;
    // 지정한 시점들에서 지정한 속도로 오버라이드 한다.
    // lArraySize     : 오버라이드 할 위치의 개수를 설정.
    // *dpOverridePos : 오버라이드 할 위치의 배열(lArraySize에서 설정한 개수보다 같거나 크게 선언해야됨)
    // *dpOverrideVel : 오버라이드 할 위치에서 변경 될 속도 배열(lArraySize에서 설정한 개수보다 같거나 크게 선언해야됨)
    // lTarget        : COMMAND(0), ACTUAL(1)
    // dwOverrideMode : 오버라이드 시작 방법을 지정함.
    //                : OVERRIDE_POS_START(0) 지정한 위치에서 지정한 속도로 오버라이드 시작함
    //                : OVERRIDE_POS_END(1) 지정한 위치에서 지정한 속도가 되도록 미리 오버라이드 시작함
    function AxmOverrideVelAtMultiPos (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; lArraySize : LongInt; dpOverridePos : PDouble; dpOverrideVel : PDouble; lTarget : LongInt; dwOverrideMode : DWord) : DWord; stdcall;

    // 지정한 시점들에서 지정한 속도/가감속도로 오버라이드 한다.(MLII 전용)
    // lArraySize     : 오버라이드 할 위치의 개수를 설정(최대 5).
    // *dpOverridePos : 오버라이드 할 위치의 배열(lArraySize에서 설정한 개수보다 같거나 크게 선언해야됨)
    // *dpOverrideVel : 오버라이드 할 위치에서 변경 될 속도 배열(lArraySize에서 설정한 개수보다 같거나 크게 선언해야됨)
    // *dpOverrideAccelDecel : 오버라이드 할 위치에서 변경 될 가감속도 배열(lArraySize에서 설정한 개수보다 같거나 크게 선언해야됨)
    // lTarget        : COMMAND(0), ACTUAL(1)
    // dwOverrideMode : 오버라이드 시작 방법을 지정함.
    //                : OVERRIDE_POS_START(0) 지정한 위치에서 지정한 속도로 오버라이드 시작함
    //                : OVERRIDE_POS_END(1) 지정한 위치에서 지정한 속도가 되도록 미리 오버라이드 시작함
    function AxmOverrideVelAtMultiPos2 (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; lArraySize : LongInt; dpOverridePos : PDouble; dpOverrideVel : PDouble; dpOverrideAccelDecel : PDouble; lTarget : LongInt; dwOverrideMode : DWord) : DWord; stdcall;

    // 지정한 시점들에서 지정한 속도/가감속도로 오버라이드 한다.
    // lArraySize   : 오버라이드 할 위치의 개수를 설정(최대 28).
    // *dpOverridePosition : 오버라이드 할 위치의 배열(lArraySize에서 설정한 개수보다 같거나 크게 선언해야됨)
    // *dpOverrideVelocity : 오버라이드 할 위치에서 변경 될 속도 배열(lArraySize에서 설정한 개수보다 같거나 크게 선언해야됨)
    // *dpOverrideAccel : 오버라이드 할 위치에서 변경 될 가속도 배열(lArraySize에서 설정한 개수보다 같거나 크게 선언해야됨)
    // *dpOverrideDecel : 오버라이드 할 위치에서 변경 될 감속도 배열(lArraySize에서 설정한 개수보다 같거나 크게 선언해야됨)
    // lTarget    : COMMAND(0), ACTUAL(1)
    // dwOverrideMode : 오버라이드 시작 방법을 지정함.
    //      : OVERRIDE_POS_START(0) 지정한 위치에서 지정한 속도로 오버라이드 시작함
    //      : OVERRIDE_POS_END(1) 지정한 위치에서 지정한 속도가 되도록 미리 오버라이드 시작함
    function AxmOverrideAccelVelDecelAtMultiPos (lAxisNo : LongInt; dPosition : Double; dVelocity : Double; dAcceleration : Double; dDeceleration : Double; lArraySize : LongInt; dpOverridePosition : PDouble; dpOverrideVelocity : PDouble; dpOverrideAccel : PDouble; dpOverrideDecel : PDouble; lTarget : LongInt; dwOverrideMode : DWord) : DWord; stdcall;

    // 다축을 동시에 속도 오버라이드 한다.
    // 주의점: 함수를 사용하기전에. AxmOverrideMaxVel 최고로 설정할수있는 속도를 설정해놓는다.
    // lArraySzie     : 오버라이드 할 축의 개수
    // lpAxisNo       : 오버라이드 할 축의 배열
    // dpOveerrideVel : 오버라이드 할 속도 배열
    function AxmOverrideMultiVel (lArraySize : LongInt; lpAxisNo : PLongInt; dpOverrideVel : PDouble) : DWord; stdcall;

    //========= 마스터, 슬레이브  기어비로 구동 함수 ====================================================================
    // Electric Gear 모드에서 Master 축과 Slave 축과의 기어비를 설정한다.
    // dSlaveRatio : 마스터축에 대한 슬레이브의 기어비( 0 : 0% , 0.5 : 50%, 1 : 100%)
    function AxmLinkSetMode (lMasterAxisNo : LongInt; lSlaveAxisNo : LongInt; dSlaveRatio : Double) : DWord; stdcall;
    // Electric Gear 모드에서 설정된 Master 축과 Slave 축과의 기어비를 반환한다.
    function AxmLinkGetMode (lMasterAxisNo : LongInt; lpSlaveAxisNo : PLongInt; dpGearRatio : PDouble) : DWord; stdcall;
    // Master 축과 Slave축간의 전자기어비를 설정 해제 한다.
    function AxmLinkResetMode (lMasterAxisNo : LongInt) : DWord; stdcall;

    //======== 겐트리 관련 함수==========================================================================================
    // Master 축을 Gantry 제어로 설정해 Slave 축을 Master 축과 동기화한다.
    // 이 함수를 이용하여 Master 축을 겐트리 제어로 설정하면 해당 Slave 축은 Master 축과 동기되어 구동됩니다.
    // Gantry 제어 기능을 활성화시킨 이후 Slave 축에 구동이나 정지 명령 등을 내려도 모두 무시됩니다.
	// *주의* AxmGantrySetEnable 함수는 Master 축과 Slave 축의 ServoOn 상태가 동일할 때만 정상 설정이 가능합니다.
	// (예시1) Master 축의 ServoOn 상태: FALSE, Slave 축의 ServoOn 상태: FALSE -> Gantry 설정 가능
	// (예시2) Master 축의 ServoOn 상태: TRUE , Slave 축의 ServoOn 상태: FALSE -> Gantry 설정 불가
	// (예시3) Master 축의 ServoOn 상태: FALSE, Slave 축의 ServoOn 상태: TRUE  -> Gantry 설정 불가
	// (예시4) Master 축의 ServoOn 상태: TRUE , Slave 축의 ServoOn 상태: TRUE  -> Gantry 설정 가능
    // uSlHomeUse     : Master와 같이 Slave 축도 원점 검색을 할 것인지 선택 (0 - 2)
    //             (0 : Master 축만 원점 검색한다.)
    //             (1 : Master 축과 Slave 축 모두 원점 검색한다. 단, Slave 축에 dSlOffset 값을 적용하여 보정한다.)
    //             (2 : Master 축과 Slave 축의 Sensor 오차 값을 확인한다.)
    // dSlOffset      : Master 축의 원점 Sensor와 Slave 축의 원점 Sensor 간의 기구적인 오차 값
    // dSlOffsetRange : 원점 검색 시 Master 축의 원점 Sensor와 Slave 축의 원점 Sensor 간 허용할 최대 오차 값
    // PCI-Nx04 사용 시 주의사항: Gantry ENABLE 시 Slave 축은 모션 중 AxmStatusReadMotion 함수로 확인하면 True(Motion 구동 중)로 확인되어야 정상 동작이다.
    //							  Slave 축을 AxmStatusReadMotion 함수로 확인했을 때, InMotion이 False면 Gantry ENABLE이 되지 않은 것이므로 Alarm 혹은 Limit Sensor 등을 확인한다.
    function AxmGantrySetEnable (lMasterAxisNo : LongInt; lSlaveAxisNo : LongInt; uSlHomeUse : DWord; dSlOffset : Double; dSlOffsetRange : Double) : DWord; stdcall;

    // Slave축의 Offset값을 알아내는방법.
    // A. 마스터, 슬레이브를 모두 서보온을 시킨다.
    // B. AxmGantrySetEnable함수에서 uSlHomeUse = 2로 설정후 AxmHomeSetStart함수를 이용해서 홈을 찾는다.
    // C. 홈을 찾고 나면 마스터축의 Command값을 읽어보면 마스터축과 슬레이브축의 틀어진 Offset값을 볼수있다.
    // D. Offset값을 읽어서 AxmGantrySetEnable함수의 dSlOffset인자에 넣어준다.
    // E. dSlOffset값을 넣어줄때 마스터축에 대한 슬레이브 축 값이기때문에 부호를 반대로 -dSlOffset 넣어준다.
    // F. dSIOffsetRange 는 Slave Offset의 Range 범위를 말하는데 Range의 한계를 지정하여 한계를 벗어나면 에러를 발생시킬때 사용한다.
    // G. AxmGantrySetEnable함수에 Offset값을 넣어줬으면  AxmGantrySetEnable함수에서 uSlHomeUse = 1로 설정후 AxmHomeSetStart함수를 이용해서 홈을 찾는다.

    // 겐트리 구동에 있어 사용자가 설정한 파라메타를 반환한다.
    function AxmGantryGetEnable (lMasterAxisNo : LongInt; upSlHomeUse : PDWord; dpSlOffset : PDouble; dpSlORange : PDouble; upGatryOn : PDWord) : DWord; stdcall;
    // 모션 모듈은 두 축이 기구적으로 Link되어있는 겐트리 구동시스템 제어를 해제한다.
    function AxmGantrySetDisable (lMasterAxisNo : LongInt; lSlaveAxisNo : LongInt) : DWord; stdcall;

    // PCI-Rxx04-MLII 전용.
    // 모션 모듈은 두 축이 기구적으로 Link되어있는 겐트리 구동시스템 제어 중 동기 보상 기능을 설정한다.
    // lMasterGain, lSlaveGain : 두 축간 위치 편차에 대한 보상 값 반영 비율을 % 값으로 입력한다.
    // lMasterGain, lSlaveGain : 0을 입력하면 두 축간 위치 편차 보상 기능을 사용하지 않음. 기본값 : 0%
    function AxmGantrySetCompensationGain (lMasterAxisNo : LongInt; lMasterGain : LongInt; lSlaveGain : LongInt) : DWord; stdcall;
    // 모션 모듈은 두 축이 기구적으로 Link되어있는 겐트리 구동시스템 제어 중 동기 보상 기능을 설정을 확인한다.
    function AxmGantryGetCompensationGain (lMasterAxisNo : LongInt; lpMasterGain : PLongInt; lpSlaveGain : PLongInt) : DWord; stdcall;

    // Master 와 Slave 간 위치편차 범위를 설정 하고 위치편차범위 이상이면 Read 함수의 Status에 TRUE를 반환 한다.
    // PCI-R1604 / PCI-R3200-MLIII 전용 함수
    // lMasterAxisNo : Gantry Master Axis No
    // dErrorRange : 위치편차 범위 설정 값
    // uUse : 모드 설정
    //      ( 0 : Disable)
    //      ( 1 : Normal 모드)
    //      ( 2 : Flag Latch 모드)
    //      ( 3 : Flag Latch 모드 + Error 발생시 SSTOP)
    //      ( 4 : Flag Latch 모드 + Error 발생시 ESTOP)
    function AxmGantrySetErrorRange (lMasterAxisNo : LongInt; dErrorRange : Double; uUse : DWord) : DWord; stdcall;
    // Master 와 Slave 간의 위치편차 범위 설정값을 반환한다.
    function AxmGantryGetErrorRange (lMasterAxisNo : LongInt; dpErrorRange : PDouble; upUse : PDWord) : DWord; stdcall;
    // Master 와 Slave 간의 위치편차값 비교 결과를 반환 한다.
    // dwpStatus : FALSE(0) -> Master 와 Slave 사이의 위치편차의 범위가 설정한 범위 보다 작다. (정상상태)
    //             TRUE(1) -> Master 와 Slave 사이의 위치편차의 범위가 설정한 범위 보다 크다. (비정상상태)
    // Gantry Enable && Master/Slave Servo On 상태를 만족 할 때만 AXT_RT_SUCCESS를 Return 한다.
    // Latch 모드의 경우 AxmGantryReadErrorRangeComparePos를 호출 해야 Latch Flag가 Reset 된다.
    function AxmGantryReadErrorRangeStatus (lMasterAxisNo : LongInt; dwpStatus : PDWord) : DWord; stdcall;
    // Master 와 Slave 간의 위치편차값을 반환 한다.
    // Flag Latch 모드 일때 다음 Error가 발생 되기 전까지 이전 Error가 발생 했을 때의 위치편차값을 유지 한다.
    // dwpStatus 가 1일 때만 Read 해야 한다. 계속 ComparePos 를 Read 하면 부하가 많이 걸려 함수 응답속도가 느려지게 된다.
    function AxmGantryReadErrorRangeComparePos (lMasterAxisNo : LongInt; dpComparePos : PDouble) : DWord; stdcall;

    //====일반 보간함수 =================================================================================================
    // 주의사항1: AxmContiSetAxisMap함수를 이용하여 축맵핑후에 낮은순서축부터 맵핑을 하면서 사용해야된다.
    //           원호보간의 경우에는 반드시 낮은순서축부터 축배열에 넣어야 동작 가능하다.

    // 주의사항2: 위치를 설정할경우 반드시 마스터축과 슬레이브 축의 UNIT/PULSE의 맞추어서 설정한다.
    //           위치를 UNIT/PULSE 보다 작게 설정할 경우 최소단위가 UNIT/PULSE로 맞추어지기때문에 그위치까지 구동이 될수없다.

    // 주의사항3: 원호 보간을 할경우 반드시 한칩내에서 구동이 될수있으므로
    //            4축내에서만 선택해서 사용해야된다.

    // 주의사항4: 보간 구동 시작/중에 비정상 정지 조건(+- Limit신호, 서보 알람, 비상정지 등)이 발생하면
    //            구동 방향에 상관없이 구동을 시작하지 않거나 정지 된다.

    // 직선 보간 한다.
    // 시작점과 종료점을 지정하여 다축 직선 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 시작점과 종료점을 지정하여 직선 보간 구동하는 Queue에 저장함수가된다.
    // 직선 프로파일 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    function AxmLineMove (lCoord : LongInt; dpEndPos : PDouble; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 2축 단위 직선 보간 한다.(Software 방식)
    // 시작점과 종료점을 지정하여 다축 직선 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    function AxmLineMoveEx2 (lCoord : LongInt; dpEndPos : PDouble; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 2축 원호보간 한다.
    // 시작점, 종료점과 중심점을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode, 와 같이사용시 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 구동하는 원호 보간 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dCenterPos = 중심점 X,Y 배열 , dEndPos = 종료점 X,Y 배열.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmCircleCenterMove (lCoord : LongInt; lAxisNo : PLongInt; dCenterPos : PDouble; dEndPos : PDouble; dVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord) : DWord; stdcall;

    // 중간점, 종료점을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 중간점, 종료점을 지정하여 구동하는 원호 보간 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dMidPos = 중간점 X,Y 배열 , dEndPos = 종료점 X,Y 배열, lArcCircle = 아크(0), 원(1)
    function AxmCirclePointMove (lCoord : LongInt; lAxisNo : PLongInt; dMidPos : PDouble; dEndPos : PDouble; dVel : Double; dAccel : Double; dDecel : Double; lArcCircle : LongInt) : DWord; stdcall;

    // 시작점, 종료점과 반지름을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 원호 보간 구동하는 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dRadius = 반지름, dEndPos = 종료점 X,Y 배열 , uShortDistance = 작은원(0), 큰원(1)
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmCircleRadiusMove (lCoord : LongInt; lAxisNo : PLongInt; dRadius : Double; dEndPos : PDouble; dVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord) : DWord; stdcall;

    // 시작점, 회전각도와 반지름을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 시작점, 회전각도와 반지름을 지정하여 원호 보간 구동하는 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dCenterPos = 중심점 X,Y 배열 , dAngle = 각도.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmCircleAngleMove (lCoord : LongInt; lAxisNo : PLongInt; dCenterPos : PDouble; dAngle : Double; dVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord) : DWord; stdcall;

    //====연속 보간 함수 ================================================================================================
    //지정된 좌표계에 연속보간 축 맵핑을 설정한다.
    //(축맵핑 번호는 0 부터 시작))
    // 주의점:  축맵핑할때는 반드시 실제 축번호가 작은 숫자부터 큰숫자를 넣는다.
    //          가상축 맵핑 함수를 사용하였을 때 가상축번호를 실제 축번호가 작은 값 부터 lpAxesNo의 낮은 인텍스에 입력하여야 한다.
    //          가상축 맵핑 함수를 사용하였을 때 가상축번호에 해당하는 실제 축번호가 다른 값이라야 한다.
    //          같은 축을 다른 Coordinate에 중복 맵핑하지 말아야 한다.
    function AxmContiSetAxisMap (lCoord : LongInt; lSize : LongInt; lpAxesNo : PLongInt) : DWord; stdcall;
    //지정된 좌표계에 연속보간 축 맵핑을 반환한다.
    function AxmContiGetAxisMap (lCoord : LongInt; lpSize : PLongInt; lpAxesNo : PLongInt) : DWord; stdcall;
    //지정된 좌표계에 연속보간 축 맵핑을 초기화한다.
    function AxmContiResetAxisMap (lCoordinate : LongInt) : DWord; stdcall;

    // 지정된 좌표계에 연속보간 축 절대/상대 모드를 설정한다.
    // (주의점 : 반드시 축맵핑 하고 사용가능)
    // 지정 축의 이동 거리 계산 모드를 설정한다.
    //uAbsRelMode : POS_ABS_MODE '0' - 절대 좌표계
    //              POS_REL_MODE '1' - 상대 좌표계
    function AxmContiSetAbsRelMode (lCoord : LongInt; uAbsRelMode : DWord) : DWord; stdcall;
    // 지정된 좌표계에 연속보간 축 절대/상대 모드를 반환한다.
    function AxmContiGetAbsRelMode (lCoord : LongInt; upAbsRelMode : PDWord) : DWord; stdcall;

    // 지정된 좌표계에 보간 구동을 위한 내부 Queue가 비어 있는지 확인하는 함수이다.
    function AxmContiReadFree (lCoord : LongInt; upQueueFree : PDWord) : DWord; stdcall;
    // 지정된 좌표계에 보간 구동을 위한 내부 Queue에 저장되어 있는 보간 구동 개수를 확인하는 함수이다.
    function AxmContiReadIndex (lCoord : LongInt; lpQueueIndex : PLongInt) : DWord; stdcall;

    // 지정된 좌표계에 연속 보간 구동을 위해 저장된 내부 Queue를 모두 삭제하는 함수이다.
    function AxmContiWriteClear (lCoord : LongInt) : DWord; stdcall;

    // 지정된 좌표계에 연속보간에서 수행할 작업들의 등록을 시작한다. 이함수를 호출한후,
    // AxmContiEndNode함수가 호출되기 전까지 수행되는 모든 모션작업은 실제 모션을 수행하는 것이 아니라 연속보간 모션으로 등록 되는 것이며,
    // AxmContiStart 함수가 호출될 때 비로소 등록된모션이 실제로 수행된다.
    function AxmContiBeginNode (lCoord : LongInt) : DWord; stdcall;
    // 지정된 좌표계에서 연속보간을 수행할 작업들의 등록을 종료한다.
    function AxmContiEndNode (lCoord : LongInt) : DWord; stdcall;

    // 연속 보간 시작 한다.
    // dwProfileset(CONTI_NODE_VELOCITY(0) : 연속 보간 사용, CONTI_NODE_MANUAL(1) : 프로파일 보간 사용, CONTI_NODE_AUTO(2) : 자동 프로파일 보간, 3 : 속도보상 모드 사용)
    function AxmContiStart (lCoord : LongInt; dwProfileset : DWord; lAngle : LongInt) : DWord; stdcall;
    // 지정된 좌표계에 연속 보간 구동 중인지 확인하는 함수이다.
    function AxmContiIsMotion (lCoord : LongInt; upInMotion : PDWord) : DWord; stdcall;

    // 지정된 좌표계에 연속 보간 구동 중 현재 구동중인 연속 보간 인덱스 번호를 확인하는 함수이다.
    function AxmContiGetNodeNum (lCoord : LongInt; lpNodeNum : PLongInt) : DWord; stdcall;
    // 지정된 좌표계에 설정한 연속 보간 구동 총 인덱스 갯수를 확인하는 함수이다.
    function AxmContiGetTotalNodeNum (lCoord : LongInt; lpNodeNum : PLongInt) : DWord; stdcall;

    // 특정 모션 세그먼트에서 I/O출력
    // AxmContiBeginNode 함수와 AxmContiEndNode 함수 사이에서 사용하여야 된다.
    // 다음 연속 보간 구동 함수(ex: AxmLineMove, AxmCircleCenterMove, etc...)에 대해서만 유효하다.
    // Digital I/O 출력 시점은 다음 연속 보간 구동함수의 종점을 기준으로 조건(dpDistTime, lpDistTimeMode)만큼 이전에 출력한다.
    //
    // lSize :  동시에 출력할 IO 접점 수 (1 ~ 8)
    // lModuleNo : dwModuleType=0 일때 는 축번호, dwModuleType=1일 경우는 Digital I/O Module No.
    // dwModuleType : 0=Motion I/O Output(Slave 자체의 출력), 1=Digital I/O Output
    //
    // % 아래 4개의 매개 변수는 lSize 만큼의 배열로 입력해서 여러 출력 접점을 동시에 제어할 수 있다.
    // lpBit : 출력 접점에 대한 Offset 위치
    // lpOffOn : 해당 출력 접점의 출력값 [LOW(0), HIGH(1)]
    // dpDistTime : 거리 값(pulse), 시간 값(msec) => 모션 프로파일 종점을 기준으로 한다.
    // lpDistTimeMode : 0=거리 모드, 1=시간모드 => 모션 프로파일 종점을 기준으로 한다.
    function AxmContiDigitalOutputBit (lCoord : LongInt; lSize : LongInt; lModuleType : LongInt; lpModuleNo : PLongInt; lpBit : PLongInt; lpOffOn : PLongInt; dpDistTime : PDouble; lpDistTimeMode : PLongInt) : DWord; stdcall;

    function AxmContiSetConnectionRadius (lCoord : LongInt; dRadius : Double) : DWord; stdcall;

    //====================트리거 함수 ===================================================================================
    // 주의사항:트리거 위치를 설정할경우 반드시 UNIT/PULSE의 맞추어서 설정한다.
    //            위치를 UNIT/PULSE 보다 작게할 경우 최소단위가 UNIT/PULSE로 맞추어지기때문에 그위치에 출력할수없다.

    // 지정 축에 트리거 기능의 사용 여부, 출력 레벨, 위치 비교기, 트리거 신호 지속 시간 및 트리거 출력 모드를 설정한다.
    // 트리거 기능 사용을 위해서는 먼저  AxmTriggerSetTimeLevel 를 사용하여 관련 기능 설정을 먼저 하여야 한다.
    // dTrigTime       : 트리거 출력 시간, 1usec - 최대 50msec ( 1 - 50000 까지 설정)
    // upTriggerLevel  : 트리거 출력 레벨 유무  => LOW(0),     HIGH(1)
    // uSelect         : 사용할 기준 위치       => COMMAND(0), ACTUAL(1)
    // uInterrupt      : 인터럽트 설정          => DISABLE(0), ENABLE(1)

    // 지정 축에 트리거 신호 지속 시간 및 트리거 출력 레벨, 트리거 출력방법을 설정한다.
    function AxmTriggerSetTimeLevel (lAxisNo : LongInt; dTrigTime : Double; uTriggerLevel : DWord; uSelect : DWord; uInterrupt : DWord) : DWord; stdcall;
    // 지정 축에 트리거 신호 지속 시간 및 트리거 출력 레벨, 트리거 출력방법을 반환한다.
    function AxmTriggerGetTimeLevel (lAxisNo : LongInt; dpTrigTime : PDouble; upTriggerLevel : PDWord; upSelect : PDWord; upInterrupt : PDWord) : DWord; stdcall;

    // 지정 축의 트리거 출력 기능을 설정한다.
    // uMethod: PERIOD_MODE  0x0 : 현재 위치를 기준으로 dPos를 위치 주기로 사용한 주기 트리거 방식
    //          ABS_POS_MODE 0x1 : 트리거 절대 위치에서 트리거 발생, 절대 위치 방식
    // dPos : 주기 선택시 : 위치마다위치마다 출력하기때문에 그 위치
    //        절대 선택시 : 출력할 그 위치, 이 위치와같으면 무조건 출력이 나간다.
    // 주의사항: AxmTriggerSetAbsPeriod의 주기모드로 설정할경우 처음 그위치가 범위 안에 있으므로 트리거 출력이 한번 발생한다.
    function AxmTriggerSetAbsPeriod (lAxisNo : LongInt; uMethod : DWord; dPos : Double) : DWord; stdcall;
    // 지정 축에 트리거 기능의 사용 여부, 출력 레벨, 위치 비교기, 트리거 신호 지속 시간 및 트리거 출력 모드를 반환한다.
    function AxmTriggerGetAbsPeriod (lAxisNo : LongInt; upMethod : PDWord; dpPos : PDouble) : DWord; stdcall;

    // 사용자가 지정한 시작위치부터 종료위치까지 일정구간마다 트리거를 출력 한다.
    function AxmTriggerSetBlock (lAxisNo : LongInt; dStartPos : Double; dEndPos : Double; dPeriodPos : Double) : DWord; stdcall;
    // 'AxmTriggerSetBlock' 함수의 설정한 값을 읽는다..
    function AxmTriggerGetBlock (lAxisNo : LongInt; dpStartPos : PDouble; dpEndPos : PDouble; dpPeriodPos : PDouble) : DWord; stdcall;

    // 사용자가 한 개의 트리거 펄스를 출력한다.
    function AxmTriggerOneShot (lAxisNo : LongInt) : DWord; stdcall;
    // 사용자가 한 개의 트리거 펄스를 지정 시간 후에 출력한다.
    function AxmTriggerSetTimerOneshot (lAxisNo : LongInt; lmSec : LongInt) : DWord; stdcall;
    // 입력한 절대위치값의 순서로 해당 위치를 지날때 트리거 신호를 출력한다.
    function AxmTriggerOnlyAbs (lAxisNo : LongInt; lTrigNum : LongInt; dpTrigPos : PDouble) : DWord; stdcall;
    // 트리거 기능 설정을 초기화 한다.
    function AxmTriggerSetReset (lAxisNo : LongInt) : DWord; stdcall;

    // 지정한 위치에서 트리거 신호 출력을 시작/종료한다.(반복사용 시 함수 재호출 필요)
    // AxmTriggerSetTimeLevel 함수로 설정된 uTriggerLevel, uSelect 값을 기준으로 동작(dTrigTime 및 uInterrupt 값은 사용되지 않음)
    // dStartpos  : 트리거 출력을 시작하는 위치
    // dEndPos   : 트리거 출력을 종료하는 위치
    function AxmTriggerSetPoint (lAxisNo : LongInt; dStartPos : Double; dEndPos : Double) : DWord; stdcall;

    // AxmTriggerSetPoint 함수로 설정한 값을 확인한다.
    // dStartpos  : 트리거 출력을 시작하는 위치
    // dEndPos   : 트리거 출력을 종료하는 위치
    function AxmTriggerGetPoint (lAxisNo : LongInt; dpStrPosition : PDouble; dpEndPos : PDouble) : DWord; stdcall;

    // AxmTriggerSetPoint 함수로 설정한 위치를 초기화한다.
    // 트리거 출력 도중 함수를 호출한 경우 트리거 출력을 종료한다.
    function AxmTriggerSetPointClear (lAxisNo : LongInt) : DWord; stdcall;

    //======== CRC( 잔여 펄스 클리어 함수)===============================================================================
    //Level   : LOW(0), HIGH(1), UNUSED(2), USED(3)
    //uMethod : 잔여펄스 제거 출력 신호 펄스 폭 2 - 6까지 설정가능.(PCI-Nx04 전용 함수)
    //          0 : Don't care, 1 : Don't care, 2: 500 uSec, 3:1 mSec, 4:10 mSec, 5:50 mSec, 6:100 mSec
    //지정 축에 CRC 신호 사용 여부 및 출력 레벨을 설정한다.
    function AxmCrcSetMaskLevel (lAxisNo : LongInt; uLevel : DWord; uMethod : DWord) : DWord; stdcall;
    // 지정 축의 CRC 신호 사용 여부 및 출력 레벨을 반환한다.
    function AxmCrcGetMaskLevel (lAxisNo : LongInt; upLevel : PDWord; upMethod : PDWord) : DWord; stdcall;

    //uOnOff  : CRC 신호를 Program으로 발생 여부  (FALSE(0),TRUE(1))
    // 지정 축에 CRC 신호를 강제로 발생 시킨다.
    function AxmCrcSetOutput (lAxisNo : LongInt; uOnOff : DWord) : DWord; stdcall;
    // 지정 축의 CRC 신호를 강제로 발생 여부를 반환한다.
    function AxmCrcGetOutput (lAxisNo : LongInt; upOnOff : PDWord) : DWord; stdcall;

    //======MPG(Manual Pulse Generation) 함수============================================================================
    // lInputMethod  : 0-3 까지 설정가능. 0:OnePhase, 1:TwoPhase1(IP만가능, QI지원안함) , 2:TwoPhase2, 3:TwoPhase4
    // lDriveMode    : 0만 설정가능(0 :MPG 연속모드)
    // MPGPos        : MPG 입력신호마다 이동하는 거리
    // MPGdenominator: MPG(수동 펄스 발생 장치 입력)구동 시 나누기 값
    // dMPGnumerator : MPG(수동 펄스 발생 장치 입력)구동 시 곱하기 값
    // dwNumerator   : 최대(1 에서    64) 까지 설정 가능
    // dwDenominator : 최대(1 에서  4096) 까지 설정 가능
    // dMPGdenominator = 4096, MPGnumerator=1 가 의미하는 것은
    // MPG 한바퀴에 200펄스면 그대로 1:1로 1펄스씩 출력을 의미한다.
    // 만약 dMPGdenominator = 4096, MPGnumerator=2 로 했을경우는 1:2로 2펄스씩 출력을 내보낸다는의미이다.
    // 여기에 MPG PULSE = ((Numerator) * (Denominator)/ 4096 ) 칩내부에 출력나가는 계산식이다.
    // 주의사항     : AxmStatusReadInMotion 함수 실행 결과에 유의한다.  (AxmMPGReset 하기 전까지 정상 상태에서는 모션 구동 중 상태.)

    // 지정 축에 MPG 입력방식, 드라이브 구동 모드, 이동 거리, MPG 속도 등을 설정한다.
    function AxmMPGSetEnable (lAxisNo : LongInt; lInputMethod : LongInt; lDriveMode : LongInt; dMPGPos : Double; dVel : Double; dAccel : Double) : DWord; stdcall;
    // 지정 축에 MPG 입력방식, 드라이브 구동 모드, 이동 거리, MPG 속도 등을 반환한다.
    function AxmMPGGetEnable (lAxisNo : LongInt; lpInputMethod : PLongInt; lpDriveMode : PLongInt; dpMPGPos : PDouble; dpVel : PDouble; dAccel : PDouble) : DWord; stdcall;

    // PCI-Nx04 함수 전용.
    // 지정 축에 MPG 드라이브 구동 모드에서 한펄스당 이동할 펄스 비율을 설정한다.
    function AxmMPGSetRatio (lAxisNo : LongInt; uMPGnumerator : DWord; uMPGdenominator : DWord) : DWord; stdcall;
    // 지정 축에 MPG 드라이브 구동 모드에서 한펄스당 이동할 펄스 비율을 반환한다.
    function AxmMPGGetRatio (lAxisNo : LongInt; upMPGnumerator : PDWord; upMPGdenominator : PDWord) : DWord; stdcall;
    // 지정 축에 MPG 드라이브 설정을 해지한다.
    function AxmMPGReset (lAxisNo : LongInt) : DWord; stdcall;

    //======= 헬리컬 이동 ===============================================================================================
    // 주의사항 : Helix를 연속보간 사용시 Spline, 직선보간과 원호보간을 같이 사용할수없다.

    // 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 헬리컬 보간 구동하는 함수이다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 헬리컬 연속보간 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다)
    // dCenterPos = 중심점 X,Y  , dEndPos = 종료점 X,Y .
    // uCWDir DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmHelixCenterMove (lCoord : LongInt; dCenterXPos : Double; dCenterYPos : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord) : DWord; stdcall;

    // 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 헬리컬 보간 구동하는 함수이다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 중간점, 종료점을 지정하여 헬리컬연속 보간 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다.)
    // dMidPos = 중간점 X,Y  , dEndPos = 종료점 X,Y
    function AxmHelixPointMove (lCoord : LongInt; dMidXPos : Double; dMidYPos : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;

    // 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 헬리컬 보간 구동하는 함수이다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 헬리컬연속 보간 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다.)
    // dRadius = 반지름, dEndPos = 종료점 X,Y  , uShortDistance = 작은원(0), 큰원(1)
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmHelixRadiusMove (lCoord : LongInt; dRadius : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord) : DWord; stdcall;

    // 지정된 좌표계에 시작점, 회전각도와 반지름을 지정하여 헬리컬 보간 구동하는 함수이다
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 시작점, 회전각도와 반지름을 지정하여 헬리컬연속 보간 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다.)
    //dCenterPos = 중심점 X,Y  , dAngle = 각도.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmHelixAngleMove (lCoord : LongInt; dCenterXPos : Double; dCenterYPos : Double; dAngle : Double; dZPos : Double; dVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord) : DWord; stdcall;

    // 임의의 축을 중심으로 회전하는 헬리컬 보간 구동을 지원한다.
    // dpFirstCenterPos=중심위치, dpSecondCenterPos=반대편 중심위치, dPicth=이동량(mm)/1Revolution, dTraverseDistance=이동량(mm)
    // dpFirstCenterPos에서 dpSecondCenterPos를 잇는 직선이 회전 축이 된다. 중심직선(dpFirstCenterPos-->dpSecondCenterPos)와 시작위치까지의 직선(dpFirstCenterPos-->시작위치)는 서로 수직이다.
    // dTraverseDistance은 시작 위치에서 회전 축과 평행한 직선의 거리이다.
    // 축 매핑은 3축 이상 가능하며 3축 이상의 축들은 Linear Interpolation 된다.
    function AxmHelixPitchMove (lCoordNo : LongInt; dpFirstCenterPos : PDouble; dpSecondCenterPos : PDouble; dPitch : Double; dTraverseDistance : Double; dVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord) : DWord; stdcall;

    //======== 스플라인 이동 (PCI-Nx04 전용 함수)========================================================================
    // 주의사항 : Spline를 연속보간 사용시 Helix , 직선보간과 원호보간을 같이 사용할수없다.

    // AxmContiBeginNode, AxmContiEndNode와 같이사용안함.
    // 스플라인 연속 보간 구동하는 함수이다. 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다.
    // AxmContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다.)
    // lPosSize : 최소 3개 이상.
    // 2축으로 사용시 dPoZ값을 0으로 넣어주면 됨.
    // 3축으로 사용시 축맵핑을 3개및 dPosZ 값을 넣어준다.
    function AxmSplineWrite (lCoord : LongInt; lPosSize : LongInt; dpPosX : PDouble; dpPosY : PDouble; dVel : Double; dAccel : Double; dDecel : Double; dPosZ : Double; lPointFactor : LongInt) : DWord; stdcall;

    //======== PCI-R1604-MLII/SIIIH, PCIe-Rxx04-SIIIH 전용 함수 ==================================================================================
    // 위치 보정 테이블 기능에 필요한 내용을 설정한다.
    function AxmCompensationSet (lAxisNo : LongInt; lNumEntry : LongInt; dStartPos : Double; dpPosition : PDouble; dpCorrection : PDouble; dwRollOver : DWord) : DWord; stdcall;
    // 위치 보정 테이블 기능 설정 내용을 반환한다.
    function AxmCompensationGet (lAxisNo : LongInt; lpNumEntry : PLongInt; dpStartPos : PDouble; dpPosition : PDouble; dpCorrection : PDouble; dwpRollOver : PDWord) : DWord; stdcall;

    // 위치 보정 테이블 기능의 사용유부를 설정한다.
    function AxmCompensationEnable (lAxisNo : LongInt; dwEnable : DWord) : DWord; stdcall;
    // 위치 보정 테이블 기능의 사용유무에 대한 설정 상태를 반환한다.
    function AxmCompensationIsEnable (lAxisNo : LongInt; dwpEnable : PDWord) : DWord; stdcall;
    // 현재 지령 위치에서의 보정값을 반환한다.
    function AxmCompensationGetCorrection (lAxisNo : LongInt; dpCorrection : PDouble) : DWord; stdcall;

    // Backlash에 관련된 설정을하는 함수
    // > lBacklashDir: Backlash 보상을 적용할 구동 방향을 설정 (원점검색 방향과 동일하게 설정함)
    //   - [0] -> Command Position값이 (+)방향으로 구동할 때 지정한 backlash를 적용함
    //   - [1] -> Command Position값이 (-)방향으로 구동할 때 지정한 backlash를 적용함
    //   - Ex1) lBacklashDir이 0, backlash가 0.01일 때 0.0 -> 100.0으로 위치이동 할 때 실제 이동하는 위치는 100.01이됨
    //   - Ex2) lBacklashDir이 0, backlash가 0.01일 때 0.0 -> -100.0으로 위치이동 할 때 실제 이동하는 위치는 -100.0이됨
    //   ※ NOTANDUM
    //   - 정확한 Backlash보상을 위해서는 원점검색시 마지막에 Backlash양 만큼 (+)Or(-)방향으로 이동 한 후 원점을 완료하고
    //     Backlash보정을 사용한다. 이 때 Backlash양 만큼 (+)구동을 했다면 backlash_dir을 [1](-)로, (-)구동을 했다면
    //     backlash_dir을 [0](+)로 설정하면 된다.
    // > dBacklash: 기구부에서 진행 방향과 반대반향으로 방향전환시 발생되는 Backlash양을 설정함
    // { RETURN VALUE }
    //   - [0] -> Backlash 설정이 성공했을 때
    function AxmCompensationSetBacklash (lAxisNo : LongInt; lBacklashDir : LongInt; dBacklash : Double) : DWord; stdcall;
    // Backlash에 관련된 설정 내용을 반환한다.
    function AxmCompensationGetBacklash (lAxisNo : LongInt; lpBacklashDir : PLongInt; dpBacklash : PDouble) : DWord; stdcall;
    // Backlash사용유무를 설정/확인하는 함수
    // > dwEnable: Backlash보정 사용유무를 지정
    //   - [0]DISABLE -> Backlash보정을 사용안함
    //   - [1]ENABLE  -> Backlash보정을 사용함
    // { RETURN VALUE }
    //   - [0]    -> Backlash 설정반환이 성공했을 때
    //   - [4303] -> Backlash 보정기능이 설정되어있지않을 때
    function AxmCompensationEnableBacklash (lAxisNo : LongInt; dwEnable : DWord) : DWord; stdcall;
    function AxmCompensationIsEnableBacklash (lAxisNo : LongInt; dwpEnable : PDWord) : DWord; stdcall;
    // Backlash보정기능을 사용할 때 Backlash양 만큼 좌우로 이동하여 기구물의 위치를 자동 정렬함(서보 온 동작 이후 한번 사용함)
    // > dVel: 이동 속도[unit / sec]
    // > dAccel: 이동가속도[unit / sec^2]
    // > dAccel: 이동감속도[unit / sec^2]
    // > dWaitTime: Backlash 양만큼 구동 후 원래의 위치로 되돌아올기 까지의 대기시간[msec]
    // { RETURN VALUE }
    //   - [0]    -> Backlash 보정을 위한 위치설정이 성공했을 때
    //   - [4303] -> Backlash 보정기능이 설정되어있지않을 때
    function AxmCompensationSetLocating (lAxisNo : LongInt; dVel : Double; dAccel : Double; dDecel : Double; dWaitTime : Double) : DWord; stdcall;

    // ECAM 기능에 필요한 내용을 설정한다.
    function AxmEcamSet (lAxisNo : LongInt; lMasterAxis : LongInt; lNumEntry : LongInt; dMasterStartPos : Double; dpMasterPos : PDouble; dpSlavePos : PDouble) : DWord; stdcall;
    // ECAM 기능에 필요한 내용을 CMD/ACT Source와 함께 설정한다. (PCIe-Rxx04-SIIIH 전용 함수)
    function AxmEcamSetWithSource (lAxisNo : LongInt; lMasterAxis : LongInt; lNumEntry : LongInt; dMasterStartPos : Double; dpMasterPos : PDouble; dpSlavePos : PDouble; dwSource : DWord) : DWord; stdcall;
    // ECAM 기능 설정 내용을 반환한다.
    function AxmEcamGet (lAxisNo : LongInt; lpMasterAxis : PLongInt; lpNumEntry : PLongInt; dpMasterStartPos : PDouble; dpMasterPos : PDouble; dpSlavePos : PDouble) : DWord; stdcall;
    // ECAM 기능 설정 내용을 CMD/ACT Source와 함께 반환한다. (PCIe-Rxx04-SIIIH 전용 함수)
    function AxmEcamGetWithSource (lAxisNo : LongInt; lpMasterAxis : PLongInt; lpNumEntry : PLongInt; dpMasterStartPos : PDouble; dpMasterPos : PDouble; dpSlavePos : PDouble; dwpSource : PDWord) : DWord; stdcall;

    // ECAM 기능의 사용 유무를 설정한다.
    function AxmEcamEnableBySlave (lAxisNo : LongInt; dwEnable : DWord) : DWord; stdcall;
    // ECAM 기능의 사용 유무를 지정한 Master 축에 연결된 모든 Slave 축에 대하여 설정한다.
    function AxmEcamEnableByMaster (lAxisNo : LongInt; dwEnable : DWord) : DWord; stdcall;
    // ECAM 기능의 사용 유무에 대한 설정 상태를 반환한다.
    function AxmEcamIsSlaveEnable (lAxisNo : LongInt; dwpEnable : PDWord) : DWord; stdcall;

    //======== Servo Status Monitor =====================================================================================
    // 지정 축의 예외 처리 기능에 대해 설정한다.(MLII : Sigma-5, SIIIH : MR_J4_xxB 전용)
    // dwSelMon(0~3): 감시 정보 선택.
    //          [0] : Torque
    //          [1] : Velocity of motor
    //          [2] : Accel. of motor
    //          [3] : Decel. of motor
    //          [4] : Position error between Cmd. position and Act. position.
    // dwActionValue: 이상 동작 판정 기준 값 설정. 각 정보에 따라 설정 값의 의미가 다음.
    //          [0] : dwSelMon에서 선택한 감시 정보에 대하여 예외 처리 하지 않음.
    //         [>0] : dwSelMon에서 선택한 감시 정보에 대하여 예외 처리 기능 적용.
    // dwAction(0~3): dwActionValue 이상으로 감시 정보가 확인되었을때 예외처리 방법 설정.
    //          [0] : Warning(setting flag only)
    //          [1] : Warning(setting flag) + Slow-down stop
    //          [2] : Warning(setting flag) + Emergency stop
    //          [3] : Warning(setting flag) + Emergency stop + Servo-Off
    // ※ 주의: 5개의 SelMon 정보에 대해 각각 예외처리 설정이 가능하며, 사용중 예외처리를 원하지않을 경우
    //          반드시 해당 SelMon 정보의 ActionValue값을 0으로 설정해 감시기능을 Disable 해됨.
    function AxmStatusSetServoMonitor (lAxisNo : LongInt; dwSelMon : DWord; dActionValue : Double; dwAction : DWord) : DWord; stdcall;
    // 지정 축의 예외 처리 기능에 대한 설정 상태를 반환한다.(MLII : Sigma-5 전용)
    function AxmStatusGetServoMonitor (lAxisNo : LongInt; dwSelMon : DWord; dpActionValue : PDouble; dwpAction : PDWord) : DWord; stdcall;
    // 지정 축의 예외 처리 기능에 대한 사용 유무를 설정한다.(MLII : Sigma-5, SIIIH : MR_J4_xxB 전용)
    function AxmStatusSetServoMonitorEnable (lAxisNo : LongInt; dwEnable : DWord) : DWord; stdcall;
    // 지정 축의 예외 처리 기능에 대한 사용 유무를 반환한다.(MLII : Sigma-5 전용)
    function AxmStatusGetServoMonitorEnable (lAxisNo : LongInt; dwpEnable : PDWord) : DWord; stdcall;

    // 지정 축의 예외 처리 기능 실행 결과 플래그 값을 반환한다. 함수 실행 후 자동 초기화.(MLII : Sigma-5 전용)
    function AxmStatusReadServoMonitorFlag (lAxisNo : LongInt; dwSelMon : DWord; dwpMonitorFlag : PDWord; dpMonitorValue : PDouble) : DWord; stdcall;
    // 지정 축의 예외 처리 기능을 위한 감시 정보를 반환한다.(MLII : Sigma-5 전용)
    function AxmStatusReadServoMonitorValue (lAxisNo : LongInt; dwSelMon : DWord; dpMonitorValue : PDouble) : DWord; stdcall;
    // 지정 축의 부하율을 읽을 수 있도록 설정 합니다.(MLII : Sigma-5 / MLIII : Sigma-5, Sigma-7 / SIIIH : MR_J4_xxB / RTEX : A5N, A6N 전용)
    // (MLII, Sigma-5, dwSelMon : 0 ~ 3) ==
    //     [0] : Accumulated load ratio(%)
    //     [1] : Regenerative load ratio(%)
    //     [2] : Reference Torque load ratio
    //     [3] : Motor rotation speed (rpm)
    // (MLIII, Sigma-5, Sigma-7 dwSelMon : 0 ~ 2) ==
    //     [0] : Accumulated load ratio(%)
    //     [1] : Regenerative load ratio(%) [Sigma-7 전용]
    //     [2] : Reference Torque load ratio
    // (SIIIH, MR_J4_xxB, dwSelMon : 0 ~ 5) ==
    //     [0] : Assumed load inertia ratio(0.1times)
    //     [1] : Regeneration load factor(%)
    //     [2] : Effective load factor(%)
    //     [3] : Peak load factor(%)
    //     [4] : Current feedback(0.1%)
    //     [5] : Speed feedback(rpm)
    // (RTEX, A5Nx, A6Nx, dwSelMon : 0 ~ 6) ==
    //     [0] : Command Torque(0.1%)
    //     [1] : Regenerative load ratio(0.1%)
    //     [2] : Overload ratio(0.1%)
    //     [3] : Inertia ratio(%)
    //     [4] : Actual speed(rpm)
    //     [5] : Servo driver temperature
    //     [6] : Main power source PN Voltage
    function AxmStatusSetReadServoLoadRatio (lAxisNo : LongInt; dwSelMon : DWord) : DWord; stdcall;
    // 지정 축의 부하율을 반환한다.(MLII : Sigma-5 / MLIII : Sigma-5, Sigma-7 / SIIIH : MR_J4_xxB / RTEX : A5N, A6N 전용)
    function AxmStatusReadServoLoadRatio (lAxisNo : LongInt; dpMonitorValue : PDouble) : DWord; stdcall;

    //======== PCI-R1604-RTEX 전용 함수==================================================================================
    // RTEX A4Nx 관련 Scale Coefficient를 설정한다.(RTEX, A4Nx 전용)
    function AxmMotSetScaleCoeff (lAxisNo : LongInt; lScaleCoeff : LongInt) : DWord; stdcall;
    // RTEX A4Nx 관련 Scale Coefficient 를 확인한다.(RTEX, A4Nx 전용)
    function AxmMotGetScaleCoeff (lAxisNo : LongInt; lpScaleCoeff : PLongInt) : DWord; stdcall;

    // 특정 Input 신호의 Edge를 검출하여 즉정지 또는 감속정지하는 함수.
    // lDetect Signal : edge 검출할 입력 신호 선택.
    // lDetectSignal  : PosEndLimit(0), NegEndLimit(1), HomeSensor(4)
    // Signal Edge    : 선택한 입력 신호의 edge 방향 선택 (rising or falling edge).
    //                  SIGNAL_DOWN_EDGE(0), SIGNAL_UP_EDGE(1)
    // 구동방향       : Vel값이 양수이면 CW, 음수이면 CCW.
    // SignalMethod   : 급정지 EMERGENCY_STOP(0), 감속정지 SLOWDOWN_STOP(1)
    // 주의사항: SignalMethod를 EMERGENCY_STOP(0)로 사용할경우 가감속이 무시되며 지정된 속도로 가속 급정지하게된다.
    //           PCI-Nx04를 사용할 경우 lDetectSignal이 PosEndLimit , NegEndLimit(0,1) 을 찾을경우 신호의레벨 Active 상태를 검출하게된다.
    function AxmMoveSignalSearchEx (lAxisNo : LongInt; dVel : Double; dAccel : Double; lDetectSignal : LongInt; lSignalEdge : LongInt; lSignalMethod : LongInt) : DWord; stdcall;
    //-------------------------------------------------------------------------------------------------------------------

    //======== PCI-R1604-MLII/SIIIH, PCIe-Rxx04-SIIIH 전용 함수 ==================================================================================
    // 설정한 절대 위치로 이동한다.
    // 속도 프로파일은 사다리꼴 전용으로 구동한다.
    // 펄스가 출력되는 시점에서 함수를 벗어난다.
    // 항상 위치 및 속도, 가감속도를 변경 가능하며, 반대방향 위치 변경 기능을 포함한다.
    function AxmMoveToAbsPos (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;
    // 지정 축의 현재 구동 속도를 읽어온다.
    function AxmStatusReadVelEx (lAxisNo : LongInt; dpVel : PDouble) : DWord; stdcall;
    //-------------------------------------------------------------------------------------------------------------------

    //======== PCI-R1604-SIIIH, PCIe-Rxx04-SIIIH 전용 함수 ==================================================================================
    // 지정 축의 전자 기어비를 설정한다. 설정 후 비 휘발성 메모리에 기억됩니다.
    // 초기 값(lNumerator : 4194304(2^22), lDenominator : 10000)
    // MR-J4-B는 전자 기어비를 설정할 수 없으며, 상위 제어기에서 아래의 함수를 사용하여 설정하여야 합니다.
    // 기존 펄스 입력 방식 서보 드라이버(MR-J4-A)의 파라미터 No.PA06, No.PA07에 해당.
    // ex1) 1 um를 제어 단위로 가정. 감속기 비율 : 1/1. Rotary motor를 장착한 Linear stage.
    // Encoder resulotion = 2^22
    // Ball screw pitch : 6 mm
    // ==> lNumerator = 2^22, lDenominator = 6000(6/0.001)
    // AxmMotSetMoveUnitPerPulse에서 Unit/Pulse = 1/1로 설정하였다면, 모든 함수의 위치 단위 : um, 속도 단위 : um/sec, 가감속도 단뒤 : um/sec^2이 된다.
    // AxmMotSetMoveUnitPerPulse에서 Unit/Pulse = 1/1000로 설정하였다면, 모든 함수의 위치 단위 : mm, 속도 단위 : mm/sec, 가감속도 단뒤 : mm/sec^2이 된다.
    // ex2) 0.01도 회전을 제어 단위로 가정. 감속기 비율 : 1/1. Rotary motor를 장착한 회전체 구조물.
    // Encoder resulotion = 2^22
    // 1 회전 : 360
    // ==> lNumerator = 2^22, lDenominator = 36000(360 / 0.01)
    // AxmMotSetMoveUnitPerPulse에서 Unit/Pulse = 1/1로 설정하였다면, 모든 함수의 위치 단위 : 0.01도, 속도 단위 : 0.01도/sec, 가감속도 단뒤 : 0.01도/sec^2이 된다.
    // AxmMotSetMoveUnitPerPulse에서 Unit/Pulse = 1/100로 설정하였다면, 모든 함수의 위치 단위 : 1도, 속도 단위 : 1도/sec, 가감속도 단뒤 : 1도/sec^2이 된다.
    function AxmMotSetElectricGearRatio (lAxisNo : LongInt; lNumerator : LongInt; lDenominator : LongInt) : DWord; stdcall;
    // 지정 축의 전자 기어비 설정을 확인한다.
    function AxmMotGetElectricGearRatio (lAxisNo : LongInt; lpNumerator : PLongInt; lpDenominator : PLongInt) : DWord; stdcall;

    //======== SSCNET / RTEX Master Board 전용 함수 ==================================================================================
    // 지정 축의 토크 리미트 값을 설정 합니다.
    // 정방향, 역방향 구동시의 토크 값을 제한하는 함수.
    // SSCNET : 설정 값은 1 ~ 3000(0.1% ~ 300.0%)까지 설정
    //          최대 토크의 0.1% 단위로 제어 함.
    // RTEX   : 설정 값은 1 ~ 500 (1% ~ 500 %)까지 설정
    //          최대 토크의 1% 단위로 제어 함.
    //          * Torque Limit 기능을 사용할 축의 Servo Drive Parameter Pr5.21(토크 한계 선택 설정)을 4로 변경 후 사용해야 한다.
    // ML-III : 설정 값은 0 ~ 800 (0% ~ 800%)까지 설정
    //          Rotary Servo 앰프 모드만 지원
    //          PCI-Rxx00-MLIII 제품만 지원
    //          단위는 1%로 제어 함.
    //          * PlusDirTorqueLimit(Forwared Torque Limit)는 Servo Drive Parameter Pn402 를 설정합니다.
    //          * MinusDirTorqueLimit(Reverse Torque Limit)는 Servo Drive Parameter Pn403 을 설정합니다.
    function AxmMotSetTorqueLimit (lAxisNo : LongInt; dbPlusDirTorqueLimit : Double; dbMinusDirTorqueLimit : Double) : DWord; stdcall;

    // 지정 축의 토크 리미트 값을 확인 합니다.
    // 정방향, 역방향 구동시의 토크 값을 읽어 오는 함수.
    // 설정 값은 1 ~ 3000(0.1% ~ 300.0%)까지 설정
    // 최대 토크의 0.1% 단위로 제어 함.
    // ML-III : 설정 범위는 0 ~ 800 (0% ~ 800%)임.
    //          Rotary Servo 앰프 모드만 지원
    //          최대 토크의 단위는 1% 임.
    function AxmMotGetTorqueLimit (lAxisNo : LongInt; dbpPlusDirTorqueLimit : PDouble; dbpMinusDirTorqueLimit : PDouble) : DWord; stdcall;

    // 지정 축의 토크 리미트 값을 설정 합니다.(아래 표시된 제품만 기능 지원함)
    // ML-III : 설정 값은 0 ~ 800 (0% ~ 800%)까지 설정
    //          Liner Servo 앰프 모드만 지원(Only SGD7S, SGD7W)
    //          PCI-Rxx00-MLIII 제품만 지원
    //          단위는 1%로 제어 함.
    //          * PlusDirTorqueLimit(Forwared Torque Limit)는 Servo Drive Parameter Pn483 를 설정합니다.
    //          * MinusDirTorqueLimit(Reverse Torque Limit)는 Servo Drive Parameter Pn484 을 설정합니다.
    function AxmMotSetTorqueLimitEx (lAxisNo : LongInt; dbPlusDirTorqueLimit : Double; dbMinusDirTorqueLimit : Double) : DWord; stdcall;

    // 지정 축의 토크 리미트 값을 확인 합니다.(아래 표시된 제품만 기능 지원함)
    // 정방향, 역방향 구동시의 토크 값을 읽어 오는 함수.
    // ML-III : 설정 범위는 0 ~ 800 (0% ~ 800%)임.
    //          Liner Servo 앰프 모드만 지원(Only SGD7S, SGD7W)
    //          최대 토크의 단위는 1% 임.
    function AxmMotGetTorqueLimitEx (lAxisNo : LongInt; dbpPlusDirTorqueLimit : PDouble; dbpMinusDirTorqueLimit : PDouble) : DWord; stdcall;

    // 지정 축의 토크 리미트 값을 설정 합니다.
    // 정방향, 역방향 구동시의 토크 값을 제한하는 함수.
    // 설정 값은 1 ~ 3000(0.1% ~ 300.0%)까지 설정
    // 최대 토크의 0.1% 단위로 제어 함.
    // dPosition : 토크 리미트 값을 변경할 위치 정보(해당 위치 정보와 대상 위치가 같은 이벤트 발생시 적용됨).
    // lTarget   : COMMAND(0), ACTUAL(1)
    function AxmMotSetTorqueLimitAtPos (lAxisNo : LongInt; dbPlusDirTorqueLimit : Double; dbMinusDirTorqueLimit : Double; dPosition : Double; lTarget : LongInt) : DWord; stdcall;

    // 지정 축의 토크 리미트 값을 확인 합니다.
    function AxmMotGetTorqueLimitAtPos (lAxisNo : LongInt; dbpPlusDirTorqueLimit : PDouble; dbpMinusDirTorqueLimit : PDouble; dpPosition : PDouble; lpTarget : PLongInt) : DWord; stdcall;

    // 토크 리미트 기능을 Enable/Disable 한다. (PCI-R1604 RTEX 전용 함수)
    // PCI-R1604의 경우 토크 리미트 값을 설정하고 기능을 Enable 해야 토크 리미트 기능이 동작합니다.
    function AxmMotSetTorqueLimitEnable (lAxisNo : LongInt; uUse : DWord) : DWord; stdcall;

    // 토크 리미트 기능의 사용유무를 확인 한다. (PCI-R1604 RTEX 전용 함수)
    function AxmMotGetTorqueLimitEnable (lAxisNo : LongInt; upUse : PDWord) : DWord; stdcall;

    // 지정 축의 AxmOverridePos에 대한 특수 기능 사용 유무를 설정한다.
    // dwUsage        : AxmOverridPos 적용 가능 위치 판단 기능 사용 유무.
    //                  DISABLE(0) : 특수 기능 사용하지 않음.
    //                  ENABLE(1) : AxmMoveStartPos 설정한 구동 중 위치 변경 가능 위치를 감속 거리의 lDecelPosRatio(%)을 기준으로 판단한다.
    // lDecelPosRatio : 감속 거리에 대한 %값.
    // dReserved      : 사용하지 않음.
    function AxmOverridePosSetFunction (lAxisNo : LongInt; dwUsage : DWord; lDecelPosRatio : LongInt; dReserved : Double) : DWord; stdcall;
    // 지정 축의 AxmOverridePos에 대한 특수 기능 사용 유무를 확인 한다.
    function AxmOverridePosGetFunction (lAxisNo : LongInt; dwpUsage : PDWord; lpDecelPosRatio : PLongInt; dpReserved : PDouble) : DWord; stdcall;

    // 지정축의 특정 위치에서 설정한 디지털 출력 값을 제어한다.
    // lModuleNo   : 모듈 번호
    // lOffset     : 출력 접점에 대한 Offset 위치
    // uValue      : OFF(0)
    //             : OM(1)
    //             : Function Clear(0xFF)
    // dPosition   : DO 출력 값을 변경할 위치 정보(해당 위치 정보와 대상 위치가 같아지는 이벤트 발생시 실행됨).
    // lTarget     : COMMAND(0), ACTUAL(1)
    function AxmSignalSetWriteOutputBitAtPos (lAxisNo : LongInt; lModuleNo : LongInt; lOffset : LongInt; uValue : DWord; dPosition : Double; lTarget : LongInt) : DWord; stdcall;
    // 지정축의 특정 위치에서 설정한 디지털 출력 값 제어 설정을 확인한다.
    function AxmSignalGetWriteOutputBitAtPos (lAxisNo : LongInt; lpModuleNo : PLongInt; lOffset : PLongInt; upValue : PDWord; dpPosition : PDouble; lpTarget : PLongInt) : DWord; stdcall;

    //-------------------------------------------------------------------------------------------------------------------

    //======== PCI-R3200-MLIII 전용 함수==================================================================================
    // 잔류 진동 억제(VST) 특수 함수
    // 사용전에 반드시 코디에 대해서 축을 할당을 해야하며, 코디 한개에 1개의 축만 맵핑을 해야한다.
    // 아래 함수 실행전에 반드시 Servo ON 상태에서 사용한다.
    // lCoordnate        : 입력 성형 적용 코디 번호를 입력한다. 각 보드별 첫번째 부터 10번째의 코디에 축을 할당해서 사용해야 한다.
    //                     MLIII 마스터 보드는 보드 번호를 기준으로 16 ~ 31까지 보드 별로 순차적으로 16씩 증가된다.
    //                     MLIII B/D 0 : 16 ~ 31
    //                     MLIII B/D 1 : 31 ~ 47
    // cISTSize          : 입력 성형 사용 주파수 개수에 대해서 입력한다. 1로 값을 고정해서 사용한다.
    // dbpFrequency,  : 10H ~ 500Hz
    //                     1차 주파수 부터 순서데로 입력한다.(저주파부터 고주파).
    // dbpDampingRatio   : 0.001 ~ 0.9
    // dwpImpulseCount   : 2 ~ 5
    function AxmAdvVSTSetParameter (lCoord : LongInt; dwISTSize : DWord; dbpFrequency : PDouble; dbpDampingRatio : PDouble; dwpImpulseCount : PDWord) : DWord; stdcall;
    function AxmAdvVSTGetParameter (lCoord : LongInt; dwpISTSize : PDWord; dbpFrequency : PDouble; dbpDampingRatio : PDouble; dwpImpulseCount : PDWord) : DWord; stdcall;
    // lCoordnate        : 입력 성형 코디 번호를 입력한다.
    // dwISTEnable       : 입력 성형 사용 유무를 결정한다.
    function AxmAdvVSTSetEnabele (lCoord : LongInt; dwISTEnable : DWord) : DWord; stdcall;
    function AxmAdvVSTGetEnabele (lCoord : LongInt; dwpISTEnable : PDWord) : DWord; stdcall;

    //====일반 보간함수 =================================================================================================
    // 직선 보간 한다.
    // 시작점과 종료점을 지정하여 다축 직선 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점과 종료점을 지정하여 직선 보간 구동하는 Queue에 저장함수가된다.
    // 직선 프로파일 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmAdvContiStart함수를 사용해서 시작한다.
    function AxmAdvLineMove (lCoordinate : LongInt; dPosition : PDouble; dMaxVelocity : Double; dStartVel : Double; dStopVel : Double; dMaxAccel : Double; dMaxDecel : Double) : DWord; stdcall;
    // 지정된 좌표계에 시작점과 종료점을 지정하는 다축 직선 보간 오버라이드하는 함수이다.
    // 현재 진행중인 보간구동을 지정된 속도 및 위치로 직선 보간 오버라이드 하며, 다음 노드에 대한 직선 보간 구동 예약도 가능한다.
    // IOverrideMode = 0일 경우, 구동중인 보간이 직선, 원호 보간에 관계없이 현재 구동 노드에서 직선 보간으로 즉시 오버라이드 되고,
    // IOverrideMode = 1이면 현재 구동 노드 다음의 노드부터 직선보간이 차례로 예약된다.
    // IOverrideMode = 1로 본 함수를 호출할때마다 최소 1개에서 최대 8개까지 오버라이드 큐에 증가되면서 자동적으로 예약이 되며, 예약 후 마지막에 IOverrideMode = 0으로 본 함수가 호출되면
    // 내부적으로 오버라이드 큐에 있는 예약 보간들이 연속보간 큐로 저장되고, 직선 오버라이드 구동과 이후의 예약된 연속보간이 순차적으로 실행된다.
    function AxmAdvOvrLineMove (lCoordinate : LongInt; dPosition : PDouble; dMaxVelocity : Double; dStartVel : Double; dStopVel : Double; dMaxAccel : Double; dMaxDecel : Double; lOverrideMode : LongInt) : DWord; stdcall;
    // 2축 원호보간 한다.
    // 시작점, 종료점과 중심점을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode, 와 같이사용시 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 구동하는 원호 보간 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmAdvContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dCenterPos = 중심점 X,Y 배열 , dEndPos = 종료점 X,Y 배열.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvCircleCenterMove (lCoord : LongInt; lAxisNo : PLongInt; dCenterPos : PDouble; dEndPos : PDouble; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord) : DWord; stdcall;
    // 중간점, 종료점을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 중간점, 종료점을 지정하여 구동하는 원호 보간 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmAdvContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dMidPos = 중간점 X,Y 배열 , dEndPos = 종료점 X,Y 배열, lArcCircle = 아크(0), 원(1)
    function AxmAdvCirclePointMove (lCoord : LongInt; lAxisNo : PLongInt; dMidPos : PDouble; dEndPos : PDouble; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; lArcCircle : LongInt) : DWord; stdcall;
    // 시작점, 회전각도와 반지름을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점, 회전각도와 반지름을 지정하여 원호 보간 구동하는 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmAdvContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dCenterPos = 중심점 X,Y 배열 , dAngle = 각도.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvCircleAngleMove (lCoord : LongInt; lAxisNo : PLongInt; dCenterPos : PDouble; dAngle : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord) : DWord; stdcall;
    // 시작점, 종료점과 반지름을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 원호 보간 구동하는 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmAdvContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dRadius = 반지름, dEndPos = 종료점 X,Y 배열 , uShortDistance = 작은원(0), 큰원(1)
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvCircleRadiusMove (lCoord : LongInt; lAxisNo : PLongInt; dRadius : Double; dEndPos : PDouble; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord) : DWord; stdcall;
    // 지정된 좌표계에 시작점과 종료점을 지정하여 2축 원호 보간 오버라이드 구동한다.
    // 현재 진행중인 보간구동을 지정된 속도 및 위치로 원호 보간 오버라이드 하며, 다음 노드에 대한 원호 보간 구동 예약도 가능한다.
    // IOverrideMode = 0일 경우, 구동중인 보간이 직선, 원호 보간에 관계없이 현재 구동 노드에서 원호 보간으로 즉시 오버라이드 되고,
    // IOverrideMode = 1이면 현재 구동 노드 다음의 노드부터 원호보간이 차례로 예약된다.
    // IOverrideMode = 1로 본 함수를 호출할때마다 최소 1개에서 최대 8개까지 오버라이드 큐에 증가되면서 자동적으로 예약이 되며, 예약 후 마지막에 IOverrideMode = 0으로 본 함수가 호출되면
    // 내부적으로 오버라이드 큐에 있는 예약 보간들이 연속보간 큐로 저장되고, 원호 오버라이드 구동과 이후의 예약된 연속보간이 순차적으로 실행된다.
    function AxmAdvOvrCircleRadiusMove (lCoord : LongInt; lAxisNo : PLongInt; dRadius : Double; dEndPos : PDouble; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord; lOverrideMode : LongInt) : DWord; stdcall;

    //======= 헬리컬 이동 ===============================================================================================
    // 주의사항 : Helix를 연속보간 사용시 Spline, 직선보간과 원호보간을 같이 사용할수없다.

    // 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 헬리컬 보간 구동하는 함수이다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 헬리컬 연속보간 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmAdvContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다)
    // dCenterPos = 중심점 X,Y  , dEndPos = 종료점 X,Y .
    // uCWDir DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvHelixCenterMove (lCoord : LongInt; dCenterXPos : Double; dCenterYPos : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord) : DWord; stdcall;
    // 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 헬리컬 보간 구동하는 함수이다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 중간점, 종료점을 지정하여 헬리컬연속 보간 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmAdvContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다.)
    // dMidPos = 중간점 X,Y  , dEndPos = 종료점 X,Y
    function AxmAdvHelixPointMove (lCoord : LongInt; dMidXPos : Double; dMidYPos : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;
    // 지정된 좌표계에 시작점, 회전각도와 반지름을 지정하여 헬리컬 보간 구동하는 함수이다
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점, 회전각도와 반지름을 지정하여 헬리컬연속 보간 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmAdvContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다.)
    //dCenterPos = 중심점 X,Y  , dAngle = 각도.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvHelixAngleMove (lCoord : LongInt; dCenterXPos : Double; dCenterYPos : Double; dAngle : Double; dZPos : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord) : DWord; stdcall;
    // 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 헬리컬 보간 구동하는 함수이다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 헬리컬연속 보간 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmAdvContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다.)
    // dRadius = 반지름, dEndPos = 종료점 X,Y  , uShortDistance = 작은원(0), 큰원(1)
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvHelixRadiusMove (lCoord : LongInt; dRadius : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord) : DWord; stdcall;
    // 지정된 좌표계에 시작점과 종료점을 지정하여 3축 헬리컬 보간 오버라이드 구동한다.
    // 현재 진행중인 보간구동을 지정된 속도 및 위치로 헬리컬 보간 오버라이드 하며, 다음 노드에 대한 헬리컬 보간 구동 예약도 가능한다.
    // IOverrideMode = 0일 경우, 구동중인 보간이 직선, 원호 보간에 관계없이 현재 구동 노드에서 헬리컬 보간으로 즉시 오버라이드 되고,
    // IOverrideMode = 1이면 현재 구동 노드 다음의 노드부터 헬리컬 보간이 차례로 예약된다.
    // IOverrideMode = 1로 본 함수를 호출할때마다 최소 1개에서 최대 8개까지 오버라이드 큐에 증가되면서 자동적으로 예약이 되며, 예약 후 마지막에 IOverrideMode = 0으로 본 함수가 호출되면
    // 내부적으로 오버라이드 큐에 있는 예약 보간들이 연속보간 큐로 저장되고, 헬리컬 오버라이드 구동과 이후의 예약된 연속보간이 순차적으로 실행된다.
    function AxmAdvOvrHelixRadiusMove (lCoord : LongInt; dRadius : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord; lOverrideMode : LongInt) : DWord; stdcall;

    //====일반 보간함수 =================================================================================================
    // 직선 보간을 예약 구동한다.
    // 시작점과 종료점을 지정하여 다축 직선 보간을 예약 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점과 종료점을 지정하여 직선 보간 구동하는 Queue에 저장함수가된다.
    // 직선 프로파일 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmAdvContiStart함수를 사용해서 시작한다.
    function AxmAdvScriptLineMove (lCoordinate : LongInt; dPosition : PDouble; dMaxVelocity : Double; dStartVel : Double; dStopVel : Double; dMaxAccel : Double; dMaxDecel : Double; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;
    // 지정된 좌표계에 시작점과 종료점을 지정하는 다축 직선 보간 오버라이드를 예약 구동하는 함수이다.
    // 현재 진행중인 보간구동을 지정된 속도 및 위치로 직선 보간 오버라이드를 예약 구동 하며, 다음 노드에 대한 직선 보간 구동 예약이 가능한다.
    // IOverrideMode = 0일 경우, 구동중인 보간이 직선, 원호 보간에 관계없이 현재 구동 노드에서 직선 보간으로 즉시 오버라이드 되고,
    // IOverrideMode = 1이면 현재 구동 노드 다음의 노드부터 직선보간이 차례로 예약된다.
    // IOverrideMode = 1로 본 함수를 호출할때마다 최소 1개에서 최대 8개까지 오버라이드 큐에 증가되면서 자동적으로 예약이 되며, 예약 후 마지막에 IOverrideMode = 0으로 본 함수가 호출되면
    // 내부적으로 오버라이드 큐에 있는 예약 보간들이 연속보간 큐로 저장되고, 직선 오버라이드 구동과 이후의 예약된 연속보간이 순차적으로 실행된다.
    function AxmAdvScriptOvrLineMove (lCoordinate : LongInt; dPosition : PDouble; dMaxVelocity : Double; dStartVel : Double; dStopVel : Double; dMaxAccel : Double; dMaxDecel : Double; lOverrideMode : LongInt; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;
    // 2축 원호보간을 예약 구동한다.
    // 시작점, 종료점과 중심점을 지정하여 원호 보간을 예약 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode, 와 같이사용시 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 구동하는 원호 보간 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmAdvContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dCenterPos = 중심점 X,Y 배열 , dEndPos = 종료점 X,Y 배열.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvScriptCircleCenterMove (lCoord : LongInt; lAxisNo : PLongInt; dCenterPos : PDouble; dEndPos : PDouble; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;
    // 중간점, 종료점을 지정하여 원호 보간을 예약 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 중간점, 종료점을 지정하여 구동하는 원호 보간 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmAdvContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dMidPos = 중간점 X,Y 배열 , dEndPos = 종료점 X,Y 배열, lArcCircle = 아크(0), 원(1)
    function AxmAdvScriptCirclePointMove (lCoord : LongInt; lAxisNo : PLongInt; dMidPos : PDouble; dEndPos : PDouble; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; lArcCircle : LongInt; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;
    // 시작점, 회전각도와 반지름을 지정하여 원호 보간을 예약 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점, 회전각도와 반지름을 지정하여 원호 보간 구동하는 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmAdvContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dCenterPos = 중심점 X,Y 배열 , dAngle = 각도.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvScriptCircleAngleMove (lCoord : LongInt; lAxisNo : PLongInt; dCenterPos : PDouble; dAngle : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;
    // 시작점, 종료점과 반지름을 지정하여 원호 보간을 예약 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 원호 보간 구동하는 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmAdvContiStart함수를 사용해서 시작한다.
    // lAxisNo = 두축 배열 , dRadius = 반지름, dEndPos = 종료점 X,Y 배열 , uShortDistance = 작은원(0), 큰원(1)
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvScriptCircleRadiusMove (lCoord : LongInt; lAxisNo : PLongInt; dRadius : Double; dEndPos : PDouble; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;
    // 지정된 좌표계에 시작점과 종료점을 지정하여 2축 원호 보간 오버라이드를 예약 구동한다.
    // 현재 진행중인 보간구동을 지정된 속도 및 위치로 원호 보간 오버라이드을 예약 구동하며, 다음 노드에 대한 원호 보간 구동 예약이 가능한다.
    // IOverrideMode = 0일 경우, 구동중인 보간이 직선, 원호 보간에 관계없이 현재 구동 노드에서 원호 보간으로 즉시 오버라이드 되고,
    // IOverrideMode = 1이면 현재 구동 노드 다음의 노드부터 원호보간이 차례로 예약된다.
    // IOverrideMode = 1로 본 함수를 호출할때마다 최소 1개에서 최대 8개까지 오버라이드 큐에 증가되면서 자동적으로 예약이 되며, 예약 후 마지막에 IOverrideMode = 0으로 본 함수가 호출되면
    // 내부적으로 오버라이드 큐에 있는 예약 보간들이 연속보간 큐로 저장되고, 원호 오버라이드 구동과 이후의 예약된 연속보간이 순차적으로 실행된다.
    function AxmAdvScriptOvrCircleRadiusMove (lCoord : LongInt; lAxisNo : PLongInt; dRadius : Double; dEndPos : PDouble; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord; lOverrideMode : LongInt; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;

    //======= 헬리컬 이동 ===============================================================================================
    // 주의사항 : Helix를 연속보간 사용시 Spline, 직선보간과 원호보간을 같이 사용할수없다.

    // 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 헬리컬 보간을 예약 구동하는 함수이다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 헬리컬 연속보간을 예약 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmAdvContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다)
    // dCenterPos = 중심점 X,Y  , dEndPos = 종료점 X,Y .
    // uCWDir DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvScriptHelixCenterMove (lCoord : LongInt; dCenterXPos : Double; dCenterYPos : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;
    // 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 헬리컬 보간을 예약 구동하는 함수이다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 중간점, 종료점을 지정하여 헬리컬연속 보간을 예약 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmAdvContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다.)
    // dMidPos = 중간점 X,Y  , dEndPos = 종료점 X,Y
    function AxmAdvScriptHelixPointMove (lCoord : LongInt; dMidXPos : Double; dMidYPos : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;
    // 지정된 좌표계에 시작점, 회전각도와 반지름을 지정하여 헬리컬 보간을 예약 구동하는 함수이다
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점, 회전각도와 반지름을 지정하여 헬리컬연속 보간을 예약 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmAdvContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다.)
    //dCenterPos = 중심점 X,Y  , dAngle = 각도.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvScriptHelixAngleMove (lCoord : LongInt; dCenterXPos : Double; dCenterYPos : Double; dAngle : Double; dZPos : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;
    // 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 헬리컬 보간을 예약 구동하는 함수이다.
    // AxmAdvContiBeginNode, AxmAdvContiEndNode와 같이사용시 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 헬리컬연속 보간을 예약 구동하는 함수이다.
    // 원호 연속 보간 구동을 위해 내부 Queue에 저장하는 함수이다. AxmAdvContiStart함수를 사용해서 시작한다. (연속보간 함수와 같이 이용한다.)
    // dRadius = 반지름, dEndPos = 종료점 X,Y  , uShortDistance = 작은원(0), 큰원(1)
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmAdvScriptHelixRadiusMove (lCoord : LongInt; dRadius : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;
    // 지정된 좌표계에 시작점과 종료점을 지정하여 3축 헬리컬 보간 오버라이드를 예약 구동한다.
    // 현재 진행중인 보간구동을 지정된 속도 및 위치로 헬리컬 보간 오버라이드를 예약 구동한다.
    // IOverrideMode = 0일 경우, 구동중인 보간이 직선, 원호 보간에 관계없이 현재 구동 노드에서 헬리컬 보간으로 즉시 오버라이드 되고,
    // IOverrideMode = 1이면 현재 구동 노드 다음의 노드부터 헬리컬 보간이 차례로 예약된다.
    // IOverrideMode = 1로 본 함수를 호출할때마다 최소 1개에서 최대 8개까지 오버라이드 큐에 증가되면서 자동적으로 예약이 되며, 예약 후 마지막에 IOverrideMode = 0으로 본 함수가 호출되면
    // 내부적으로 오버라이드 큐에 있는 예약 보간들이 연속보간 큐로 저장되고, 헬리컬 오버라이드 구동과 이후의 예약된 연속보간이 순차적으로 실행된다.
    function AxmAdvScriptOvrHelixRadiusMove (lCoord : LongInt; dRadius : Double; dEndXPos : Double; dEndYPos : Double; dZPos : Double; dVel : Double; dStartVel : Double; dStopVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord; lOverrideMode : LongInt; dwScript : DWord; lScirptAxisNo : LongInt; dScriptPos : Double) : DWord; stdcall;

    //====연속 보간 함수 ================================================================================================
    // 지정된 좌표계에 연속 보간 구동 중 현재 구동중인 연속 보간 인덱스 번호를 확인하는 함수이다.
    function AxmAdvContiGetNodeNum (lCoordinate : LongInt; lpNodeNum : PLongInt) : DWord; stdcall;
    // 지정된 좌표계에 설정한 연속 보간 구동 총 인덱스 갯수를 확인하는 함수이다.
    function AxmAdvContiGetTotalNodeNum (lCoordinate : LongInt; lpNodeNum : PLongInt) : DWord; stdcall;
    // 지정된 좌표계에 보간 구동을 위한 내부 Queue에 저장되어 있는 보간 구동 개수를 확인하는 함수이다.
    function AxmAdvContiReadIndex (lCoordinate : LongInt; lpQueueIndex : PLongInt) : DWord; stdcall;
    // 지정된 좌표계에 보간 구동을 위한 내부 Queue가 비어 있는지 확인하는 함수이다.
    function AxmAdvContiReadFree (lCoordinate : LongInt; upQueueFree : PDWord) : DWord; stdcall;
    // 지정된 좌표계에 연속 보간 구동을 위해 저장된 내부 Queue를 모두 삭제하는 함수이다.
    function AxmAdvContiWriteClear (lCoordinate : LongInt) : DWord; stdcall;
    // 지정된 좌표계에 연속 보간 오버라이드 구동을 위해 예약된 오버라이드용 큐를 모두 삭제하는 함수이다.
    function AxmAdvOvrContiWriteClear (lCoordinate : LongInt) : DWord; stdcall;
    // 연속 보간 시작 한다.
    function AxmAdvContiStart (lCoord : LongInt; dwProfileset : DWord; lAngle : LongInt) : DWord; stdcall;
    // 연속 보간 정지 한다.
    function AxmAdvContiStop (lCoordinate : LongInt; dDecel : Double) : DWord; stdcall;
    //지정된 좌표계에 연속보간 축 맵핑을 설정한다.
    //(축맵핑 번호는 0 부터 시작))
    // 주의점:  축맵핑할때는 반드시 실제 축번호가 작은 숫자부터 큰숫자를 넣는다.
    //          가상축 맵핑 함수를 사용하였을 때 가상축번호를 실제 축번호가 작은 값 부터 lpAxesNo의 낮은 인텍스에 입력하여야 한다.
    //          가상축 맵핑 함수를 사용하였을 때 가상축번호에 해당하는 실제 축번호가 다른 값이라야 한다.
    //          같은 축을 다른 Coordinate에 중복 맵핑하지 말아야 한다.
    function AxmAdvContiSetAxisMap (lCoord : LongInt; lSize : LongInt; lpAxesNo : PLongInt) : DWord; stdcall;
    //지정된 좌표계에 연속보간 축 맵핑을 반환한다.
    function AxmAdvContiGetAxisMap (lCoord : LongInt; lpSize : PLongInt; lpAxesNo : PLongInt) : DWord; stdcall;
    // 지정된 좌표계에 연속보간 축 절대/상대 모드를 설정한다.
    // (주의점 : 반드시 축맵핑 하고 사용가능)
    // 지정 축의 이동 거리 계산 모드를 설정한다.
    //uAbsRelMode : POS_ABS_MODE '0' - 절대 좌표계
    //              POS_REL_MODE '1' - 상대 좌표계
    function AxmAdvContiSetAbsRelMode (lCoord : LongInt; uAbsRelMode : DWord) : DWord; stdcall;
    // 지정된 좌표계에 연속보간 축 절대/상대 모드를 반환한다.
    function AxmAdvContiGetAbsRelMode (lCoord : LongInt; uAbsRelMode : PDWord) : DWord; stdcall;
    // 지정된 좌표계에 연속 보간 구동 중인지 확인하는 함수이다.
    function AxmAdvContiIsMotion (lCoordinate : LongInt; upInMotion : PDWord) : DWord; stdcall;
    // 지정된 좌표계에 연속보간에서 수행할 작업들의 등록을 시작한다. 이함수를 호출한후,
    // AxmAdvContiEndNode함수가 호출되기 전까지 수행되는 모든 모션작업은 실제 모션을 수행하는 것이 아니라 연속보간 모션으로 등록 되는 것이며,
    // AxmAdvContiStart 함수가 호출될 때 비로소 등록된모션이 실제로 수행된다.
    function AxmAdvContiBeginNode (lCoord : LongInt) : DWord; stdcall;
    // 지정된 좌표계에서 연속보간을 수행할 작업들의 등록을 종료한다.
    function AxmAdvContiEndNode (lCoord : LongInt) : DWord; stdcall;

    // 지정한 다축을 설정한 감속도로 동기 감속 정지한다.
    function AxmMoveMultiStop (lArraySize : LongInt; lpAxesNo : PLongInt; dMaxDecel : PDouble) : DWord; stdcall;
    // 지정한 다축을 동기 급 정지한다.
    function AxmMoveMultiEStop (lArraySize : LongInt; lpAxesNo : PLongInt) : DWord; stdcall;
    // 지정한 다축을 동기 감속 정지한다.
    function AxmMoveMultiSStop (lArraySize : LongInt; lpAxesNo : PLongInt) : DWord; stdcall;

    // 지정한 축의 실제 구동 속도를 읽어온다.
    function AxmStatusReadActVel (lAxisNo : LongInt; dpVel : PDouble) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의 SVCMD_STAT 커맨드 값을 읽는다.
    function AxmStatusReadServoCmdStat (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의 SVCMD_CTRL 커맨드 값을 읽는다.
    function AxmStatusReadServoCmdCtrl (lAxisNo : LongInt; upStatus : PDWord) : DWord; stdcall;

    // 겐트리 구동시 마스터 축과 슬레이브 축 간의 위치 차에 대한 설정된 오차 한계값을 반환한다.
    function AxmGantryGetMstToSlvOverDist (lAxisNo : LongInt; dpPosition : PDouble) : DWord; stdcall;
    // 겐트리 구동시 마스터 축과 슬레이브 축 간의 위치 차에 대한 오차 한계값을 설정한다.
    function AxmGantrySetMstToSlvOverDist (lAxisNo : LongInt; dPosition : Double) : DWord; stdcall;

    // 지정 축의 알람 신호의 코드 상태를 반환한다.
    function AxmSignalReadServoAlarmCode (lAxisNo : LongInt; upCodeStatus : PWord) : DWord; stdcall;

    // 서보 타입 슬레이브 기기의 좌표계 설정을 실시한다. (MLIII 전용)
    function AxmM3ServoCoordinatesSet (lAxisNo : LongInt; dwPosData : DWord; dwPos_sel : DWord; dwRefe : DWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의 브레이크 작동 신호를 출력한다. (MLIII 전용)
    function AxmM3ServoBreakOn (lAxisNo : LongInt) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의 브레이크 작동 신호를 해제한다. (MLIII 전용)
    function AxmM3ServoBreakOff (lAxisNo : LongInt) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의
    function AxmM3ServoConfig (lAxisNo : LongInt; dwCfMode : DWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의 센서 종보 초기화를 요구한다.
    function AxmM3ServoSensOn (lAxisNo : LongInt) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의 센서전원 OFF를 요구한다.
    function AxmM3ServoSensOff (lAxisNo : LongInt) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의 SMON 커맨드를 실행한다.
    function AxmM3ServoSmon (lAxisNo : LongInt) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의 모니터 정보나 입출력 신호의 상태를 읽는다.
    function AxmM3ServoGetSmon (lAxisNo : LongInt; pbParam : PByte) : DWord; stdcall;
    // 서보 타입 슬레이브 기기에 서보 ON을 요구한다.
    function AxmM3ServoSvOn (lAxisNo : LongInt) : DWord; stdcall;
    // 서보 타입 슬레이브 기기에 서보 OFF를 요구한다.
    function AxmM3ServoSvOff (lAxisNo : LongInt) : DWord; stdcall;
    // 서보 타입 슬레이브 기기가 지정된 보간 위치로 보간이동을 실시한다.
    function AxmM3ServoInterpolate (lAxisNo : LongInt; dwTPOS : DWord; dwVFF : DWord; dwTFF : DWord; dwTLIM : DWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기가 지정한 위치로 위치이송을 실시한다.
    function AxmM3ServoPosing (lAxisNo : LongInt; dwTPOS : DWord; dwSPD : DWord; dwACCR : DWord; dwDECR : DWord; dwTLIM : DWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기가 지정된 이동속도로 정속이송을 실시한다.
    function AxmM3ServoFeed (lAxisNo : LongInt; lSPD : LongInt; dwACCR : DWord; dwDECR : DWord; dwTLIM : DWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기가 이송중 외부 위치결정 신호의 입력에 의해 위치이송을 실시한다.
    function AxmM3ServoExFeed (lAxisNo : LongInt; lSPD : LongInt; dwACCR : DWord; dwDECR : DWord; dwTLIM : DWord; dwExSig1 : DWord; dwExSig2 : DWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기가 외부 위치결정 신호 입력에 의해 위치이송을 실시한다.
    function AxmM3ServoExPosing (lAxisNo : LongInt; dwTPOS : DWord; dwSPD : DWord; dwACCR : DWord; dwDECR : DWord; dwTLIM : DWord; dwExSig1 : DWord; dwExSig2 : DWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기가 원점 복귀를 실시한다.
    function AxmM3ServoZret (lAxisNo : LongInt; dwSPD : DWord; dwACCR : DWord; dwDECR : DWord; dwTLIM : DWord; dwExSig1 : DWord; dwExSig2 : DWord; bHomeDir : Byte; bHomeType : Byte) : DWord; stdcall;
    // 서보 타입 슬레이브 기기가 속도제어를 실시한다.
    function AxmM3ServoVelctrl (lAxisNo : LongInt; dwTFF : DWord; dwVREF : DWord; dwACCR : DWord; dwDECR : DWord; dwTLIM : DWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기가 토크제어를 실시한다.
    function AxmM3ServoTrqctrl (lAxisNo : LongInt; dwVLIM : DWord; lTQREF : LongInt) : DWord; stdcall;
    // bmode 0x00 : common parameters ram
    // bmode 0x01 : common parameters flash
    // bmode 0x10 : device parameters ram
    // bmode 0x11 : device parameters flash
    // 서보 타입 슬레이브 기기의 서보팩 특정 파라미터 설정값을 반환한다.
    function AxmM3ServoGetParameter (lAxisNo : LongInt; wNo : Word; bSize : Byte; bMode : Byte; pbParam : PByte) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의 서보팩 특정 파라미터 값을 설정한다.
    function AxmM3ServoSetParameter (lAxisNo : LongInt; wNo : Word; bSize : Byte; bMode : Byte; pbParam : PByte) : DWord; stdcall;
    // M3 서보팩에 Command Execution을 실행한다
    // dwSize는 사용할 변수 개수(예: 1)M3StatNop : AxmServoCmdExecution(m_lAxis, 0, NULL), 2)M3GetStationIdRd : AxmServoCmdExecution(m_lAxis, 3, *pbIdRd))
    // M3StationNop(int lNodeNum)                                                                                                   : bwSize = 0
    // M3GetStationIdRd(int lNodeNum, BYTE bIdCode, BYTE bOffset, BYTE bSize, BYTE *pbIdRd)                                         : bwSize = 3
    // M3ServoSetConfig(int lNodeNum, BYTE bMode)                                                                                   : bwSize = 1
    // M3SetStationAlarmClear(int lNodeNum, WORD wAlarmClrMod)                                                                      : bwSize = 1
    // M3ServoSyncSet(int lNodeNum)                                                                                                 : bwSize = 0
    // M3SetStationConnect(int lNodeNum, BYTE bVer, uByteComMod ubComMode, BYTE bComTime, BYTE bProfileType)                        : bwSize = 4
    // M3SetStationDisconnect(int lNodeNum)                                                                                         : bwSize = 0
    // M3ServoSmon(int lNodeNum)                                                                                                    : bwSize = 0
    // M3ServoSvOn(int lNodeNum)                                                                                                    : bwSize = 0
    // M3ServoSvOff(int lNodeNum)                                                                                                   : bwSize = 0
    // M3ServoInterpolate(int lNodeNum, LONG lTPOS, LONG lVFF, LONG lTFF)                                                           : bwSize = 3
    // M3ServoPosing(int lNodeNum, LONG lTPOS, LONG lSPD, LONG lACCR, LONG lDECR, LONG lTLIM)                                       : bwSize = 5
    // M3ServoFeed(int lNodeNum, LONG lSPD, LONG lACCR, LONG lDECR, LONG lTLIM)                                                     : bwSize = 4
    // M3ServoExFeed(int lNodeNum, LONG lSPD, LONG lACCR, LONG lDECR, LONG lTLIM, DWORD dwExSig1, DWORD dwExSig2)                   : bwSize = 6
    // M3ServoExPosing(int lNodeNum, LONG lTPOS, LONG lSPD, LONG lACCR, LONG lDECR, LONG lTLIM, DWORD dwExSig1, DWORD dwExSig2)     : bwSize = 7
    // M3ServoTrqctrl(int lNodeNum, LONG lVLIM, LONG lTQREF)                                                                        : bwSize = 2
    // M3ServoGetParameter(int lNodeNum, WORD wNo, BYTE bSize, BYTE bMode, BYTE *pbParam)                                           : bwSize = 3
    // M3ServoSetParameter(int lNodeNum, WORD wNo, BYTE bSize, BYTE bMode, BYTE *pbParam)                                           : bwSize = 7
    function AxmServoCmdExecution (lAxisNo : LongInt; dwCommand : DWord; dwSize : DWord; pdwExcData : PDWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기의 설정된 토크 제한 값을 반환한다.
    function AxmM3ServoGetTorqLimit (lAxisNo : LongInt; dwpTorqLimit : PDWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기에 토크 제한 값을 설정한다.
    function AxmM3ServoSetTorqLimit (lAxisNo : LongInt; dwTorqLimit : DWord) : DWord; stdcall;

    // 서보 타입 슬레이브 기기에 설정된 SVCMD_IO 커맨드 값을 반환한다.
    function AxmM3ServoGetSendSvCmdIOOutput (lAxisNo : LongInt; dwData : PDWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기에 SVCMD_IO 커맨드 값을 설정한다.
    function AxmM3ServoSetSendSvCmdIOOutput (lAxisNo : LongInt; dwData : DWord) : DWord; stdcall;

    // 서보 타입 슬레이브 기기에 설정된 SVCMD_CTRL 커맨드 값을 반환한다.
    function AxmM3ServoGetSvCmdCtrl (lAxisNo : LongInt; dwData : PDWord) : DWord; stdcall;
    // 서보 타입 슬레이브 기기에 SVCMD_CTRL 커맨드 값을 설정한다.
    function AxmM3ServoSetSvCmdCtrl (lAxisNo : LongInt; dwData : DWord) : DWord; stdcall;

    // MLIII adjustment operation을 설정 한다.
    // dwReqCode == 0x1005 : parameter initialization : 20sec
    // dwReqCode == 0x1008 : absolute encoder reset   : 5sec
    // dwReqCode == 0x100E : automatic offset adjustment of motor current detection signals  : 5sec
    // dwReqCode == 0x1013 : Multiturn limit setting  : 5sec
    function AxmM3AdjustmentOperation (lAxisNo : LongInt; dwReqCode : DWord) : DWord; stdcall;
    // 서보 축 추가 모니터링 채널별 선택 값을 설정한다.
    function AxmM3ServoSetMonSel (lAxisNo : LongInt; dwMon0 : DWord; dwMon1 : DWord; dwMon2 : DWord) : DWord; stdcall;
    // 서보 축 추가 모니터링 채널별 설정 값을 반환한다.
    function AxmM3ServoGetMonSel (lAxisNo : LongInt; upMon0 : PDWord; upMon1 : PDWord; upMon2 : PDWord) : DWord; stdcall;
    // 서보 축 추가 모니터링 채널별 설정 값을 기준으로 현재 상태를 반환한다.
    function AxmM3ServoReadMonData (lAxisNo : LongInt; dwMonSel : DWord; dwpMonData : PDWord) : DWord; stdcall;
    // 제어할 토크 축 설정
    function AxmAdvTorqueContiSetAxisMap (lCoord : LongInt; lSize : LongInt; lpAxesNo : PLongInt; dwTLIM : DWord; dwConMode : DWord) : DWord; stdcall;
    // 2014.04.28
    // 토크 프로파일 설정 파라미터
    function AxmM3ServoSetTorqProfile (lCoord : LongInt; lAxisNo : LongInt; TorqueSign : LongInt; dwVLIM : DWord; dwProfileMode : DWord; dwStdTorq : DWord; dwStopTorq : DWord) : DWord; stdcall;
    // 토크 프로파일 확인 파라미터
    function AxmM3ServoGetTorqProfile (lCoord : LongInt; lAxisNo : LongInt; lpTorqueSign : PLongInt; updwVLIM : PDWord; upProfileMode : PDWord; upStdTorq : PDWord; upStopTorq : PDWord) : DWord; stdcall;
    //-------------------------------------------------------------------------------------------------------------------

    //======== SMP 전용 함수 =======================================================================================
    // Inposition 신호의 Range를 설정한다. (dInposRange > 0)
    function AxmSignalSetInposRange (lAxisNo : LongInt; dInposRange : Double) : DWord; stdcall;
    // Inposition 신호의 Range를 반환한다.
    function AxmSignalGetInposRange (lAxisNo : LongInt; dpInposRange : PDouble) : DWord; stdcall;

    // 오버라이드할때 위치속성(절대/상대)을 설정한다.
    function AxmMotSetOverridePosMode (lAxisNo : LongInt; dwAbsRelMode : DWord) : DWord; stdcall;
    // 오버라이드할때 위치속성(절대/상대)을 읽어온다.
    function AxmMotGetOverridePosMode (lAxisNo : LongInt; dwpAbsRelMode : PDWord) : DWord; stdcall;
    // LineMove 오버라이드할때 위치속성(절대/상대)을 설정한다.
    function AxmMotSetOverrideLinePosMode (lCoordNo : LongInt; dwAbsRelMode : DWord) : DWord; stdcall;
    // LineMove 오버라이드할때 위치속성(절대/상대)을 읽어온다.
    function AxmMotGetOverrideLinePosMode (lCoordNo : LongInt; dwpAbsRelMode : PDWord) : DWord; stdcall;

    // AxmMoveStartPos와 동일하며 종료속도(EndVel)가 추가되었다.
    function AxmMoveStartPosEx (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; dEndVel : Double) : DWord; stdcall;
    // AxmMovePos와 동일하며 종료속도(EndVel)가 추가되었다.
    function AxmMovePosEx (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; dEndVel : Double) : DWord; stdcall;

    // Coordinate Motion을 경로상에서 감속정지(dDecel) 시킨다.
    function AxmMoveCoordStop (lCoordNo : LongInt; dDecel : Double) : DWord; stdcall;
    // Coordinate Motion을 급정지 시킨다.
    function AxmMoveCoordEStop (lCoordNo : LongInt) : DWord; stdcall;
    // Coordinate Motion을 경로상에서 감속정지 시킨다.
    function AxmMoveCoordSStop (lCoordNo : LongInt) : DWord; stdcall;

    // AxmLineMove모션의 위치를 오버라이드 시킨다.
    function AxmOverrideLinePos (lCoordNo : LongInt; dpOverridePos : PDouble) : DWord; stdcall;
    // AxmLineMove모션의 속도를 오버라이드 시킨다. 각축들의 속도비율은 dpDistance로 결정된다.
    function AxmOverrideLineVel (lCoordNo : LongInt; dOverrideVel : Double; dpDistance : PDouble) : DWord; stdcall;

    // AxmLineMove모션의 속도를 오버라이드 시킨다.
    // dMaxAccel  : 오버라이드 가속도
    // dMaxDecel  : 오버라이드 감속도
    // dpDistance : 각축의 속도 비율
    function AxmOverrideLineAccelVelDecel (lCoordNo : LongInt; dOverrideVelocity : Double; dMaxAccel : Double; dMaxDecel : Double; dpDistance : PDouble) : DWord; stdcall;
    // AxmOverrideVelAtPos에 추가적으로 AccelDecel을 오버라이드 시킨다.
    function AxmOverrideAccelVelDecelAtPos (lAxisNo : LongInt; dPos : Double; dVel : Double; dAccel : Double; dDecel : Double; dOverridePos : Double; dOverrideVel : Double; dOverrideAccel : Double; dOverrideDecel : Double; lTarget : LongInt) : DWord; stdcall;

    // 하나의 마스터축에 다수의 슬레이브축들을 연결한다(Electronic Gearing).
    // lMasterAxisNo : 마스터축
    // lSize : 슬레이브축 개수(최대 8)
    // lpSlaveAxisNo : 슬레이브축 번호
    // dpGearRatio : 마스터축을 기준으로하는 슬레이브축 비율(0은 제외, 1 = 100%)
    function AxmEGearSet (lMasterAxisNo : LongInt; lSize : LongInt; lpSlaveAxisNo : PLongInt; dpGearRatio : PDouble) : DWord; stdcall;
    // Electronic Gearing정보를 읽어온다.
    function AxmEGearGet (lMasterAxisNo : LongInt; lpSize : PLongInt; lpSlaveAxisNo : PLongInt; dpGearRatio : PDouble) : DWord; stdcall;
    // Electronic Gearing을 해제한다.
    function AxmEGearReset (lMasterAxisNo : LongInt) : DWord; stdcall;
    // Electronic Gearing을 활성/비활성한다.
    function AxmEGearEnable (lMasterAxisNo : LongInt; dwEnable : DWord) : DWord; stdcall;
    // Electronic Gearing을 활성/비활성상태를 읽어온다.
    function AxmEGearIsEnable (lMasterAxisNo : LongInt; dwpEnable : PDWord) : DWord; stdcall;

    // 주의사항: 입력한 종료속도가 '0'미만이면 '0'으로, 'AxmMotSetMaxVel'로 설정한 최대속도를 초과하면 'MaxVel'로 재설정된다.
    // 지정 축에 종료속도를 설정한다.
    function AxmMotSetEndVel (lAxisNo : LongInt; dEndVelocity : Double) : DWord; stdcall;
    // 지정 축의 종료속도를 반환한다.
    function AxmMotGetEndVel (lAxisNo : LongInt; dpEndVelocity : PDouble) : DWord; stdcall;
    // 직선 보간 한다.
    // 시작점과 종료점을 지정하여 다축 직선 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 시작점과 종료점을 지정하여 직선 보간 구동하는 Queue에 저장함수가된다.
    // 직선 프로파일 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // lpAxisNo의 축 배열에 해당하는 축들은 직선 보간을 하며, 나머지 Coordinate의 축들은 직선 보간 비율에 맞게 단축 구동을 수행한다.
    function AxmLineMoveWithAxes (lCoord : LongInt; lArraySize : LongInt; lpAxisNo : PLongInt; dpEndPos : PDouble; dVel : Double; dAccel : Double; dDecel : Double) : DWord; stdcall;
    // 2차원/3차원 원호보간 및 그 이상의 축에 대해서 직선보간을 한다.
    // 시작점, 종료점과 중심점을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode, 와 같이사용시 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 구동하는 원호 보간 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // lAxisNo = 축 배열 , dCenterPosition = 중심점 X,Y 배열/X, Y, Z 배열, dEndPos = 종료점 X,Y 배열/X, Y, Z배열
    // 2차원/3차원 이상의 축에 대해서는 직선보간을 할 때 dEndPosition의 값을 Targetposition으로 사용한다.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    // dw3DCircle(0) = 2차원 원호보간 및 그 이상의 축에 대해서 직선보간
    // dw3DCircle(1) = 3차원 원호보간 및 그 이상의 축에 대해서 직선보간
    function AxmCircleCenterMoveWithAxes (lCoord : LongInt; lArraySize : LongInt; lpAxisNo : PLongInt; dCenterPosition : PDouble; dEndPosition : PDouble; dMaxVelocity : Double; dMaxAccel : Double; dMaxDecel : Double; uCWDir : DWord; dw3DCircle : DWord) : DWord; stdcall;

    // 시작점, 종료점과 반지름을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 시작점, 종료점과 반지름을 지정하여 원호 보간 구동하는 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // lArraySize       : 원호보간을 할 축의 갯수(2 or 3)
    // lpAxisNo         : 원호 보간을 할 축 배열
    // dRadius          : 원의 반지름
    // dEndPos          : 원호보간시 종료위치 배열, AxmContiSetAxisMap에서 맵핑한 축 번호 순서에 맞는 배열의 위치에 값을 입력한다.
    // uCWDir           : DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    // uShortDistance   : 작은원(0), 큰원(1)
    function AxmCircleRadiusMoveWithAxes (lCoord : LongInt; lArraySize : LongInt; lpAxisNo : PLongInt; dRadius : Double; dEndPos : PDouble; dVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord; uShortDistance : DWord) : DWord; stdcall;


    // 시작점, 회전각도와 반지름을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 시작점, 회전각도와 반지름을 지정하여 원호 보간 구동하는 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // lArraySize       : 원호보간을 할 축의 갯수(2 or 3)
    // lpAxisNo         : 원호 보간을 할 축 배열
    // dCenterPos       : 원호보간에 사용할 중심점 배열, AxmContiSetAxisMap에서 맵핑한 축 번호 순서에 맞는 배열의 위치에 값을 입력한다
    // dAngle           : 각도.
    // uCWDir           : DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    function AxmCircleAngleMoveWithAxes (lCoord : LongInt; lArraySize : LongInt; lpAxisNo : PLongInt; dCenterPos : PDouble; dAngle : Double; dVel : Double; dAccel : Double; dDecel : Double; uCWDir : DWord) : DWord; stdcall;

    // 2차원/3차원 원호보간 및 그 이상의 축에 대해서 직선보간을 한다.
    // 시작위치에서 중간점, 종료점을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode, 와 같이사용시 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 구동하는 원호 보간 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // 2차원/3차원 이상의 축에 대해서는 직선보간을 할 때 dEndPosition의 값을 Targetposition으로 사용한다.
    // lArraySize       : 원호보간을 할 축의 갯수(2 or 3)
    // lpAxisNo         : 원호 보간을 할 축 배열
    // dMidPOs          : 원호보간에 사용할 중간점 배열, AxmContiSetAxisMap에서 맵핑한 축 번호 순서에 맞는 배열의 위치에 입력한다.
    // dEndPos          : 원호보간에 사용할 종료점 배열, AxmContiSetAxisMap에서 맵핑한 축 번호 순서에 맞는 배열의 위치에 입력한다.
    //   Ex) AxmContiSetAxisMap(4, [0, 1, 2, 3]맵핑, 2축 3축 원호보간, 시작위치 (0.0, 100), 중간점을 (70.70, 70.7), 종료점 (0.0, 100.0), 0축, 1축 (300.0, 400.0)
    //       dMidPos[4] = { 0.0, 0.0, 50.0, 100.0 }, dEndPos[4] = { 300.0, 400.0, 0.0, 100.0 }
    // lArcCircle       : 아크(0), 원(1)
    function AxmCirclePointMoveWithAxes (lCoordNo : LongInt; lArraySize : LongInt; lpAxisNo : PLongInt; dpMidPos : PDouble; dpEndPos : PDouble; dVel : Double; dAccel : Double; dDecel : Double; lArcCircle : LongInt) : DWord; stdcall;

    // 직선 보간 한다.
    // 시작점과 종료점을 지정하여 다축 직선 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode와 같이사용시 지정된 좌표계에 시작점과 종료점을 지정하여 직선 보간 구동하는 Queue에 저장함수가된다.
    // 직선 프로파일 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // lpAxisNo의 축 배열에 해당하는 축들은 직선 보간을 하며, 나머지 Coordinate의 축들은 직선 보간 비율에 맞게 단축 구동을 수행한다.
    function AxmLineMoveWithAxesWithEvent (lCoord : LongInt; lArraySize : LongInt; lpAxisNo : PLongInt; dpEndPos : PDouble; dVel : Double; dAccel : Double; dDecel : Double; dwEventFlag : DWord) : DWord; stdcall;

    // 2차원/3차원 원호보간 및 그 이상의 축에 대해서 직선보간을 한다.
    // 시작점, 종료점과 중심점을 지정하여 원호 보간 구동하는 함수이다. 구동 시작 후 함수를 벗어난다.
    // AxmContiBeginNode, AxmContiEndNode, 와 같이사용시 지정된 좌표계에 시작점, 종료점과 중심점을 지정하여 구동하는 원호 보간 Queue에 저장함수가된다.
    // 프로파일 원호 연속 보간 구동을 위해 내부 Queue에 저장하여 AxmContiStart함수를 사용해서 시작한다.
    // lAxisNo = 축 배열 , dCenterPosition = 중심점 X,Y 배열/X, Y, Z 배열, dEndPos = 종료점 X,Y 배열/X, Y, Z배열
    // 2차원/3차원 이상의 축에 대해서는 직선보간을 할 때 dEndPosition의 값을 Targetposition으로 사용한다.
    // uCWDir   DIR_CCW(0): 반시계방향, DIR_CW(1) 시계방향
    // dw3DCircle(0) = 2차원 원호보간 및 그 이상의 축에 대해서 직선보간
    // dw3DCircle(1) = 3차원 원호보간 및 그 이상의 축에 대해서 직선보간
    function AxmCircleCenterMoveWithAxesWithEvent (lCoord : LongInt; lArraySize : LongInt; lpAxisNo : PLongInt; dCenterPosition : PDouble; dEndPosition : PDouble; dMaxVelocity : Double; dMaxAccel : Double; dMaxDecel : Double; uCWDir : DWord; dw3DCircle : DWord; dwEventFlag : DWord) : DWord; stdcall;

    function AxmFilletMove (lCoordinate : LongInt; dPosition : PDouble; dFirstVector : PDouble; dSecondVector : PDouble; dMaxVelocity : Double; dMaxAccel : Double; dMaxDecel : Double; dRadius : Double) : DWord; stdcall;

    // 단축 PVT 구동을 한다.
    // 사용자가 Position, Velocity, Time Table을 이용하여 생성한 프로파일로 구동한다.
    // AxmSyncBegin, AxmSyncEnd API와 함께 사용시 여러 축의 PVT 구동을 예약한다.
    // 예약된 PVT 구동 프로파일은 AxmSyncStart 명령을 받게되면 동시에 시작한다.
    // lAxisNo : 구동 축
    // dwArraySize : PVT Table size
    // pdPos : Position 배열
    // pdVel : Velocity 배열
    // pdwUsec : Time 배열(Usec 단위, 단 Cycle의 배수여야만 한다. ex 1sec = 1,000,000)
    function AxmMovePVT (lAxisNo : LongInt; dwArraySize : DWord; pdPos : PDouble; pdVel : PDouble; pdwUsec : PDWord) : DWord; stdcall;

    //====Sync 함수 ================================================================================================
    //지정된 Sync No.에서 사용할 축을 맵핑한다.
    //(맵핑 번호는 0 부터 시작))
    // SyncSetAxisMap의 경우 Sync 구동에서 사용되는 유효축을 설정하는 함수이다.
    // SyncBegin과 SyncEnd 사이에서 사용되는 PVT Motion의 지정 축이 맵핑되지 않은 축일 경우
    // 예약되지 않고 즉시 구동한다. 즉 맵핑된 축만이 Begin과 End사이에서 구동 예약이 되며
    // SyncStart API를 호출하면 지정된 Sync Index에서 예약된 구동이 동시에 시작한다.

    // Sync 구동에서 사용될 유효 축을 지정한다.
    // lSyncNo : Sync Index
    // lSize : 맵핑할 축 갯수
    // lpAxesNo : 맵핑 축 배열
    function AxmSyncSetAxisMap (lSyncNo : LongInt; lSize : LongInt; lpAxesNo : PLongInt) : DWord; stdcall;

    // 지정된 Sync Index에 할당된 축 맵핑과 예약 프로파일을 리셋한다.
    function AxmSyncClear (lSyncNo : LongInt) : DWord; stdcall;

    // 지정된 Sync Index에 수행할 구동 예약을 시작한다.
    // 이 함수를 호출한 후, AxmSyncEnd 함수가 호출되기 전까지 실행되는
    // 유효 축의 PVT 구동은 실제 구동을 즉시 수행하는 것이 아니라 구동 예약이 되며
    // AxmSyncStart 함수가 호출될 때 비로소 예약된 구동이 수행된다.
    function AxmSyncBegin (lSyncNo : LongInt) : DWord; stdcall;

    // 지정된 Sync Index에서 수행할 구동 예약을 종료한다.
    function AxmSyncEnd (lSyncNo : LongInt) : DWord; stdcall;

    // 지정된 Sync Index에서 예약된 구동을 시작한다.
    function AxmSyncStart (lSyncNo : LongInt) : DWord; stdcall;

    // 지정된 축의 Profile Queue에 여유 Count를 확인한다.
    function AxmStatusReadRemainQueueCount (lAxisNo : LongInt; pdwRemainQueueCount : PDWord) : DWord; stdcall;


implementation

const

    dll_name    = 'AXL.dll';
    function AxmInfoGetAxis; external dll_name name 'AxmInfoGetAxis';
    function AxmInfoIsMotionModule; external dll_name name 'AxmInfoIsMotionModule';
    function AxmInfoIsInvalidAxisNo; external dll_name name 'AxmInfoIsInvalidAxisNo';
    function AxmInfoGetAxisStatus; external dll_name name 'AxmInfoGetAxisStatus';
    function AxmInfoGetAxisCount; external dll_name name 'AxmInfoGetAxisCount';
    function AxmInfoGetFirstAxisNo; external dll_name name 'AxmInfoGetFirstAxisNo';
    function AxmInfoGetBoardFirstAxisNo; external dll_name name 'AxmInfoGetBoardFirstAxisNo';
    function AxmVirtualSetAxisNoMap; external dll_name name 'AxmVirtualSetAxisNoMap';
    function AxmVirtualGetAxisNoMap; external dll_name name 'AxmVirtualGetAxisNoMap';
    function AxmVirtualSetMultiAxisNoMap; external dll_name name 'AxmVirtualSetMultiAxisNoMap';
    function AxmVirtualGetMultiAxisNoMap; external dll_name name 'AxmVirtualGetMultiAxisNoMap';
    function AxmVirtualResetAxisMap; external dll_name name 'AxmVirtualResetAxisMap';
    function AxmInterruptSetAxis; external dll_name name 'AxmInterruptSetAxis';
    function AxmInterruptSetAxisEnable; external dll_name name 'AxmInterruptSetAxisEnable';
    function AxmInterruptGetAxisEnable; external dll_name name 'AxmInterruptGetAxisEnable';
    function AxmInterruptRead; external dll_name name 'AxmInterruptRead';
    function AxmInterruptReadAxisFlag; external dll_name name 'AxmInterruptReadAxisFlag';
    function AxmInterruptSetUserEnable; external dll_name name 'AxmInterruptSetUserEnable';
    function AxmInterruptGetUserEnable; external dll_name name 'AxmInterruptGetUserEnable';
    function AxmInterruptSetCNTComparator; external dll_name name 'AxmInterruptSetCNTComparator';
    function AxmInterruptGetCNTComparator; external dll_name name 'AxmInterruptGetCNTComparator';
    function AxmMotLoadParaAll; external dll_name name 'AxmMotLoadParaAll';
    function AxmMotSaveParaAll; external dll_name name 'AxmMotSaveParaAll';
    function AxmMotSetParaLoad; external dll_name name 'AxmMotSetParaLoad';
    function AxmMotGetParaLoad; external dll_name name 'AxmMotGetParaLoad';
    function AxmMotSetPulseOutMethod; external dll_name name 'AxmMotSetPulseOutMethod';
    function AxmMotGetPulseOutMethod; external dll_name name 'AxmMotGetPulseOutMethod';
    function AxmMotSetEncInputMethod; external dll_name name 'AxmMotSetEncInputMethod';
    function AxmMotGetEncInputMethod; external dll_name name 'AxmMotGetEncInputMethod';
    function AxmMotSetMoveUnitPerPulse; external dll_name name 'AxmMotSetMoveUnitPerPulse';
    function AxmMotGetMoveUnitPerPulse; external dll_name name 'AxmMotGetMoveUnitPerPulse';
    function AxmMotSetDecelMode; external dll_name name 'AxmMotSetDecelMode';
    function AxmMotGetDecelMode; external dll_name name 'AxmMotGetDecelMode';
    function AxmMotSetRemainPulse; external dll_name name 'AxmMotSetRemainPulse';
    function AxmMotGetRemainPulse; external dll_name name 'AxmMotGetRemainPulse';
    function AxmMotSetMaxVel; external dll_name name 'AxmMotSetMaxVel';
    function AxmMotGetMaxVel; external dll_name name 'AxmMotGetMaxVel';
    function AxmMotSetAbsRelMode; external dll_name name 'AxmMotSetAbsRelMode';
    function AxmMotGetAbsRelMode; external dll_name name 'AxmMotGetAbsRelMode';
    function AxmMotSetProfileMode; external dll_name name 'AxmMotSetProfileMode';
    function AxmMotGetProfileMode; external dll_name name 'AxmMotGetProfileMode';
    function AxmMotSetAccelUnit; external dll_name name 'AxmMotSetAccelUnit';
    function AxmMotGetAccelUnit; external dll_name name 'AxmMotGetAccelUnit';
    function AxmMotSetMinVel; external dll_name name 'AxmMotSetMinVel';
    function AxmMotGetMinVel; external dll_name name 'AxmMotGetMinVel';
    function AxmMotSetAccelJerk; external dll_name name 'AxmMotSetAccelJerk';
    function AxmMotGetAccelJerk; external dll_name name 'AxmMotGetAccelJerk';
    function AxmMotSetDecelJerk; external dll_name name 'AxmMotSetDecelJerk';
    function AxmMotGetDecelJerk; external dll_name name 'AxmMotGetDecelJerk';
    function AxmMotSetProfilePriority; external dll_name name 'AxmMotSetProfilePriority';
    function AxmMotGetProfilePriority; external dll_name name 'AxmMotGetProfilePriority';
    function AxmSignalSetZphaseLevel; external dll_name name 'AxmSignalSetZphaseLevel';
    function AxmSignalGetZphaseLevel; external dll_name name 'AxmSignalGetZphaseLevel';
    function AxmSignalSetServoOnLevel; external dll_name name 'AxmSignalSetServoOnLevel';
    function AxmSignalGetServoOnLevel; external dll_name name 'AxmSignalGetServoOnLevel';
    function AxmSignalSetServoAlarmResetLevel; external dll_name name 'AxmSignalSetServoAlarmResetLevel';
    function AxmSignalGetServoAlarmResetLevel; external dll_name name 'AxmSignalGetServoAlarmResetLevel';
    function AxmSignalSetInpos; external dll_name name 'AxmSignalSetInpos';
    function AxmSignalGetInpos; external dll_name name 'AxmSignalGetInpos';
    function AxmSignalReadInpos; external dll_name name 'AxmSignalReadInpos';
    function AxmSignalSetServoAlarm; external dll_name name 'AxmSignalSetServoAlarm';
    function AxmSignalGetServoAlarm; external dll_name name 'AxmSignalGetServoAlarm';
    function AxmSignalReadServoAlarm; external dll_name name 'AxmSignalReadServoAlarm';
    function AxmSignalSetLimit; external dll_name name 'AxmSignalSetLimit';
    function AxmSignalGetLimit; external dll_name name 'AxmSignalGetLimit';
    function AxmSignalReadLimit; external dll_name name 'AxmSignalReadLimit';
    function AxmSignalSetSoftLimit; external dll_name name 'AxmSignalSetSoftLimit';
    function AxmSignalGetSoftLimit; external dll_name name 'AxmSignalGetSoftLimit';
    function AxmSignalReadSoftLimit; external dll_name name 'AxmSignalReadSoftLimit';
    function AxmSignalSetStop; external dll_name name 'AxmSignalSetStop';
    function AxmSignalGetStop; external dll_name name 'AxmSignalGetStop';
    function AxmSignalReadStop; external dll_name name 'AxmSignalReadStop';
    function AxmSignalServoOn; external dll_name name 'AxmSignalServoOn';
    function AxmSignalIsServoOn; external dll_name name 'AxmSignalIsServoOn';
    function AxmSignalServoAlarmReset; external dll_name name 'AxmSignalServoAlarmReset';
    function AxmSignalWriteOutput; external dll_name name 'AxmSignalWriteOutput';
    function AxmSignalReadOutput; external dll_name name 'AxmSignalReadOutput';
    function AxmSignalReadBrakeOn; external dll_name name 'AxmSignalReadBrakeOn';
    function AxmSignalWriteOutputBit; external dll_name name 'AxmSignalWriteOutputBit';
    function AxmSignalReadOutputBit; external dll_name name 'AxmSignalReadOutputBit';
    function AxmSignalReadInput; external dll_name name 'AxmSignalReadInput';
    function AxmSignalReadInputBit; external dll_name name 'AxmSignalReadInputBit';
    function AxmSignalSetFilterBandwidth; external dll_name name 'AxmSignalSetFilterBandwidth';
    function AxmSignalOutputOn; external dll_name name 'AxmSignalOutputOn';
    function AxmSignalOutputOff; external dll_name name 'AxmSignalOutputOff';
    function AxmStatusReadInMotion; external dll_name name 'AxmStatusReadInMotion';
    function AxmStatusReadDrivePulseCount; external dll_name name 'AxmStatusReadDrivePulseCount';
    function AxmStatusReadMotion; external dll_name name 'AxmStatusReadMotion';
    function AxmStatusReadStop; external dll_name name 'AxmStatusReadStop';
    function AxmStatusReadMechanical; external dll_name name 'AxmStatusReadMechanical';
    function AxmStatusReadVel; external dll_name name 'AxmStatusReadVel';
    function AxmStatusReadPosError; external dll_name name 'AxmStatusReadPosError';
    function AxmStatusReadDriveDistance; external dll_name name 'AxmStatusReadDriveDistance';
    function AxmStatusSetPosType; external dll_name name 'AxmStatusSetPosType';
    function AxmStatusGetPosType; external dll_name name 'AxmStatusGetPosType';
    function AxmStatusSetAbsOrgOffset; external dll_name name 'AxmStatusSetAbsOrgOffset';
    function AxmStatusSetActPos; external dll_name name 'AxmStatusSetActPos';
    function AxmStatusGetActPos; external dll_name name 'AxmStatusGetActPos';
    function AxmStatusGetAmpActPos; external dll_name name 'AxmStatusGetAmpActPos';
    function AxmStatusSetCmdPos; external dll_name name 'AxmStatusSetCmdPos';
    function AxmStatusGetCmdPos; external dll_name name 'AxmStatusGetCmdPos';
    function AxmStatusSetPosMatch; external dll_name name 'AxmStatusSetPosMatch';
    function AxmStatusReadMotionInfo; external dll_name name 'AxmStatusReadMotionInfo';
    function AxmStatusRequestServoAlarm; external dll_name name 'AxmStatusRequestServoAlarm';
    function AxmStatusReadServoAlarm; external dll_name name 'AxmStatusReadServoAlarm';
    function AxmStatusGetServoAlarmString; external dll_name name 'AxmStatusGetServoAlarmString';
    function AxmStatusRequestServoAlarmHistory; external dll_name name 'AxmStatusRequestServoAlarmHistory';
    function AxmStatusReadServoAlarmHistory; external dll_name name 'AxmStatusReadServoAlarmHistory';
    function AxmStatusClearServoAlarmHistory; external dll_name name 'AxmStatusClearServoAlarmHistory';
    function AxmHomeSetSignalLevel; external dll_name name 'AxmHomeSetSignalLevel';
    function AxmHomeGetSignalLevel; external dll_name name 'AxmHomeGetSignalLevel';
    function AxmHomeReadSignal; external dll_name name 'AxmHomeReadSignal';
    function AxmHomeSetMethod; external dll_name name 'AxmHomeSetMethod';
    function AxmHomeGetMethod; external dll_name name 'AxmHomeGetMethod';
    function AxmHomeSetFineAdjust; external dll_name name 'AxmHomeSetFineAdjust';
    function AxmHomeGetFineAdjust; external dll_name name 'AxmHomeGetFineAdjust';
    function AxmHomeSetInterlock; external dll_name name 'AxmHomeSetInterlock';
    function AxmHomeGetInterlock; external dll_name name 'AxmHomeGetInterlock';
    function AxmHomeSetVel; external dll_name name 'AxmHomeSetVel';
    function AxmHomeGetVel; external dll_name name 'AxmHomeGetVel';
    function AxmHomeSetStart; external dll_name name 'AxmHomeSetStart';
    function AxmHomeSetResult; external dll_name name 'AxmHomeSetResult';
    function AxmHomeGetResult; external dll_name name 'AxmHomeGetResult';
    function AxmHomeGetRate; external dll_name name 'AxmHomeGetRate';
    function AxmMoveStartPos; external dll_name name 'AxmMoveStartPos';
    function AxmMovePos; external dll_name name 'AxmMovePos';
    function AxmMoveVel; external dll_name name 'AxmMoveVel';
    function AxmMoveStartMultiVel; external dll_name name 'AxmMoveStartMultiVel';
    function AxmMoveStartMultiVelEx; external dll_name name 'AxmMoveStartMultiVelEx';
    function AxmMoveStartLineVel; external dll_name name 'AxmMoveStartLineVel';
    function AxmMoveSignalSearch; external dll_name name 'AxmMoveSignalSearch';
    function AxmMoveSignalSearchAtDis; external dll_name name 'AxmMoveSignalSearchAtDis';
    function AxmMoveSignalCapture; external dll_name name 'AxmMoveSignalCapture';
    function AxmMoveGetCapturePos; external dll_name name 'AxmMoveGetCapturePos';
    function AxmMoveStartMultiPos; external dll_name name 'AxmMoveStartMultiPos';
    function AxmMoveMultiPos; external dll_name name 'AxmMoveMultiPos';
    function AxmMoveStartTorque; external dll_name name 'AxmMoveStartTorque';
    function AxmMoveTorqueStop; external dll_name name 'AxmMoveTorqueStop';
    function AxmMoveStartPosWithList; external dll_name name 'AxmMoveStartPosWithList';
    function AxmMoveStartPosWithPosEvent; external dll_name name 'AxmMoveStartPosWithPosEvent';
    function AxmMoveStop; external dll_name name 'AxmMoveStop';
    function AxmMoveStopEx; external dll_name name 'AxmMoveStopEx';
    function AxmMoveEStop; external dll_name name 'AxmMoveEStop';
    function AxmMoveSStop; external dll_name name 'AxmMoveSStop';
    function AxmOverridePos; external dll_name name 'AxmOverridePos';
    function AxmOverrideSetMaxVel; external dll_name name 'AxmOverrideSetMaxVel';
    function AxmOverrideVel; external dll_name name 'AxmOverrideVel';
    function AxmOverrideAccelVelDecel; external dll_name name 'AxmOverrideAccelVelDecel';
    function AxmOverrideVelAtPos; external dll_name name 'AxmOverrideVelAtPos';
    function AxmOverrideVelAtMultiPos; external dll_name name 'AxmOverrideVelAtMultiPos';
    function AxmOverrideVelAtMultiPos2; external dll_name name 'AxmOverrideVelAtMultiPos2';
    function AxmOverrideAccelVelDecelAtMultiPos; external dll_name name 'AxmOverrideAccelVelDecelAtMultiPos';
    function AxmOverrideMultiVel; external dll_name name 'AxmOverrideMultiVel';
    function AxmLinkSetMode; external dll_name name 'AxmLinkSetMode';
    function AxmLinkGetMode; external dll_name name 'AxmLinkGetMode';
    function AxmLinkResetMode; external dll_name name 'AxmLinkResetMode';
    function AxmGantrySetEnable; external dll_name name 'AxmGantrySetEnable';
    function AxmGantryGetEnable; external dll_name name 'AxmGantryGetEnable';
    function AxmGantrySetDisable; external dll_name name 'AxmGantrySetDisable';
    function AxmGantrySetCompensationGain; external dll_name name 'AxmGantrySetCompensationGain';
    function AxmGantryGetCompensationGain; external dll_name name 'AxmGantryGetCompensationGain';
    function AxmGantrySetErrorRange; external dll_name name 'AxmGantrySetErrorRange';
    function AxmGantryGetErrorRange; external dll_name name 'AxmGantryGetErrorRange';
    function AxmGantryReadErrorRangeStatus; external dll_name name 'AxmGantryReadErrorRangeStatus';
    function AxmGantryReadErrorRangeComparePos; external dll_name name 'AxmGantryReadErrorRangeComparePos';
    function AxmLineMove; external dll_name name 'AxmLineMove';
    function AxmLineMoveEx2; external dll_name name 'AxmLineMoveEx2';
    function AxmCircleCenterMove; external dll_name name 'AxmCircleCenterMove';
    function AxmCirclePointMove; external dll_name name 'AxmCirclePointMove';
    function AxmCircleRadiusMove; external dll_name name 'AxmCircleRadiusMove';
    function AxmCircleAngleMove; external dll_name name 'AxmCircleAngleMove';
    function AxmContiSetAxisMap; external dll_name name 'AxmContiSetAxisMap';
    function AxmContiGetAxisMap; external dll_name name 'AxmContiGetAxisMap';
    function AxmContiResetAxisMap; external dll_name name 'AxmContiResetAxisMap';
    function AxmContiSetAbsRelMode; external dll_name name 'AxmContiSetAbsRelMode';
    function AxmContiGetAbsRelMode; external dll_name name 'AxmContiGetAbsRelMode';
    function AxmContiReadFree; external dll_name name 'AxmContiReadFree';
    function AxmContiReadIndex; external dll_name name 'AxmContiReadIndex';
    function AxmContiWriteClear; external dll_name name 'AxmContiWriteClear';
    function AxmContiBeginNode; external dll_name name 'AxmContiBeginNode';
    function AxmContiEndNode; external dll_name name 'AxmContiEndNode';
    function AxmContiStart; external dll_name name 'AxmContiStart';
    function AxmContiIsMotion; external dll_name name 'AxmContiIsMotion';
    function AxmContiGetNodeNum; external dll_name name 'AxmContiGetNodeNum';
    function AxmContiGetTotalNodeNum; external dll_name name 'AxmContiGetTotalNodeNum';
    function AxmContiDigitalOutputBit; external dll_name name 'AxmContiDigitalOutputBit';
    function AxmContiSetConnectionRadius; external dll_name name 'AxmContiSetConnectionRadius';
    function AxmTriggerSetTimeLevel; external dll_name name 'AxmTriggerSetTimeLevel';
    function AxmTriggerGetTimeLevel; external dll_name name 'AxmTriggerGetTimeLevel';
    function AxmTriggerSetAbsPeriod; external dll_name name 'AxmTriggerSetAbsPeriod';
    function AxmTriggerGetAbsPeriod; external dll_name name 'AxmTriggerGetAbsPeriod';
    function AxmTriggerSetBlock; external dll_name name 'AxmTriggerSetBlock';
    function AxmTriggerGetBlock; external dll_name name 'AxmTriggerGetBlock';
    function AxmTriggerOneShot; external dll_name name 'AxmTriggerOneShot';
    function AxmTriggerSetTimerOneshot; external dll_name name 'AxmTriggerSetTimerOneshot';
    function AxmTriggerOnlyAbs; external dll_name name 'AxmTriggerOnlyAbs';
    function AxmTriggerSetReset; external dll_name name 'AxmTriggerSetReset';
    function AxmTriggerSetPoint; external dll_name name 'AxmTriggerSetPoint';
    function AxmTriggerGetPoint; external dll_name name 'AxmTriggerGetPoint';
    function AxmTriggerSetPointClear; external dll_name name 'AxmTriggerSetPointClear';
    function AxmCrcSetMaskLevel; external dll_name name 'AxmCrcSetMaskLevel';
    function AxmCrcGetMaskLevel; external dll_name name 'AxmCrcGetMaskLevel';
    function AxmCrcSetOutput; external dll_name name 'AxmCrcSetOutput';
    function AxmCrcGetOutput; external dll_name name 'AxmCrcGetOutput';
    function AxmMPGSetEnable; external dll_name name 'AxmMPGSetEnable';
    function AxmMPGGetEnable; external dll_name name 'AxmMPGGetEnable';
    function AxmMPGSetRatio; external dll_name name 'AxmMPGSetRatio';
    function AxmMPGGetRatio; external dll_name name 'AxmMPGGetRatio';
    function AxmMPGReset; external dll_name name 'AxmMPGReset';
    function AxmHelixCenterMove; external dll_name name 'AxmHelixCenterMove';
    function AxmHelixPointMove; external dll_name name 'AxmHelixPointMove';
    function AxmHelixRadiusMove; external dll_name name 'AxmHelixRadiusMove';
    function AxmHelixAngleMove; external dll_name name 'AxmHelixAngleMove';
    function AxmHelixPitchMove; external dll_name name 'AxmHelixPitchMove';
    function AxmSplineWrite; external dll_name name 'AxmSplineWrite';
    function AxmCompensationSet; external dll_name name 'AxmCompensationSet';
    function AxmCompensationGet; external dll_name name 'AxmCompensationGet';
    function AxmCompensationEnable; external dll_name name 'AxmCompensationEnable';
    function AxmCompensationIsEnable; external dll_name name 'AxmCompensationIsEnable';
    function AxmCompensationGetCorrection; external dll_name name 'AxmCompensationGetCorrection';
    function AxmCompensationSetBacklash; external dll_name name 'AxmCompensationSetBacklash';
    function AxmCompensationGetBacklash; external dll_name name 'AxmCompensationGetBacklash';
    function AxmCompensationEnableBacklash; external dll_name name 'AxmCompensationEnableBacklash';
    function AxmCompensationIsEnableBacklash; external dll_name name 'AxmCompensationIsEnableBacklash';
    function AxmCompensationSetLocating; external dll_name name 'AxmCompensationSetLocating';
    function AxmEcamSet; external dll_name name 'AxmEcamSet';
    function AxmEcamSetWithSource; external dll_name name 'AxmEcamSetWithSource';
    function AxmEcamGet; external dll_name name 'AxmEcamGet';
    function AxmEcamGetWithSource; external dll_name name 'AxmEcamGetWithSource';
    function AxmEcamEnableBySlave; external dll_name name 'AxmEcamEnableBySlave';
    function AxmEcamEnableByMaster; external dll_name name 'AxmEcamEnableByMaster';
    function AxmEcamIsSlaveEnable; external dll_name name 'AxmEcamIsSlaveEnable';
    function AxmStatusSetServoMonitor; external dll_name name 'AxmStatusSetServoMonitor';
    function AxmStatusGetServoMonitor; external dll_name name 'AxmStatusGetServoMonitor';
    function AxmStatusSetServoMonitorEnable; external dll_name name 'AxmStatusSetServoMonitorEnable';
    function AxmStatusGetServoMonitorEnable; external dll_name name 'AxmStatusGetServoMonitorEnable';
    function AxmStatusReadServoMonitorFlag; external dll_name name 'AxmStatusReadServoMonitorFlag';
    function AxmStatusReadServoMonitorValue; external dll_name name 'AxmStatusReadServoMonitorValue';
    function AxmStatusSetReadServoLoadRatio; external dll_name name 'AxmStatusSetReadServoLoadRatio';
    function AxmStatusReadServoLoadRatio; external dll_name name 'AxmStatusReadServoLoadRatio';
    function AxmMotSetScaleCoeff; external dll_name name 'AxmMotSetScaleCoeff';
    function AxmMotGetScaleCoeff; external dll_name name 'AxmMotGetScaleCoeff';
    function AxmMoveSignalSearchEx; external dll_name name 'AxmMoveSignalSearchEx';
    function AxmMoveToAbsPos; external dll_name name 'AxmMoveToAbsPos';
    function AxmStatusReadVelEx; external dll_name name 'AxmStatusReadVelEx';
    function AxmMotSetElectricGearRatio; external dll_name name 'AxmMotSetElectricGearRatio';
    function AxmMotGetElectricGearRatio; external dll_name name 'AxmMotGetElectricGearRatio';
    function AxmMotSetTorqueLimit; external dll_name name 'AxmMotSetTorqueLimit';
    function AxmMotGetTorqueLimit; external dll_name name 'AxmMotGetTorqueLimit';
    function AxmMotSetTorqueLimitEx; external dll_name name 'AxmMotSetTorqueLimitEx';
    function AxmMotGetTorqueLimitEx; external dll_name name 'AxmMotGetTorqueLimitEx';
    function AxmMotSetTorqueLimitAtPos; external dll_name name 'AxmMotSetTorqueLimitAtPos';
    function AxmMotGetTorqueLimitAtPos; external dll_name name 'AxmMotGetTorqueLimitAtPos';
    function AxmMotSetTorqueLimitEnable; external dll_name name 'AxmMotSetTorqueLimitEnable';
    function AxmMotGetTorqueLimitEnable; external dll_name name 'AxmMotGetTorqueLimitEnable';
    function AxmOverridePosSetFunction; external dll_name name 'AxmOverridePosSetFunction';
    function AxmOverridePosGetFunction; external dll_name name 'AxmOverridePosGetFunction';
    function AxmSignalSetWriteOutputBitAtPos; external dll_name name 'AxmSignalSetWriteOutputBitAtPos';
    function AxmSignalGetWriteOutputBitAtPos; external dll_name name 'AxmSignalGetWriteOutputBitAtPos';
    function AxmAdvVSTSetParameter; external dll_name name 'AxmAdvVSTSetParameter';
    function AxmAdvVSTGetParameter; external dll_name name 'AxmAdvVSTGetParameter';
    function AxmAdvVSTSetEnabele; external dll_name name 'AxmAdvVSTSetEnabele';
    function AxmAdvVSTGetEnabele; external dll_name name 'AxmAdvVSTGetEnabele';
    function AxmAdvLineMove; external dll_name name 'AxmAdvLineMove';
    function AxmAdvOvrLineMove; external dll_name name 'AxmAdvOvrLineMove';
    function AxmAdvCircleCenterMove; external dll_name name 'AxmAdvCircleCenterMove';
    function AxmAdvCirclePointMove; external dll_name name 'AxmAdvCirclePointMove';
    function AxmAdvCircleAngleMove; external dll_name name 'AxmAdvCircleAngleMove';
    function AxmAdvCircleRadiusMove; external dll_name name 'AxmAdvCircleRadiusMove';
    function AxmAdvOvrCircleRadiusMove; external dll_name name 'AxmAdvOvrCircleRadiusMove';
    function AxmAdvHelixCenterMove; external dll_name name 'AxmAdvHelixCenterMove';
    function AxmAdvHelixPointMove; external dll_name name 'AxmAdvHelixPointMove';
    function AxmAdvHelixAngleMove; external dll_name name 'AxmAdvHelixAngleMove';
    function AxmAdvHelixRadiusMove; external dll_name name 'AxmAdvHelixRadiusMove';
    function AxmAdvOvrHelixRadiusMove; external dll_name name 'AxmAdvOvrHelixRadiusMove';
    function AxmAdvScriptLineMove; external dll_name name 'AxmAdvScriptLineMove';
    function AxmAdvScriptOvrLineMove; external dll_name name 'AxmAdvScriptOvrLineMove';
    function AxmAdvScriptCircleCenterMove; external dll_name name 'AxmAdvScriptCircleCenterMove';
    function AxmAdvScriptCirclePointMove; external dll_name name 'AxmAdvScriptCirclePointMove';
    function AxmAdvScriptCircleAngleMove; external dll_name name 'AxmAdvScriptCircleAngleMove';
    function AxmAdvScriptCircleRadiusMove; external dll_name name 'AxmAdvScriptCircleRadiusMove';
    function AxmAdvScriptOvrCircleRadiusMove; external dll_name name 'AxmAdvScriptOvrCircleRadiusMove';
    function AxmAdvScriptHelixCenterMove; external dll_name name 'AxmAdvScriptHelixCenterMove';
    function AxmAdvScriptHelixPointMove; external dll_name name 'AxmAdvScriptHelixPointMove';
    function AxmAdvScriptHelixAngleMove; external dll_name name 'AxmAdvScriptHelixAngleMove';
    function AxmAdvScriptHelixRadiusMove; external dll_name name 'AxmAdvScriptHelixRadiusMove';
    function AxmAdvScriptOvrHelixRadiusMove; external dll_name name 'AxmAdvScriptOvrHelixRadiusMove';
    function AxmAdvContiGetNodeNum; external dll_name name 'AxmAdvContiGetNodeNum';
    function AxmAdvContiGetTotalNodeNum; external dll_name name 'AxmAdvContiGetTotalNodeNum';
    function AxmAdvContiReadIndex; external dll_name name 'AxmAdvContiReadIndex';
    function AxmAdvContiReadFree; external dll_name name 'AxmAdvContiReadFree';
    function AxmAdvContiWriteClear; external dll_name name 'AxmAdvContiWriteClear';
    function AxmAdvOvrContiWriteClear; external dll_name name 'AxmAdvOvrContiWriteClear';
    function AxmAdvContiStart; external dll_name name 'AxmAdvContiStart';
    function AxmAdvContiStop; external dll_name name 'AxmAdvContiStop';
    function AxmAdvContiSetAxisMap; external dll_name name 'AxmAdvContiSetAxisMap';
    function AxmAdvContiGetAxisMap; external dll_name name 'AxmAdvContiGetAxisMap';
    function AxmAdvContiSetAbsRelMode; external dll_name name 'AxmAdvContiSetAbsRelMode';
    function AxmAdvContiGetAbsRelMode; external dll_name name 'AxmAdvContiGetAbsRelMode';
    function AxmAdvContiIsMotion; external dll_name name 'AxmAdvContiIsMotion';
    function AxmAdvContiBeginNode; external dll_name name 'AxmAdvContiBeginNode';
    function AxmAdvContiEndNode; external dll_name name 'AxmAdvContiEndNode';
    function AxmMoveMultiStop; external dll_name name 'AxmMoveMultiStop';
    function AxmMoveMultiEStop; external dll_name name 'AxmMoveMultiEStop';
    function AxmMoveMultiSStop; external dll_name name 'AxmMoveMultiSStop';
    function AxmStatusReadActVel; external dll_name name 'AxmStatusReadActVel';
    function AxmStatusReadServoCmdStat; external dll_name name 'AxmStatusReadServoCmdStat';
    function AxmStatusReadServoCmdCtrl; external dll_name name 'AxmStatusReadServoCmdCtrl';
    function AxmGantryGetMstToSlvOverDist; external dll_name name 'AxmGantryGetMstToSlvOverDist';
    function AxmGantrySetMstToSlvOverDist; external dll_name name 'AxmGantrySetMstToSlvOverDist';
    function AxmSignalReadServoAlarmCode; external dll_name name 'AxmSignalReadServoAlarmCode';
    function AxmM3ServoCoordinatesSet; external dll_name name 'AxmM3ServoCoordinatesSet';
    function AxmM3ServoBreakOn; external dll_name name 'AxmM3ServoBreakOn';
    function AxmM3ServoBreakOff; external dll_name name 'AxmM3ServoBreakOff';
    function AxmM3ServoConfig; external dll_name name 'AxmM3ServoConfig';
    function AxmM3ServoSensOn; external dll_name name 'AxmM3ServoSensOn';
    function AxmM3ServoSensOff; external dll_name name 'AxmM3ServoSensOff';
    function AxmM3ServoSmon; external dll_name name 'AxmM3ServoSmon';
    function AxmM3ServoGetSmon; external dll_name name 'AxmM3ServoGetSmon';
    function AxmM3ServoSvOn; external dll_name name 'AxmM3ServoSvOn';
    function AxmM3ServoSvOff; external dll_name name 'AxmM3ServoSvOff';
    function AxmM3ServoInterpolate; external dll_name name 'AxmM3ServoInterpolate';
    function AxmM3ServoPosing; external dll_name name 'AxmM3ServoPosing';
    function AxmM3ServoFeed; external dll_name name 'AxmM3ServoFeed';
    function AxmM3ServoExFeed; external dll_name name 'AxmM3ServoExFeed';
    function AxmM3ServoExPosing; external dll_name name 'AxmM3ServoExPosing';
    function AxmM3ServoZret; external dll_name name 'AxmM3ServoZret';
    function AxmM3ServoVelctrl; external dll_name name 'AxmM3ServoVelctrl';
    function AxmM3ServoTrqctrl; external dll_name name 'AxmM3ServoTrqctrl';
    function AxmM3ServoGetParameter; external dll_name name 'AxmM3ServoGetParameter';
    function AxmM3ServoSetParameter; external dll_name name 'AxmM3ServoSetParameter';
    function AxmServoCmdExecution; external dll_name name 'AxmServoCmdExecution';
    function AxmM3ServoGetTorqLimit; external dll_name name 'AxmM3ServoGetTorqLimit';
    function AxmM3ServoSetTorqLimit; external dll_name name 'AxmM3ServoSetTorqLimit';
    function AxmM3ServoGetSendSvCmdIOOutput; external dll_name name 'AxmM3ServoGetSendSvCmdIOOutput';
    function AxmM3ServoSetSendSvCmdIOOutput; external dll_name name 'AxmM3ServoSetSendSvCmdIOOutput';
    function AxmM3ServoGetSvCmdCtrl; external dll_name name 'AxmM3ServoGetSvCmdCtrl';
    function AxmM3ServoSetSvCmdCtrl; external dll_name name 'AxmM3ServoSetSvCmdCtrl';
    function AxmM3AdjustmentOperation; external dll_name name 'AxmM3AdjustmentOperation';
    function AxmM3ServoSetMonSel; external dll_name name 'AxmM3ServoSetMonSel';
    function AxmM3ServoGetMonSel; external dll_name name 'AxmM3ServoGetMonSel';
    function AxmM3ServoReadMonData; external dll_name name 'AxmM3ServoReadMonData';
    function AxmAdvTorqueContiSetAxisMap; external dll_name name 'AxmAdvTorqueContiSetAxisMap';
    function AxmM3ServoSetTorqProfile; external dll_name name 'AxmM3ServoSetTorqProfile';
    function AxmM3ServoGetTorqProfile; external dll_name name 'AxmM3ServoGetTorqProfile';
    function AxmSignalSetInposRange; external dll_name name 'AxmSignalSetInposRange';
    function AxmSignalGetInposRange; external dll_name name 'AxmSignalGetInposRange';
    function AxmMotSetOverridePosMode; external dll_name name 'AxmMotSetOverridePosMode';
    function AxmMotGetOverridePosMode; external dll_name name 'AxmMotGetOverridePosMode';
    function AxmMotSetOverrideLinePosMode; external dll_name name 'AxmMotSetOverrideLinePosMode';
    function AxmMotGetOverrideLinePosMode; external dll_name name 'AxmMotGetOverrideLinePosMode';
    function AxmMoveStartPosEx; external dll_name name 'AxmMoveStartPosEx';
    function AxmMovePosEx; external dll_name name 'AxmMovePosEx';
    function AxmMoveCoordStop; external dll_name name 'AxmMoveCoordStop';
    function AxmMoveCoordEStop; external dll_name name 'AxmMoveCoordEStop';
    function AxmMoveCoordSStop; external dll_name name 'AxmMoveCoordSStop';
    function AxmOverrideLinePos; external dll_name name 'AxmOverrideLinePos';
    function AxmOverrideLineVel; external dll_name name 'AxmOverrideLineVel';
    function AxmOverrideLineAccelVelDecel; external dll_name name 'AxmOverrideLineAccelVelDecel';
    function AxmOverrideAccelVelDecelAtPos; external dll_name name 'AxmOverrideAccelVelDecelAtPos';
    function AxmEGearSet; external dll_name name 'AxmEGearSet';
    function AxmEGearGet; external dll_name name 'AxmEGearGet';
    function AxmEGearReset; external dll_name name 'AxmEGearReset';
    function AxmEGearEnable; external dll_name name 'AxmEGearEnable';
    function AxmEGearIsEnable; external dll_name name 'AxmEGearIsEnable';
    function AxmMotSetEndVel; external dll_name name 'AxmMotSetEndVel';
    function AxmMotGetEndVel; external dll_name name 'AxmMotGetEndVel';
    function AxmLineMoveWithAxes; external dll_name name 'AxmLineMoveWithAxes';
    function AxmCircleCenterMoveWithAxes; external dll_name name 'AxmCircleCenterMoveWithAxes';
    function AxmCircleRadiusMoveWithAxes; external dll_name name 'AxmCircleRadiusMoveWithAxes';
    function AxmCircleAngleMoveWithAxes; external dll_name name 'AxmCircleAngleMoveWithAxes';
    function AxmCirclePointMoveWithAxes; external dll_name name 'AxmCirclePointMoveWithAxes';
    function AxmLineMoveWithAxesWithEvent; external dll_name name 'AxmLineMoveWithAxesWithEvent';
    function AxmCircleCenterMoveWithAxesWithEvent; external dll_name name 'AxmCircleCenterMoveWithAxesWithEvent';
    function AxmFilletMove; external dll_name name 'AxmFilletMove';
    function AxmMovePVT; external dll_name name 'AxmMovePVT';
    function AxmSyncSetAxisMap; external dll_name name 'AxmSyncSetAxisMap';
    function AxmSyncClear; external dll_name name 'AxmSyncClear';
    function AxmSyncBegin; external dll_name name 'AxmSyncBegin';
    function AxmSyncEnd; external dll_name name 'AxmSyncEnd';
    function AxmSyncStart; external dll_name name 'AxmSyncStart';
    function AxmStatusReadRemainQueueCount; external dll_name name 'AxmStatusReadRemainQueueCount';
