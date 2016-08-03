import nginx
import haproxy
import apache
import mysql
import phpfpm
import java
import mongo


servicelist = {
    'nginx': nginx.Nginx,
    'haproxy': haproxy.Haproxy,
    'apache': apache.Apache,
    'phpfpm': phpfpm.Phpfpm,
    'java': java.Java,
    'mongodb': mongo.MongoDB,
    'mysql': mysql.MySQL
}
