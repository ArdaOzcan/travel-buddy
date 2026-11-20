CREATE TABLE Country (
    country_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    iso2 CHAR(2) NOT NULL UNIQUE
);

CREATE TABLE Destination (
    destination_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_id INT NOT NULL REFERENCES Country(country_id) ON DELETE RESTRICT,
    city VARCHAR(100) NOT NULL,
    region VARCHAR(100)
);

CREATE TABLE Trip (
    trip_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    destination_id INT NOT NULL REFERENCES Destination(destination_id) ON DELETE RESTRICT,
    traveler_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    travel_style VARCHAR(20) NOT NULL DEFAULT 'budget'
        CHECK (travel_style IN ('budget', 'backpacking', 'comfort', 'luxury', 'adventure')),
    CONSTRAINT chk_trip_dates CHECK (end_date >= start_date)
);

-- Seed sample data
INSERT INTO Country (name, iso2) VALUES
    ('Turkey', 'TR'),
    ('Poland', 'PL'),
    ('Hungary', 'HU');

INSERT INTO Destination (country_id, city, region) VALUES
    (1, 'Istanbul', 'Marmara'),
    (2, 'Krakow', 'Lesser Poland'),
    (3, 'Budapest', 'Central Hungary');

INSERT INTO Trip (destination_id, traveler_name, start_date, end_date, travel_style) VALUES
    (1, 'Arda', '2026-12-10', '2026-12-15', 'backpacking'),
    (2, 'Mert', '2026-12-12', '2026-12-18', 'budget');
