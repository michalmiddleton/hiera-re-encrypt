
# Hiera re-encrypt utility
This script can be used to rotate keys and re-encrypt whole YAML files.
The file is read line by line and each ENC[...] is decrypted and re-encrypted.

## Limitations
- This utility does NOT work with the whole-file encryption via EYAML. By its definition, those are easy to re-encrypt manually.
- Heredoc/block format of EYAML secrets is not supported. Search your hiera for `: >` string to find them.

## Prerequisites
- Python 2 or 3
- `hiera-eyaml` ruby gem installed (implies compatible Ruby)
- old and new key pairs

## Usage
### One file
```
./Re-encrypt.py --hiera-file yourhiera.yaml \
--pubkey-old old_pubkey.pem --privkey-old old_privkey.pem \
--privkey-new new_pubkey.pem --pubkey-new new_privkey.pem
```

###  Directory of files
```
for YAML in $(ls -1); do echo "Processing $YAML"; python ~/git/Re-encrypt.py --eyaml-bin $(which eyaml) --pubkey-old ~/git/eyaml-keys/qa-public-legacy.pem --privkey-old ~/git/eyaml-keys/qa-private-legacy.pem --privkey-new ~/git/eyaml-keys/qa-private.pem --pubkey-new ~/git/eyaml-keys/qa-public.pem --hiera-file $YAML --log "${YAML}.log"; done
```


### Optional parameters (with defaults)
```
--eyaml-bin     (defaults to '/usr/local/bin/eyaml')
--log           (defaults to 'reencrypt.log')
```

## Output/logging
By default, debug output is both appended to `--log` file and printed on the screen.

Legend:
- `PASS: <text>` are lines with no encrypted values
- `LINE: ENC[...]` are printed for lines containg a secret, outputting the old encrypted value
- `DECODED` is printed when the old secret was successfully decoded
- `ENCODED` is printed when the secret was successfully encrypted with new keys
- `ENCRYPT FAIL:`, `DECRYPT FAIL` is printed when `eyaml` utility returned anything to STDERR. See appended message for more details
