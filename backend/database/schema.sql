-- ============================================================
-- Stay or Leave — PostgreSQL Schema
-- Run with: psql -U <user> -d stay_or_leave -f schema.sql
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------
-- USERS
-- ------------------------------------------------------------
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    profile_picture VARCHAR(500),
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_email ON users(email);

-- ------------------------------------------------------------
-- EMAIL VERIFICATION / PASSWORD RESET TOKENS
-- ------------------------------------------------------------
CREATE TABLE auth_tokens (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) NOT NULL UNIQUE,
    token_type  VARCHAR(30) NOT NULL CHECK (token_type IN ('email_verify', 'password_reset')),
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_auth_tokens_token ON auth_tokens(token);
CREATE INDEX idx_auth_tokens_user ON auth_tokens(user_id);

-- ------------------------------------------------------------
-- PLACES (Country / City / Company / College — unified entity)
-- ------------------------------------------------------------
CREATE TABLE places (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(150) NOT NULL,
    type            VARCHAR(20) NOT NULL CHECK (type IN ('country', 'city', 'company', 'college')),
    slug            VARCHAR(170) NOT NULL UNIQUE,
    country_code    VARCHAR(2),
    image_url       VARCHAR(500),
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_places_type ON places(type);
CREATE INDEX idx_places_name ON places(name);

-- ------------------------------------------------------------
-- PLACE METRICS (the comparable factors — cost of living, salary, etc.)
-- One row per place per metric key, keeps the factor list extensible.
-- ------------------------------------------------------------
CREATE TABLE place_metrics (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    place_id    UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    metric_key  VARCHAR(50) NOT NULL,   -- e.g. 'cost_of_living', 'avg_salary', 'safety_index'
    value       NUMERIC(12, 2),
    unit        VARCHAR(20),            -- e.g. 'USD', 'index_0_100', 'mbps'
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (place_id, metric_key)
);

CREATE INDEX idx_place_metrics_place ON place_metrics(place_id);
CREATE INDEX idx_place_metrics_key ON place_metrics(metric_key);

-- ------------------------------------------------------------
-- COMPARISONS (a saved A vs B comparison, optionally tied to a user)
-- ------------------------------------------------------------
CREATE TABLE comparisons (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    place_a_id      UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    place_b_id      UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    recommendation  VARCHAR(10) CHECK (recommendation IN ('A', 'B', 'tie')),
    summary         TEXT,
    view_count      INTEGER NOT NULL DEFAULT 0,
    is_featured     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_comparisons_user ON comparisons(user_id);
CREATE INDEX idx_comparisons_places ON comparisons(place_a_id, place_b_id);
CREATE INDEX idx_comparisons_featured ON comparisons(is_featured);

-- ------------------------------------------------------------
-- BOOKMARKS (users saving comparisons)
-- ------------------------------------------------------------
CREATE TABLE bookmarks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    comparison_id   UUID NOT NULL REFERENCES comparisons(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, comparison_id)
);

CREATE INDEX idx_bookmarks_user ON bookmarks(user_id);

-- ------------------------------------------------------------
-- REVIEWS / EXPERIENCES (user-submitted experience about a place)
-- ------------------------------------------------------------
CREATE TABLE reviews (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    place_id        UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    title           VARCHAR(150) NOT NULL,
    body            TEXT NOT NULL,
    rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    status          VARCHAR(20) NOT NULL DEFAULT 'published'
                        CHECK (status IN ('published', 'flagged', 'removed')),
    helpful_count   INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reviews_place ON reviews(place_id);
CREATE INDEX idx_reviews_user ON reviews(user_id);
CREATE INDEX idx_reviews_status ON reviews(status);
CREATE INDEX idx_reviews_rating ON reviews(rating);

-- ------------------------------------------------------------
-- REVIEW IMAGES
-- ------------------------------------------------------------
CREATE TABLE review_images (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id   UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    image_url   VARCHAR(500) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_review_images_review ON review_images(review_id);

-- ------------------------------------------------------------
-- COMMENTS (on reviews)
-- ------------------------------------------------------------
CREATE TABLE comments (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id   UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body        VARCHAR(1000) NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'published'
                    CHECK (status IN ('published', 'flagged', 'removed')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_comments_review ON comments(review_id);
CREATE INDEX idx_comments_user ON comments(user_id);

-- ------------------------------------------------------------
-- LIKES (polymorphic-ish: likes on reviews or comments via target_type)
-- ------------------------------------------------------------
CREATE TABLE likes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_type     VARCHAR(20) NOT NULL CHECK (target_type IN ('review', 'comment')),
    target_id       UUID NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, target_type, target_id)
);

CREATE INDEX idx_likes_target ON likes(target_type, target_id);

-- ------------------------------------------------------------
-- REPORTS (flagging inappropriate content)
-- ------------------------------------------------------------
CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reporter_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_type     VARCHAR(20) NOT NULL CHECK (target_type IN ('review', 'comment')),
    target_id       UUID NOT NULL,
    reason          VARCHAR(255) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'reviewed', 'dismissed')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reports_target ON reports(target_type, target_id);
CREATE INDEX idx_reports_status ON reports(status);

-- ------------------------------------------------------------
-- CONTACT MESSAGES
-- ------------------------------------------------------------
CREATE TABLE contact_messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    subject     VARCHAR(200),
    message     TEXT NOT NULL,
    is_read     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_contact_messages_read ON contact_messages(is_read);

-- ------------------------------------------------------------
-- updated_at auto-touch trigger (reused across tables)
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_users
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER set_updated_at_places
    BEFORE UPDATE ON places
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER set_updated_at_reviews
    BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
