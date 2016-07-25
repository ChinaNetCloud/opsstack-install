import nginx
import haproxy
import apache
import mysql
import phpfpm
import java


servicelist = {
    'nginx': nginx.Nginx,
    'haproxy': haproxy.Haproxy,
    'apache': apache.Apache,
    'phpfpm': phpfpm.Phpfpm,
    'java': java.Java,
    'mysql': mysql.MySQL
}
