from json import dumps
from neo4jrestclient.client import GraphDatabase, Node
from flask import Flask, Response, request


app = Flask(__name__, static_url_path='/static/')
gdb = GraphDatabase("http://localhost:7474")


@app.route('/')
def hello_world():
    try:
        print(query_builder(where_dict={'r.name': 'Київська область'}, limit=100))
    except BaseException as e:
        print(e)
    return app.send_static_file('index.html')


def query_builder(where_dict=None, limit=25, order=None):
    final_query = query_base
    if where_dict:
        where_str = 'where '
        for k in where_dict:
            where_str += k + "='" + where_dict[k] + "' "
        final_query += where_str
    final_query += query_return
    if order:
        final_query += 'order by ' + order + ' '
    final_query += 'limit ' + str(limit)
    return final_query

query_base = """
match (r:Region)<-[crt_r:SITUATED_IN]-(crt:Court)<-[c_crt:RULED_BY]-(c:Case)-[c_ch:CARRIED_BY]->(ch:Chairman)
optional match (ct:Court_Decision_Type)-[c_ct]-c-[c_vt]-(vt:Court_Judgement_Type)
"""
query_return = """
return r, crt, c, ch, ct, vt, crt_r, c_crt, c_ch, c_ct, c_vt
"""

query_sample = """
match (r:Region)<-[crt_r:SITUATED_IN]-(crt:Court)<-[c_crt:RULED_BY]-(c:Case)-[c_ch:CARRIED_BY]->(ch:Chairman)
optional match (ct:Court_Decision_Type)-[c_ct]-c-[c_vt]-(vt:Court_Judgement_Type)
where r.name='Київська область'
return r, crt, c, ch, ct, vt, c_crt
order by vt.name
limit 10
"""


def node(title, label, _id):
    return {'caption':title, 'node_type': label, 'id': _id}


def relation(rel):
    start = rel['start'].split('/')[-1]
    end = rel['end'].split('/')[-1]
    type = rel['metadata']['type']
    return {'source': start, 'target': end, 'caption': type}


@app.route("/graph.json")
def get_graph():
    query = query_builder()
    results = gdb.query(query,
                        params={"limit": request.args.get("limit", 100)})
    nodes = []
    rels = []
    i = 0
    for region, court, case, chairman, ct, vt, crt_r, c_crt, c_ch, c_ct, c_vt in results:
        # region
        reg_node = node(region['data']['name'], 'Region', region['metadata']['id'])
        if reg_node not in nodes:
            nodes.append(reg_node)
        # court
        court_node = node(court['data']['name'], 'Court', court['metadata']['id'])
        if court_node not in nodes:
            nodes.append(court_node)
        # chairman
        chairman_node = node(chairman['data']['name'], 'Chairman', chairman['metadata']['id'])
        if chairman_node not in nodes:
            nodes.append(chairman_node)
        # ct
        ct_node = node(ct['data']['name'], 'Court Decision Type', ct['metadata']['id'])
        if ct_node not in nodes:
            nodes.append(ct_node)
        # vt
        vt_node = node(vt['data']['name'], 'Court Judgement Type', vt['metadata']['id'])
        if vt_node not in nodes:
            nodes.append(vt_node)
        # case
        # TODO: INFO!!!1
        case_node = node(case['data']['id'] + case['data'][''], 'Court case', case['metadata']['id'])
        if case_node not in nodes:
            nodes.append(case_node)
        # crt_r
        crt_r_rel = relation(crt_r)
        if crt_r_rel not in rels:
            rels.append(crt_r_rel)
        # c_crt
        c_crt_rel = relation(c_crt)
        if c_crt_rel not in rels:
            rels.append(c_crt_rel)
        # c_ch
        c_ch_rel = relation(c_ch)
        if c_ch_rel not in rels:
            rels.append(c_ch_rel)
        # c_ct
        c_ct_rel = relation(c_ct)
        if c_ct_rel not in rels:
            rels.append(c_ct_rel)
        # c_vt
        c_vt_rel = relation(c_vt)
        if c_vt_rel not in rels:
            rels.append(c_vt_rel)
    print(nodes)
    print(rels)
    try:
        return Response(dumps({"nodes": nodes, "edges": rels}), mimetype="application/json")
    except BaseException as e:
        print(e.__str__())
        return Response(dumps({'error: ': e.__str__()}))


@app.route("/search")
def get_search():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run()
