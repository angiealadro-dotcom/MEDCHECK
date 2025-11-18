-- Script para inicializar datos en Cloudflare D1
-- Ejecutar DESPUÉS de aplicar 001_initial_schema.sql

-- 1. Crear organización demo
INSERT INTO organizations (
    name,
    slug,
    contact_email,
    contact_phone,
    institution_type,
    country,
    city,
    is_active,
    plan,
    max_users,
    trial_ends_at,
    created_at,
    updated_at
) VALUES (
    'MedCheck Demo',
    'medcheck-demo',
    'admin@medcheck.com',
    '',
    'hospital',
    'Mexico',
    'Monterrey',
    1,
    'free',
    5,
    datetime('now', '+30 days'),
    datetime('now'),
    datetime('now')
);

-- 2. Crear usuario super admin
-- Password: Admin123! (cambiar después del primer login)
-- Hash bcrypt de "Admin123!"
INSERT INTO users (
    email,
    username,
    hashed_password,
    full_name,
    is_active,
    is_admin,
    is_super_admin,
    organization_id
) VALUES (
    'admin@medcheck.com',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIJU6fz5jm',
    'Super Administrador',
    1,
    1,
    1,
    1
);

-- Verificar inserción
SELECT 'Organizations created:' as status, COUNT(*) as count FROM organizations;
SELECT 'Users created:' as status, COUNT(*) as count FROM users;
SELECT 'Super admins:' as status, COUNT(*) as count FROM users WHERE is_super_admin = 1;
