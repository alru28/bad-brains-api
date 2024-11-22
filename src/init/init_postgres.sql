-- Create users table if it doesn't already exist
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant privileges to the PostgreSQL user defined in docker-compose.yml
-- Replace `postgres_user` with the actual user specified in your Docker Compose file, if different.
GRANT ALL PRIVILEGES ON TABLE users TO postgres_user;

-- Grant privileges on the sequence used for the primary key
GRANT ALL PRIVILEGES ON SEQUENCE users_id_seq TO postgres_user;