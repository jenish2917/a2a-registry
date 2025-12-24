-- Vector extension and embeddings table for semantic search
-- This file is loaded after schema.sql

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create embeddings table
CREATE TABLE IF NOT EXISTS agent_embeddings (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    embedding vector(384),
    text_content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES registry_entries(agent_id) ON DELETE CASCADE
);

-- Create index for similarity search (using IVFFlat for speed)
CREATE INDEX IF NOT EXISTS idx_agent_embeddings_vector
ON agent_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Trigger for auto-updating timestamp
CREATE OR REPLACE FUNCTION update_embeddings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agent_embeddings_timestamp
    BEFORE UPDATE ON agent_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_embeddings_timestamp();
