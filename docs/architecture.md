# Architecture and data flow

## Dependency direction

`routes → services → repositories / AI modules → infrastructure`

Routes validate transport data and enforce authentication. Services coordinate a use case. Repositories contain MongoDB access. The ingestion, retrieval, audit, and graph modules do not depend on React or FastAPI route objects.

## Document flow

1. The route verifies the JWT and project owner.
2. `DocumentService` validates extension, size, and content.
3. The loader extracts pages while retaining page numbers when available.
4. The chunker prefers requirement/section boundaries, with bounded overlap.
5. OpenAI creates embeddings when configured.
6. MongoDB stores chunks with project, document, filename, version, page, and chunk IDs.
7. A document becomes `processed`; failures become `failed` with a controlled message.

Deleting a document removes both the stored upload and its indexed chunks.

## Grounded chat graph

```text
START → retrieve → relevant? ─ yes → generate → END
                    │
                    no
                    ▼
                 retries left? ─ yes → rewrite → retrieve
                    │
                    no
                    ▼
             insufficient evidence → END
```

The retry limit is explicit. Generation receives only selected chunks. Uploaded text is labelled untrusted and cannot override the system instruction. Original evidence—not a generated paraphrase—is returned to the UI.

## Retrieval strategy

The current provider combines lexical overlap, exact identifier bonus, and cosine similarity. Broad questions use bounded deterministic query expansion, while exact requirement IDs skip expansion. Natural-language document type/version constraints are converted only through an allowlist. Candidates are reranked for the original question, and relevant original sentences can be compressed for generation; the UI still receives the untouched evidence chunks. It fetches a bounded project-scoped candidate set. This is simple to learn and works with local MongoDB. For a large production corpus, replace its `search` implementation with MongoDB Atlas Vector Search and Atlas Search fusion without changing routes or UI.

## Human review

Audit output starts as `pending`. Approve/reject/needs-evidence decisions record reviewer ID, timestamp, and comment. Reports retain the original candidate, evidence, and decision state.

## Security boundaries

- Every project endpoint verifies `owner_id`.
- Every chunk query includes `project_id`.
- Filenames are stripped to a basename; stored filenames are random UUIDs.
- Secrets are backend-only environment variables.
- Passwords use Argon2 and tokens have expiration.
- Upload paths are resolved and checked against the upload root.
- External web search only runs when the user enables it.

