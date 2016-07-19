import nginx
import haproxy
import apache
import mysql
import phpfpm


servicelist = {
    'nginx': nginx.Nginx,
    'haproxy': haproxy.Haproxy,
    'apache': apache.Apache,
    'phpfpm': phpfpm.Phpfpm,
    'mysql': mysql.MySQL
}
