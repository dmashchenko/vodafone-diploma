-- -----------------------------------------------------
-- Schema traffic
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `traffic` DEFAULT CHARACTER SET utf8 ;
USE `traffic` ;

-- -----------------------------------------------------
-- Table `traffic`.`traffic_prediction`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `traffic`.`traffic_prediction` ;

CREATE TABLE IF NOT EXISTS `traffic`.`traffic_prediction` (
  `idtraffic_prediction` INT NOT NULL AUTO_INCREMENT,
  `value` FLOAT(9,6) UNSIGNED NOT NULL,
  `lon` FLOAT(9,6) NOT NULL,
  `lat` FLOAT(9,6) NOT NULL,
  `month` DATE NOT NULL,
  PRIMARY KEY (`idtraffic_prediction`));

INSERT INTO `traffic_prediction` (`value`, `lon`, `lat`, `month`) VALUES ('0.001858', '30.083', '50.149', '2020-07-01');
INSERT INTO `traffic_prediction` (`value`, `lon`, `lat`, `month`) VALUES ('0.203970', '31.26', '47.71', '2020-07-01');
INSERT INTO `traffic_prediction` (`value`, `lon`, `lat`, `month`) VALUES ('21.978195', '29.349', '48.864', '2020-07-01');
