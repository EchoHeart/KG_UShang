from py2neo import Graph


def loadConfig(path):
    config = []
    try:
        with open(path, 'r') as configFile:
            for line in configFile:
                line = line.strip()
                if line.startswith('NEO4J'):
                    config.append(line.split('=')[1])

        return config
    except FileNotFoundError:
        print(f"文件 {path} 不存在")


def connect(url, username, password):
    return Graph(url, auth=(username, password))
