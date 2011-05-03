SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `springfiles`
--

-- --------------------------------------------------------

--
-- Table structure for table `upqueue`
--

CREATE TABLE IF NOT EXISTS `upqueue` (
  `jobid` int(11) NOT NULL AUTO_INCREMENT,
  `jobname` varchar(255) NOT NULL COMMENT 'job module name',
  `state` varchar(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL COMMENT 'new/running/done',
  `pickle_blob` blob NOT NULL COMMENT 'obj state saved with pickle',
  `result` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'UpqJob.result[''success'']',
  `result_msg` varchar(255) NOT NULL DEFAULT 'New' COMMENT 'UpqJob.result[msg]',
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'job create time',
  `start_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT 'job start time',
  `end_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT 'job end time',
  PRIMARY KEY (`jobid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=100 ;
