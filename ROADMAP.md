# FastAPI Batteries — Roadmap

## Phase 0 — Foundation ✅ (current state)

**Goal:** Stable data layer + migrations + CLI

**Status:** In progress / mostly done

- ✅ SQLModel-based `BaseModel`
- ✅ Common model mixins (timestamps, IDs, etc.)
- ✅ `BaseCRUD` with basic CRUD operations
- ✅ Async-first DB configuration
- ✅ Alembic integration
- ✅ Typer-based CLI
- ✅ PostgreSQL & SQLite support
- ✅ Environment-driven configuration

**Exit criteria:**
- Public API for `BaseModel` and `BaseCRUD` is stable
- No breaking changes without major version bump

---

## Phase 1 — Hardening & DX (v0.2) ✅

**Goal:** Make it safe, predictable, and pleasant to use

**Status:** Complete

### Core
- ✅ Document BaseModel & BaseCRUD contracts
- ✅ Type-safety improvements (generics, bounds)
- ✅ Better error messages for misconfiguration
- ✅ Fix critical package import bug (src. prefix)
- ✅ Add get_or_create() to BaseCRUD

### CLI
- ✅ CLI command discovery cleanup
- ✅ Consistent command naming
- ✅ `--dry-run` support where applicable
- ✅ Better help text & examples
- ✅ Add migration management commands (current, history, heads, stamp)

### Testing
- ✅ Integration tests (SQLite + Postgres)
- ⬜ Migration test coverage (deferred to Phase 2)
- ✅ CRUD behavior tests (25 tests passing)

**Exit criteria:**
- ✅ Confident minor releases
- ✅ Safe to recommend for new projects

---

## Phase 2 — Fixtures & Data Lifecycle (v0.3)

**Goal:** First-class data management (Django-level feature parity)

### Fixtures
- ⬜ `fixtures dump` (JSON)
- ⬜ `fixtures load`
- ⬜ SQLModel auto-discovery
- ⬜ Deterministic ordering
- ⬜ Transactional load
- ⬜ Idempotent inserts (`merge`)

### CLI
```bash
fastapi-batteries fixtures dump
fastapi-batteries fixtures load fixtures.json
```

### Safety
- ⬜ Confirmation for destructive operations
- ⬜ `--truncate` / `--append` modes
- ⬜ Rollback on failure

**Exit criteria:**
- Dump → wipe DB → load restores state
- Fixtures usable outside of tests (staging/prod)

---

## Phase 3 — Relationships & Advanced Fixtures (v0.4)

**Goal:** Handle real-world schemas safely

- ⬜ FK dependency resolution
- ⬜ Topological sorting of models
- ⬜ Multi-pass insert for circular deps
- ⬜ Optional natural keys
- ⬜ UUID and composite PK support

**Exit criteria:**
- Works with non-trivial schemas
- Predictable fixture loading order

---

## Phase 4 — Developer Utilities (v0.5)

**Goal:** Improve day-to-day developer workflow

- ⬜ `dev` command (runserver + env)
- ⬜ `shell` command (async DB shell)
- ⬜ Optional auto-migrate on startup
- ⬜ Optional fixture seeding for dev

**Exit criteria:**
- Faster local development
- Clear separation between dev and prod tools

---

## Phase 5 — Extensibility & Plugins (v0.6)

**Goal:** Avoid core bloat while enabling customization

- ⬜ Pluggable fixture formats (YAML, custom)
- ⬜ Custom model hooks for dump/load
- ⬜ CLI extension points
- ⬜ Multiple database support (named DBs)

**Exit criteria:**
- Users can extend without forking
- Core remains small

---

## Phase 6 — Stabilization & v1.0

**Goal:** Long-term stability

- ⬜ Freeze public APIs
- ⬜ Full documentation
- ⬜ Migration guides
- ⬜ Deprecation policy
- ⬜ Backward compatibility guarantees

**Exit criteria:**
- v1.0 release
- “Safe default” recommendation for FastAPI + SQLModel projects

---

## Non-goals (important to state)

FastAPI Batteries will **not**:
- ❌ Provide auth/user models
- ❌ Replace FastAPI dependency injection
- ❌ Add admin panels
- ❌ Hide SQLAlchemy/SQLModel behavior

---

## Strategic advice (short)

- Ship **Phase 2 (fixtures)** early — that’s your differentiator
- Delay renaming until after adoption
- Guard `BaseCRUD` API carefully (breaking changes hurt)
