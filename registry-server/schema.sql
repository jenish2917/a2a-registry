-- A2A Registry Database Schema

-- Create the registry entries table
CREATE TABLE IF NOT EXISTS registry_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    agent_card JSONB NOT NULL,
    owner VARCHAR(255) NOT NULL,
    tags TEXT[] DEFAULT '{}',
    verified BOOLEAN DEFAULT FALSE,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Indexes for common queries
    CONSTRAINT valid_agent_card CHECK (agent_card ? 'name' AND agent_card ? 'endpoint')
);

-- Create indexes
CREATE INDEX idx_agent_id ON registry_entries(agent_id);
CREATE INDEX idx_owner ON registry_entries(owner);
CREATE INDEX idx_tags ON registry_entries USING GIN(tags);
CREATE INDEX idx_registered_at ON registry_entries(registered_at DESC);
CREATE INDEX idx_last_updated ON registry_entries(last_updated DESC);
CREATE INDEX idx_verified ON registry_entries(verified);

-- GIN index for JSONB searches
CREATE INDEX idx_agent_card_gin ON registry_entries USING GIN(agent_card);

-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_email ON users(email);
CREATE INDEX idx_api_key ON users(api_key);

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    agent_id VARCHAR(255),
    action VARCHAR(50) NOT NULL,
    details JSONB,
    ip_address INET,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_agent_id ON audit_logs(agent_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);

-- Function to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update last_updated
CREATE TRIGGER update_registry_entries_last_updated
    BEFORE UPDATE ON registry_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated_column();
