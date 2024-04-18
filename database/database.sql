-- MySQL 

--
-- Table structure for table `tzdb_timezones`
--

DROP TABLE IF EXISTS `tzdb_timezones`;

CREATE TABLE `tzdb_timezones` (
  `country_code` varchar(2) NOT NULL,
  `country_name` varchar(100) NOT NULL,
  `zone_name` varchar(100) NOT NULL,
  `gmt_offset` int DEFAULT NULL,
  `import_date` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`zone_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- Table structure for table `tzdb_zone_details`
--

DROP TABLE IF EXISTS `tzdb_zone_details`;

CREATE TABLE `tzdb_zone_details` (
  `country_code` varchar(2) NOT NULL,
  `country_name` varchar(100) NOT NULL,
  `zone_name` varchar(100) NOT NULL,
  `gmt_offset` int NOT NULL,
  `dst` int NOT NULL,
  `zone_start` bigint NOT NULL,
  `zone_end` bigint NOT NULL,
  `import_date` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`zone_name`,`zone_start`,`zone_end`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- Table structure for table `tzdb_error_log`
--

DROP TABLE IF EXISTS `tzdb_error_log`;

CREATE TABLE `tzdb_error_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `error_date` timestamp NOT NULL,
  `error_message` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1256 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- Table structure for table `staging_tzdb_zone_details`
--

DROP TABLE IF EXISTS `staging_tzdb_zone_details`;

CREATE TABLE `staging_tzdb_zone_details` (
  `country_code` varchar(2) NOT NULL,
  `country_name` varchar(100) NOT NULL,
  `zone_name` varchar(100) NOT NULL,
  `gmt_offset` int NOT NULL,
  `dst` int NOT NULL,
  `zone_start` bigint NOT NULL,
  `zone_end` bigint NOT NULL,
  `import_date` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`zone_name`,`zone_start`,`zone_end`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;