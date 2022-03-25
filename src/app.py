import json

from flask import Flask, request

from blockchain import Blockchain

app = Flask(__name__)

blockchain = Blockchain()


@app.route("/chain", methods=["GET"])
def getChain():
    chainData = []
    for block in blockchain.chain:
        chainData.append(block.__dict__)
    return json.dumps({"length": len(chainData), "chain": chainData})


app.run(debug=True, port=5000)
