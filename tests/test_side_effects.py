"""부수 효과 검증 테스트.

입금/출금이 은행 잔액과 현금함 양쪽 모두에 정확히 반영되는지,
조회 동작은 상태를 변경하지 않는지 검증.
"""


def test_deposit_updates_bank_and_cash_box(authenticated_atm, bank, cash_box):
    """입금 시 은행 잔액 + 현금함 모두 동일 금액만큼 증가해야 함."""
    cash_before = cash_box.get_available_cash()
    balance_before = bank.get_balance("checking")

    authenticated_atm.deposit(40)

    assert cash_box.get_available_cash() == cash_before + 40
    assert bank.get_balance("checking") == balance_before + 40


def test_withdraw_updates_bank_and_cash_box(authenticated_atm, bank, cash_box):
    """출금 시 은행 잔액 + 현금함 모두 동일 금액만큼 감소해야 함."""
    cash_before = cash_box.get_available_cash()
    balance_before = bank.get_balance("checking")

    authenticated_atm.withdraw(60)

    assert cash_box.get_available_cash() == cash_before - 60
    assert bank.get_balance("checking") == balance_before - 60


def test_balance_query_does_not_mutate(authenticated_atm, bank, cash_box):
    """잔액 조회는 어떤 상태도 변경해서는 안 됨 (멱등성)."""
    cash_before = cash_box.get_available_cash()
    balance_before = bank.get_balance("checking")

    authenticated_atm.get_balance()
    authenticated_atm.get_balance()

    assert cash_box.get_available_cash() == cash_before
    assert bank.get_balance("checking") == balance_before
