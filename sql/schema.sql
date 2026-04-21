-- =====================================================================
-- Portail Étudiant — Schéma MySQL
-- =====================================================================
DROP DATABASE IF EXISTS portail_etudiant;
CREATE DATABASE portail_etudiant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE portail_etudiant;

-- ---------------------------------------------------------------------
-- Utilisateurs (login + rôle)
-- ---------------------------------------------------------------------
CREATE TABLE utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    role ENUM('etudiant','admin') NOT NULL DEFAULT 'etudiant',
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Étudiants (fiche détaillée)
-- ---------------------------------------------------------------------
CREATE TABLE etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL UNIQUE,
    matricule VARCHAR(30) NOT NULL UNIQUE,
    nom VARCHAR(80) NOT NULL,
    prenom VARCHAR(80) NOT NULL,
    email VARCHAR(120),
    telephone VARCHAR(30),
    filiere VARCHAR(100) NOT NULL,
    specialite VARCHAR(100),
    photo_path VARCHAR(255),
    date_naissance DATE,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Matières
-- ---------------------------------------------------------------------
CREATE TABLE matieres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    intitule VARCHAR(150) NOT NULL,
    coefficient DECIMAL(4,2) NOT NULL DEFAULT 1.00,
    semestre INT NOT NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Notes
-- ---------------------------------------------------------------------
CREATE TABLE notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    matiere_id INT NOT NULL,
    semestre INT NOT NULL,
    note DECIMAL(5,2) NOT NULL CHECK (note >= 0 AND note <= 20),
    date_saisie DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (matiere_id) REFERENCES matieres(id) ON DELETE CASCADE,
    UNIQUE KEY uniq_note (etudiant_id, matiere_id, semestre)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Cours
-- ---------------------------------------------------------------------
CREATE TABLE cours (
    id INT AUTO_INCREMENT PRIMARY KEY,
    matiere_id INT NOT NULL,
    professeur VARCHAR(120) NOT NULL,
    FOREIGN KEY (matiere_id) REFERENCES matieres(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Emploi du temps
-- ---------------------------------------------------------------------
CREATE TABLE emploi_temps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cours_id INT NOT NULL,
    filiere VARCHAR(100) NOT NULL,
    jour ENUM('Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi') NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    salle VARCHAR(50) NOT NULL,
    FOREIGN KEY (cours_id) REFERENCES cours(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Documents (supports de cours)
-- ---------------------------------------------------------------------
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    matiere_id INT NOT NULL,
    semestre INT NOT NULL,
    titre VARCHAR(200) NOT NULL,
    url VARCHAR(500) NOT NULL,
    type ENUM('pdf','lien') NOT NULL DEFAULT 'pdf',
    date_ajout DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matiere_id) REFERENCES matieres(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Paiements
-- ---------------------------------------------------------------------
CREATE TABLE paiements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    montant_du DECIMAL(10,2) NOT NULL DEFAULT 0,
    montant_paye DECIMAL(10,2) NOT NULL DEFAULT 0,
    date_paiement DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mode_paiement ENUM('Espèces','Virement','Mobile Money','Carte','Chèque') NOT NULL,
    statut ENUM('valide','en_attente') NOT NULL DEFAULT 'en_attente',
    reference VARCHAR(100),
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Données de démonstration
-- ---------------------------------------------------------------------
-- mot de passe pour TOUS les comptes de démo : "password123"
-- hash bcrypt généré ci-dessous (sera utilisable directement)
INSERT INTO utilisateurs (login, mot_de_passe_hash, role) VALUES
('admin', '$2b$12$KIXQk8g3yY8E5N3p6gQ8eO0wQ8VqgY7r1Y9K5n6zX0lJpZqWfWqGS', 'admin'),
('etudiant1', '$2b$12$KIXQk8g3yY8E5N3p6gQ8eO0wQ8VqgY7r1Y9K5n6zX0lJpZqWfWqGS', 'etudiant'),
('etudiant2', '$2b$12$KIXQk8g3yY8E5N3p6gQ8eO0wQ8VqgY7r1Y9K5n6zX0lJpZqWfWqGS', 'etudiant');

INSERT INTO etudiants (utilisateur_id, matricule, nom, prenom, email, filiere, specialite) VALUES
(2, 'MAT2024001', 'Diallo', 'Awa', 'awa.diallo@univ.edu', 'Informatique', 'Génie Logiciel'),
(3, 'MAT2024002', 'Traoré', 'Moussa', 'moussa.traore@univ.edu', 'Informatique', 'Réseaux');

INSERT INTO matieres (code, intitule, coefficient, semestre) VALUES
('INF101', 'Algorithmique', 3, 1),
('INF102', 'Programmation Python', 3, 1),
('MAT101', 'Mathématiques discrètes', 2, 1),
('INF201', 'Bases de données', 3, 2),
('INF202', 'Réseaux', 2, 2);

INSERT INTO notes (etudiant_id, matiere_id, semestre, note) VALUES
(1,1,1,15.5),(1,2,1,17.0),(1,3,1,12.0),(1,4,2,16.0),(1,5,2,14.5),
(2,1,1,11.0),(2,2,1,13.5),(2,3,1,10.0),(2,4,2,12.0),(2,5,2,15.0);

INSERT INTO cours (matiere_id, professeur) VALUES
(1,'M. Kone'),(2,'Mme Bah'),(3,'M. Sylla'),(4,'Mme Camara'),(5,'M. Barry');

INSERT INTO emploi_temps (cours_id, filiere, jour, heure_debut, heure_fin, salle) VALUES
(1,'Informatique','Lundi','08:00:00','10:00:00','A101'),
(2,'Informatique','Lundi','10:15:00','12:15:00','A102'),
(3,'Informatique','Mardi','08:00:00','10:00:00','B201'),
(4,'Informatique','Mercredi','14:00:00','16:00:00','A101'),
(5,'Informatique','Jeudi','08:00:00','10:00:00','C301');

INSERT INTO documents (matiere_id, semestre, titre, url, type) VALUES
(1,1,'Cours Algo - Chap 1','https://example.com/algo1.pdf','pdf'),
(2,1,'Tutoriel Python','https://docs.python.org/3/tutorial/','lien'),
(4,2,'Support SQL','https://example.com/sql.pdf','pdf');

INSERT INTO paiements (etudiant_id, montant_du, montant_paye, mode_paiement, statut, reference) VALUES
(1, 500000, 300000, 'Mobile Money', 'valide', 'PAY-001'),
(1, 0, 100000, 'Virement', 'en_attente', 'PAY-002'),
(2, 500000, 500000, 'Espèces', 'valide', 'PAY-003');
