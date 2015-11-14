# FixtureFinder
Finds any upcoming top v bottom football league fixtures, by scraping the web for tables and fixture information.

## Usage
```bash
Usage: FixtureFinder [OPTIONS] [leagueCode]

Options:
  -h, --help            show this help message and exit
  -l, --list            lists the league codes
  -a, --all             get all fixtures
  -t, --target          get fixtures for specified league
```

## Examples

```bash
python FixtureFinder --list
python FixtureFinder -t SP1
python FixtureFinder --all
```

## Output
The output is an upcoming fixture between a top and bottom ranked team in a number of UK and European leagues. The output is of the form, 

```bash
Home Win: SC5, 20160109, Edinburgh City v Threave Rovers
Away Win: SC4, 20151114, Huntly v Turriff United
Home Win: SC4, 20151120, Cove Rangers v Huntly
```

Which predicts a home win for The Citizen's (a.k.a., Edinburgh City) on the 9th January 2016 against Threave Rovers. The format of the output is

```bash
[Home Win|Away Win]: [League-Code], YYYYMMDD, HomeTeam v AwayTeam
```
