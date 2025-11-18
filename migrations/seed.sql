-- Seed data for MedCheck D1 Database

-- Insert demo organization
INSERT INTO organizations (
    name, slug, contact_email, institution_type, country, city,
    is_active, plan, max_users, trial_ends_at
) VALUES (
    'MedCheck Demo',
    'medcheck-demo',
    'admin@medcheck.com',
    'hospital',
    'Mexico',
    'Monterrey',
    1,
    'free',
    5,
    datetime('now', '+30 days')
);

-- Insert super admin user
-- Password: Admin123! (bcrypt hash)
INSERT INTO users (
    email, username, hashed_password, full_name,
    is_active, is_admin, is_super_admin, organization_id
) VALUES (
    'admin@medcheck.com',
    'admin',
    '$2a$10$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIJU6fz5jm',
    'Super Administrador',
    1,
    1,
    1,
    1
);

-- Verify
SELECT 'Organizations:', COUNT(*) FROM organizations;
SELECT 'Users:', COUNT(*) FROM users;
SELECT 'Super Admins:', COUNT(*) FROM users WHERE is_super_admin = 1;
