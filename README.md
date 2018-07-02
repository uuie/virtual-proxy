# virtual-proxy



Virtual-proxy is a py script that helps developer dispatch http request to different docker instance via nginx.



- step1 : run your services and export the inner 80/tcp port out , and append a env variable HOSTNAME  , 

  ```bash
  $ docker run -itd -p 8900:80 -eHOSTNAME='project1.localserver.com' java/project1 
  $ docker run -itd -p 8901:80 -eHOSTNAME='project2.localserver.com' java/project2
  $ docker run -itd -p 8902:80 -eHOSTNAME='s1.localserver.com' java/service1
  ```

  

- step2 : run a nginx instance and run the script 

   ```bash
    $ docker run -itd -p 80:80 nginx
    $ python vp.py
   ```

  

- Step3: the script will find all instances with  in-container http service , and list a ip=> hostname result, append the result to your /etc/hosts file. then you can visit the all the instance via host name. 



#### *  the script will did not change the hosts file automatically, you can made the change on demand.

#### * the script using IP address in proxy config file , if your ip changed or a new service is launched,  you have to re-launch the script , it will update the nginx proxy's config.

