-- Create the table
CREATE TABLE IF NOT EXISTS public.server_user_log
(
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(250) COLLATE pg_catalog."default",
    server_name VARCHAR(250) COLLATE pg_catalog."default",
    server_password VARCHAR(250) COLLATE pg_catalog."default",
    access_granted BOOLEAN,
    time_log TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
)
TABLESPACE pg_default;

-- Alter the table owner
ALTER TABLE IF EXISTS public.server_user_log
    OWNER TO postgres;

-- Revoke all permissions from chandru_s
REVOKE ALL ON TABLE public.server_user_log FROM chandru_s;

-- Grant all permissions to chandru0538
GRANT ALL ON TABLE public.server_user_log TO chandru0538;

-- Grant specific permissions to chandru_s
GRANT UPDATE, DELETE, INSERT, SELECT ON TABLE public.server_user_log TO chandru_s;

-- Grant all permissions to postgres
GRANT ALL ON TABLE public.server_user_log TO postgres;
