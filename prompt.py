OPTIMIZED_PROMPT = """
Please format the following transcription according to these rules:

## Arabic and Non-English Words
1. **Basic Transliteration Rules:**
   - Italicize all Arabic/non-English words except those in common English usage (e.g., Allah, imam, Quran)
   - People's names and places are not italicized (e.g., Imam Bukhari, Makkah)
   - Italicize all book titles, whether English or Arabic (e.g., *Ṣaḥīḥ Bukhāri*)
   - Use macrons for long vowels: ā, ī, ū (no double vowels)
   - Do not end words with long vowels (e.g., Ḥanbali, Bukhari)
   - Always use lowercase for "al-" unless it starts a sentence or title
   - Words ending with ة should end with 'h' (e.g., sūrah, Abu Ḥanīfah)

2. **Special Characters:**
   - Use Unicode symbol 02bf for ع
   - Use Unicode symbol 02be for ء
   - Do not use hamzat'l-waṣl for surah names and prayers (e.g., Sūrat al-Fātiḥah, ṣalāt al-Fajr)
   - Omit initial hamzah transliteration unless the word is between two words
   - Double letters for shaddah (e.g., شدّة becomes shaddah)

## Numbers and Units
- Write single-digit numbers as words
- Use numerals for numbers requiring hyphens (e.g., twenty-four)
- Include space between numbers and units (e.g., 75 km)
- No space with percentages (e.g., 75%)
- Write fractions as words (e.g., one fifth)
- Time format: digits with a.m./p.m. (e.g., 5:00 a.m.)

## Content Guidelines
- Omit colloquial expressions (e.g., "ya'ni", "like", "gonna")
- Replace informal phrases with formal alternatives (e.g., "so he goes" → "he said")
- Remove teaching fillers (e.g., "Does that make sense?", "Is that clear?")
- Use complete forms instead of contractions (e.g., "is not" instead of "isn't")
- For hadith references, transcribe as paraphrased in class
- Exclude jokes unless they illustrate a point
- Fix incomplete or trailing sentences for grammatical correctness while maintaining the original meaning

## Additional Notes
- Honorifics should use symbols only, not written forms
- If symbols cannot be used, use the following letter replacements:
  - Prophet (ﷺ): use 'r'
  - Allah (ﷻ): use 'I'
  - Male Companion (رضي الله عنه): use 't'
  - Omit all other honorifics if symbols unavailable

Please provide the text to be formatted, and I will apply these rules while maintaining the original flow and meaning of the content.
"""