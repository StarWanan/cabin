import json

def add_tunnel_category_2_node_meta(metadata_file, connections_file):
    with open(metadata_file, 'r') as f:
        nodes_metadata = json.load(f)

    with open(connections_file, 'r') as f:
        nodes_connections = json.load(f)

    # 创建一个字典来存储每个节点的tunnel_category
    tunnel_category_dict = {}

    # 遍历连接数据
    for connection in nodes_connections:
        node1, node2, tunnel_category = connection

        # 如果节点还没有tunnel_category，添加它
        if node1 not in tunnel_category_dict:
            tunnel_category_dict[node1] = tunnel_category
        if node2 not in tunnel_category_dict:
            tunnel_category_dict[node2] = tunnel_category

    # 更新nodes_metadata.json中的数据
    for node, metadata in nodes_metadata.items():
        if node in tunnel_category_dict:
            metadata['tunnel_category'] = tunnel_category_dict[node]

    with open(metadata_file, 'w') as f:
        json.dump(nodes_metadata, f, indent=4)

add_tunnel_category_2_node_meta('src/data/ExportDtas/node_metadata.json', 'src/data/ExportDtas/nodes_connections.json')