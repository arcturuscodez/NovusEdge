GRANT ALL PRIVILEGES ON SCHEMA public TO "your_user";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "your_user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO "your_user";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "your_user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO "your_user";