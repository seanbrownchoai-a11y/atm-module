"""ATM 컨트롤러가 던지는 예외들.

크게 3가지로 묶인다.

1) 흐름 위반     - InvalidStateError
   잘못된 순서로 호출. 예: 카드도 안 넣고 PIN 입력.

2) 입력 오류     - InvalidPinError, AccountNotFoundError, InvalidAmountError
   사용자가 잘못된 값을 줬을 때.

3) 돈 부족       - NotEnoughBalanceError, NotEnoughCashBoxError
   잔액 또는 ATM 현금이 모자랄 때.

UI 레이어는 각 예외를 잡아서 사용자에게 알맞은 메시지를 보여주면 된다.
모든 ATM 예외는 ATMError 를 상속하므로, 한 번에 잡고 싶으면 ATMError 만
잡아도 된다.
"""


class ATMError(Exception):
    """모든 ATM 예외의 부모."""


# 1) 흐름 위반
class InvalidStateError(ATMError):
    """잘못된 순서로 메서드를 호출했다."""


# 2) 입력 오류
class InvalidPinError(ATMError):
    """PIN이 틀렸다."""


class AccountNotFoundError(ATMError):
    """카드와 연결되지 않은 계좌를 골랐다."""


class InvalidAmountError(ATMError):
    """금액이 양의 정수가 아니다."""


# 3) 돈 부족
class NotEnoughBalanceError(ATMError):
    """계좌 잔액이 모자란다."""


class NotEnoughCashBoxError(ATMError):
    """ATM 현금이 모자란다."""
