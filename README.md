# Chimera FSU-1Y — The Racing API

> **⚠️ DATA COVERAGE LIMITATIONS — READ FIRST**
>
> **Geographic depth:** This FSU provides *complete* daily racing coverage for
> **UK, Ireland and Hong Kong only**. All other regions (South Africa, UAE, Japan,
> Australia, USA, France, Germany, etc.) are covered at **group/stakes level only**
> — major races, not full daily cards.
>
> **Bookmaker odds:** Multi-bookmaker odds (20+ bookies per runner) are available
> for **UK and Irish racing only** on the Standard plan. Odds for other regions
> are limited or absent depending on plan tier.
>
> **Full daily global coverage** (SA, Japan, UAE, Singapore, etc.) is not available
> through The Racing API. When FSU-1Z (Betfair Exchange) is live, it will serve as
> the global racing layer — Betfair runs markets across all territories where they
> operate, complementing this FSU's UK/IRE depth.
>
> **North America and Australia** full daily coverage are available as paid add-ons
> on The Racing API dashboard — not included in the current subscription.

---

## What This FSU Is

Fractional Service Unit wrapping: [The Racing API](https://theracingapi.com).
Provides UK/Ireland/HK horse racing data: racecards, runners, multi-bookmaker
odds, results, form, and full reference lookups — via a secured REST API with
its own key management layer.

---

## Architecture

```
GitHub (main branch)
  ├── backend/   → Cloud Run (europe-west2, chimera-v4)   — chimera-fsu-1y
  └── frontend/  → Cloudflare Pages (auto-deploy)
```

---

## Endpoints

### Core Racing

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | Health check |
| GET | `/v1/racecards` | X-API-Key | Today's/tomorrow's racecards |
| GET | `/v1/racecards/pro/{race_id}` | X-API-Key | Full racecard with form & ratings |
| GET | `/v1/races` | X-API-Key | List races by date/region/course |
| GET | `/v1/runners/{race_id}` | X-API-Key | Runners for a race |
| GET | `/v1/odds/{race_id}` | X-API-Key | 20+ bookmaker odds per runner (UK/IRE, Standard plan+) |
| GET | `/v1/results` | X-API-Key | Race results |
| GET | `/v1/results/{race_id}` | X-API-Key | Single race result |
| GET | `/v1/form/{horse_id}` | X-API-Key | Horse form (last N runs) |

### Reference / Lookup

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/v1/courses` | X-API-Key | List racecourses (filter by region) |
| GET | `/v1/courses/regions` | X-API-Key | List all racing regions |
| GET | `/v1/horses` | X-API-Key | Search horses by name or ID |
| GET | `/v1/jockeys` | X-API-Key | Search jockeys by name or ID |
| GET | `/v1/trainers` | X-API-Key | Search trainers by name or ID |
| GET | `/v1/owners` | X-API-Key | Search owners by name or ID |
| GET | `/v1/sires` | X-API-Key | Search sires by name or ID |
| GET | `/v1/dams` | X-API-Key | Search dams by name or ID |
| GET | `/v1/damsires` | X-API-Key | Search damsires by name or ID |

### Key Management

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/v1/keys` | X-Admin-Key | Create consumer key |
| GET | `/v1/keys` | X-Admin-Key | List all keys |
| DELETE | `/v1/keys/{key_id}` | X-Admin-Key | Revoke a key |

Swagger UI: `https://your-cloud-run-url/docs`

---

## Racing API Credentials

Authentication: HTTP Basic Auth (username:password).
Credentials stored in GCP Secret Manager — never in code.

- Plan required for odds endpoint: **Standard or above** (20+ bookmakers per runner)
- Data update frequency: every 3 minutes for today's racecards

---

## First-time GCP Setup

```bash
# 1. Store Racing API credentials
gcloud secrets create fsu1y-racing-api-user \
  --replication-policy=automatic --project=chimera-v4
echo -n "S3bM06ZK5gK5YAf6A2BipFF6" | \
  gcloud secrets versions add fsu1y-racing-api-user --data-file=- --project=chimera-v4

gcloud secrets create fsu1y-racing-api-pass \
  --replication-policy=automatic --project=chimera-v4
echo -n "oHvz4ETlhG2LCEb69eoKcD92" | \
  gcloud secrets versions add fsu1y-racing-api-pass --data-file=- --project=chimera-v4

# 2. Generate and store admin key
python3 -c "import secrets; print('admin_' + secrets.token_urlsafe(32))"
echo -n "admin_YOUR_GENERATED_KEY" | \
  gcloud secrets versions add fsu1y-admin-key --data-file=- --project=chimera-v4

# 3. Grant Cloud Run SA access to secrets
gcloud projects add-iam-policy-binding chimera-v4 \
  --member="serviceAccount:$(gcloud iam service-accounts list \
    --filter='displayName:Default compute service account' \
    --format='value(email)' --project=chimera-v4)" \
  --role="roles/secretmanager.secretAccessor"

# 4. Firestore composite index for key auth
gcloud firestore indexes composite create \
  --collection-group=fsu_1y_api_keys \
  --field-config=field-path=key,order=ASCENDING \
  --field-config=field-path=is_active,order=ASCENDING \
  --project=chimera-v4
```

---

## Cloud Run Deploy (backend)

Triggered automatically on push to `main`. Manual trigger:

```bash
cd backend
gcloud builds submit --config=cloudbuild.yaml --project=chimera-v4
```

---

## Cloudflare Pages Setup (frontend)

In Cloudflare Pages → Connect to Git → `charles-ascot/beta-fsu1y`:

| Setting | Value |
|---------|-------|
| Framework preset | Vite |
| Build command | `npm run build` |
| Output directory | `dist` |
| Root directory | `frontend` |

Environment variables (Production):

| Variable | Value |
|----------|-------|
| `VITE_API_BASE_URL` | Cloud Run URL |
| `VITE_FSU_API_KEY` | A `fsu1y_` consumer key |

---

## First Consumer Key

After deployment:

```bash
curl -X POST https://your-cloud-run-url/v1/keys \
  -H "X-Admin-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "mark-racing-dashboard"}'
```

---

## Cache TTLs

| Data | TTL | Reason |
|------|-----|--------|
| Racecards | 3 min | Matches Racing API update frequency |
| Odds | 60 sec | Change rapidly pre-race |
| Results | 5 min | Stable once posted |
| Form | 1 hour | Historical — rarely changes |
| Meetings | 10 min | Stable during race day |
| Reference data | 1 hour | Courses, jockeys, trainers etc. |

---

## Dashboard Layout

The odds grid displays:
- **Rows** = runners (horses)
- **Columns** = bookmakers
- Read across a row to compare all bookmaker prices for one horse
- Best price per runner highlighted in green

---

## Regional Coverage Summary

| Region | Daily Cards | Bookmaker Odds | Notes |
|--------|-------------|----------------|-------|
| Great Britain | ✅ Full | ✅ 20+ bookies | Core coverage |
| Ireland | ✅ Full | ✅ 20+ bookies | Core coverage |
| Hong Kong | ✅ Full | Limited | Core coverage |
| France | ⚠️ Group/stakes | Limited | Core coverage |
| South Africa | ⚠️ Group/stakes | Limited | Core coverage |
| USA | ⚠️ Group/stakes | Limited | Full daily via add-on |
| Australia | ⚠️ Group/stakes | Limited | Full daily via add-on |
| UAE | ⚠️ Group/stakes | Limited | Core coverage |
| Japan | ⚠️ Group/stakes | Limited | Core coverage |
| Germany/Italy/ARG etc | ⚠️ Group/stakes | None | Core coverage |

**Global daily racing supplement:** FSU-1Z (Betfair Exchange) — planned.
