-- Create table for storing personal best lap times
CREATE TABLE IF NOT EXISTS pb (
    track TEXT NOT NULL,
    car TEXT NOT NULL,
    laptime_ms INTEGER NOT NULL,
    date TEXT NOT NULL
);

-- Ensure track/car combination remains unique
CREATE UNIQUE INDEX IF NOT EXISTS idx_pb_track_car
    ON pb(track, car);
