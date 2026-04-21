"""Pages côté Administration : dashboard, CRUD étudiants, saisie notes."""
import flet as ft
from database import query, execute
from datetime import datetime
from services import admin_update_payment, admin_update_document
from auth import hash_password
from database import query, execute

# ---------- Gestion des paiements (admin) ----------
def paiements_admin_view(page: ft.Page):
    rows = query("SELECT p.*, e.matricule, e.nom, e.prenom FROM paiements p JOIN etudiants e ON e.id=p.etudiant_id ORDER BY p.date_paiement DESC")

    def refresh():
        nonlocal rows
        rows = query("SELECT p.*, e.matricule, e.nom, e.prenom FROM paiements p JOIN etudiants e ON e.id=p.etudiant_id ORDER BY p.date_paiement DESC")
        table.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r['date_paiement'])[:10])),
                ft.DataCell(ft.Text(f"{r['matricule']} - {r['nom']} {r['prenom']}")),
                ft.DataCell(ft.Text(f"{float(r['montant_du']):,.0f} F")),
                ft.DataCell(ft.Text(f"{float(r['montant_paye']):,.0f} F")),
                ft.DataCell(ft.Text(r['mode_paiement'])),
                ft.DataCell(ft.Text(r['statut'])),
                        ft.DataCell(ft.Text(r.get('reference') or '-')),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.Icons.EDIT, tooltip='Éditer', on_click=lambda e, row=r: open_edit_payment(row)),
                            ft.IconButton(ft.Icons.CHECK, tooltip='Valider', on_click=lambda e, rid=r['id']: set_status(rid,'valide')),
                            ft.IconButton(ft.Icons.PAUSE, tooltip='Marquer en_attente', on_click=lambda e, rid=r['id']: set_status(rid,'en_attente')),
                            ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, tooltip='Supprimer', on_click=lambda e, rid=r['id']: confirm_delete_payment(rid)),
                        ])),
            ]) for r in rows
        ]
        page.update()

    def set_status(rid, statut):
        try:
            execute("UPDATE paiements SET statut=%s WHERE id=%s", (statut, rid))
            refresh()
            page.snack_bar = ft.SnackBar(ft.Text('Statut mis à jour'), bgcolor=ft.Colors.GREEN_600)
            page.snack_bar.open = True; page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True; page.update()

    # Filter by status
    status_filter = ft.Dropdown(label='Statut', width=200, options=[ft.dropdown.Option('all','Tous'), ft.dropdown.Option('valide','Valide'), ft.dropdown.Option('en_attente','En attente')])
    def apply_filter(e):
        stat = status_filter.value
        if not stat or stat == 'all':
            rows2 = query("SELECT p.*, e.matricule, e.nom, e.prenom FROM paiements p JOIN etudiants e ON e.id=p.etudiant_id ORDER BY p.date_paiement DESC")
        else:
            rows2 = query("SELECT p.*, e.matricule, e.nom, e.prenom FROM paiements p JOIN etudiants e ON e.id=p.etudiant_id WHERE p.statut=%s ORDER BY p.date_paiement DESC", (stat,))
        # reuse rows variable to rebuild table
        nonlocal rows
        rows = rows2
        refresh()

    # Export CSV
    def do_export(e):
        from services import export_payments_csv
        fname = f"exports/paiements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = export_payments_csv(fname, status_filter.value)
        page.snack_bar = ft.SnackBar(ft.Text(f'Exporté: {path}'), bgcolor=ft.Colors.GREEN_600); page.snack_bar.open = True; page.update()

    table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(c)) for c in ["Date","Étudiant","Montant dû","Montant payé","Mode","Statut","Réf","Actions"]],
        rows=[],
    )

    def add_payment(e):
        dlg_add.open = True
        page.update()

    # Add dialog
    dd_et = ft.Dropdown(label='Étudiant', width=400, options=[ft.dropdown.Option(str(r['id']), f"{r['matricule']} - {r['nom']} {r['prenom']}") for r in query('SELECT id, matricule, nom, prenom FROM etudiants ORDER BY nom')])
    f_du = ft.TextField(label='Montant dû', width=200)
    f_paye = ft.TextField(label='Montant payé', width=200)
    dd_mode = ft.Dropdown(label='Mode', width=200, options=[ft.dropdown.Option(m, m) for m in ['Espèces','Virement','Mobile Money','Carte','Chèque']])
    f_ref = ft.TextField(label='Référence', width=300)

    def do_add(e):
        try:
            if not dd_et.value or (not f_du.value and not f_paye.value):
                raise ValueError('Étudiant et montant requis')
            # validate numeric amounts
            try:
                du = float(f_du.value) if f_du.value else 0.0
                paye = float(f_paye.value) if f_paye.value else 0.0
            except Exception:
                raise ValueError('Montants invalides')
            if du < 0 or paye < 0:
                raise ValueError('Les montants doivent être positifs')
            execute('INSERT INTO paiements(etudiant_id,montant_du,montant_paye,mode_paiement,statut,reference) VALUES(%s,%s,%s,%s,%s,%s)',
                    (int(dd_et.value), du, paye, dd_mode.value or 'Espèces', 'valide' if paye>0 else 'en_attente', f_ref.value or None))
            dlg_add.open = False
            refresh()
            page.snack_bar = ft.SnackBar(ft.Text('Paiement ajouté'), bgcolor=ft.Colors.GREEN_600); page.snack_bar.open = True; page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400); page.snack_bar.open = True; page.update()

    # --- Edit payment dialog ---
    f_du_edit = ft.TextField(label='Montant dû', width=200)
    f_paye_edit = ft.TextField(label='Montant payé', width=200)
    dd_mode_edit = ft.Dropdown(label='Mode', width=200, options=[ft.dropdown.Option(m,m) for m in ['Espèces','Virement','Mobile Money','Carte','Chèque']])
    dd_stat_edit = ft.Dropdown(label='Statut', width=200, options=[ft.dropdown.Option('en_attente','En attente'), ft.dropdown.Option('valide','Valide')])
    f_ref_edit = ft.TextField(label='Référence', width=300)
    edit_payment_id = {'v': None}

    def open_edit_payment(row):
        edit_payment_id['v'] = row['id']
        f_du_edit.value = str(row.get('montant_du') or '')
        f_paye_edit.value = str(row.get('montant_paye') or '')
        dd_mode_edit.value = row.get('mode_paiement')
        dd_stat_edit.value = row.get('statut')
        f_ref_edit.value = row.get('reference') or ''
        dlg_edit_pay.open = True
        page.update()

    def do_update_payment(e):
        try:
            pid = edit_payment_id['v']
            # validate numeric input
            mont_du = None
            mont_paye = None
            if f_du_edit.value:
                try:
                    mont_du = float(f_du_edit.value)
                except Exception:
                    raise ValueError('Montant dû invalide')
                if mont_du < 0:
                    raise ValueError('Montant dû doit être >= 0')
            if f_paye_edit.value:
                try:
                    mont_paye = float(f_paye_edit.value)
                except Exception:
                    raise ValueError('Montant payé invalide')
                if mont_paye < 0:
                    raise ValueError('Montant payé doit être >= 0')

            admin_update_payment(pid, montant_du=mont_du, montant_paye=mont_paye, mode=dd_mode_edit.value, statut=dd_stat_edit.value, reference=f_ref_edit.value or None)
            dlg_edit_pay.open = False
            refresh()
            page.snack_bar = ft.SnackBar(ft.Text('Paiement mis à jour'), bgcolor=ft.Colors.GREEN_600); page.snack_bar.open=True; page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400); page.snack_bar.open=True; page.update()

    dlg_edit_pay = ft.AlertDialog(modal=True, title=ft.Text('Éditer paiement'), content=ft.Column([f_du_edit,f_paye_edit,dd_mode_edit,dd_stat_edit,f_ref_edit]), actions=[ft.TextButton('Annuler', on_click=lambda e: setattr(dlg_edit_pay,'open',False) or page.update()), ft.ElevatedButton('Enregistrer', on_click=do_update_payment)])
    page.overlay.append(dlg_edit_pay)

    # generic confirmation dialog used for deletes
    dlg_confirm = ft.AlertDialog(modal=True, title=ft.Text('Confirmer'))
    page.overlay.append(dlg_confirm)

    # --- Confirm delete payment ---
    def confirm_delete_payment(rid):
        def do_confirm(e):
            try:
                execute('DELETE FROM paiements WHERE id=%s', (rid,))
                dlg_confirm.open = False
                refresh()
                page.snack_bar = ft.SnackBar(ft.Text('Paiement supprimé'), bgcolor=ft.Colors.GREEN_600); page.snack_bar.open=True; page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400); page.snack_bar.open=True; page.update()
        dlg_confirm.content = ft.Text(f"Confirmer la suppression du paiement {rid} ?")
        dlg_confirm.actions = [ft.TextButton('Annuler', on_click=lambda e: setattr(dlg_confirm,'open',False) or page.update()), ft.ElevatedButton('Supprimer', on_click=do_confirm)]
        dlg_confirm.open = True; page.update()


    def cancel_add(e):
        dlg_add.open = False
        page.update()

    dlg_add = ft.AlertDialog(
        modal=True,
        title=ft.Text('Ajouter paiement'),
        content=ft.Column([dd_et, f_du, f_paye, dd_mode, f_ref]),
        actions=[ft.TextButton('Annuler', on_click=cancel_add), ft.ElevatedButton('Ajouter', on_click=do_add)],
    )
    page.overlay.append(dlg_add)

    refresh()
    return ft.Column([
        ft.Row([
            ft.Text('Gestion des paiements', size=24, weight=ft.FontWeight.BOLD),
            ft.Row([status_filter, ft.ElevatedButton('Filtrer', on_click=apply_filter), ft.ElevatedButton('Exporter CSV', icon=ft.Icons.FILE_DOWNLOAD, on_click=do_export), ft.ElevatedButton('Ajouter', icon=ft.Icons.ADD, on_click=add_payment)], spacing=8)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(), table
    ], spacing=10)


# ---------- Gestion des documents (admin) ----------
def documents_admin_view(page: ft.Page):
    items = query('SELECT d.*, m.intitule FROM documents d JOIN matieres m ON m.id=d.matiere_id ORDER BY d.semestre, m.intitule')

    container = ft.Column(scroll=ft.ScrollMode.AUTO)

    def refresh():
        nonlocal items
        items = query('SELECT d.*, m.intitule FROM documents d JOIN matieres m ON m.id=d.matiere_id ORDER BY d.semestre, m.intitule')
        build_list()

    def build_list():
        rows = []
        for d in items:
            rows.append(ft.Card(content=ft.Container(ft.Row([ft.Text(d['titre'], weight=ft.FontWeight.BOLD), ft.Text(d['intitule'], size=12, color=ft.Colors.GREY_700), ft.IconButton(ft.Icons.OPEN_IN_NEW, on_click=lambda e, url=d['url']: page.launch_url(url)), ft.IconButton(ft.Icons.EDIT, tooltip='Éditer', on_click=lambda e, doc=d: open_edit_doc(doc)), ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=lambda e, rid=d['id']: confirm_delete_doc(rid))], spacing=10), padding=10)))
        def open_doc_dlg(e):
            dlg.open = True
            page.update()

        container.controls = [ft.Row([ft.Text('Gestion des documents', size=24, weight=ft.FontWeight.BOLD), ft.ElevatedButton('Ajouter', icon=ft.Icons.ADD, on_click=open_doc_dlg)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), ft.Divider()] + rows
        page.update()

    # dialog add
    matieres = query('SELECT id, intitule FROM matieres ORDER BY intitule')
    dd_mat = ft.Dropdown(label='Matière', width=360, options=[ft.dropdown.Option(str(m['id']), m['intitule']) for m in matieres])
    f_title = ft.TextField(label='Titre', width=480)
    f_url = ft.TextField(label='URL', width=480)
    dd_type = ft.Dropdown(label='Type', width=200, options=[ft.dropdown.Option('pdf','pdf'), ft.dropdown.Option('lien','lien')])
    f_sem = ft.TextField(label='Semestre', width=160)

    def do_add_doc(e):
        try:
            if not dd_mat.value or not f_title.value or not f_url.value:
                raise ValueError('Tous les champs requis')
            execute('INSERT INTO documents(matiere_id, semestre, titre, url, type) VALUES(%s,%s,%s,%s,%s)', (int(dd_mat.value), int(f_sem.value or 0), f_title.value, f_url.value, dd_type.value or 'pdf'))
            dlg.open = False
            refresh()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400); page.snack_bar.open = True; page.update()

    def do_delete(rid):
        try:
            execute('DELETE FROM documents WHERE id=%s', (rid,))
            refresh()
            page.snack_bar = ft.SnackBar(ft.Text('Document supprimé'), bgcolor=ft.Colors.GREEN_600); page.snack_bar.open = True; page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400); page.snack_bar.open = True; page.update()

    # confirmation dialog for documents
    dlg_confirm_doc = ft.AlertDialog(modal=True, title=ft.Text('Confirmer'))
    page.overlay.append(dlg_confirm_doc)

    def confirm_delete_doc(rid):
        def do_confirm(e):
            try:
                execute('DELETE FROM documents WHERE id=%s', (rid,))
                dlg_confirm_doc.open = False
                refresh()
                page.snack_bar = ft.SnackBar(ft.Text('Document supprimé'), bgcolor=ft.Colors.GREEN_600); dlg_confirm_doc.open=True; page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400); page.snack_bar.open=True; page.update()
        dlg_confirm_doc.content = ft.Text(f"Confirmer la suppression du document {rid} ?")
        dlg_confirm_doc.actions = [ft.TextButton('Annuler', on_click=lambda e: setattr(dlg_confirm_doc,'open',False) or page.update()), ft.ElevatedButton('Supprimer', on_click=do_confirm)]
        dlg_confirm_doc.open = True; page.update()

    def cancel_doc(e):
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(modal=True, title=ft.Text('Ajouter un document'), content=ft.Column([dd_mat,f_title,f_url,dd_type,f_sem]), actions=[ft.TextButton('Annuler', on_click=cancel_doc), ft.ElevatedButton('Ajouter', on_click=do_add_doc)])
    page.overlay.append(dlg)

    # Edit document dialog
    dd_mat_edit = ft.Dropdown(label='Matière', width=360, options=[ft.dropdown.Option(str(m['id']), m['intitule']) for m in matieres])
    f_title_edit = ft.TextField(label='Titre', width=480)
    f_url_edit = ft.TextField(label='URL', width=480)
    dd_type_edit = ft.Dropdown(label='Type', width=200, options=[ft.dropdown.Option('pdf','pdf'), ft.dropdown.Option('lien','lien')])
    f_sem_edit = ft.TextField(label='Semestre', width=160)
    edit_doc_id = {'v': None}

    def open_edit_doc(doc):
        edit_doc_id['v'] = doc['id']
        dd_mat_edit.value = str(doc['matiere_id'])
        f_title_edit.value = doc.get('titre') or ''
        f_url_edit.value = doc.get('url') or ''
        dd_type_edit.value = doc.get('type')
        f_sem_edit.value = str(doc.get('semestre') or '')
        dlg_edit_doc.open = True
        page.update()

    def do_update_doc(e):
        try:
            did = edit_doc_id['v']
            admin_update_document(did, matiere_id=int(dd_mat_edit.value), semestre=int(f_sem_edit.value or 0), titre=f_title_edit.value, url=f_url_edit.value, type=dd_type_edit.value or 'pdf')
            dlg_edit_doc.open = False
            refresh()
            page.snack_bar = ft.SnackBar(ft.Text('Document mis à jour'), bgcolor=ft.Colors.GREEN_600); page.snack_bar.open = True; page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400); page.snack_bar.open = True; page.update()

    dlg_edit_doc = ft.AlertDialog(modal=True, title=ft.Text('Éditer document'), content=ft.Column([dd_mat_edit,f_title_edit,f_url_edit,dd_type_edit,f_sem_edit]), actions=[ft.TextButton('Annuler', on_click=lambda e: setattr(dlg_edit_doc,'open',False) or page.update()), ft.ElevatedButton('Enregistrer', on_click=do_update_doc)])
    page.overlay.append(dlg_edit_doc)

    build_list()
    return container

# ---------- Dashboard ----------
def dashboard_view(user):
    nb_et = query("SELECT COUNT(*) c FROM etudiants")[0]["c"]
    moy_row = query("SELECT AVG(note) m FROM notes")[0]
    moy = float(moy_row["m"] or 0)
    pay = query("""
        SELECT COALESCE(SUM(montant_du),0) du,
               COALESCE(SUM(CASE WHEN statut='valide' THEN montant_paye ELSE 0 END),0) paye
        FROM paiements
    """)[0]
    taux = (float(pay["paye"]) / float(pay["du"]) * 100) if float(pay["du"]) else 0

    def stat(label, val, icon, color):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=36),
                ft.Column([
                    ft.Text(label, size=12, color=ft.Colors.GREY_700),
                    ft.Text(val, size=22, weight=ft.FontWeight.BOLD),
                ], spacing=2),
            ], spacing=15),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=12, expand=True,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
        )

    return ft.Column([
        ft.Text("Tableau de bord", size=26, weight=ft.FontWeight.BOLD),
        ft.Text("Vue d'ensemble de la promotion", color=ft.Colors.GREY_700),
        ft.Divider(),
        ft.Row([
            stat("Étudiants inscrits", str(nb_et), ft.Icons.PEOPLE, ft.Colors.BLUE_700),
            stat("Moyenne promo", f"{moy:.2f}/20", ft.Icons.GRADE, ft.Colors.GREEN_700),
            stat("Taux de paiement", f"{taux:.1f} %", ft.Icons.PAYMENTS, ft.Colors.ORANGE_700),
        ], spacing=15),
    ], spacing=10)

# ---------- CRUD Étudiants ----------
def etudiants_view(page: ft.Page):
    container = ft.Column(scroll=ft.ScrollMode.AUTO)

    def refresh():
        rows = query("""
            SELECT e.id, e.matricule, e.nom, e.prenom, e.filiere, e.specialite, u.login
            FROM etudiants e JOIN utilisateurs u ON u.id=e.utilisateur_id
            ORDER BY e.nom
        """)
        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(c)) for c in
                     ["Matricule","Nom","Prénom","Filière","Spécialité","Login","Actions"]],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r["matricule"])),
                    ft.DataCell(ft.Text(r["nom"])),
                    ft.DataCell(ft.Text(r["prenom"])),
                    ft.DataCell(ft.Text(r["filiere"])),
                    ft.DataCell(ft.Text(r["specialite"] or "-")),
                    ft.DataCell(ft.Text(r["login"])),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.Icons.EDIT, on_click=lambda e, rid=r["id"]: open_dialog(rid)),
                        ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED,
                                      on_click=lambda e, rid=r["id"]: delete_etudiant(rid)),
                    ])),
                ]) for r in rows
            ],
        )
        container.controls = [
            ft.Row([
                ft.Text("Gestion des étudiants", size=24, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Ajouter", icon=ft.Icons.ADD, on_click=lambda e: open_dialog(None)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(), table,
        ]
        page.update()

    # --- Dialog ajout / édition ---
    f_login = ft.TextField(label="Login")
    f_pwd = ft.TextField(label="Mot de passe", password=True, can_reveal_password=True)
    f_mat = ft.TextField(label="Matricule")
    f_nom = ft.TextField(label="Nom")
    f_pre = ft.TextField(label="Prénom")
    f_email = ft.TextField(label="Email")
    f_fil = ft.TextField(label="Filière")
    f_spe = ft.TextField(label="Spécialité")
    edit_id = {"v": None}

    def open_dialog(rid):
        edit_id["v"] = rid
        if rid:
            r = query("""SELECT e.*, u.login FROM etudiants e
                         JOIN utilisateurs u ON u.id=e.utilisateur_id WHERE e.id=%s""", (rid,))[0]
            f_login.value = r["login"]; f_pwd.value = ""
            f_mat.value=r["matricule"]; f_nom.value=r["nom"]; f_pre.value=r["prenom"]
            f_email.value=r["email"] or ""; f_fil.value=r["filiere"]; f_spe.value=r["specialite"] or ""
        else:
            for f in [f_login,f_pwd,f_mat,f_nom,f_pre,f_email,f_fil,f_spe]:
                f.value = ""
        dlg.open = True
        page.update()

    def close_dialog(e=None):
        dlg.open = False; page.update()

    def save_etudiant(e):
        try:
            # validations
            if not f_login.value:
                snack("Login requis", error=True); return
            if edit_id["v"] is None and not f_pwd.value:
                snack("Mot de passe requis", error=True); return
            if not f_mat.value or not f_nom.value or not f_pre.value:
                snack("Matricule, nom et prénom requis", error=True); return

            if edit_id["v"] is None:
                # create user
                try:
                    uid = execute(
                        "INSERT INTO utilisateurs(login,mot_de_passe_hash,role) VALUES(%s,%s,'etudiant')",
                        (f_login.value, hash_password(f_pwd.value)),
                    )
                except Exception as ex:
                    # log and rethrow to show friendly message
                    print("Erreur INSERT utilisateurs:", ex)
                    raise
                # some DB drivers may not return lastrowid; fallback to SELECT
                if not uid:
                    try:
                        uid = query("SELECT id FROM utilisateurs WHERE login=%s", (f_login.value,))[0]["id"]
                    except Exception:
                        uid = None
                if not uid:
                    raise RuntimeError('Impossible de récupérer l\'id utilisateur créé')

                execute("""INSERT INTO etudiants(utilisateur_id,matricule,nom,prenom,email,filiere,specialite)
                           VALUES(%s,%s,%s,%s,%s,%s,%s)""",
                        (uid, f_mat.value, f_nom.value, f_pre.value, f_email.value or None, f_fil.value or None, f_spe.value or None))
                snack("Étudiant ajouté")
            else:
                execute("""UPDATE etudiants SET matricule=%s,nom=%s,prenom=%s,email=%s,filiere=%s,specialite=%s
                           WHERE id=%s""",
                        (f_mat.value, f_nom.value, f_pre.value, f_email.value, f_fil.value, f_spe.value, edit_id["v"]))
                if f_pwd.value:
                    r = query("SELECT utilisateur_id FROM etudiants WHERE id=%s", (edit_id["v"],))[0]
                    execute("UPDATE utilisateurs SET login=%s, mot_de_passe_hash=%s WHERE id=%s",
                            (f_login.value, hash_password(f_pwd.value), r["utilisateur_id"]))
                else:
                    r = query("SELECT utilisateur_id FROM etudiants WHERE id=%s", (edit_id["v"],))[0]
                    execute("UPDATE utilisateurs SET login=%s WHERE id=%s", (f_login.value, r["utilisateur_id"]))
                snack("Étudiant modifié")
            close_dialog(); refresh()
        except Exception as ex:
            # detailed logging for debugging
            print("Erreur save_etudiant:", ex)
            snack(f"Erreur : {ex}", error=True)

    def delete_etudiant(rid):
        try:
            execute("""DELETE FROM utilisateurs WHERE id=
                       (SELECT utilisateur_id FROM etudiants WHERE id=%s)""", (rid,))
            snack("Étudiant supprimé"); refresh()
        except Exception as ex:
            snack(f"Erreur : {ex}", error=True)

    def snack(msg, error=False):
        page.snack_bar = ft.SnackBar(ft.Text(msg),
                                     bgcolor=ft.Colors.RED_400 if error else ft.Colors.GREEN_600)
        page.snack_bar.open = True; page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Étudiant"),
        content=ft.Container(content=ft.Column(
            [f_login,f_pwd,f_mat,f_nom,f_pre,f_email,f_fil,f_spe],
            tight=True, scroll=ft.ScrollMode.AUTO,
        ), width=400, height=500),
        actions=[
            ft.TextButton("Annuler", on_click=close_dialog),
            ft.ElevatedButton("Enregistrer", on_click=save_etudiant),
        ],
    )
    page.overlay.append(dlg)
    refresh()
    return container

# ---------- Saisie des notes ----------
def saisie_notes_view(page: ft.Page):
    etudiants = query("SELECT id, matricule, nom, prenom FROM etudiants ORDER BY nom")
    matieres = query("SELECT id, intitule, semestre FROM matieres ORDER BY semestre, intitule")

    dd_et = ft.Dropdown(label="Étudiant", width=320,
        options=[ft.dropdown.Option(str(e["id"]), f"{e['matricule']} - {e['nom']} {e['prenom']}") for e in etudiants])
    dd_mat = ft.Dropdown(label="Matière", width=320,
        options=[ft.dropdown.Option(str(m["id"]), f"S{m['semestre']} - {m['intitule']}") for m in matieres])
    f_note = ft.TextField(label="Note (0-20)", width=160)

    def enregistrer(e):
        try:
            if not (dd_et.value and dd_mat.value and f_note.value):
                raise ValueError("Tous les champs sont requis")
            note = float(f_note.value.replace(",", "."))
            if not 0 <= note <= 20: raise ValueError("Note hors limites")
            mat = next(m for m in matieres if m["id"] == int(dd_mat.value))
            execute("""INSERT INTO notes(etudiant_id,matiere_id,semestre,note) VALUES(%s,%s,%s,%s)
                       ON DUPLICATE KEY UPDATE note=VALUES(note), date_saisie=NOW()""",
                    (int(dd_et.value), int(dd_mat.value), mat["semestre"], note))
            page.snack_bar = ft.SnackBar(ft.Text("Note enregistrée"), bgcolor=ft.Colors.GREEN_600)
            page.snack_bar.open = True; f_note.value = ""; page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erreur : {ex}"), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True; page.update()

    return ft.Column([
        ft.Text("Saisie des notes", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        dd_et, dd_mat, f_note,
        ft.ElevatedButton("Enregistrer", icon=ft.Icons.SAVE, on_click=enregistrer),
    ], spacing=15)


# ---------- Gestion des enseignants (simple) ----------
def enseignants_view(page: ft.Page):
    # list distinct professors from cours
    def refresh():
        rows = query('SELECT DISTINCT professeur FROM cours ORDER BY professeur')
        container.controls = [ft.Row([ft.Text('Enseignants', size=24, weight=ft.FontWeight.BOLD), ft.ElevatedButton('Ajouter', icon=ft.Icons.ADD, on_click=open_add)] , alignment=ft.MainAxisAlignment.SPACE_BETWEEN), ft.Divider()]
        for r in rows:
            name = r['professeur']
            container.controls.append(ft.Row([ft.Text(name), ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=lambda e, n=name: confirm_delete(n))]))
        page.update()

    container = ft.Column(scroll=ft.ScrollMode.AUTO)

    # add dialog: pick matiere and enter professor name -> creates a cours row
    matieres = query('SELECT id, intitule FROM matieres ORDER BY intitule')
    dd_mat = ft.Dropdown(label='Matière', width=360, options=[ft.dropdown.Option(str(m['id']), m['intitule']) for m in matieres])
    f_prof = ft.TextField(label='Nom enseignant', width=420)

    def open_add(e):
        f_prof.value = ''
        dd_mat.value = None
        dlg_add.open = True; page.update()

    def do_add(e):
        try:
            if not f_prof.value or not dd_mat.value:
                raise ValueError('Matière et nom requis')
            execute('INSERT INTO cours(matiere_id, professeur) VALUES(%s,%s)', (int(dd_mat.value), f_prof.value))
            dlg_add.open = False
            refresh()
            page.snack_bar = ft.SnackBar(ft.Text('Enseignant ajouté (cours créé)'), bgcolor=ft.Colors.GREEN_600); page.snack_bar.open=True; page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400); page.snack_bar.open=True; page.update()

    dlg_add = ft.AlertDialog(modal=True, title=ft.Text('Ajouter enseignant'), content=ft.Column([dd_mat, f_prof]), actions=[ft.TextButton('Annuler', on_click=lambda e: setattr(dlg_add,'open',False) or page.update()), ft.ElevatedButton('Ajouter', on_click=do_add)])
    page.overlay.append(dlg_add)

    # confirm delete: remove cours rows for that professor
    dlg_confirm_teacher = ft.AlertDialog(modal=True, title=ft.Text('Confirmer'))
    page.overlay.append(dlg_confirm_teacher)

    def confirm_delete(name):
        def do_confirm(e):
            try:
                execute('DELETE FROM cours WHERE professeur=%s', (name,))
                dlg_confirm_teacher.open = False
                refresh()
                page.snack_bar = ft.SnackBar(ft.Text('Enseignant (cours) supprimé'), bgcolor=ft.Colors.GREEN_600); page.snack_bar.open=True; page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400); page.snack_bar.open=True; page.update()
        dlg_confirm_teacher.content = ft.Text(f"Confirmer la suppression de l'enseignant '{name}' et de ses cours ?")
        dlg_confirm_teacher.actions = [ft.TextButton('Annuler', on_click=lambda e: setattr(dlg_confirm_teacher,'open',False) or page.update()), ft.ElevatedButton('Supprimer', on_click=do_confirm)]
        dlg_confirm_teacher.open = True; page.update()

    refresh()
    return container
