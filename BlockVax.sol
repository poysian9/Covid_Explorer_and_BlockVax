pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/drafts/Counters.sol";


contract blockVax is ERC721Full {

    // Addresses of Providers
    address public provider1 = 0x82D270F2444C7946A6bb8373c50F46795b849548;
    address public provider2 = 0x162AFB7A9d4cD1Cfda18337a0EAb2a4ECFD73C3d;
    // Names of Vaccines
    string name1 = 'Pfizer';
    string name2 = 'AstraZeneca';
    string success = "Is vaccinated";
    string fail = "Is not vaccinated";
    
    // Constructing token name and symbol
    constructor() ERC721Full("BlockVax", "VAX") public {}
    
    using Counters for Counters.Counter;
    Counters.Counter tokenIDs;

    struct Patient {
        uint patientID;
        address addy;
        string photoURI;
    }

    struct Provider {
        address addy;
        string vaccineName;
    }

    struct Vaccination {
        Patient patient;
        Provider provider;
    }
    // Mapping to register patient and vaccine info
    mapping (uint => Vaccination) vaccinations;

    // Mapping to check which registered patients have been vaccined and with what vaccine
    mapping (address => string )  status;

    // Array to keep track of number of entries
    uint[] array;

    // Modifier that ensures only registed providers can use the registerProvider function with checks on vaccine name and patient ID
    modifier onlyRegisteredProvider(string memory vaxName, uint patientId) {
        require(msg.sender == provider1 || msg.sender == provider2, 'Only registered providers may update this info.');
        require(keccak256(bytes(vaxName)) == keccak256(bytes(name1)) || 
            keccak256(bytes(vaxName)) == keccak256(bytes(name2)), 'Please provide the correct vaccine name');
        require(patientId > 0 && patientId <= array.length, 'Please enter a correct patient ID number.');
        _;
    }
    
    // Modifier that checks if inputed details are correct when quereing which patients are vaccinated
    modifier correctDetails(address addr, uint patientId, string memory vaxName) {
        require(addr != address(0), 'Please enter a correct address.');
        require(patientId > 0 && patientId <= array.length, 'Please enter a correct patient ID number.');
        require(keccak256(bytes(vaxName)) == keccak256(bytes(name1)) || 
            keccak256(bytes(vaxName)) == keccak256(bytes(name2)), 'Please provide the correct vaccine name');        
        require(vaccinations[patientId].patient.addy == addr, 'The address you are looking for is not registered.');
        _;
    }
    
    // Function that allows someone to register themselves or others onto the blockchain with an attached (hashed) photo ID
    function registerPatient (address addr, string memory photo_uri) public returns (uint) 
    {
        require(addr != address(0), 'Please enter a correct address.');

        tokenIDs.increment();
        uint tokenID = tokenIDs.current();
        array.push(tokenID);

        vaccinations[tokenID].patient.patientID = tokenID;
        vaccinations[tokenID].patient.addy = addr;
        vaccinations[tokenID].patient.photoURI = photo_uri;

        return tokenID;
    }

    // Function that allows only registered providers to add vaccine details to registered patients, minting a personalized token
    function registerProvider (address addr, uint patientId, string memory vaxName, string memory photo_uri) 
        public 
        onlyRegisteredProvider (vaxName, patientId)
    {
        vaccinations[patientId].provider.addy = msg.sender;
        vaccinations[patientId].provider.vaccineName = vaxName;
        status[addr] = vaxName;

        _mint(addr, patientId);
        _setTokenURI(patientId, photo_uri);
    }

    // Function that checks if registered patients have been vaccinated with either vaccine
    // function isVaccinated (address addr, uint patientId, string memory vaxName) 
    //     public
    //     correctDetails (addr, patientId, vaxName)
    //     returns (string memory) 
    // {
    //     if (status[addr] = vaxName) {
    //         return success;
    //     }

    //     else return fail;
    // }
}
