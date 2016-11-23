import nginx
import apache
import mysql
import phpfpm
import java
import mongo
import memcached
import redis


servicelist = {
    'nginx': nginx.Nginx,
    'apache': apache.Apache,
    'phpfpm': phpfpm.Phpfpm,
    'java': java.Java,
    'memcached': memcached.Memcached,
    'redis': redis.Redis,
#    'mongodb': mongo.MongoDB,
    'mysql': mysql.MySQL
}
