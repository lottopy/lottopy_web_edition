# WVLottopy: Matteo DiBiagio
# wvlottery.com only keeps about 3 years of results (cash pop only 1) so this adds every new draw
# to the excel sheets each run, that way the records keep growing instead of getting lost again.
# Nothing already in the sheets gets changed or removed.
import fcntl
import os
import shutil
from collections import Counter

import pandas as pd


def draw_day(x):
    # drawingDate from the site is in UTC so the late draws (powerball, megamillions, lotto america)
    # show up a day late, converting drawDate to eastern time gives the real day
    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        t = datetime.fromisoformat(str(x['drawDate']).replace('Z', '+00:00'))
        return t.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d')
    except Exception:
        return x['drawingDate']


def _fmt_date(d):
    # site dates are 2026-10-09, the sheets use 10/09/2026
    s = str(d)[:10]
    if len(s) == 10 and s[4] == '-':
        return f'{s[5:7]}/{s[8:10]}/{s[0:4]}'
    return s


def _fmt_nums(n):
    # site splits numbers with – and the sheets use -
    return str(n).replace('–', '-').strip()


def _newer_first(df):
    # some of the sheets are newest first and some are oldest first
    d = pd.to_datetime(df['Date'], errors='coerce').dropna()
    return len(d) > 1 and d.iloc[0] > d.iloc[-1]


def merge_save(path, web_df, fallback=None, ids=None, times=None):
    # if saving fails for whatever reason just use the site + old sheet so the numbers still come out
    try:
        return _merge_save(path, web_df, ids, times)
    except Exception as e:
        print(f'records: could not update {os.path.basename(path)}: {e!r}')
        if fallback is not None:
            return pd.concat([web_df, fallback], ignore_index=True)
        return None


def _merge_save(path, web_df, ids=None, times=None):
    # web_df is Date, Numbers and the bonus ball column if the game has one
    # ids is the site's draw id for each row (cash pop needs it), returns the whole sheet
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

    # rows with a draw id get matched by the id, date + numbers is only for the old rows without one
    # (cash pop draws 1 number out of 15 like 90 times a day so the same date + number happens a lot)
    have_ids = set(old['DrawID'].dropna().astype(str)) if 'DrawID' in old.columns else set()
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
            # one time backup of the sheet before it ever gets added to
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
    return full[['Date', 'Numbers'] + bonus].copy()
