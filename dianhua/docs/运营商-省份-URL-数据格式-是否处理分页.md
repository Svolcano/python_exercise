# 运营商-省份-URL-数据格式-是否处理分页



|运营商|省份|数据格式|URL|是否处理分页|其他|
|:---:|:---:|:----:|:---|:---|:---|
|移动|商城|||有分页,已处理|||
| 移动  | 安徽 |json|http://service.ah.10086.cn/qry/qryBillDetailPage?detailType=201&startDate=20170501&endDate=20170531&nowPage=1&qryType=&_=1497262837809  |不详| {"result":"0","retCode":"000000","retMsg":null,"detail_msg":null,"user_msg":null,"prompt_msg":null,"object":{"retInfo":null,"return_code":"000000","return_msg":null,"detail_msg":null,"user_msg":null,"prompt_msg":null,"standard_prompt_msg":null,"inter_mark":false,"codelist":[],"digesterType":0,"retStrList":null,"groupScanFlag":null,"cdrHead":{"custName":"＊＊国","phoneNO":"18365169107","cycDate":"2017年05月01日 至 2017年05月31日","qryDate":"2017年06月12日"},"cdrPackage":null,"cdrVoice":{"localTotalFee":"0.00元","localTrainFee":"0.00元","localOtherFee":"0.00元","trudgeTotalFee":"0.00元","trudgeHomeFee":"0.00元","trudgeHarborFee":"0.00元","trudgeInterFee":"0.00元","vagileTotalFee":"0.00元","vagileHomeFee":"0.00元","vagileHarborFee":"0.00元","vagileInterFee":"0.00元","cdrVoiceTotal":"0","cdrVoiceSum":"0.00元","cdrVoiceDetail":null,"cdrVoiceDetailList":[]},"cdrWlan":null,"cdrSms":null,"cdrSelf":null,"cdrSp":null,"cdrOther":null,"gprsType":"0","cdrRemark":null,"segment":"END","shareDetailList":[]},"list":null,"uuid":"ff8080815c89044f015c9bd1c2ef5471","optTime":482,"sOperTime":"20170612182034","result4Boolean":true} 2017-01~06 全都没有详单数据|
| 移动|重庆| xml(无数据,从程序来看XML中包含json) |http://service.cq.10086.cn/ics?service=ajaxDirect/1/myMobile/myMobile/javascript/&pagename=myMobile&eventname=getDetailBill&cond_DETAIL_TYPE=undefined&cond_QUERY_TYPE=0&cond_QUERY_MONTH=201705&cond_GOODS_ENAME=XFMX&cond_GOODS_NAME=%E6%B6%88%E8%B4%B9%E6%98%8E%E7%BB%86&cond_TRANS_TYPE=Q&cond_GOODS_ID=2015060500000083&ajaxSubmitType=post&ajax_randomcode=20170612182949950.9404329134526381 |<?xml version="1.0" encoding="UTF-8"?><parts><TRANSFERDATA id="tfdata"></TRANSFERDATA><JSONDATA id="json"><![CDATA[]]></JSONDATA><DATASETDATA id="dataset"><![CDATA[[{"returnInfoFlag":"not find info or cannot deal"}]]]></DATASETDATA></parts>|不详| 六个月无数据|
|移动|广东|json|url|不详|官网加载不出来|
|移动|河北|html|http://www.he.10086.cn/service/fee/qryDetailBill!qryNewBill.action?smsrandom=&r=0.39661926716127716 | 直接返回当月所有的数据, 无需处理分页||
|移动|河南|html|http://service.ha.10086.cn/service/self/tel-bill-detail!call.action?type=call&StartDate=20170501&EndDate=20170531&FilteredMobileNo= |直接返回当月所有的数据, 无需处理分页||
|移动|湖南|json||无需处理分页||
|移动|江苏|json||无需处理分页||
|移动|江西|html|http://service.jx.10086.cn/service/showBillDetail!billQueryCommit.action?otherorder=1497321231869_27224_129&billType=202&startDate=20170501&endDate=20170531&clientDate=2017-06-13%2010:33:51&menuid=00890201&requestStartTime= |每页20条 需要处理分页, 当前未处理,  处理方法见下方|
|移动|辽宁|HTML| GET /busicenter/detailquery/DetailQueryMenuAction/queryResult.menu?_menuId=40399&select=201705&beginDate=20170501&endDate=20170531&detailType=202&_=1497323267513 | 无需处理分页, 所有记录在一页上|
|移动|陕西| html| http://service.sn.10086.cn/app?service=ajaxDirect/1/DetailedQuery/DetailedQuery/javascript/refushBusiSearchResult&pagename=DetailedQuery&eventname=queryAll&&MONTH=201705&MONTH_DAY=&LAST_MONTH_DAY=2017-06-30%2000%3A00%3A00&BILL_TYPE=201&SHOW_TYPE=0&CUST_INFO=%BF%CD%BB%A7%D0%C5%CF%A2&partids=refushBusiSearchResult&ajaxSubmitType=get&ajax_randomcode=0.3795926206200302| 需要处理分页, 已处理|
|移动|山东|json|官网无反应, 返回: {"returnAttr":"中国移动客户名称,月结出账","error":"尚未登录,没有此用户的详单信息"}    待重试||
|移动|上海|js..|| 不需要处理|
|移动|天津|xml/json|不需处理|
|移动|浙江|||有分页, 已处理|
|电信|北京|没有短信接收|
|电信|重庆|json| |数据最大六条, 系统未翻页|
|电信|河北| HTML|http://he.189.cn/service/bill/action/ifr_bill_detailslist_em_new_iframe.jsp| 有分页, 无需处理, 所有记录在一页上
|电信|黑龙江|HTML| http://hl.189.cn/service/cqd/queryDetailList.do?isMobile=0&seledType=0&queryType=&pageSize=10&pageNo=1&flag=&pflag=&accountNum=18182842719%3A2000004&callType=3&selectType=1&detailType=0&selectedDate=20175&method=queryCQDMain  |最长21条记录, 官网未翻页, 程序未做翻页判断, 是否需要处理翻页: 不详|detailType = seledType = 0 漫游详单(点进去之后显示的是"详单查询"),1 长途详单,2 市话详单|
|电信|河南|html|http://ha.189.cn/service/iframe/bill/iframe_inxxall.jsp | 官网有翻页, 数据在一个响应中, 无需处理|
|电信|湖北|html|http://hb.189.cn/feesquery_querylist.action |有分页, 已处理|
|电信|湖南|html| 有分页, 已处理|
|电信|江苏|json|http://js.189.cn/queryVoiceMsgAction.action |无需处理|
|电信|江西|js/text|http://jx.189.cn/dwr/call/plaincall/Service.excute.dwr |官网有分页, 最长数据长度的7, 官网未翻页, 是否需要处理分页未知|
|电信|辽宁|json| http://ln.189.cn/queryVoiceMsgAction.action |最长记录六条, 无法确定|
|电信|内蒙古|json|http://nm.189.cn/selfservice/bill/xdQuery|记录被广告遮盖, 只能显示前4~5条, 最长记录47条, 无法确定官网是否翻页, 是否有下一页以请求另一组json数据|
|电信|陕西|html|http://sn.189.cn/service/bill/feeDetailrecordList.action| 有分页, 已处理|
|电信|上海|json| http://service.sh.189.cn/service/service/authority/query/billdetailQuery.do?begin=0&end=99999&flag=1&devNo=17321021422&dateType=his&bill_type=SCP&queryDate=2017%2F06&startDate=&endDate= | 有分页, 已处理, 目前可获取最大数据为999, 经测试, 官网支持99999条数据, 以10开头会出现异常|
|电信|四川|json|http://sc.189.cn/service/billDetail/detailQuery.jsp?startTime=2017-05-01&endTime=2017-05-31&qryType=21&randomCode=ODUwNDU1|无需处理|
|电信|云南|html|http://yn.189.cn/service/jt/bill/actionjt/ifr_bill_detailslist_em_new.jsp| 最长3条记录, 官网分页未翻页, 不详|
|电信|浙江|html|http://zj.189.cn/zjpr/cdr/getCdrDetail.htm|官网有分页, 最长数据长度的30, 官网未翻页, 是否需要处理分页未知|
|联通|all|xx|xx|有分页, 已处理|

# 不详
1. 移动|广东
1. 移动|山东
1. 电信|北京
1. 电信|重庆
1. 电信|黑龙江 目前最大999条, 可上调
1. 电信|辽宁
1. 电信|江西
1. 电信|内蒙古
1. 电信|上海 目前最大999条, 可上调
1. 电信|云南
1. 电信|浙江

# 确认需添加
1. 移动|江西

# 江西电信 数据比较奇怪
六月 数据
var s7=[];var s9={};var s10={};var s11=[];var s0={};var s1={};var s2={};var s3={};var s4={};var s5={};var s6={};var s8={};var s12=[];s7[0]=s9;
s9.ret="0";s9.totalFee="0.15";s9['total_data']=s10;s9.details=s11;s9.acctName="\u5F90\u5FD7\u4F1F";s9.MSG0="\u5BA2\u6237\u67E5\u8BE2\u5355\u6708\u8BE6\u5355\u6210\u529F\uFF01queryContent:7";s9.rowNum="7";s9.FLAG0="0";
s10['total_time']="4\u5206\u949F11\u79D2";s10['cust_name']="\u5F90\u5FD7\u4F1F";s10['total_fee']="0.15";
s11[0]=s0;s11[1]=s1;s11[2]=s2;s11[3]=s3;s11[4]=s4;s11[5]=s5;s11[6]=s6;
s0['times_int']="10";s0.otherFee="0.00";s0.callStartTime="2017/06/06 18:17:13";s0.roamFee="0.00";s0.longDistaFee="0.00";s0.totalFee="0.0";s0.callAddr="\u5317\u4EAC";s0.dialing="17379139120";s0.times="10\u79D2";s0.privilege="0.00";s0.called="10000";s0.tonghuatype="\u672C\u5730";s0.callType="\u4E3B\u53EB\u547C\u51FA";
s1['times_int']="21";s1.otherFee="0.00";s1.callStartTime="2017/06/06 18:21:17";s1.roamFee="0.00";s1.longDistaFee="0.00";s1.totalFee="0.0";s1.callAddr="\u5317\u4EAC";s1.dialing="17379139120";s1.times="21\u79D2";s1.privilege="0.00";s1.called="10000";s1.tonghuatype="\u672C\u5730";s1.callType="\u4E3B\u53EB\u547C\u51FA";
s2['times_int']="108";s2.otherFee="0.00";s2.callStartTime="2017/06/06 18:21:45";s2.roamFee="0.00";s2.longDistaFee="0.00";s2.totalFee="0.0";s2.callAddr="\u5317\u4EAC";s2.dialing="17379139120";s2.times="1\u5206\u949F48\u79D2";s2.privilege="0.00";s2.called="11888";s2.tonghuatype="\u672C\u5730";s2.callType="\u4E3B\u53EB\u547C\u51FA";
s3['times_int']="64";s3.otherFee="0.00";s3.callStartTime="2017/06/06 18:24:05";s3.roamFee="0.00";s3.longDistaFee="0.00";s3.totalFee="0.0";s3.callAddr="\u5317\u4EAC";s3.dialing="17379139120";s3.times="1\u5206\u949F4\u79D2";s3.privilege="0.00";s3.called="11888";s3.tonghuatype="\u672C\u5730";s3.callType="\u4E3B\u53EB\u547C\u51FA";
s4['times_int']="39";s4.otherFee="0.00";s4.callStartTime="2017/06/06 18:26:02";s4.roamFee="0.00";s4.longDistaFee="0.00";s4.totalFee="0.0";s4.callAddr="\u5317\u4EAC";s4.dialing="17379139120";s4.times="39\u79D2";s4.privilege="0.00";s4.called="10000";s4.tonghuatype="\u672C\u5730";s4.callType="\u4E3B\u53EB\u547C\u51FA";
s5['times_int']="4";s5.otherFee="0.00";s5.callStartTime="2017/06/06 18:26:48";s5.roamFee="0.15";s5.longDistaFee="0.00";s5.totalFee="0.15";s5.callAddr="\u5317\u4EAC";s5.dialing="17379139120";s5.times="4\u79D2";s5.privilege="0.00";s5.called="10086";s5.tonghuatype="\u6F2B\u6E38";s5.callType="\u4E3B\u53EB\u547C\u51FA";
s6['times_int']="5";s6.otherFee="0.00";s6.callStartTime="2017/06/10 13:43:37";s6.roamFee="0.00";s6.longDistaFee="0.00";s6.totalFee="0.0";s6.callAddr="\u5317\u4EAC";s6.dialing="17379139120";s6.times="5\u79D2";s6.privilege="0.00";s6.called="17701020875";s6.tonghuatype="\u6F2B\u6E38";s6.callType="\u88AB\u53EB\u547C\u5165";
s8['page_size']="15";s8['page_index']="1";s8['data_list']=s12;s8['total_count']="7";s8['page_count']="1";
s12[0]=s0;s12[1]=s1;s12[2]=s2;s12[3]=s3;s12[4]=s4;s12[5]=s5;s12[6]=s6;
dwr.engine._remoteHandleCallback('23','0',{DEVICETYPE:"10",SORTINGORDER:"1",'AREA_CODE':"-1",'TWB_GET_MONTH_DETAIL_BILL':s7,'HIDE_PAGER':"false",'SEARCH_DATE':"",'TABLE_ID':"myPage_table",'CALL_TYPE':"",'SERVICE_TYPE':"0",'DICT_CALL_TYPE':"dwr",'ACC_NBR':"17379139120",'NEED_CHECK_SESSION':"yes",QUERYCONTENT:"7",'PAGE_SIZE':"15",'_msg':null,IP:"106.37.212.73",msg:null,'PAGE_INDEX':"1",INYEARMONTH:"201706",'WRITE_ORDER':"1",flag:"0",'PAGE_MODEL':s8,'FUNC_ID':"TWB_GET_MONTH_DETAIL_BILL_NEW",'DIV_ID':"myPage",'IS_SQL':"false"});



# 江西移动
## 程序:
 post   http://service.jx.10086.cn/service/showBillDetail!billQueryCommit.action
为啥用post?
## 官方
GET http://service.jx.10086.cn/service/showBillDetail!billQueryCommit.action?otherorder=1497321231869_27224_129&billType=202&startDate=20170501&endDate=20170531&clientDate=2017-06-13%2010:33:51&menuid=00890201&requestStartTime=

## 解决分页办法:
1. step1 get URL
1. STEP2 获取记录总条数
1. 当总条数大于单页条数(20条), 请求其他方法
```
POST http://service.jx.10086.cn/service/dwr/call/plaincall/queryBill.getHtml.dwr HTTP/1.1
Host: service.jx.10086.cn
Connection: keep-alive
Content-Length: 404
Origin: http://service.jx.10086.cn
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36
Content-Type: text/plain
Accept: */*
Referer: http://service.jx.10086.cn/service/showBillDetail!queryIndex.action?billType=202&startDate=20170501&endDate=20170531&clientDate=2017-06-13%2010:33:51&menuid=00890201&requestStartTime=
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.8
Cookie: JSESSIONID=C9A88BF6A451DAA20B67EAF4F1608D2F; CmWebtokenid="15070876044,jx"; U_C_VS=3B88C65E8E13C8169041A1A8306EC6154FB261DCCBEF4CE1225480F2358C26BA; userinfokey=%7b%22loginType%22%3a%2201%22%2c%22provinceName%22%3a%22791%22%2c%22pwdType%22%3a%2202%22%2c%22userName%22%3a%2215070876044%22%7d; is_login=true; loginName=15070876044; c=e5bf78ef4835434a8278ac43faa3b4f5; mmobile_roteServer=PRODUCT; CmLocation=791|791; CmProvid=jx; WT_FPC=id=282e4a963e110c23a1b1497320990720:lv=1497321232957:ss=1497320990720; servicea=88be8665d27b98a1a13304f6833900f3|1497321238|1497321171; g_wangting_ic=r_WT_F5_05

callCount=1
page=/service/showBillDetail!queryIndex.action?billType=202&startDate=20170501&endDate=20170531&clientDate=2017-06-13%2010:33:51&menuid=00890201&requestStartTime=
httpSessionId=C9A88BF6A451DAA20B67EAF4F1608D2F
scriptSessionId=DAB7AE952D1F2E8920148A65BD03AF1F815
c0-scriptName=queryBill
c0-methodName=getHtml
c0-id=0
c0-param0=number:0 # 起始记录 该值为0/1均可
c0-param1=string:407 # 总记录数
c0-param2=boolean:false
batchId=0
使用上述请求可直接获取所有数据()

```