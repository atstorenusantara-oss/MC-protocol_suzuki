-- Database export for PLC Monitoring
-- Alamat PLC B0 - B7FF ke MySQL

CREATE DATABASE IF NOT EXISTS `plc_db`;
USE `plc_db`;

-- ---------------------------------------------------------
-- Struktur dari tabel `plc_b_relay`
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS `plc_b_relay` (
  `address` varchar(10) NOT NULL COMMENT 'Alamat PLC (Format Hex: B0 - B7FF)',
  `value` tinyint(1) DEFAULT '0' COMMENT 'Nilai Bit (0 atau 1)',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Waktu pembaharuan terakhir',
  PRIMARY KEY (`address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- Catatan:
-- Jika Anda ingin menyimpan data secara historis (log), 
-- gunakan struktur tabel di bawah ini sebagai alternatif:
-- ---------------------------------------------------------

/*
CREATE TABLE IF NOT EXISTS `plc_b_relay_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `address` varchar(10) NOT NULL,
  `value` tinyint(1) NOT NULL,
  `recorded_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_address` (`address`),
  KEY `idx_time` (`recorded_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
*/
