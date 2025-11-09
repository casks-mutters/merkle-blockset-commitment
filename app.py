# app.py
from web3 import Web3
import sys
import time
from typing import List, Tuple

RPC_URL = "https://mainnet.infura.io/v3/your_api_key"

def get_network_name(chain_id: int) -> str:
    networks = {
        1: "Ethereum Mainnet",
        11155111: "Sepolia Testnet",
        10: "Optimism",
        137: "Polygon",
        42161: "Arbitrum One",
    }
    return networks.get(chain_id, f"Unknown (chain ID {chain_id})")

def keccak_concat(a: bytes, b: bytes) -> bytes:
    return Web3.keccak(a + b)

def build_merkle_tree(leaves: List[bytes]) -> List[List[bytes]]:
    if not leaves:
        raise ValueError("No leaves provided")
    # ensure each leaf is exactly 32 bytes
    lvl = [bytes(leaf).rjust(32, b"\x00") for leaf in leaves]
    tree = [lvl]
    while len(lvl) > 1:
        nxt = []
        for i in range(0, len(lvl), 2):
            left = lvl[i]
            right = lvl[i + 1] if i + 1 < len(lvl) else lvl[i]  # duplicate last if odd
            nxt.append(keccak_concat(left, right))
        tree.append(nxt)
        lvl = nxt
    return tree

def merkle_root(tree: List[List[bytes]]) -> bytes:
    return tree[-1][0]

def merkle_proof(tree: List[List[bytes]], index: int) -> List[Tuple[bytes, str]]:
    proof = []
    idx = index
    for level in tree[:-1]:
        sibling_idx = idx ^ 1  # toggle last bit to get sibling
        if sibling_idx >= len(level):
            sibling = level[idx]  # if no sibling, duplicate self
        else:
            sibling = level[sibling_idx]
        position = "right" if idx % 2 == 0 else "left"
        proof.append((sibling, position))
        idx //= 2
    return proof

def verify_merkle_proof(leaf: bytes, proof: List[Tuple[bytes, str]], expected_root: bytes) -> bool:
    computed = leaf.rjust(32, b"\x00")
    for sibling, position in proof:
        sibling = sibling.rjust(32, b"\x00")
        if position == "right":
            computed = keccak_concat(computed, sibling)
        else:
            computed = keccak_concat(sibling, computed)
    return computed == expected_root

def fetch_block_hashes(w3: Web3, start_block: int, count: int) -> List[bytes]:
    hashes = []
    for n in range(start_block, start_block + count):
        blk = w3.eth.get_block(n)
        hashes.append(bytes(blk.hash))
    return hashes

def main():
    if len(sys.argv) not in (3, 4):
        print("Usage: python app.py <start_block> <count> [proof_index]")
        sys.exit(1)

    start_block = int(sys.argv[1])
    count = int(sys.argv[2])
    proof_index = int(sys.argv[3]) if len(sys.argv) == 4 else 0
    if count <= 0:
        print("Count must be > 0")
        sys.exit(1)
    if proof_index < 0 or proof_index >= count:
        print("proof_index out of range for the chosen count")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ RPC connection failed. Check RPC_URL or network.")
        sys.exit(1)

    print("🌐 Connected to:", get_network_name(w3.eth.chain_id))
    print(f"🔢 Start block: {start_block}, Count: {count}, Proof index: {proof_index}")
    t0 = time.time()
    hashes = fetch_block_hashes(w3, start_block, count)
    print(f"⛓️  Fetched {len(hashes)} block hashes in {time.time() - t0:.2f}s")

    # Use block hashes as leaves (already 32 bytes)
    tree = build_merkle_tree(hashes)
    root = merkle_root(tree)
    proof = merkle_proof(tree, proof_index)
    leaf = hashes[proof_index]
    ok = verify_merkle_proof(leaf, proof, root)

    def to_hex(b: bytes) -> str:
        return "0x" + b.hex()

    print("🌳 Merkle Root:", to_hex(root))
    print("🍃 Leaf (block hash at index):", to_hex(leaf))
    print("🧾 Proof (sibling, position):")
    for i, (sib, pos) in enumerate(proof):
        print(f"  L{i}: sibling={to_hex(sib)} position={pos}")
    print("🧩 Soundness check (proof verifies against root):", "✅ OK" if ok else "❌ FAIL")
    print(f"⏱️  Total time: {time.time() - t0:.2f}s")

if __name__ == "__main__":
    main()
