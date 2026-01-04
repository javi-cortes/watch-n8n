SELECT 'CREATE DATABASE watch_n8n'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'watch_n8n')\gexec
