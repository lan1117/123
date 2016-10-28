CREATE DATABASE photoshare;
USE photoshare;

/*SET FOREIGN_KEY_CHECKS=0;
DROP TABLE Albums_own;
SET FOREIGN_KEY_CHECKS=1;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE Users;
SET FOREIGN_KEY_CHECKS=1;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE Pictures_Album;
SET FOREIGN_KEY_CHECKS=1;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE Tag;
SET FOREIGN_KEY_CHECKS=1;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE Comments_photo;
SET FOREIGN_KEY_CHECKS=1;

DROP TABLE Picture_tags CASCADE;
DROP TABLE users_leave_comment CASCADE;
DROP TABLE friends CASCADE;*/

CREATE TABLE Users (
    user_id int4 AUTO_INCREMENT,
    fname varchar(255),
    lname varchar(255),
    email varchar(255) UNIQUE,
    dob varchar(255),
    hometown varchar(255),
    gender varchar(255),
    password varchar(255),
    PRIMARY KEY (user_id)
);

CREATE TABLE Albums_own (
  album_id int4 AUTO_INCREMENT,
  alname varchar(255),
  docreation varchar(255),
  user_id int4 NOT NULL,
  PRIMARY KEY (album_id),
  FOREIGN KEY (user_id)
      REFERENCES Users(user_id)
);

CREATE TABLE Pictures_Album
(
  picture_id int4 AUTO_INCREMENT,
  imgdata longblob,
  caption varchar(255),
  album_id int NOT NULL,
  PRIMARY KEY (picture_id),
  FOREIGN KEY (album_id)
      REFERENCES Albums_own(album_id)
);

CREATE TABLE Tag(
  tag varchar(255),
  PRIMARY KEY(tag)
);

CREATE TABLE Comments_photo(
  comment_id int4 AUTO_INCREMENT,
  cotext varchar(255),
  dohave varchar(255),
  user_id int4,
  picture_id int NOT NULL,
  PRIMARY KEY (comment_id),
  FOREIGN KEY (picture_id)
      REFERENCES Pictures_Album(picture_id)
);

CREATE TABLE Picture_tags(
  picture_id int4 AUTO_INCREMENT,
  tag varchar(255),
  PRIMARY KEY (picture_id, tag),
  FOREIGN KEY (picture_id)
      REFERENCES Pictures_Album(picture_id),
  FOREIGN KEY (tag)
      REFERENCES Tag(tag)
);

CREATE TABLE users_leave_comment(
  comment_id int4 AUTO_INCREMENT,
  user_id int4,
  PRIMARY KEY (comment_id, user_id),
  FOREIGN KEY (comment_id)
      REFERENCES Comments_photo(comment_id),
  FOREIGN KEY (user_id)
      REFERENCES Users(user_id)
);

CREATE TABLE friends(
  user_id int4  NOT NULL
      REFERENCES Users(user_id),
  friend int4 NOT NULL
      REFERENCES Users(user_id),
  PRIMARY KEY (user_id, friend)
);
INSERT INTO Users (fname, lname, email, dob, hometown, gender, password) VALUES ('ZK','Liu','zk@bu.edu', '730','qd','M','123456');
