# Blockchain Intelligence Lab

Educational B.Tech 3rd-semester project connecting Discrete Mathematics with blockchain transaction processing.

## Modules
1. Transaction builder + real local ECDSA secp256k1 sign/verify demo (`cryptography` library).
2. SHA-256 vs Ethereum-style Keccak-256 hash comparison + avalanche-effect illustration.
3. Local linked-block chain construction and integrity validation.
4. Simplified Proof-of-Work nonce search and weighted Proof-of-Stake proposer analogy.
5. Tampering simulator.
6. Discrete Mathematics concept guide.

## Run locally (Windows / VS Code)
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Open Terminal → New Terminal.
4. Create an environment: `python -m venv .venv`
5. Activate it:
   - PowerShell: `.venv\\Scripts\\Activate.ps1`
   - Command Prompt: `.venv\\Scripts\\activate.bat`
6. Install: `pip install -r requirements.txt`
7. Run: `streamlit run app.py`
8. Open the local URL shown in the terminal (usually http://localhost:8501).

## Important scope note
This is a teaching simulator. It is not a blockchain node, wallet, smart contract, production cryptographic implementation, or connection to Bitcoin/Ethereum. The ECDSA demo uses a vetted library. Schnorr is a conceptual comparison only. The PoS picker is a toy weighted-random analogy, not an implementation of Ethereum consensus.

## Suggested demonstration
- Sign a transaction, then edit a field and observe verification fail.
- Change one character in the Hash Lab and compare digests.
- Add two blocks, then tamper with an earlier block and run chain validation.
- Increase PoW difficulty and observe the nonce search require more attempts.
- Change validator weights in the PoS analogy and rerun proposer selection.

## Results policy
Record actual values from your own run. Do not claim fixed performance, energy, or security results from this simulator.
