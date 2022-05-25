mod models;

use models::*;
use std::collections::VecDeque;
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;
use wasm_bindgen_futures::JsFuture;
use sha2::{Sha256, Digest};
use web_sys::{WebSocket, MessageEvent, Request, Response, HtmlElement};

const SIZE_OF_BOUNDS: u32 = 10000;

// functions we need in rust from javascript api
#[wasm_bindgen]
extern {
    #[wasm_bindgen(js_namespace = console)]
    pub fn log(s: &str);
}

// make the console_log more rusty
macro_rules! console_log {
    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))
}


// internal calc function; not provided to javascript
fn calc(block: &BlockToVerify, lower_bound: u32) -> Option<u32> {
    let mut nonce: u32 = lower_bound.into();

    let mut s;
    let mut s_hashed;
    let mut s_hashed_hex;

    let challenge_pattern = "0".repeat(block.difficulty.try_into().unwrap());
    while nonce < (lower_bound + SIZE_OF_BOUNDS).into() {
        s = block.get_hashable_string(nonce);
        s_hashed = Sha256::new().chain_update(&s).finalize();
        s_hashed_hex = base16ct::lower::encode_string(&s_hashed);

        if s_hashed_hex.starts_with(&challenge_pattern) {
            return Some(nonce)
        }

        nonce = nonce + 1;
    }
    None
}

// update the last blocks
fn display_last_blocks(blocks: &VecDeque<InfoBlock>) {
    let window = web_sys::window().unwrap();
    let document = window.document().unwrap();

    document.get_element_by_id(&format!("row-{}", blocks.len())).unwrap().set_class_name("");
    for (i, val) in blocks.iter().enumerate() {
        document.get_element_by_id(&format!("id-{}", i + 1)).unwrap().set_inner_html(&format!("<a href=\"/block/{}\">{}</a>", val.id, val.id));
        document.get_element_by_id(&format!("date-{}", i + 1)).unwrap().set_text_content(Some(&val.timestamp));
        document.get_element_by_id(&format!("miner-{}", i + 1)).unwrap().set_text_content(Some(&val.miner));
    }
    if blocks.len() != 1 {
        let row_one = document.get_element_by_id("row-1").unwrap().dyn_into::<HtmlElement>().unwrap();
        row_one.set_class_name("");
        row_one.offset_width();
        row_one.set_class_name("fade-out");
    }
}

// method for fetching ip
#[wasm_bindgen]
pub async fn get_ip() -> Result<(), JsValue> {
    let request = Request::new_with_str("https://ip.tfld.de:50000")?;

    let window = web_sys::window().unwrap();
    let resp_value = JsFuture::from(window.fetch_with_request(&request)).await?;

    let resp: Response = resp_value.dyn_into().unwrap();
    let ip_value = JsFuture::from(resp.text()?).await?;

    window.document().unwrap().get_element_by_id("ip").unwrap().set_text_content(Some(&format!("Deine IP: {}", ip_value.as_string().unwrap())));
    js_sys::Reflect::set(&window, &JsValue::from_str("ip"), &ip_value)?;

    Ok(())
}

// method for setting the websocket callbacks
#[wasm_bindgen]
pub fn start_websocket() -> Result<(), JsValue> {
    console_error_panic_hook::set_once();
    let window = web_sys::window().expect("No window object found");
    let host = window.location().host().expect("No host field on object location found");
    let pathname = window.location().pathname().expect("No pathname field on object location found");

    let ws = WebSocket::new(&format!("wss://{}{}", host, pathname))?;
    let mut new_block = BlockToVerify { id: 0, timestamp: 0., transactions_included: Vec::new(), transactions_count: 2, size: 2, prev_hash: "df".into(), difficulty: 0 };
    let mut last_blocks: VecDeque<InfoBlock> = VecDeque::new();

    let document = window.document().expect("No document object found");
    let status = document.get_element_by_id("status").unwrap();
    let lower_bound_span = document.get_element_by_id("lowerBound").unwrap();
    let upper_bound_span = document.get_element_by_id("upperBound").unwrap();

    let cloned_ws = ws.clone();
    let cloned_status = status.clone();

    let onmessage_callback = Closure::wrap(Box::new(move |e: MessageEvent| {
        if let Ok(txt) = e.data().dyn_into::<js_sys::JsString>() {
            let mut lower_bound: u32 = 0;

            match txt {
                x if x.as_string().unwrap().starts_with("{") => {
                    let packed_instructions: PackedInstructions = serde_json::from_str(&x.as_string().unwrap()).expect("Deserialization failed");
                    new_block = packed_instructions.block.clone();

                    if last_blocks.len() == 5 {
                        last_blocks.pop_back();
                    }
                    last_blocks.push_front(packed_instructions.last_block);
                    display_last_blocks(&last_blocks);

                    lower_bound = packed_instructions.lower_bound;
                },
                x if str::parse::<u32>(&x.as_string().unwrap()).is_ok() => {
                    lower_bound = str::parse::<u32>(&x.as_string().unwrap()).unwrap();
                }
                x => console_log!("{}", x)
            }
            cloned_status.set_text_content(Some(&format!("Challenge erhalten. Verifiziere Block {}", new_block.id)));
            lower_bound_span.set_text_content(Some(&(lower_bound).to_string()));
            upper_bound_span.set_text_content(Some(&(lower_bound + SIZE_OF_BOUNDS).to_string()));

            let message: Message;
            match calc(&new_block, lower_bound) {
                Some(nonce) => {
                    message = Message { op: "NONCE".to_string(), value: nonce.to_string() };
                    cloned_status.set_text_content(Some(&"Passende Nonce gefunden. Sende an Backend"));
                },
                None => {
                    message = Message { op: "NEXT".to_string(), value: lower_bound.to_string() };
                    cloned_status.set_text_content(Some(&"Keine passende Nonce gefunden. Frage Backend nach neuem Noncebereich ..."));
                }
            }

            cloned_ws.send_with_str(&serde_json::to_string(&message).unwrap()).expect("Error when sending message to backend")

        } else {
            console_log!("message event, received other than text: {:?}", e.data());
        }
    }) as Box<dyn FnMut(MessageEvent)>);
    ws.set_onmessage(Some(onmessage_callback.as_ref().unchecked_ref()));
    onmessage_callback.forget();

    let cloned_ws = ws.clone();

    let onopen_callback = Closure::wrap(Box::new(move |_| {
        let message = Message { op: "IP".to_string(), value: window.get("ip").unwrap().as_string().unwrap() };
        cloned_ws.send_with_str(&serde_json::to_string(&message).unwrap()).expect("Error when sending message to backend");

        status.set_text_content(Some("Verbunden. Warte auf Challenge ..."))
    }) as Box<dyn FnMut(JsValue)>);
    ws.set_onopen(Some(onopen_callback.as_ref().unchecked_ref()));
    onopen_callback.forget();

    Ok(())
}
