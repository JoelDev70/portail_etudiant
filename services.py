"""Fonctions métier réutilisables pour paiements et documents.
Ces fonctions encapsulent l'accès DB et la validation pour faciliter les tests.
"""
from database import query, execute
import csv
import os
from datetime import datetime


def submit_payment(etudiant_id: int, montant_paye: float, mode: str = 'Mobile Money', reference: str | None = None):
    if montant_paye is None or float(montant_paye) <= 0:
        raise ValueError('Le montant doit être strictement positif')
    # Insert as en_attente by default
    return execute('INSERT INTO paiements(etudiant_id,montant_du,montant_paye,mode_paiement,statut,reference) VALUES(%s,%s,%s,%s,%s,%s)',
                   (int(etudiant_id), 0, float(montant_paye), mode or 'Mobile Money', 'en_attente', reference or None))


def admin_add_payment(etudiant_id: int, montant_du: float, montant_paye: float, mode: str, reference: str | None):
    if float(montant_du) < 0 or float(montant_paye) < 0:
        raise ValueError('Les montants doivent être positifs')
    statut = 'valide' if float(montant_paye) > 0 else 'en_attente'
    return execute('INSERT INTO paiements(etudiant_id,montant_du,montant_paye,mode_paiement,statut,reference) VALUES(%s,%s,%s,%s,%s,%s)',
                   (int(etudiant_id), float(montant_du), float(montant_paye), mode or 'Espèces', statut, reference or None))


def admin_update_payment(payment_id: int, montant_du: float | None = None, montant_paye: float | None = None, mode: str | None = None, statut: str | None = None, reference: str | None = None):
    # Build dynamic update
    sets = []
    params = []
    if montant_du is not None:
        if float(montant_du) < 0: raise ValueError('Montant dû invalide')
        sets.append('montant_du=%s'); params.append(float(montant_du))
    if montant_paye is not None:
        if float(montant_paye) < 0: raise ValueError('Montant payé invalide')
        sets.append('montant_paye=%s'); params.append(float(montant_paye))
    if mode is not None:
        sets.append('mode_paiement=%s'); params.append(mode)
    if statut is not None:
        sets.append('statut=%s'); params.append(statut)
    if reference is not None:
        sets.append('reference=%s'); params.append(reference)
    if not sets:
        return None
    sql = 'UPDATE paiements SET ' + ','.join(sets) + ' WHERE id=%s'
    params.append(int(payment_id))
    return execute(sql, tuple(params))


def export_payments_csv(file_path: str, status_filter: str | None = None):
    sql = 'SELECT p.*, e.matricule, e.nom, e.prenom FROM paiements p JOIN etudiants e ON e.id=p.etudiant_id'
    params = ()
    if status_filter and status_filter != 'all':
        sql += ' WHERE p.statut=%s'
        params = (status_filter,)
    sql += ' ORDER BY p.date_paiement DESC'
    rows = query(sql, params)
    os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['date_paiement','matricule','nom','prenom','montant_du','montant_paye','mode','statut','reference'])
        for r in rows:
            w.writerow([str(r.get('date_paiement'))[:19], r.get('matricule'), r.get('nom'), r.get('prenom'), r.get('montant_du'), r.get('montant_paye'), r.get('mode_paiement'), r.get('statut'), r.get('reference')])
    return file_path


def admin_add_document(matiere_id: int, semestre: int, titre: str, url: str, typ: str = 'pdf'):
    if not titre or not url:
        raise ValueError('Titre et URL requis')
    return execute('INSERT INTO documents(matiere_id, semestre, titre, url, type) VALUES(%s,%s,%s,%s,%s)', (int(matiere_id), int(semestre), titre, url, typ))


def admin_update_document(doc_id: int, matiere_id: int | None = None, semestre: int | None = None, titre: str | None = None, url: str | None = None, typ: str | None = None):
    sets = []
    params = []
    if matiere_id is not None:
        sets.append('matiere_id=%s'); params.append(int(matiere_id))
    if semestre is not None:
        sets.append('semestre=%s'); params.append(int(semestre))
    if titre is not None:
        sets.append('titre=%s'); params.append(titre)
    if url is not None:
        sets.append('url=%s'); params.append(url)
    if typ is not None:
        sets.append('type=%s'); params.append(typ)
    if not sets:
        return None
    sql = 'UPDATE documents SET ' + ','.join(sets) + ' WHERE id=%s'
    params.append(int(doc_id))
    return execute(sql, tuple(params))


def admin_delete_document(doc_id: int):
    return execute('DELETE FROM documents WHERE id=%s', (int(doc_id),))


if __name__ == '__main__':
    # quick manual test for export (not run in CI)
    path = export_payments_csv('exports/paiements_test.csv', None)
    print('Exported to', path)
