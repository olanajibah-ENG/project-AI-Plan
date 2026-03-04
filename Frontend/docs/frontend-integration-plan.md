# Frontend Integration Plan (Persisted)

## Scope
- Stack: Vite + React + TypeScript
- UX: Arabic-first RTL
- Modules: Auth + AI Trip Planner + Admin CRUD (destinations/hotels/events)
- Data: React Query + Axios
- Auth: JWT in localStorage + refresh-on-401

## Milestones
- M1 Foundation: routing, providers, design tokens, API client
- M2 Auth + Guards: login/register, role redirects, protected routes
- M3 AI Planner: session-aware chat, options rendering, plan confirmation
- M4 Admin CRUD: destinations/hotels/events create-edit-delete, image upload
- M5 QA + Hardening: unit tests + integration/E2E foundations

## Implemented Artifacts
- App shell and auth layouts
- Global RTL setup and design system primitives
- API contracts and typed models
- Auth flows and storage utilities
- AI chat page with state rendering and option confirmation
- Admin management pages for destinations, hotels, events
- Vitest unit tests for key reliability areas

## Feature Flags (Ready to Add)
- ENABLE_ADMIN_UI
- ENABLE_AI_CHAT

## Acceptance Baseline
- Route guards enforce auth and role
- AI flow supports multi-turn session and option confirmation
- Admin pages support CRUD and multipart image uploads
- Frontend builds successfully and core unit tests pass
