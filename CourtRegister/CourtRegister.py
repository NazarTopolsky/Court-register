from json import dumps
from neo4jrestclient.client import GraphDatabase, Node
from flask import Flask, Response, request


app = Flask(__name__, static_url_path='/static/')
gdb = GraphDatabase("http://localhost:7474")


@app.route('/')
def hello_world():
    return app.send_static_file('index.html')


# match (r:Region)<-[Situated_in]-(crt:Court)<-[Ruled_by]-(c:Case)-[Carried_by]-(ch:Chairman)
# optional match (ct:Court_Decision_Type)-[]-c-[]-(vt:Court_Judgement_Type)
# return r, crt, c, ch, ct, vt limit 10


@app.route("/graph")
def get_graph():
    query = ("MATCH n "
             "RETURN n "
             "LIMIT {limit}")
    results = gdb.query(query,
                        params={"limit": request.args.get("limit", 100)})

    # return Response(dumps({"nodes": nodes, "links": rels}),
    #                 mimetype="application/json")
    try:
        for r in results:
            for k in r:
                print(k)
            print('\n')
        return Response(dumps({"nodes":results.__str__()}), mimetype="application/json")
    except BaseException as e:
        print(e.__str__())
        return app.send_static_file('index.html')


@app.route("/search")
def get_search():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run()
