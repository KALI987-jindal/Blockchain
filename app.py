import streamlit as st
import hashlib, json, time, random
from datetime import datetime
from Crypto.Hash import keccak
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

st.set_page_config(page_title="Blockchain Intelligence Lab", page_icon="⛓️", layout="wide")
st.title("⛓️ Blockchain Intelligence Lab")
st.caption("An educational simulator for transaction security, data integrity, block linking and consensus.")
st.warning("Learning prototype only — it is not connected to Bitcoin, Ethereum, wallets, or a live blockchain. Do not enter real private keys or sensitive data.")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def keccak256_hex(data: bytes) -> str:
    h = keccak.new(digest_bits=256)
    h.update(data)
    return h.hexdigest()

def canonical_tx(sender, receiver, amount, note):
    payload = {"sender": sender.strip(), "receiver": receiver.strip(),
               "amount": float(amount), "note": note.strip()}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

def mine_demo(data, difficulty):
    prefix = "0" * difficulty
    nonce = 0
    started = time.perf_counter()
    while True:
        digest = sha256_hex(data + str(nonce).encode())
        if digest.startswith(prefix):
            return nonce, digest, time.perf_counter() - started
        nonce += 1

def chain_valid(chain):
    for i, block in enumerate(chain):
        if block["hash"] != sha256_hex(block["payload"].encode()):
            return False, f"Block {i} data/hash mismatch"
        if i > 0 and block["previous_hash"] != chain[i-1]["hash"]:
            return False, f"Block {i} previous-hash link mismatch"
    return True, "All block hashes and links are valid"

tabs = st.tabs(["1 · Transaction & Signature", "2 · Hash Lab", "3 · Block Chain", "4 · Consensus Lab", "5 · Attack Simulator", "6 · Concepts"])

with tabs[0]:
    st.subheader("Create a transaction")
    c1, c2 = st.columns(2)
    with c1:
        sender = st.text_input("Sender", "Aarav")
        receiver = st.text_input("Receiver", "Diya")
        amount = st.number_input("Amount (demo units)", min_value=0.01, value=25.0, step=1.0)
        note = st.text_input("Transaction note", "Library book payment")
    tx = canonical_tx(sender, receiver, amount, note)
    st.code(tx.decode(), language="json")
    st.markdown("### ECDSA signature demonstration (secp256k1)")
    if "private_key" not in st.session_state:
        st.session_state.private_key = ec.generate_private_key(ec.SECP256K1())
    if st.button("Generate demo key and sign transaction"):
        st.session_state.private_key = ec.generate_private_key(ec.SECP256K1())
        st.session_state.signature = st.session_state.private_key.sign(tx, ec.ECDSA(hashes.SHA256()))
        st.session_state.signed_tx = tx
    if "signature" in st.session_state:
        pub = st.session_state.private_key.public_key()
        sig = st.session_state.signature
        st.success("Signature generated with the Python cryptography library.")
        st.write("Signature (DER, hex):")
        st.code(sig.hex())
        try:
            pub.verify(sig, tx, ec.ECDSA(hashes.SHA256()))
            st.success("Verification: VALID for the current transaction.")
        except InvalidSignature:
            st.error("Verification: INVALID — transaction content changed after signing.")
        st.caption("ECDSA uses elliptic-curve group operations. The private key signs; the public key verifies. This is a demonstration, not an Ethereum/Bitcoin wallet implementation.")
    st.markdown("### ECDSA vs Schnorr — design comparison")
    st.write("Bitcoin historically used ECDSA over secp256k1; Taproot introduced BIP-340 Schnorr signatures. This dashboard performs a real local ECDSA sign/verify demo; Schnorr is explained comparatively, not implemented.")
    st.table([
        {"Aspect":"Signature scheme","ECDSA":"Schnorr"},
        {"Aspect":"Underlying curve here","ECDSA":"secp256k1","Schnorr":"secp256k1"},
        {"Aspect":"Linearity / aggregation","ECDSA":"More complex","Schnorr":"Supports useful aggregation constructions"},
        {"Aspect":"Project treatment","ECDSA":"Implemented demo","Schnorr":"Conceptual comparison"},
    ])

with tabs[1]:
    st.subheader("Compare cryptographic hash functions")
    msg = st.text_area("Input message", "Transfer 25 units from Aarav to Diya")
    raw = msg.encode()
    a, b = st.columns(2)
    with a:
        st.markdown("**SHA-256**")
        st.code(sha256_hex(raw))
        st.caption("256-bit digest from the SHA-2 family.")
    with b:
        st.markdown("**Keccak-256**")
        st.code(keccak256_hex(raw))
        st.caption("Ethereum uses Keccak-256; it is not identical to standardized SHA3-256.")
    st.markdown("### Avalanche-effect experiment")
    changed = msg + ("!" if not msg.endswith("!") else "?")
    st.write("Original:", msg)
    st.write("Modified:", changed)
    st.write("SHA-256 original:", sha256_hex(msg.encode()))
    st.write("SHA-256 modified:", sha256_hex(changed.encode()))
    st.write("Keccak-256 original:", keccak256_hex(msg.encode()))
    st.write("Keccak-256 modified:", keccak256_hex(changed.encode()))
    st.caption("A tiny input change should produce a very different digest. This is a visual demonstration, not a statistical proof of cryptographic security.")

with tabs[2]:
    st.subheader("Build a linked block chain")
    if "chain" not in st.session_state:
        genesis_payload = json.dumps({"index":0,"transactions":["Genesis block"]}, sort_keys=True)
        st.session_state.chain = [{"index":0,"payload":genesis_payload,"previous_hash":"0"*64,"hash":sha256_hex(genesis_payload.encode())}]
    new_tx = st.text_input("Transaction to add to next block", "Aarav pays Diya 25")
    if st.button("Add block"):
        prev = st.session_state.chain[-1]["hash"]
        idx = len(st.session_state.chain)
        payload = json.dumps({"index":idx,"transactions":[new_tx],"created_at":datetime.utcnow().isoformat()+"Z"}, sort_keys=True)
        st.session_state.chain.append({"index":idx,"payload":payload,"previous_hash":prev,"hash":sha256_hex(payload.encode())})
    if st.button("Reset chain"):
        st.session_state.pop("chain", None)
        st.rerun()
    for block in st.session_state.chain:
        with st.expander(f"Block {block['index']} · {block['hash'][:16]}…", expanded=True):
            st.write("Payload:", block["payload"])
            st.write("Previous hash:", block["previous_hash"])
            st.write("Current hash:", block["hash"])
    ok, message = chain_valid(st.session_state.chain)
    (st.success if ok else st.error)(message)

with tabs[3]:
    st.subheader("Consensus mechanisms: simplified simulations")
    left, right = st.columns(2)
    with left:
        st.markdown("### Proof of Work")
        difficulty = st.slider("Leading zero difficulty (demo)", 1, 4, 2)
        pow_input = st.text_input("Block data", "Block 7: demo transactions")
        if st.button("Run PoW nonce search"):
            nonce, digest, elapsed = mine_demo(pow_input.encode(), difficulty)
            st.metric("Nonce found", nonce)
            st.metric("Attempts", nonce + 1)
            st.metric("Elapsed time (seconds)", f"{elapsed:.5f}")
            st.code(digest)
            st.caption("The demo checks sequential nonces. This is not Bitcoin mining and its timing is hardware-dependent.")
    with right:
        st.markdown("### Proof of Stake")
        n = st.slider("Number of demo validators", 3, 12, 6)
        stakes = [st.number_input(f"Validator {i+1} stake weight", min_value=1, max_value=100, value=(i+1)*5, key=f"stake{i}") for i in range(n)]
        if st.button("Select proposer (weighted demo)"):
            chosen = random.choices(range(n), weights=stakes, k=1)[0]
            st.success(f"Selected proposer: Validator {chosen+1}")
            st.bar_chart({f"Validator {i+1}": stakes[i] for i in range(n)})
        st.caption("This weighted random selection is only an analogy. Ethereum PoS uses a specified protocol, cryptographic randomness, attestations, fork choice and slashing—not this toy picker.")
    st.markdown("### Comparison")
    st.table([
        {"Dimension":"Resource committed","Proof of Work":"Computational work / energy","Proof of Stake":"Staked capital"},
        {"Dimension":"Block proposer","Proof of Work":"Miner wins nonce race","Proof of Stake":"Protocol selects validator"},
        {"Dimension":"Main trade-off","Proof of Work":"Energy and hardware cost","Proof of Stake":"Stake concentration and protocol/economic risks"},
    ])

with tabs[4]:
    st.subheader("Tampering and integrity checks")
    if "chain" not in st.session_state:
        st.info("Create blocks in the Block Chain tab first.")
    else:
        idx = st.number_input("Select block index to tamper with", min_value=0, max_value=len(st.session_state.chain)-1, value=0, step=1)
        replacement = st.text_input("Replacement payload", "ALTERED: unauthorized transaction")
        if st.button("Tamper with selected block"):
            st.session_state.chain[int(idx)]["payload"] = replacement
            st.warning("Block payload changed without recalculating its hash.")
        if st.button("Recalculate hash of selected block (does not repair later links)"):
            b = st.session_state.chain[int(idx)]
            b["hash"] = sha256_hex(b["payload"].encode())
        ok, message = chain_valid(st.session_state.chain)
        (st.success if ok else st.error)(message)
        st.caption("The chain check detects a mismatch in this local list. Real networks additionally rely on distributed consensus and independent nodes.")

with tabs[5]:
    st.subheader("Discrete Mathematics connections")
    st.markdown("""
- **Sets and sequences:** a blockchain is an ordered sequence of blocks; transactions form finite data collections.
- **Functions:** a hash function maps an input bit string to a fixed-length digest.
- **Modular arithmetic and finite groups:** elliptic-curve cryptography uses algebraic group operations over a finite field.
- **Binary logic:** SHA-256 and Keccak use bitwise Boolean operations and permutations.
- **Probability:** Proof of Work can be studied through the probability of finding a valid hash; a simplified model has expected trials that grow as the target becomes harder.
- **Graphs / linked structures:** each block references its predecessor, creating a linked sequence; distributed nodes maintain copies of the ledger.
""")
    st.info("Important distinction: hashing provides a digest for integrity checks; it does not encrypt data or prove who created it. Digital signatures provide authentication/integrity under their cryptographic assumptions. Consensus helps distributed nodes agree on accepted history.")
