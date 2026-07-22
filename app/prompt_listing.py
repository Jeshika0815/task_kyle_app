import re
import json
from dataclasses import asdict, dataclass, field
from typing import Optional

# define dataclass
@dataclass
class Plans:
    plan_name: Optional[str] = None
    date: dict = field(default_factory=lambda: {"start_date": None, "finish_date": None})
    time: dict = field(default_factory=lambda: {"start_time": None, "finish_time": None})
    alarm: bool = False
    repeats: Optional[str] = None
    tags: list = field(default_factory=list)
    location: Optional[str] = None
    url: Optional[str] = None
    memo: Optional[str] = None

# define patterns
datep = re.compile(r'\d{4}[/-]\d{1,2}[/-]\d{1,2}')
timep = re.compile(r'\d{1,2}:\d{1,2}')
tagsp = re.compile(r'#[A-Za-z0-9_]+')
alarmp = re.compile(r'通知(?:あり|有り|アリ|True)?')
repeatp = re.compile(r'(毎日|毎週|毎月|毎年|平日|繰り返し|\d+日|\d+週|\d+月|\d+年)')
addrsp = re.compile(r'(?:東京都|北海道|(?:大阪|京都)府|[^\s]{2,3}県)[^\s]*')
urlp = re.compile(r'http[s]?://\S+')

# main process
def p_listing(prompt: str):
    analyze_result = char_analyze(prompt)
    output = output_result(analyze_result)
    plans = json.dumps(asdict(output), ensure_ascii=False)
    return plans

# Char Analyze
def char_analyze(pmpt: str) -> dict:
    text = pmpt.strip()

    date_list = datep.findall(text)
    time_list = timep.findall(text)
    tags = tagsp.findall(text)
    alarm = bool(alarmp.search(text))
    repm = repeatp.search(text)
    repeat = repm.group(1) if repm else None
    adrm = addrsp.search(text)
    location = adrm.group(0) if adrm else None
    urls = urlp.findall(text)

    left_over = text
    for pt in (datep, timep, tagsp, alarmp, repeatp, addrsp, urlp):
        left_over = pt.sub('', left_over)
    chunks = [c for c in left_over.split() if c]

    plan_name = chunks[0] if chunks else None
    memo = ' '.join(chunks[1:]) if len(chunks) > 1 else None

    def _normalize_range(lst, start_key, finish_key):
        if not lst:
            return {start_key: None, finish_key: None}
        if len(lst) == 1:
            return {start_key: lst[0], finish_key: None}
        return {start_key: lst[0], finish_key: lst[1]}

    date = _normalize_range(date_list, 'start_date', 'finish_date')
    time = _normalize_range(time_list, 'start_time', 'finish_time')

    return {
        "plan_name": plan_name,
        "date": date,
        "time": time,
        "tags": tags,
        "alarm": alarm,
        "repeat": repeat,
        "location": location,
        "urls": urls,
        "memo": memo
    }

def output_result(prmpt: dict) -> Plans:

    return Plans(
        plan_name = prmpt.get("plan_name"),
        date = {"start_date": prmpt["date"]["start_date"], "finish_date": prmpt["date"]["finish_date"]},
        time = {"start_time": prmpt["time"]["start_time"], "finish_time": prmpt["time"]["finish_time"]},
        alarm = prmpt.get("alarm", False),
        repeats = prmpt.get("repeat"),
        tags = prmpt.get("tags", []),
        location = prmpt.get("location"),
        url = prmpt.get("urls"),
        memo = prmpt.get("memo")
    )


# For testing
"""
def test():
    dataset = [
        "やること 2026/08/15 09:00 東京都渋谷区宇田川町XX-YY-ZZ アラーム付き 今日は私の誕生日です",
        "出張 2026/09/01 2026/09/03 10:00 18:00 毎週 #仕事 #大阪 大阪府大阪市北区 議事録を忘れずに",
        "ジム 19:00 20:00 毎日 #健康 軽めのメニューで",
        "買い物 2026/08/20",
    ]
    for prompt in dataset:
        result = p_listing(prompt)
        print(result)

if __name__ == "__main__":
    test()
"""
