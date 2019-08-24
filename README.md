Зайдите в консоль управления mysql
Создайте нового пользователя. Вместо YaBack укажите имя пользователя, вместо Your_Password48 паоль

```CREATE USER 'YaBack'@'localhost' IDENTIFIED BY 'Your_Password48';
GRANT ALL PRIVILEGES ON * . * TO 'YaBack'@'localhost';
FLUSH PRIVILEGES;
```
Следующие команды создадут новую базу данных и необходимые таблицы 
```
CREATE DATABASE `imports` CHARACTER SET utf8 COLLATE utf8_general_ci;
use imports;
create table `imports` ( id int auto_increment, constraint imports_pk primary key (id) );
```
