User table:

CREATE TABLE `UoGWZOqwCP`.`user` ( `username` VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `email` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `first_name` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `last_name` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `password` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , PRIMARY KEY (`username`(10))) ENGINE = InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;


workspace table:

CREATE TABLE `UoGWZOqwCP`.`workspace` ( `slug` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `logo` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `name` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , PRIMARY KEY (`slug`(15))) ENGINE = InnoDB;

project table:

CREATE TABLE `UoGWZOqwCP`.`project` ( `project_id` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `slug` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `name` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `description` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `api_key` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , PRIMARY KEY (`project_id`(15))) ENGINE = InnoDB;

#1:N relation between workspace and project table therefore slug attribute is added as foreign key in project table..

ALTER TABLE `project` ADD FOREIGN KEY (`slug`) REFERENCES `workspace`(`slug`) ON DELETE RESTRICT ON UPDATE RESTRICT;


event table:

CREATE TABLE `UoGWZOqwCP`.`event` ( `event_id` VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `project_id` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `origin_id` VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `event_type` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `custom_data` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , PRIMARY KEY (`event_id`(10))) ENGINE = InnoDB;

#1:N relation between project and event table therefore project_id attribute is added as foreign key in event table..

ALTER TABLE `event` ADD FOREIGN KEY (`project_id`) REFERENCES `project`(`project_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;


belongs_to table: #M:N relation between user and workspace therefore new relational table is added by adding respective primary keys of the tables..

CREATE TABLE `UoGWZOqwCP`.`belongs_to` ( `username` VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `slug` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , PRIMARY KEY (`username`(10), `slug`(15))) ENGINE = InnoDB;

ALTER TABLE `belongs_to` ADD FOREIGN KEY (`username`) REFERENCES `user`(`username`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `belongs_to` ADD FOREIGN KEY (`slug`) REFERENCES `workspace`(`slug`) ON DELETE RESTRICT ON UPDATE RESTRICT;



permission table: #M:N relation between user and project therefore new relational table is added by adding respective primary keys of the tables..

CREATE TABLE `UoGWZOqwCP`.`permission` ( `username` VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , `project_id` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL , PRIMARY KEY (`username`(10), `project_id`(15))) ENGINE = InnoDB;


ALTER TABLE `permission` ADD FOREIGN KEY (`project_id`) REFERENCES `project`(`project_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;


ALTER TABLE `permission` ADD FOREIGN KEY (`username`) REFERENCES `user`(`username`) ON DELETE RESTRICT ON UPDATE RESTRICT;


