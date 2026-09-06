/* Page language only. Protocol bytes, inputs, seed words and firmware state stay
 * untouched. English remains the source of each text node so switching language
 * never rebuilds a form, restarts the device, or loses an in-progress tutorial. */
(function (scope) {
  "use strict";
  var KO = {
    "JikKey Simulator": "직키 시뮬레이터",
    "Simulator": "시뮬레이터",
    "Language": "언어 선택",
    "About this simulator": "시뮬레이터 알아보기",
    "About this network": "테스트 네트워크 알아보기",
    "More about this": "자세히 알아보기",
    "Never enter a seed phrase you rely on.": "실제 자산을 보관하는 시드 문구는 입력하지 마세요.",
    "Use a throwaway test seed.": "연습용 시드만 사용해 주세요.",
    "On Mainnet this page holds the real mainnet keys for whatever you give it, with no secure element under them: treat anything typed in as public.": "메인넷에서는 실제 키가 만들어져요. 보안 칩으로 보호되지 않으니, 여기 입력한 시드는 공개된 것으로 생각해 주세요.",
    "Try a SeedSigner in your browser.": "브라우저에서 SeedSigner를 체험해 보세요.",
    "Its Python firmware runs locally with Pyodide. The simulator provides the display, buttons, camera and optional smartcards.": "Pyodide로 Python 펌웨어를 이 브라우저에서 실행해요. 화면, 버튼, 카메라와 스마트카드는 시뮬레이터가 연결해요.",
    "Choose your firmware below the device.": "기기 아래에서 펌웨어를 골라 보세요.",
    "SeedSigner is the original release. ShieldSigner adds SeedKeeper and Satochip support. DoomSigner opens DOOM before the smartcard wallet.": "SeedSigner는 기본 펌웨어예요. ShieldSigner는 SeedKeeper와 Satochip을 지원해요. DoomSigner는 DOOM을 먼저 실행한 뒤 스마트카드 지갑을 열어요.",
    "Display and buttons:": "화면과 버튼",
    "use the device buttons, or the arrow keys, Enter and side keys 1, 2, 3.": "기기의 버튼을 눌러 보세요. 키보드 방향키와 Enter, 측면 버튼에 해당하는 1·2·3 키도 쓸 수 있어요.",
    "Camera:": "카메라",
    "scanning uses your webcam. In the wallet and walkthrough, QR codes pass between the on-page screens without a webcam.": "QR 스캔에는 웹캠을 사용해요. 연습 지갑과 따라 하기에서는 웹캠 없이 화면 사이로 QR 코드를 전달해요.",
    "Smartcards:": "스마트카드",
    "simulated SeedKeeper and Satochip cards respond to the firmware's card commands.": "가상 SeedKeeper와 Satochip 카드가 펌웨어의 카드 명령에 응답해요.",
    "Practice with test coins.": "테스트 코인으로 연습해 보세요.",
    "Bitsaga Signet is a separate Bitcoin test network with a faucet and blocks about every 30 seconds. Its coins have no monetary value.": "Bitsaga Signet은 테스트 코인을 받아 쓸 수 있는 별도의 비트코인 테스트 네트워크예요. 약 30초마다 블록이 생기며, 코인에는 금전적 가치가 없어요.",
    "Keys stay in this browser.": "키는 이 브라우저 안에만 있어요.",
    "The firmware does not access the network. Opening the wallet or starting the walkthrough connects the page to": "펌웨어는 네트워크에 접속하지 않아요. 연습 지갑이나 따라 하기를 열면 페이지가 다음 서버에 연결돼요:",
    "for test coins, address balances, transaction confirmations and broadcasting. Keys, xpubs and descriptors are never sent there.": "테스트 코인 받기, 주소 잔액과 거래 확인, 거래 전송에만 사용해요. 키, xpub, 디스크립터는 서버로 보내지 않아요.",
    "This browser is not a secure wallet.": "이 브라우저는 자산 보관용 지갑이 아니에요.",
    "There is no secure element or air gap. Treat every seed entered here as public. Mainnet derives real mainnet keys and valid signatures, so never use a seed that protects real funds.": "보안 칩이나 네트워크 격리가 없어요. 여기에 입력한 시드는 공개된 것으로 생각해 주세요. 메인넷에서는 실제 키와 유효한 서명이 만들어지므로 실제 자산을 보관하는 시드를 사용하면 안 돼요.",
    "This is a simulator, and it starts on Testnet, so you can use it with": "테스트넷으로 시작하는 시뮬레이터예요. 다음 테스트 네트워크와 함께 연습할 수 있어요:",
    ", my own test network. These are not real bitcoin. They exist only on that test network, cannot be sold or sent to anyone, and are worth nothing.": "의 코인은 실제 비트코인이 아니에요. 이 테스트 네트워크에서만 쓸 수 있고, 판매하거나 다른 사람에게 보낼 수 없어요. 금전적 가치도 없어요.",
    "What is running": "실행 중인 펌웨어",
    "Firmware": "펌웨어",
    "Upstream": "원본 프로젝트",
    "Tag": "릴리스 태그",
    "Commit": "커밋",
    "Interpreter": "실행 환경",
    ", CPython compiled to WebAssembly": ", WebAssembly로 만든 CPython",
    "Each firmware is pinned to the newest release its project has published, by tag and by commit, rather than to a branch. A branch moves and can be rewritten out from under a rebuild; a published tag cannot.": "재현 가능한 빌드를 위해 펌웨어의 릴리스 태그와 커밋을 고정했어요. 아래 정보로 어떤 코드를 실행하는지 확인할 수 있어요.",
    "The wallet zip this page loaded,": "불러온 지갑 ZIP 파일",
    "published sha256": "공개된 SHA-256",
    "what arrived here": "받은 파일의 SHA-256",
    "published contents": "공개된 내용 해시",
    "not loaded yet": "아직 불러오지 않았어요",
    "The zip is hashed as the wallet loads it, so this fills in while the wallet is starting.": "지갑을 시작하며 ZIP 파일의 해시를 확인하고 있어요.",
    "They match: the wallet zip this page loaded is the published build, byte for byte.": "해시가 일치해요. 받은 지갑 ZIP 파일이 공개된 빌드와 같아요.",
    "They differ: the wallet zip this page loaded is not the published build. Do not trust anything this page shows you.": "해시가 달라요. 받은 지갑 ZIP 파일이 공개된 빌드와 일치하지 않아요. 이 페이지의 내용을 신뢰하지 마세요.",
    "The page is checking itself, so this is a convenience and not proof: only rebuilding the zip and comparing the hash is a check that does not depend on this page being honest.": "이 결과는 페이지가 스스로 확인한 값이에요. 독립적으로 검증하려면 ZIP 파일을 직접 빌드한 뒤 해시를 비교해 주세요.",
    "What is in it": "포함된 코드",
    "The upstream tree at the commit above, this repository's stand-ins for the hardware a browser does not have, and these pinned dependencies. Nothing else.": "위 커밋의 원본 코드, 브라우저용 하드웨어 어댑터, 아래 버전으로 고정한 의존성이 들어 있어요.",
    "Check it yourself:": "직접 확인하기:",
    "rebuild the zip": "ZIP 다시 빌드하기",
    "the same rebuild on a clean runner": "독립 환경의 빌드 결과",
    "tests": "테스트",
    "upstream's own tests": "원본 프로젝트 테스트",
    "source": "소스 코드",
    "latest release": "최신 릴리스",
    "device images": "기기 이미지",
    "Running stock SeedSigner 0.8.7, the firmware a plain SeedSigner runs. It has no smartcard support, so there is no card tray.": "기본 펌웨어 SeedSigner 0.8.7을 실행하고 있어요. 스마트카드를 지원하지 않아 카드 트레이는 표시되지 않아요.",
    "Running the 3rdIteration smartcard fork of SeedSigner, tag SeSi-0.8.7+ShSi-B11, which adds SeedKeeper and Satochip cards.": "SeedKeeper와 Satochip을 지원하는 3rdIteration의 펌웨어를 실행하고 있어요. 릴리스는 SeSi-0.8.7+ShSi-B11이에요.",
    "stock, SeedSigner as its own project publishes it, which is what a plain device runs": "stock, SeedSigner 프로젝트의 기본 펌웨어",
    "smartcard, the 3rdIteration fork of SeedSigner, a third party fork that adds SeedKeeper and Satochip cards": "smartcard, SeedKeeper와 Satochip을 추가한 3rdIteration의 외부 포크",
    "Fill the screen": "전체 화면으로 보기",
    "Tap a menu to open it. Swipe up or down to move through the list.": "메뉴를 눌러 열어 보세요. 위아래로 쓸어 목록을 이동할 수 있어요.",
    "Back to the page": "원래 화면으로 돌아가기",
    "starting…": "시작하고 있어요…",
    "Preparing the simulator. This page will refresh once.": "시뮬레이터를 준비하고 있어요. 잠시 후 페이지가 한 번 새로고침돼요.",
    "Open the HTTPS address to run the simulator on your phone.": "휴대폰에서 기기를 실행하려면 HTTPS 주소로 접속해 주세요.",
    "This browser could not start the simulator. Open this page in a regular browser tab and try again.": "시뮬레이터를 시작하지 못했어요. 일반 브라우저 탭에서 다시 열어 주세요.",
    "loading Python…": "실행 환경을 준비하고 있어요…",
    "loading python…": "실행 환경을 준비하고 있어요…",
    "loading libraries…": "필요한 기능을 불러오고 있어요…",
    "unpacking wallet…": "지갑을 준비하고 있어요…",
    "starting wallet…": "지갑을 시작하고 있어요…",
    "loading DOOM…": "DOOM을 불러오고 있어요…",
    "There is no camera on this device, so scanning will not work. Everything else on the simulator will.": "카메라가 없어 QR 코드를 스캔할 수 없어요. 다른 기능은 사용할 수 있어요.",
    "The camera was refused, so scanning will not work. Everything else will. Allow it in the address bar and press Scan again.": "카메라 사용이 허용되지 않았어요. 주소창에서 카메라를 허용한 뒤 ‘Scan’을 다시 눌러 주세요.",
    "Something else on this machine is holding the camera, so scanning will not work. Close it and press Scan again.": "다른 앱이 카메라를 사용하고 있어요. 해당 앱을 닫고 ‘Scan’을 다시 눌러 주세요.",
    "A browser only hands a camera to a secure page, and this one is not, so scanning will not work here.": "보안 연결이 없는 페이지에서는 카메라를 쓸 수 없어요. HTTPS 주소로 열어 주세요.",
    "The camera would not start.": "카메라를 시작하지 못했어요. 사용 권한을 확인하고 다시 시도해 주세요.",
    "the camera stopped": "카메라가 멈췄어요. 다시 연결해 주세요",
    "The camera is not sending any pictures. The device only checks its buttons after it reads one, so it will not answer a press until they start again: close whatever else is using the camera, or reload.": "카메라 영상이 멈춰 기기 버튼도 응답하지 않아요. 카메라를 쓰는 다른 앱을 닫거나 페이지를 새로고침해 주세요.",
    "Testnet": "테스트넷",
    "Mainnet": "메인넷",
    "Regtest": "로컬 테스트넷",
    "The three side buttons open the wallet: press 1, then 2, then 3.": "측면 버튼을 1 → 2 → 3 순서로 누르면 지갑이 열려요.",
    "Everything above is a simulation of": "실제 기기도 만나보세요.",
    "hardware you can buy": "기기 구매하기",
    "this browser will not give the page shared memory, which is what the simulator runs on. Firefox, Chrome, Edge and Safari all will; some privacy browsers turn it off, and that setting is the thing to look for.": "브라우저가 시뮬레이터에 필요한 공유 메모리를 허용하지 않아요. 브라우저 설정을 확인하거나 Firefox, Chrome, Edge, Safari에서 열어 주세요.",
    "this page needs cross-origin isolation and is not getting it. If this is your own copy of the site, it has to send COOP and COEP on every response.": "시뮬레이터 실행에 필요한 사이트 격리 설정이 없어요. 직접 호스팅 중이라면 모든 응답에 COOP와 COEP 헤더를 추가해 주세요.",
    "Card reader empty": "카드를 넣어 주세요",
    "Eject": "카드 꺼내기",
    "IN": "연결됨",
    "blank": "빈 카드",
    "initialised": "설정 완료",
    "seeded": "시드 저장됨",
    "Open wallet": "연습 지갑 열기",
    "Close wallet": "연습 지갑 닫기",
    "Simulator wallet": "연습 지갑",
    "Close the simulator wallet": "연습 지갑 닫기",
    "Close": "닫기",
    "Not connected": "연결 전",
    "Connecting": "연결 중",
    "Connecting to the device.": "기기에 연결하고 있어요.",
    "Not a real wallet. Bitsaga Signet test coins only, no keys, and it forgets everything when you close the tab.": "Bitsaga Signet 테스트 코인으로만 연습해요. 이 지갑 패널에는 키가 없고, 탭을 닫으면 모든 정보가 사라져요.",
    "These are not real bitcoin. They exist only on that test network, cannot be sold or sent to anyone, and are worth nothing.": "실제 비트코인이 아니에요. 이 테스트 네트워크에서만 쓸 수 있으며, 판매하거나 다른 사람에게 보낼 수 없어요. 금전적 가치도 없어요.",
    "These are not real bitcoin. They exist only on our test network, cannot be sold or sent to anyone, and are worth nothing.": "실제 비트코인이 아니에요. 이 테스트 네트워크에서만 쓸 수 있으며, 판매하거나 다른 사람에게 보낼 수 없어요. 금전적 가치도 없어요.",
    "Make a seed on the device.": "기기에서 연습용 시드를 만들어 주세요.",
    "Tools → New seed": "Tools(도구) → New seed(새 시드)",
    "Export its public key.": "시드의 공개키를 내보내 주세요.",
    "Seeds → your seed → Export Xpub → Single sig → Native Segwit": "Seeds → 내 시드 → Export Xpub → Single sig → Native Segwit",
    "Leave that QR on the device's screen. This panel reads it off the screen by itself.": "기기에 QR 코드를 띄워 두면 연습 지갑이 자동으로 읽어요.",
    "Try again": "다시 시도하기",
    "Your first address": "내 첫 번째 주소",
    "Scan it on the device to check it matches.": "기기로 스캔해서 주소가 맞는지 확인해 주세요.",
    "Show it to the device": "기기로 QR 읽기",
    "On the device, go to Scan.": "기기에서 ‘Scan’을 선택해 주세요.",
    "On the device, go to Scan": "기기에서 ‘Scan’을 선택해 주세요",
    "Done": "완료",
    "Get test bitcoin": "테스트 코인 받기",
    "The faucet is empty at the moment. Rob has been told; try again shortly.": "지금은 받을 수 있는 테스트 코인이 없어요. 운영자에게 알려졌으니 잠시 후 다시 시도해 주세요.",
    "The faucet pays test coins on Bitsaga Signet, which is the only place they exist.": "Bitsaga Signet에서만 쓸 수 있는 테스트 코인을 받아요.",
    "Sent": "보냈어요",
    "Received": "받았어요",
    "Receive": "받기",
    "Send": "보내기",
    "Back": "돌아가기",
    "Amount, in sats": "보낼 수량 (sats)",
    "To": "받는 주소",
    "Use one of my addresses": "내 주소 넣기",
    "Create transaction": "거래 만들기",
    "There is nowhere to send it yet. Type an address, or use one of your own.": "받는 주소를 입력하거나 ‘내 주소 넣기’를 눌러 주세요.",
    "There is nobody else on this test network to pay, so paying yourself is the honest demonstration, and it is a real transaction either way: signed, relayed and mined like any other. The button under the field fills it with one of your own receive addresses.": "내 주소로 보내며 거래를 연습해요. 서명부터 전송, 블록 확인까지 실제 절차를 거쳐요. ‘내 주소 넣기’를 누르면 받을 주소가 채워져요.",
    "Show this to your signer.": "이 QR 코드를 기기로 읽어 주세요.",
    "The device's camera is pointed at this canvas, so nothing has to be held anywhere and no webcam is opened.": "기기가 이 화면의 QR 코드를 바로 읽어요. 웹캠은 사용하지 않아요.",
    "One code.": "QR 코드 1개예요.",
    "The device has it. Work through its own review screens and approve it there: what it is showing you is the transaction this panel built.": "기기가 거래를 읽었어요. 기기 화면에서 거래 내용을 확인한 뒤 승인해 주세요.",
    "Reading the signature off the device's screen.": "기기 화면에서 서명을 읽고 있어요.",
    "Sent, mined and confirmed on Bitsaga Signet.": "Bitsaga Signet에 거래를 보냈고 블록에 포함된 것을 확인했어요.",
    "Back to the wallet": "지갑으로 돌아가기",
    "Build the transaction here, in this tab": "이 탭에서 거래를 만들어요",
    "Show it to your signer as a QR code": "기기에 QR 코드로 전달해요",
    "The device reads it and shows what it would sign": "기기에서 서명할 내용을 확인해요",
    "Read the signature back off the device's screen": "기기 화면에서 서명을 읽어요",
    "Finish it here, and hand it to Bitsaga Signet": "거래를 완성해 Bitsaga Signet에 보내요",
    "In a block": "블록에서 확인했어요",
    "Waiting for Bitsaga Signet to put it in a block, about thirty seconds.": "Bitsaga Signet에서 블록에 포함되기를 기다려요. 약 30초 걸려요.",
    "Reading the account key off the device's screen.": "기기 화면에서 계정 공개키를 읽고 있어요.",
    "Asking Bitsaga Signet what those addresses hold.": "Bitsaga Signet에서 주소 잔액을 확인하고 있어요.",
    "That send stopped when the wallet was closed. Nothing was signed or sent. Start it again when you are ready.": "지갑을 닫아 보내기가 멈췄어요. 서명하거나 전송한 내용은 없어요. 준비되면 다시 시작해 주세요.",
    "There is nothing in this wallet to spend.": "보낼 코인이 없어요. 먼저 테스트 코인을 받아 주세요.",
    "There is not enough in this wallet to send that.": "잔액이 부족해요. 보낼 수량을 줄여 주세요.",
    "That address mixes upper and lower case, which no address does.": "주소에 대문자와 소문자가 섞여 있어요. 주소를 다시 확인해 주세요.",
    "Addresses on Bitsaga Signet begin with tb1.": "Bitsaga Signet 주소는 tb1으로 시작해요. 받는 주소를 확인해 주세요.",
    "That address has a character no address can have.": "주소에 쓸 수 없는 문자가 있어요. 주소를 다시 확인해 주세요.",
    "That address does not check out. One character of it is wrong.": "주소가 올바르지 않아요. 빠지거나 잘못 입력한 문자가 없는지 확인해 주세요.",
    "This wallet can only pay segwit v0 addresses.": "이 연습 지갑에서는 Segwit v0 주소로만 보낼 수 있어요.",
    "That is not the right length for a segwit address.": "Segwit 주소의 길이가 맞지 않아요. 주소를 다시 확인해 주세요.",
    "Bitsaga Signet has not put this in a block. It may still turn up.": "아직 블록에서 거래를 찾지 못했어요. 조금 더 기다리면 확인될 수 있어요.",
    "Bitsaga Signet did not answer in time": "Bitsaga Signet의 응답이 늦어지고 있어요. 잠시 후 다시 시도해 주세요",
    "Bitsaga Signet is not reachable from this browser": "Bitsaga Signet에 연결할 수 없어요. 인터넷 연결을 확인해 주세요",
    "Bitsaga Signet answered with something that is not JSON": "Bitsaga Signet 응답을 읽지 못했어요. 잠시 후 다시 시도해 주세요",
    "Bitsaga Signet did not say what these addresses hold": "주소 잔액을 확인하지 못했어요. 잠시 후 다시 시도해 주세요",
    "signet-coordinator.js is not on this page, so there is nothing to ask the chain with.": "네트워크 연결 기능을 불러오지 못했어요. 페이지를 새로고침해 주세요.",
    "wallet-tutorial.js is not on this page, so there is nothing here to split the transaction into codes.": "거래를 QR로 전달할 기능을 불러오지 못했어요. 페이지를 새로고침해 주세요.",
    "that is not an exported account key": "계정 공개키를 읽지 못했어요. 기기에서 ‘Export Xpub’을 다시 실행해 주세요.",
    "there is no account key in that payload": "QR 데이터에 계정 공개키가 없어요. ‘Export Xpub’ 화면인지 확인해 주세요.",
    "that account key does not say which seed it came from": "공개키의 시드 정보를 찾지 못했어요. 기기에서 공개키를 다시 내보내 주세요.",
    "these inputs do not cover that spend": "잔액이 부족해요. 보낼 수량을 줄여 주세요.",
    "these inputs do not cover that spend and its fee": "수수료를 포함하면 잔액이 부족해요. 보낼 수량을 줄여 주세요.",
    "that is not a PSBT": "서명할 거래 데이터를 읽지 못했어요. 거래 QR을 다시 확인해 주세요.",
    "that PSBT does not carry a transaction": "PSBT에 거래 데이터가 없어요. 거래를 다시 만들어 주세요.",
    "the faucet's transaction does not pay this wallet": "테스트 코인 거래의 받는 주소가 이 지갑과 달라요. 거래를 다시 확인해 주세요.",
    "the network gave the transaction a different id": "네트워크에서 받은 거래 ID가 예상한 값과 달라요. 거래를 확인하지 못했어요.",
    "Nothing about the simulator itself has changed.": "시뮬레이터의 현재 상태는 그대로예요.",
    "A 2 of 3 on Bitsaga Signet": "서명 2개로 쓰는 3인 지갑",
    "Start multisig walkthrough": "다중 서명 따라 하기",
    "Play": "자동으로 진행하기",
    "Pause": "잠시 멈추기",
    "Step": "한 단계 진행하기",
    "I will drive": "직접 해보기",
    "Let it drive": "자동으로 진행하기",
    "Start again": "처음부터 다시 하기",
    "Ready": "준비됐어요",
    "the coordinator": "연습 지갑",
    "Show the details": "자세히 보기",
    "Phone → device": "연습 지갑 → 기기",
    "Device → phone": "기기 → 연습 지갑",
    "The scanning is done for you. Nothing here uses your webcam: the device's camera is pointed at the phone's screen and the phone's at the device's, and both screens are on this page.": "QR 코드는 두 화면 사이에서 자동으로 읽어요. 웹캠은 사용하지 않아요.",
    "network": "네트워크",
    "mainnet": "메인넷",
    "Bitsaga Signet, our own Bitcoin test network. Testnet address prefixes, a block every thirty seconds, and a faucet.": "Bitsaga Signet은 테스트넷 주소를 쓰는 별도의 비트코인 테스트 네트워크예요. 약 30초마다 블록이 생기고 테스트 코인을 받을 수 있어요.",
    "Mainnet works here exactly as on hardware, and that is the danger: on Mainnet this page exports the correct mainnet account keys and produces real, valid mainnet signatures, so any seed you type into it should be treated as public. Nothing in this tutorial needs it.": "메인넷에서는 실제 계정 키와 유효한 서명을 만들어요. 여기에 입력한 시드는 공개된 것으로 생각해 주세요. 이 따라 하기에서는 메인넷이 필요하지 않아요.",
    "Bitsaga Signet coordinator": "Bitsaga Signet 연습 지갑",
    "Nothing built yet. Press Play, or take the buttons yourself.": "‘자동으로 진행하기’를 누르거나 직접 기기 버튼을 눌러 시작해 주세요.",
    "Three test seeds go onto three cards, the three public keys come back off them, and those keys make one wallet that needs any two of the three to spend. Then coins from the Bitsaga Signet faucet, and a spend signed twice.": "카드 3장에 연습용 시드를 각각 저장해요. 공개키 3개로 지갑을 만들고, 서명 2개로 테스트 코인을 보내 볼 거예요.",
    "Holding all three keys on one device is fine for a demo and wrong for real funds. The point of multisig is keys in different places and different hands, so that losing one, or someone else finding one, is survivable.": "여기서는 연습을 위해 키 3개를 한 기기에 모아요. 실제 자산을 보관할 때는 키를 서로 다른 장소와 사람에게 나눠 보관해 주세요. 키 하나를 잃거나 누군가 가져가도 자산을 지킬 수 있어요.",
    "The seed is scanned in, written to the card, and then forgotten by the device, so from here on the only copy is on the card. The card is blank, so it asks for a PIN and then takes one twice: that is the card's own ceremony, and it is real here.": "시드를 QR로 읽어 카드에 저장한 뒤 기기에서 지워요. 빈 카드에는 PIN을 새로 만들고 한 번 더 입력해 확인해요.",
    "Press the select button to open Scan.": "선택 버튼을 눌러 ‘Scan’을 열어 주세요.",
    "Press select to open Scan.": "선택 버튼을 눌러 ‘Scan’을 열어 주세요.",
    "The device shows the seed's fingerprint. Select for Done.": "시드의 지문을 확인하고 ‘Done’을 선택해 주세요.",
    "Go down three times to Backup seed, then select.": "아래로 3번 이동해 ‘Backup seed’를 선택해 주세요.",
    "Go down once to To SeedKeeper, then select.": "아래로 1번 이동해 ‘To SeedKeeper’를 선택해 주세요.",
    "The card is asked for its PIN. Press select four times, then the third side button to save.": "선택 버튼을 4번 눌러 연습용 PIN을 입력한 뒤 측면 3번 버튼으로 저장해 주세요.",
    "The card has no PIN yet. Select to give it one.": "아직 PIN이 없어요. 선택 버튼을 눌러 새로 만들어 주세요.",
    "Choose the PIN: select four times, then the third side button.": "선택 버튼을 4번 누른 뒤 측면 3번 버튼을 눌러 PIN을 정해 주세요.",
    "Type it once more to confirm it.": "같은 PIN을 한 번 더 입력해 주세요.",
    "The card is set up. Select to carry on.": "카드 설정을 마쳤어요. 선택 버튼을 눌러 계속해 주세요.",
    "Accept the label the device offers, which is the seed's own fingerprint: the third side button.": "시드 지문을 이름으로 사용할게요. 측면 3번 버튼을 눌러 주세요.",
    "The seed is on the card. Select to finish.": "카드에 시드를 저장했어요. 선택 버튼을 눌러 마쳐 주세요.",
    "Now make the device forget it: down five times to Discard, then select.": "기기에서 시드를 지울게요. 아래로 5번 이동해 ‘Discard’를 선택해 주세요.",
    "Down five times to Discard, then select.": "아래로 5번 이동해 ‘Discard’를 선택해 주세요.",
    "Confirm: down once, then select.": "아래로 1번 이동한 뒤 선택 버튼으로 확인해 주세요.",
    "The card gives the seed back, the device works out the account's public key, and shows it as a QR for the coordinator to photograph. A public key is not a spending key: it can make addresses and check them, and it can do nothing else.": "기기가 카드에서 시드를 읽어 계정 공개키를 만들어요. 연습 지갑이 이 공개키의 QR을 읽어요. 공개키로는 주소를 만들고 확인할 수 있지만 자산을 보낼 수는 없어요.",
    "Press right to Seeds, then select.": "오른쪽으로 이동해 ‘Seeds’를 선택해 주세요.",
    "Down three times to From SeedKeeper, then select.": "아래로 3번 이동해 ‘From SeedKeeper’를 선택해 주세요.",
    "Type the card's PIN: select four times, then the third side button.": "선택 버튼을 4번 눌러 카드 PIN을 입력한 뒤 측면 3번 버튼을 눌러 주세요.",
    "Select the one secret the card is carrying.": "카드에 저장한 시드를 선택해 주세요.",
    "Select for Done.": "‘Done’을 선택해 완료해 주세요.",
    "Down once to Export Xpub, then select.": "아래로 1번 이동해 ‘Export Xpub’을 선택해 주세요.",
    "Down once to Multisig, then select.": "아래로 1번 이동해 ‘Multisig’를 선택해 주세요.",
    "Choose Native Segwit, the first in the list.": "첫 번째 항목인 ‘Native Segwit’을 선택해 주세요.",
    "Down once to Static, so the key comes as one code, then select.": "아래로 1번 이동해 ‘Static’을 선택하면 공개키가 QR 하나로 나와요.",
    "Any button leaves the QR.": "아무 버튼이나 눌러 QR 화면을 닫아 주세요.",
    "Make the device forget the seed: press right to Seeds, then select.": "기기에서 시드를 지울게요. 오른쪽으로 이동해 ‘Seeds’를 선택해 주세요.",
    "Select the loaded seed.": "불러온 시드를 선택해 주세요.",
    "Press left and then select, as many times as it takes, until the device is back on its home screen.": "왼쪽 이동과 선택을 반복해 기기의 홈 화면으로 돌아가 주세요.",
    "The coordinator hands the unfinished transaction to the device, the device shows what it would be signing, and the card's seed signs it. The signature comes back as a QR. One signature is not enough to move anything, which is the point of a 2 of 3.": "연습 지갑이 서명 전 거래를 기기에 전달해요. 기기에서 내용을 확인하고 카드의 시드로 서명하면 결과가 QR로 돌아와요. 이 지갑은 서명 2개가 있어야 보낼 수 있어요.",
    "Type the card's PIN.": "카드의 PIN을 입력해 주세요.",
    "Select the secret on the card.": "카드에 저장한 시드를 선택해 주세요.",
    "The transaction to be signed, split across several codes because one would be too dense to read.": "서명할 거래를 여러 QR 코드로 나눠 전달하고 있어요.",
    "Work through the review screens, pressing select, until the device offers to sign.": "선택 버튼을 눌러 거래 내용을 하나씩 확인하고 서명 화면까지 진행해 주세요.",
    "Approve it.": "내용을 확인했으면 승인해 주세요.",
    "Build the 2 of 3": "서명 2개가 필요한 지갑 만들기",
    "Three public keys make one wallet. Any two of the three can spend from it; any one of them alone can do nothing. The description of that wallet is called a descriptor, and it is not a secret.": "공개키 3개로 지갑 하나를 만들어요. 이 중 2개로 서명해야 보낼 수 있어요. 지갑의 구성을 담은 디스크립터는 비밀 정보가 아니에요.",
    "Building the wallet": "지갑을 만들고 있어요",
    "Sorting three public keys into one 2 of 3 and working out an address to receive at.": "공개키 3개를 묶고 코인을 받을 주소를 만들고 있어요.",
    "2 of 3 wallet": "서명 2개가 필요한 지갑",
    "Tell the device about the wallet": "기기에 지갑 정보 전달하기",
    "The device has only ever seen one key at a time. Giving it the whole descriptor is what lets it recognise its own key in a transaction later, and check that an address really belongs to this wallet.": "디스크립터를 전달하면 기기가 거래 안에서 자신의 키를 알아보고, 주소가 이 지갑에 속하는지도 확인할 수 있어요.",
    "The 2 of 3 descriptor, which names all three keys and says two of them are needed.": "공개키 3개와 서명 2개가 필요하다는 정보를 담은 디스크립터예요.",
    "The device shows the wallet. Select to accept it.": "기기에 표시된 지갑을 확인하고 선택 버튼을 눌러 주세요.",
    "Ask Bitsaga Signet's faucet for coins": "Bitsaga Signet 테스트 코인 받기",
    "Bitsaga Signet is our own Bitcoin test network. It makes a block every thirty seconds, so a confirmation happens while you watch.": "Bitsaga Signet은 별도의 비트코인 테스트 네트워크예요. 약 30초마다 블록이 생겨 거래가 확인되는 과정을 볼 수 있어요.",
    "Asking the faucet": "테스트 코인을 요청하고 있어요",
    "Coins on the way": "코인을 받고 있어요",
    "Waiting for Bitsaga Signet to put it in a block.": "Bitsaga Signet에서 블록에 포함되기를 기다리고 있어요.",
    "Build the spend": "보낼 거래 만들기",
    "A signing device cannot know what a wallet owns or what a fee should be, so the coordinator works that out and hands over an unfinished transaction for the device to sign. This one pays a second address of the same wallet, because there is nobody on this network to pay.": "연습 지갑이 잔액과 수수료를 확인해 서명 전 거래를 만들어요. 이번에는 같은 지갑의 다른 주소로 보내 볼게요.",
    "Building the spend": "거래를 만들고 있어요",
    "One input, one output, and the script that needs two signatures.": "입력과 출력이 하나씩 있고, 서명 2개가 필요한 거래예요.",
    "Unsigned transaction": "서명 전 거래",
    "Put the two signatures together and send it": "서명 2개를 모아 거래 보내기",
    "Neither signature alone moves anything. Together they satisfy the 2 of 3, and the coordinator can finish the transaction and hand it to the network.": "서명 하나만으로는 보낼 수 없어요. 서명 2개를 모으면 연습 지갑이 거래를 완성해 네트워크로 보내요.",
    "Finishing the transaction": "거래를 완성하고 있어요",
    "Two signatures into one witness.": "서명 2개를 거래의 증명 데이터로 모아요.",
    "Broadcast": "네트워크에 보냈어요",
    "Waiting for the spend to be mined.": "거래가 블록에 포함되기를 기다리고 있어요.",
    "Three seeds on three cards, a wallet that none of them can spend from alone, and a transaction that two of them signed and the network accepted.": "카드 3장에 시드를 나눠 저장하고, 서명 2개로 거래를 보냈어요. 네트워크에서도 거래를 확인했어요.",
    "Confirmed": "확인됐어요",
    "Waiting for a block": "블록을 기다리고 있어요",
    "Everything above happened in this tab. The one thing to carry away: all three keys were on one device here, which is fine for a demo and wrong for real funds, where the keys belong in different places and different hands.": "모든 과정을 이 탭에서 체험했어요. 실제 자산을 보관할 때는 키 3개를 한 기기에 모으지 말고, 서로 다른 장소와 사람에게 나눠 보관해 주세요.",
    "This step did not get where it was going. Try it again, or start over.": "이 단계를 마치지 못했어요. 다시 시도하거나 처음부터 시작해 주세요.",
    "This step did not get where it was going. Try it again, or take the buttons yourself.": "이 단계를 마치지 못했어요. 다시 시도하거나 ‘직접 해보기’를 눌러 주세요.",
    "descriptor": "디스크립터",
    "receive address": "받는 주소",
    "witness script": "위트니스 스크립트",
    "faucet transaction": "테스트 코인을 받은 거래",
    "spending": "사용하는 코인",
    "paying": "받는 주소",
    "unsigned PSBT": "서명 전 PSBT",
    "signatures collected": "모은 서명 수",
    "signed transaction": "서명한 거래",
    "transaction id": "거래 ID"
  };

  var language = "ko";
  try {
    var saved = scope.localStorage.getItem("jikkey.language");
    if (saved === "ko" || saved === "en") language = saved;
  } catch (_) { /* Storage may be disabled; a page-local choice still works. */ }
  var asked = new URLSearchParams(scope.location.search).get("lang");
  if (asked === "ko" || asked === "en") language = asked;
  document.documentElement.lang = language;

  function normalized(text) { return String(text).replace(/\s+/g, " ").trim(); }
  var phrases = Object.keys(KO).filter(function (key) { return key.length > 35; })
    .sort(function (a, b) { return b.length - a.length; });

  // Full sentence patterns keep changing counts and public addresses verbatim.
  var rules = [
    [/^Card ([ABC])$/, function (_, card) { return "카드 " + card; }],
    [/^Card ([ABC]) inserted$/, function (_, card) { return "카드 " + card + " 연결됨"; }],
    [/^(\d+) PIN tries left$/, function (_, tries) { return "PIN 입력 기회 " + tries + "번 남음"; }],
    [/^Eject Card ([ABC]) to change its type$/, function (_, card) { return "종류를 바꾸려면 카드 " + card + "를 꺼내 주세요"; }],
    [/^Swap for a (SeedKeeper|Satochip)$/, function (_, kind) { return kind + "으로 바꾸기"; }],
    [/^Bitcoin network: (.+)$/, function (_, network) { return "비트코인 네트워크: " + network; }],
    [/^Code (\d+) of (\d+)\.$/, function (_, have, total) { return "QR 코드 " + total + "개 중 " + have + "개를 읽었어요."; }],
    [/^Working out your addresses, (\d+) of (\d+)\.$/, function (_, have, total) { return "주소 " + total + "개 중 " + have + "개를 만들었어요."; }],
    [/^In block (\d+)$/, function (_, height) { return "블록 " + height + "에서 확인"; }],
    [/^Block (\d+)$/, function (_, height) { return "블록 " + height; }],
    [/^([\d,]+ sats) of it is not in a block yet\.$/, function (_, amount) { return amount + "는 아직 블록에 포함되지 않았어요."; }],
    [/^That is less than the network will relay, which is (\d+) sats\.$/, function (_, amount) { return "최소 " + amount + " sats부터 보낼 수 있어요."; }],
    [/^Asking Bitsaga Signet's faucet to pay (\S+)\.$/, function (_, address) { return "다음 주소로 테스트 코인을 요청하고 있어요: " + address; }],
    [/^Your next unused address\. It belongs to the seed in the device, and the device can prove that to you: it is address (\d+) of the account you exported\.$/, function (_, index) { return "아직 쓰지 않은 내 주소예요. 내보낸 계정의 " + index + "번 주소이며, 기기에서 이 시드의 주소가 맞는지 확인할 수 있어요."; }],
    [/^Put a test seed on Card ([ABC])$/, function (_, card) { return "카드 " + card + "에 연습용 시드 저장하기"; }],
    [/^Read Card ([ABC])'s public key$/, function (_, card) { return "카드 " + card + "의 공개키 읽기"; }],
    [/^Sign with Card ([ABC])$/, function (_, card) { return "카드 " + card + "로 서명하기"; }],
    [/^Click Card ([ABC])(?: in the tray)? to put it in the reader\.$/, function (_, card) { return "트레이의 카드 " + card + "를 눌러 리더기에 넣어 주세요."; }],
    [/^Take Card ([ABC]) (?:back )?out of the reader\.$/, function (_, card) { return "리더기에서 카드 " + card + "를 꺼내 주세요."; }],
    [/^The twelve word test seed for Card ([ABC]), as a SeedQR\.$/, function (_, card) { return "카드 " + card + "에 저장할 12단어 연습용 시드의 SeedQR이에요."; }],
    [/^Card ([ABC])'s account public key, photographed off the device's screen\.$/, function (_, card) { return "기기 화면에서 카드 " + card + "의 계정 공개키를 읽어요."; }],
    [/^The signature from Card ([ABC]), photographed off the device's screen\.$/, function (_, card) { return "기기 화면에서 카드 " + card + "의 서명을 읽어요."; }],
    [/^Card ([ABC]) (test seed|SeedQR payload|account key|signed PSBT)$/, function (_, card, kind) { return "카드 " + card + " " + ({"test seed":"연습용 시드", "SeedQR payload":"SeedQR 데이터", "account key":"계정 공개키", "signed PSBT":"서명한 PSBT"})[kind]; }],
    [/^Keep pressing the select button until the device reaches (\w+)\.$/, function (_, screen) { return "선택 버튼을 눌러 다음 화면까지 진행해 주세요: " + screen; }],
    [/^The wallet is built\. Its address for this run is (\S+)$/, function (_, address) { return "지갑을 만들었어요. 이번에 받을 주소예요: " + address; }],
    [/^(\d+) codes to hold up$/, function (_, total) { return "QR 코드 " + total + "개로 전달해요"; }],
    [/^(?:Sent to|Confirmed on) Bitsaga Signet: (\S+)$/, function (_, txid) { return "Bitsaga Signet 거래: " + txid; }],
    [/^(.+) Code (\d+) of (\d+)\.$/, function (_, caption, have, total) { return translate(caption) + " QR 코드 " + total + "개 중 " + have + "개를 읽었어요."; }],
    [/^DOOM is not available here \((.+)\), so the wallet is starting instead\.$/, function (_, reason) { return "DOOM을 실행할 수 없어 지갑을 열고 있어요. (" + reason + ")"; }],
    [/^(?:failed|Error): (.+)$/i, function (_, error) { return "실행하지 못했어요: " + translate(error); }],
    [/^Bitsaga Signet said (\d+)$/, function (_, status) { return "Bitsaga Signet 요청을 처리하지 못했어요. (" + status + ")"; }],
    [/^(?:Nothing arrived|nothing happened) while waiting for (.+)$/, function (_, what) { return "응답을 기다리다 멈췄어요. 다시 시도해 주세요. (" + what + ")"; }]
  ];

  function translate(source) {
    if (language === "en" || !source) return source;
    var text = normalized(source);
    if (Object.prototype.hasOwnProperty.call(KO, text)) return KO[text];
    for (var i = 0; i < rules.length; i++) {
      if (rules[i][0].test(text)) return text.replace(rules[i][0], rules[i][1]);
    }
    // Paragraphs often combine a specific explanation and the shared warning.
    // Only complete, long source phrases match; seed words cannot be translated.
    var result = text;
    phrases.forEach(function (phrase) {
      if (result.indexOf(phrase) !== -1) result = result.split(phrase).join(KO[phrase]);
    });
    result = result.replace(/^The faucet pays ([\d,]+ sats) at a time, on Bitsaga Signet, which is the only place they exist\./, "$1씩 받아요. Bitsaga Signet에서만 쓸 수 있어요.")
      .replace(/^(\d+) codes, cycling\./, "QR 코드 $1개를 차례로 보여 줘요.")
      .replace(/^The faucet sent ([\d.]+) to the wallet\./, "지갑으로 $1 BTC를 보냈어요.")
      .replace(/^Ready to sign: ([\d.]+) to (\S+), with (\d+) sat of fee\./, "서명할 준비가 됐어요. $2에 $1 BTC를 보내며, 수수료는 $3 sat예요.")
      .replace(/^Confirmed on Bitsaga Signet in block (\d+)\./, "Bitsaga Signet의 블록 $1에서 확인했어요.")
      .replace(/\(receive number (\d+)\)/, "(받는 주소 번호 $1)")
      .replace(/^(the faucet's payment|the spend) confirmed in block$/, function (_, what) { return what === "the spend" ? "보낸 거래가 포함된 블록" : "받은 거래가 포함된 블록"; });
    return result === text ? source : result;
  }

  function t(source, params) {
    var translated = translate(source == null ? "" : String(source));
    return translated.replace(/\{(\w+)\}/g, function (token, key) {
      return params && Object.prototype.hasOwnProperty.call(params, key) ? String(params[key]) : token;
    });
  }

  var texts = new WeakMap();
  var attributes = new WeakMap();
  var observer;
  var skip = "script,style,code,pre,kbd,samp,textarea,input,[translate=no],[data-i18n-skip]";
  function textNode(node) {
    if (!node.parentElement || node.parentElement.closest(skip)) return;
    var previous = texts.get(node);
    var source = previous && node.data === previous.rendered ? previous.source : node.data;
    var translated = t(source);
    // Keep source whitespace around inline elements (links, strong, spans).
    if (translated !== source) {
      translated = (source.match(/^\s*/) || [""])[0] + translated + (source.match(/\s*$/) || [""])[0];
    }
    texts.set(node, {source: source, rendered: translated});
    if (node.data !== translated) node.data = translated;
  }

  function element(node) {
    // Form values are data, but their labels and placeholders are UI copy.
    if (node.matches("script,style,code,pre,kbd,samp") || node.closest("[translate=no],[data-i18n-skip]")) return;
    var previous = attributes.get(node) || {};
    ["title", "aria-label", "placeholder"].forEach(function (name) {
      if (!node.hasAttribute(name)) { delete previous[name]; return; }
      var current = node.getAttribute(name);
      var record = previous[name];
      var source = record && current === record.rendered ? record.source : current;
      var translated = t(source);
      previous[name] = {source: source, rendered: translated};
      if (translated !== current) node.setAttribute(name, translated);
    });
    attributes.set(node, previous);
  }

  function observe() {
    if (observer && document.body) observer.observe(document.body, {
      subtree: true, childList: true, characterData: true,
      attributes: true, attributeFilter: ["title", "aria-label", "placeholder"]
    });
  }

  function refresh() {
    if (!document.body) return;
    if (observer) observer.disconnect();
    var walk = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walk.nextNode())) {
      if (node.nodeType === 3) textNode(node); else element(node);
    }
    document.title = t("JikKey Simulator");
    document.querySelectorAll("[data-language]").forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.language === language));
    });
    observe();
  }

  function setLanguage(next) {
    if (next !== "ko" && next !== "en") return;
    language = next;
    try { scope.localStorage.setItem("jikkey.language", language); } catch (_) {}
    document.documentElement.lang = language;
    // Keep an explicit URL preference in sync without navigating or losing state.
    var url = new URL(scope.location.href);
    if (url.searchParams.has("lang")) {
      url.searchParams.set("lang", language);
      scope.history.replaceState(scope.history.state, "", url.href);
    }
    refresh();
    scope.dispatchEvent(new CustomEvent("jikkey-language-change", {detail: {language: language}}));
  }

  scope.JikKeyI18n = Object.freeze({
    get language() { return language; }, t: t, setLanguage: setLanguage, refresh: refresh
  });

  function start() {
    var switcher = document.getElementById("language-switch");
    if (switcher) {
      switcher.addEventListener("click", function (event) {
        var button = event.target.closest("[data-language]");
        if (button) setLanguage(button.dataset.language);
      });
      // Keep activation keys with the switch. Escape still belongs to the
      // page's fullscreen and popover dismissal even while a language has focus.
      ["keydown", "keyup"].forEach(function (name) {
        switcher.addEventListener(name, function (event) {
          if (event.key !== "Escape") event.stopPropagation();
        });
      });
    }
    observer = new MutationObserver(refresh);
    refresh();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, {once: true});
  else start();
})(window);
