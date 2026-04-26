"""ATM 세션 상태 상수.

상태 전이:
    READY        -> CARD_IN        (insert_card)
    CARD_IN      -> PIN_OK         (enter_pin, 검증 성공)
    PIN_OK       -> ACCOUNT_OPEN   (select_account)
    ACCOUNT_OPEN -> ACCOUNT_OPEN   (잔액조회/입금/출금)
    어느 상태에서든 -> READY        (return_card)
"""

READY = "READY"               # 카드 대기 중 (시작 상태)
CARD_IN = "CARD_IN"           # 카드 들어옴, PIN 입력 대기
PIN_OK = "PIN_OK"             # PIN 통과, 계좌 선택 대기
ACCOUNT_OPEN = "ACCOUNT_OPEN" # 계좌 선택 완료, 거래 가능
