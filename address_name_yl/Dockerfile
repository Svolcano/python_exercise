FROM rainjay/python3:3.6.4

LABEL authros=RainJay

ENV TZ=Asia/Taipei

WORKDIR /usr/src/app/

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y  gcc && apt-get autoremove -y && \
    apt-get clean autoclean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 8000

CMD ["python", "bqc_app2.py"]
