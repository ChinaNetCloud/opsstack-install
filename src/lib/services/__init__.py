import nginx
import haproxy
import apache

servicelist = {
    'nginx': nginx.Nginx,
    'haproxy': haproxy.Haproxy,
    'apache': apache.Apache,
    'mysql': mysql.MySQL
}
