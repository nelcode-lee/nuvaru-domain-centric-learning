-- Database initialization script for Nuvaru platform
-- This script sets up the initial database structure

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS nuvaru_db;

-- Use the database
\c nuvaru_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create initial admin user (password: admin123)
-- This will be handled by the application, but we can set up the structure
-- The actual user creation will be done through the API

-- Create indexes for better performance
-- These will be created when the tables are created by SQLAlchemy

-- Set up initial configuration
-- Any initial data or configuration can be added here



