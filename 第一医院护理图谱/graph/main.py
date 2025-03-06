import pandas as pd

from connect import loadConfig, connect
from createGraph import createGraph

if __name__ == '__main__':
    orderData = pd.read_csv('../data/订单信息_2580.csv')
    nurseData = pd.read_csv('../data/护工信息_817.csv', encoding='GBK')

    # 订单属性
    orderProperty = ['订单号', '订单类型', '服务项目', '科室', '床位号', '创建时间', '接单时间', '服务开始时间',
                     '服务结束时间', '关闭时间', '服务天数', '费用', '已支付费用', '已退款费用']
    # 医院属性
    hospitalProperty = ['医院ID', '医院名称']
    # 病区属性
    zoneProperty = ['病区ID', '病区名称', '楼号', '楼层']
    # 服务商属性
    providerProperty = ['服务商ID', '服务商名称']
    # 护工属性
    nurseProperty = list(nurseData.columns)

    [url, username, password] = loadConfig('config.neo4j.txt')  # 加载Neo4j数据库配置
    graph = connect(url, username, password)  # 连接Neo4j数据库

    createGraph(orderData, nurseData, orderProperty, nurseProperty, graph)
    # graph.delete_all()
