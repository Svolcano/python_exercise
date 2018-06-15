# 部属介绍

## 测试环境
* 地址：172.18.19.155
* 目的：此服务器主要提供预备上线的版本的黑盒测试，由测试组测试稳定后，再提交正式上线环境。
* 代码分支：此服务器上的代码皆为release分支，用来给测试组测试此预备上线的版本，任何测试发现的问题，直接再此分支上做修改，再交由测试组重新测试，稳定后merge回develop and master分支，并在master上下版本tag。)
* screen服务配置：
    * crs => api接口服务（任何api端修改代码，需重启可使用run_api.sh）
    * crs_worker => worker服务常驻于此（任何worker端修改代码，需重启可使用run_worker.sh）
    * dashboard => mrq dashboard服务常驻于此（正常情况不需重启）
    * redis => redis服务常驻于此（正常情况不需重启）

## 正式环境
* 地址：  
    * 172.18.21.216 => 目前api, worker放置這
    * 172.18.21.117 => 中央mongo db
    * 172.18.21.217 => 預計之後worker放置這
    * 172.18.21.218 => 預計之後worker放置這
* 目的：此服务器群集，提供正式环境使用，多台worker机器可配置负载平衡。
* 代码分支：皆使用master上最新的tag版本代码。
* 分散式worker的方式，需將settings/mrq_worker.py移至上层目录更名为mrq-config.py，并更改合适配置。
    * 具体设定请参考 - http://mrq.readthedocs.io/en/latest/configuration/
