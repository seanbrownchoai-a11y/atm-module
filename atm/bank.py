from abc import ABC, abstractmethod


class BankAPI(ABC):
    """은행 백엔드와 통신하는 추상 인터페이스.

    ATM 컨트롤러는 이 인터페이스에만 의존하므로, 나중에 실제 은행
    서비스로 교체할 때 컨트롤러 코드는 수정하지 않아도 됨.

    중요: PIN 자체는 절대 외부로 노출하지 않음.
    사용자가 입력한 PIN이 맞는지 검증만 해주는 형태.
    """

    @abstractmethod
    def validate_pin(self, card_number: str, pin: str) -> bool:
        """카드 번호와 PIN이 일치하면 True, 아니면 False."""

    @abstractmethod
    def get_accounts(self, card_number: str) -> list[str]:
        """해당 카드에 연결된 계좌 ID 목록 반환."""

    @abstractmethod
    def get_balance(self, account_id: str) -> int:
        """계좌의 현재 잔액(달러) 반환."""

    @abstractmethod
    def deposit(self, account_id: str, amount: int) -> int:
        """계좌에 amount 만큼 입금하고, 변경된 잔액 반환."""

    @abstractmethod
    def withdraw(self, account_id: str, amount: int) -> int:
        """계좌에서 amount 만큼 출금하고, 변경된 잔액 반환.

        잔액이 부족하면 NotEnoughBalanceError 발생.
        """
