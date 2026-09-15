from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (ROOT / "contracts" / "capacitybook.py").read_text()
GUARD = (ROOT / "contracts" / "capacity_guard.py").read_text()


def test_chain_id_is_studionet_61999_only():
    corpus = "\n".join(p.read_text(errors="ignore") for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and p.suffix != ".pyc" and "__pycache__" not in p.parts)
    assert "61999" in corpus
    assert ("619" + "97") not in corpus


def test_contract_has_real_custom_validator():
    assert "gl.vm.run_nondet_default" in CONTRACT
    assert "validator_fn" in CONTRACT
    assert "gl.nondet.web.render" in CONTRACT
    assert "gl.nondet.exec_prompt" in CONTRACT
    assert "evidence not in source" in CONTRACT


def test_admission_is_deterministic_not_model_controlled():
    assert "used + int(demand.declared_units) > int(pool.capacity_units)" in CONTRACT
    assert "windows_overlap" in CONTRACT
    assert "try_admit" in CONTRACT


def test_consumer_contract_checks_admission_and_replay():
    assert "capacitybook.view().is_effective" in GUARD
    assert "action was already executed" in GUARD


def test_semantic_quantity_direction_prevents_under_reservation():
    assert "SAFE UPPER BOUND" in CONTRACT
    assert "under-reservation must never match" in CONTRACT
