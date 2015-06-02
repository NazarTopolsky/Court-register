from json import dumps
from neo4jrestclient.client import GraphDatabase
from flask import Flask, Response, request, render_template
from datetime import datetime
from re import findall

app = Flask(__name__, static_url_path='/static/')
gdb = GraphDatabase("http://localhost:7474")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        nodes, rels = generate_graph(limit=25)
        js = dumps({"nodes": nodes, "edges": rels})
    else:
        try:
            limit = int(request.form['limit'])
        except:
            limit=25
        print(limit)
        neo4j_query = query_builder(request.form, limit)
        nodes, rels = generate_graph(limit=limit, query=neo4j_query)
        js = dumps({"nodes": nodes, "edges": rels})
    return render_template("index.html", json=js)

@app.route('/js')
def js():
    return app.send_static_file('d3.v2.js')

@app.route("/graph")
def get_graph():
    nodes, rels = generate_graph(25)
    s = dumps({"nodes": nodes, "edges": rels})
    try:
        return Response(s, mimetype="application/json")
    except BaseException as e:
        print(e.__str__())
        return Response(dumps({'error: ': e.__str__()}))

def __timestamp__(_datetime):
    if _datetime is not None and _datetime != '' and not isinstance(_datetime, float):
        d = [int(x) for x in findall(r'\d+', _datetime)]
        return datetime(d[2], d[1], d[0], 0, 0, 0).timestamp()
    else:
        return _datetime

def where_builder(params):
    try:
        result = 'WHERE '
        query_list = []
        if params['region']:
            query_list.append('(r.name =~ ".*' + params['region'] + '.*") ')
        if params['court']:
            query_list.append('(crt.name =~ ".*' + params['court'] + '.*") ')
        if params['chairman']:
            query_list.append('(ch.name =~ ".*' + params['chairman'] + '.*") ')
        # TODO
        if params['dateFrom']:
            timestamp = __timestamp__(params['dateFrom'])
            if timestamp != '':
                query_list.append('(toFloat(c.law_date) >= ' + str(timestamp) + ') ')
        if params['dateTo']:
            timestamp = __timestamp__(params['dateTo'])
            if timestamp != '':
                query_list.append('(toFloat(c.law_date) <= ' + str(timestamp) + ') ')
        # /TODO
        if 'caseTypes' in params:
            case_type_list = []
            s = '('
            for c in params.getlist('caseTypes'):
                case_type_list.append('vt.name = "' + c + '"')
            if len(case_type_list) > 1:
                for c in case_type_list[:-1]:
                    s += c + ' OR '
                s += case_type_list[len(case_type_list) - 1] + ')'
            if len(case_type_list) > 0:
                query_list.append(s)
        if len(query_list) > 1:
            for s in query_list[:-1]:
                result += s + 'AND '
            result += query_list[len(query_list) - 1]
        elif len(query_list) == 1:
            result += query_list[0]
        else:
            return ''
    except BaseException as e:
        result = ''
    return result

def query_builder(where_dict=None, limit=25, order=None):
    query_base = """
MATCH (r:Region)<-[crt_r:SITUATED_IN]-(crt:Court)<-[c_crt:RULED_BY]-(c:Case)-[c_ch:CARRIED_BY]->(ch:Chairman),
(ct:Court_Decision_Type)-[c_ct]-c-[c_vt]-(vt:Court_Judgement_Type)"""
    query_return = """
RETURN r, crt, c, ch, ct, vt, crt_r, c_crt, c_ch, c_ct, c_vt
"""
    final_query = query_base
    if where_dict:
        final_query += where_builder(where_dict)
    final_query += query_return
    if order:
        final_query += 'ORDER BY ' + order + ' '
    final_query += 'LIMIT ' + str(limit)
    return final_query

class GraphMaker:
    def __init__(self):
        self.ids_dict = {}
        self.i = -1
        self.nodes = []
        self.links = []

    def tr_id(self, _id):
        if _id not in self.ids_dict:
            self.i += 1
            self.ids_dict[_id] = self.i
        return self.ids_dict[_id]

    def push_node(self, _id, name, label, data=None):
        _node = {
            'id': self.tr_id(_id),
            'name': name,
            'label': label
        }
        if data is not None:
            _node['data'] = data
        if _node not in self.nodes:
            self.nodes.append(_node)
        return _node

    def push_link(self, source, target, caption):
        _link = {
            'source': self.tr_id(source),
            'target': self.tr_id(target),
            'label': caption
        }
        if _link not in self.links:
            self.links.append(_link)
        return _link

def generate_graph(limit=25, query=None):
    def _link(rel):
        start = int(rel['start'].split('/')[-1])
        end = int(rel['end'].split('/')[-1])
        caption = rel['metadata']['type']
        return start, end, caption

    def make_data(_dict):
        allowed = {
            'case_number': 'Номер справи',
            'link': 'Посилання',
            'reg_date': 'Дата',
            'law_date': 'Дата набуття законної сили',
            'name': 'name'
        }
        data = {}
        for key in _dict:
            if _dict[key] is not None and _dict[key] != '' and key in allowed:
                if 'date' in key:
                    val = datetime.fromtimestamp(_dict[key])
                    data[allowed[key]] = str(val).split(' ')[0]
                else:
                    data[allowed[key]] = _dict[key]
        return data

    query = query or query_builder(limit=limit)
    print(query)
    results = gdb.query(query, params={"limit": limit})
    g = GraphMaker()
    for region, court, case, chairman, ct, vt, crt_r, c_crt, c_ch, c_ct, c_vt in results:
        # nodes
        g.push_node(region['metadata']['id'],   region['data']['name'],   'Region', data=make_data(region['data']))
        g.push_node(court['metadata']['id'],    court['data']['name'],    'Court', data=make_data(court['data']))
        g.push_node(chairman['metadata']['id'], chairman['data']['name'], 'Chairman', data=make_data(chairman['data']))
        # merged with case
        # g.push_node(ct['metadata']['id'],       ct['data']['name'],                'Court Decision Type')
        # g.push_node(vt['metadata']['id'],       vt['data']['name'],                'Court Judgement Type')
        case_data = make_data(case['data'])
        case_data['Форма судочинства'] = ct['data']['name']
        case_data['Форма судового рішення'] = vt['data']['name']
        g.push_node(case['metadata']['id'], '№' + case['data']['case_number'], 'Court case', data=case_data)

        source, target, caption = _link(crt_r)
        g.push_link(source, target, caption)
        # c_crt
        source, target, caption = _link(c_crt)
        g.push_link(source, target, caption)
        # c_ch
        source, target, caption = _link(c_ch)
        g.push_link(source, target, caption)
        # merged with case
        # c_ct
        # source, target, caption = _link(c_ct)
        # g.push_link(source, target, caption)
        # # c_vt
        # source, target, caption = _link(c_vt)
        # g.push_link(source, target, caption)
    return g.nodes, g.links

if __name__ == '__main__':
    app.run()
