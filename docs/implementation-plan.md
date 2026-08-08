# Kang Lee Lab Surveys — Implementation Plan

This document outlines the roadmap to make the React + Django application metadata-driven, enable data collection, and support individual participant profiles via Auth0 and a relational database.

**Status:** Draft  
**Last updated:** 2026-08-08  
**Related:** [ARCHITECTURE.md](../backend/ARCHITECTURE.md), [backend README](../backend/README.md)

---

## Goals

1. **Dynamic survey catalog** — Homepage and Participate tab driven by backend metadata, not hardcoded frontend JSON.
2. **Metadata-driven results** — Results UI rendered from `results_EN.json` (and API payloads), not per-survey React branches.
3. **Data collection** — Consent → survey → persisted responses for research studies.
4. **Participant profiles** — Auth0-authenticated users with consent history and personal survey history.
5. **Sustainable survey authoring** — Schema validation in CI; minimal code changes to add a new survey.

## Principles

- Prefer **configuration (JSON + metadata)** over new routes or JSX branches.
- Keep **anonymous demo surveys** working without login.
- **Fail closed** on data collection: no save without consent; respect `turn_off_data_collection`.
- Ship in **small PRs** per phase; each phase should be deployable independently where possible.

---

## Current state (summary)

| Area | Works today | Gap |
|------|-------------|-----|
| Survey questions | `SurveyPage` + JSON from `GET /survey/{id}` | Multi-page surveys (`pages[1+]`) not navigated |
| Homepage | Hardcoded `*-surveys.json` | `GET /catalog` exists but unused |
| Results | Hardcoded `ResultsPage.jsx` per `survey_id` | `results_EN.json` ignored for display |
| Persistence | `Response` model + `post_to_db` | `post_to_db` commented out in `calculate_results` |
| Data collection | Manga flow prototype | Hardcoded list; consent not stored; manga not saved |
| Auth | Auth0 sign-in UI; local admin for history/CSV | No user FK on responses; JWT not validated on API |
| Validation | JSON schemas in `backend/surveys/static/schemas/` | No automated validation in CI |

---

## Phase 0 — Foundation & hygiene

**Objective:** Safe baseline for feature work on the monorepo.

| Task | Owner hint | Notes |
|------|------------|-------|
| Merge monorepo PR (`monorepo/consolidate-frontend-backend`) | — | Update Heroku/Vercel root dirs to `backend/` / `frontend/` |
| Archive `lab-surveys-frontend` and `lab-surveys-backend` repos | — | Point README to monorepo |
| Document local dev: dual Docker backends + frontend `.env` | — | Root README |
| Add `REACT_APP_AUTH0_*` to `frontend/.env.example` | — | Already in code but not in example file |
| Confirm production API base paths (`/surveys/*` vs root) | — | Align frontend env vars with Heroku |

**Acceptance criteria**

- [ ] Single repo deployed; QA frontend + backend reachable
- [ ] New contributor can run frontend + backend from README

**Estimated effort:** 1–2 days

---

## Phase 1 — Catalog-driven UI

**Objective:** Replace hardcoded survey lists with `GET /catalog`.

### Backend

| Task | Details |
|------|---------|
| Extend catalog entries | Add fields from `metadata_EN.json`: `is_data_collection`, `turn_off_data_collection`, `instructions`, `consent_route_id` (e.g. `manga_consent`) |
| Optional: `GET /survey/{id}/metadata` | Return metadata only if catalog payload is too heavy |
| Document catalog API | OpenAPI or markdown in `backend/README.md` |

### Frontend

| Task | Details |
|------|---------|
| `Homepage.jsx` | Fetch catalog; render `by_category` using `display: true` (or all demo surveys) |
| `DataColSurveys.jsx` | Filter catalog where `is_data_collection === true` |
| `ConsentSurveyCards` | Link from `consent_route_id` or `{route_id}_consent` convention |
| Deprecate | `psychology-surveys.json`, `physiology-surveys.json`, `physical-surveys.json`, `data-collection-surveys.json` (remove after migration) |

**Acceptance criteria**

- [ ] Adding a survey with `display: true` in metadata appears on Home after registry entry (no frontend JSON edit)
- [ ] Manga appears on Participate via `is_data_collection: true`
- [ ] Existing survey links (`/survey/anxiety-moderate`, etc.) still work

**Dependencies:** Phase 0  
**Estimated effort:** 3–5 days

---

## Phase 2 — Response persistence

**Objective:** Reliably save survey submissions with correct typing and metadata gates.

### Backend

| Task | Details |
|------|---------|
| Re-enable `post_to_db` in `calculate_results` | With explicit policy (see below) |
| Save policy | **Demo** (`is_data_collection: false`): optional flag `save_anonymous: true` in metadata, or never save |
| | **Data collection**: save only if `turn_off_data_collection` is false |
| Manga / no-results surveys | New `POST /submit` or branch when `has_results: false` — save answers only |
| Fix `response_type` | Use consistent route_id / survey_id (fix Flask-era mismatches like `DASS_Stress` for ASQ) |
| Admin CSV / history | Unchanged for now (all responses) |

### Frontend

| Task | Details |
|------|---------|
| Optional demo checkbox | Only if product wants Flask-style “participating in study?” on demos; otherwise skip |
| Error handling | Surface API errors when save fails (don’t block results display) |

**Acceptance criteria**

- [ ] Completed demo survey with save enabled → row in `Response` table locally
- [ ] Data-collection survey → row only after consent flow (Phase 3 links consent)
- [ ] `turn_off_data_collection: true` → no row created
- [ ] Manga completion → answers stored

**Dependencies:** Phase 1 (metadata flags)  
**Estimated effort:** 3–4 days

---

## Phase 3 — Data collection & consent records

**Objective:** End-to-end research flow: list study → consent → survey → persisted data.

### Backend

| Task | Details |
|------|---------|
| `ConsentRecord` model | `survey_id`, `consent_version`, `consented_at`, `participant` (nullable until Phase 4), `session_id` (anonymous fallback) |
| `POST /consent` | Body: `route_id`, `consent_version`; returns `consent_id` |
| Generalize `get_consent_file_path` | Derive path from metadata or `{survey_folder}/{survey_folder}-consent.json` |
| Link save to consent | `post_to_db` accepts `consent_id`; reject save for data-collection without valid consent |

### Frontend

| Task | Details |
|------|---------|
| `GeneralConsent` | On “Next”, call `POST /consent` then navigate to survey |
| Pass `consent_id` | Include in survey submit payload |
| `Completed` page | Generic completion route `/survey/{id}/completed` (not only manga) |

**Acceptance criteria**

- [ ] New data-collection study (metadata only + JSON files) → visible on Participate → consent → survey → DB rows for consent + response
- [ ] Submit without consent → 403 for data-collection surveys

**Dependencies:** Phase 2  
**Estimated effort:** 4–6 days

---

## Phase 4 — Auth0 + participant profiles

**Objective:** Authenticated participants with owned history; separate admin access from participant access.

### Backend

| Task | Details |
|------|---------|
| `Participant` model | `auth0_sub` (unique), `email`, `created_at`, `updated_at` |
| JWT validation | Django middleware or decorator using Auth0 JWKS; audience + issuer checks |
| `POST /participants/me` | Upsert participant on first login (called from frontend after Auth0) |
| FK on `Response` | `participant` nullable; `ConsentRecord.participant` |
| `GET /participants/me/responses` | List responses for authenticated user |
| `GET /participants/me/consents` | List consent records |
| Protect admin routes | History + CSV require admin role (Auth0 role or separate admin auth) |

### Frontend

| Task | Details |
|------|---------|
| Auth0 token on API calls | Axios interceptor adds `Authorization: Bearer` |
| Profile page | `/profile` — consents + survey history |
| Header | “My surveys” when signed in |
| Clarify roles | Auth0 = participant; env-based admin login = lab staff only (or migrate admin to Auth0 roles) |

**Acceptance criteria**

- [ ] Signed-in user sees only their responses on profile
- [ ] Anonymous users can still take demo surveys
- [ ] Data-collection save attaches `participant_id` when logged in
- [ ] Admin CSV export still works for staff

**Dependencies:** Phase 2–3  
**Estimated effort:** 5–8 days

---

## Phase 5 — Metadata-driven results UI

**Objective:** One results renderer driven by `results_EN.json` + API response.

### Backend

| Task | Details |
|------|---------|
| Include display config in `/results` | Merge or attach `results_EN.json` content in response |
| Standardize result payload | Map calculator output to `results[]` schema where possible |

### Frontend

| Task | Details |
|------|---------|
| `ResultsRenderer` | Components: `PercentagePie`, `RadarChart`, `ResultsTable`, `ScalarResult`, `TextBlock` |
| Map `result.type` | `scalar`, `percentage`, `text` |
| Map flags | `use_multiedged_graph`, `use_table`, `final_message` |
| Special cases | `dass_multiclass` chart — extend schema or `result_id` hook |
| Remove | Per-survey branches in `ResultsPage.jsx` (keep thin wrapper) |

**Acceptance criteria**

- [ ] ASQ, DASS, NAFLD, MMPI, child BMI, multiclass anxiety match current UX using JSON-driven renderer
- [ ] New survey with `results_EN.json` only needs backend calculator + registry (no `ResultsPage` edit)

**Dependencies:** Phase 1 (metadata paths)  
**Estimated effort:** 5–7 days  
**Note:** Can parallelize with Phase 4 if different owners.

---

## Phase 6 — Survey authoring & quality

**Objective:** Lower cost and risk of adding surveys.

| Task | Details |
|------|---------|
| Port `validate_schema.py` to `backend/` | Validate all surveys in `survey_files/` |
| CI step | `python validate_schema.py all` in `backend-ci.yml` |
| Auto-discovery | Scan `survey_files/*/metadata_EN.json` to build registry (reduce manual `SURVEY_JSON_PATHS`) |
| Multi-page surveys | `SurveyPage` pagination over `pages[]`; progress bar across pages |
| Authoring guide | Update `backend/README.md` for catalog-only listing |

**Acceptance criteria**

- [ ] CI fails on invalid survey JSON
- [ ] New survey folder + metadata with `display: true` appears in catalog without editing `survey_registry.py` (if auto-discovery shipped)
- [ ] Multi-page survey (e.g. manga) navigates all pages

**Dependencies:** Phases 1, 5  
**Estimated effort:** 4–6 days

---

## Phase 7 — English / Chinese (EN / CH)

**Objective:** Users can switch between English and Chinese for app chrome and survey content, with English fallback when a translation is missing.

### Why two layers (recommended approach)

Survey content and app UI have different shapes and lifecycles. **Do not** put survey question text in `react-i18next` files or translate surveys only in the frontend.

| Layer | What | Mechanism |
|-------|------|-----------|
| **A — Survey content** | Questions, metadata, results text, consent forms | Per-language JSON on the backend (already partially designed) |
| **B — App chrome** | Header, buttons, errors, homepage intro, empty states | `react-i18next` (or similar) with `frontend/src/locales/en/` and `frontend/src/locales/ch/` |

ML calculators, `question_id` keys, and stored `response_answers` stay **language-agnostic**. Only display strings change.

### Language codes

- Internal API code: **`EN`** and **`CH`** (matches existing JSON schemas).
- Document that **`CH` = Simplified Chinese** (`zh-Hans` / `zh-CN` in BCP 47).
- Do not rename to `ZH` in files without a migration plan — schemas already use `CH`.

### Backend

| Task | Details |
|------|---------|
| `lang` on all content APIs | Query param `?lang=CH` on `GET /survey/{id}`, `GET /catalog`, `GET /participate/{id}`, `POST /results` |
| Unify file naming | Per survey folder: `metadata_{lang}.json`, `results_{lang}.json`, questions as `{route}.json` **or** `questions_{lang}.json` — pick one convention and document it |
| Fallback | If `metadata_CH.json` missing → `metadata_EN.json`; same for questions and results |
| `get_survey_file_path(survey, lang)` | Resolve language-specific question file path |
| Pass `language` into calculators | `views.calculate_results` already has calculators accepting `language`; wire request `lang` through (currently hardcoded to EN path) |
| Catalog | Each entry includes `available_languages: ["EN", "CH"]` derived from which files exist |
| Consent | `manga-consent.json` → `consent_CH.json` or `manga-consent_CH.json` pattern |
| Validation | `validate_schema.py` runs per language folder suffix |
| Optional persistence | `Response.language` or store `lang` on consent/submit for audit |

### Frontend

| Task | Details |
|------|---------|
| `react-i18next` | App shell strings in `locales/en/common.json`, `locales/ch/common.json` |
| `LanguageProvider` | Context + `localStorage` key `preferred_language`; sync with URL `?lang=CH` |
| Language switcher | Header: EN / 中文 |
| API client | Axios interceptor adds `lang` query param from context |
| Routes | Keep `/survey/asq` (language via context, not path) — avoids doubling routes; optional future `/en/` prefix |
| Fonts | Ensure CSS supports Chinese glyphs (system stack or Noto Sans SC) |
| Auth0 / profile | `preferred_language` on `Participant` (Phase 4); apply on login |

### Content authoring workflow

1. Copy `metadata_EN.json` → `metadata_CH.json`; translate strings.
2. Copy question JSON → Chinese version; **keep identical `question_id` values**.
3. Copy `results_EN.json` → `results_CH.json`; translate labels and `final_message`.
4. Run `validate_schema.py {survey_id} CH`.
5. Catalog picks up CH when files exist.

Start with **one pilot survey** (e.g. DASS anxiety moderate) before translating all surveys.

### Relationship to other phases

- **Phase 1 (catalog):** Catalog should expose `available_languages` early — avoids rework when switching homepage to catalog.
- **Phase 5 (results UI):** Metadata-driven `ResultsRenderer` should read localized `results_{lang}.json` — avoids duplicating Chinese in React.
- **Phase 4 (profiles):** `preferred_language` on participant is the long-term source of truth; localStorage for anonymous users.

**Acceptance criteria**

- [ ] Language switcher toggles header + homepage chrome between EN and CH
- [ ] At least one full survey (questions + results + consent if applicable) available in both languages
- [ ] Submitting in Chinese stores same `question_id` keys as English; ML results unchanged
- [ ] Missing CH file for a survey falls back to EN without error
- [ ] CI validates EN and CH JSON for pilot survey(s)

**Dependencies:** Phase 1 (catalog), Phase 5 (recommended for results); can start backend + chrome in parallel with Phase 1  
**Estimated effort:** 5–8 days (content translation for all surveys is additional lab/writer time)

---

## Suggested PR / issue breakdown

| Issue | Phase | Title |
|-------|-------|-------|
| 1 | 0 | Deploy monorepo; update Heroku/Vercel roots |
| 2 | 0 | Env examples and local dev docs |
| 3 | 1 | Extend catalog API with data-collection fields |
| 4 | 1 | Homepage driven by catalog |
| 5 | 1 | Participate tab driven by catalog |
| 6 | 2 | Re-enable post_to_db with save policy |
| 7 | 2 | Persist manga / no-results submissions |
| 8 | 3 | ConsentRecord model and POST /consent |
| 9 | 3 | Wire GeneralConsent to consent API |
| 10 | 4 | Participant model + Auth0 JWT middleware |
| 11 | 4 | Profile page and scoped history API |
| 12 | 5 | ResultsRenderer from results_EN.json |
| 13 | 6 | Schema validation in CI |
| 14 | 6 | Registry auto-discovery |
| 15 | 6 | Multi-page SurveyPage |
| 16 | 7 | Backend lang param + file resolution + fallback |
| 17 | 7 | react-i18next + language switcher |
| 18 | 7 | Pilot survey full CH translation + CI validation |
| 19 | 7 | preferred_language on Participant (with Phase 4) |

---

## Data model (target)

```text
Participant
  id, auth0_sub (unique), email, preferred_language (EN|CH), created_at

ConsentRecord
  id, participant_id (nullable), session_id, survey_id, consent_version, consented_at

Response
  id, participant_id (nullable), consent_id (nullable),
  response_type, response_answers, response_results,
  response_date, response_time, response_duration
```

Anonymous demo: `participant_id` and `consent_id` null.  
Data collection: `consent_id` required; `participant_id` required when Phase 4 is live (or `session_id` before login).

---

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Dual ML backends (8000 / 8001) | Keep env-based API routing; document in catalog `submit.backend` hint if needed |
| Auth0 + anonymous demos | Nullable FKs; never require login for `is_data_collection: false` |
| Large model files in git | Consider Git LFS for `model.h5` if clone size hurts |
| Breaking production URLs | Feature-flag catalog homepage; keep static JSON fallback one release |
| Supabase free tier sleep | Keep wakeup calls; monitor DB in QA |

---

## Out of scope (for now)

- Public self-registration (accounts created manually in Auth0 per ARCHITECTURE.md)
- Replacing local admin login (can stay until Auth0 roles are ready)
- French (`FR`) and additional locales beyond EN/CH
- Real-time collaboration or in-survey chat

---

## Success metrics

- **Time to add a demo survey:** metadata + JSON + registry (or auto-discovery) only — no React results page edit.
- **Time to add a data-collection study:** same + consent JSON; no new frontend list files.
- **Data integrity:** 100% of data-collection responses have matching `ConsentRecord`.
- **Profile:** authenticated user can view their own history without admin login.
- **i18n:** User can complete a pilot survey end-to-end in Chinese; language preference persists across sessions.

---

## Revision history

| Date | Change |
|------|--------|
| 2026-08-08 | Initial draft after monorepo consolidation and gap analysis |
| 2026-08-08 | Added Phase 7 (EN/CH i18n) |
| 2026-08-08 | Removed legacy Flask app and CI |
