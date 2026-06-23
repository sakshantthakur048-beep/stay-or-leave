-- ============================================================
-- Stay or Leave — Sample Seed Data
-- Run AFTER schema.sql: psql -U <user> -d stay_or_leave -f seed.sql
-- ============================================================

-- Admin user. Password is "Admin@12345" (bcrypt hash below).
-- Change this password immediately in any real deployment.
INSERT INTO users (id, name, email, password_hash, role, is_verified)
VALUES (
    uuid_generate_v4(),
    'Site Admin',
    'admin@stayorleave.com',
    '$2b$12$3eYsX5pZ/sCm1Vp5oqLgs.Vw1l0c2nHnq3jvJrUO1cQHEv8qFh9Cq', -- Admin@12345
    'admin',
    TRUE
);

-- Sample regular user. Password is "Password@123".
INSERT INTO users (id, name, email, password_hash, role, is_verified)
VALUES (
    uuid_generate_v4(),
    'Jordan Patel',
    'jordan@example.com',
    '$2b$12$tH1sIsAFakeButValidLengthHashForSeedPurposesOnly0000',
    'user',
    TRUE
);

-- ------------------------------------------------------------
-- PLACES
-- ------------------------------------------------------------
INSERT INTO places (id, name, type, slug, country_code, image_url, description) VALUES
(uuid_generate_v4(), 'Canada',       'country', 'canada',        'CA', '/images/places/canada.jpg',       'A North American country known for healthcare and quality of life.'),
(uuid_generate_v4(), 'Germany',      'country', 'germany',       'DE', '/images/places/germany.jpg',      'A European country with strong industry and social benefits.'),
(uuid_generate_v4(), 'Australia',    'country', 'australia',     'AU', '/images/places/australia.jpg',    'An island country known for climate and outdoor lifestyle.'),
(uuid_generate_v4(), 'Singapore',    'country', 'singapore',     'SG', '/images/places/singapore.jpg',    'A city-state known for safety and economic opportunity.'),
(uuid_generate_v4(), 'United States','country', 'united-states', 'US', '/images/places/usa.jpg',          'A large country with diverse economic opportunity.'),
(uuid_generate_v4(), 'Toronto',      'city',    'toronto',       'CA', '/images/places/toronto.jpg',      'Canada''s largest city, a major financial hub.'),
(uuid_generate_v4(), 'Berlin',       'city',    'berlin',        'DE', '/images/places/berlin.jpg',       'Germany''s capital, known for culture and startups.');

-- ------------------------------------------------------------
-- PLACE METRICS
-- Pull each place's id by slug to attach metrics.
-- ------------------------------------------------------------
DO $$
DECLARE
    canada_id     UUID := (SELECT id FROM places WHERE slug = 'canada');
    germany_id    UUID := (SELECT id FROM places WHERE slug = 'germany');
    australia_id  UUID := (SELECT id FROM places WHERE slug = 'australia');
    singapore_id  UUID := (SELECT id FROM places WHERE slug = 'singapore');
    usa_id        UUID := (SELECT id FROM places WHERE slug = 'united-states');
BEGIN
    INSERT INTO place_metrics (place_id, metric_key, value, unit) VALUES
    -- Canada
    (canada_id, 'cost_of_living',   72.5, 'index_0_100'),
    (canada_id, 'avg_salary',       55000, 'USD'),
    (canada_id, 'tax_rate',         33, 'percent'),
    (canada_id, 'safety_index',     75, 'index_0_100'),
    (canada_id, 'healthcare_index', 82, 'index_0_100'),
    (canada_id, 'internet_speed',   120, 'mbps'),
    (canada_id, 'happiness_index',  7.0, 'index_0_10'),
    (canada_id, 'pollution_index',  28, 'index_0_100'),
    (canada_id, 'gdp_per_capita',   52000, 'USD'),

    -- Germany
    (germany_id, 'cost_of_living',   68.0, 'index_0_100'),
    (germany_id, 'avg_salary',       50000, 'USD'),
    (germany_id, 'tax_rate',         42, 'percent'),
    (germany_id, 'safety_index',     78, 'index_0_100'),
    (germany_id, 'healthcare_index', 84, 'index_0_100'),
    (germany_id, 'internet_speed',   95, 'mbps'),
    (germany_id, 'happiness_index',  7.1, 'index_0_10'),
    (germany_id, 'pollution_index',  32, 'index_0_100'),
    (germany_id, 'gdp_per_capita',   48000, 'USD'),

    -- Australia
    (australia_id, 'cost_of_living',   75.0, 'index_0_100'),
    (australia_id, 'avg_salary',       58000, 'USD'),
    (australia_id, 'tax_rate',         32, 'percent'),
    (australia_id, 'safety_index',     76, 'index_0_100'),
    (australia_id, 'healthcare_index', 80, 'index_0_100'),
    (australia_id, 'internet_speed',   55, 'mbps'),
    (australia_id, 'happiness_index',  7.2, 'index_0_10'),
    (australia_id, 'pollution_index',  22, 'index_0_100'),
    (australia_id, 'gdp_per_capita',   54000, 'USD'),

    -- Singapore
    (singapore_id, 'cost_of_living',   85.0, 'index_0_100'),
    (singapore_id, 'avg_salary',       62000, 'USD'),
    (singapore_id, 'tax_rate',         20, 'percent'),
    (singapore_id, 'safety_index',     93, 'index_0_100'),
    (singapore_id, 'healthcare_index', 88, 'index_0_100'),
    (singapore_id, 'internet_speed',   210, 'mbps'),
    (singapore_id, 'happiness_index',  6.6, 'index_0_10'),
    (singapore_id, 'pollution_index',  40, 'index_0_100'),
    (singapore_id, 'gdp_per_capita',   72000, 'USD'),

    -- United States
    (usa_id, 'cost_of_living',   78.0, 'index_0_100'),
    (usa_id, 'avg_salary',       65000, 'USD'),
    (usa_id, 'tax_rate',         30, 'percent'),
    (usa_id, 'safety_index',     63, 'index_0_100'),
    (usa_id, 'healthcare_index', 60, 'index_0_100'),
    (usa_id, 'internet_speed',   140, 'mbps'),
    (usa_id, 'happiness_index',  6.4, 'index_0_10'),
    (usa_id, 'pollution_index',  45, 'index_0_100'),
    (usa_id, 'gdp_per_capita',   76000, 'USD');
END $$;

-- ------------------------------------------------------------
-- SAMPLE COMPARISON
-- ------------------------------------------------------------
DO $$
DECLARE
    canada_id  UUID := (SELECT id FROM places WHERE slug = 'canada');
    germany_id UUID := (SELECT id FROM places WHERE slug = 'germany');
    jordan_id  UUID := (SELECT id FROM users WHERE email = 'jordan@example.com');
BEGIN
    INSERT INTO comparisons (user_id, place_a_id, place_b_id, recommendation, summary, is_featured)
    VALUES (
        jordan_id,
        canada_id,
        germany_id,
        'A',
        'Canada edges ahead on healthcare and safety, while Germany offers a lower cost of living. For long-term settlement with family, Canada is the stronger overall pick; for affordability and EU access, Germany is competitive.',
        TRUE
    );
END $$;

-- ------------------------------------------------------------
-- SAMPLE REVIEW
-- ------------------------------------------------------------
DO $$
DECLARE
    canada_id UUID := (SELECT id FROM places WHERE slug = 'canada');
    jordan_id UUID := (SELECT id FROM users WHERE email = 'jordan@example.com');
BEGIN
    INSERT INTO reviews (user_id, place_id, title, body, rating)
    VALUES (
        jordan_id,
        canada_id,
        'Moved here two years ago — no regrets',
        'The healthcare system alone was worth the move. Winters are tough but the work-life balance more than makes up for it.',
        5
    );
END $$;
