# README.md
# merkle-blockset-commitment

##Overview
This mini-repo demonstrates a Web3-flavored “soundness” idea inspired by rollups like Aztec: commit to a set of on-chain objects (here, consecutive block hashes) with a Merkle root and verify an inclusion proof for any element. It uses web3.py to fetch block hashes, builds a Keccak-based Merkle tree, emits a proof for a selected index, and verifies it locally. This mirrors how zk-rollups commit to state with roots and prove inclusion without revealing everything.

##Files
- app.py — CLI tool that fetches block hashes, builds a Merkle root, prints an inclusion proof, and verifies it.
- README.md — this documentation.

##Requirements
- Python 3.10+
- A reachable Ethereum RPC endpoint (Infura, Alchemy, local node, etc.)

##Installation
1) Create and activate a virtual environment (optional).
2) Install dependencies:
   pip install web3
3) Edit app.py and replace the placeholder your_api_key in RPC_URL with your actual endpoint key (or set the full RPC URL directly).

##Usage
Basic:
   python app.py <start_block> <count> [proof_index]

##Parameters:
- start_block: The first block number to include as a leaf.
- count: How many consecutive blocks to include (the set size). Keep it small, e.g., 8 or 16, if your RPC is rate-limited.
- proof_index (optional): Which leaf to generate and verify a proof for (0-based). Defaults to 0.

##Examples
1) Commit to 8 blocks starting at block 18000000 and verify the first leaf:
   python app.py 18000000 8

2) Commit to 16 blocks starting at block 18000000 and verify the 7th leaf:
   python app.py 18000000 16 7

##What the tool does
- Connects to your RPC and detects the network (e.g., Ethereum Mainnet or Sepolia).
- Fetches the requested consecutive block hashes.
- Builds a Keccak-based Merkle tree over those hashes (pairwise keccak(left||right), duplicating the last node if the level length is odd).
- Prints the Merkle root, the chosen leaf, and a step-by-step proof (sibling and position per level).
- Verifies the proof against the root and displays the result.

##Expected Output
- Network name and parameters (start block, count, proof index).
- Number of fetched block hashes and timing.
- Merkle root as a hex string.
- The chosen leaf (block hash) as hex.
- A list of proof elements (each sibling hash with its position: left or right).
- Final verification status showing whether the proof reconstructs the root (soundness check OK/FAIL).
- Total elapsed time.

##Why this is relevant to ZK and soundness
- Rollups (e.g., Aztec-style systems) commit to large sets/state using succinct roots.
- Users prove inclusion of a specific element with a short Merkle proof, without revealing the entire set.
- This demo shows the commitment and verification pattern that underlies many zk systems; you could swap local verification with a true zk circuit to gain zero-knowledge privacy.

##Notes
- Works with any Ethereum-compatible network; just point RPC_URL to the desired chain (Mainnet, Sepolia, Polygon, Optimism, Arbitrum, etc.).
- For larger counts, RPC latency and rate limits can slow down fetching; start small (8–32).
- This is a conceptual demo. It does not build real zk proofs, but its commitment/proof flow aligns with the soundness guarantees leveraged by zk rollups.
- To extend this demo, try:
  - Using transaction hashes within a single block as leaves.
  - Emitting proofs to a file for later verification.
  - Implementing the same Merkle logic inside a zk circuit (e.g., with circom/halo2) to gain zero-knowledge privacy while preserving soundness.
