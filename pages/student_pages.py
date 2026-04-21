"""Pages côté Étudiant : profil, notes, emploi du temps, documents, paiements."""
import flet as ft
from database import query, execute
import re

# ---------- Profil ----------
def profil_view(user, page: ft.Page):
    """Affiche la fiche étudiant et permet d'ouvrir un dialogue d'édition."""
    et = user.get("etudiant", {})
    container = ft.Column([], spacing=15)

    def build_profile():
        et_local = user.get("etudiant", {})
        photo = et_local.get("photo_path") or "https://i.pravatar.cc/150"
        container.controls = [
            ft.Row([
                ft.Text("Ma Fiche Étudiant", size=24, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Modifier", icon=ft.Icons.EDIT, on_click=open_edit),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Row([
                ft.CircleAvatar(foreground_image_src=photo, radius=60),
                ft.Column([
                    ft.Text(f"{et_local.get('prenom','')} {et_local.get('nom','')}", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Matricule : {et_local.get('matricule','-') }"),
                    ft.Text(f"Filière : {et_local.get('filiere','-')}"),
                    ft.Text(f"Spécialité : {et_local.get('specialite','-')}"),
                    ft.Text(f"Email : {et_local.get('email','-')}", color=ft.Colors.GREY_700),
                    ft.Text(f"Téléphone : {et_local.get('telephone','-')}", color=ft.Colors.GREY_700),
                ], spacing=4),
            ], spacing=30),
        ]

    # --- Edition ---
    f_nom = ft.TextField(label="Nom", width=320)
    f_pre = ft.TextField(label="Prénom", width=320)
    f_email = ft.TextField(label="Email", width=320)
    f_tel = ft.TextField(label="Téléphone", width=200)
    f_fil = ft.TextField(label="Filière", width=320)
    f_spe = ft.TextField(label="Spécialité", width=320)
    f_photo = ft.TextField(label="Photo URL", width=400)

    def open_edit(e):
        et_local = user.get('etudiant', {})
        f_nom.value = et_local.get('nom','')
        f_pre.value = et_local.get('prenom','')
        f_email.value = et_local.get('email','') or ''
        f_tel.value = et_local.get('telephone','') or ''
        f_fil.value = et_local.get('filiere','') or ''
        f_spe.value = et_local.get('specialite','') or ''
        f_photo.value = et_local.get('photo_path','') or ''
        dlg.open = True
        page.update()

    def close_edit(e=None):
        dlg.open = False
        page.update()

    def save_edit(e):
        # Simple validation
        if f_email.value and not re.match(r"[^@]+@[^@]+\.[^@]+", f_email.value):
            page.snack_bar = ft.SnackBar(ft.Text("Email invalide"), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True; page.update(); return
        try:
            # Update DB
            et_id = user.get('etudiant', {}).get('id')
            if et_id is None:
                # Create new student row if missing
                execute("INSERT INTO etudiants(utilisateur_id, matricule, nom, prenom, email, filiere, specialite, telephone, photo_path) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (user['id'], '', f_nom.value, f_pre.value, f_email.value or None, f_fil.value or None, f_spe.value or None, f_tel.value or None, f_photo.value or None))
                # reload from db
                et = query("SELECT * FROM etudiants WHERE utilisateur_id=%s", (user['id'],))[0]
                user['etudiant'] = et
            else:
                execute("UPDATE etudiants SET nom=%s, prenom=%s, email=%s, telephone=%s, filiere=%s, specialite=%s, photo_path=%s WHERE id=%s",
                        (f_nom.value, f_pre.value, f_email.value or None, f_tel.value or None, f_fil.value or None, f_spe.value or None, f_photo.value or None, et_id))
                # update local user dict
                et = query("SELECT * FROM etudiants WHERE id=%s", (et_id,))[0]
                user['etudiant'] = et
            page.snack_bar = ft.SnackBar(ft.Text("Profil mis à jour"), bgcolor=ft.Colors.GREEN_600)
            page.snack_bar.open = True
            close_edit()
            build_profile()
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erreur : {ex}"), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True
            page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Modifier ma fiche"),
        content=ft.Container(content=ft.Column([f_nom,f_pre,f_email,f_tel,f_fil,f_spe,f_photo], tight=True, scroll=ft.ScrollMode.AUTO), width=480, height=420),
        actions=[
            ft.TextButton("Annuler", on_click=close_edit),
            ft.ElevatedButton("Enregistrer", on_click=save_edit),
        ],
    )
    page.overlay.append(dlg)

    build_profile()
    return container

# ---------- Notes ----------
def notes_view(user):
    if not user.get("etudiant") or not user.get("etudiant").get("id"):
        return ft.Column([ft.Text("Pas de fiche étudiant trouvée.", color=ft.Colors.RED_400)])
    et_id = user["etudiant"]["id"]
    rows = query("""
        SELECT m.intitule, m.coefficient, m.semestre, n.note
        FROM notes n JOIN matieres m ON m.id=n.matiere_id
        WHERE n.etudiant_id=%s ORDER BY m.semestre, m.intitule
    """, (et_id,))

    semestres = {}
    for r in rows:
        semestres.setdefault(r["semestre"], []).append(r)

    blocks = [ft.Text("Mes Notes", size=24, weight=ft.FontWeight.BOLD), ft.Divider()]
    for sem, items in sorted(semestres.items()):
        total_pond = sum(float(i["note"]) * float(i["coefficient"]) for i in items)
        total_coef = sum(float(i["coefficient"]) for i in items)
        moy = total_pond / total_coef if total_coef else 0
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Matière")),
                ft.DataColumn(ft.Text("Coef")),
                ft.DataColumn(ft.Text("Note /20")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(i["intitule"])),
                    ft.DataCell(ft.Text(str(i["coefficient"]))),
                    ft.DataCell(ft.Text(str(i["note"]))),
                ]) for i in items
            ],
        )
        blocks += [
            ft.Text(f"Semestre {sem}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            table,
            ft.Container(
                content=ft.Text(f"Moyenne générale : {moy:.2f} / 20",
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700 if moy >= 10 else ft.Colors.RED_700),
                padding=10,
            ),
            ft.Divider(),
        ]
    return ft.Column(blocks, scroll=ft.ScrollMode.AUTO, spacing=10)

# ---------- Emploi du temps ----------
def emploi_view(user):
    filiere = user["etudiant"]["filiere"]
    rows = query("""
        SELECT e.jour, e.heure_debut, e.heure_fin, e.salle,
               m.intitule, c.professeur
        FROM emploi_temps e
        JOIN cours c ON c.id=e.cours_id
        JOIN matieres m ON m.id=c.matiere_id
        WHERE e.filiere=%s
        ORDER BY FIELD(e.jour,'Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'), e.heure_debut
    """, (filiere,))
    table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(c)) for c in ["Jour","Horaire","Matière","Professeur","Salle"]],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(r["jour"])),
                ft.DataCell(ft.Text(f"{r['heure_debut']} - {r['heure_fin']}")),
                ft.DataCell(ft.Text(r["intitule"])),
                ft.DataCell(ft.Text(r["professeur"])),
                ft.DataCell(ft.Text(r["salle"])),
            ]) for r in rows
        ],
    )
    return ft.Column([
        ft.Text("Emploi du temps", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(), table,
    ], scroll=ft.ScrollMode.AUTO)

# ---------- Documents ----------
def documents_view(user, page: ft.Page):
    rows = query("""
        SELECT d.titre, d.url, d.type, d.semestre, m.intitule
        FROM documents d JOIN matieres m ON m.id=d.matiere_id
        ORDER BY d.semestre, m.intitule
    """)
    items = [ft.Text("Supports de cours", size=24, weight=ft.FontWeight.BOLD), ft.Divider()]
    by_sem = {}
    for r in rows:
        by_sem.setdefault(r["semestre"], []).append(r)
    for sem, docs in sorted(by_sem.items()):
        items.append(ft.Text(f"Semestre {sem}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700))
        for d in docs:
            items.append(ft.Card(content=ft.Container(
                ft.Row([
                    ft.Icon(ft.Icons.PICTURE_AS_PDF if d["type"]=="pdf" else ft.Icons.LINK,
                            color=ft.Colors.RED_400 if d["type"]=="pdf" else ft.Colors.BLUE_400),
                    ft.Column([
                        ft.Text(d["titre"], weight=ft.FontWeight.BOLD),
                        ft.Text(d["intitule"], size=12, color=ft.Colors.GREY_700),
                    ], expand=True),
                    ft.IconButton(ft.Icons.OPEN_IN_NEW,
                                  on_click=lambda e, url=d["url"]: page.launch_url(url)),
                ]), padding=10,
            )))
    return ft.Column(items, scroll=ft.ScrollMode.AUTO, spacing=8)

# ---------- Paiements ----------
def paiements_view(user, page: ft.Page):
    et_id = user["etudiant"]["id"]
    rows = query("SELECT * FROM paiements WHERE etudiant_id=%s ORDER BY date_paiement DESC", (et_id,))
    total_du = sum(float(r["montant_du"]) for r in rows)
    total_paye = sum(float(r["montant_paye"]) for r in rows if r["statut"]=="valide")
    reste = max(total_du - total_paye, 0)
    progress = (total_paye / total_du) if total_du else 0

    def card(label, val, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=12, color=ft.Colors.GREY_700),
                ft.Text(f"{val:,.0f} F", size=20, weight=ft.FontWeight.BOLD, color=color),
            ]),
            bgcolor=ft.Colors.WHITE, padding=15, border_radius=10, expand=True,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12),
        )

    table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(c)) for c in ["Date","Montant","Mode","Statut","Référence"]],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r["date_paiement"])[:10])),
                ft.DataCell(ft.Text(f"{float(r['montant_paye']):,.0f} F")),
                ft.DataCell(ft.Text(r["mode_paiement"])),
                ft.DataCell(ft.Container(
                    ft.Text(r["statut"], color=ft.Colors.WHITE, size=11),
                    bgcolor=ft.Colors.GREEN_600 if r["statut"]=="valide" else ft.Colors.ORANGE_600,
                    padding=ft.padding.symmetric(4,8), border_radius=12,
                )),
                ft.DataCell(ft.Text(r["reference"] or "-")),
            ]) for r in rows
        ],
    )

    # --- Submit new payment (student) ---
    f_paye = ft.TextField(label='Montant payé', width=200)
    dd_mode = ft.Dropdown(label='Mode', width=200, options=[ft.dropdown.Option(m,m) for m in ['Espèces','Virement','Mobile Money','Carte','Chèque']])
    f_ref = ft.TextField(label='Référence', width=300)

    def open_submit(e):
        dlg.open = True; page.update()

    def cancel_submit(e):
        dlg.open = False; page.update()

    def do_submit(e):
        try:
            if not f_paye.value:
                raise ValueError('Montant requis')
            execute('INSERT INTO paiements(etudiant_id,montant_du,montant_paye,mode_paiement,statut,reference) VALUES(%s,%s,%s,%s,%s,%s)',
                    (et_id, 0, float(f_paye.value), dd_mode.value or 'Mobile Money', 'en_attente', f_ref.value or None))
            dlg.open = False
            page.snack_bar = ft.SnackBar(ft.Text('Paiement soumis (en_attente)'), bgcolor=ft.Colors.GREEN_600); page.snack_bar.open=True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f'Erreur : {ex}'), bgcolor=ft.Colors.RED_400); page.snack_bar.open=True; page.update()

    dlg = ft.AlertDialog(modal=True, title=ft.Text('Soumettre un paiement'), content=ft.Column([f_paye, dd_mode, f_ref]), actions=[ft.TextButton('Annuler', on_click=cancel_submit), ft.ElevatedButton('Soumettre', on_click=do_submit)])
    page.overlay.append(dlg)

    return ft.Column([
        ft.Text("État des paiements", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Row([
            card("Total dû", total_du, ft.Colors.BLUE_700),
            card("Déjà payé", total_paye, ft.Colors.GREEN_700),
            card("Reste à payer", reste, ft.Colors.RED_700),
        ], spacing=15),
        ft.Container(height=10),
        ft.Text(f"Progression : {progress*100:.1f} %"),
        ft.ProgressBar(value=progress, height=12, color=ft.Colors.GREEN_600),
        ft.Container(height=20),
        ft.Row([ft.Text("Historique des transactions", size=18, weight=ft.FontWeight.BOLD), ft.ElevatedButton('Soumettre un paiement', icon=ft.Icons.PAYMENTS, on_click=open_submit)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        table,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)
