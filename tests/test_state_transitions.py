"""상태 머신 전이 검증 테스트.

각 동작은 허용된 상태에서만 호출 가능하고, 그 외에는 InvalidStateError가
발생해야 함.
"""

import pytest

from atm.errors import InvalidStateError


def test_cannot_enter_pin_before_inserting_card(atm):
    """카드 삽입 전엔 PIN 입력 불가."""
    with pytest.raises(InvalidStateError):
        atm.enter_pin("1234")


def test_cannot_select_account_before_pin(atm, card_number):
    """PIN 인증 전엔 계좌 선택 불가."""
    atm.insert_card(card_number)
    with pytest.raises(InvalidStateError):
        atm.select_account("checking")


def test_cannot_get_balance_before_account_selected(atm, card_number):
    """계좌 선택 전엔 잔액 조회 불가."""
    atm.insert_card(card_number)
    atm.enter_pin("1234")
    with pytest.raises(InvalidStateError):
        atm.get_balance()


def test_cannot_withdraw_before_account_selected(atm, card_number):
    """계좌 선택 전엔 출금 불가."""
    atm.insert_card(card_number)
    atm.enter_pin("1234")
    with pytest.raises(InvalidStateError):
        atm.withdraw(10)


def test_cannot_insert_card_twice(atm, card_number):
    """카드가 이미 삽입된 상태에선 또 삽입 불가."""
    atm.insert_card(card_number)
    with pytest.raises(InvalidStateError):
        atm.insert_card(card_number)


def test_get_accounts_works_in_authenticated_and_selected(atm, card_number):
    """계좌 목록 조회는 PIN 인증 이후 어느 시점에서나 가능해야 함."""
    atm.insert_card(card_number)
    atm.enter_pin("1234")
    assert atm.get_accounts() == ["checking", "savings"]

    atm.select_account("checking")
    # 계좌 선택 후에도 다시 목록 조회 가능 (다른 계좌로 전환하기 위해)
    assert atm.get_accounts() == ["checking", "savings"]
