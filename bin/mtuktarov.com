server {
	server_name mtuktarov.com;
	root /var/www/DjangoBlog/;
	listen 80;
	keepalive_timeout 70;

	location /static/ {
		expires max;
		alias /var/www/DjangoBlog/collectedstatic/;
	}

	location / {
       	proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Host $http_host;
		proxy_set_header X-NginX-Proxy true;
		proxy_redirect off;
		if (!-f $request_filename) {
			proxy_pass http://127.0.0.1:8000;
				break;
		}
	}

}
