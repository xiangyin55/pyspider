
DROP TABLE IF EXISTS `scenic_area`;
CREATE TABLE `scenic_area` (
  `id` int(11) NOT NULL DEFAULT '0',
  `parent` int(11) NOT NULL DEFAULT '0' COMMENT '父级ID',
  `name` varchar(50) NOT NULL DEFAULT '' COMMENT '名称',
  `alias` varchar(255) DEFAULT NULL COMMENT '别名',
  `type` varchar(255) DEFAULT NULL COMMENT '类型（公园、动物园、植物园、游乐园、博物馆、水族馆、海滨浴场、文物古迹、教堂、风景区 、旅游景点、公园广场、城市广场、风景名胜、世界遗产、国家级景点、省级景点、纪念馆、寺庙道观、回教寺、海滩、观景点）',
  `tag` text COMMENT '头衔、标签',
  `relateid` json DEFAULT NULL COMMENT '关联ID',
  `summary` varchar(255) DEFAULT NULL COMMENT '简介',
  `location` json DEFAULT NULL COMMENT '经纬度坐标',
  `areaid` int(11) NOT NULL DEFAULT '0' COMMENT '行政区ID',
  `contact` json DEFAULT NULL COMMENT '联系方式',
  `level` int(1) NOT NULL DEFAULT '2' COMMENT '级别（1景区;2景点;3内部景点)',
  
  
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='景点';
