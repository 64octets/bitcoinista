import os
import wallet, core
import pybitcointools as bc
import json

class PasswordError(Exception):
    # Exception thrown when wrong password
    # is entered
    pass

class InputError(Exception):
    # Exception thrown when unsupported input
    # is entered
    pass

class LowBalanceError(Exception):
    # Exception thrown when trying
    # to send with not enough funds
    pass

class Model:
    
    def __init__(self, user_mode = 'mainnet'):
        
        self.user_mode = user_mode
        
        if self.user_mode == 'testnet' or self.user_mode == 'demo':
            self.wallet_filename = "bitcoinista_wallet_testnet.json"
            self.magic_byte = 111
        else:
            self.wallet_filename = "bitcoinista_wallet.json"
            self.magic_byte = 0
        
        self.txfee = 10000
        self.txfee_warn_above = 100000
        self.is_wallet_loaded = False
        
        self.demo_unspent = [{'output': '2818b4de824faa41539c4501cc68912e2da07a050b407024c56f8e622cc208c4:1', 'value': 10000000},
               {'output': '58df9f2348323f46706d84e83b31d685e88100e21feab3a6bd91859670199c0a:1', 'value': 50000000},
               {'output': '09604cfd3e2bfdef31e1404c93249023955634cd8686f02adaa7694ca6cafdea:3', 'value': 20000000}
               ]

        self.addr = ''
        self.encr_privkey = ''
        self.unspent = []
        self.balance = 0.0
        
        self.send_amount = 0.0
        self.is_send_amount_set = False
        self.dest_addr = ''
        self.is_dest_addr_set = False
        
    def load_wallet(self):
        
        if not os.path.exists(self.wallet_filename):
            raise OSError('Wallet filename not found')
        
        self.encr_privkey, self.addr = wallet.read_from_wallet_file(self.wallet_filename)
        
        if self.user_mode == 'demo':
            self.unspent = self.demo_unspent
        elif self.user_mode == 'mainnet':
            try:
                self.unspent = bc.unspent(self.addr)
            except:
                try:
                    self.unspent = bc.blockr_unspent(self.addr)
                except:
                    raise IOError('Could not get unspent outputs.')
        elif self.user_mode == 'testnet':
            try:
                self.unspent = bc.blockr_unspent(self.addr, 'testnet')
            except:
                raise IOError('Could not get unspent outputs.')
        else:
            raise Exception('Unsupported user_mode ' + self.user_mode)
        
        self.balance = core.get_balance(self.unspent)
        self.is_wallet_loaded = True
        
        return
        
    def create_wallet(self, method, input, aes_pw):
        privkey = ''
        if method == 'wif':
            fmt = bc.get_privkey_format(input)
            if fmt == 'wif':
                privkey = bc.encode_privkey(input, 'hex')
            elif fmt == 'wif_compressed':
                privkey = bc.encode_privkey(input, 'hex_compressed')
            else:
                raise Exception('Unrecoginized format for private key.')
                
        elif method == 'random':
            privkey = bc.random_key()
        else:
            raise Exception('Unsupported method: {0}.'.format(method))
        
        wal_addr = bc.privtoaddr(privkey, self.magic_byte)
        encr_privkey = wallet.encrypt_privkey(privkey, aes_pw)
        wallet.create_wallet_file(self.wallet_filename, encr_privkey, wal_addr)
        
        # Read back from wallet to ensure consistency
        encr_privkey2, wal_addr2 = wallet.read_from_wallet_file(self.wallet_filename)
        privkey2 = wallet.decrypt_privkey(encr_privkey2, aes_pw)
        
        if encr_privkey2 != encr_privkey or wal_addr2 != wal_addr:
            raise Exception('Inconsistency in reading from/writing to wallet!')

        if privkey2 != privkey:
            raise Exception('Inconsistency in encrypting/decrypting private key!')
        
        return

    def is_wif_privkey_valid(self, privkey):
        try:
            frm = bc.get_privkey_format(privkey)
        except:
            return False
        
        if frm == 'wif' or frm == 'wif_compressed':
            return True
        else:
            return False
    
    def get_wif_privkey(self, pw):
        if not self.is_wallet_loaded:
            raise Exception('Tried getting private key when wallet not loaded.')
            
        prv = ''
        try:
            prv = wallet.decrypt_privkey(self.encr_privkey, pw)
        except:
            raise PasswordError("Wrong password!")

        frm = bc.get_privkey_format(prv)
        if frm == 'hex':
            wif_privkey = bc.encode_privkey(prv, 'wif', self.magic_byte)
        elif frm == 'hex_compressed':
            wif_privkey = bc.encode_privkey(prv, 'wif_compressed', self.magic_byte)
        else:
            raise Exception('Unrecognized private key format: ' + frm)
            
        return wif_privkey
        
    def get_address(self):
        if not self.is_wallet_loaded:
            raise Exception('Tried getting address when wallet not loaded.')

        return self.addr
        
    def get_balance(self):
        if not self.is_wallet_loaded:
            raise Exception('Tried getting balance when wallet not loaded.')
                
        return core.satoshi_to_btc(self.balance)
            
    def get_unspent(self):
        if not self.is_wallet_loaded:
            raise Exception('Tried getting unspent outputs when wallet not loaded.')
            
        return self.unspent
    
    def get_txfee(self):
        return core.satoshi_to_btc(self.txfee)
    
    def parse_bitcoin_uri(self, clipboard_input):
        destination_addr, btc_amount = core.parse_bitcoin_uri(clipboard_input)
        return destination_addr, btc_amount
        
    def set_destination_addr(self, dest_addr):

        is_testnet_or_demo = (self.user_mode=='testnet' or self.user_mode=='demo')
        if not core.is_address_valid(dest_addr, is_testnet_or_demo):
            raise InputError('Destination address {0} is invalid.'.format(dest_addr))

        self.dest_addr = dest_addr
        self.is_dest_addr_set = True
        return
    
    def parse_send_amount(self, input_send_amount, btcusd_spot):
        if '$' in input_send_amount:
            if btcusd_spot <= 0.0:
                raise Exception('Unable to get exchange rate for local currency. Please specify amount in BTC instead.')
            usd_send_amount = float(input_send_amount.replace('$', ''))
            btc_send_amount = (1.0*usd_send_amount) / btcusd_spot
            sat_send_amount = core.btc_to_satoshi(btc_send_amount)
            btc_send_amount = core.satoshi_to_btc(sat_send_amount)
        else:
            btc_send_amount = float(input_send_amount)
            sat_send_amount = core.btc_to_satoshi(btc_send_amount)
            btc_send_amount = core.satoshi_to_btc(sat_send_amount)
            usd_send_amount = btc_send_amount*btcusd_spot
        
        return btc_send_amount, usd_send_amount
    
    def set_send_amount(self, btc_amount):
        
        amount = core.btc_to_satoshi(btc_amount)
        if amount <= 0:
            raise InputError("Amount to send must be strictly positive!")
        
        self.send_amount = amount
        self.is_send_amount_set = True
        return
    
    def set_txfee(self, btc_txfee):
        
        txfee = core.btc_to_satoshi(btc_txfee)
        msg = "OK"
        if txfee < 0:
            raise InputError("Negative transaction fee.")

        if txfee >= self.txfee_warn_above:
            msg = "LARGE"
        if txfee == 0:
            msg = "ZERO"
    
        self.txfee = txfee
        return msg
    
    def is_balance_sufficient(self):
        if not self.is_wallet_loaded:
            raise Exception('Tried to check for balance when wallet not loaded.')

        if not self.is_send_amount_set:
            raise Exception('Tried to check send amount when amount not set.')

        if self.send_amount + self.txfee <= self.balance:
            return True
        else:
            return False

    def sign_tx(self, pw):
        if not self.is_wallet_loaded:
            raise Exception('Tried to spend when wallet not loaded.')

        if not self.is_dest_addr_set:
            raise Exception('Tried to spend when destination address not set.')

        if not self.is_send_amount_set:
            raise Exception('Tried to spend when amount not set.')
        
        if self.send_amount + self.txfee > self.balance:
            raise LowBalanceError("Insufficient funds to send {0} + {1} BTC.".format(core.satoshi_to_btc(self.send_amount), core.satoshi_to_btc(self.txfee)))
            
        try:
            prv = wallet.decrypt_privkey(self.encr_privkey, pw)
            addr = bc.privtoaddr(prv, self.magic_byte)
        except:
            raise PasswordError("Wrong password!")
        
        if addr != self.addr:
            raise Exception('Address from wallet does not match address from private key!')

        tx_ins, tx_outs = core.simple_tx_inputs_outputs(self.addr, self.unspent, self.dest_addr, self.send_amount, self.txfee)
        
        # Make transaction
        tx = bc.mktx(tx_ins, tx_outs)
        
        # Sign transaction
        for i in range(len(tx_ins)):
            tx = bc.sign(tx,i,prv)
        
        return tx_ins, tx_outs, tx, bc.deserialize(tx)
        
    def push_tx(self, tx):
        # Send transaction
        if self.user_mode == 'mainnet':
            try:
                bc.pushtx(tx)
            except:
                try:
                    bc.eligius_pushtx(tx)
                except:
                    raise IOError("Unable to push transaction!")
        elif self.user_mode == 'testnet':
            try:
                bc.blockr_pushtx(tx, 'testnet')
            except:
                raise IOError("Unable to push transaction!")
        else:
            raise Exception("User mode {0} not supported for push_tx.".format(self.user_mode))
            
        return
    
    def get_ephem_pubkey_if_stealth(self, tx_outs):
        
        if 'script' in tx_outs[0]:
            try:
                return bc.ephem_pubkey_from_tx_script(tx_outs[0]['script'])
            except:
                return None
        else:
            return None

    def get_btcusd_spot(self):
        url = 'https://blockchain.info/ticker'
        try:
            data = bc.make_request(url)
        except:
            if self.user_mode == 'demo':
                return 588.0
            else:
                return 0.0
        jsonobj = json.loads(data)
        return float(jsonobj['USD']['15m'])

