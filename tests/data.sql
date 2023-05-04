INSERT INTO user (username, password)
VALUES
    ('test', 'pbkdf2:sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08'),
    ('other', 'pbkdf2:sha256:7e4fa2eb8c7ac089739d5defc4489fad68a100d92082ca35c6b40a4524821f87')

INSERT INTO post (title, body, author_id, created)
VALUES
('test title', 'test' || x'0a' || 'body', 1, '2023-05-05 00:00:00');
