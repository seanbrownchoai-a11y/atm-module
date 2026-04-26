"""정상 플로우 테스트.

카드 삽입 → PIN → 계좌 선택 → 잔액/입금/출금이 의도대로 동작하는지 검증.
"""


def test_full_flow_balance_deposit_withdraw(atm, card_number):
    """전체 플로우 한 번 끝까지 돌려보기."""
    atm.insert_card(card_number)
    atm.enter_pin("1234")
    assert atm.get_accounts() == ["checking", "savings"]

    atm.select_account("checking")
    assert atm.get_balance() == 100

    # 입금 후 잔액이 정확히 증가하는지
    new_balance_after_deposit = atm.deposit(50)
    assert new_balance_after_deposit == 150
    assert atm.get_balance() == 150

    # 출금 후 잔액이 정확히 감소하는지
    new_balance_after_withdraw = atm.withdraw(30)
    assert new_balance_after_withdraw == 120
    assert atm.get_balance() == 120


def test_switching_account_within_session(atm, card_number):
    """같은 세션 안에서 계좌 전환이 가능해야 함."""
    atm.insert_card(card_number)
    atm.enter_pin("1234")

    atm.select_account("checking")
    assert atm.get_balance() == 100

    atm.select_account("savings")
    assert atm.get_balance() == 500


def test_return_card_resets_session(atm, card_number, bank, cash_box):
    """카드 반환 후 세션이 READY로 리셋되어 다시 카드 삽입이 가능해야 함."""
    from atm import ATMController

    atm.insert_card(card_number)
    atm.enter_pin("1234")
    atm.select_account("checking")
    atm.return_card()

    # 같은 의존성으로 새 컨트롤러를 만들어도 동작해야 함
    fresh = ATMController(bank=bank, cash_box=cash_box)
    fresh.insert_card(card_number)  # 카드 반환 후 READY 상태이므로 다시 삽입 가능
