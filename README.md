# ATM Controller

간단한 ATM 컨트롤러 (Python). UI에 의존하지 않고, 은행 시스템과 ATM 하드웨어
같은 외부 의존은 추상 인터페이스로 분리해서 나중에 실제 구현체로 갈아끼울 수
있도록 설계했다.

## 동작 흐름

```
카드 삽입 → PIN 입력 → 계좌 선택 → 잔액 조회 / 입금 / 출금 → 카드 배출
```

이 세상엔 1달러 지폐만 있다고 가정하므로 모든 금액은 정수.

## 프로젝트 구조

```
atm/                ATM 비즈니스 로직
  controller.py     ATMController (상태 머신 + 거래 처리)
  bank.py           BankAPI 추상 인터페이스
  cash_box.py       CashBox 추상 인터페이스 (ATM 안 현금함)
  state.py          상태 상수
  errors.py         커스텀 예외 모음
tests/              pytest 테스트 모음
  fakes.py          BankAPI / CashBox 인메모리 테스트 구현체
```

## 설치

```
git clone <this-repo-url>
cd atm-module
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Python 3.10 이상 필요.

## 테스트 실행

```
pytest
```

모든 테스트는 인메모리 fake 객체 위에서 돌아간다. 실제 은행이나 하드웨어 없이
바로 검증 가능.

## 사용 예시

`BankAPI`와 `CashBox`의 실제 구현체를 주입해서 사용한다. 인메모리 더미
구현체 예시는 `tests/fakes.py` 참고.

```python
from atm import ATMController

# bank: BankAPI 구현체, cash_box: CashBox 구현체
atm = ATMController(bank=bank, cash_box=cash_box)

atm.insert_card("4242-1111")
atm.enter_pin("1234")
atm.select_account("checking")

print(atm.get_balance())     # 현재 잔액
print(atm.deposit(50))       # 입금 후 잔액
print(atm.withdraw(30))      # 출금 후 잔액
atm.return_card()
```

## 설계 노트

### 의존성 주입 (Dependency Injection)

`ATMController`는 추상 인터페이스인 `BankAPI`와 `CashBox`에만 의존한다.
실제 구현체(네트워크 호출, 하드웨어 드라이버)는 컨트롤러를 수정하지 않고
교체 가능하다. 테스트에서는 인메모리 fake를 주입한다.

### 상태 머신

컨트롤러는 자기 세션 상태를 `state` 모듈의 상수로 추적하고, 정해진 순서를
어기는 호출은 거부한다. 덕분에 UI 레이어는 상태를 직접 관리하지 않아도 된다.

### PIN 처리

은행 API는 `validate_pin(card_number, pin) -> bool` 만 노출한다. PIN은
컨트롤러에도 절대 저장하지 않는다 (실제 ATM 보안 제약과 동일).

### 거래 순서

* `deposit(amount)`: 현금함이 지폐를 먼저 받고, 그 다음 은행 잔액 증가.
* `withdraw(amount)`: 현금함과 은행 잔액을 먼저 모두 확인하고, 은행에서 차감,
  마지막에 현금 지급.

실서비스에서는 부분 실패 롤백을 위한 트랜잭션이 필요하지만, 본 과제에서는
범위 밖으로 두었다.

### BankAPI vs CashBox 분리

은행 계좌 잔액(논리적 숫자)과 ATM 안 실제 현금(물리적 지폐)은 다른 개념이라
인터페이스를 둘로 분리했다.

* 내 계좌에 100만 달러가 있어도 ATM에 5만 달러만 있으면 5만 달러밖에 못 뽑음.
* 그래서 `NotEnoughBalanceError`(계좌 부족)와 `NotEnoughCashBoxError`(ATM 부족)도
  따로 둠.

### 에러 모델

UI가 사용자에게 적절한 메시지를 보여줄 수 있도록 예외를 작게 분리했다.

* `InvalidStateError` – 잘못된 순서로 메서드 호출
* `InvalidPinError` – PIN 틀림
* `AccountNotFoundError` – 카드와 연결되지 않은 계좌
* `InvalidAmountError` – 금액이 양의 정수가 아님
* `NotEnoughBalanceError` – 계좌 잔액 부족
* `NotEnoughCashBoxError` – ATM 현금 부족

## 범위 밖 (Out of Scope)

* 실제 은행 연동 (REST, RPC 등)
* 실제 ATM 하드웨어 드라이버 (지폐 카운터, 카드 리더기 등)
* 다중 통화, 소수점 금액
* 동시성 / 분산 트랜잭션
* 사용자 인터페이스 (CLI, GUI, 웹 등)
