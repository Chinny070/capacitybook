"""Direct-mode scenarios for CapacityBook."""

import json
from datetime import datetime

CONTRACT = "contracts/capacitybook.py"
CLASSIFIER = r"CAPACITYBOOK / RESOURCE-DEMAND VERIFICATION"
BASE = "2026-09-14T12:00:00+00:00"
START = int(datetime.fromisoformat("2026-09-15T10:00:00+00:00").timestamp())
END = int(datetime.fromisoformat("2026-09-15T12:00:00+00:00").timestamp())
LATER_START = int(datetime.fromisoformat("2026-09-15T13:00:00+00:00").timestamp())
LATER_END = int(datetime.fromisoformat("2026-09-15T15:00:00+00:00").timestamp())
URL = "https://example.com/commitment/alpha"
SOURCE = "Service commitment Alpha reserves two dedicated P1 responders from 10:00 UTC until 12:00 UTC on 15 September 2026."


def alice_address():
    from gltest.direct import create_address
    return create_address("alice")


def bob_address():
    from gltest.direct import create_address
    return create_address("bob")


def mock_match(vm, body=SOURCE, evidence=SOURCE):
    vm.clear_mocks()
    vm.mock_web(r".*example\.com/commitment/.*", {"status": 200, "body": body})
    vm.mock_llm(
        CLASSIFIER,
        json.dumps({"verdict": "MATCHED", "reason": "the public commitment grounds the declared demand", "evidence": evidence}).encode(),
    )


def mock_ambiguous(vm):
    vm.clear_mocks()
    vm.mock_web(r".*example\.com/commitment/.*", {"status": 200, "body": "Provider promises rapid incident response."})
    vm.mock_llm(
        CLASSIFIER,
        json.dumps({"verdict": "AMBIGUOUS", "reason": "resource quantity and interval are not established", "evidence": ""}).encode(),
    )


def build_book(vm, deploy, capacity=2):
    vm.warp(BASE)
    contract = deploy(CONTRACT)
    book = contract.create_book(
        "P1 Response Capacity",
        "Prevent service providers from making jointly impossible exclusive incident-response commitments.",
    )
    pool = contract.add_pool(
        book,
        "Dedicated P1 responders",
        "responder",
        capacity,
        "A human or autonomous responder reserved for exclusive P1 incident handling during the declared interval.",
    )
    contract.seal_book(book)
    return contract, book, pool


def create_verified(contract, vm, book, pool, counterparty, units=2, start=START, end=END):
    reservation = contract.open_reservation(book, counterparty, "Alpha support commitment", URL, start, end)
    demand = contract.add_demand(reservation, pool, units)
    mock_match(vm)
    assert contract.verify_demand(demand) == 1
    with vm.prank(counterparty):
        contract.accept_reservation(reservation)
    assert contract.try_admit(reservation) is True
    return reservation, demand


def test_book_seal_freezes_definition(direct_vm, direct_deploy):
    contract, book, pool = build_book(direct_vm, direct_deploy)
    data = contract.get_book(book)
    assert data["status_name"] == "SEALED"
    assert data["pool_ids"] == [pool]
    assert len(data["definition_hash"]) == 64
    with direct_vm.expect_revert("sealed"):
        contract.add_pool(book, "late", "unit", 1, "Late mutable pool must not be accepted after seal.")


def test_creation_uses_transaction_clock(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    book = contract.create_book("Book", "A sufficiently bounded capacity purpose.")
    expected = int(datetime.fromisoformat(direct_vm._datetime).timestamp())
    assert contract.get_book(book)["created_at"] == expected


def test_public_evidence_match_is_validator_reproducible(direct_vm, direct_deploy):
    contract, book, pool = build_book(direct_vm, direct_deploy)
    reservation = contract.open_reservation(book, alice_address(), "Alpha support commitment", URL, START, END)
    demand = contract.add_demand(reservation, pool, 2)
    mock_match(direct_vm)
    assert contract.verify_demand(demand) == 1
    assert contract.get_demand(demand)["evidence"] == SOURCE
    assert direct_vm.run_validator() is True


def test_ambiguous_evidence_cannot_unlock_capacity(direct_vm, direct_deploy):
    contract, book, pool = build_book(direct_vm, direct_deploy)
    reservation = contract.open_reservation(book, alice_address(), "Alpha support commitment", URL, START, END)
    demand = contract.add_demand(reservation, pool, 2)
    mock_ambiguous(direct_vm)
    assert contract.verify_demand(demand) == 3
    with direct_vm.prank(alice_address()):
        contract.accept_reservation(reservation)
    with direct_vm.expect_revert("every demand"):
        contract.try_admit(reservation)


def test_overlapping_commitment_is_blocked(direct_vm, direct_deploy):
    contract, book, pool = build_book(direct_vm, direct_deploy, capacity=2)
    first, _ = create_verified(contract, direct_vm, book, pool, alice_address(), units=2)
    second = contract.open_reservation(book, bob_address(), "Beta support commitment", URL, START, END)
    demand2 = contract.add_demand(second, pool, 1)
    mock_match(direct_vm)
    assert contract.verify_demand(demand2) == 1
    with direct_vm.prank(bob_address()):
        contract.accept_reservation(second)
    assert contract.try_admit(second) is False
    assert contract.get_reservation(first)["status_name"] == "ADMITTED"
    blocked = contract.get_reservation(second)
    assert blocked["status_name"] == "PENDING"
    assert blocked["last_blocked_pool_id"] == pool
    assert contract.available_units(pool, START, END) == 0


def test_disjoint_intervals_can_reuse_same_capacity(direct_vm, direct_deploy):
    contract, book, pool = build_book(direct_vm, direct_deploy, capacity=2)
    create_verified(contract, direct_vm, book, pool, alice_address(), units=2)
    later = contract.open_reservation(book, bob_address(), "Later support commitment", URL, LATER_START, LATER_END)
    demand = contract.add_demand(later, pool, 2)
    mock_match(direct_vm)
    contract.verify_demand(demand)
    with direct_vm.prank(bob_address()):
        contract.accept_reservation(later)
    assert contract.try_admit(later) is True
    assert contract.available_units(pool, LATER_START, LATER_END) == 0


def test_early_release_requires_both_parties(direct_vm, direct_deploy):
    contract, book, pool = build_book(direct_vm, direct_deploy, capacity=2)
    reservation, _ = create_verified(contract, direct_vm, book, pool, alice_address(), units=2)
    assert contract.request_release(reservation) is False
    assert contract.get_reservation(reservation)["status_name"] == "ADMITTED"
    with direct_vm.prank(alice_address()):
        assert contract.request_release(reservation) is True
    assert contract.get_reservation(reservation)["status_name"] == "RELEASED"
    assert contract.available_units(pool, START, END) == 2


def test_blocked_reservation_can_retry_after_release(direct_vm, direct_deploy):
    contract, book, pool = build_book(direct_vm, direct_deploy, capacity=2)
    first, _ = create_verified(contract, direct_vm, book, pool, alice_address(), units=2)
    second = contract.open_reservation(book, bob_address(), "Beta support commitment", URL, START, END)
    demand2 = contract.add_demand(second, pool, 2)
    mock_match(direct_vm)
    contract.verify_demand(demand2)
    with direct_vm.prank(bob_address()):
        contract.accept_reservation(second)
    assert contract.try_admit(second) is False
    contract.request_release(first)
    with direct_vm.prank(alice_address()):
        contract.request_release(first)
    assert contract.try_admit(second) is True


def test_book_hash_pins_consumer_semantics(direct_vm, direct_deploy):
    contract, book, pool = build_book(direct_vm, direct_deploy)
    reservation, _ = create_verified(contract, direct_vm, book, pool, alice_address(), units=2)
    current = contract.current_book_hash(book)
    assert contract.is_admitted(reservation, current) is True
    assert contract.is_admitted(reservation, "00" * 32) is False


def test_cancelled_draft_never_reserves_capacity(direct_vm, direct_deploy):
    contract, book, pool = build_book(direct_vm, direct_deploy)
    reservation = contract.open_reservation(book, alice_address(), "Cancelled", URL, START, END)
    contract.add_demand(reservation, pool, 2)
    contract.cancel_draft(reservation)
    assert contract.get_reservation(reservation)["status_name"] == "CANCELLED"
    assert contract.available_units(pool, START, END) == 2
