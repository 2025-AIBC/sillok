module.exports = {
    networks: {
        development: {
            host: "0.0.0.0", // Ganache가 실행되는 호스트 주소 (Docker에서 내부적으로 0.0.0.0 사용)
            port: 8545, // Ganache 기본 포트
            network_id: "1337", // Ganache 네트워크 ID (docker-compose.yml의 설정과 일치해야 함)
        },
        worldland: {
            host: "127.0.0.1",
            port: 8546,
            network_id: "250407",      // WorldLand 체인 ID
            from: "0xb81b609e33ff3bcf2f380326af25d85ae51aa281",
            gas: 2000000,
        },           
    },
    compilers: {
        solc: {
            version: "0.8.0", // 사용할 Solidity 버전
        },
    },
};
