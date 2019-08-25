Для работы сервиса необходимы необходимы интерпретатор python3, мененджер пакетов pip и база данных mysql

Настройка сервиса:
    Клонируйте данный репозиторий себе на машину
    Устновите virtualenv
    ```pip install virtualenv```
    Перейдите в созданную директорию
    ```cd YaBackSchool```
    Создайте новое виртуальное окружение
    ```virtualenv env```
    Ативируйте его
    ```source env/bin/activate```
    Устновите зависимости
    ```pip install -r requirements.txt```
    
    Зайдите в консоль управления mysql
    Создайте нового пользователя. Вместо YaBack укажите имя пользователя, вместо Your_Password48 пароль
    
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
   Откройте config.py и впишите ваши логин и пароль, которые вы указали на при создании нового пользователя в mysql
   
   Запустите сервис
   ```python3 run.py```
   
Запуск тестов:
    Запустите сервис
    В директории проекта выполните:
    ```pytest```