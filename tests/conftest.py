import pytest

from atm import ATMController
from tests.fakes import FakeBank, FakeCashBox


@pytest.fixture
def card_number():
    """테스트용 기본 카드 번호."""
    return "4242-1111"


@pytest.fixture
def bank():
    """테스트용 인메모리 은행. PIN 1234, checking/savings 계좌 보유."""
    return FakeBank(
        pins={"4242-1111": "1234"},
        accounts_by_card={"4242-1111": ["checking", "savings"]},
        balances={"checking": 100, "savings": 500},
    )


@pytest.fixture
def cash_box():
    """테스트용 현금함. 잔액 부족 테스트와 분리하기 위해 충분한 현금 보유."""
    return FakeCashBox(initial_cash=100_000)


@pytest.fixture
def atm(bank, cash_box):
    """은행과 현금함이 주입된 ATM 컨트롤러."""
    return ATMController(bank=bank, cash_box=cash_box)


@pytest.fixture
def authenticated_atm(atm, card_number):
    """카드 삽입 + PIN 인증 + 계좌 선택까지 마친 ATM."""
    atm.insert_card(card_number)
    atm.enter_pin("1234")
    atm.select_account("checking")
    return atm
