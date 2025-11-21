from dataclasses import dataclass
from datetime import datetime
import json

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

def _string_to_tuple_manual(s: str) -> tuple:
    """Manual parsing by stripping parentheses and splitting"""
    # Remove parentheses and strip whitespace
    content = s.strip()[1:-1]
    # Split by comma and convert to appropriate types
    elements = []
    for item in content.split(','):
        item = item.strip()
        # Try to convert to int, then float, otherwise keep as string
        try:
            elements.append(int(item))
        except ValueError:
            try:
                elements.append(float(item))
            except ValueError:
                elements.append(item)
    return tuple(elements)

_origin = "Jordi A. Navarrette"

class _quote:      
                                                # year, month,       day
    def __init__(self, content: str, date: tuple[int, int | None, int | None] | tuple[int] | None = None, origin: str = _origin):
        global _id
        self.content = content
        self.date: tuple[int, int | None, int | None] = date if date is not None and len(date) == 3 else (0, None, None)
        self.origin = origin
        self.id = _id
        _id += 1

    def __str__(self) -> str:
        datestr = f"{_months[self.date[1] - 1] if len(self.date) > 1 and self.date[1] is not None else "n.d."}{f", {self.date[2]}, " if len(self.date) > 2 and self.date[2] is not None else ''}{self.date[0] if self.date[0] != 0 else ""}"
        return f'{self.content} -- {self.origin}, {datestr}'

    def encode(self) -> str:
        """Convert the _quote object to a JSON string"""
        quote_dict = {
            'content': self.content,
            'date': self.date,
            'origin': self.origin,
            'id': self.id
        }
        return json.dumps(quote_dict)

    @classmethod
    def decode(cls, json_str: str) -> '_quote':
        """Create a _quote object from a JSON string"""
        data = json.loads(json_str)
        
        # Convert date list back to tuple
        date_data = data.get('date', (0, None, None))
        if isinstance(date_data, list):
            date_data = tuple(date_data)
        
        # Create new _quote instance
        quote = cls(
            content=data['content'],
            date=date_data,
            origin=data.get('origin', 'Unknown')
        )
        
        # Restore the original ID
        quote.id = data['id']
        
        return quote

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
            quotelist.append(_quote(q, (year, _months_to_numbers[month], day))) # type: ignore
        # print(f"Year: {year}, Month: {month}, Day: {day}")
    return quotelist
    

def test():
    q1 = _quote("Test with full tuple", (2025, 9, 1))
    q2 = _quote("Test with empty tuple", (2023, None, None))
    q3 = _quote("Test without tuple")
    print(q1)
    print(q2)
    print(q3)

def load_quotes_from_json(file_path: str) -> list['_quote']:
    """Load a list of _quote objects from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing quotes
        
    Returns:
        List of _quote objects
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        quotes = []
        # Check if the JSON has the expected structure
        if 'quotes' in data and isinstance(data['quotes'], list):
            for quote_data in data['quotes']:
                # Convert the quote dict to JSON string for decoding
                json_str = json.dumps(quote_data)
                quote = _quote.decode(json_str)
                quotes.append(quote)
        
        return quotes
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{file_path}'.")
        return []
    except Exception as e:
        print(f"Error loading quotes: {e}")
        return []

quote_list = []

def encode_quotes_to_json(file_path: str) -> None:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('{"quotes": [\n')
            for i, q in enumerate(quote_list):
                f.write("\t" + q.encode() + f"{"," if i != len(quote_list) - 1 else ''}\n")
                # print(q)
            f.write("\n]}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error loading quotes: {e}")


quote_list = extract()
    
loaded_quote_list = load_quotes_from_json("./quotes.json")

if len(quote_list) != len(loaded_quote_list):
    encode_quotes_to_json("./quotes.json")
    raise RuntimeWarning(f"Length of quote list extracted from .txt file ({len(quote_list)}) is not equal to length of that from json file ({len(loaded_quote_list)})")
else:
    encode_quotes_to_json("./quotes.json")