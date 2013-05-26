-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               5.5.24 - MySQL Community Server (GPL)
-- Server OS:                    Linux
-- HeidiSQL version:             7.0.0.4053
-- Date/time:                    2012-06-29 08:20:43
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET FOREIGN_KEY_CHECKS=0 */;

-- Dumping database structure for muchview
CREATE DATABASE IF NOT EXISTS `muchview` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `muchview`;


-- Dumping structure for table muchview.agents
CREATE TABLE IF NOT EXISTS `agents` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `source_name` varchar(50) NOT NULL,
  `capture_start_time` datetime NOT NULL,
  `capture_end_time` datetime NOT NULL,
  `capture_items_num` int(10) NOT NULL DEFAULT '0',
  `capture_images_num` int(10) NOT NULL DEFAULT '0',
  `capture_items_error_num` int(10) DEFAULT '0',
  `language` varchar(10) NOT NULL,
  `category_by_this_agent` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`),
  KEY `source_name` (`source_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='agent sites';

-- Data exporting was unselected.


-- Dumping structure for table muchview.agents_categories
CREATE TABLE IF NOT EXISTS `agents_categories` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `source_name` varchar(50) NOT NULL,
  `category_name` varchar(50) NOT NULL,
  `category_url` text NOT NULL,
  `capture_datetime` datetime NOT NULL,
  `capture_done` varchar(10) NOT NULL DEFAULT 'N/A',
  PRIMARY KEY (`id`),
  KEY `id` (`id`),
  KEY `source_name` (`source_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='agents categories';

-- Data exporting was unselected.


-- Dumping structure for table muchview.agents_items
CREATE TABLE IF NOT EXISTS `agents_items` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `source_name` varchar(50) NOT NULL,
  `category_name` varchar(50) NOT NULL,
  `category_url` text NOT NULL,
  `items_name` text NOT NULL,
  `items_url` text NOT NULL,
  `capture_datetime` datetime NOT NULL,
  `capture_done` varchar(10) NOT NULL DEFAULT 'N/A',
  PRIMARY KEY (`id`),
  KEY `id` (`id`),
  KEY `source_name` (`source_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='agents items';

-- Data exporting was unselected.


-- Dumping structure for table muchview.agents_items_attrs
CREATE TABLE IF NOT EXISTS `agents_items_attrs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `source_name` varchar(50) NOT NULL,
  `items_name` text NOT NULL,
  `items_url` text NOT NULL,
  `logo` text NOT NULL,
  `title` text NOT NULL,
  `desc` text NOT NULL,
  `offical_url` text NOT NULL,
  `cates` text NOT NULL,
  `rating` text NOT NULL,
  `price` text NOT NULL,
  `capture_datetime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`),
  KEY `source_name` (`source_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='agents items attribute';

-- Data exporting was unselected.


-- Dumping structure for table muchview.agents_items_images
CREATE TABLE IF NOT EXISTS `agents_items_images` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `source_name` varchar(50) NOT NULL,
  `items_url` text NOT NULL,
  `images_key` text NOT NULL,
  `images_url` text NOT NULL,
  `capture_datetime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='agents items images';

-- Data exporting was unselected.


-- Dumping structure for table muchview.agents_items_spec
CREATE TABLE IF NOT EXISTS `agents_items_spec` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `source_name` varchar(50) NOT NULL,
  `items_url` text NOT NULL,
  `spec_key` text NOT NULL,
  `spec_url` text NOT NULL,
  `capture_datetime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='agents items specfication';

-- Data exporting was unselected.


-- Dumping structure for table muchview.agents_items_user_reviews
CREATE TABLE IF NOT EXISTS `agents_items_user_reviews` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `source_name` varchar(50) NOT NULL,
  `items_url` text NOT NULL,
  `author` text NOT NULL,
  `author_comment` text NOT NULL,
  `rating` text,
  `review_datetime` text,
  `capture_datetime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='User review for agent items';

-- Data exporting was unselected.


-- Dumping structure for table muchview.agents_items_user_reviews_pros
CREATE TABLE IF NOT EXISTS `agents_items_user_reviews_pros` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `source_name` varchar(50) NOT NULL,
  `items_url` text NOT NULL,
  `pros_key` text,
  `pros_value` text,
  PRIMARY KEY (`id`),
  KEY `id` (`id`),
  KEY `source_name` (`source_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='agents_items_user_reviews_pros';

-- Data exporting was unselected.
/*!40014 SET FOREIGN_KEY_CHECKS=1 */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
