

```
mongoexport -d crs -c call_log --type=csv --query '{"field": 1}' --fields=sid,call_time,tel,call_tel,call_method,call_from,call_type,call_duration,call_cost --limit=10000 --out 20170512.csv
```


```
mongoexport --db test --collection traffic --out traffic.json

mongoexport -d mrq -c state_log -q '{ created: { $gte: 1489248000 } }' --out state_log_20170312_1489248000_to_20170612_1497283200.json
```