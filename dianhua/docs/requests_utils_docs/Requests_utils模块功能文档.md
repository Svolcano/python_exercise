`requests_utils.py` 文件目录：
  `call_history_crawler/worker/crawler`

`proxy_config.py` 文件目录：
  `call_history_crawler/setting`


功能实现：

  1.相对目标URL proxy pool's IP 可用
  2.对于不可用的pool's IP 持久化处理
  3.以上所用功能参数可配置


### 相对目标URL proxy pool's IP 可用

 原子粒度: request
 
 从可用`PROXIES_IP_POOLS`获取ip后，经过请求url测试ip是否可用
 如果ip可用则继续
 如果ip不可用则从可用ip列表中移除目标ip并重新获取ip


### 对于不可用的pool's IP 持久化处理

 通过写入文件持久化pools中不可用的ip
     格式: "LEVEL: 20  IP: %s URL: %s METHOD: %s PARAMS: %s DATA: %s JSON: %s"

