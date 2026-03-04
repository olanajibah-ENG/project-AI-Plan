# Ola AI Trip Planner

## Run Everything With Docker Compose

From the repository root:

```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:8000/api`

The frontend proxies `/api/*` to backend internally, so all app calls work through `http://localhost:8080`.

## Auto Seed (Runs on Container Startup)

Backend automatically seeds demo data each startup (`AUTO_SEED=true` in compose):
- Creates/updates admin user: `admin / 11223344`
- Seeds a large demo catalog (destinations, hotels, events)
- Attaches reproducible local media assets from `Backend/seed_assets`

You can disable seeding by setting `AUTO_SEED=false` for backend service.

## Stop

```bash
docker compose down
```

To remove persisted sqlite/media volumes:

```bash
docker compose down -v
```
