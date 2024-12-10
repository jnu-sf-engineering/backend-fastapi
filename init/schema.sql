USE jnu-sf;

CREATE TABLE USER (
    USER_ID BIGINT(20) NOT NULL AUTO_INCREMENT,
    EMAIL VARCHAR(255) NOT NULL UNIQUE,
    PASSWORD VARCHAR(255) NOT NULL,
    NICKNAME VARCHAR(255) NOT NULL,
    PRIMARY KEY (USER_ID)
) ENGINE=InnoDB;

CREATE TABLE PROJECT (
    PROJECT_ID BIGINT(20) NOT NULL AUTO_INCREMENT,
    USER_ID BIGINT(20) NOT NULL,
    PROJECT_NAME VARCHAR(255) NOT NULL,
    SPRINT_COUNT TINYINT NULL,
    MANAGER VARCHAR(255) NOT NULL,
    PRIMARY KEY (PROJECT_ID),
    FOREIGN KEY (USER_ID) REFERENCES USER (USER_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE SUMMARY (
    SUMMARY_ID BIGINT(20) NOT NULL AUTO_INCREMENT,
    PROJECT_ID BIGINT(20) NOT NULL,
    SUMMARY_CONTENT TEXT NOT NULL,
    LAST_UPDATED DATETIME(6) NOT NULL,
    PRIMARY KEY (SUMMARY_ID),
    FOREIGN KEY (PROJECT_ID) REFERENCES PROJECT (PROJECT_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE SPRINT (
    SPRINT_ID BIGINT(20) NOT NULL AUTO_INCREMENT,
    PROJECT_ID BIGINT(20) NOT NULL,
    SPRINT_NAME VARCHAR(255) NOT NULL,
    START_DATE DATETIME(6) NOT NULL,
    END_DATE DATETIME(6) NOT NULL,
    PRIMARY KEY (SPRINT_ID),
    FOREIGN KEY (PROJECT_ID) REFERENCES PROJECT (PROJECT_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE CARD (
    CARD_ID BIGINT(20) NOT NULL AUTO_INCREMENT,
    SPRINT_ID BIGINT(20) NOT NULL,
    CARD_CONTENT VARCHAR(255) NOT NULL,
    CARD_PARTICIPANTS VARCHAR(255) NOT NULL,
    CARD_STATUS TINYINT NOT NULL,
    PRIMARY KEY (CARD_ID),
    FOREIGN KEY (SPRINT_ID) REFERENCES SPRINT (SPRINT_ID)ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE RETROSPECT (
    RETRO_ID BIGINT(20) NOT NULL AUTO_INCREMENT,
    SPRINT_ID BIGINT(20) NOT NULL,
    SUMMARY TEXT NOT NULL,
    PRIMARY KEY (RETRO_ID),
    FOREIGN KEY (SPRINT_ID) REFERENCES SPRINT (SPRINT_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE KPT (
    RETRO_ID BIGINT(20) NOT NULL,
    KEEP TEXT NULL,
    PROBLEM TEXT NULL,
    TRY TEXT NULL,
    PRIMARY KEY (RETRO_ID),
    FOREIGN KEY (RETRO_ID) REFERENCES RETROSPECT (RETRO_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE FOUR_LS (
    RETRO_ID BIGINT(20) NOT NULL,
    LIKED TEXT NULL,
    LEARNED TEXT NULL,
    LACKED TEXT NULL,
    LOGGED_FOR TEXT NULL,
    PRIMARY KEY (RETRO_ID),
    FOREIGN KEY (RETRO_ID) REFERENCES RETROSPECT (RETRO_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE CSS (
    RETRO_ID BIGINT(20) NOT NULL,
    CSS_CONTINUE TEXT NULL,
    CSS_STOP TEXT NULL,
    CSS_START TEXT NULL,
    PRIMARY KEY (RETRO_ID),
    FOREIGN KEY (RETRO_ID) REFERENCES RETROSPECT (RETRO_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT INTO USER (EMAIL, PASSWORD, NICKNAME) VALUES ("seoyun@gmail.com", "$2b$12$qCcA0wtPMZW4hC/Ab56KPu2hv2YvzR4mZH1AH2eoWwVqFF5Jw0jD.", "seoyun");
INSERT INTO PROJECT (USER_ID, PROJECT_NAME, SPRINT_COUNT, MANAGER) VALUES (1, "소공론1", 2, "정서윤");
INSERT INTO SPRINT (PROJECT_ID, SPRINT_NAME, START_DATE, END_DATE) 
VALUES (1, 'Sprint 1', '2024-01-01 09:00:00', '2024-01-15 18:00:00'),
       (1, 'Sprint 2', '2024-01-16 09:00:00', '2024-01-31 18:00:00');