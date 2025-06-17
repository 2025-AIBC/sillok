const MetaDataStoreContract = artifacts.require("MetaDataStoreContract"); // build/contracts/... 내부의 json파일들

module.exports = async function (deployer, network, accounts) {
    const deployedContract = await MetaDataStoreContract.deployed().catch(
        () => null
    );

    if (!deployedContract) {
        console.log("Deploying contract...");
        await deployer.deploy(MetaDataStoreContract);
        const instance = await MetaDataStoreContract.deployed();
        console.log(`Contract deployed at address: ${instance.address}`);
    } else {
        console.log(
            `Contract already deployed at address: ${deployedContract.address}`
        );
    }
};
