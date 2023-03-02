# Setup/Hosting

This site was run on a cloud VPS behind an nginx reverse proxy.

# Installation

```
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && docker -v
```

```
sudo groupadd docker && sudo usermod -aG docker $USER && logout
```

```
sudo apt update && sudo apt install docker-compose
```

```
git clone <the repo>
```

```
sudo apt install python3-pip
```

```
pip3 install redis flask flask-sock
```

```
docker-compose up -d --build --remove-orphans
```

Now get nginx working and HTTPs enabled

```
sudo apt install nginx
```

To setup the reverse proxy follow from Step 2 listed [here on digital ocean](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04#step-2-confirming-nginx-s-configuration)

[Add the necessary upgrade header rules](https://www.serverlab.ca/tutorials/linux/web-servers-linux/how-to-configure-nginx-for-websockets/) to let nginx know that websockets should be allowed

Purchase a domain, point the DNS to the cloud instance and then follow through with enabling HTTPS through NGINX [also here in this digital ocean guide](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04#step-2-confirming-nginx-s-configuration). Make sure the firewall rules are tight

and yeow. its working

For monitoring logs use [dozzle](http://localhost:9999) on port 9999