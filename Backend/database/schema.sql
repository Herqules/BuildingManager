-- Organizations Table
CREATE TABLE organizations (
    organization_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    size INT NOT NULL,
    address TEXT NOT NULL,
    gps_coordinates VARCHAR(100),
    attributes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staff Table
CREATE TABLE staff (
    staff_id SERIAL PRIMARY KEY,
    organization_id INT REFERENCES organizations(organization_id),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    office_location TEXT,
    is_on_job BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    organization_id INT REFERENCES organizations(organization_id),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    identifier VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Locations Table
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    organization_id INT REFERENCES organizations(organization_id),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    gps_coordinates VARCHAR(100),
    floor_number INT,
    room_number VARCHAR(50),
    address TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Tickets Table
CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    location_id INT REFERENCES locations(location_id),
    description TEXT NOT NULL,
    status VARCHAR(50) CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled')) DEFAULT 'open',
    urgency_score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Incident Severity Table
CREATE TABLE incident_severity (
    severity_id SERIAL PRIMARY KEY,
    level VARCHAR(50) NOT NULL,
    response_time INT NOT NULL,
    description TEXT,
    color_code VARCHAR(7),
    priority_level INT
);

-- Emergency Tickets Table
CREATE TABLE emergency_tickets (
    ticket_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id INT REFERENCES organizations(organization_id) ON DELETE CASCADE,
    user_input_location TEXT NOT NULL,
    matched_location TEXT,
    location_type VARCHAR(50),
    location_details TEXT,
    description VARCHAR(400) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')) DEFAULT 'pending',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_name VARCHAR(100) NOT NULL,
    user_contact VARCHAR(100) NOT NULL,
    identifier VARCHAR(100),
    severity_id INT REFERENCES incident_severity(severity_id),
    assigned_staff_id INT REFERENCES staff(staff_id) ON DELETE SET NULL,
    estimated_response_time INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Staff Skills Table
CREATE TABLE staff_skills (
    skill_id SERIAL PRIMARY KEY,
    staff_id INT REFERENCES staff(staff_id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    skill_level VARCHAR(20) NOT NULL,
    CONSTRAINT unique_staff_skill UNIQUE (staff_id, category, subcategory)
);

-- Ticket Logs Table
CREATE TABLE ticket_logs (
    log_id SERIAL PRIMARY KEY,
    ticket_id INT REFERENCES emergency_tickets(ticket_id) ON DELETE CASCADE,
    action VARCHAR(50),
    performed_by INT REFERENCES staff(staff_id),
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced Ticket Logs Table (for both regular and emergency tickets)
CREATE TABLE enhanced_ticket_logs (
    log_id SERIAL PRIMARY KEY,
    ticket_type VARCHAR(20) NOT NULL CHECK (ticket_type IN ('regular', 'emergency')),
    ticket_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    changes JSONB,  -- Stores the actual changes made
    performed_by INT REFERENCES staff(staff_id),
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Add constraints to handle both ticket types
    CONSTRAINT valid_ticket_reference CHECK (
        (ticket_type = 'regular' AND ticket_id IN (SELECT ticket_id FROM tickets))
        OR 
        (ticket_type = 'emergency' AND ticket_id IN (SELECT ticket_id FROM emergency_tickets))
    )
);

-- Create all indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_urgency ON tickets(urgency_score);
CREATE INDEX idx_emergency_tickets_status ON emergency_tickets(status);
CREATE INDEX idx_emergency_tickets_date ON emergency_tickets(created_date);

-- Create indexes for better query performance
CREATE INDEX idx_ticket_logs_ticket_type_id ON enhanced_ticket_logs(ticket_type, ticket_id);
CREATE INDEX idx_ticket_logs_timestamp ON enhanced_ticket_logs(log_timestamp);
