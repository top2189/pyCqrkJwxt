import cqrk

web = cqrk.web()

# 启动web服务，监听7200端口
web.runServer(port=7200, debug=True)