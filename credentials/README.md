# Credential Tools

Tools for hash identification, password analysis, and wordlist manipulation.

## Tools

| Tool | Language | Description | Requirements |
|---|---|---|---|
| `hash_identifier.py` | Python | Identify hash type by pattern matching | stdlib only |
| `password_strength.py` | Python | Score password strength and estimate crack time | stdlib only |
| `wordlist_utils.sh` | Bash | Deduplicate, sort, filter, and transform wordlists | Unix tools only |

No pip dependencies required for this category.

## Usage

```bash
# Hash identification
python3 hash_identifier.py 5f4dcc3b5aa765d61d8327deb882cf99
python3 hash_identifier.py '$2b$12$...' --all
echo "hash_here" | python3 hash_identifier.py -

# Password strength
python3 password_strength.py "MyP@ssw0rd123"
python3 password_strength.py "hunter2" --verbose
echo "secretpassword" | python3 password_strength.py --stdin
python3 password_strength.py "mypass" --min-score 60 && echo "OK"

# Wordlist utilities
bash wordlist_utils.sh -i rockyou.txt -d -s -l 8:16 -o filtered.txt
bash wordlist_utils.sh -i words.txt -S               # stats only
cat raw.txt | bash wordlist_utils.sh -d -u           # dedup and uppercase
bash wordlist_utils.sh -i list.txt -x "^[0-9]" -m 1000 -o output.txt
bash wordlist_utils.sh -h                            # full help
```
