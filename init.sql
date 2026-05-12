CREATE TABLE IF NOT EXISTS users (
    user_tg_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority SMALLINT DEFAULT 1 CHECK (priority IN (1, 2, 3)),
    deadline TIMESTAMP WITH TIME ZONE,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_tasks_user_id
        FOREIGN KEY (user_id)
        REFERENCES users (user_tg_id)
        ON DELETE CASCADE
);

