from typing import Optional


class Emoji:
    def __init__(self, data: dict):
        self._data = data
        self.hex_code = data.get('hexcode')
        self.label = data.get('label')
        self.unicode = data.get('unicode')


class EmojiTools:
    def __init__(self, data_path_override: Optional[str] = None):
        _data_path = data_path_override or 'static/data/emojis.json'
        self.emojis = self._load_emojis(data_path=_data_path)

    def _load_emojis(self, data_path: str) -> list[Emoji]:
        with open(data_path, 'r') as f:
            self._emoji_data = f.read()

        import json
        emoji_dicts = json.loads(self._emoji_data)
        return [Emoji(data=emoji_dict) for emoji_dict in emoji_dicts]

    def validate_emoji_hex_code(self, emoji_hex_code: str) -> bool:
        """
        Validate that the provided emoji hex code exists in the emoji dataset.
        :param emoji_hex_code: The hex code of the emoji to validate (e.g. "1F600" for 😀)
        :return: True if the emoji hex code is valid, False otherwise
        """
        return any(emoji.hex_code == emoji_hex_code for emoji in self.emojis)

    def validate_emoji_unicode(self, emoji_unicode: str) -> bool:
        """
        Validate that the provided emoji unicode exists in the emoji dataset.
        :param emoji_unicode: The unicode of the emoji to validate (e.g. "😀")
        :return: True if the emoji unicode is valid, False otherwise
        """
        return any(emoji.unicode == emoji_unicode for emoji in self.emojis)
