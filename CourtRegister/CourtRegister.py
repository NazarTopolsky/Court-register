from json import dumps
from neo4jrestclient.client import GraphDatabase, Node
from flask import Flask, Response, request


app = Flask(__name__, static_url_path='/static/')
gdb = GraphDatabase("http://localhost:7474")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return app.send_static_file('index.html')
    else:
        q = '?'
        try:
            for k in request.form:
                q += '&' + k + '=' + request.form[k]
            print(q)
        except BaseException as e:
            print(e.__str__())
        return Response(dumps({'a': q}))


@app.route('/')
def search():
    pass


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


def node(title, label, _id, cluster):
    return {'caption': title, 'node_type': label, 'id': _id, 'cluster': cluster}


def relation(rel, cluster):
    start = rel['start'].split('/')[-1]
    end = rel['end'].split('/')[-1]
    type = rel['metadata']['type']
    return {'source': start, 'target': end, 'caption': type, 'cluster': cluster}


@app.route("/graph.json")
def get_graph():
    query = query_builder()
    results = gdb.query(query,
                        params={"limit": request.args.get("limit", 100)})
    nodes = []
    rels = []
    for region, court, case, chairman, ct, vt, crt_r, c_crt, c_ch, c_ct, c_vt in results:
        # region
        reg_node = node(region['data']['name'], 'Region', region['metadata']['id'], 1)
        if reg_node not in nodes:
            nodes.append(reg_node)
        # court
        court_node = node(court['data']['name'], 'Court', court['metadata']['id'], 2)
        if court_node not in nodes:
            nodes.append(court_node)
        # chairman
        chairman_node = node(chairman['data']['name'], 'Chairman', chairman['metadata']['id'], 3)
        if chairman_node not in nodes:
            nodes.append(chairman_node)
        # ct
        ct_node = node(ct['data']['name'], 'Court Decision Type', ct['metadata']['id'], 4)
        if ct_node not in nodes:
            nodes.append(ct_node)
        # vt
        vt_node = node(vt['data']['name'], 'Court Judgement Type', vt['metadata']['id'], 5)
        if vt_node not in nodes:
            nodes.append(vt_node)
        # case
        # TODO: INFO!!!1
        info = case['data']['id'] + ': ' + str(case['data']['law_date'])
        case_node = node(info, 'Court case', case['metadata']['id'], 6)
        if case_node not in nodes:
            nodes.append(case_node)
        # crt_r
        crt_r_rel = relation(crt_r, 7)
        if crt_r_rel not in rels:
            rels.append(crt_r_rel)
        # c_crt
        c_crt_rel = relation(c_crt, 8)
        if c_crt_rel not in rels:
            rels.append(c_crt_rel)
        # c_ch
        c_ch_rel = relation(c_ch, 9)
        if c_ch_rel not in rels:
            rels.append(c_ch_rel)
        # c_ct
        c_ct_rel = relation(c_ct, 10)
        if c_ct_rel not in rels:
            rels.append(c_ct_rel)
        # c_vt
        c_vt_rel = relation(c_vt, 11)
        if c_vt_rel not in rels:
            rels.append(c_vt_rel)
    print(nodes)
    print(rels)
    try:
        return Response(dumps({"nodes": nodes, "edges": rels}), mimetype="application/json")
    except BaseException as e:
        print(e.__str__())
        return Response(dumps({'error: ': e.__str__()}))


if __name__ == '__main__':
    app.run()
