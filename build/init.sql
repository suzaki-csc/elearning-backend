-- 初期データベース設定
CREATE DATABASE IF NOT EXISTS elearning_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS elearning_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ユーザー権限設定
GRANT ALL PRIVILEGES ON elearning_db.* TO 'elearning'@'%';
GRANT ALL PRIVILEGES ON elearning_test_db.* TO 'elearning'@'%';
FLUSH PRIVILEGES;