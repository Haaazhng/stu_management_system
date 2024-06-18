drop DATABASE if exists Student_Management_System;
CREATE DATABASE Student_Management_System;
USE Student_Management_System;
-- 创建班级表
drop TABLE if exists Class;
CREATE TABLE Class (
    ClassID INT PRIMARY KEY,
    NumberOfStudents INT DEFAULT 0,
    Major VARCHAR(20),
    Teacher VARCHAR(20)
);

-- 创建学生表
drop TABLE if exists Student;
CREATE TABLE Student (
    StudentID CHAR(5) PRIMARY KEY,
    Name VARCHAR(20) NOT NULL,
    Gender VARCHAR(1) CHECK (Gender IN ('M', 'F')),
    Age INT CHECK (Age > 0),
    ClassID INT,
    BirthDate DATE,
    ContactInfo CHAR(11),
    Photo VARCHAR(255),
    -- 级联删除
    Constraint fk_ClassID FOREIGN KEY (ClassID) REFERENCES Class(ClassID) ON DELETE CASCADE
);

-- 创建专业变更记录表
drop TABLE if exists MajorChange;
CREATE TABLE MajorChange (
    StudentID CHAR(5), 
    OldMajor VARCHAR(20),
    NewMajor VARCHAR(20),
    ChangeDate DATE,
    PRIMARY KEY (StudentID, OldMajor, NewMajor, ChangeDate),
    -- 级联删除
    Constraint fk_StudentID FOREIGN KEY (StudentID) REFERENCES Student(StudentID) ON DELETE CASCADE
);

-- 创建奖励记录表
drop TABLE if exists Reward;
CREATE TABLE Reward (
    StudentID CHAR(5),
    Detail VARCHAR(50),
    PRIMARY KEY (StudentID, Detail)
);

-- 创建惩罚记录表
drop TABLE if exists Punish;
CREATE TABLE Punish (
    StudentID CHAR(5),
    Detail VARCHAR(50),
    PRIMARY KEY (StudentID, Detail)
);

-- 创建课程表
drop TABLE if exists Course;
CREATE TABLE Course (
    CourseID INT PRIMARY KEY, 
    CourseName VARCHAR(20) NOT NULL,
    Teacher VARCHAR(20),
    Classroom VARCHAR(10)
);

-- 创建成绩表
drop TABLE if exists Grade;
CREATE TABLE Grade (
    StudentID CHAR(5), 
    CourseID INT,
    Score INT CHECK (Score >= 0 AND Score <= 100),
    PRIMARY KEY (StudentID, CourseID)
);

-- 创建触发器，在添加学生时增加班级人数
drop TRIGGER if exists increment_class_size;
DELIMITER //
CREATE TRIGGER increment_class_size AFTER INSERT ON Student
FOR EACH ROW
BEGIN
    UPDATE Class SET NumberOfStudents = NumberOfStudents + 1 WHERE ClassID = NEW.ClassID;
END//
DELIMITER ;

-- 创建触发器，在删除学生时减少班级人数，删除奖惩信息和选课信息
drop TRIGGER if exists decrement_class_size;
DELIMITER //
CREATE TRIGGER decrement_class_size AFTER DELETE ON Student
FOR EACH ROW
BEGIN
    UPDATE Class SET NumberOfStudents = NumberOfStudents - 1 WHERE ClassID = OLD.ClassID;
    Delete from Reward where StudentID = OLD.StudentID;
    Delete from Punish where StudentID = OLD.StudentID;
    Delete from Grade where StudentID = OLD.StudentID;
END//
DELIMITER ;

-- 创建触发器，在更新信息时检查是否更换班级且更换专业，是则记录专业变更
drop TRIGGER if exists major_change;
DELIMITER //
CREATE TRIGGER major_change AFTER UPDATE ON Student
FOR EACH ROW
BEGIN
    DECLARE old_major VARCHAR(20);
    DECLARE new_major VARCHAR(20);
    SELECT Major INTO old_major FROM Class WHERE ClassID = OLD.ClassID;
    SELECT Major INTO new_major FROM Class WHERE ClassID = NEW.ClassID;
    IF old_major != new_major THEN
        INSERT INTO MajorChange(StudentID, OldMajor, NewMajor, ChangeDate) VALUES (NEW.StudentID, old_major, new_major, CURDATE());
    END IF;
END//
DELIMITER ;

-- 存储过程，添加学生信息
DROP PROCEDURE IF EXISTS AddStudent;
DELIMITER //
CREATE PROCEDURE AddStudent(IN p_StudentID CHAR(5), IN p_Name VARCHAR(20), IN p_Gender VARCHAR(1), IN p_Age INT, IN p_ClassID INT, IN p_BirthDate DATE, IN p_ContactInfo CHAR(11), IN p_Photo VARCHAR(255))
BEGIN
    INSERT INTO Student(StudentID, Name, Gender, Age, ClassID, BirthDate, ContactInfo, Photo)
    VALUES (p_StudentID, p_Name, p_Gender, p_Age, p_ClassID, p_BirthDate, p_ContactInfo, p_Photo);
END//
DELIMITER ;

-- 存储过程，用事务更新学生信息
drop PROCEDURE if exists UpdateStudent;
DELIMITER //
CREATE PROCEDURE UpdateStudent(IN p_StudentID CHAR(5), IN p_Name VARCHAR(20), IN p_Age INT, IN p_ClassID INT, IN p_ContactInfo CHAR(11), IN p_Photo VARCHAR(255))
BEGIN
    declare s int default 0;
    declare continue handler for sqlwarning set s=1;
    declare continue handler for not found set s=2;
    declare continue handler for sqlexception set s=3;
    start transaction;
    select ClassID into @classID from Student where StudentID = p_StudentID;
    UPDATE Student SET Name=p_Name, Age=p_Age, ClassID=p_ClassID, ContactInfo = p_ContactInfo, Photo = p_Photo WHERE StudentID = p_StudentID;
    if @classID != p_ClassID then
        UPDATE Class SET NumberOfStudents = NumberOfStudents + 1 WHERE ClassID = p_ClassID;
        UPDATE Class SET NumberOfStudents = NumberOfStudents - 1 WHERE ClassID = @classID;
    end if;
    if s=0 then
        commit;
    else
        rollback;
    end if;
END//
DELIMITER ;

-- 存储过程，删除学生信息
drop PROCEDURE if exists DeleteStudent;
DELIMITER //
CREATE PROCEDURE DeleteStudent(IN p_StudentID CHAR(5))
BEGIN
    DELETE FROM Student WHERE StudentID = p_StudentID;
END//
DELIMITER ;

-- 存储过程，查询学生信息，同时使用连接查询显示专业、班级人数和班主任信息
drop PROCEDURE if exists SearchStudent;
DELIMITER //
CREATE PROCEDURE SearchStudent(IN p_StudentID CHAR(5))
BEGIN
    SELECT StudentID, Name, Gender, Age, BirthDate, ContactInfo, Student.ClassID AS clsID, Photo, Major, Teacher, NumberOfStudents
    FROM Student, Class WHERE StudentID = p_StudentID AND Student.ClassID = Class.ClassID;
END//
DELIMITER ;

-- 存储过程，录入选课 
drop PROCEDURE if exists AddCourseGrade;
DELIMITER //
CREATE PROCEDURE AddCourseGrade(IN p_StudentID CHAR(5), IN p_CourseID INT)
BEGIN
    INSERT INTO Grade(StudentID, CourseID, Score) VALUES (p_StudentID, p_CourseID, NULL);
END//
DELIMITER ;

-- 存储过程，修改成绩
drop PROCEDURE if exists UpdateGrade;
DELIMITER //
CREATE PROCEDURE UpdateGrade(IN p_StudentID CHAR(5), IN p_CourseID INT, IN p_Score INT)
BEGIN
    UPDATE Grade
    SET Score = p_Score
    WHERE StudentID = p_StudentID AND CourseID = p_CourseID;
END//
DELIMITER ;

-- 存储过程，查询学生选课信息
drop PROCEDURE if exists SearchCourse;
DELIMITER //
CREATE PROCEDURE SearchCourse(IN p_StudentID CHAR(5))
BEGIN
    SELECT StudentID, Grade.CourseID as cs_id, CourseName, Teacher, Classroom, Score
    FROM Grade, Course
    WHERE StudentID = p_StudentID AND Grade.CourseID = Course.CourseID;
END//
DELIMITER ;

-- 函数，查询具体成绩
drop FUNCTION if exists GetGrade;
DELIMITER //
CREATE FUNCTION GetGrade(p_StudentID CHAR(5), p_CourseID INT) RETURNS INT DETERMINISTIC
BEGIN
    DECLARE v_score INT;
    SELECT Score INTO v_score FROM Grade WHERE StudentID = p_StudentID AND CourseID = p_CourseID;
    RETURN v_score;
END//
DELIMITER ;

-- 插入班级信息
INSERT INTO Class (ClassID, NumberOfStudents, Major, Teacher) VALUES
(101, 0, 'Computer Science', 'Dr. Zhang'),
(102, 0, 'Computer Science', 'Dr. Li'),
(201, 0, 'Chemistry', 'Dr. Wang'),
(202, 0, 'Chemistry', 'Dr. Lu'),
(301, 0, 'Physics', 'Dr. Zhu'),
(302, 0, 'Physics', 'Dr. Yang');

-- 插入学生信息
INSERT INTO Student (StudentID, Name, Gender, Age, ClassID, BirthDate, ContactInfo, Photo) VALUES
('PB001', '张三', 'M', 20, 101, '2004-05-10', '12345678901', './images/001.jpg'),
('PB002', '李四', 'F', 21, 101, '2003-04-15', '09876543210', './images/002.jpeg'),
('PB003', '王五', 'M', 22, 102, '2001-12-20', '12312312312', './images/003.jpeg'),
('PB004', '赵六', 'M', 23, 102, '2000-11-11', '32132132132', './images/004.jpg'),
('PB005', '钱七', 'M', 19, 201, '2004-08-08', '45645645645', './images/005.jpg'),
('PB006', '孙八', 'F', 20, 201, '2004-01-10', '78978978978', './images/006.jpeg'),
('PB007', '周九', 'M', 21, 202, '2002-09-15', '10101010101', './images/007.jpg'),
('PB008', '吴十', 'F', 22, 202, '2001-07-20', '20202020202', './images/008.jpg'),
('PB009', '郑十一', 'M', 20, 301, '2003-11-21', '30303030303', './images/009.jpeg'),
('PB010', '王十二', 'F', 19, 301, '2004-09-27', '40404040404', './images/010.jpeg'),
('PB011', '李十三', 'M', 21, 302, '2002-06-25', '50505050505', './images/011.jpg');

-- 插入课程信息
INSERT INTO Course (CourseID, CourseName, Teacher, Classroom) VALUES
(101, '模式识别导论', 'Dr. Yu', 'GT-B112'),
(102, '数据库系统及其应用', 'Dr. Zhou', 'GT-B212'),
(301, '力学', 'Dr. Zhu', '5202'),
(401, '歌唱艺术', 'Dr. Sun', 'GH-404'),
(201, '有机化学', 'Dr. Wang', '5206'),
(302, '量子物理', 'Dr. Yang', '3A102'),
(103, '人工智能', 'Dr. Ji', 'GT-B212'),
(402, '数学分析', 'Dr. Zhao', '1217'),
(303, '热学', 'Dr. Zhu', '5202');

-- 插入成绩信息
INSERT INTO Grade (StudentID, CourseID) VALUES
('PB001', 102),
('PB002', 102),
('PB003', 102);

INSERT INTO Grade (StudentID, CourseID, Score) VALUES
('PB001', 101, 90),
('PB001', 402, 87),
('PB002', 103, 80),
('PB003', 103, 84),
('PB004', 302, 88),
('PB005', 302, 83),
('PB005', 301, 73),
('PB005', 201, 79),
('PB006', 201, 91),
('PB007', 201, 90),
('PB008', 302, 76),
('PB008', 201, 86),
('PB009', 301, 85),
('PB009', 303, 90),
('PB010', 301, 95),
('PB010', 302, 87),
('PB010', 303, 72),
('PB010', 402, 87),
('PB011', 401, 76),
('PB011', 302, 78),
('PB011', 303, 84);

-- 插入奖励信息
INSERT INTO Reward (StudentID, Detail) VALUES
('PB001', '国家奖学金'),
('PB007', '郭沫若奖学金'),
('PB004', 'ICPC铜奖'),
('PB010', '优秀学生银奖'),
('PB008', '优秀共青团员'),
('PB002', '优秀共青团员'),
('PB001', '优秀学生金奖');

-- 插入惩罚信息
INSERT INTO Punish (StudentID, Detail) VALUES
('PB006', '违反校纪'),
('PB003', '考试作弊'),
('PB010', '违反校纪');

-- 插入转专业信息
INSERT INTO MajorChange (StudentID, OldMajor, NewMajor, ChangeDate) VALUES
('PB001', 'Chemistry', 'Computer Science', '2022-07-01'),
('PB004', 'Physics', 'Computer Science', '2023-06-29'),
('PB011', 'Computer Science', 'Physics', '2022-12-17');
