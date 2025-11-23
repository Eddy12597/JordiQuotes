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
>>> print(quote_list[67].date)
(2024, 11, 27)
>>> print(quote_list[67].content)
"You can't defeat the Harkenans if you can't do your calculus homework!"
>>> print(quote_list[67].origin) 
Jordi A. Navarrette
>>> 
```

## Future Roadmap

- JESS extraction and analysis
- expand to other languages
- maybe publish package