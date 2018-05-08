# Project - Linux Server Configuration

## Submission Goal
You will take a baseline installation of a Linux distribution on a virtual machine and prepare it to host your web applications, to include installing updates, securing it from a number of attack vectors and installing/configuring web and database servers.

## Submission 
IP Address : 13.58.200.92.xip.io
SSH Port : 2200
Application URL : http://13.58.200.92.xip.io

## Step followed 

## Secure the Server

1. Update and upgrade packages
   ```sudo apt-get update```
   ```sudo apt-get upgrade```

   Remove unwanted packages
   ```sudo apt-get autoremove```

2. Change SSH port from 22 to 2200
    Run 
    ```sudo nano /etc/ssh/sshd_config```
    Port 2200

    Restart SSH - ```/etc/init.d/ssh restart```

3. Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port      123).
    
    ```sudo ufw default deny incoming```
    ```sudo ufw default allow outgoing```
    ```sudo ufw allow ssh```
    ```sudo ufw allow 2200/tcp```
    ```sudo ufw allow www```
    ```sudo ufw allow ntp```

4.  New User Grader
    Create new user grader
    ```sudo adduser grader --disabled-password```

    Grant sudo access to grader
    - Create sudoers file for grader
      ```sudo touch /etc/sudoers.d/grader```

    - Add below text to the file
      ```grader ALL=(ALL:ALL) ALL```

5. Create key pair for grader
   Run ```ssh-keygen on local machine```

   Install Public Key
   Login as grader and run following commands
   ```mkdir .ssh```
   ```touch .ssh/authorized_keys```
   Add the contents of the .pub file which was generated locally with ssh-keygen command to authorized_keys
   ```chmod 700 .ssh```
   ```chown 644 .ssh/authorized_keys```

   Disable password based login
   Edit configuration file with below command
   ```sudo nano /etc/ssh/sshd_config ```

   Change PasswordAuthentication from yes to no
   ```PasswordAuthentication no```

    Restart ssh service
    ```sudo service ssh restart```

6.  Cofigure local timezone to UTC
    Run ```sudo nano /etc/timezone```
    and update it to ```Etc/UTC```

7.  Install and Configure Apache2
    Run sudo apt-get install apache2

    Install mod_wsgi for Python3
    ```sudo apt-get install libapache2-mod-wsgi-py3```

    Create configuration file for Virual host
    Run below commands
    ```sudo touch /etc/apache2/sites-available/catalog.conf```
    ```sudo nano /etc/apache2/sites-available/catalog.conf```

    Paste below 

    <VirtualHost *:80>
        ServerName 13.58.200.92
        ServerAlias 13.58.200.92.xip.io
        ServerAdmin admin@13.58.200.92
        WSGIDaemonProcess catalog
        WSGIProcessGroup catalog
        WSGIScriptAlias / /var/www/catalog/catalog.wsgiRun 
        <Directory /var/www/catalog/Catalog/>
            Order allow,deny
            Allow from all
        </Directory>
        Alias /static /var/www/catalog/Catalog/static
        <Directory /var/www/catalog/Catalog/static/>
            Order allow,deny
            Allow from all
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        LogLevel warn
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>

    Enable virtual host
    ```sudo a2ensite catalog```

    Restart Apache
    ```sudo apache2ctl restart```

    Verify Apache Status
    ```sudo systemctl status apache2```

8.  Install and Configure PostgreSQL
    Run ```sudo apt-get install postgresql```
    
    sudo su postgres
    Run `psql`

    Configure PostgreSQL
    1. Create user
       ```CREATE USER EMPCAT;```

    2. Grant user access to create database
       ```ALTER USER EMPCAT CREATEDB;```

    3. Create database
       ```CREATE DATABASE EMP_CATALOG WITH OWNER EMPCAT;```

    4. Revoke Schema access
       ```REVOKE ALL ON SCHEMA public FROM public;```
       ```GRANT ALL ON SCHEMA public TO empcat;```

    5.  Check for remote connection settings
        ```sudo nano /etc/postgresql/9.5/main/pg_hba.conf```
```
        local   all             postgres                                peer
        TYPE  DATABASE        USER            ADDRESS                 METHOD
   
        "local" is for Unix domain socket connections only
        local   all             all                                     peer
        IPv4 local connections:
        host    all             all             127.0.0.1/32            md5
        IPv6 local connections:
        host    all             all             ::1/128                 md5
```

9.  Install git
    ```sudo apt-get install git```

    TO ensure .git is not accessible via browser add the following somewhere in the config file.
        ```RedirectMatch 404 /.git```

    Restart apache: 
    `sudo service apache2 restart`

10. Clone the project code
    `cd /var/www`
    `mkdir catalog`

    Clone project from github
    `sudo git clone https://github.com/VasudhaLalit/Employee-Catalog.git`

    Change all the create_engine code lines to below postgresql line
    `create_engine('postgresql://empcat:empcat@localhost/emp_catalog')`

    Goto https://console.developers.google.com and select the project credentials
    Update `Authorized Javascript Origins` and `Authorized Redirect URIs` with the project URL.
    Download new client_secrets.json and update the file in the project directory.

    Add the absolute path to the `client_secrets.json` file in the program.

11. Create .wsgi
    `sudo touch /var/www/catalog/catalog.wsgi`
    `sudo nano /var/www/catalog/catalog.wsgi`

       Paste below 
        
        #!/usr/bin/python3.5
        import sys
        import os
        import logging
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        sys.path.insert(0,"/var/www/catalog/")
        sys.path.append('/var/www/catalog/Catalog')
        sys.path.append('/usr/local/lib/python3.5/site-packages')

        from Employee import app as application
        application.secret_key = 'super
`
12. Install all the dependancies
    `sudo apt-get install python3-flask`
    `sudo apt-get install python3-sqlalchemy`
    `sudo apt-get install python3-sqlalchemy_utils`
    `sudo apt-get install python3-psycopg2`
    `sudo apt-get install python3-oauth2client`
    `sudo apt-get install python3-httplib2`
    `sudo apt-get install python3-flask`

13. Make all the necessary changes for the code to work.
    `sudo service apache2 restart`


14. Goto: http://13.58.200.92.xip.io

## Author
_**Vasudha Lalit**_

## References
1. Udacity
2. Github.com 
3. https://devops.profitbricks.com/tutorials/install-and-configure-mod_wsgi-on-ubuntu-1604-1/
4. https://www.digitalocean.com/community/tutorials/how-to-set-up-apache-virtual-hosts-on-ubuntu-14-04-lts
5. StackOverflow.com
