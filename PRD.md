# Wastelessia — Product Requirements Document
**Version** : 0.1.0  
**Statut** : MVP en cours  
**Positionnement** : Gouvernance financière de la dépense IA pour les startups tech (5-20 devs)

---

## 1. Résumé

Wastelessia est une couche de gouvernance financière qui se pose **par-dessus l'infrastructure IA existante** des startups — sans proxy, sans migration, sans changer une ligne d'architecture.

En 3 lignes de code, les CTOs savent enfin ce que chaque équipe, feature et client leur coûte en tokens. Ils fixent des limites. Ils reçoient un rapport que leur CFO comprend.

**Promesse** :
> "Sachez exactement ce que chaque feature vous coûte en IA — et fixez des limites avant que ça explose."

**Cible** : CTO de startup tech, 5 à 20 devs, dépense IA entre 500€ et 15 000€/mois, budget imprévisible.

---

## 2. Le problème

### Ce qui se passe dans les startups aujourd'hui

- Les devs appellent les APIs LLM directement, sans tagging ni attribution
- Le CTO découvre la facture en fin de mois, sans savoir d'où elle vient
- Il ne peut pas répondre à son CFO : *"quelle feature consomme quoi ?"*
- Un agent mal configuré peut brûler un budget trimestriel en une nuit

### Les chiffres qui valident le problème

- **85%** des entreprises ratent leurs prévisions de coûts IA de plus de 10%
- **68%** sous-estiment leur dépense LLM de première année par un facteur 3x
- Les workflows agentiques consomment **10 à 20x** plus de tokens que les requêtes simples
- Les prix des APIs ont baissé de 80% en un an — mais les budgets ont augmenté de 483%

### Cas réel (Uber, avril 2026)

Uber a déployé Claude Code pour 5 000 ingénieurs en décembre 2025. En avril 2026, l'entreprise avait brûlé **100% de son budget IA annuel en 4 mois**. Pas de guardrails. Pas d'attribution. Pas de visibilité.

---

## 3. Ce que les outils existants ne font pas

| Outil | Force | Angle mort |
|---|---|---|
| **Eden AI** (France) | Gateway unifiée, RGPD | Outil pour devs, pas pour la finance |
| **Helicone** | Observabilité technique | Dashboard ingénieur, pas CFO |
| **LiteLLM** | Proxy open-source | Pas de gouvernance budgétaire |
| **Datadog** | APM + logs | FinOps IA non prioritaire, cher |
| **Cloudflare AI Gateway** | Infra mondiale | Pas d'attribution par feature |

**Le vrai vide** : aucun outil ne fait le pont entre la dépense technique (tokens, latence, modèles) et la gouvernance financière (budget par équipe, attribution par feature, rapport CFO).

---

## 4. La solution

### Principe

Un SDK léger (Python + JS) qui intercepte les métadonnées des appels LLM — sans toucher au contenu des prompts, sans proxy, sans changer l'infrastructure existante.

### Les 3 features du MVP

#### 4.1 SDK de tracking

```python
from wastelessia import track

@track(team="backend", feature="search", env="prod")
def call_claude(prompt):
    return anthropic.messages.create(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": prompt}]
    )
```

Ce que le SDK capture à chaque appel :
- Tokens input / output
- Modèle utilisé
- Coût calculé (tarifs publics fournisseurs)
- Timestamp, durée, succès/erreur
- Tags : team, feature, env, client (optionnel)

Ce que le SDK **ne fait pas** :
- Stocker les prompts ou les réponses
- Intercepter le trafic réseau
- Modifier les requêtes envoyées aux LLMs

#### 4.2 Dashboard de visibilité

**Vue 1 — Dépense par feature (mois en cours)**

```
Juin 2026 — Dépense IA totale : 3 847 €

Par feature :
  code-agent      1 441 €   ████████░░  37%
  search          1 203 €   ███████░░░  31%
  chat-support      892 €   █████░░░░░  23%
  autres            311 €   ██░░░░░░░░   8%

Projection fin de mois : 5 100 €
Budget configuré       : 4 000 €  ⚠️ Dépassement probable
```

**Vue 2 — Guardrails budgétaires**

Interface pour configurer des règles :

```
Feature "code-agent"  →  alerte si > 2 000 € / mois   [configuré ✓]
Feature "search"      →  alerte si > 1 500 € / mois   [configuré ✓]
Team "frontend"       →  blocage si > 500 € / mois    [configuré ✓]
```

Déclenchement : email immédiat + webhook Slack optionnel.

#### 4.3 Rapport CFO automatique

Email HTML envoyé chaque lundi matin. Lisible par un non-technicien.

```
Semaine du 9 au 15 juin 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dépense totale    :  961 €
vs semaine préc.  :  +12% (856 €)
Projection mois   :  4 200 €  ⚠️ Budget : 4 000 €

Top 3 features :
  1. code-agent    → 412 € (43%)
  2. search        → 287 € (30%)
  3. chat-support  → 198 € (21%)

Action recommandée : revoir le budget "code-agent"
ou ajuster le guardrail à 1 800 €/mois.
```

---

## 5. Architecture technique

### Stack MVP

| Composant | Technologie | Justification |
|---|---|---|
| SDK Python | Package PyPI léger | Intégration en 1 ligne |
| SDK JS/TS | npm package | Couverture Node.js / Next.js |
| Backend API | FastAPI (Python) | Rapide à développer, performant |
| Base de données | PostgreSQL | 1 table `events`, index sur tags + timestamp |
| Hébergement | Hetzner VPS (6€/mois) | Suffisant pour les 5 premiers clients |
| Emails | Resend ou SendGrid | Rapport CFO automatique |
| Dashboard | React + Recharts | Minimaliste, fonctionnel |

### Modèle de données (table `events`)

```sql
CREATE TABLE events (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id   UUID NOT NULL,
  timestamp    TIMESTAMPTZ NOT NULL,
  model        TEXT NOT NULL,
  tokens_in    INTEGER NOT NULL,
  tokens_out   INTEGER NOT NULL,
  cost_usd     NUMERIC(10, 6) NOT NULL,
  duration_ms  INTEGER,
  success      BOOLEAN NOT NULL DEFAULT TRUE,
  tag_team     TEXT,
  tag_feature  TEXT,
  tag_env      TEXT,
  tag_client   TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_project_timestamp ON events (project_id, timestamp);
CREATE INDEX idx_events_tags ON events (project_id, tag_team, tag_feature);
```

### Endpoint de collecte

```
POST https://api.wastelessia.com/v1/events
Authorization: Bearer proj_xxx

{
  "timestamp": "2026-06-17T14:32:00Z",
  "model": "claude-sonnet-4-6",
  "tokens_in": 1240,
  "tokens_out": 380,
  "cost_usd": 0.0058,
  "duration_ms": 1240,
  "success": true,
  "tags": {
    "team": "backend",
    "feature": "search",
    "env": "prod"
  }
}
```

---

## 6. Ce qui est hors scope (MVP)

Les éléments suivants sont **explicitement exclus** du MVP et traités après validation :

- Proxy HTTP / interception du trafic
- Optimisation automatique (routing, compression, cache)
- SDK Go, Java, Ruby
- SSO / SAML
- Facturation automatique (Stripe)
- Comparaison inter-modèles
- On-premise / self-hosted
- Support multi-tenant avancé

---

## 7. Roadmap des 3 semaines

### Semaine 1 — Le SDK fonctionne

| Jour | Tâche | Livrable |
|---|---|---|
| J1-J2 | SDK Python avec `@track` | `pip install wastelessia` fonctionnel |
| J3 | Backend FastAPI + PostgreSQL | Endpoint POST /events opérationnel |
| J4 | SDK JS/TS | `npm install wastelessia` fonctionnel |
| J5 | Test end-to-end sur usage propre | Events visibles en base |

**Critère de succès** : mes propres appels Claude sont trackés et stockés.

### Semaine 2 — Le dashboard existe

| Jour | Tâche | Livrable |
|---|---|---|
| J1-J2 | Vue dépense par feature | Graphique lisible avec données réelles |
| J3 | Système d'alertes (règles + email) | Alerte déclenchée sur seuil test |
| J4 | Rapport CFO hebdomadaire | Email envoyé automatiquement lundi 8h |
| J5 | README d'intégration (15 lignes) | Doc suffisante pour s'auto-onboarder |

**Critère de succès** : je peux faire une démo live de 10 minutes avec mes propres données.

### Semaine 3 — Les 5 premiers clients

| Jour | Tâche | Livrable |
|---|---|---|
| J1-J2 | Contacter 10 CTOs (LinkedIn, Slack, réseau) | 5 réponses positives |
| J3-J4 | Onboarding manuel (appel 30 min + intégration guidée) | SDK installé chez 5 clients |
| J5 | Premier feedback structuré | Liste des 3 frictions principales |

**Critère de succès** : 5 clients actifs avec des données réelles qui tournent sans intervention.

---

## 8. Métriques de succès

### J+14 après onboarding (test de valeur)

Question posée à chaque client :
> *"Est-ce que tu as appris quelque chose sur ta dépense IA que tu ne savais pas avant ?"*

Si **oui** → la valeur est prouvée.  
Si **non** → problème de tagging ou de présentation des données. On itère.

### KPIs MVP (fin semaine 3)

| Métrique | Cible |
|---|---|
| Clients actifs | 5 |
| SDK installé et qui envoie des events | 5/5 |
| Taux de rétention à J+14 | > 80% (4/5 utilisent encore) |
| NPS informel | > 7/10 |
| Problème #1 identifié | 1 insight clair pour l'itération suivante |

### KPIs post-MVP (mois 3)

| Métrique | Cible |
|---|---|
| Clients payants | 15 |
| MRR | 2 000 € |
| Churn mensuel | < 5% |
| Temps d'intégration SDK | < 30 minutes |
| NPS | > 40 |

---

## 9. Pricing post-validation

Applicable à partir du mois 4 (après 3 mois gratuits pour les beta testeurs).

| Plan | Prix | Projets | Events/mois | Features clés |
|---|---|---|---|---|
| **Starter** | 49 €/mois | 3 | 1M | Dashboard, alertes email |
| **Pro** | 149 €/mois | 10 | 10M | + Slack, + rapport CFO, + export CSV |
| **Business** | 499 €/mois | Illimité | Illimité | + Rapport CFO personnalisé, + support dédié |

**Période beta** : 3 mois gratuits pour les 5 premiers clients, en échange de 30 min de feedback hebdomadaire.

---

## 10. Analyse des risques MVP

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Le SDK ajoute de la latence | Faible | Élevé | Envoi asynchrone des events, zéro impact sur le call LLM |
| Les clients ne taguent pas correctement | Élevée | Moyen | Onboarding manuel, revue des tags à J+3 |
| Les données sont insuffisantes pour le rapport | Moyenne | Moyen | Minimum 7 jours de données avant le premier rapport |
| Concurrent sort la même feature | Faible | Moyen | Avance de 3 semaines + réseau de beta testeurs |
| Les 5 clients n'utilisent pas après J+14 | Moyenne | Élevé | Feedback à J+7 pour corriger avant J+14 |

---

## 11. Différenciation

### Pourquoi ce n'est pas Eden AI

Eden AI est une gateway pour devs. Wastelessia est un outil pour que le CTO puisse parler à son CFO. Les deux sont complémentaires — Wastelessia fonctionne **par-dessus** Eden AI, Helicone, ou les APIs directes.

### Pourquoi ce n'est pas Datadog

Datadog coûte cher et est orienté performance technique. Wastelessia est orienté gouvernance financière. Simple, rapide, abordable.

### L'avantage défendable

- **Intégration 3 lignes** : moins de friction que tout ce qui existe
- **Rapport CFO natif** : traduit les tokens en euros, pas en métriques techniques
- **Guardrails proactifs** : alerte avant le dépassement, pas après
- **Positionné France/Europe** : RGPD, support en français, pricing en euros

---

## 12. Prochaine étape immédiate

**Cette semaine** : écrire le décorateur `@track` en Python (20 lignes), l'intégrer sur son propre usage de Claude, et mesurer sa propre dépense pendant 7 jours.

Ce chiffre personnel — vérifié, honnête, sur un usage réel — est le premier argument de vente pour les 5 premiers clients.

---

*Document vivant — mis à jour à chaque itération.*  
*Version 0.1.0 — Juin 2026*
