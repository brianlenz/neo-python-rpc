"""

Test MainNet JSON-RPC

Setup:

python -m venv venv
source venv/bin/activate
pip install -r requirements_dev.txt
python test.py


"""

from neorpc.Client import RPCClient
from neorpc.Settings import SettingsHolder

from binascii import hexlify
from base58 import b58decode_check

settings = SettingsHolder()
settings.setup_mainnet()
client = RPCClient(settings)

script_bytes = bytes.fromhex('2e25d2127e0240c6deaf35394702feb236d4d7fc')
reversed_bytes = script_bytes[::-1]
nrv_script_hash = hexlify(reversed_bytes)

tests = {}

def register_test(script, expected_result):
    tests[script] = expected_result

# testinvoke 2e25d2127e0240c6deaf35394702feb236d4d7fc totalSupply []
# this incorrectly returns 4,350,400 NRV (0x00c0a9a4aa8b01)
# it should return 12,338,000 NRV (b'\x00P\xb9r"b\x04' or 0x0050b972226204)
#https://neotracker.io/asset/2e25d2127e0240c6deaf35394702feb236d4d7fc
register_test(b'000b746f74616c537570706c7967' + nrv_script_hash, 12338000)

def get_balanceOf_script(addr):
    return b'14' + hexlify(b58decode_check(addr)[1:]) + b'51c10962616c616e63654f6667' + nrv_script_hash

# testinvoke 2e25d2127e0240c6deaf35394702feb236d4d7fc balanceOf ['AcCiYbGqADfcwN9sdacWw9CZuGYdAW3iYy']
# this correctly returns 1,200,000 NRV (b'\x00\x80_\xad#m' or 0x00805fad236d)
#https://neotracker.io/address/AcCiYbGqADfcwN9sdacWw9CZuGYdAW3iYy
register_test(get_balanceOf_script('AcCiYbGqADfcwN9sdacWw9CZuGYdAW3iYy'), 1200000)

# testinvoke 2e25d2127e0240c6deaf35394702feb236d4d7fc balanceOf ['AXnfejvXc7zoWD7reJ8hB3QUQd7jeCpLn1']
# this incorrectly returns nothing (0)
# it should return 160,000 NRV (b'\x00\x00QJ\x8d\x0e' or 0x0000514a8d0e)
#https://neotracker.io/address/AXnfejvXc7zoWD7reJ8hB3QUQd7jeCpLn1
register_test(get_balanceOf_script('AXnfejvXc7zoWD7reJ8hB3QUQd7jeCpLn1'), 160000)

#https://neotracker.io/address/AbURiKqqxJocXQTWLQWYm463Y2hv2MT5oT
register_test(get_balanceOf_script('AbURiKqqxJocXQTWLQWYm463Y2hv2MT5oT'), 320000)
#https://neotracker.io/address/AMtmqc3miofxvdaxBWcnYzzW7tHL8pdcmu
register_test(get_balanceOf_script('AMtmqc3miofxvdaxBWcnYzzW7tHL8pdcmu'), 390800)
#https://neotracker.io/address/APPUZ22aeorSfNQhe5HbiYZ6bShZLot4oW
register_test(get_balanceOf_script('APPUZ22aeorSfNQhe5HbiYZ6bShZLot4oW'), 489600)
#https://neotracker.io/address/AM2LBoV6JXWJz3E9nGDMVCCpxigea595Mg
register_test(get_balanceOf_script('AM2LBoV6JXWJz3E9nGDMVCCpxigea595Mg'), 220000)

for test in tests:
    expected_value = tests[test]
    for endpoint in client.endpoints:
        result = client.invoke_script(test.decode('utf-8'),1234,endpoint)
        if result:
            #print(result)
            value = result['stack'][0]['value']
            # NOTE: NRV has 8 decimals, so dividing by 10^8
            value = (int)(int.from_bytes(bytearray.fromhex(value),"little")/100000000)
            if value != expected_value:
                print('FAIL! expected %d but got %d from %s' % (expected_value, value, endpoint.addr))
            else:
                print('SUCCESS! got %d from %s' % (value, endpoint.addr))

