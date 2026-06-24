-- Admin user (password: Admin@12345)
INSERT INTO users (id, name, email, password_hash, role, is_verified)
VALUES (
    gen_random_uuid(),
    'Site Admin',
    'admin@stayorleave.com',
    '$2b$12$3eYsX5pZ/sCm1Vp5oqLgs.Vw1l0c2nHnq3jvJrUO1cQHEv8qFh9Cq',
    'admin',
    TRUE
);

-- Sample regular user (password: Password@123)
INSERT INTO users (id, name, email, password_hash, role, is_verified)
VALUES (
    gen_random_uuid(),
    'Jordan Patel',
    'jordan@example.com',
    '$2b$12$tH1sIsAFakeButValidLengthHashForSeedPurposesOnly0000',
    'user',
    TRUE
);

-- Places
INSERT INTO places (id, name, type, slug, country_code, image_url, description) VALUES
(gen_random_uuid(), 'Canada',        'country', 'canada',        'CA', '/images/places/canada.jpg',       'A North American country known for healthcare and quality of life.'),
(gen_random_uuid(), 'Germany',       'country', 'germany',       'DE', '/images/places/germany.jpg',      'A European country with strong industry and social benefits.'),
(gen_random_uuid(), 'Australia',     'country', 'australia',     'AU', '/images/places/australia.jpg',    'An island country known for climate and outdoor lifestyle.'),
(gen_random_uuid(), 'Singapore',     'country', 'singapore',     'SG', '/images/places/singapore.jpg',    'A city-state known for safety and economic opportunity.'),
(gen_random_uuid(), 'United States', 'country', 'united-states', 'US', '/images/places/usa.jpg',          'A large country with diverse economic opportunity.'),
(gen_random_uuid(), 'Toronto',       'city',    'toronto',       'CA', '/images/places/toronto.jpg',      'Canada''s largest city, a major financial hub.'),
(gen_random_uuid(), 'Berlin',        'city',    'berlin',        'DE', '/images/places/berlin.jpg',       'Germany''s capital, known for culture and startups.');

-- Place metrics
INSERT INTO place_metrics (place_id, metric_key, value, unit)
SELECT p.id, 'cost_of_living',   72.5,  'index_0_100' FROM places p WHERE p.slug = 'canada' UNION ALL
SELECT p.id, 'avg_salary',       55000, 'USD'          FROM places p WHERE p.slug = 'canada' UNION ALL
SELECT p.id, 'tax_rate',         33,    'percent'      FROM places p WHERE p.slug = 'canada' UNION ALL
SELECT p.id, 'safety_index',     75,    'index_0_100'  FROM places p WHERE p.slug = 'canada' UNION ALL
SELECT p.id, 'healthcare_index', 82,    'index_0_100'  FROM places p WHERE p.slug = 'canada' UNION ALL
SELECT p.id, 'internet_speed',   120,   'mbps'         FROM places p WHERE p.slug = 'canada' UNION ALL
SELECT p.id, 'happiness_index',  7.0,   'index_0_10'   FROM places p WHERE p.slug = 'canada' UNION ALL
SELECT p.id, 'pollution_index',  28,    'index_0_100'  FROM places p WHERE p.slug = 'canada' UNION ALL
SELECT p.id, 'gdp_per_capita',   52000, 'USD'          FROM places p WHERE p.slug = 'canada' UNION ALL

SELECT p.id, 'cost_of_living',   68.0,  'index_0_100' FROM places p WHERE p.slug = 'germany' UNION ALL
SELECT p.id, 'avg_salary',       50000, 'USD'          FROM places p WHERE p.slug = 'germany' UNION ALL
SELECT p.id, 'tax_rate',         42,    'percent'      FROM places p WHERE p.slug = 'germany' UNION ALL
SELECT p.id, 'safety_index',     78,    'index_0_100'  FROM places p WHERE p.slug = 'germany' UNION ALL
SELECT p.id, 'healthcare_index', 84,    'index_0_100'  FROM places p WHERE p.slug = 'germany' UNION ALL
SELECT p.id, 'internet_speed',   95,    'mbps'         FROM places p WHERE p.slug = 'germany' UNION ALL
SELECT p.id, 'happiness_index',  7.1,   'index_0_10'   FROM places p WHERE p.slug = 'germany' UNION ALL
SELECT p.id, 'pollution_index',  32,    'index_0_100'  FROM places p WHERE p.slug = 'germany' UNION ALL
SELECT p.id, 'gdp_per_capita',   48000, 'USD'          FROM places p WHERE p.slug = 'germany' UNION ALL

SELECT p.id, 'cost_of_living',   75.0,  'index_0_100' FROM places p WHERE p.slug = 'australia' UNION ALL
SELECT p.id, 'avg_salary',       58000, 'USD'          FROM places p WHERE p.slug = 'australia' UNION ALL
SELECT p.id, 'tax_rate',         32,    'percent'      FROM places p WHERE p.slug = 'australia' UNION ALL
SELECT p.id, 'safety_index',     76,    'index_0_100'  FROM places p WHERE p.slug = 'australia' UNION ALL
SELECT p.id, 'healthcare_index', 80,    'index_0_100'  FROM places p WHERE p.slug = 'australia' UNION ALL
SELECT p.id, 'internet_speed',   55,    'mbps'         FROM places p WHERE p.slug = 'australia' UNION ALL
SELECT p.id, 'happiness_index',  7.2,   'index_0_10'   FROM places p WHERE p.slug = 'australia' UNION ALL
SELECT p.id, 'pollution_index',  22,    'index_0_100'  FROM places p WHERE p.slug = 'australia' UNION ALL
SELECT p.id, 'gdp_per_capita',   54000, 'USD'          FROM places p WHERE p.slug = 'australia' UNION ALL

SELECT p.id, 'cost_of_living',   85.0,  'index_0_100' FROM places p WHERE p.slug = 'singapore' UNION ALL
SELECT p.id, 'avg_salary',       62000, 'USD'          FROM places p WHERE p.slug = 'singapore' UNION ALL
SELECT p.id, 'tax_rate',         20,    'percent'      FROM places p WHERE p.slug = 'singapore' UNION ALL
SELECT p.id, 'safety_index',     93,    'index_0_100'  FROM places p WHERE p.slug = 'singapore' UNION ALL
SELECT p.id, 'healthcare_index', 88,    'index_0_100'  FROM places p WHERE p.slug = 'singapore' UNION ALL
SELECT p.id, 'internet_speed',   210,   'mbps'         FROM places p WHERE p.slug = 'singapore' UNION ALL
SELECT p.id, 'happiness_index',  6.6,   'index_0_10'   FROM places p WHERE p.slug = 'singapore' UNION ALL
SELECT p.id, 'pollution_index',  40,    'index_0_100'  FROM places p WHERE p.slug = 'singapore' UNION ALL
SELECT p.id, 'gdp_per_capita',   72000, 'USD'          FROM places p WHERE p.slug = 'singapore' UNION ALL

SELECT p.id, 'cost_of_living',   78.0,  'index_0_100' FROM places p WHERE p.slug = 'united-states' UNION ALL
SELECT p.id, 'avg_salary',       65000, 'USD'          FROM places p WHERE p.slug = 'united-states' UNION ALL
SELECT p.id, 'tax_rate',         30,    'percent'      FROM places p WHERE p.slug = 'united-states' UNION ALL
SELECT p.id, 'safety_index',     63,    'index_0_100'  FROM places p WHERE p.slug = 'united-states' UNION ALL
SELECT p.id, 'healthcare_index', 60,    'index_0_100'  FROM places p WHERE p.slug = 'united-states' UNION ALL
SELECT p.id, 'internet_speed',   140,   'mbps'         FROM places p WHERE p.slug = 'united-states' UNION ALL
SELECT p.id, 'happiness_index',  6.4,   'index_0_10'   FROM places p WHERE p.slug = 'united-states' UNION ALL
SELECT p.id, 'pollution_index',  45,    'index_0_100'  FROM places p WHERE p.slug = 'united-states' UNION ALL
SELECT p.id, 'gdp_per_capita',   76000, 'USD'          FROM places p WHERE p.slug = 'united-states';

-- Sample comparison: Canada vs Germany
INSERT INTO comparisons (user_id, place_a_id, place_b_id, recommendation, summary, is_featured)
SELECT
    u.id,
    pa.id,
    pb.id,
    'A',
    'Canada edges ahead on healthcare and safety, while Germany offers a lower cost of living. For long-term settlement with family, Canada is the stronger overall pick; for affordability and EU access, Germany is competitive.',
    TRUE
FROM
    users u,
    places pa,
    places pb
WHERE
    u.email = 'jordan@example.com'
    AND pa.slug = 'canada'
    AND pb.slug = 'germany';

-- Sample review
INSERT INTO reviews (user_id, place_id, title, body, rating)
SELECT
    u.id,
    p.id,
    'Moved here two years ago — no regrets',
    'The healthcare system alone was worth the move. Winters are tough but the work-life balance more than makes up for it.',
    5
FROM
    users u,
    places p
WHERE
    u.email = 'jordan@example.com'
    AND p.slug = 'canada';
