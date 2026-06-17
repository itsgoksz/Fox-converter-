DROP TABLE IF EXISTS `cart_item`;

CREATE TABLE `cart_item` (
  `cart_id` int(11) NOT NULL AUTO_INCREMENT,
  `item_idesc` varchar(50) NOT NULL,
  `item_tgno` varchar(50) NOT NULL,
  `item_qty` varchar(10) NOT NULL,
  `item_date` datetime NOT NULL,
  `mobile` varchar(15) NOT NULL,
  `item_tpre` varchar(50) NOT NULL,
  `item_gwt` varchar(50) NOT NULL,
  `item_order` varchar(10) NOT NULL DEFAULT '0',
  `item_design` varchar(150) NOT NULL,
  `remarks` varchar(150) NOT NULL,
  `salemrp` varchar(20) DEFAULT NULL,
  `wt` varchar(50) DEFAULT NULL,
  `tsno` int(11) DEFAULT NULL,
  `stamp` varchar(60) DEFAULT NULL,
  `branchid` int(6) DEFAULT NULL,
  `quality` varchar(40) DEFAULT NULL,
  `rlid` int(11) DEFAULT NULL,
  PRIMARY KEY (`cart_id`),
  KEY `idxrlid` (`mobile`,`rlid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `cart_item` */

/*Table structure for table `companydetail` */

DROP TABLE IF EXISTS `companydetail`;

CREATE TABLE `companydetail` (
  `comid` int(11) NOT NULL AUTO_INCREMENT,
  `comname` varchar(50) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `email` varchar(30) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `head1` varchar(100) DEFAULT NULL,
  `contact1` varchar(40) DEFAULT NULL,
  `head2` varchar(100) DEFAULT NULL,
  `contact2` varchar(40) DEFAULT NULL,
  `head3` varchar(100) DEFAULT NULL,
  `contact3` varchar(40) DEFAULT NULL,
  `head4` varchar(100) DEFAULT NULL,
  `contact4` varchar(40) DEFAULT NULL,
  `address1` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`comid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `companydetail` */

/*Table structure for table `config` */

DROP TABLE IF EXISTS `config`;

CREATE TABLE `config` (
  `qty` tinyint(1) DEFAULT NULL,
  `rgap` int(6) DEFAULT NULL,
  `chqty` tinyint(1) DEFAULT NULL,
  `sorder` tinyint(1) DEFAULT NULL,
  `status` tinyint(1) DEFAULT '0',
  `orderdelete` tinyint(2) DEFAULT NULL,
  `profiledisplay` tinyint(2) DEFAULT NULL,
  `orderprefix` varchar(50) DEFAULT NULL,
  `ordertype` tinyint(2) DEFAULT NULL,
  `tagging` tinyint(1) DEFAULT NULL,
  `orderby` varchar(20) DEFAULT NULL,
  `interested` tinyint(4) DEFAULT NULL,
  `tagverification` varchar(20) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Data for the table `config` */

insert  into `config`(`qty`,`rgap`,`chqty`,`sorder`,`status`,`orderdelete`,`profiledisplay`,`orderprefix`,`ordertype`,`tagging`,`orderby`,`interested`,`tagverification`) values (1,1,0,0,0,1,1,'ROD',2,1,'vtgno',0,'rfid');

/*Table structure for table `my_cart` */

DROP TABLE IF EXISTS `my_cart`;

CREATE TABLE `my_cart` (
  `cart_id` int(11) NOT NULL AUTO_INCREMENT,
  `item_idesc` varchar(50) DEFAULT NULL,
  `item_tgno` varchar(50) DEFAULT NULL,
  `item_qty` varchar(10) DEFAULT NULL,
  `item_date` datetime DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `item_tpre` varchar(50) DEFAULT NULL,
  `item_gwt` varchar(50) DEFAULT NULL,
  `item_design` varchar(50) DEFAULT NULL,
  `remarks` varchar(150) DEFAULT NULL,
  `size` varchar(20) DEFAULT NULL,
  `duedate` date DEFAULT NULL,
  `color` int(11) DEFAULT '0',
  `stones` int(11) DEFAULT '0',
  `mina` int(11) DEFAULT '0',
  `status` varchar(50) DEFAULT '0',
  `karigarid` varchar(20) DEFAULT NULL,
  `codate` date DEFAULT NULL,
  `oremarks` varchar(250) DEFAULT NULL,
  `rejectmsg` varchar(250) DEFAULT NULL,
  `deliverdate` date DEFAULT NULL,
  `salemrp` varchar(20) DEFAULT NULL,
  `itemwt` varchar(100) DEFAULT NULL,
  `orderno` varchar(100) DEFAULT NULL,
  `tsno` int(11) DEFAULT NULL,
  `vodno` tinyint(2) DEFAULT NULL,
  `prefix` varchar(50) DEFAULT NULL,
  `stamp` varchar(60) DEFAULT NULL,
  `branchid` int(6) DEFAULT NULL,
  `quality` varchar(40) DEFAULT NULL,
  `rlid` int(11) DEFAULT NULL,
  `delivered` tinyint(2) DEFAULT NULL,
  `cpid` int(10) DEFAULT NULL,
  PRIMARY KEY (`cart_id`),
  KEY `idxrlid` (`status`,`orderno`,`rlid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `my_cart` */

/*Table structure for table `pstock` */

DROP TABLE IF EXISTS `pstock`;

CREATE TABLE `pstock` (
  `pitemid` int(11) NOT NULL AUTO_INCREMENT,
  `idesc` varchar(100) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`pitemid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `pstock` */

/*Table structure for table `setdesign` */

DROP TABLE IF EXISTS `setdesign`;

CREATE TABLE `setdesign` (
  `sdid` int(11) NOT NULL AUTO_INCREMENT,
  `itemname` varchar(255) DEFAULT NULL,
  `srno` int(11) DEFAULT NULL,
  `caption` varchar(255) DEFAULT NULL,
  `selected` tinyint(4) DEFAULT '0',
  `filtercheck` tinyint(4) DEFAULT '0',
  `filtercaption` varchar(255) DEFAULT NULL,
  `filtersrno` tinyint(4) DEFAULT NULL,
  `filter` tinyint(1) DEFAULT '0',
  `xyz` varchar(500) DEFAULT NULL,
  `disadditem` char(1) DEFAULT NULL,
  PRIMARY KEY (`sdid`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8;

/*Data for the table `setdesign` */

insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (1,'idesc',1,'Item',0,0,'Item',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (2,'tgno',2,'Tag No',1,0,'Tag No',0,1,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (3,'vtgno',0,'vtgno',0,0,'vtgno',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (4,'tpre',0,'tpre',0,0,'tpre',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (5,'remarks',0,'Remark',0,0,'remarks',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (6,'tdate',0,'tdate',0,0,'tdate',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (7,'gwt',5,'Gross Wt',1,0,'Gross Wt',0,1,'3d','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (8,'lesswt',6,'Less Wt',0,0,'Less Wt',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (9,'wt',7,'Net Wt',1,0,'Net Wt',0,1,'3d','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (10,'sdiawt',8,'Dia Wt',0,0,'Dia Wt',0,1,'2d','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (11,'sstnwt',9,'Stn Wt',0,0,'Stn Wt',0,1,'2d','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (12,'goldwt',0,'Gold Wt',0,0,'Gold Wt',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (13,'silwt',0,'silwt',0,0,'silwt',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (14,'platwt',0,'platwt',0,0,'platwt',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (15,'othwt',0,'othwt',0,0,'othwt',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (16,'slbr',0,'Lbr./Gm',0,0,'slbr',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (17,'slbr2',0,'slbr2',0,0,'slbr2',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (18,'slbr3',0,'slbr3',0,0,'slbr3',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (19,'status',0,'status',0,0,'status',0,0,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (20,'stunch',0,'stunch',0,0,'stunch',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (21,'swstg',0,'swstg',0,0,'swstg',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (22,'sbeeds',0,'sbeeds',0,0,'sbeeds',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (23,'sothers',0,'sothers',0,0,'sothers',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (24,'othrem',0,'othrem',0,0,'Remark',0,1,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (25,'design',0,'Design No',0,0,'Design No',0,1,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (26,'karigar',0,'karigar',0,0,'karigar',0,0,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (27,'mrate',0,'mrate',0,0,'mrate',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (28,'gwt1',0,'gwt1',0,0,'gwt1',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (29,'gwt2',0,'gwt2',0,0,'gwt2',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (30,'stamp',3,'Stamp',1,0,'Stamp',0,1,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (31,'size',0,'size',0,0,'size',0,0,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (32,'quality',0,'quality',0,0,'Quality',0,1,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (33,'color',0,'color',0,0,'color',0,0,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (34,'clarity',0,'clarity',0,0,'clarity',0,0,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (35,'site',0,'site',0,0,'site',0,0,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (36,'linktgno',0,'linktgno',0,0,'linktgno',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (37,'diapc',0,'diapc',0,0,'diapc',0,0,'n','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (38,'stnpc',0,'stnpc',0,0,'stnpc',0,0,'n','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (39,'mrp1',0,'mrp1',0,0,'mrp1',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (40,'mrp2',0,'mrp2',0,0,'mrp2',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (41,'sdamt',11,'D Amt',0,0,'sdamt',0,0,'2d','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (42,'ssamt',12,'S Amt',0,0,'ssamt',0,0,'2d','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (43,'slamt',13,'L Amt',0,0,'slamt',0,0,'2d','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (44,'smamt',10,'M Amt',0,0,'smamt',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (45,'scamt',0,'scamt',0,0,'scamt',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (46,'mrp',0,'mrp',0,0,'mrp',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (47,'hm',0,'hm',0,0,'hm',0,0,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (48,'certno',0,'certno',0,0,'certno',0,0,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (49,'spolish',0,'spolish',0,0,'spolish',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (50,'spolishwt',0,'spolishwt',0,0,'spolishwt',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (51,'pc',4,'Pc',0,0,'pc',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (52,'salemrp',14,'MRP',0,0,'salemrp',0,0,'2d','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (53,'diawt1',0,'diawt1',0,0,'diawt1',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (54,'diawt2',0,'diawt2',0,0,'diawt2',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (55,'stnwt1',0,'stnwt1',0,0,'stnwt1',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (56,'stnwt2',0,'stnwt2',0,0,'stnwt2',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (57,'lakhwt',0,'lakhwt',0,0,'lakhwt',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (58,'shape',0,'shape',0,0,'shape',0,0,'s','N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (59,'itname',0,'itname',0,0,'itname',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (60,'category',0,'category',0,0,'category',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (61,'gcode',0,'gcode',0,0,'gcode',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (62,'tsno',0,'tsno',0,0,'tsno',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (63,'designid',0,'designid',0,0,'designid',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (64,'pname',0,'pname',0,0,'pname',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (65,'branch',0,'branch',0,0,'branch',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (66,'tgmastid',0,'tgmastid',0,0,'tgmastid',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (67,'diacut',0,'diacut',0,0,'diacut',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (68,'diapol',0,'diapol',0,0,'diapol',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (69,'diasymm',0,'diasymm',0,0,'diasymm',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (70,'pdis',0,'pdis',0,0,'pdis',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (71,'cindex',0,'cindex',0,0,'cindex',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (72,'tgimage',0,'tgimage',0,0,'tgimage',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (73,'tgimgfile',0,'tgimgfile',0,0,'tgimgfile',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (74,'tpimgfile',0,'tpimgfile',0,0,'tpimgfile',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (75,'wt1',0,'wt1',0,0,'wt1',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (76,'wt2',0,'wt2',0,0,'wt2',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (77,'gst',0,'gst',0,0,'gst',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (78,'billamt',0,'billamt',0,0,'billamt',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (79,'mno',0,'mno',0,0,'mno',0,0,NULL,'N');
insert  into `setdesign`(`sdid`,`itemname`,`srno`,`caption`,`selected`,`filtercheck`,`filtercaption`,`filtersrno`,`filter`,`xyz`,`disadditem`) values (80,'min_stock',0,'min_stock',0,0,'min_stock',0,0,NULL,'N');

/*Table structure for table `studd` */

DROP TABLE IF EXISTS `studd`;

CREATE TABLE `studd` (
  `stid` int(11) NOT NULL AUTO_INCREMENT,
  `fieldname` varchar(200) DEFAULT NULL,
  `caption` varchar(200) DEFAULT NULL,
  `srno` int(10) DEFAULT NULL,
  `width` int(10) DEFAULT '0',
  PRIMARY KEY (`stid`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4;

/*Data for the table `studd` */

insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (1,'tsno','TSNO',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (2,'idesc','Item Name',1,500);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (3,'remarks','Remarks',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (4,'stamp','Stamp',2,200);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (5,'wt','Wt',4,250);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (6,'pc','Pc',3,150);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (7,'unit','Unit',5,200);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (8,'sprice','Rate',6,300);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (9,'rateunit','Unit',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (10,'part','Part',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (11,'color','Color',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (12,'clarity','Clarity',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (13,'shape','Shape',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (14,'size','Size',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (15,'batch','Batch',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (16,'stunch','Remarks',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (17,'slbr','Stamp',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (18,'svalue','Amount',8,300);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (19,'swstg','Pc',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (20,'id','Unit',0,0);
insert  into `studd`(`stid`,`fieldname`,`caption`,`srno`,`width`) values (21,'branch','SPrice',0,0);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
