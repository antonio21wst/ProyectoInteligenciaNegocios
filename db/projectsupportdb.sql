-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3307
-- Generation Time: Oct 28, 2025 at 05:12 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `projectsupportdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `dim_address`
--

CREATE TABLE `dim_address` (
  `idAddress` int(11) NOT NULL,
  `street` varchar(200) DEFAULT NULL,
  `postalCode` varchar(20) DEFAULT NULL,
  `idCity` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dim_area`
--

CREATE TABLE `dim_area` (
  `idArea` int(11) NOT NULL,
  `nameArea` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dim_city`
--

CREATE TABLE `dim_city` (
  `idCity` int(11) NOT NULL,
  `nameCity` varchar(100) NOT NULL,
  `idState` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dim_client`
--

CREATE TABLE `dim_client` (
  `idClient` int(11) NOT NULL,
  `nameClient` varchar(120) NOT NULL,
  `idAddress` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dim_country`
--

CREATE TABLE `dim_country` (
  `idCountry` int(11) NOT NULL,
  `nameCountry` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dim_employee`
--

CREATE TABLE `dim_employee` (
  `idEmployee` int(11) NOT NULL,
  `nameEmployee` varchar(120) NOT NULL,
  `idRol` int(11) DEFAULT NULL,
  `idExperience` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dim_experience`
--

CREATE TABLE `dim_experience` (
  `idExperience` int(11) NOT NULL,
  `experience` enum('Junior','Mid','Senior','Lead') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dim_rol`
--

CREATE TABLE `dim_rol` (
  `idRol` int(11) NOT NULL,
  `rol` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dim_state`
--

CREATE TABLE `dim_state` (
  `idState` int(11) NOT NULL,
  `nameState` varchar(100) NOT NULL,
  `idCountry` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dim_team`
--

CREATE TABLE `dim_team` (
  `idTeam` int(11) NOT NULL,
  `nameTeam` varchar(100) DEFAULT NULL,
  `integrantes` int(11) DEFAULT NULL,
  `idEmployee` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dim_time`
--

CREATE TABLE `dim_time` (
  `idTime` int(11) NOT NULL,
  `date` date NOT NULL,
  `year` int(11) DEFAULT NULL,
  `month` int(11) DEFAULT NULL,
  `day` int(11) DEFAULT NULL,
  `quarter` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `fact_project`
--

CREATE TABLE `fact_project` (
  `idFact_Project` int(11) NOT NULL,
  `idClient` int(11) DEFAULT NULL,
  `idArea` int(11) DEFAULT NULL,
  `idTeam` int(11) DEFAULT NULL,
  `idEmployee` int(11) DEFAULT NULL,
  `idFechaInicio` int(11) DEFAULT NULL,
  `idFechaFin` int(11) DEFAULT NULL,
  `idTime` int(11) DEFAULT NULL,
  `budget` decimal(12,2) DEFAULT NULL,
  `cost` decimal(12,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `dim_address`
--
ALTER TABLE `dim_address`
  ADD PRIMARY KEY (`idAddress`),
  ADD KEY `idCity` (`idCity`);

--
-- Indexes for table `dim_area`
--
ALTER TABLE `dim_area`
  ADD PRIMARY KEY (`idArea`);

--
-- Indexes for table `dim_city`
--
ALTER TABLE `dim_city`
  ADD PRIMARY KEY (`idCity`),
  ADD KEY `idState` (`idState`);

--
-- Indexes for table `dim_client`
--
ALTER TABLE `dim_client`
  ADD PRIMARY KEY (`idClient`),
  ADD KEY `idAddress` (`idAddress`);

--
-- Indexes for table `dim_country`
--
ALTER TABLE `dim_country`
  ADD PRIMARY KEY (`idCountry`);

--
-- Indexes for table `dim_employee`
--
ALTER TABLE `dim_employee`
  ADD PRIMARY KEY (`idEmployee`),
  ADD KEY `idRol` (`idRol`),
  ADD KEY `idExperience` (`idExperience`);

--
-- Indexes for table `dim_experience`
--
ALTER TABLE `dim_experience`
  ADD PRIMARY KEY (`idExperience`);

--
-- Indexes for table `dim_rol`
--
ALTER TABLE `dim_rol`
  ADD PRIMARY KEY (`idRol`);

--
-- Indexes for table `dim_state`
--
ALTER TABLE `dim_state`
  ADD PRIMARY KEY (`idState`),
  ADD KEY `idCountry` (`idCountry`);

--
-- Indexes for table `dim_team`
--
ALTER TABLE `dim_team`
  ADD PRIMARY KEY (`idTeam`),
  ADD KEY `idEmployee` (`idEmployee`);

--
-- Indexes for table `dim_time`
--
ALTER TABLE `dim_time`
  ADD PRIMARY KEY (`idTime`);

--
-- Indexes for table `fact_project`
--
ALTER TABLE `fact_project`
  ADD PRIMARY KEY (`idFact_Project`),
  ADD KEY `idClient` (`idClient`),
  ADD KEY `idArea` (`idArea`),
  ADD KEY `idTeam` (`idTeam`),
  ADD KEY `idEmployee` (`idEmployee`),
  ADD KEY `idFechaInicio` (`idFechaInicio`),
  ADD KEY `idFechaFin` (`idFechaFin`),
  ADD KEY `idTime` (`idTime`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `dim_address`
--
ALTER TABLE `dim_address`
  MODIFY `idAddress` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dim_area`
--
ALTER TABLE `dim_area`
  MODIFY `idArea` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dim_city`
--
ALTER TABLE `dim_city`
  MODIFY `idCity` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dim_client`
--
ALTER TABLE `dim_client`
  MODIFY `idClient` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dim_country`
--
ALTER TABLE `dim_country`
  MODIFY `idCountry` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dim_employee`
--
ALTER TABLE `dim_employee`
  MODIFY `idEmployee` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dim_experience`
--
ALTER TABLE `dim_experience`
  MODIFY `idExperience` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dim_rol`
--
ALTER TABLE `dim_rol`
  MODIFY `idRol` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dim_state`
--
ALTER TABLE `dim_state`
  MODIFY `idState` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dim_team`
--
ALTER TABLE `dim_team`
  MODIFY `idTeam` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dim_time`
--
ALTER TABLE `dim_time`
  MODIFY `idTime` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `fact_project`
--
ALTER TABLE `fact_project`
  MODIFY `idFact_Project` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `dim_address`
--
ALTER TABLE `dim_address`
  ADD CONSTRAINT `dim_address_ibfk_1` FOREIGN KEY (`idCity`) REFERENCES `dim_city` (`idCity`);

--
-- Constraints for table `dim_city`
--
ALTER TABLE `dim_city`
  ADD CONSTRAINT `dim_city_ibfk_1` FOREIGN KEY (`idState`) REFERENCES `dim_state` (`idState`);

--
-- Constraints for table `dim_client`
--
ALTER TABLE `dim_client`
  ADD CONSTRAINT `dim_client_ibfk_1` FOREIGN KEY (`idAddress`) REFERENCES `dim_address` (`idAddress`);

--
-- Constraints for table `dim_employee`
--
ALTER TABLE `dim_employee`
  ADD CONSTRAINT `dim_employee_ibfk_1` FOREIGN KEY (`idRol`) REFERENCES `dim_rol` (`idRol`),
  ADD CONSTRAINT `dim_employee_ibfk_2` FOREIGN KEY (`idExperience`) REFERENCES `dim_experience` (`idExperience`);

--
-- Constraints for table `dim_state`
--
ALTER TABLE `dim_state`
  ADD CONSTRAINT `dim_state_ibfk_1` FOREIGN KEY (`idCountry`) REFERENCES `dim_country` (`idCountry`);

--
-- Constraints for table `dim_team`
--
ALTER TABLE `dim_team`
  ADD CONSTRAINT `dim_team_ibfk_1` FOREIGN KEY (`idEmployee`) REFERENCES `dim_employee` (`idEmployee`);

--
-- Constraints for table `fact_project`
--
ALTER TABLE `fact_project`
  ADD CONSTRAINT `fact_project_ibfk_1` FOREIGN KEY (`idClient`) REFERENCES `dim_client` (`idClient`),
  ADD CONSTRAINT `fact_project_ibfk_2` FOREIGN KEY (`idArea`) REFERENCES `dim_area` (`idArea`),
  ADD CONSTRAINT `fact_project_ibfk_3` FOREIGN KEY (`idTeam`) REFERENCES `dim_team` (`idTeam`),
  ADD CONSTRAINT `fact_project_ibfk_4` FOREIGN KEY (`idEmployee`) REFERENCES `dim_employee` (`idEmployee`),
  ADD CONSTRAINT `fact_project_ibfk_5` FOREIGN KEY (`idFechaInicio`) REFERENCES `dim_time` (`idTime`),
  ADD CONSTRAINT `fact_project_ibfk_6` FOREIGN KEY (`idFechaFin`) REFERENCES `dim_time` (`idTime`),
  ADD CONSTRAINT `fact_project_ibfk_7` FOREIGN KEY (`idTime`) REFERENCES `dim_time` (`idTime`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
