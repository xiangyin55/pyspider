# Host: 106.12.108.36:3000  (Version 5.7.25-0ubuntu0.16.04.2)
# Date: 2019-02-21 10:38:43
# Generator: MySQL-Front 6.1  (Build 1.26)


#
# Structure for table "post"
#

DROP TABLE IF EXISTS `post`;
CREATE TABLE `post` (
  `id` int(11) NOT NULL DEFAULT '0',
  `name` varchar(50) NOT NULL DEFAULT '',
  `parent` int(11) DEFAULT NULL,
  `alias` varchar(50) DEFAULT NULL,
  `level` int(11) DEFAULT '0',
  `code` varchar(10) DEFAULT NULL,
  `post` varchar(10) DEFAULT NULL,
  `full` varchar(255) DEFAULT NULL,
  `lng` double DEFAULT NULL,
  `lat` double DEFAULT NULL,
  `pinyin` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
