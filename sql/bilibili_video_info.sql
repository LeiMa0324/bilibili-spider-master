CREATE TABLE `bilibili_video_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `aid` int(11) DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `copyright` varchar(150) DEFAULT NULL,
  `created` varchar(45) DEFAULT NULL,
  `favourites` int(11) DEFAULT NULL,
  `length` varchar(11) DEFAULT NULL,
  `mid` int(11) DEFAULT NULL,
  `play` int(11) DEFAULT NULL,
  `review` int(11) DEFAULT NULL,
  `title` varchar(150) DEFAULT NULL,
  `typeid` int(11) DEFAULT NULL,
  `video_review` int(11) DEFAULT NULL,
  `tags` text,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;
