from abc import ABC, abstractmethod


class CashBox(ABC):
    """ATM 안에 물리적으로 들어있는 현금 보관함 추상 인터페이스.

    은행 계좌 잔액(BankAPI)과는 별개의 개념.
    내 계좌에 돈이 있어도 ATM 안에 현금이 없으면 출금 불가.

    실제 하드웨어(지폐 카운터, 모터, 센서 등) 드라이버는 나중에
    이 인터페이스를 구현해서 갈아끼움.

    이 세상엔 1달러 지폐만 있다고 가정하므로 모든 금액은 정수.
    """

    @abstractmethod
    def get_available_cash(self) -> int:
        """현재 ATM 안에 들어있는 현금 총액(달러) 반환."""

    @abstractmethod
    def give_cash(self, amount: int) -> None:
        """출금: ATM이 사용자에게 현금을 준다 (현금 지급)."""

    @abstractmethod
    def take_cash(self, amount: int) -> None:
        """입금: ATM이 사용자로부터 현금을 받는다 (지폐 수납)."""
