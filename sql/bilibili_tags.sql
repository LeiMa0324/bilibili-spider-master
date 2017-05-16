CREATE TABLE `bilibili_tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tagid` int(11) DEFAULT NULL,
  `tagname` varchar(45) DEFAULT NULL,
  `tagtype` int(11) DEFAULT NULL,
  `tagcontent` text,
  `tagctime` varchar(45) DEFAULT NULL,
  `taguse` int(11) DEFAULT NULL,
  `tagatten` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;
