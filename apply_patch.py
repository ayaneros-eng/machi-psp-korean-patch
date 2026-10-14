"""Rebuild the reviewed Machi R42 CSO from the exact original Japanese ISO (Python 3.11+)."""
from pathlib import Path
import argparse, array, hashlib, json, mmap, shutil, struct, sys, time, zipfile, zlib

SCHEMA = 'MACHI_ORIGINAL_JP_TO_EXACT_R42_V1'
SOURCE_SHA = '48C5DF78FA7EBDDFB80DBC249BE211DB759678539976B8B45A9D9972A565488F'
TARGET_SHA = '8FEFB36146E179B1A02343448C7A110DCD069413E079AAD9A8BD4CE661A7A650'
def digest(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest().upper()
def require(condition, message):
    if not condition: raise ValueError(message)
def deflate(raw, level=9):
    c = zlib.compressobj(level, zlib.DEFLATED, -15)
    return c.compress(raw) + c.flush()
def rebuild(source, patch, output):
    source, patch, output = (Path(p).resolve() for p in (source, patch, output))
    require(len({source, patch, output}) == 3, 'Input and output paths must differ.')
    require(not output.exists(), 'Output already exists; choose a new filename.')
    require(output.parent.is_dir(), 'Output directory does not exist.')
    with zipfile.ZipFile(patch) as z:
        require(set(z.namelist()) == {'manifest.json', 'modes.bin', 'literals.bin'}, 'Unexpected patch members.')
        m = json.loads(z.read('manifest.json').decode('utf-8'))
        require(m['schema'] == SCHEMA, 'Unsupported patch format.')
        b, t = m['baseline'], m['target']
        require(b['sha256'] == SOURCE_SHA and t['sha256'] == TARGET_SHA, 'Unsupported release identity.')
        require(source.stat().st_size == b['bytes'], 'Original ISO size does not match.')
        require(digest(source) == SOURCE_SHA, 'Original ISO SHA256 does not match.')
        require(t['logical_bytes'] % 2048 == 0, 'Invalid logical size.')
        count = t['logical_bytes'] // 2048
        require(shutil.disk_usage(output.parent).free >= t['bytes'] + 2 * 1024**3, 'Insufficient free space.')
        modes = z.read('modes.bin')
        require(len(modes) == count and hashlib.sha256(modes).hexdigest().upper() == m['modes_sha256'], 'Invalid modes data.')
        header = bytes.fromhex(t['CISO_header_hex'])
        require(struct.unpack('<4sIQIBB2x', header) == (b'CISO', 24, t['logical_bytes'], 2048, 1, 0), 'Invalid CISO header.')
        idx = array.array('I'); counts = [0, 0, 0, 0]; literal_hash = hashlib.sha256()
        started = last = time.monotonic()
        with source.open('rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as src, z.open('literals.bin') as literals, output.open('xb') as dest:
            dest.write(header); dest.write(bytes(4 * (count + 1)))
            for i, mode in enumerate(modes):
                require(mode in (0, 1, 2, 3), 'Invalid block mode.')
                counts[mode] += 1
                if mode != 2:
                    raw = src[i*2048:(i+1)*2048]
                    require(len(raw) == 2048, 'Source block outside original ISO.')
                    flag, payload = (1, raw) if mode == 0 else (0, deflate(raw, 9 if mode == 1 else 1))
                else:
                    record = literals.read(3); require(len(record) == 3, 'Truncated literal header.')
                    literal_hash.update(record); flag, length = struct.unpack('<BH', record)
                    require(flag in (0, 1) and 0 < length <= 2048, 'Invalid literal block.')
                    payload = literals.read(length); require(len(payload) == length, 'Truncated literal payload.')
                    literal_hash.update(payload)
                require((flag == 1 and len(payload) == 2048) or (flag == 0 and 0 < len(payload) < 2048), 'Invalid encoded sector.')
                position = dest.tell(); require(position < 0x80000000, 'CISO offset overflow.')
                idx.append(position | (flag << 31)); dest.write(payload)
                if time.monotonic() - last >= 5:
                    last = time.monotonic()
                    print(json.dumps(dict(event='rebuild',blocks=i+1,total_blocks=count,elapsed_seconds=round(last-started,1))), flush=True)
            require(not literals.read(1), 'Extra literal data.')
            require(counts == m['mode_counts'] and literal_hash.hexdigest().upper() == m['literals_sha256'], 'Literal count/hash mismatch.')
            idx.append(dest.tell()); require(idx[-1] == t['bytes'], 'Physical size mismatch.')
            if sys.byteorder != 'little': idx.byteswap()
            packed = idx.tobytes()
            require(hashlib.sha256(packed).hexdigest().upper() == t['CISO_index_sha256'], 'CISO index mismatch; compression runtime may differ.')
            dest.seek(24); dest.write(packed); dest.flush()
    actual = digest(output); require(actual == TARGET_SHA, 'Output SHA256 mismatch.')
    return dict(status='ORIGINAL_JP_TO_EXACT_R42_REBUILD_PASS',source_sha256=SOURCE_SHA,output=str(output),bytes=output.stat().st_size,sha256=actual,mode_counts=counts,zlib_runtime=zlib.ZLIB_RUNTIME_VERSION,elapsed_seconds=round(time.monotonic()-started,3))
if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True); p.add_argument('--patch',default=str(Path(__file__).with_name('Machi_ORIGINAL_JP_to_R42.patch.zip'))); p.add_argument('--output',required=True)
    a = p.parse_args()
    try: print(json.dumps(rebuild(a.source,a.patch,a.output),indent=2),flush=True)
    except (ValueError, OSError, zipfile.BadZipFile) as e: p.exit(1, f'ERROR: {e}\n')
