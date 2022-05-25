use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct BlockToVerify {
    pub id: u32,
    pub timestamp: f64,
    #[serde(rename(deserialize = "transactionsIncluded"))]
    pub transactions_included: Vec<String>,
    #[serde(rename(deserialize = "transactionsCount"))]
    pub transactions_count: u32,
    pub size: u32,
    #[serde(rename(deserialize = "prevHash"))]
    pub prev_hash: String,
    pub difficulty: u32
}

#[derive(Serialize, Deserialize)]
pub struct PackedInstructions {
    pub block: BlockToVerify,
    #[serde(rename(deserialize = "lowerBound"))]
    pub lower_bound: u32,
    #[serde(rename(deserialize = "lastBlock"))]
    pub last_block: InfoBlock
}

#[derive(Serialize)]
pub struct Message {
    pub op: String,
    pub value: String
}

#[derive(Serialize, Deserialize, PartialEq)]
pub struct InfoBlock {
    pub id: u32,
    pub timestamp: String,
    pub miner: String
}

impl BlockToVerify {
    pub fn get_hashable_string(&self, nonce: u32) -> String {
        format!(r###"{{"id": {}, "timestamp": {}, "transactionsIncluded": ["{}"], "transactionsCount": {}, "size": {}, "prevHash": "{}", "difficulty": {}, "nonce": {}}}"###,
        self.id, self.timestamp, self.transactions_included.join("\", \""), self.transactions_count, self.size, self.prev_hash, self.difficulty, nonce
)
    }
}
