/*
* xiaoqy 2018/11/2
*/

#删除之前的数据库
use mysql;
DELETE FROM mysql.user WHERE user='Tentacles' AND host='%';
DELETE FROM mysql.user WHERE user='Tentacles' AND host='localhost';
drop database if  exists Tentacles;
FLUSH PRIVILEGES;

create database Tentacles DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

use Tentacles;
#创建用户名密码

CREATE USER 'Tentacles'@'localhost' IDENTIFIED BY 'de80a2074c3e60479ead0e64e5b6bc325cdb02b';
CREATE USER 'Tentacles'@'%' IDENTIFIED BY 'de80a2074c3e60479ead0e64e5b6bc325cdb02b';

REVOKE ALL PRIVILEGES ON *.* FROM 'Tentacles'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'Tentacles'@'%';

REVOKE ALL PRIVILEGES ON *.* FROM 'Tentacles'@'localhost';
GRANT ALL PRIVILEGES ON *.* TO 'Tentacles'@'localhost';

FLUSH PRIVILEGES;


use Tentacles;



/**
用户信息表
 */
CREATE TABLE  IF NOT EXISTS USERS(

  `id` varchar(50) not null, #会员ID
  `userName` VARCHAR(25) NOT NULL, #用户名
  `passwd` varchar(50) NOT NULL,#密码
  `phone` VARCHAR(11), #手机号
  `status` INT(4),#状态
  `permissions` int(8),#权限
  `headImage` VARCHAR(500), #头像
  `created_at` REAL NOT NULL,
  `recommendid` varchar(50) not null, #推荐人id
  `recommendCode` varchar(6) not null, #推荐码
  `depth` int not null,#深度

  unique key `idx_userName` (`userName`),
  key `idx_phone` (`phone`),
  key `idx_recommendCode` (`recommendCode`),
  primary key (`id`)
);


#功能列表
CREATE TABLE  IF NOT EXISTS FUNCTION(

  `id` varchar(50), #功能id
  `name` VARCHAR(25), #功能名
  `fatherid` varchar(50),#功能父id
  `icon` VARCHAR(20),#功能icon
  `api` VARCHAR(50), #功能api
  `permissions` int(8),#角色

  primary key (`id`)
);

#权限列表

CREATE TABLE  IF NOT EXISTS PERMISSIONS(

  `id` varchar(50), #权限id
  `name` VARCHAR(25), #权限名
  `permissions` int(8),#角色

  primary key (`id`)
);


#app功能配置列表

CREATE TABLE  IF NOT EXISTS APPFUNVCTION(

  `id` varchar(50), #id
  `name` VARCHAR(25), #功能名
  primary key (`id`)
);

#app功能配置列表

CREATE TABLE  IF NOT EXISTS APPWAY(

  `id` varchar(50), #id
  `name` VARCHAR(25), #路由名
  `appfuncid` varchar(50), #功能类型
  `url` VARCHAR(125), #跳转路径
  `icon` VARCHAR(500), #图片
  `soft` INT, #排序

  primary key (`id`)
);




