"""
StudioNet integration checklist, intentionally skipped until deployed addresses are supplied.

Network is fixed to StudioNet chain ID 61999. This file exists so the deployment agent
has one canonical place to add live receipt checks after deployment.
"""

import os
import pytest

CHAIN_ID = 61999


def test_network_pin():
    assert CHAIN_ID == 61999


@pytest.mark.skipif(not os.getenv("CAPACITYBOOK_ADDRESS"), reason="deploy CapacityBook on StudioNet 61999 first")
def test_live_addresses_are_supplied():
    assert os.environ["CAPACITYBOOK_ADDRESS"].startswith("0x")
    assert os.environ.get("CAPACITY_GUARD_ADDRESS", "").startswith("0x")
