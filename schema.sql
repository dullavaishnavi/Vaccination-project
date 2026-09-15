PRAGMA foreign_keys = ON;

CREATE TABLE countries (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    who_region TEXT
);

CREATE TABLE coverage (
    code TEXT NOT NULL,
    year INTEGER NOT NULL,
    antigen TEXT,
    description TEXT,
    coverage_category TEXT,
    target_population REAL,
    doses REAL,
    coverage REAL,
    FOREIGN KEY(code) REFERENCES countries(code)
);

CREATE TABLE incidence_rate (
    code TEXT NOT NULL,
    year INTEGER NOT NULL,
    disease TEXT,
    disease_description TEXT,
    denominator TEXT,
    incidence_rate REAL,
    FOREIGN KEY(code) REFERENCES countries(code)
);

CREATE TABLE reported_cases (
    code TEXT NOT NULL,
    year INTEGER NOT NULL,
    disease TEXT,
    disease_description TEXT,
    cases REAL,
    FOREIGN KEY(code) REFERENCES countries(code)
);

CREATE TABLE vaccine_introduction (
    code TEXT NOT NULL,
    year INTEGER NOT NULL,
    description TEXT,
    intro INTEGER,
    FOREIGN KEY(code) REFERENCES countries(code)
);

CREATE TABLE vaccine_schedule (
    code TEXT NOT NULL,
    year INTEGER NOT NULL,
    vaccine_code TEXT,
    vaccine_description TEXT,
    schedule_rounds INTEGER,
    target_pop_description TEXT,
    geoarea TEXT,
    age_administered TEXT,
    source_comment TEXT,
    FOREIGN KEY(code) REFERENCES countries(code)
);

CREATE INDEX idx_coverage_code_year ON coverage(code, year);
CREATE INDEX idx_incidence_code_year ON incidence_rate(code, year);
CREATE INDEX idx_cases_code_year ON reported_cases(code, year);
