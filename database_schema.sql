-- ============================================
-- SQL Server Database Schema for CV Parser
-- ============================================

-- Create CVs table (main table)
CREATE TABLE CVs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NULL,
    full_name NVARCHAR(200),
    email NVARCHAR(200),
    phone NVARCHAR(50),
    location NVARCHAR(200),
    summary NVARCHAR(MAX),
    skills NVARCHAR(MAX),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Create Education table
CREATE TABLE Education (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cv_id INT NOT NULL,
    degree NVARCHAR(200),
    field NVARCHAR(200),
    institution NVARCHAR(300),
    year NVARCHAR(50),
    FOREIGN KEY (cv_id) REFERENCES CVs(id) ON DELETE CASCADE
);

-- Create Experience table
CREATE TABLE Experience (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cv_id INT NOT NULL,
    job_title NVARCHAR(200),
    company NVARCHAR(300),
    start_date NVARCHAR(50),
    end_date NVARCHAR(50),
    description NVARCHAR(MAX),
    FOREIGN KEY (cv_id) REFERENCES CVs(id) ON DELETE CASCADE
);

-- Create Certifications table
CREATE TABLE Certifications (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cv_id INT NOT NULL,
    certification NVARCHAR(300),
    FOREIGN KEY (cv_id) REFERENCES CVs(id) ON DELETE CASCADE
);

-- Create Languages table
CREATE TABLE Languages (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cv_id INT NOT NULL,
    language NVARCHAR(100),
    FOREIGN KEY (cv_id) REFERENCES CVs(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IX_CVs_user_id ON CVs(user_id);
CREATE INDEX IX_CVs_email ON CVs(email);
CREATE INDEX IX_CVs_created_at ON CVs(created_at);
CREATE INDEX IX_Education_cv_id ON Education(cv_id);
CREATE INDEX IX_Experience_cv_id ON Experience(cv_id);

-- Create a view for easy CV retrieval with all related data
CREATE VIEW vw_CVDetails AS
SELECT 
    c.id,
    c.user_id,
    c.full_name,
    c.email,
    c.phone,
    c.location,
    c.summary,
    c.skills,
    c.created_at,
    (SELECT 
        degree,
        field,
        institution,
        year
     FROM Education e 
     WHERE e.cv_id = c.id
     FOR JSON PATH) as education_json,
    (SELECT 
        job_title,
        company,
        start_date,
        end_date,
        description
     FROM Experience ex 
     WHERE ex.cv_id = c.id
     FOR JSON PATH) as experience_json
FROM CVs c;
