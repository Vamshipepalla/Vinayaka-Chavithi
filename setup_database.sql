-- ============================================================
-- Vinayaka Chavithi App — MySQL Database Setup Script
-- Run this ONCE before starting the application.
-- ============================================================

-- 1. Create the database
CREATE DATABASE IF NOT EXISTS vinayaka_chavithi_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 2. (Optional) Create a dedicated user for the app
-- Replace 'appuser' and 'StrongPassword@123' with your own values.
-- Skip this block if you're using the root user directly.
CREATE USER IF NOT EXISTS 'appuser'@'localhost' IDENTIFIED BY 'StrongPassword@123';
GRANT ALL PRIVILEGES ON vinayaka_chavithi_db.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;

-- 3. Select the database (Flask-SQLAlchemy creates tables automatically,
--    but having this here helps when inspecting manually.)
USE vinayaka_chavithi_db;

-- All tables are created automatically by Flask-SQLAlchemy when you run
-- the application for the first time (db.create_all() in app.py).
-- You do NOT need to create individual tables manually.

SELECT 'Database setup complete!' AS status;
