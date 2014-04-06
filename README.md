#Bitcoinista: Simple python bitcoin wallet for iOS#

Bitcoinista is a simple bitcoin wallet with a text-based UI for
spending small amounts of bitcoin on the go. It can run on the desktop
but the main usecase is to run it in the sandboxed python app
[Pythonista](http://omz-software.com/pythonista/) on iOS. Within this
environment Bitcoinista is able to sign transactions and relay them to
the bitcoin network, allowing you to spend your coins on your iPhone
or iPad without your private key ever leaving your device.

Bitcoinista is built on the excellent
[pybitcointools](https://github.com/vbuterin/pybitcointools) library
which is leightweight enough to be run in Pythonista. It also uses
[SlowAES](https://code.google.com/p/slowaes/) which is a pure python
implementation of AES.

##Installation##

To install Bitcoinista on your iOS device, go to installer.py in the
bitcoinista repository, the raw code is here:
[installer.py](https://raw.githubusercontent.com/christianlundkvist/bitcoinista/master/installer.py).

Select all the code and copy it. Go to Pythonista, create a new script
in the Script Library and paste the code in there. Now run it. This
will install bitcoinista, pybitcointools and slowaes.

The main script to run from Pythonista is ```bitcoinista.py``` in the
main script library. If you want a shortcut to bitcoinista on your
home screen you can go
[here](http://omz-software.com/pythonista/shortcut/), write
"bitcoinista" as script name, and then add the page to your
homescreen.

##Usage##

###Creating wallet###

The first time you start Bitcoinista, you will be asked to create a
wallet. The wallet is just a single address/private key pair, and you
can create it in one of three ways:

* Importing your own private key in WIF format.

* Letting Bitcoinista create a random key using ```pybitcointools.random_key()```

* Supplying a brainwallet passphrase if you like using diceware or
  similar system to control your own randomness. We strongly advice
  against using less than 128 bits of entropy for this passphrase.

###Transaction from bitcoin URI###

When scanning a QR code from a merchant the contents of the code looks something like

```
bitcoin:1BMjTvpSzsRYFEutYjx3AnTC49z4Pk8r7i?amount=0.01&label=starbucks
```

You can scan such a QR code and copy the corresponding URI. When
Bitcoinista notices a bitcoin URI in the clipboard a transaction is
automatically created with the above address and amount. All you need
to do is to enter your password and transaction fee and the
transaction is sent.

###Manual transaction###

If no bitcoin URI is in the clipboard Bitcoinista will ask you to
enter the address to send to and the amount you wish to send.

##Features##

* Runs on iOS, no jailbreak needed.

* Unjailbroken iOS security features: App environment is sandboxed,
  all executables signed by Apple, hardware encryption.

* Quickly spend using a scanned QR code.

* Private key encrypted with AES in case your phone is lost or
  stolen. Remember to back up your key!

* Ability to import your own private key

##Limitations##

* Needs paid software: Pythonista is $6.99 in the App Store. Note that
  this author is not affiliated with Pythonista in any way.

* Single address in wallet: No change addresses or BIP32 support.

* Only simple transactions: Unable to send to more than one address at
  a time.

* No GUI: Simple, text-based interface.

* No testnet support at this time, but see Demo Mode below.

##Demo mode##

If you set the flag ```demo_mode=True``` in the script
```bitcoinista.py``` you can run Bitcoinista in demo mode. In this
mode you will always have 0.8 fake coins in your wallet and you can
create transactions. Instead of sending a transaction to the network
Bitcoinista will simply display the inputs and outputs of the
transactions so you can see which unspent outputs are selected, if the
correct amount of change is sent etc.

##Troubleshooting##

The following error

```
An error occurred: maximum recursion depth exceeded in cmp
```

can be resolved in the following way: Hard reboot Pythonista by
double-clicking the home button and swipe up on the Pythonista
screenshot.
