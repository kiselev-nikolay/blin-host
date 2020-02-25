
cd /usr/share/monkey/

yum install dnf
dnf update
dnf install epel-release
dnf update
dnf install python3

python3 -m pip install starlette pytest requests uvicorn paramiko python-multipart

chmod +x /usr/share/monkey/services/redis.sh
sudo touch /etc/systemd/system/redis.service
sudo chmod 664 /etc/systemd/system/redis.service
echo "[Unit]
Description=redis
[Service]
ExecStart=/usr/share/monkey/services/redis.sh
[Install]
WantedBy=multi-user.target">/etc/systemd/system/redis.service


chmod +x /usr/share/monkey/services/busybox.sh
sudo touch /etc/systemd/system/busybox.service
sudo chmod 664 /etc/systemd/system/busybox.service
echo "[Unit]
Description=busybox
[Service]
ExecStart=/usr/share/monkey/services/busybox.sh
[Install]
WantedBy=multi-user.target">/etc/systemd/system/busybox.service


sudo systemctl daemon-reload
sudo systemctl start redis
sudo systemctl start busybox

