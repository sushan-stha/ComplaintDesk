-- ComplaintDesk - Database Schema
-- For Nepali College System
-- MySQL version

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',  -- student | admin
    department VARCHAR(255),
    semester INT,
    college VARCHAR(255) DEFAULT 'Tribhuvan University',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,           -- Academic | Hostel | Transport | Infrastructure | Administration | Other
    priority VARCHAR(20) NOT NULL,           -- Low | Medium | High | Critical
    sentiment VARCHAR(20) NOT NULL,          -- Positive | Neutral | Negative | Very Negative
    sentiment_score FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'Pending',    -- Pending | In Review | Resolved | Rejected
    assigned_to VARCHAR(255),
    admin_response TEXT,
    is_anonymous TINYINT(1) DEFAULT 0,
    upvotes INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS complaint_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT NOT NULL,
    tag VARCHAR(100) NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    performed_by VARCHAR(255) NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS upvotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_vote (complaint_id, user_id)
) ENGINE=InnoDB;
