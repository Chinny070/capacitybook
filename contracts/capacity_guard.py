# v0.1.0
# { "Depends": "py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng" }

import genlayer as gl
from genlayer.types import *
from genlayer.storage import TreeMap

from dataclasses import dataclass
import typing


@gl.contract.interface
class ICapacityBook:
    class View:
        def is_effective(self, reservation_id: u256, expected_book_hash: str) -> bool: ...

    class Write:
        pass


@gl.storage.allow
@dataclass
class ExecutionReceipt:
    caller: Address
    reservation_id: u256
    book_hash: str
    action_hash: str


class CapacityGuard(gl.contract.Contract):
    """Minimal consumer proving CapacityBook can gate another IC's action."""

    capacitybook_address: Address
    executions: TreeMap[str, ExecutionReceipt]
    execution_count: u256

    def __init__(self, capacitybook_address: Address):
        self.capacitybook_address = capacitybook_address
        self.execution_count = 0

    @gl.public.write
    def execute(
        self,
        reservation_id: u256,
        expected_book_hash: str,
        action_hash: str,
    ) -> None:
        action_hash = str(action_hash).strip().lower()
        if len(action_hash) != 64:
            raise gl.vm.UserError("EXPECTED: action_hash must be a 32-byte hex digest")
        for char in action_hash:
            if char not in "0123456789abcdef":
                raise gl.vm.UserError("EXPECTED: action_hash must be lowercase hex")

        capacitybook = ICapacityBook(self.capacitybook_address)
        if not capacitybook.view().is_effective(reservation_id, expected_book_hash):
            raise gl.vm.UserError("EXPECTED: capacity reservation is not currently effective")
        if action_hash in self.executions:
            raise gl.vm.UserError("EXPECTED: action was already executed")

        self.executions[action_hash] = ExecutionReceipt(
            caller=gl.message.sender_address,
            reservation_id=reservation_id,
            book_hash=str(expected_book_hash),
            action_hash=action_hash,
        )
        self.execution_count = int(self.execution_count) + 1

    @gl.public.view
    def was_executed(self, action_hash: str) -> bool:
        return str(action_hash).strip().lower() in self.executions

    @gl.public.view
    def get_execution(self, action_hash: str) -> dict[str, typing.Any]:
        key = str(action_hash).strip().lower()
        if key not in self.executions:
            raise gl.vm.UserError("EXPECTED: unknown execution")
        item = self.executions[key]
        return {
            "caller": str(item.caller),
            "reservation_id": int(item.reservation_id),
            "book_hash": str(item.book_hash),
            "action_hash": str(item.action_hash),
        }
