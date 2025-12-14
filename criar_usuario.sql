CREATE USER 'ngrok_user'@'%' IDENTIFIED BY 'senha_segura_ngrok_2025';
GRANT ALL PRIVILEGES ON *.* TO 'ngrok_user'@'%';
FLUSH PRIVILEGES;