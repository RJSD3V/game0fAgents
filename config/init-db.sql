CREATE DATABASE IF NOT EXISTS symbiosis;

CREATE TABLE IF NOT EXISTS symbiosis.epoch_telemetry (
    epoch          UInt32,
    timestamp      DateTime64(3),
    alive_count    UInt32,
    total_cells    UInt32,
    density        Float32,
    births         Int32,
    deaths         Int32,
    ai_decision    String DEFAULT '',
    ai_reasoning   String DEFAULT ''
) ENGINE = MergeTree()
ORDER BY (epoch, timestamp);
