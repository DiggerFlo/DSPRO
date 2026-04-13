
SELECT COUNT(*) AS total_chunks
FROM embeddings;

-- CHUNKS MIT ALLEN METADATEN 
SELECT
    e.id                                                                  AS row_id,
    MAX(CASE WHEN m.key = 'article_id'      THEN m.string_value END)     AS article_id,
    MAX(CASE WHEN m.key = 'chunk_index'     THEN m.int_value    END)     AS chunk_index,
    MAX(CASE WHEN m.key = 'title'           THEN m.string_value END)     AS title,
    MAX(CASE WHEN m.key = 'category'        THEN m.string_value END)     AS ressort,
    MAX(CASE WHEN m.key = 'author'          THEN m.string_value END)     AS autor,
    MAX(CASE WHEN m.key = 'published_date'  THEN m.string_value END)     AS datum,
    SUBSTR(MAX(CASE WHEN m.key = 'chroma:document' THEN m.string_value END), 1, 120) AS text_vorschau
FROM embeddings e
LEFT JOIN embedding_metadata m ON e.id = m.id
GROUP BY e.id
ORDER BY datum DESC, article_id, chunk_index
LIMIT 100;

-- RESSORT-VERTEILUNG 
SELECT
    m.string_value              AS ressort,
    COUNT(*)                    AS chunks,
    COUNT(DISTINCT a.string_value) AS artikel
FROM embedding_metadata m
JOIN embedding_metadata a ON m.id = a.id AND a.key = 'article_id'
WHERE m.key = 'category'
GROUP BY m.string_value
ORDER BY chunks DESC;

-- ARTIKEL SUCHEN
SELECT
    MAX(CASE WHEN m.key = 'title'           THEN m.string_value END)     AS title,
    MAX(CASE WHEN m.key = 'chunk_index'     THEN m.int_value    END)     AS chunk_nr,
    MAX(CASE WHEN m.key = 'published_date'  THEN m.string_value END)     AS datum,
    MAX(CASE WHEN m.key = 'chroma:document' THEN m.string_value END)     AS chunk_text
FROM embeddings e
JOIN embedding_metadata id_m ON e.id = id_m.id AND id_m.key = 'article_id'
LEFT JOIN embedding_metadata m ON e.id = m.id
WHERE id_m.string_value = '336541061'   -- ← article_id hier ändern
GROUP BY e.id
ORDER BY MAX(CASE WHEN m.key = 'chunk_index' THEN m.int_value END);

-- VOLLTEXT-SUCHE IN CHUNK-TEXTEN 
SELECT
    MAX(CASE WHEN m.key = 'article_id'      THEN m.string_value END)     AS article_id,
    MAX(CASE WHEN m.key = 'title'           THEN m.string_value END)     AS title,
    MAX(CASE WHEN m.key = 'category'        THEN m.string_value END)     AS ressort,
    MAX(CASE WHEN m.key = 'published_date'  THEN m.string_value END)     AS datum,
    SUBSTR(MAX(CASE WHEN m.key = 'chroma:document' THEN m.string_value END), 1, 200) AS text_vorschau
FROM embeddings e
JOIN embedding_metadata doc ON e.id = doc.id AND doc.key = 'chroma:document'
LEFT JOIN embedding_metadata m ON e.id = m.id
WHERE doc.string_value LIKE '%Negativzins%'  -- ← Suchbegriff hier ändern
GROUP BY e.id
LIMIT 20;

-- AUTOREN-STATISTIK
SELECT
    m.string_value              AS autor,
    COUNT(DISTINCT a.string_value) AS artikel,
    COUNT(*)                    AS chunks
FROM embedding_metadata m
JOIN embedding_metadata a ON m.id = a.id AND a.key = 'article_id'
WHERE m.key = 'author' AND m.string_value != ''
GROUP BY m.string_value
ORDER BY artikel DESC
LIMIT 20;

-- ARTIKEL PRO TAG
SELECT
    m.string_value              AS datum,
    COUNT(DISTINCT a.string_value) AS artikel,
    COUNT(*)                    AS chunks
FROM embedding_metadata m
JOIN embedding_metadata a ON m.id = a.id AND a.key = 'article_id'
WHERE m.key = 'published_date'
GROUP BY m.string_value
ORDER BY datum DESC
LIMIT 31;

-- GROUND-TRUTH CHECK
SELECT
    id_m.string_value           AS article_id,
    COUNT(*)                    AS chunks_vorhanden,
    MAX(CASE WHEN m.key = 'title'          THEN m.string_value END) AS title,
    MAX(CASE WHEN m.key = 'published_date' THEN m.string_value END) AS datum
FROM embedding_metadata id_m
LEFT JOIN embedding_metadata m ON id_m.id = m.id
WHERE id_m.key = 'article_id'
  AND id_m.string_value IN (
      '336541061', '336531094', '336520888', '336536063',
      '336553040', '296024981', '336544085'
  )
GROUP BY id_m.string_value
ORDER BY id_m.string_value;
