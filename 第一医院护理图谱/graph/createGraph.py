from py2neo import Node, Relationship, Subgraph


# 收集医院信息，创建医院节点
def collectHospital(df, g, m):
    nodes = []
    for hospitalID, hospitalName in zip(list(df['医院ID'].unique()), list(df['医院名称'].unique())):
        hospitalNode = Node('Hospital')
        hospitalNode['医院ID'] = str(hospitalID)
        hospitalNode['医院名称'] = hospitalName

        nodes.append(hospitalNode)
        m[hospitalName] = hospitalNode

    g.create(Subgraph(nodes))


# 收集服务商信息，创建服务商节点
def collectProvider(df, g, m):
    nodes = []
    for providerID, providerName in zip(list(df['服务商ID'].unique()), list(df['服务商名称'].unique())):
        providerNode = Node('Provider')
        providerNode['服务商ID'] = str(providerID)
        providerNode['服务商名称'] = providerName

        nodes.append(providerNode)
        m[providerID] = providerNode

    g.create(Subgraph(nodes))


# 收集病区信息，创建病区节点
def collectZone(df, g, m):
    nodes = []
    for zoneID, zoneName in zip(list(df['病区ID'].unique()), list(df['病区名称'].unique())):
        zoneNode = Node('Zone')
        zoneNode['病区ID'] = str(zoneID)
        zoneNode['病区名称'] = zoneName

        tmp = zoneName.split(' ')
        buildingNumber, floor = tmp[0], tmp[1]
        zoneNode['楼号'] = buildingNumber
        zoneNode['楼层'] = floor

        nodes.append(zoneNode)
        m[zoneID] = zoneNode

    g.create(Subgraph(nodes))


# 收集护工信息，创建护工节点
def collectNurse(df, g, properties, m, hMap, pMap):
    nodes = []
    relationships = []
    for _, row in df.iterrows():
        nurseNode = Node('Nurse')
        for prop in properties:
            nurseNode[prop] = str(row[prop])

        hospitalNode = hMap[row['常驻医院']]
        providerNode = pMap[row['服务商ID']]

        nodes.append(nurseNode)
        relationships.append(Relationship(nurseNode, '常驻', hospitalNode))
        relationships.append(Relationship(nurseNode, '属于', providerNode))
        relationships.append(Relationship(providerNode, '雇佣', nurseNode))

        m[row['护工ID']] = nurseNode

    g.create(Subgraph(nodes, relationships))


# 收集订单信息，创建订单节点
def collectOrder(df, g, properties, hMap, pMap, zMap, nMap):
    def transformOrderID(orderID, createTime):
        [date, time] = createTime.split(' ')
        [year, month, day] = date.split('/')
        [hour, minute] = time.split(':')
        month = '0' + month if len(month) == 1 else month
        day = '0' + day if len(day) == 1 else day
        hour = '0' + hour if len(hour) == 1 else hour

        return "{:.0f}".format(orderID)[0:5] + year + month + day + hour + minute

    nodes = []
    relationships = []
    for _, row in df.iterrows():
        orderNode = Node('Order')
        for prop in properties:
            if prop == '订单号':
                orderNode[prop] = transformOrderID(row['订单号'], row['创建时间'])
            else:
                orderNode[prop] = str(row[prop])
        nodes.append(orderNode)

        hospitalName = row['医院名称']
        hospitalNode = hMap[hospitalName]
        relationships.append(Relationship(orderNode, '位于', hospitalNode))

        zoneID = row['病区ID']
        zoneNode = zMap[zoneID]
        relationships.append(Relationship(orderNode, '位于', zoneNode))
        relationships.append(Relationship(zoneNode, '位于', hospitalNode))

        providerID = row['服务商ID']
        providerNode = pMap[providerID]
        relationships.append(Relationship(providerNode, '合作', hospitalNode))
        relationships.append(Relationship(hospitalNode, '合作', providerNode))

        nurseID = row['护工ID']
        nurseNode = nMap[nurseID]
        relationships.append(Relationship(nurseNode, '接取', orderNode))
        relationships.append(Relationship(nurseNode, '负责', zoneNode))

    g.create(Subgraph(nodes, relationships))


def createGraph(orderData, nurseData, orderProperty, nurseProperty, graph):
    hospitalMap = {}
    providerMap = {}
    zoneMap = {}
    nurseMap = {}

    collectHospital(orderData, graph, hospitalMap)  # 医院
    collectProvider(orderData, graph, providerMap)  # 服务商
    collectZone(orderData, graph, zoneMap)  # 病区
    collectNurse(nurseData, graph, nurseProperty, nurseMap, hospitalMap, providerMap)  # 护工
    collectOrder(orderData, graph, orderProperty, hospitalMap, providerMap, zoneMap, nurseMap)  # 订单

    providers = graph.nodes.match('Provider').all()
    relationships = []
    for i, left in enumerate(providers):
        for right in (providers[0:i] + providers[i + 1:]):
            relationships.append(Relationship(left, '竞争', right))

    graph.create(Subgraph(relationships=relationships))
