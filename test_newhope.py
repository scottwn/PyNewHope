import newhope
import sys
console = sys.stdout
sys.stdout = open('poly_log.txt', 'w')
alice_message = newhope.keygen(True)
bob_message = newhope.sharedb(alice_message)
newhope.shareda(bob_message)
sys.stdout.close()
sys.stdout = console
print("Alice's message is " + str(alice_message) + '\n\n')
print("Bob's message is " + str(bob_message) + '\n\n')
print("Alice's key is ")
print(str(newhope.a_key))
print("Bob's key is ")
print(str(newhope.b_key))
if newhope.a_key == newhope.b_key:
    print("Successful handshake! Keys match.")
else:
    print("Error! Keys do not match.")
