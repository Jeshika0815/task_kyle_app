CREATE DATABASE task_agent_db;

--USE `task_agent_db`;


CREATE TABLE users (                    --ユーザーテーブル制作
    name TEXT,
    password_hash TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO  users(name, password_hash, email)
VALUES (
        '前田',
        'youkoso',
        'example@gmail.com'

);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    comment TEXT,
    limit_date DATE,
    priority TEXT CHECK (priority IN ('高', '中', '小')),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO tasks (title, comment, limit_date, priority, completed)
VALUES (

    'DjangoのAPI掲示板を完成させる',         -- title
    '先生に教えてもらう',                     -- comment
    '2026-06-30',                           -- limit_date (期限日)
    '高',                                   -- priority ('高', '中', '小')
    FALSE                                   -- completed (まだ未完了)
);
INSERT INTO tasks ( title, priority) --空白はNULL
VALUES (
 
    'スーパーで牛乳を買う',                  
    '中'                                    
);
CREATE TABLE task_name_history (
    id SERIAL PRIMARY KEY,
    update_task TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO task_name_history (
    
    update_task
)
VALUES (

    'xammpの勉強会'
);
