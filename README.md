# crunchbase
crunchbase miner


    upstream vidality_resume_service {
         server 127.0.0.1:8095;
    }


       location /crunchbase_search {
          proxy_pass         http://vidality_resume_service;
          proxy_redirect     off;
          proxy_set_header   Host $host;
          proxy_set_header   X-Real-IP $remote_addr;
          proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header   X-Forwarded-Host $server_name;
       }
 source ~/envs/vidality/bin/activate