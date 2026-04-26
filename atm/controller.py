from atm import state
from atm.bank import BankAPI
from atm.cash_box import CashBox
from atm.errors import (
    AccountNotFoundError,
    NotEnoughCashBoxError,
    NotEnoughBalanceError,
    InvalidAmountError,
    InvalidPinError,
    InvalidStateError,
)


class ATMController:
    """ATM 한 번 사용(세션) 동안의 흐름을 관리하는 클래스.

    화면(UI)은 이 클래스의 메서드를 정해진 순서대로 호출만 하면 된다.
    순서가 틀리면 InvalidStateError가 발생한다.

    동작 순서:
        카드 넣기 -> PIN 입력 -> 계좌 선택 -> 잔액조회/입금/출금 -> 카드 빼기

    은행 통신과 현금 입출은 외부에서 받은 객체에 맡긴다(BankAPI, CashBox).
    덕분에 나중에 진짜 은행 시스템이나 진짜 ATM 하드웨어로 바꿔도
    이 컨트롤러 코드는 그대로 둘 수 있다.
    """

    def __init__(self, bank: BankAPI, cash_box: CashBox) -> None:
        self._bank = bank
        self._cash_box = cash_box
        # 처음엔 아무도 카드를 안 넣은 상태(READY)로 시작
        self._state = state.READY
        self._card_number = None
        self._selected_account = None

    def get_state(self) -> str:
        """지금 어느 단계에 있는지 알려준다 (테스트/디버깅용)."""
        return self._state

    # ---- 카드 / 인증 ----

    def insert_card(self, card_number: str) -> None:
        """카드를 ATM에 넣는다. READY 상태일 때만 가능."""
        if self._state != state.READY:
            raise InvalidStateError("이미 카드가 들어있다")
        self._card_number = card_number
        self._state = state.CARD_IN

    def enter_pin(self, pin: str) -> None:
        """PIN을 입력한다. 카드가 들어와 있어야 가능."""
        if self._state != state.CARD_IN:
            raise InvalidStateError("PIN을 입력할 단계가 아니다")
        # PIN이 맞는지는 은행에 물어본다 (ATM은 PIN을 저장하지 않는다)
        if not self._bank.validate_pin(self._card_number, pin):
            raise InvalidPinError("PIN이 틀렸다")
        self._state = state.PIN_OK

    # ---- 계좌 ----

    def get_accounts(self) -> list[str]:
        """이 카드에 연결된 계좌 목록을 가져온다."""
        if self._state not in (state.PIN_OK, state.ACCOUNT_OPEN):
            raise InvalidStateError("PIN 인증을 먼저 해야 한다")
        return self._bank.get_accounts(self._card_number)

    def select_account(self, account_id: str) -> None:
        """거래할 계좌를 고른다."""
        if self._state not in (state.PIN_OK, state.ACCOUNT_OPEN):
            raise InvalidStateError("PIN 인증을 먼저 해야 한다")
        # 카드에 연결되지 않은 계좌는 못 고른다
        if account_id not in self._bank.get_accounts(self._card_number):
            raise AccountNotFoundError(f"이 카드와 연결되지 않은 계좌: {account_id}")
        self._selected_account = account_id
        self._state = state.ACCOUNT_OPEN

    # ---- 거래 ----

    def get_balance(self) -> int:
        """선택한 계좌의 잔액을 조회한다."""
        if self._state != state.ACCOUNT_OPEN:
            raise InvalidStateError("계좌를 먼저 선택해야 한다")
        return self._bank.get_balance(self._selected_account)

    def deposit(self, amount: int) -> int:
        """선택한 계좌에 입금한다. 변경된 잔액을 반환."""
        if self._state != state.ACCOUNT_OPEN:
            raise InvalidStateError("계좌를 먼저 선택해야 한다")
        self._check_amount(amount)
        # 1) ATM이 사용자로부터 지폐를 받는다
        # 2) 은행 계좌에 그만큼 더한다
        self._cash_box.take_cash(amount)
        return self._bank.deposit(self._selected_account, amount)

    def withdraw(self, amount: int) -> int:
        """선택한 계좌에서 출금한다. 변경된 잔액을 반환."""
        if self._state != state.ACCOUNT_OPEN:
            raise InvalidStateError("계좌를 먼저 선택해야 한다")
        self._check_amount(amount)

        # ATM 안에 줄 현금이 있는지부터 확인 (없으면 줄 게 없으니 바로 거부)
        if self._cash_box.get_available_cash() < amount:
            raise NotEnoughCashBoxError("ATM에 현금이 부족하다")
        # 그 다음 계좌에 돈이 있는지 확인
        if self._bank.get_balance(self._selected_account) < amount:
            raise NotEnoughBalanceError("계좌 잔액이 부족하다")

        # 은행에서 먼저 빼고, 그 다음 사용자에게 현금을 지급한다
        new_balance = self._bank.withdraw(self._selected_account, amount)
        self._cash_box.give_cash(amount)
        return new_balance

    # ---- 종료 ----

    def return_card(self) -> None:
        """카드를 사용자에게 돌려주고 세션을 처음 상태로 되돌린다. 언제든 호출 가능."""
        self._card_number = None
        self._selected_account = None
        self._state = state.READY

    # ---- 내부 헬퍼 ----

    def _check_amount(self, amount: int) -> None:
        """금액이 양의 정수인지 확인. 1달러 지폐만 있으니 정수여야 한다."""
        # 주의: True/False 도 int 의 일종이므로 따로 막아준다
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise InvalidAmountError("금액은 정수여야 한다")
        if amount <= 0:
            raise InvalidAmountError("금액은 0보다 커야 한다")
