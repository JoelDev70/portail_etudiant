import pytest

import os
import sys
import pytest

# ensure repo root is on sys.path so tests can import project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import services


class DummyExecute:
    def __init__(self):
        self.calls = []

    def __call__(self, sql, params=None):
        self.calls.append((sql, params))
        # emulate mysql-connector execute returning lastrowid or affected rows
        return {'sql': sql, 'params': params}


def test_admin_update_payment_builds_sql_and_calls_execute(monkeypatch):
    de = DummyExecute()
    monkeypatch.setattr('services.execute', de)

    # call with montant_du and montant_paye and mode
    res = services.admin_update_payment(42, montant_du=100.0, montant_paye=50.0, mode='Virement', statut='valide', reference='ref123')

    assert len(de.calls) == 1
    sql, params = de.calls[0]
    assert 'UPDATE paiements SET' in sql
    # ensure all fields are present in params (order must match construction)
    assert params[-1] == 42
    assert 'montant_du=%s' in sql
    assert 'montant_paye=%s' in sql
    assert 'mode_paiement=%s' in sql
    assert 'statut=%s' in sql
    assert 'reference=%s' in sql
    assert res['params'] == params


def test_admin_update_payment_no_fields_returns_none(monkeypatch):
    # when no fields given, should return None and not call execute
    de = DummyExecute()
    monkeypatch.setattr('services.execute', de)

    res = services.admin_update_payment(1)
    assert res is None
    assert len(de.calls) == 0


def test_admin_update_payment_negative_amount_raises():
    with pytest.raises(ValueError):
        services.admin_update_payment(1, montant_du=-10)


class DummyExecuteDoc(DummyExecute):
    pass


def test_admin_update_document_builds_sql_and_calls_execute(monkeypatch):
    de = DummyExecuteDoc()
    monkeypatch.setattr('services.execute', de)

    res = services.admin_update_document(7, matiere_id=3, semestre=2, titre='New Titre', url='http://ex', typ='pdf')

    assert len(de.calls) == 1
    sql, params = de.calls[0]
    assert 'UPDATE documents SET' in sql
    assert params[-1] == 7
    assert 'matiere_id=%s' in sql
    assert 'semestre=%s' in sql
    assert 'titre=%s' in sql
    assert 'url=%s' in sql
    assert 'type=%s' in sql
    assert res['params'] == params


def test_admin_update_document_no_fields_returns_none(monkeypatch):
    de = DummyExecuteDoc()
    monkeypatch.setattr('services.execute', de)

    res = services.admin_update_document(9)
    assert res is None
    assert len(de.calls) == 0
