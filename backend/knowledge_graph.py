"""
NeuralFortress v3 — Knowledge Graph + Chunking helpers
======================================================
Pure helper functions. All Gemini calls take `client` (your initialized
genai.Client) as a parameter so this module never touches your API key directly.
"""

import json
from google.genai import types
from sqlalchemy import or_


# ----------------------------------------------------------------------
# 1. CHUNKING  (solves the gemini-embedding-001 ~2,048-token input limit)
# ----------------------------------------------------------------------
def chunk_text(text, max_chars=1800, overlap_chars=200):
    """Split text into overlapping word-bounded chunks, each safely under the
    embedding model's input limit. Short text returns a single chunk (identical
    to the old behaviour). Overlap preserves context across chunk boundaries."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    words = text.split()
    chunks, cur, cur_len = [], [], 0
    for w in words:
        add = len(w) + (1 if cur else 0)
        if cur_len + add > max_chars and cur:
            chunks.append(" ".join(cur))
            # carry an overlap tail into the next chunk
            tail, tlen = [], 0
            for tw in reversed(cur):
                if tlen + len(tw) + 1 > overlap_chars:
                    break
                tail.insert(0, tw)
                tlen += len(tw) + 1
            cur, cur_len = tail[:], tlen
        cur.append(w)
        cur_len += add
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def embed_texts(client, texts, batch=50, dims=1536):
    """Embed a list of strings, batched. Returns a list of vectors (lists of floats)."""
    vectors = []
    for i in range(0, len(texts), batch):
        group = texts[i:i + batch]
        resp = client.models.embed_content(
            model="gemini-embedding-001",
            contents=group,
            config=types.EmbedContentConfig(output_dimensionality=dims),
        )
        for e in resp.embeddings:
            vectors.append(e.values)
    return vectors


# ----------------------------------------------------------------------
# 2. TRIPLE EXTRACTION  (entities + typed relationships, via Gemini)
# ----------------------------------------------------------------------
ENTITY_TYPES = {"PERSON", "ORG", "TECHNOLOGY", "CONCEPT", "PLACE", "EVENT", "OTHER"}


def _parse_json_block(raw):
    """Defensively parse a JSON object even if the model wrapped it in prose/fences."""
    raw = raw or ""
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return {}
    return json.loads(raw[start:end + 1])


def extract_triples(client, text):
    """Ask Gemini for knowledge-graph triples. Generation models have a large
    context window, so we feed the whole document (capped) even when we had to
    chunk it for embeddings. Returns a list of dicts."""
    prompt = (
        "Extract knowledge-graph triples from the TEXT. Return STRICT JSON only, no markdown.\n"
        'Schema: {"triples":[{"subject":str,"subject_type":str,"predicate":str,'
        '"object":str,"object_type":str}]}\n'
        "Rules:\n"
        "- subject/object are concise canonical entity names (max 4 words).\n"
        "- predicate is a short verb phrase (1-3 words), e.g. 'orchestrates', 'wrote', 'depends on'.\n"
        "- subject_type/object_type must each be one of: PERSON, ORG, TECHNOLOGY, CONCEPT, PLACE, EVENT, OTHER.\n"
        "- Extract 3-15 of the MOST important, factual relationships. Skip vague filler.\n\n"
        f"TEXT:\n{(text or '')[:12000]}"
    )
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return _parse_json_block(resp.text).get("triples", [])
    except Exception as e:
        print(f"[GRAPH EXTRACT ERROR] {repr(e)}")
        return []


def extract_query_entities(client, query):
    """Pull the key entity names out of a user's question."""
    prompt = (
        "List the key entities (people, technologies, organizations, concepts) in this question "
        'as STRICT JSON, no markdown: {"entities":["..."]}\n\nQUESTION: ' + (query or "")
    )
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return _parse_json_block(resp.text).get("entities", [])
    except Exception as e:
        print(f"[QUERY ENTITY ERROR] {repr(e)}")
        return []


# ----------------------------------------------------------------------
# 3. PERSISTENCE  (upsert entities, store relationships)
# ----------------------------------------------------------------------
def _norm(name):
    return " ".join((name or "").strip().lower().split())


def upsert_entity(db, models, name, etype="OTHER"):
    norm = _norm(name)
    if not norm:
        return None
    ent = db.query(models.Entity).filter(models.Entity.norm_name == norm).first()
    if ent:
        return ent
    t = (etype or "OTHER").upper()
    if t not in ENTITY_TYPES:
        t = "OTHER"
    ent = models.Entity(name=name.strip(), norm_name=norm, type=t)
    db.add(ent)
    db.flush()  # assigns ent.id without committing the whole transaction yet
    return ent


def store_triples(db, models, triples, document_id):
    """Upsert entities and insert relationships with provenance to the document.
    Returns (entities_touched, relationships_added)."""
    rel_count = 0
    touched = set()
    for t in triples:
        subj = (t.get("subject") or "").strip()
        obj = (t.get("object") or "").strip()
        pred = (t.get("predicate") or "").strip()
        if not (subj and obj and pred):
            continue
        s = upsert_entity(db, models, subj, t.get("subject_type"))
        o = upsert_entity(db, models, obj, t.get("object_type"))
        if not (s and o) or s.id == o.id:
            continue
        touched.add(s.id)
        touched.add(o.id)
        db.add(models.Relationship(
            source_id=s.id, target_id=o.id, predicate=pred, document_id=document_id
        ))
        rel_count += 1
    return len(touched), rel_count


# ----------------------------------------------------------------------
# 4. MULTI-HOP TRAVERSAL  (BFS over the relationship graph)
# ----------------------------------------------------------------------
def multi_hop_subgraph(db, models, seed_ids, max_hops=2, max_edges=40):
    """Breadth-first walk outward from seed entities, collecting relationships
    up to `max_hops` away. This is the 'beyond vector distance' step."""
    visited = set(seed_ids)
    frontier = set(seed_ids)
    collected, seen_rel = [], set()
    hops = 0
    while frontier and hops < max_hops and len(collected) < max_edges:
        rels = db.query(models.Relationship).filter(
            or_(models.Relationship.source_id.in_(frontier),
                models.Relationship.target_id.in_(frontier))
        ).limit(max_edges * 2).all()
        next_frontier = set()
        for r in rels:
            if r.id in seen_rel:
                continue
            seen_rel.add(r.id)
            collected.append(r)
            for nid in (r.source_id, r.target_id):
                if nid not in visited:
                    visited.add(nid)
                    next_frontier.add(nid)
            if len(collected) >= max_edges:
                break
        frontier = next_frontier
        hops += 1
    return collected, visited