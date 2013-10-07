[getting started]
  [安装]
    最好不要和ccf在同一台机器启动
    pip install Django==1.4.5
    pip install -r requirements.txt
  [启动]
    python start_vt_manager.py

[plugins/vt/statemanager]
  [功能]
  1、主机状态管理：定期扫描server状态
  2、虚拟机状态管理：定期扫描虚拟机的状态

  [接口]
  目前采用共享数据库的方式和ccf交换状态信息。

[plugins/vt/vtmanager]
  [功能]
  1、虚拟机管理：提供虚拟机的创建、删除、起停等方法

  [接口]
  目前接口都是提供给vt_plugin使用的内部接口，在此不多做赘述。

[plugins/common]
  [功能]
  1、提供基础的工具集，比如文件操作，进程，命令行，异常处理
  2、glance client：由于自有glanceclient安装问题比较多，所以重写了一个glance client（安装文档中可以吧所有有关glance client安装的步骤都去掉）
  3、agent client：调用agent的xml rpc方法，用于创建、删除、起停虚拟机及管理虚拟机的网络链接
  4、undoManager：通用的事物管理工具，用于回滚（比如删除底层虚拟机时需要清除的资源比较多，为了保障整体的事务性需要提供一个类似RDB的事务管理工具）

[建议]
  目前的方案设计是以portal为中心的设计思想，在这种情况下portal的变化就有可能导致业务及model的变化。业务间耦合度比较大。比如现在vt_manager就必须和ccf采用共享数据库的方式来实现一些数据共享。建议vt_manager、ofmanager都各自为何自己的业务和数据，portal通过接口获取所需数据。
