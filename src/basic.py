import random

############ implemention by TPM ############

def createRandomString():
    return str(random.randint(0,99999999))

def createUniqueDID():
    return "did:"+createRandomString()

def generateKeyPair(privateKeysFile):
    publicKey = "#publicKey-1"
    privateKey = "#privateKey-1"

    # write private key into TPM
    with open(privateKeysFile, "w") as outfile:
        outfile.write(privateKey)

    return publicKey

def signVC(s):
    return "signed_"+s

def encrypt(s, key):
    return "encrypt"+s

def decrypt(s, key):
    return "decrypt"+s