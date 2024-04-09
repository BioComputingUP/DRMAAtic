-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: mysql:3306
-- Generation Time: Apr 04, 2024 at 08:52 AM
-- Server version: 11.2.2-MariaDB-1:11.2.2+maria~ubu2204
-- PHP Version: 8.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `drmaatic`
--
CREATE DATABASE drmaatic;
USE drmaatic;
-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add group', 6, 'add_group'),
(22, 'Can change group', 6, 'change_group'),
(23, 'Can delete group', 6, 'delete_group'),
(24, 'Can view group', 6, 'view_group'),
(25, 'Can add job', 7, 'add_job'),
(26, 'Can change job', 7, 'change_job'),
(27, 'Can delete job', 7, 'delete_job'),
(28, 'Can view job', 7, 'view_job'),
(29, 'Can add queue', 8, 'add_queue'),
(30, 'Can change queue', 8, 'change_queue'),
(31, 'Can delete queue', 8, 'delete_queue'),
(32, 'Can view queue', 8, 'view_queue'),
(33, 'Can add user', 9, 'add_user'),
(34, 'Can change user', 9, 'change_user'),
(35, 'Can delete user', 9, 'delete_user'),
(36, 'Can view user', 9, 'view_user'),
(37, 'Can add token', 10, 'add_token'),
(38, 'Can change token', 10, 'change_token'),
(39, 'Can delete token', 10, 'delete_token'),
(40, 'Can view token', 10, 'view_token'),
(41, 'Can add task', 11, 'add_task'),
(42, 'Can change task', 11, 'change_task'),
(43, 'Can delete task', 11, 'delete_task'),
(44, 'Can view task', 11, 'view_task'),
(45, 'Can add parameter', 12, 'add_parameter'),
(46, 'Can change parameter', 12, 'change_parameter'),
(47, 'Can delete parameter', 12, 'delete_parameter'),
(48, 'Can view parameter', 12, 'view_parameter'),
(49, 'Can add job parameter', 13, 'add_jobparameter'),
(50, 'Can change job parameter', 13, 'change_jobparameter'),
(51, 'Can delete job parameter', 13, 'delete_jobparameter'),
(52, 'Can view job parameter', 13, 'view_jobparameter'),
(53, 'Can add admin', 14, 'add_admin'),
(54, 'Can change admin', 14, 'change_admin'),
(55, 'Can delete admin', 14, 'delete_admin'),
(56, 'Can view admin', 14, 'view_admin');

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2023-12-19 09:25:28.240583', '1', 'normal', 1, '[{\"added\": {}}]', 8, 1),
(2, '2023-12-19 09:28:13.439283', '1', 'test', 1, '[{\"added\": {}}, {\"added\": {\"name\": \"parameter\", \"object\": \"file --file\"}}]', 11, 1),
(3, '2024-04-04 08:30:33.207796', '1', 'wait_task', 2, '[{\"changed\": {\"fields\": [\"Name\", \"Command\"]}}, {\"changed\": {\"name\": \"parameter\", \"object\": \"wait_time --waitTtime\", \"fields\": [\"Name\", \"Flag\"]}}]', 11, 1);

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(14, 'drmaatic', 'admin'),
(6, 'drmaatic', 'group'),
(7, 'drmaatic', 'job'),
(13, 'drmaatic', 'jobparameter'),
(12, 'drmaatic', 'parameter'),
(8, 'drmaatic', 'queue'),
(11, 'drmaatic', 'task'),
(10, 'drmaatic', 'token'),
(9, 'drmaatic', 'user'),
(5, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2023-12-19 09:22:34.736396'),
(2, 'contenttypes', '0002_remove_content_type_name', '2023-12-19 09:22:34.757806'),
(3, 'auth', '0001_initial', '2023-12-19 09:22:34.825322'),
(4, 'auth', '0002_alter_permission_name_max_length', '2023-12-19 09:22:34.839034'),
(5, 'auth', '0003_alter_user_email_max_length', '2023-12-19 09:22:34.842134'),
(6, 'auth', '0004_alter_user_username_opts', '2023-12-19 09:22:34.844905'),
(7, 'auth', '0005_alter_user_last_login_null', '2023-12-19 09:22:34.847672'),
(8, 'auth', '0006_require_contenttypes_0002', '2023-12-19 09:22:34.848700'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2023-12-19 09:22:34.852888'),
(10, 'auth', '0008_alter_user_username_max_length', '2023-12-19 09:22:34.855524'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2023-12-19 09:22:34.858090'),
(12, 'auth', '0010_alter_group_name_max_length', '2023-12-19 09:22:34.865475'),
(13, 'auth', '0011_update_proxy_permissions', '2023-12-19 09:22:34.868946'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2023-12-19 09:22:34.871628'),
(15, 'drmaatic', '0001_initial', '2023-12-19 09:22:35.203423'),
(16, 'admin', '0001_initial', '2023-12-19 09:22:35.238183'),
(17, 'admin', '0002_logentry_remove_auto_add', '2023-12-19 09:22:35.242642'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2023-12-19 09:22:35.247966'),
(19, 'drmaatic', '0002_group_execution_token_regen_amount_and_more', '2023-12-19 09:22:35.280802'),
(20, 'drmaatic', '0003_remove_group_throttling_rate_sustained', '2023-12-19 09:22:35.290691'),
(21, 'drmaatic', '0004_rename_execution_token_regen_time_group__execution_token_regen_time', '2023-12-19 09:22:35.304344'),
(22, 'drmaatic', '0005_alter_user_group', '2023-12-19 09:22:35.358575'),
(23, 'drmaatic', '0006_alter_job_deleted', '2023-12-19 09:22:35.368093'),
(24, 'drmaatic', '0007_rename_is_output_visible_task_is_output_public', '2023-12-19 09:22:35.381323'),
(25, 'drmaatic', '0008_alter_task_queue_alter_user_group', '2023-12-19 09:22:35.413426'),
(26, 'drmaatic', '0009_alter_queue_max_cpu_alter_queue_max_mem', '2023-12-19 09:22:35.420894'),
(27, 'drmaatic', '0010_alter_job_task', '2023-12-19 09:22:35.480281'),
(28, 'drmaatic', '0011_alter_user_group', '2023-12-19 09:22:35.525722'),
(29, 'sessions', '0001_initial', '2023-12-19 09:22:35.541249'),
(30, 'drmaatic', '0011_rename_hash_token_jwt_remove_token_created_and_more', '2024-04-04 08:27:52.538043'),
(31, 'drmaatic', '0012_remove_token_user', '2024-04-04 08:27:52.556180'),
(32, 'drmaatic', '0013_rename__execution_token_regen_time_group__cpu_credit_regen_time_and_more', '2024-04-04 08:27:52.606279'),
(33, 'drmaatic', '0014_auto_20240404_1027', '2024-04-04 08:27:52.627248');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('dsm2ne76ezm8s063ch861lofzbvkmsip', '.eJxVjDsOwjAQBe_iGlk2_oaSPmew1t5dHECOFCcV4u4QKQW0b2beSyTY1pq2TkuaUFyEFqffLUN5UNsB3qHdZlnmti5TlrsiD9rlOCM9r4f7d1Ch129NBtxQ0Gb2ijx4Q2w96WhycOQQlHUBUWuNQ2QiLsVwOANHa6JCKOL9AQWyOPk:1rsIO4:gHti_EyDyF4lbWCtpYNkJRaBQIy4BZlhCL10FapWtS0', '2024-04-18 08:23:56.604525'),
('ny120bbp6pop8bycjx9fjbg4m2c4clqb', '.eJxVjDsOwjAQBe_iGlk2_oaSPmew1t5dHECOFCcV4u4QKQW0b2beSyTY1pq2TkuaUFyEFqffLUN5UNsB3qHdZlnmti5TlrsiD9rlOCM9r4f7d1Ch129NBtxQ0Gb2ijx4Q2w96WhycOQQlHUBUWuNQ2QiLsVwOANHa6JCKOL9AQWyOPk:1rFWJf:SWzfGya8YSmIn3pM9v43EhfELvlR_zo6oUFJfX29-c0', '2024-01-02 09:23:07.738675'),
('wi8gakczpmjdj8fa4mdudqx4ai6zjaex', '.eJxVjDsOwjAQBe_iGlk2_oaSPmew1t5dHECOFCcV4u4QKQW0b2beSyTY1pq2TkuaUFyEFqffLUN5UNsB3qHdZlnmti5TlrsiD9rlOCM9r4f7d1Ch129NBtxQ0Gb2ijx4Q2w96WhycOQQlHUBUWuNQ2QiLsVwOANHa6JCKOL9AQWyOPk:1rFsqk:hNcwtrm69UWNaEOCJPhNy7Qwfu5SZdZ5U-QbHMGdXFM', '2024-01-03 09:26:46.105436');

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_admin`
--

CREATE TABLE `drmaatic_admin` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `drmaatic_admin`
--

INSERT INTO `drmaatic_admin` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(1, 'pbkdf2_sha256$260000$IogQIMWuHtDbJz7igD9OVw$J2m3ok7QwjxWTdrRIhFCq0zT63CE3sTvJafmQzcu9xs=', '2024-04-04 08:23:56.603217', 1, 'admin', '', '', '', 1, 1, '2023-12-19 09:22:53.717830');

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_admin_groups`
--

CREATE TABLE `drmaatic_admin_groups` (
  `id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_admin_user_permissions`
--

CREATE TABLE `drmaatic_admin_user_permissions` (
  `id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_group`
--

CREATE TABLE `drmaatic_group` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `has_full_access` tinyint(1) NOT NULL,
  `throttling_rate_burst` varchar(30) NOT NULL,
  `cpu_credit_max_amount` int(11) NOT NULL,
  `token_renewal_time` varchar(40) NOT NULL,
  `cpu_credit_regen_amount` int(11) NOT NULL,
  `_cpu_credit_regen_time` varchar(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `drmaatic_group`
--

INSERT INTO `drmaatic_group` (`id`, `name`, `has_full_access`, `throttling_rate_burst`, `cpu_credit_max_amount`, `token_renewal_time`, `cpu_credit_regen_amount`, `_cpu_credit_regen_time`) VALUES
(1, 'registered', 0, '30/s', 200, '5 days', 1, '30 seconds'),
(2, 'anonymous', 0, '20/s', 100, '3 days', 1, '30 seconds');

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_job`
--

CREATE TABLE `drmaatic_job` (
  `creation_date` datetime(6) NOT NULL,
  `update_date` datetime(6) NOT NULL,
  `id` int(11) NOT NULL,
  `_job_description` varchar(200) DEFAULT NULL,
  `uuid` char(32) NOT NULL,
  `_sender_ip_addr` char(39) DEFAULT NULL,
  `_files_name` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`_files_name`)),
  `_status` varchar(200) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `_drm_job_id` int(10) UNSIGNED DEFAULT NULL CHECK (`_drm_job_id` >= 0),
  `dependency_type` varchar(20) DEFAULT NULL,
  `parent_job_id` int(11) DEFAULT NULL,
  `task_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_jobparameter`
--

CREATE TABLE `drmaatic_jobparameter` (
  `id` int(11) NOT NULL,
  `value` longtext NOT NULL,
  `job_id` int(11) DEFAULT NULL,
  `param_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_job_dependencies`
--

CREATE TABLE `drmaatic_job_dependencies` (
  `id` int(11) NOT NULL,
  `from_job_id` int(11) NOT NULL,
  `to_job_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_parameter`
--

CREATE TABLE `drmaatic_parameter` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `flag` varchar(100) DEFAULT NULL,
  `type` varchar(100) NOT NULL,
  `default` varchar(1000) NOT NULL,
  `description` varchar(300) NOT NULL,
  `private` tinyint(1) NOT NULL,
  `required` tinyint(1) NOT NULL,
  `task_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `drmaatic_parameter`
--

INSERT INTO `drmaatic_parameter` (`id`, `name`, `flag`, `type`, `default`, `description`, `private`, `required`, `task_id`) VALUES
(1, 'wait_time', '--waitTtime', 'file', '', '', 0, 0, 1);

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_queue`
--

CREATE TABLE `drmaatic_queue` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `max_cpu` int(10) UNSIGNED NOT NULL CHECK (`max_cpu` >= 0),
  `max_mem` int(10) UNSIGNED NOT NULL CHECK (`max_mem` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `drmaatic_queue`
--

INSERT INTO `drmaatic_queue` (`id`, `name`, `max_cpu`, `max_mem`) VALUES
(1, 'normal', 1, 500);

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_task`
--

CREATE TABLE `drmaatic_task` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `command` varchar(500) NOT NULL,
  `required_tokens` int(11) NOT NULL,
  `_max_clock_time` varchar(100) NOT NULL,
  `is_array` tinyint(1) NOT NULL,
  `begin_index` int(11) DEFAULT NULL,
  `end_index` int(11) DEFAULT NULL,
  `step_index` int(11) DEFAULT NULL,
  `cpus` int(10) UNSIGNED NOT NULL CHECK (`cpus` >= 0),
  `mem` int(10) UNSIGNED NOT NULL CHECK (`mem` >= 0),
  `is_output_public` tinyint(1) NOT NULL,
  `queue_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `drmaatic_task`
--

INSERT INTO `drmaatic_task` (`id`, `name`, `command`, `required_tokens`, `_max_clock_time`, `is_array`, `begin_index`, `end_index`, `step_index`, `cpus`, `mem`, `is_output_public`, `queue_id`) VALUES
(1, 'wait_task', 'wait.py', 1, '3 hours', 0, NULL, NULL, NULL, 1, 256, 0, 1);

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_task_groups`
--

CREATE TABLE `drmaatic_task_groups` (
  `id` int(11) NOT NULL,
  `task_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_token`
--

CREATE TABLE `drmaatic_token` (
  `id` int(11) NOT NULL,
  `jwt` varchar(1000) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `drmaatic_user`
--

CREATE TABLE `drmaatic_user` (
  `id` int(11) NOT NULL,
  `source` varchar(50) NOT NULL,
  `username` varchar(100) NOT NULL,
  `name` varchar(20) DEFAULT NULL,
  `surname` varchar(20) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `token_renewal_time` varchar(40) DEFAULT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_drmaatic_admin_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `drmaatic_admin`
--
ALTER TABLE `drmaatic_admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `drmaatic_admin_groups`
--
ALTER TABLE `drmaatic_admin_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `drmaatic_admin_groups_admin_id_group_id_585cafee_uniq` (`admin_id`,`group_id`),
  ADD KEY `drmaatic_admin_groups_group_id_db0c44fd_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `drmaatic_admin_user_permissions`
--
ALTER TABLE `drmaatic_admin_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `drmaatic_admin_user_perm_admin_id_permission_id_767368e5_uniq` (`admin_id`,`permission_id`),
  ADD KEY `drmaatic_admin_user__permission_id_5cace836_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `drmaatic_group`
--
ALTER TABLE `drmaatic_group`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `drmaatic_job`
--
ALTER TABLE `drmaatic_job`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uuid` (`uuid`),
  ADD KEY `drmaatic_job_user_id_a616772a_fk_drmaatic_user_id` (`user_id`),
  ADD KEY `drmaatic_job_parent_job_id_0204730b_fk_drmaatic_job_id` (`parent_job_id`),
  ADD KEY `drmaatic_job_task_id_896e3703_fk_drmaatic_task_id` (`task_id`);

--
-- Indexes for table `drmaatic_jobparameter`
--
ALTER TABLE `drmaatic_jobparameter`
  ADD PRIMARY KEY (`id`),
  ADD KEY `drmaatic_jobparameter_job_id_a59e315e_fk_drmaatic_job_id` (`job_id`),
  ADD KEY `drmaatic_jobparameter_param_id_6c784c83_fk_drmaatic_parameter_id` (`param_id`);

--
-- Indexes for table `drmaatic_job_dependencies`
--
ALTER TABLE `drmaatic_job_dependencies`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `drmaatic_job_dependencies_from_job_id_to_job_id_9d654c34_uniq` (`from_job_id`,`to_job_id`),
  ADD KEY `drmaatic_job_dependencies_to_job_id_7cbbf40b_fk_drmaatic_job_id` (`to_job_id`);

--
-- Indexes for table `drmaatic_parameter`
--
ALTER TABLE `drmaatic_parameter`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `param_name` (`name`,`task_id`),
  ADD KEY `drmaatic_parameter_task_id_741abbe6_fk_drmaatic_task_id` (`task_id`);

--
-- Indexes for table `drmaatic_queue`
--
ALTER TABLE `drmaatic_queue`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `drmaatic_task`
--
ALTER TABLE `drmaatic_task`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `drmaatic_task_queue_id_6f0e6726_fk_drmaatic_queue_id` (`queue_id`);

--
-- Indexes for table `drmaatic_task_groups`
--
ALTER TABLE `drmaatic_task_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `drmaatic_task_groups_task_id_group_id_55fc3a98_uniq` (`task_id`,`group_id`),
  ADD KEY `drmaatic_task_groups_group_id_ef71843e_fk_drmaatic_group_id` (`group_id`);

--
-- Indexes for table `drmaatic_token`
--
ALTER TABLE `drmaatic_token`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `drmaatic_user`
--
ALTER TABLE `drmaatic_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `drmaatic_user_source_username_d45a59eb_uniq` (`source`,`username`),
  ADD KEY `drmaatic_user_group_id_d7811189_fk_drmaatic_group_id` (`group_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=57;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT for table `drmaatic_admin`
--
ALTER TABLE `drmaatic_admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `drmaatic_admin_groups`
--
ALTER TABLE `drmaatic_admin_groups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `drmaatic_admin_user_permissions`
--
ALTER TABLE `drmaatic_admin_user_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `drmaatic_group`
--
ALTER TABLE `drmaatic_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `drmaatic_job`
--
ALTER TABLE `drmaatic_job`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `drmaatic_jobparameter`
--
ALTER TABLE `drmaatic_jobparameter`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- AUTO_INCREMENT for table `drmaatic_job_dependencies`
--
ALTER TABLE `drmaatic_job_dependencies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `drmaatic_parameter`
--
ALTER TABLE `drmaatic_parameter`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `drmaatic_queue`
--
ALTER TABLE `drmaatic_queue`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `drmaatic_task`
--
ALTER TABLE `drmaatic_task`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `drmaatic_task_groups`
--
ALTER TABLE `drmaatic_task_groups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `drmaatic_token`
--
ALTER TABLE `drmaatic_token`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `drmaatic_user`
--
ALTER TABLE `drmaatic_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_drmaatic_admin_id` FOREIGN KEY (`user_id`) REFERENCES `drmaatic_admin` (`id`);

--
-- Constraints for table `drmaatic_admin_groups`
--
ALTER TABLE `drmaatic_admin_groups`
  ADD CONSTRAINT `drmaatic_admin_groups_admin_id_1d0c9af6_fk_drmaatic_admin_id` FOREIGN KEY (`admin_id`) REFERENCES `drmaatic_admin` (`id`),
  ADD CONSTRAINT `drmaatic_admin_groups_group_id_db0c44fd_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `drmaatic_admin_user_permissions`
--
ALTER TABLE `drmaatic_admin_user_permissions`
  ADD CONSTRAINT `drmaatic_admin_user__admin_id_c9008345_fk_drmaatic_` FOREIGN KEY (`admin_id`) REFERENCES `drmaatic_admin` (`id`),
  ADD CONSTRAINT `drmaatic_admin_user__permission_id_5cace836_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);

--
-- Constraints for table `drmaatic_job`
--
ALTER TABLE `drmaatic_job`
  ADD CONSTRAINT `drmaatic_job_parent_job_id_0204730b_fk_drmaatic_job_id` FOREIGN KEY (`parent_job_id`) REFERENCES `drmaatic_job` (`id`),
  ADD CONSTRAINT `drmaatic_job_task_id_896e3703_fk_drmaatic_task_id` FOREIGN KEY (`task_id`) REFERENCES `drmaatic_task` (`id`),
  ADD CONSTRAINT `drmaatic_job_user_id_a616772a_fk_drmaatic_user_id` FOREIGN KEY (`user_id`) REFERENCES `drmaatic_user` (`id`);

--
-- Constraints for table `drmaatic_jobparameter`
--
ALTER TABLE `drmaatic_jobparameter`
  ADD CONSTRAINT `drmaatic_jobparameter_job_id_a59e315e_fk_drmaatic_job_id` FOREIGN KEY (`job_id`) REFERENCES `drmaatic_job` (`id`),
  ADD CONSTRAINT `drmaatic_jobparameter_param_id_6c784c83_fk_drmaatic_parameter_id` FOREIGN KEY (`param_id`) REFERENCES `drmaatic_parameter` (`id`);

--
-- Constraints for table `drmaatic_job_dependencies`
--
ALTER TABLE `drmaatic_job_dependencies`
  ADD CONSTRAINT `drmaatic_job_depende_from_job_id_d0f5ba0d_fk_drmaatic_` FOREIGN KEY (`from_job_id`) REFERENCES `drmaatic_job` (`id`),
  ADD CONSTRAINT `drmaatic_job_dependencies_to_job_id_7cbbf40b_fk_drmaatic_job_id` FOREIGN KEY (`to_job_id`) REFERENCES `drmaatic_job` (`id`);

--
-- Constraints for table `drmaatic_parameter`
--
ALTER TABLE `drmaatic_parameter`
  ADD CONSTRAINT `drmaatic_parameter_task_id_741abbe6_fk_drmaatic_task_id` FOREIGN KEY (`task_id`) REFERENCES `drmaatic_task` (`id`);

--
-- Constraints for table `drmaatic_task`
--
ALTER TABLE `drmaatic_task`
  ADD CONSTRAINT `drmaatic_task_queue_id_6f0e6726_fk_drmaatic_queue_id` FOREIGN KEY (`queue_id`) REFERENCES `drmaatic_queue` (`id`);

--
-- Constraints for table `drmaatic_task_groups`
--
ALTER TABLE `drmaatic_task_groups`
  ADD CONSTRAINT `drmaatic_task_groups_group_id_ef71843e_fk_drmaatic_group_id` FOREIGN KEY (`group_id`) REFERENCES `drmaatic_group` (`id`),
  ADD CONSTRAINT `drmaatic_task_groups_task_id_cd6559f9_fk_drmaatic_task_id` FOREIGN KEY (`task_id`) REFERENCES `drmaatic_task` (`id`);

--
-- Constraints for table `drmaatic_user`
--
ALTER TABLE `drmaatic_user`
  ADD CONSTRAINT `drmaatic_user_group_id_d7811189_fk_drmaatic_group_id` FOREIGN KEY (`group_id`) REFERENCES `drmaatic_group` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
