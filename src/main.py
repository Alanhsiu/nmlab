from item import Item
from owner import Owner
from vc import VC_transfer 
from vc import VC_revoke

##### DID initialization: everyone has a TPM to generate its DID #####
A_factory = "did:A_factory"
B_factory = "did:B_factory"
C_factory = "did:C_factory"
D_factory = "did:D_factory"
E_contractor = "did:E_contractor"
F_Army = "did:F_Army"
G_MinistryOfDefense = "did:G_MinistryOfDefense"
H_DefenseIndustrialBase = "did:H_DefenseIndustrialBase"
A = Owner(A_factory)
B = Owner(B_factory)
C = Owner(C_factory)
D = Owner(D_factory)
E = Owner(E_contractor)
F = Owner(F_Army)
G = Owner(G_MinistryOfDefense)
H = Owner(H_DefenseIndustrialBase)


##### Step 1: create new items #####
barrel = Item(A.did) # 槍管
gunstock = Item(B.did) # 槍托
magazine = Item(C.did) # 彈匣


##### Step 2-1: A transfer item to D #####
issuer = "did:A_factory"
verifier = "did:D_factory"
holder = "did:A_factory"
item_did = barrel.id
action = "Ownership_transfer"
vc1 = VC_transfer(issuer, verifier, holder, item_did)
# vc4 = VC_revoke(issuer, verifier, holder, item_did)
