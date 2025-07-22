"""
AJINEXTEK AXL Library Error Codes

This module contains all error codes and descriptions from the AXL library.
"""

# ============================================================================
# General Return Codes
# ============================================================================

# Success
AXT_RT_SUCCESS = 0x0000  # 함수 실행 성공

# Library Open/Close Errors (1000-1099)
AXT_RT_OPEN_ERROR = 1001  # 라이브러리가 오픈 되어있지 않음
AXT_RT_OPEN_ALREADY = 1002  # 라이브러리가 오픈 되어있고 사용 중임
AXT_RT_NOT_INITIAL = 1052  # Serial module이 초기화되어있지 않음
AXT_RT_NOT_OPEN = 1053  # 라이브러리 초기화 실패
AXT_RT_NOT_SUPPORT_VERSION = 1054  # 지원하지않는 하드웨어
AXT_RT_LOCK_FILE_MISMATCH = 1055  # Lock파일과 현재 Scan정보가 일치하지 않음
AXT_RT_MASTER_VERSION_MISMATCH = 1056  # Library와 EtherCAT Master 버젼이 일치하지 않음
AXT_RT_NOT_RUN_EZMANAGER = 1057  # EzManager가 실행되지않음
AXT_RT_NOT_FIND_BIN_FILE = 1058  # BIN 파일을 찾을 수 없음
AXT_RT_NOT_FIND_ENI_FILE = 1059  # ENI 파일을 찾을 수 없음
AXT_RT_NOT_FIND_CONFIG_FILE = 1060  # Config 파일을 찾을 수 없음
AXT_RT_RTOS_OPEN_ERROR = 1061  # RTOS Open 실패
AXT_RT_SLAVE_CONFIG_ERROR = 1062  # RTOS Slave Config 실패
AXT_RT_SLAVE_OP_TIMEOUT_WARNING = 1063  # Slave들이 OP 모드가 될 때까지 대기중 Timeout이 발생
AXT_RT_SLAVE_NOT_OP = 1064  # OP 모드가 아닌 Slave가 존재함
AXT_RT_RESCAN_NOT_EXIST_BOARD = 1065  # 보드가 존재하지 않음
AXT_RT_RESCAN_TIMEOUT = 1066  # Rescan 명령 후 대기 시간 초과

# Parameter Errors (1070-1099)
AXT_RT_BAD_PARAMETER = 1070  # 사용자가 입력한 파라미터가 적절하지 않음

# Hardware Validation Errors (1100-1159)
AXT_RT_INVALID_HARDWARE = 1100  # 유효하지 않는 보드
AXT_RT_INVALID_BOARD_NO = 1101  # 유효하지 않는 보드 번호
AXT_RT_INVALID_MODULE_POS = 1102  # 유효하지 않는 모듈 위치
AXT_RT_INVALID_LEVEL = 1103  # 유효하지 않는 레벨
AXT_RT_INVALID_VARIABLE = 1104  # 유효하지 않는 변수
AXT_RT_INVALID_MODULE_NO = 1105  # 유효하지 않는 모듈
AXT_RT_INVALID_NO = 1106  # 유효하지 않는 번호
AXT_RT_ERROR_VERSION_READ = 1151  # 라이브러리 버전을 읽을수 없음
AXT_RT_NETWORK_ERROR = 1152  # 하드웨어 네트워크 에러
AXT_RT_NETWORK_LOCK_MISMATCH = 1153  # 보드 Lock정보와 현재 Scan정보가 일치하지 않음

# Parameter Range Errors (1160-1259)
AXT_RT_1ST_BELOW_MIN_VALUE = 1160  # 첫번째 인자값이 최소값보다 더 작음
AXT_RT_1ST_ABOVE_MAX_VALUE = 1161  # 첫번째 인자값이 최대값보다 더 큼
AXT_RT_2ND_BELOW_MIN_VALUE = 1170  # 두번째 인자값이 최소값보다 더 작음
AXT_RT_2ND_ABOVE_MAX_VALUE = 1171  # 두번째 인자값이 최대값보다 더 큼
AXT_RT_3RD_BELOW_MIN_VALUE = 1180  # 세번째 인자값이 최소값보다 더 작음
AXT_RT_3RD_ABOVE_MAX_VALUE = 1181  # 세번째 인자값이 최대값보다 더 큼
AXT_RT_4TH_BELOW_MIN_VALUE = 1190  # 네번째 인자값이 최소값보다 더 작음
AXT_RT_4TH_ABOVE_MAX_VALUE = 1191  # 네번째 인자값이 최대값보다 더 큼
AXT_RT_5TH_BELOW_MIN_VALUE = 1200  # 다섯번째 인자값이 최소값보다 더 작음
AXT_RT_5TH_ABOVE_MAX_VALUE = 1201  # 다섯번째 인자값이 최대값보다 더 큼
AXT_RT_6TH_BELOW_MIN_VALUE = 1210  # 여섯번째 인자값이 최소값보다 더 작음
AXT_RT_6TH_ABOVE_MAX_VALUE = 1211  # 여섯번째 인자값이 최대값보다 더 큼
AXT_RT_7TH_BELOW_MIN_VALUE = 1220  # 일곱번째 인자값이 최소값보다 더 작음
AXT_RT_7TH_ABOVE_MAX_VALUE = 1221  # 일곱번째 인자값이 최대값보다 더 큼
AXT_RT_8TH_BELOW_MIN_VALUE = 1230  # 여덟번째 인자값이 최소값보다 더 작음
AXT_RT_8TH_ABOVE_MAX_VALUE = 1231  # 여덟번째 인자값이 최대값보다 더 큼
AXT_RT_9TH_BELOW_MIN_VALUE = 1240  # 아홉번째 인자값이 최소값보다 더 작음
AXT_RT_9TH_ABOVE_MAX_VALUE = 1241  # 아홉번째 인자값이 최대값보다 더 큼
AXT_RT_10TH_BELOW_MIN_VALUE = 1250  # 열번째 인자값이 최소값보다 더 작음
AXT_RT_10TH_ABOVE_MAX_VALUE = 1251  # 열번째 인자값이 최대값보다 더 큼
AXT_RT_11TH_BELOW_MIN_VALUE = 1252  # 열한번째 인자값이 최소값보다 더 작음
AXT_RT_11TH_ABOVE_MAX_VALUE = 1253  # 열한번째 인자값이 최대값보다 더 큼
AXT_RT_WRONG_HOME_POS_DIR = 1254  # 잘못된 원점 검색 방향 설정(+)
AXT_RT_WRONG_HOME_NEG_DIR = 1255  # 잘못된 원점 검색 방향 설정(-)

# ============================================================================
# AIO (Analog I/O) Module Errors (2000-2199)
# ============================================================================

AXT_RT_AIO_OPEN_ERROR = 2001  # AIO 모듈 오픈실패
AXT_RT_AIO_NOT_MODULE = 2051  # AIO 모듈 없음
AXT_RT_AIO_NOT_EVENT = 2052  # AIO 이벤트 읽지 못함
AXT_RT_AIO_INVALID_MODULE_NO = 2101  # 유효하지않은 AIO모듈
AXT_RT_AIO_INVALID_CHANNEL_NO = 2102  # 유효하지않은 AIO채널번호
AXT_RT_AIO_INVALID_USE = 2106  # AIO 함수 사용못함
AXT_RT_AIO_INVALID_TRIGGER_MODE = 2107  # 유효하지않는 트리거 모드
AXT_RT_AIO_EXTERNAL_DATA_EMPTY = 2108  # 외부 데이터 값이 없을 경우
AXT_RT_AIO_INVALID_VALUE = 2109  # 유효하지않는 값 설정
AXT_RT_AIO_UPG_ALEADY_ENABLED = 2110  # AO UPG 기능 사용중 설정됨

# ============================================================================
# DIO (Digital I/O) Module Errors (3000-3199)
# ============================================================================

AXT_RT_DIO_OPEN_ERROR = 3001  # DIO 모듈 오픈실패
AXT_RT_DIO_NOT_MODULE = 3051  # DIO 모듈 없음
AXT_RT_DIO_NOT_INTERRUPT = 3052  # DIO 인터럽트 설정안됨
AXT_RT_DIO_INVALID_MODULE_NO = 3101  # 유효하지않는 DIO 모듈 번호
AXT_RT_DIO_INVALID_OFFSET_NO = 3102  # 유효하지않는 DIO OFFSET 번호
AXT_RT_DIO_INVALID_LEVEL = 3103  # 유효하지않는 DIO 레벨
AXT_RT_DIO_INVALID_MODE = 3104  # 유효하지않는 DIO 모드
AXT_RT_DIO_INVALID_VALUE = 3105  # 유효하지않는 값 설정
AXT_RT_DIO_INVALID_USE = 3106  # DIO 함수 사용못함
AXT_RT_DIO_INVALID_LINK = 3107  # DIO Link가 유효하지 않음
AXT_RT_DIO_INTERLOCK_NOT_ENABLED = 3108  # DIO InterLock 유효하지 않음
AXT_RT_DIO_INTERLOCK_NOT_SAME_BOARD = 3109  # Destination Module과 Source Module일 동일한 보드내에 있지 않음

# ============================================================================
# CNT (Counter) Module Errors (3200-3399)
# ============================================================================

AXT_RT_CNT_OPEN_ERROR = 3201  # CNT 모듈 오픈실패
AXT_RT_CNT_NOT_MODULE = 3251  # CNT 모듈 없음
AXT_RT_CNT_NOT_INTERRUPT = 3252  # CNT 인터럽트 설정안됨
AXT_RT_CNT_NOT_TRIGGER_ENABLE = 3253  # CNT Trigger 출력 기능이 활성화되어 있지 않음
AXT_RT_CNT_INVALID_MODULE_NO = 3301  # 유효하지않는 CNT 모듈 번호
AXT_RT_CNT_INVALID_CHANNEL_NO = 3302  # 유효하지않는 채널 번호
AXT_RT_CNT_INVALID_OFFSET_NO = 3303  # 유효하지않는 CNT OFFSET 번호
AXT_RT_CNT_INVALID_LEVEL = 3304  # 유효하지않는 CNT 레벨
AXT_RT_CNT_INVALID_MODE = 3305  # 유효하지않는 CNT 모드
AXT_RT_CNT_INVALID_VALUE = 3306  # 유효하지않는 값 설정
AXT_RT_CNT_INVALID_USE = 3307  # CNT 함수 사용못함
AXT_RT_CNT_CMD_EXE_TIMEOUT = 3308  # CNT 모듈 데이터입력 시간초과 했을 때
AXT_RT_CNT_INVALID_VELOCITY = 3309  # 유효하지않는 CNT 속도
AXT_RT_PROTECTED_DURING_PWMENABLE = 3310  # PWM Enable 되어 있는 상태에서 사용 못 함
AXT_RT_CNT_INVALID_TABLEPOS = 3311  # 유효하지 않은 CNT TABLE 번호
AXT_RT_CNT_DIMENSION_ERROR = 3312  # 해당 Dimension 설정 상태에서는 사용할 수 없음
AXT_RT_CNT_TRIGGEROUTPORT_ERROR = 3313  # 트리거출력포트 중복

# ============================================================================
# COM (Communication) Module Errors (3400-3599)
# ============================================================================

AXT_RT_COM_OPEN_ERROR = 3401  # COM 포트 오픈실패
AXT_RT_COM_NOT_OPEN = 3402  # COM 포트 오픈되지 않음
AXT_RT_COM_ALREADY_IN_USE = 3403  # COM 포트 사용중
AXT_RT_COM_NOT_MODULE = 3451  # COM 포트 없음
AXT_RT_COM_NOT_INTERRUPT = 3452  # COM 인터럽트 설정안됨
AXT_RT_COM_INVALID_MODULE_NO = 3501  # 유효하지않는 COM 모듈 번호
AXT_RT_COM_INVALID_PORT_NO = 3502  # 유효하지않는 채널 번호
AXT_RT_COM_INVALID_OFFSET_NO = 3503  # 유효하지않는 COM OFFSET 번호
AXT_RT_COM_INVALID_LEVEL = 3504  # 유효하지않는 COM 레벨
AXT_RT_COM_INVALID_MODE = 3505  # 유효하지않는 COM 모드
AXT_RT_COM_INVALID_VALUE = 3506  # 유효하지않는 값 설정
AXT_RT_COM_INVALID_USE = 3507  # COM 함수 사용못함
AXT_RT_COM_INVALID_BAUDRATE = 3508  # 유효하지않는 값 설정

# ============================================================================
# Motion Module Errors (4000-4999)
# ============================================================================

# Motion Open/Initialization Errors (4000-4099)
AXT_RT_MOTION_OPEN_ERROR = 4001  # 모션 라이브러리 Open 실패
AXT_RT_MOTION_NOT_MODULE = 4051  # 시스템에 장착된 모션 모듈이 없음
AXT_RT_MOTION_NOT_INTERRUPT = 4052  # 인터럽트 결과 읽기 실패
AXT_RT_MOTION_NOT_INITIAL_AXIS_NO = 4053  # 해당 축 모션 초기화 실패
AXT_RT_MOTION_NOT_IN_CONT_INTERPOL = 4054  # 연속 보간 구동 중이 아닌 상태에서 연속보간 중지 명령을 수행 하였음
AXT_RT_MOTION_NOT_PARA_READ = 4055  # 원점 구동 설정 파라미터 로드 실패

# Motion Parameter Validation Errors (4100-4149)
AXT_RT_MOTION_INVALID_AXIS_NO = 4101  # 해당 축이 존재하지 않음
AXT_RT_MOTION_INVALID_METHOD = 4102  # 해당 축 구동에 필요한 설정이 잘못됨
AXT_RT_MOTION_INVALID_USE = 4103  # 'uUse' 인자값이 잘못 설정됨
AXT_RT_MOTION_INVALID_LEVEL = 4104  # 'uLevel' 인자값이 잘못 설정됨
AXT_RT_MOTION_INVALID_BIT_NO = 4105  # 범용 입출력 해당 비트가 잘못 설정됨
AXT_RT_MOTION_INVALID_STOP_MODE = 4106  # 모션 정지 모드 설정값이 잘못됨
AXT_RT_MOTION_INVALID_TRIGGER_MODE = 4107  # 트리거 설정 모드가 잘못 설정됨
AXT_RT_MOTION_INVALID_TRIGGER_LEVEL = 4108  # 트리거 출력 레벨 설정이 잘못됨
AXT_RT_MOTION_INVALID_SELECTION = 4109  # 'uSelection' 인자가 COMMAND 또는 ACTUAL 이외의 값으로 설정되어 있음
AXT_RT_MOTION_INVALID_TIME = 4110  # Trigger 출력 시간값이 잘못 설정되어 있음
AXT_RT_MOTION_INVALID_FILE_LOAD = 4111  # 모션 설정값이 저장된 파일이 로드가 안됨
AXT_RT_MOTION_INVALID_FILE_SAVE = 4112  # 모션 설정값을 저장하는 파일 저장에 실패함
AXT_RT_MOTION_INVALID_VELOCITY = 4113  # 모션 구동 속도값이 0으로 설정되어 모션 에러 발생
AXT_RT_MOTION_INVALID_ACCELTIME = 4114  # 모션 구동 가속 시간값이 0으로 설정되어 모션 에러 발생
AXT_RT_MOTION_INVALID_PULSE_VALUE = 4115  # 모션 단위 설정 시 입력 펄스값이 0보다 작은값으로 설정됨
AXT_RT_MOTION_INVALID_NODE_NUMBER = 4116  # 위치나 속도 오버라이드 함수가 모션 정지 중에 실햄됨
AXT_RT_MOTION_INVALID_TARGET = 4117  # 다축 모션 정지 원인에 관한 플래그를 반환함
AXT_RT_ERROR_INVALID_SETTLING_TIME = 4118  # 설정 값이 Cycle Time 미만이거나, Cycle Time의 배수가 아닐 때

# Motion State Errors (4150-4199)
AXT_RT_MOTION_ERROR_IN_NONMOTION = 4151  # 모션 구동중이어야 되는데 모션 구동중이 아닐 때
AXT_RT_MOTION_ERROR_IN_MOTION = 4152  # 모션 구동 중에 다른 모션 구동 함수를 실행함
AXT_RT_MOTION_ERROR = 4153  # 다축 구동 정지 함수 실행 중 에러 발생함
AXT_RT_MOTION_ERROR_GANTRY_ENABLE = 4154  # 겐트리 enable이 되어있을 때
AXT_RT_MOTION_ERROR_GANTRY_AXIS = 4155  # 겐트리 축이 마스터채널(축) 번호(0 ~ (최대축수 - 1))가 잘못 들어갔을 때
AXT_RT_MOTION_ERROR_MASTER_SERVOON = 4156  # 마스터 축 서보온이 안되어있을 때
AXT_RT_MOTION_ERROR_SLAVE_SERVOON = 4157  # 슬레이브 축 서보온이 안되어있을 때
AXT_RT_MOTION_INVALID_POSITION = 4158  # 유효한 위치에 없을 때
AXT_RT_ERROR_NOT_SAME_MODULE = 4159  # 똑 같은 모듈내에 있지 않을경우
AXT_RT_ERROR_NOT_SAME_BOARD = 4160  # 똑 같은 보드내에 있지 아닐경우
AXT_RT_ERROR_NOT_SAME_PRODUCT = 4161  # 제품이 서로 다를경우
AXT_RT_NOT_CAPTURED = 4162  # 위치가 저장되지 않을 때
AXT_RT_ERROR_NOT_SAME_IC = 4163  # 같은 칩내에 존재하지않을 때
AXT_RT_ERROR_NOT_GEARMODE = 4164  # 기어모드로 변환이 안될 때
AXT_ERROR_CONTI_INVALID_AXIS_NO = 4165  # 연속보간 축맵핑 시 유효한 축이 아닐 때
AXT_ERROR_CONTI_INVALID_MAP_NO = 4166  # 연속보간 맵핑 시 유효한 맵핑 번호가 아닐 때
AXT_ERROR_CONTI_EMPTY_MAP_NO = 4167  # 연속보간 맵핑 번호가 비워 있을 때
AXT_RT_MOTION_ERROR_CACULATION = 4168  # 계산상의 오차가 발생했을 때
AXT_RT_ERROR_MOVE_SENSOR_CHECK = 4169  # 연속보간 구동전 에러센서가(Alarm, EMG, Limit등) 감지된경우
AXT_ERROR_HELICAL_INVALID_AXIS_NO = 4170  # 헬리컬 축 맵핑 시 유효한 축이 아닐 때
AXT_ERROR_HELICAL_INVALID_MAP_NO = 4171  # 헬리컬 맵핑 시 유효한 맵핑 번호가 아닐 때
AXT_ERROR_HELICAL_EMPTY_MAP_NO = 4172  # 헬리컬 맵핑 번호가 비워 있을 때
AXT_ERROR_HELICAL_ZPOS_DISTANCE_ZERO = 4173  # 헬리컬 맵핑된 Z축의 이동량이 0일 때
AXT_ERROR_SPLINE_INVALID_AXIS_NO = 4180  # 스플라인 축 맵핑 시 유효한 축이 아닐 때
AXT_ERROR_SPLINE_INVALID_MAP_NO = 4181  # 스플라인 맵핑 시 유효한 맵핑 번호가 아닐 때
AXT_ERROR_SPLINE_EMPTY_MAP_NO = 4182  # 스플라인 맵핑 번호가 비워있을 때
AXT_ERROR_SPLINE_NUM_ERROR = 4183  # 스플라인 점숫자가 부적당할 때
AXT_RT_MOTION_INTERPOL_VALUE = 4184  # 보간할 때 입력 값이 잘못넣어졌을 때
AXT_RT_ERROR_NOT_CONTIBEGIN = 4185  # 연속보간 할 때 CONTIBEGIN함수를 호출하지 않을 때
AXT_RT_ERROR_NOT_CONTIEND = 4186  # 연속보간 할 때 CONTIEND함수를 호출하지 않을 때

# Home Search Errors (4200-4219)
AXT_RT_MOTION_HOME_SEARCHING = 4201  # 홈을 찾고 있는 중일 때 다른 모션 함수들을 사용할 때
AXT_RT_MOTION_HOME_ERROR_SEARCHING = 4202  # 홈을 찾고 있는 중일 때 외부에서 사용자나 혹은 어떤것에 의한 강제로 정지당할 때
AXT_RT_MOTION_HOME_ERROR_START = 4203  # 초기화 문제로 홈시작 불가할 때
AXT_RT_MOTION_HOME_ERROR_GANTRY = 4204  # 홈을 찾고 있는 중일 때 겐트리 enable 불가할 때
AXT_RT_CREATE_HOME_THREAD_FAIL = 4205  # HomeSearchThread 생성 실패

# Alarm Related Errors (4210-4239)
AXT_RT_MOTION_READ_ALARM_WAITING = 4210  # 서보팩으로부터 알람코드 결과를 기다리는 중
AXT_RT_MOTION_READ_ALARM_NO_REQUEST = 4211  # 서보팩에 알람코드 반환 명령이 내려지지않았을 때
AXT_RT_MOTION_READ_ALARM_TIMEOUT = 4212  # 서보팩 알람읽기 시간초과 했을때(1sec이상)
AXT_RT_MOTION_READ_ALARM_FAILED = 4213  # 서보팩 알람읽기에 실패 했을 때
AXT_RT_MOTION_READ_ALARM_UNKNOWN = 4220  # 알람코드가 알수없는 코드일 때
AXT_RT_MOTION_READ_ALARM_FILES = 4221  # 알람정보 파일이 정해진위치에 존재하지 않을 때
AXT_RT_MOTION_READ_ALARM_NOT_DETECTED = 4222  # 알람코드 Read 시, 알람이 발생하지 않았을 때

# Motion Setting Errors (4250-4299)
AXT_RT_MOTION_POSITION_OUTOFBOUND = 4251  # 설정한 위치값이 설정 최대값보다 크거나 최소값보다 작은값임
AXT_RT_MOTION_PROFILE_INVALID = 4252  # 구동 속도 프로파일 설정이 잘못됨
AXT_RT_MOTION_VELOCITY_OUTOFBOUND = 4253  # 구동 속도값이 최대값보다 크게 설정됨
AXT_RT_MOTION_MOVE_UNIT_IS_ZERO = 4254  # 구동 단위값이 0으로 설정됨
AXT_RT_MOTION_SETTING_ERROR = 4255  # 속도, 가속도, 저크, 프로파일 설정이 잘못됨
AXT_RT_MOTION_IN_CONT_INTERPOL = 4256  # 연속 보간 구동 중 구동 시작 또는 재시작 함수를 실행하였음
AXT_RT_MOTION_DISABLE_TRIGGER = 4257  # 트리거 출력이 Disable 상태임
AXT_RT_MOTION_INVALID_CONT_INDEX = 4258  # 연속 보간 Index값 설정이 잘못됨
AXT_RT_MOTION_CONT_QUEUE_FULL = 4259  # 모션 칩의 연속 보간 큐가 Full 상태임
AXT_RT_PROTECTED_DURING_SERVOON = 4260  # 서보 온 되어 있는 상태에서 사용 못 함
AXT_RT_HW_ACCESS_ERROR = 4261  # 메모리 Read / Write 실패
AXT_RT_HW_DPRAM_CMD_WRITE_ERROR_LV1 = 4262  # DPRAM Comamnd Write 실패 Level1
AXT_RT_HW_DPRAM_CMD_WRITE_ERROR_LV2 = 4263  # DPRAM Comamnd Write 실패 Level2
AXT_RT_HW_DPRAM_CMD_WRITE_ERROR_LV3 = 4264  # DPRAM Comamnd Write 실패 Level3
AXT_RT_HW_DPRAM_CMD_READ_ERROR_LV1 = 4265  # DPRAM Comamnd Read 실패 Level1
AXT_RT_HW_DPRAM_CMD_READ_ERROR_LV2 = 4266  # DPRAM Comamnd Read 실패 Level2
AXT_RT_HW_DPRAM_CMD_READ_ERROR_LV3 = 4267  # DPRAM Comamnd Read 실패 Level3

# Compensation Errors (4300-4329)
AXT_RT_COMPENSATION_SET_PARAM_FIRST = 4300  # 보정 파라미터 중 첫번째 값이 잘못 설정되었음
AXT_RT_COMPENSATION_NOT_INIT = 4301  # 보정테이블 기능 초기화 되지않음
AXT_RT_COMPENSATION_POS_OUTOFBOUND = 4302  # 위치 값이 범위내에 존재하지 않음
AXT_RT_COMPENSATION_BACKLASH_NOT_INIT = 4303  # 백랙쉬 보정기능 초기화 되지않음
AXT_RT_COMPENSATION_INVALID_ENTRY = 4304  # 보정테이블 개수가 잘못 입력되었음
AXT_RT_COMPENSATION_INVALID_SET_POS = 4310  # 보정테이블 범위로 Position 설정
AXT_RT_COMPENSATION_INVALID_MOTOR_POS = 4311  # 보정테이블 범위 내에서 Position 설정
AXT_RT_COMPENSATION_TWODIM_TABLE_MAX = 4312  # ECAT HW 보드에 할당 가능한 2차원 보정테이블 최대 개수 초과 (4개)
AXT_RT_COMPENSATION_TWODIM_BOARD_MAX = 4313  # 할당 가능한 2차원 보정 ECAT HW 보드 최대 개수 초과 (4개)

# Sequential Motion Errors (4400-4439)
AXT_RT_SEQ_NOT_IN_SERVICE = 4400  # 순차 구동 함수 실행 중 자원 할당 실패
AXT_ERROR_SEQ_INVALID_MAP_NO = 4401  # 순차 구동 함수 실행 중 맵핑 번호 이상
AXT_ERROR_INVALID_AXIS_NO = 4402  # 함수 설정 인자중 축번호 이상
AXT_RT_ERROR_NOT_SEQ_NODE_BEGIN = 4403  # 순차 구동 노드 입력 시작 함수를 호출하지 않음
AXT_RT_ERROR_NOT_SEQ_NODE_END = 4404  # 순차 구동 노드 입력 종료 함수를 호출하지 않음
AXT_RT_ERROR_NO_NODE = 4405  # 순차 구동 노드 입력이 없음
AXT_RT_ERROR_SEQ_STOP_TIMEOUT = 4406  # 순차 구동 함수 종료 시 TimeOut 발생
AXT_RT_ERROR_INVALID_SEQ_MASTER_AXIS_NO = 4407  # 순차 구동 Master 축이 유효하지 않음
AXT_RT_ERROR_RING_COUNTER_ENABLE = 4420  # Ring Counter 기능이 사용 중
AXT_RT_ERROR_RING_COUNTER_OUT_OF_RANGE = 4421  # Ring Counter 사용 중 범위 밖 명령 위치 호출
AXT_RT_ERROR_SOFT_LIMIT_ENABLE = 4430  # Software Limit 기능이 사용 중
AXT_RT_ERROR_SOFT_LIMIT_NEGATIVE = 4431  # 이동할 위치가 Negative Software Limit을 벗어남
AXT_RT_ERROR_SOFT_LIMIT_POSITIVE = 4432  # 이동할 위치가 Positive Software Limit을 벗어남

# ML3 Motion Communication Errors (4500-4599)
AXT_RT_M3_COMMUNICATION_FAILED = 4500  # ML3 통신 기준, 통신 실패
AXT_RT_MOTION_ONE_OF_AXES_IS_NOT_M3 = 4501  # ML3 통신 기준, 구성된 ML3 노드 중에서 모션 노드 없음
AXT_RT_MOTION_BIGGER_VEL_THEN_MAX_VEL = 4502  # ML3 통신 기준, 지정된 축의 설정된 최대 속도보다 큼
AXT_RT_MOTION_SMALLER_VEL_THEN_MAX_VEL = 4503  # ML3 통신 기준, 지정된 축의 설정된 최대 속도보다 작음
AXT_RT_MOTION_ACCEL_MUST_BIGGER_THEN_ZERO = 4504  # ML3 통신 기준, 지정된 축의 설정된 가속도가 0보다 큼
AXT_RT_MOTION_SMALL_ACCEL_WITH_UNIT_PULSE = 4505  # ML3 통신 기준, UnitPulse가 적용된 가속도가 0보다 큼
AXT_RT_MOTION_INVALID_INPUT_ACCEL = 4506  # ML3 통신 기준, 지정된 축의 가속도 입력이 잘못됨
AXT_RT_MOTION_SMALL_DECEL_WITH_UNIT_PULSE = 4507  # ML3 통신 기준, UnitPulse가 적용된 감속도가 0보다 큼
AXT_RT_MOTION_INVALID_INPUT_DECEL = 4508  # ML3 통신 기준, 지정된 축의 감속도 입력이 잘못됨
AXT_RT_MOTION_SAME_START_AND_CENTER_POS = 4509  # ML3 통신 기준, 원호보간의 시작점과 중심점이 같음
AXT_RT_MOTION_INVALID_JERK = 4510  # ML3 통신 기준, 지정된 축의 저크 입력이 잘못됨
AXT_RT_MOTION_INVALID_INPUT_VALUE = 4511  # ML3 통신 기준, 지정된 축의 입력값이 잘못됨
AXT_RT_MOTION_NOT_SUPPORT_PROFILE = 4512  # ML3 통신 기준, 제공되지 않는 속도 프로파일임
AXT_RT_MOTION_INPOS_UNUSED = 4513  # ML3 통신 기준, 인포지션 사용하지 않음
AXT_RT_MOTION_AXIS_IN_SLAVE_STATE = 4514  # ML3 통신 기준, 지정된 축이 슬레이브 상태가 아님
AXT_RT_MOTION_AXES_ARE_NOT_SAME_BOARD = 4515  # ML3 통신 기준, 지정된 축들이 같은 보드 내에 있지 않음
AXT_RT_MOTION_ERROR_IN_ALARM = 4516  # ML3 통신 기준, 지정된 축이 알람 상태임
AXT_RT_MOTION_ERROR_IN_EMGN = 4517  # ML3 통신 기준, 지정된 축이 비상정지 상태임
AXT_RT_MOTION_CAN_NOT_CHANGE_COORD_NO = 4518  # ML3 통신 기준, 코디네이터 넘버 변환 불가임
AXT_RT_MOTION_INVALID_INTERNAL_RADIOUS = 4519  # ML3 통신 기준, 원호보간의 X, Y축 반지름 불일치
AXT_RT_MOTION_CONTI_QUEUE_FULL = 4521  # ML3 통신 기준, 보간의 큐가 가득 참
AXT_RT_MOTION_SAME_START_AND_END_POSITION = 4522  # ML3 통신 기준, 원호보간의 시작점과 종료점이 같음
AXT_RT_MOTION_INVALID_ANGLE = 4523  # ML3 통신 기준, 원호보간의 각도가 360도 초과됨
AXT_RT_MOTION_CONTI_QUEUE_EMPTY = 4524  # ML3 통신 기준, 보간의 큐가 비어있음
AXT_RT_MOTION_ERROR_GEAR_ENABLE = 4525  # ML3 통신 기준, 지정된 축이 이미 링크 설정 상태임
AXT_RT_MOTION_ERROR_GEAR_AXIS = 4526  # ML3 통신 기준, 지정된 축이 링크축이 아님
AXT_RT_MOTION_ERROR_NO_GANTRY_ENABLE = 4527  # ML3 통신 기준, 지정된 축이 겐트리 설정 상태가 아님
AXT_RT_MOTION_ERROR_NO_GEAR_ENABLE = 4528  # ML3 통신 기준, 지정된 축이 링크 설정 상태가 아님
AXT_RT_MOTION_ERROR_GANTRY_ENABLE_FULL = 4529  # ML3 통신 기준, 겐트리 설정 가득참
AXT_RT_MOTION_ERROR_GEAR_ENABLE_FULL = 4530  # ML3 통신 기준, 링크 설정 가득참
AXT_RT_MOTION_ERROR_NO_GANTRY_SLAVE = 4531  # ML3 통신 기준, 지정된 축이 겐트리 슬레이브 설정상태가 아님
AXT_RT_MOTION_ERROR_NO_GEAR_SLAVE = 4532  # ML3 통신 기준, 지정된 축이 링크 슬레이브 설정상태가 아님
AXT_RT_MOTION_ERROR_MASTER_SLAVE_SAME = 4533  # 마스터 축과 슬레이브 축이 동일함
AXT_RT_MOTION_NOT_SUPPORT_HOMESIGNAL = 4534  # ML3 통신 기준, 지정된 축의 홈신호는 지원되지 않음
AXT_RT_MOTION_ERROR_NOT_SYNC_CONNECT = 4535  # ML3 통신 기준, 지정된 축이 싱크 연결 상태가 아님
AXT_RT_MOTION_OVERFLOW_POSITION = 4536  # ML3 통신 기준, 지정된 축에 대한 구동 위치값이 오버플로우임
AXT_RT_MOTION_ERROR_INVALID_CONTIMAPAXIS = 4537  # ML3 통신 기준, 보간작업을 위한 지정된 좌표계 축맵핑이 없음
AXT_RT_MOTION_ERROR_INVALID_CONTIMAPSIZE = 4538  # ML3 통신 기준, 보간작업을 위한 지정된 좌표계 축맵핑 축사이즈가 잘못됨
AXT_RT_MOTION_ERROR_IN_SERVO_OFF = 4539  # ML3 통신 기준, 지정된 축이 서보 OFF되어 있음
AXT_RT_MOTION_ERROR_POSITIVE_LIMIT = 4540  # ML3 통신 기준, 지정된 축이 (+)리밋 ON되어 있음
AXT_RT_MOTION_ERROR_NEGATIVE_LIMIT = 4541  # ML3 통신 기준, 지정된 축이 (-)리밋 ON되어 있음
AXT_RT_MOTION_ERROR_OVERFLOW_SWPROFILE_NUM = 4542  # ML3 통신 기준, 지정된 축들에 대한 지원 프로파일 개수가 오버플로우됨
AXT_RT_PROTECTED_DURING_INMOTION = 4543  # in_motion 되어 있는 상태에서 사용 못 함

# Sync Motion Errors (4600-4699)
AXT_RT_ERROR_SYNC_INVALID_AXIS_NO = 4600  # Sync 축맵핑 시 유효한 축이 아닐 때
AXT_RT_ERROR_SYNC_INVALID_MAP_NO = 4601  # Sync 맵핑 시 유효한 맵핑 번호가 아닐 때
AXT_RT_ERROR_SYNC_DUPLICATED_TIME = 4602  # Time table이 중복되었을 때
AXT_RT_ERROR_PVT_VALUE = 4603  # PVT Data가 유효하지 않은 데이터 일 때
AXT_RT_CREATE_PVT_THREAD_FAIL = 4604  # PVT Thread 생성을 실패했을 때
AXT_RT_ERROR_SYNC_STATE = 4605  # AxisMap의 Sync Status가 서로 다름
AXT_RT_ERROR_SYNC_STATUS_NOT_NONE = 4606  # 변경 될 수 없는 Sync Status

# ============================================================================
# Data Flash Errors (5000-5099)
# ============================================================================

AXT_RT_DATA_FLASH_NOT_EXIST = 5000  # 플래시 메모리가 존재하지 않음
AXT_RT_DATA_FLASH_BUSY = 5001  # 플래시 메모리가 사용 중
AXT_RT_MOTION_STILL_CONTI_MOTION = 5018  # 연속보간 구동 중에 WriteClear나 SetAxisMap 등의 함수를 호출하였음

# ============================================================================
# License Errors (6500-6599)
# ============================================================================

AXT_RT_LICENSE_INVALID = 6500  # 유효하지않은 License

# ============================================================================
# Monitor Errors (6600-6699)
# ============================================================================

AXT_RT_MONITOR_IN_OPERATION = 6600  # 현재 Monitor 기능이 동작중에 있음
AXT_RT_MONITOR_NOT_OPERATION = 6601  # 현재 Monitor 기능이 동작중이지 않음
AXT_RT_MONITOR_EMPTY_QUEUE = 6602  # Monitor data queue가 비어있음
AXT_RT_MONITOR_INVALID_TRIGGER_OPTION = 6603  # 트리거 설정이 유효하지 않음
AXT_RT_MONITOR_EMPTY_ITEM = 6604  # Item이 비어 있음

# ============================================================================
# Error Code Mapping Dictionary
# ============================================================================

ERROR_MESSAGES = {
    # General
    AXT_RT_SUCCESS: "Function executed successfully",
    
    # Library Errors
    AXT_RT_OPEN_ERROR: "Library is not open",
    AXT_RT_OPEN_ALREADY: "Library is already open and in use",
    AXT_RT_NOT_INITIAL: "Serial module is not initialized",
    AXT_RT_NOT_OPEN: "Library initialization failed",
    AXT_RT_NOT_SUPPORT_VERSION: "Unsupported hardware",
    AXT_RT_BAD_PARAMETER: "Invalid parameter provided by user",
    
    # Hardware Validation
    AXT_RT_INVALID_HARDWARE: "Invalid board",
    AXT_RT_INVALID_BOARD_NO: "Invalid board number",
    AXT_RT_INVALID_MODULE_POS: "Invalid module position",
    AXT_RT_INVALID_LEVEL: "Invalid level",
    AXT_RT_INVALID_VARIABLE: "Invalid variable",
    AXT_RT_INVALID_MODULE_NO: "Invalid module number",
    AXT_RT_INVALID_NO: "Invalid number",
    
    # DIO Errors
    AXT_RT_DIO_OPEN_ERROR: "DIO module open failed",
    AXT_RT_DIO_NOT_MODULE: "DIO module not found",
    AXT_RT_DIO_INVALID_MODULE_NO: "Invalid DIO module number",
    AXT_RT_DIO_INVALID_OFFSET_NO: "Invalid DIO offset number",
    AXT_RT_DIO_INVALID_VALUE: "Invalid value setting",
    
    # Motion Errors
    AXT_RT_MOTION_OPEN_ERROR: "Motion library open failed",
    AXT_RT_MOTION_NOT_MODULE: "No motion module installed in system",
    AXT_RT_MOTION_INVALID_AXIS_NO: "Axis does not exist",
    AXT_RT_MOTION_INVALID_METHOD: "Invalid axis drive configuration",
    AXT_RT_MOTION_INVALID_VELOCITY: "Motion velocity set to 0, causing motion error",
    AXT_RT_MOTION_ERROR_IN_MOTION: "Cannot execute motion function while axis is already in motion",
    AXT_RT_MOTION_ERROR_IN_NONMOTION: "Axis should be in motion but is not moving",
    AXT_RT_MOTION_HOME_SEARCHING: "Cannot use other motion functions while home search is in progress",
    AXT_RT_PROTECTED_DURING_SERVOON: "Cannot use this function while servo is ON",
}


def get_error_message(error_code: int) -> str:
    """
    Get error message for given error code
    
    Args:
        error_code: AXL library error code
        
    Returns:
        str: Error description in English
    """
    return ERROR_MESSAGES.get(error_code, f"Unknown error code: {error_code}")


def is_success(error_code: int) -> bool:
    """
    Check if error code indicates success
    
    Args:
        error_code: AXL library error code
        
    Returns:
        bool: True if success, False otherwise
    """
    return error_code == AXT_RT_SUCCESS


def is_library_error(error_code: int) -> bool:
    """
    Check if error code is library related
    
    Args:
        error_code: AXL library error code
        
    Returns:
        bool: True if library error, False otherwise
    """
    return 1000 <= error_code < 2000


def is_motion_error(error_code: int) -> bool:
    """
    Check if error code is motion related
    
    Args:
        error_code: AXL library error code
        
    Returns:
        bool: True if motion error, False otherwise
    """
    return 4000 <= error_code < 5000


def is_dio_error(error_code: int) -> bool:
    """
    Check if error code is DIO related
    
    Args:
        error_code: AXL library error code
        
    Returns:
        bool: True if DIO error, False otherwise
    """
    return 3000 <= error_code < 3200