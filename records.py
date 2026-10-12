# WVLottopy records: keeps the excel history files growing as draws happen
# wvlottery.com only keeps ~3 years of results (Cash Pop one year), so every run appends any draw that is
# not in the sheet yet. Nothing is ever removed or rewritten, existing rows stay exactly as they are.
import fcntl
import os
import shutil
from collections import Counter

import pandas as pd


def draw_day(x):
    # the site's drawingDate is the UTC date, so late evening draws (powerball, mega millions, lotto america at ~11pm ET)
    # come out a day late. The real draw day is drawDate converted to Eastern time.
    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        t = datetime.fromisoformat(str(x['drawDate']).replace('Z', '+00:00'))
        return t.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d')
    except Exception:
        return x['drawingDate']


def _fmt_date(d):
    # site gives 2026-10-09, the sheets use 10/09/2026
    s = str(d)[:10]
    if len(s) == 10 and s[4] == '-':
        return f'{s[5:7]}/{s[8:10]}/{s[0:4]}'
    return s


def _fmt_nums(n):
    # site numbers come split by an en dash, the sheets use a hyphen
    return str(n).replace('–', '-').strip()


def _newer_first(df):
    # some sheets are oldest first, some newest first
    d = pd.to_datetime(df['Date'], errors='coerce').dropna()
    return len(d) > 1 and d.iloc[0] > d.iloc[-1]


def merge_save(path, web_df, fallback=None, ids=None, times=None):
    # recording must never break the forecast: if anything goes wrong the old behaviour (site + sheet) is used
    try:
        return _merge_save(path, web_df, ids, times)
    except Exception as e:
        print(f'records: could not update {os.path.basename(path)}: {e!r}')
        if fallback is not None:
            return pd.concat([web_df, fallback], ignore_index=True)
        return None


def _merge_save(path, web_df, ids=None, times=None):
    """Append draws from the site (web_df: Date, Numbers[, bonus col]) that the sheet at path does not have yet.
    ids: optional list of site draw ids, same length as web_df. Returns the whole sheet as Date/Numbers/[bonus]
    so callers can keep counting from one source. If the site gave nothing the sheet is left alone."""
    bonus = [c for c in web_df.columns if c not in ('Date', 'Numbers')]
    if os.path.exists(path):
        old = pd.read_excel(path)
    else:
        old = pd.DataFrame(columns=['Unnamed: 0', 'Date', 'Numbers'] + bonus)
    if len(web_df) == 0:
        return old[['Date', 'Numbers'] + bonus].copy()

    web = web_df.copy()
    web['Date'] = web['Date'].map(_fmt_date)
    web['Numbers'] = web['Numbers'].map(_fmt_nums)
    if ids is not None:
        web['DrawID'] = [str(i) for i in ids]
    if times is not None:
        web['DrawTime'] = [str(t) for t in times]

    def key(r):
        return (str(r['Date']), _fmt_nums(r['Numbers'])) + tuple(str(int(r[c])) if str(r[c]) not in ('nan', 'None', '') else '' for c in bonus)

    have_ids = set(old['DrawID'].dropna().astype(str)) if 'DrawID' in old.columns else set()
    # Rows that carry a draw id are matched by id only. The Date+Numbers match is just for old rows without an id:
    # cash pop draws one number out of 15 about 90 times a day, so other draws on the same day share Date+Numbers.
    no_id = old['DrawID'].isna() if 'DrawID' in old.columns else pd.Series(True, index=old.index)
    have = Counter(key(r) for _, r in old[no_id].iterrows())
    keep = []
    for _, r in web.iterrows():
        if 'DrawID' in web.columns and str(r['DrawID']) in have_ids:
            continue
        k = key(r)
        if have[k] > 0:
            have[k] -= 1
            continue
        keep.append(r)
    new = pd.DataFrame(keep, columns=web.columns)

    if len(new):
        lock = open(os.path.join(os.path.dirname(path) or '.', '.' + os.path.basename(path) + '.lock'), 'w')
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            backup = path + '.pre-recording'
            if os.path.exists(path) and not os.path.exists(backup):
                shutil.copy2(path, backup)
            new['_d'] = pd.to_datetime(new['Date'], errors='coerce')
            desc = _newer_first(old) if len(old) else True
            new = new.sort_values('_d', ascending=not desc, kind='stable').drop(columns='_d')
            start = int(pd.to_numeric(old['Unnamed: 0'], errors='coerce').max() + 1) if len(old) and 'Unnamed: 0' in old.columns else 0
            new.insert(0, 'Unnamed: 0', range(start, start + len(new)))
            full = pd.concat([new, old], ignore_index=True) if desc else pd.concat([old, new], ignore_index=True)
            tmp = path[:-5] + '.tmp.xlsx'
            full.to_excel(tmp, index=False, engine='openpyxl')
            os.replace(tmp, path)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
            lock.close()
        print(f'records: {os.path.basename(path)} +{len(new)} new draws')
    else:
        full = old
    out = full[['Date', 'Numbers'] + bonus].copy()
    return out
