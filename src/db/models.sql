-- ----------------------
-- Create Performance table
-- ----------------------
CREATE TABLE IF NOT EXISTS `Performance`
(
     id int(10) NOT NULL AUTO_INCREMENT,
     hostname   varchar(50) NOT NULL,
     db_name varchar(255) NOT NULL,
     avgmicrosec int NOT NULL,
     err_count int NOT NULL,
     create_time datetime NOT NULL,
     PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------
-- Create Performance table
-- ----------------------
CREATE TABLE IF NOT EXISTS `Throughput`
(
     id int(10) NOT NULL AUTO_INCREMENT,
     hostname   varchar(50) NOT NULL,
     questions int NOT NULL,
     com_select int NOT NULL,
     writes int NOT NULL,
     create_time datetime NOT NULL,
     PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------
-- Create Connections table
-- ----------------------
CREATE TABLE IF NOT EXISTS `Connections`
(
     id int(10) NOT NULL AUTO_INCREMENT,
     hostname   varchar(50) NOT NULL,
     max_connections int NOT NULL,
     threads_connected int NOT NULL,
     threads_running int NOT NULL,
     connection_errors_internal int NOT NULL,
     aborted_connects int NOT NULL,
     connection_errors_max_connections int NOT NULL,
     create_time datetime NOT NULL,
     PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------
-- Create Innodb table
-- ----------------------
CREATE TABLE IF NOT EXISTS `Innodb`
(
     id int(10) NOT NULL AUTO_INCREMENT,
     hostname   varchar(50) NOT NULL,
     innodb_buffer_pool_pages_total int NOT NULL,
     innodb_buffer_pool_rate int NOT NULL,
     innodb_buffer_pool_read_requests int NOT NULL,
     innodb_buffer_pool_reads int NOT NULL,
     innodb_page_size int NOT NULL,
     create_time datetime NOT NULL,
     PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------
-- Create Agent table
-- ----------------------
CREATE TABLE IF NOT EXISTS `Agent`
(
     id int(10) NOT NULL AUTO_INCREMENT,
     hostname   varchar(50) NOT NULL,
     status     varchar(20) NOT NULL,
     dbs        varchar(2000) NOT NULL,
     intervel   int DEFAULT 300,
     PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;