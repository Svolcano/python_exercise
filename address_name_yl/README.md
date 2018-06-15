## Build Image
```sh
docker-compose build
```

## image add tag
```sh
docker tag ${IMAGE_ID} 127.0.0.1:5000/bqc/api_server:${TAG}
```

## upload to private repository
```sh
docker push 127.0.0.1:5000/bqc/api_server:latest
```

## rolling update
```sh
docker service update --update-failure-action=rollback --detach=false --image 127.0.0.1:5000/bqc/api_server bqc_api_server
```

## Run

python bqc_app.py args

 - w: works ( multiprocess )
 - b: bind host ip
 - p: port
 - l: access_log to console ( True or False )

```sh
docker run --restart=unless-stopped -d -p 80:8000 --name bqc_api rainjay/bqc_api python bqc_app.py -w 4
```
---

# API

## Name Compare

### Name Compare
| request   |  http://api.bqc.dianhua.cn/name? |
|---|---|
| method | GET  |
| parmas |--------------- 输入参数--------------- |
| input | 商户输入名称 |
| bkwd | 反查结果名称 |
|  response | ---------------回传结果---------------|
|http返回直值|200|
|  Type| JSON  |
|similarity_score | 相似程度 1為最高分, 0為不相似, -1輸入有為空值不比對 |
|error| ---------------錯誤代碼 ---------------|
|http返回直值|404|
|  Type| JSON  |
|status_code| 錯誤代碼值|
|msg|錯誤描述|



### Name Compare Debug
| request   |  http://api.bqc.dianhua.cn/name?debug=1 |
|---|---|
| method | GET  |
| parmas |--------------- 输入参数--------------- |
| input | 商户输入名称 |
| bkwd | 反查结果名称 |
|  response | ---------------回传结果---------------|
| Type | JSON  |
|input_parser| 商戶輸入parser結果 |
|bkwd_parser| 反查輸入parser結果 |
|score_region|region比較分數|
|score_name|name比較分數|
|score_industry|行業號比較分數|
|score_type|企業類型比較分數|
|similarity_score | 相似程度 1為最高分, 0為不相似 |

錯誤代碼   
> - 1001 : bkwd or input輸入為空   
- 1999 : 未知錯誤   

parser結果
> - region: 地區
- name: 企業名
- industry: 行業號
- type: 企業類型

比較分數
> - 都是-1之情況為有一輸入為空
- 都是0.6為特殊狀況 input\_name為bkwd\_name子字串



```python
# Python Sample
url = 'http://192.168.20.156:8000/name?input=北京电话邦企业科技公司&bkwd=北京创新'
r = requests.get(url)
assert r.status_code == 200
print(r.json())
```

### Quality Name Compare

[swagger](http://api-bqc.dianhua.cn/swagger)

| request   |  http://api.bqc.dianhua.cn/qualityname? |
|---|---|
| method | GET  |
| parmas |--------------- 输入参数--------------- |
| name | 商户输入名称 |
| tel | 格式化后之电话号码  |
|  response | ---------------回传结果---------------|
|  Type| JSON  |
|match_result| tpye int, -1:无法比较, 99999:自行匹配结果|
|keyword_similarity| type float, 名称关键词相似度 range:0~1|
|sid| type string, 在source為dianhua時返回內部數據之shop id|
|name| type string, 搜尋結果之名稱|
|score | type float, 搜尋引擎返回之信心水準 |
|source| type string, 數據來源目前為 dianhua, tianyancha|
|status_code|type int, 返回是否正確0為正確其他請參考錯誤代碼|
|msg|返回狀態描述|


錯誤代碼
> - 1001 : bkwd or input輸入為空
- 1999 : 未知錯誤
- 1002 : debug參數錯誤
- 1003 : name or tel is empty
- Tianyancha Error
>  - 300001 : 请求失败
>  - 300002 : 账号失效
>  - 300003 : 账号过期
>  - 300004 : 访问频率过快
>  - 300005 : 无权限访问此api
>  - 300006 : 余额不足
>  - 300007 : 剩余次数不足
>  - 300008 : 缺少必要参数
>  - 300009 : 账号信息有误
>  - 300010 : URL不存在



## Address Compare

### Address Compare
| request   |  http://api.bqc.dianhua.cn/address? |
|---|---|
| method | GET  |
| parmas |--------------- 输入参数--------------- |
| name | 商户名称 |
| tel | 商户电话 |
| address | 商户地址 |
|  response | ---------------回传结果---------------|
|http返回直值|200|
|  Type|  JSON  |
| status_code | type int, 返回是否正確0為正確其他請參考錯誤代碼|
| msg | 返回狀態描述 |
|  count | results之数量  |
|  results |  回傳結果型別為list, 下方为results之详细fields |
| &nbsp;&nbsp;&nbsp;&nbsp;source |  查得地址的来源 |
| &nbsp;&nbsp;&nbsp;&nbsp;match_result | 经由高德api与detail address判断之结果 对应表如下 |
| &nbsp;&nbsp;&nbsp;&nbsp;detail_similarity | 去除三級區劃之詳細地址的edit distance 相似度 <br> 詳細地址 Ex: 朝阳区来广营朝来科技园(36号院)14号楼4层|
| &nbsp;&nbsp;&nbsp;&nbsp;raw_address_similarity | 原始地址之edit distance similarity |
| &nbsp;&nbsp;&nbsp;&nbsp;min_distance | 估計最短的地址經緯度距離|
| &nbsp;&nbsp;&nbsp;&nbsp;max_distance | 估計最長的地址經緯度距離|
| &nbsp;&nbsp;&nbsp;&nbsp;address | 查詢結果之地址|
|error| ---------------錯誤代碼 ---------------|
|http返回直值|404|
|  Type | JSON  |
| status_code | type int, 返回是否正確0為正確其他請參考錯誤代碼|
| msg | 返回狀態描述 |

---

|match_result|地址相似結果|value_code|
|---|:---:|:---:|
|AREA\_TOO\_BIG|tips給的area過大|-5|
|LNG\_LAT\_LEVEL\_TOO\_BIG|高得經緯度LEVEL過大|-4|
|MISS\_CITY|商戶與反查遺失城市資訊|-3|
|MISS\_DETAIL|商戶或反查遺失詳細地址（反查遺失率較高） |-2|
|EMPTY\_ADDRESS|商戶或反查之數入地址為空 |-1|
|MISMATCH|地址不一致 |0|
|EXACT\_MATCH|地址精確一致 |1|
|AMBIGUOUS\_MATCH|地址模糊一致|2|
