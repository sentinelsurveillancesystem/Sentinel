-- ============================================================
--  Sentinel AI — identity schema (fresh build)
--  WARNING: line 1 destroys all existing data in this schema.
--  Run with:  psql -U postgres -p 7000 -d sentinel_db -f schema.sql
-- ============================================================

DROP SCHEMA IF EXISTS identity CASCADE;

CREATE SCHEMA identity;


-- ---------- users ----------

CREATE TABLE identity.users (
    user_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    username      VARCHAR(32)  NOT NULL,
    full_name     VARCHAR(50)  NOT NULL,
    branch        VARCHAR(100) NOT NULL,
    roll_num      VARCHAR(20)  NOT NULL,
    age           SMALLINT     NOT NULL,
    email         VARCHAR(255) NOT NULL,
    phone         VARCHAR(20)  NOT NULL,

    -- Self-service registration always sets 'member' (enforced in
    -- main.py, not client input). 'admin' accounts are provisioned
    -- out-of-band with create_admin.py.
    role          VARCHAR(10)  NOT NULL DEFAULT 'member',

    -- argon2id hashes are ~97 chars and the length varies with
    -- parameters. TEXT avoids silent truncation on a bad VARCHAR(n).
    password_hash TEXT         NOT NULL,

    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT users_username_key UNIQUE (username),
    CONSTRAINT users_email_key    UNIQUE (email),
    CONSTRAINT users_roll_num_key UNIQUE (roll_num),

    CONSTRAINT users_age_range    CHECK (age BETWEEN 13 AND 120),
    CONSTRAINT users_email_lower  CHECK (email = lower(email)),
    CONSTRAINT users_phone_format CHECK (phone ~ '^\+?[1-9][0-9]{7,14}$'),
    CONSTRAINT users_role_valid   CHECK (role IN ('admin', 'member'))
);


-- ---------- keep updated_at honest ----------

CREATE FUNCTION identity.touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_touch_updated_at
    BEFORE UPDATE ON identity.users
    FOR EACH ROW
    EXECUTE FUNCTION identity.touch_updated_at();


-- ---------- login lookup ----------
-- username/email/roll_num already have indexes via UNIQUE.
-- This one only helps the "list active users" query.

CREATE INDEX users_active_created_idx
    ON identity.users (created_at DESC)
    WHERE is_active;