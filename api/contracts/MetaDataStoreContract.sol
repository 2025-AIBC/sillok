// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MetaDataStoreContract {
    struct FileMetadata {
        string CID;
        string fileType;
        uint256 lastUpdate;
        bool isDeleted;
        string userId;
    }

    mapping(string => FileMetadata) public files;  // CID를 키로 하여 파일 메타데이터를 저장

    event FileMetadataStored(string CID, string fileType, uint256 lastUpdate, bool isDeleted, string userId);

    // 메타데이터 저장 함수
    function storeFileMetadata(
        string memory _CID, 
        string memory _fileType, 
        uint256 _lastUpdate, 
        bool _isDeleted, 
        string memory _userId
    ) public {
        files[_CID] = FileMetadata(_CID, _fileType, _lastUpdate, _isDeleted, _userId);
        emit FileMetadataStored(_CID, _fileType, _lastUpdate, _isDeleted, _userId);
    }

    // 파일 메타데이터 조회 함수
    function getFileMetadata(string memory _CID) public view returns (
        string memory CID, 
        string memory fileType, 
        uint256 lastUpdate, 
        bool isDeleted, 
        string memory userId
    ) {
        FileMetadata storage file = files[_CID];
        return (file.CID, file.fileType, file.lastUpdate, file.isDeleted, file.userId);
    }
}
