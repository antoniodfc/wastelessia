-- Crée un projet de test avec une clé API connue.
-- Idempotent : ré-exécutable sans erreur.
INSERT INTO projects (name, api_key)
VALUES ('demo', 'proj_demo123')
ON CONFLICT (api_key) DO NOTHING;
