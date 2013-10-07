#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:config.py
# Date:Sun Sep 22 00:30:02 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
#[vtmanager]
#代表启用的服务。1 代表启用 ; 0 代表禁用
vt_manager = 1
vt_manager_port = 8891

#[agent]
compute_service_port = 8886
monitor_service_port = 8887
dhcp_service_port = 8888
ovs_service_port = 8889
gateway_service_port = 8893
nat_service_port = 8894

#[statemanager]
#设置每隔多长时间探测一次agent的compute服务的状态
duration = 1
#配置服务探测的超时时间
state_connection_timeout = 1

#[scheduler]
#单台机器最多允许创建的虚拟机的数量
unique_hosts_per_alloc = 10
#可以创建虚拟机的主机，cpu、mem的最大负载，取值为百分必的形式，如下代表百分之80
max_cpu = 80
max_mem = 80
#可以创建虚拟机的主机，至少要有10G的磁盘剩余
max_disk = 10

#[高级配置项]
rpc_connection_timeout = 150
