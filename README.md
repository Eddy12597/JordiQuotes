# JordiQuotes

List of Mr. Jordi's famous quotes. Credits are listed on the top of the file `Jordi's Famous Quotes.txt`.

## Extraction

`extract.py` parses `Jordi's Famous quotes.txt` into JSON format in `quotes.json`.

```bash
python extract.py
```

You can also use it in other python files:

```python
>>> from extract import *
>>> print(quote_list[67])
"You can't defeat the Harkenans if you can't do your calculus homework!" -- Jordi A. Navarrette, Nov 27, 2024
```