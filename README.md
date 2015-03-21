#Zabbix-Ceilometer Proxy
**A.K.A. ZCP**

##Nguồn bài viết

[OneSourceConsult](https://github.com/OneSourceConsult/ZabbixCeilometer-Proxy)

##Cách sử dụng

####Tại Zabbix host

Log on với quyền root

Cài các gói cần thiết
```sh
apt-get install -y python-pip git
pip install pika
```

Clone repo này về 
```sh
git clone https://github.com/longsube/ZabbixCeilometer-Proxy.git
```

####Tại Controller node:

*Yêu cầu: Cần cài đặt ceilometer*

Sửa file cấu hình keystone

```vi /etc/keystone/keystone.conf```

```sh 
[DEFAULT]
...
notification_driver = keystone.openstack.common.notifier.rpc_notifier
...
```

Trở lại Zabbix Node

`cd ZabbixCeilometer-Proxy`

Sửa file proxy.conf và cấu hình các thông số cho đúng với cấu hình zabbix và openstack của bạn. Có thể tham khảo file proxy.conf trong github này

Sau khi sửa xong chạy lệnh:

`python proxy.py`

Tại web của zabbix, download `template_nova.xml` và import vào Các template của bạn (Configuration, Template, Import)

**Chú ý** Bạn có thể tham khảo hướng dẫn tại [youtube](https://www.youtube.com/watch?v=DXz-W9fgvRk)

####Sử dụng script auto start

```sh
cd /root/ZabbixCeilometer-Proxy
mv proxy /etc/init.d/
chmod 770 /etc/init.d/proxy
/etc/init.d/proxy start
/etc/init.d/proxy stop
update-rc.d proxy defaults
```

##Copyright
Copyright (c) 2014 OneSource Consultoria Informatica, Lda. [🔗](http://www.onesource.pt)

This project has been developed in the scope of the MobileCloud Networking project[🔗](http://mobile-cloud-networking.eu) by Cláudio Marques, David Palma and Luis Cordeiro.

##License
Distributed under the Apache 2 license. See ``LICENSE.txt`` for more information.
