from dataclasses import dataclass
from datetime import datetime

_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_months_to_numbers = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}
_numbers_to_months = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

_id = 0

class _quote:      
                                                # year, month,       day
    def __init__(self, content: str, date: tuple[int, int | None, int | None] | tuple[int] | None = None, origin: str = "Jordi A. Navarrette"):
        global _id
        self.content = content
        self.date: tuple[int, int | None, int | None] = date if date is not None and len(date) == 2 else (0, None, None)
        self.origin = origin
        self.id = _id
        _id += 1

    def __str__(self) -> str:
        datestr = f"{_months[self.date[1] - 1] if len(self.date) > 1 and self.date[1] is not None else "n.d.,"}{f" {self.date[2]}," if len(self.date) > 2 and self.date[2] is not None else ''} {self.date[0]}"
        return f'{self.content} -- {self.origin}, {datestr}'

def extract(filename: str = "./Jordi's Famous Quotes.txt") -> list[_quote]:
    quotes = "[Extraction Error]"
    with open(filename, 'r', encoding='utf-8') as f:
        quotes = f.read()
    quotelist: list[_quote] = []
    year = 2022
    month = None
    day = None
    # print(f"Raw quotes: {quotes}")
    for q in quotes.split("\n\n"):
        if q.startswith("20"):
            year = int(q)
            month = "Jan"
            day = 1
        if any(q.startswith(k) for k in _months):
            month = q[0:3]
            day = int(q[4:6])
        if any(q.startswith(k) for k in ("S: ", '"', "[")):
            quotelist.append(_quote(q, (year, _months_to_numbers[month] if month is not None else None, day)))
        # print(f"Year: {year}, Month: {month}, Day: {day}")
    return quotelist
    

def test():
    q1 = _quote("Jess!", (2025, 9, 1))
    q2 = _quote("Kashun!", (2023, None, None))
    q3 = _quote("Jeses")
    print(q1)
    print(q2)
    print(q3)

quote_list = extract()