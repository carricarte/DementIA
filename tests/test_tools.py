import pytest

from backend.tools.calculators import (
    donepezil_dose,
    interpret_cdr,
    interpret_mmse,
    interpret_moca,
    memantine_dose,
)


def test_cdr_interpretation():
    assert "No impairment" in interpret_cdr(0.0)
    assert "Mild" in interpret_cdr(1.0)
    assert "Moderate" in interpret_cdr(2.0)
    assert "Severe" in interpret_cdr(3.0)


def test_cdr_unknown_score():
    result = interpret_cdr(99.0)
    assert "99" in result


def test_mmse_interpretation():
    assert "Normal" in interpret_mmse(28)
    assert "Mild" in interpret_mmse(20)
    assert "Severe" in interpret_mmse(5)


def test_moca_interpretation():
    assert "Normal" in interpret_moca(27)
    assert "Mild" in interpret_moca(22)


def test_donepezil_initiation():
    dose = donepezil_dose("initiation")
    assert "5 mg" in dose["dose"]


def test_donepezil_maintenance_severe():
    dose = donepezil_dose("maintenance", severe=True)
    assert "23" in dose["dose"]


def test_memantine_titration():
    dose = memantine_dose("initiation")
    assert "titration" in dose
