import nginx
import apache
import mysql
import phpfpm
import java
import mongo
import memcached


servicelist = {
    'nginx': nginx.Nginx,
    'apache': apache.Apache,
    'phpfpm': phpfpm.Phpfpm,
    'java': java.Java,
    'memcached': memcached.Memcached,
#    'mongodb': mongo.MongoDB,
    'mysql': mysql.MySQL
}
