"""에러 케이스 테스트.

각 에러가 정확한 상황에서만 발생하고, 잘못된 입력으로 부수 효과가
남지 않는지 검증.
"""

import pytest

from atm import ATMController
from atm.errors import (
    AccountNotFoundError,
    NotEnoughCashBoxError,
    NotEnoughBalanceError,
    InvalidAmountError,
    InvalidPinError,
)
from tests.fakes import FakeBank, FakeCashBox


def test_invalid_pin_raises(atm, card_number):
    """틀린 PIN 입력 시 InvalidPinError."""
    atm.insert_card(card_number)
    with pytest.raises(InvalidPinError):
        atm.enter_pin("0000")


def test_select_unknown_account_raises(atm, card_number):
    """카드에 연결되지 않은 계좌 선택 시 AccountNotFoundError."""
    atm.insert_card(card_number)
    atm.enter_pin("1234")
    with pytest.raises(AccountNotFoundError):
        atm.select_account("not-mine")


def test_withdraw_more_than_balance_raises(authenticated_atm):
    """계좌 잔액보다 많이 출금 시 NotEnoughBalanceError."""
    with pytest.raises(NotEnoughBalanceError):
        authenticated_atm.withdraw(10_000)


def test_withdraw_more_than_cash_box_raises():
    """ATM 안 현금보다 많이 출금 시 NotEnoughCashBoxError.

    계좌 잔액은 충분하지만 ATM에 현금이 부족한 상황을 만들기 위해
    별도 fixture를 사용하지 않고 인라인으로 셋업.
    """
    bank = FakeBank(
        pins={"c": "1"},
        accounts_by_card={"c": ["a"]},
        balances={"a": 1_000_000},
    )
    cash_box = FakeCashBox(initial_cash=50)
    atm = ATMController(bank=bank, cash_box=cash_box)
    atm.insert_card("c")
    atm.enter_pin("1")
    atm.select_account("a")

    with pytest.raises(NotEnoughCashBoxError):
        atm.withdraw(100)


@pytest.mark.parametrize("amount", [0, -5])
def test_invalid_deposit_amount_raises(authenticated_atm, amount):
    """0이나 음수 입금 시 InvalidAmountError."""
    with pytest.raises(InvalidAmountError):
        authenticated_atm.deposit(amount)


@pytest.mark.parametrize("amount", [0, -5])
def test_invalid_withdraw_amount_raises(authenticated_atm, amount):
    """0이나 음수 출금 시 InvalidAmountError."""
    with pytest.raises(InvalidAmountError):
        authenticated_atm.withdraw(amount)


def test_non_integer_amount_raises(authenticated_atm):
    """정수가 아닌 금액(실수, 문자열) 거부."""
    with pytest.raises(InvalidAmountError):
        authenticated_atm.deposit(10.5)
    with pytest.raises(InvalidAmountError):
        authenticated_atm.withdraw("100")


def test_balance_unchanged_when_pin_wrong(atm, card_number, bank):
    """PIN 검증 실패해도 계좌 잔액에는 영향 없어야 함."""
    atm.insert_card(card_number)
    with pytest.raises(InvalidPinError):
        atm.enter_pin("0000")
    assert bank.get_balance("checking") == 100


def test_cash_box_unchanged_when_withdraw_fails(authenticated_atm, cash_box):
    """출금 실패 시 현금함 잔량에 영향 없어야 함 (롤백/원자성)."""
    cash_before = cash_box.get_available_cash()
    with pytest.raises(NotEnoughBalanceError):
        authenticated_atm.withdraw(10_000)
    assert cash_box.get_available_cash() == cash_before
