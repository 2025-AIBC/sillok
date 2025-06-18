# Integrating WorldLand Private Network with MetaMask and a FastAPI+Gradio DApp
## Truffle 프로젝트로 스마트 컨트랙트를 관리
Local Ganache 환경에서 컨트랙트를 컴파일, 배포, 확인

## 로컬 Ganache에 MetaDataStoreContract(및 Migrations)의 정상 배포 **확인** (개발-디버그용) (컨트랙트 로직 정상 동작 검증)
- `contracts/Migrations.sol` 및 `migrations/1_initial_migration.js` 파일 추가 필요
  
#### 1) Ganache 로컬 체인 실행: 로컬 RPC 서버(포트 8545, 체인 ID 1337) 및 테스트용 계정 2개 생성
```bash
npx ganache-cli -a 2 -m "test test test test test test test test test test test junk" --host 0.0.0.0 --port 8545 --networkId 1337
```
#### 2) 기존 빌드 결과 삭제: 재컴파일/재배포를 위해 산출물 폴더 초기화
```bash
rm -rf build
```
#### 3) 스마트 컨트랙트 컴파일: atrifact 생성
```bash
npx truffle compile
```
#### 4) 컨트랙트 배포 (development 네트워크, Ganache)
```bash
npx truffle migrate --network development --reset
```
#### 5) Truffle 콘솔로 배포된 인스턴스 확인
```bash
npx truffle console --network development
```

```bash
winpty docker run -it --name worldland-bcai -p 8546:8545 -p 30303:30303 infonetlab/worldland_bcai

winpty docker run -it --name worldland-bcai   -p 8546:8545   -p 30303:30303  infonetlab/worldland_bcai   --http --http.addr 0.0.0.0 --http.port 8545 --http.api eth,net,web3,personal   --allow-insecure-unlock --unlock 0x78e93bc8bdcbebbc058dedb3ec211a5ce4c44366   --password 1234   console

docker compose up
winpty docker attach worldland-bcai
```

# Integrating WorldLand Private Network with MetaMask and a FastAPI+Gradio DApp

## 1. Setting Up the WorldLand Private Network and Connecting MetaMask
### 1.1. Launch a Local WorldLand Node: You can run a WorldLand (an Ethereum-based) private network locally.
Using Docker (recommended): If a Docker image is provided, run it to quickly start the node. For example:
```bash
docker run -it --name worldland-bcai -p 8545:8545 -p 30303:30303 infonetlab/worldland_bcai
```
This command runs the WorldLand client in a container, exposing JSON-RPC on port 8545 and P2P on 30303. It will drop you into an interactive console (similar to `geth` console). No manual installation needed.

In this example, `250407` is the Chain ID (network ID) for the WorldLand private network. We enabled the HTTP JSON-RPC server on port 8545 and allowed cross-origin requests so that MetaMask (running in a browser) can connect.


### Create an account and mine some WLC (!!Should change this part)
Once the node is running (you should see a `>` prompt for the console), create an account on the private chain and start mining so you have funds for transactions:
```js
personal.newAccount("your_password");    // create a new account
eth.accounts;                            // should list the account address
miner.setEtherbase(eth.accounts[0]);     // set mining rewards to this account
miner.start(1);                          // start mining with 1 thread
miner.stop(); // when stop
docker cp 복사경로workspace/worland-bcai_123~~/keysore~ 도착경로
하고 meta mask에서 json 불러오기

```
You’ll see the node begin to mine blocks. After a few blocks, check your account balance:
```js
eth.getBalance(eth.accounts[0]); 
web3.fromWei(eth.getBalance(eth.accounts[0]), "ether");
```
You should have some WLC (WorldLand’s native currency) to use for gas fees. Keep the miner running so that transactions will be processed on the network.

### 1.2. Configure MetaMask for WorldLand
MetaMask can connect to custom networks. We’ll add the WorldLand private network to MetaMask
1. Install MetaMask in your browser and create a wallet.
2. Add a Custom Network

## 2. Importing and Exporting Accounts between MetaMask and WorldLand
### 2.1. Import a WorldLand Node Account into MetaMask
1. **Locate the keystore file** for your account. If you’re running the node in Docker, the keystore is inside the container. Copy it to your host machine with:
    ```bash
    docker cp worldland-bcai:/workspace/BCAInetwork/keystore ./keystore
    키 저장
    docker cp worldland-bcai:/workspace/worldland-bcai_22222-2222/keystore ./keystore
    키 이외 전부 (코인 저장)
    docker cp worldland-bcai:/workspace/worldland-bcai_22222-2222/worldland ./worldland
    ```
2. **Import into MetaMask**: Open MetaMask and click the account icon (top right), then choose Import Account. Select “JSON File” (instead of private key) as the import method. Choose the JSON file you obtained above and enter the password you used when creating the account on the node.
### 2.2 Export a MetaMask Account to the WorldLand Node
1. Export Private Key from MetaMask: In MetaMask, select the account you want to export. Click the three-dot menu -> Account Details -> Export Private Key.
2. Import into WorldLand node: In the WorldLand geth console, import the raw key using the personal API:
   
    ```js
    web3.personal.importRawKey("YOUR_PRIVATE_KEY_HEX", "a_strong_password");
    eth.accounts;
    ```
    Replace `"YOUR_PRIVATE_KEY_HEX"` (no 0x prefix) with the string from MetaMask.

3. (Optional) Unlock the account: If you plan to use this account for sending transactions from the node console or via JSON-RPC, you’ll need to unlock it

    ```js
    personal.unlockAccount("0xYourImportedAddress", "a_strong_password", 300);
    personal.unlockAccount("0xb81b609e33ff3bcf2f380326af25d85ae51aa281", "1234", 300);
    // you need to type account address not the private key for account
    ```

    (This unlocks the account for 300 seconds so it can be used to send transactions.)

## 3. Sending a Transaction to the Smart Contract via MetaMask
Assume the smart contract MetaDataStoreContract is already deployed on the WorldLand network.

We want to call `storeFileMetadata` from our app, using MetaMask to sign and send the transaction on WorldLand. Here’s how to do it step by step:

### 3.1 Ensure MetaMask is connected to WorldLand
In MetaMask, select the WorldLand-BCAI network and the account you want to use. This account should have WLC balance for gas

### 3.2 Prepare contract details
Your dApp (frontend or backend) needs to know the **contract’s address** and **ABI** to interact with it. The ABI defines the function signatures so that calls can be encoded. For example, the ABI (in JSON) for storeFileMetadata might include an entry like:
```json
{ "name": "storeFileMetadata", "type": "function", "inputs": [ ... ], "stateMutability": "nonpayable" }
```

### 3.3 Use a Web3 library in the frontend
To actually invoke the contract via MetaMask, you typically write frontend code (JavaScript) that uses `window.ethereum` (MetaMask’s provider). You can use ethers.js or web3.js. Below is an example with ethers.js:
- Connect to MetaMask and get a signer: MetaMask injects a window.ethereum object. Using ethers:
  
    ```js
    // Ensure MetaMask is available
    if (window.ethereum) {
    await window.ethereum.request({ method: 'eth_requestAccounts' });
    const provider = new ethers.providers.Web3Provider(window.ethereum);
    const signer = provider.getSigner();
    // signer is now an Ethers.js signer backed by MetaMask (the selected account)
    }
    ```

    This code requests the user’s permission to connect their MetaMask account to the dApp. MetaMask will pop up asking for confirmation to share the account address. After approval, `provider.getSigner()` gives us an account to sign transactions (the first MetaMask account by default).
- Instantiate the contract: With ethers, you can create a contract instance if you have the address and ABI:
    ```js
    const contractAddress = "0xABCD...1234";  // MetaDataStoreContract address on WorldLand
    const contractABI = [
    "function storeFileMetadata(string CID, string fileType, uint256 lastUpdate, bool isDeleted, string userId) public"
    ];
    const contract = new ethers.Contract(contractAddress, contractABI, signer);
    ```
    
    Here we used a human-readable ABI format for brevity. You could also import a JSON ABI array. The signer is attached so that any write operations will be signed by MetaMask.

- Call the function via MetaMask: Now simply call the function on the contract object:
  ```js
    const tx = await contract.storeFileMetadata(
        "Qm...CID...hash",   // CID (e.g., an IPFS hash or similar)
        "pdf",               // fileType
        1687000000,          // lastUpdate timestamp (e.g., Unix time)
        false,               // isDeleted
        "user123"            // userId
    );
    console.log("Transaction sent, hash:", tx.hash);
  ```

  When this code runs, MetaMask will open a prompt for the user to confirm the transaction. The user will see that they are about to call a contract (it may show the contract’s address and the data being sent, unless you have set up MetaMask to recognize the contract’s ABI via interface – in most cases it just says “Contract Interaction”). The user will also see the estimated gas fee for this transaction in WLC (which in a private net is just informational, since the gas is essentially from mining). After the user clicks Confirm, MetaMask will sign the transaction with the user’s private key and transmit it to the WorldLand node.

- Transaction handling: The `contract.storeFileMetadata(...)` call returns a transaction object `tx`. You can get the transaction hash (`tx.hash`) and wait for it to be mined if you want:
  
    ```js
    await tx.wait();  // wait for confirmation
    console.log("Transaction mined in block", tx.blockNumber);
    ```
    (On a private network, mining might be slower if only one node is mining depending on block time. If you have instant mining or very short block times, this will be quick.) You could also retrieve the transaction by hash via the node's RPC or check the contract’s state to confirm the data was stored.

**MetaMask & Gas**: When using MetaMask’s provider with a library like ethers, you typically do not need to manually set gas price or nonce – MetaMask will take care of that. In fact, calling a contract function via MetaMask in ethers is as simple as shown above; MetaMask auto-fills `chainId`, `nonce`, `gasLimit` and `gasPrice` for you when you send the transaction.

## 4. Building a FastAPI + Gradio Frontend Example
We built a simple web application (frontend) that allows a user to input data and trigger the `storeFileMetadata` transaction via MetaMask.