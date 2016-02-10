# set this to the full path to the dashvend respository checkout
DASHVEND_DIR = '/home/pi/dashvend'
# note: also update paths in:
#   bin/.init.d.dashvend
#   bin/_dashvend_control.sh
#   bin/dashvend_screens.screenrc
#   bin/show_screen_number.sh

# after testing, set this to True to use mainnet
MAINNET = False

# **public** mainnet bip32 seed for vending address generation
BIP32_MAINNET_SEED = 'drkpRxPP5eefb7GqpdDSQKGPjJHHuBqPJJVD2Qx4BHF7CVP1dC8uVxVy6JfDQsn1U1EazDZPa4DWMsmV7pDhMtLTQQypHHc6cFnPPYZvwib5nVi'  # noqa
# on a secure machine, generate above with pycoin 'ku' command.
# for testing, ku is already installed on this machine during the 'make'
# install pycoin by doing:
# git clone https://github.com/richardkiss/pycoin.git
# cd pycoin ; sudo python setup.py install
# ku -n DASH -s 0p/0 P:<a unique, unpublished 100 character long sentence>
# and use the **public version** output
# for sane passphrase selection see: https://masternode.me/smart_passwords.html

# **public** testnet bip32 seed for vending address generation
BIP32_TESTNET_SEED = 'DRKPuUbaZSQn2SV5vyTh9DRHcooktYP3TB3NQa8cgMGXxT8znzH5opFtDgY8PVTKzTohyEfitf1TkcxnygJdY7ACJxvbVTvSVn6q6gCEVfydtJ6y'  # noqa
# ku -n tDASH -s 0p/0 P:<a unique, unpublished 100 character long sentence>

# require seven (out of ten) masternode locks to accept purchase
IX_LOCK_TRESHOLD = 7
# note: sometimes all ten locks do not fully propagate across the network,
# settings above 9 are not recommended.

# dash value required to trigger sale
VENDING_COST = 0.01
