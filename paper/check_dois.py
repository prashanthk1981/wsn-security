import re, urllib.request, json, urllib.error

with open('/home/kp/SpoofingAttack/paper/nkcon_2026_conference_paper.tex', 'r', encoding='utf-8') as f:
    text = f.read()

bib_start = text.find(r'\begin{thebibliography}')
bib_end = text.find(r'\end{thebibliography}')
bib_section = text[bib_start:bib_end]

raw_items = bib_section.split(r'\bibitem{')[1:]

def verify_doi_crossref(doi):
    if not doi:
        return False, 'No DOI string'
    url = f'https://api.crossref.org/works/{doi}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) mailto:researcher@rvce.edu.in'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            title = data['message'].get('title', [''])[0]
            container = data['message'].get('container-title', [''])[0]
            return True, f"VERIFIED: '{title}' in '{container}'"
    except urllib.error.HTTPError as e:
        return False, f'CrossRef Error HTTP {e.code}'
    except Exception as e:
        return False, str(e)

print('=== INDIVIDUAL CROSSREF RESOLUTION CHECK ===')
for idx, item in enumerate(raw_items, 1):
    parts = item.split('}', 1)
    key = parts[0].strip()
    body = parts[1].strip() if len(parts) > 1 else ''
    body_clean = ' '.join(body.split())
    
    doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', body_clean)
    doi = doi_match.group(0).rstrip('.,;)\\\n ') if doi_match else None
    
    ok, msg = verify_doi_crossref(doi)
    print(f'#{idx:02d} [{key}] DOI: {doi}')
    print(f'     Status: {"✅" if ok else "❌"} {msg}')
