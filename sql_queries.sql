
-- SQL Requêtes - My English Vocabulary Training
-- Base de données : vocabulary.db (SQLite)
-- Objectif : Vérification des données via des requêtes SQL


--tous les utilisateurs
SELECT * FROM users;


--Pseudo et  rôle de chaque utilisateur
SELECT username, role FROM users;


-- Afficher  les administrateurs
SELECT username FROM users
WHERE role = 'admin';


--  Afficher  les mots avec leur traduction
SELECT english, french FROM words;


--  les mots maîtrisés
SELECT * FROM words
WHERE mastered = 1;


--  nombre total de mots
SELECT COUNT(*) AS total_mots FROM words;


-- Nombre de mots par utilisateur
SELECT u.username, COUNT(w.english) AS nb_mots
FROM users u
INNER JOIN words w ON w.user_id = u.id
GROUP BY u.username;


-- mots non maîtrisés avec le pseudo de l'utilisateur
SELECT u.username, w.english, w.french
FROM users u
INNER JOIN words w ON w.user_id = u.id
WHERE w.mastered = 0;
