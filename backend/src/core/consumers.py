import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import redis
from core.functions.blocks.blockGeneration import addBlockToDatabase, blockGeneration, blockValidation
from core.functions.blocks.blockQueries import getLastBlock
from core.functions.blocks.classBlock import PreBlock
from core.functions.transactions.transactionDBUpdate import transactionDatabaseUpdate
from core.functions.transactions.transactionGeneration import transactionGeneration
from core.models import Block, CalculationRange
from core.utils import combineBlockJsonWithBound, getNextLowerBound
from projectControl.settings import REDIS_HOST, REDIS_PORT

class MiningConsumer(WebsocketConsumer):
    redis_instance = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    def connect(self):
        self.accept();

        async_to_sync(self.channel_layer.group_add)("mining", self.channel_name)

		# determine lower nonce bound, get current block to verify, serialize it and send it to the new client
        newBlockJson = self.redis_instance.get("newBlock")
        newRange = CalculationRange(lowerBound=getNextLowerBound())
        newRange.save()

        lastBlock = getLastBlock()
        self.send(text_data=combineBlockJsonWithBound(newBlockJson, newRange.lowerBound, { "id": lastBlock.id, "timestamp": lastBlock.timestamp, "miner": lastBlock.miner }))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("mining", self.channel_name)

        self.close()

    def receive(self, text_data=None):
        # text_data is something like { "op": "NONCE|NEXT|IP", "value": 1234 } when op == nonce, then value is the found nonce; when op == NEXT, then value is the last bound; when IP then value is the minerip
        message = json.loads(text_data);

        if message["op"] == "IP":
            self.redis_instance.set(name=self.channel_name, value=message["value"])
        elif message["op"] == "NEXT":
            range = CalculationRange.objects.filter(lowerBound=int(message["value"]))
            if range.count() == 1:
                range[0].status = CalculationRange.FINISHED
                range[0].save()
            
            newRange = CalculationRange(lowerBound=getNextLowerBound())
            newRange.save()

            self.send(text_data=str(newRange.lowerBound))
        elif message["op"] == "NONCE":
            nonce = message["value"]

            newBlockJson = self.redis_instance.get("newBlock")
            if newBlockJson is not None:
                block = json.loads(newBlockJson, object_hook=lambda d: PreBlock(**d))

                if isinstance(block, PreBlock) and Block.objects.filter(id=block.id).count() == 0:
                    block.nonce = int(nonce)
                    block.miner = self.redis_instance.get(name=self.channel_name).decode()
                    block.hash = block.generateHash()
                    if blockValidation(block, block.difficulty):
                        addBlockToDatabase(block)
                        transactionDatabaseUpdate(block)
                        print("new block added!")

                        # start new round
                        blockGeneration()
                        transactionGeneration()
                    else:
                        print("vailidation failed")
                        self.send(text_data="Error! Block is not valid with given nonce.")

    def broadcast(self, event):
        self.send(text_data=event["text"])
