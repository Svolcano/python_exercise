#!/bin/bash
#mrq-worker
#mrq-worker q-crawl default --processes 8
python com/redis_que.py
mrq-worker q-crawl default --processes 16 --greenlets 16
#mrq-worker zhijie-crawl default --processes 8 --greenlets 10
