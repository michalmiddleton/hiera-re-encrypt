#!/usr/bin/python
import re
import argparse
import logging
import subprocess

# Collect parameters
parser = argparse.ArgumentParser(description='Re-encrypts Hiera EYAML')
parser.add_argument('--hiera-file', dest='hiera_file', help="Input Hiera YML file", required=True)
parser.add_argument('--pubkey-old', dest='pubkey_old', help="Public key (for decryption)", required=True)
parser.add_argument('--privkey-old', dest='privkey_old', help="Private key (for decryption)", required=True)
parser.add_argument('--pubkey-new', dest='pubkey_new', help="Public key (for encryption)", required=True)
parser.add_argument('--privkey-new', dest='privkey_new', help="Private key (for encryption)", required=True)
parser.add_argument('--eyaml-bin', dest='eyaml_bin', help="EYAML utility", default='/usr/local/bin/eyaml')
parser.add_argument('--log', dest='log', help="Log file", default='reencrypt.log')
args = parser.parse_args()

# Set up logging. debug by default to file and console
logging.basicConfig(filename=args.log, level=logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(console_handler)

# Open original Hiera file
f_in = open(args.hiera_file)
new_file_content = []

# Read line by line and analyze
line = f_in.readline()
while line:
    # Search for ENC[*]
    target = re.search(r'.*?(ENC\[.*?\])', line)
    if target:
        # Line contains ENC[*]
        undecoded = target.group(1)
        logging.debug('LINE: ' + undecoded)
        # Remove the existing enc value and put ENC_PLACE_HOLDER in plcace
        place_holder = re.sub(r'ENC\[.*?\]', 'ENC_PLACE_HOLDER', line)
        # Decode secret
        pdec = subprocess.Popen([args.eyaml_bin, "decrypt", "--pkcs7-public-key", args.pubkey_old, "--pkcs7-private-key", args.privkey_old, "-s", undecoded], stdout=subprocess.PIPE)
        decoded_stdout, decoded_stderr = pdec.communicate()

        if decoded_stderr:
            logging.error("DECODE FAIL:[%s], stderr:[%s]" % (line, decoded_stderr))

        logging.debug('DECODED')
        # Re-encode the secret
        penc = subprocess.Popen([args.eyaml_bin, "encrypt", "-o", "string", "--pkcs7-public-key", args.pubkey_new, "--pkcs7-private-key", args.privkey_new, "-s", decoded_stdout], stdout=subprocess.PIPE)
        encoded_stdout, encoded_stderr = penc.communicate()

        if encoded_stderr:
            logging.error("ENCODE FAIL:[%s], stderr:[%s]" % (line, encoded_stderr))

        # Remove newline char that comes from eyaml utility
        logging.debug('ENCODED\n')
        reencoded_line = re.sub(r'ENC_PLACE_HOLDER', encoded_stdout.rstrip('\n'), place_holder)

        # Finally write it back
        new_file_content.append(reencoded_line)
    else:
        # Line with no encryption. copy back 1:1
        logging.debug('PASS: ' + line)
        new_file_content.append(line)

    # Continue reading the input file
    line = f_in.readline()
f_in.close()

# Write the content back to the hiera file
f_out = open(args.hiera_file, 'w')
f_out.writelines(new_file_content)
f_out.close()
