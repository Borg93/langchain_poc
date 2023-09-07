import tiktoken

enc = tiktoken.get_encoding("cl100k_base")
print(enc.encode("hello world"))

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


if  __name__ == "__main__":
    text ="""
När ärendehandläggningen flyttades mellan de olika myndigheterna
gjorde man inte något brott i arkivbildningen. Det betyder att serier av
dossierer som lades upp av en myndighet har fortsatt att föras av dess efterträdare. När man sedan i efterhand har ordnat och förtecknat arkiven, har
det inte gått att göra en skarp skillnad mellan de olika myndigheternas
arkiv. Så går till exempel Invandrarverkets/Migrationsverkets dossierer
över utlänningar ofta tillbaka till långt före verkets tillkomst 1969, i teorin ända till 1920-talet, förutsatt att vederbörande inte blivit svensk medborgare men varit aktuell för verkets handläggning efter 1970. En sådan
centraldossier skall i princip innehålla flertalet handlingar som rör den enskilde utlänningen och förvaras i den centrala utlänningsmyndighetens
arkiv (Socialstyrelsen, Utlänningskommissionen eller Invandrarverket/
Migrationsverket). Beskrivningen av arkivförhållandena utgår därför från
typ av handling. I stora drag delas beskrivningen upp på följande avsnitt:

- Härbärgerarkort (poliseringskort, bostadsanmälningskort), 1916–1969
- Pass- och viseringshandlingar, 1917–
- Ansökningar om uppehållsböcker, 1918–1927
- Centraldossierer över utlänningar (ansökningar och beslut om arbetstillstånd, uppehållstillstånd, bosättningstillstånd, permanent uppehållstillstånd m.m.), 1920–
- Register över utlänningar, 1917–
  - Viseringsregister m.m. över utlänningar, 1917–1943
  - Centralregister över utlänningar, 1942–1973
  - ADB-baserade register över invandrare, 1973–
- Kontrolldossierer m.m., dvs. ofördelaktiga uppgifter om
  utlänningar, 1914–
- Arbetsgivaranmälningar, 1926–1977
- In- och utresekort (kontrollkort), 1926–
- Utlänningsräkningen, 1939
- Nationalitetsregister, 1939–1945
- Anställningstillstånd, 1974–

"""

    num_tokens_from_string(text, "cl100k_base")
