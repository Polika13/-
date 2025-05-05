class Polybius:
    def __init__(self, word):
        self.word = word
        if 65 <= min([ord(i) for i in self.word]) <= 122:  # латиница
            self.b = [['A', 'B', 'C', 'D', 'E'],
                      ['F', 'G', 'H', 'I', 'K'],
                      ['L', 'M', 'N', 'O', 'P'],
                      ['Q', 'R', 'S', 'T', 'U'],
                      ['V', 'W', 'X', 'Y', 'Z']]
        elif 1040 <= min([ord(i) for i in self.word]) <= 1103:  # кириллица
            self.b = [['А', 'Б', 'В', 'Г', 'Д', 'Е'],
                      ['Ё', 'Ж', 'З', 'И', 'Й', 'К'],
                      ['Л', 'М', 'Н', 'О', 'П', 'Р'],
                      ['С', 'Т', 'У', 'Ф', 'Х', 'Ц'],
                      ['Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь'],
                      ['Э', 'Ю', 'Я', '-', '+', '=']]
        self.matrixHeight, self.matrixWidth = len(self.b), len(self.b[0])

    def find_coordinates(self, symbol):
        """Находит координаты символа в таблице."""
        for i in range(self.matrixHeight):
            for j in range(self.matrixWidth):
                if self.b[i][j] == symbol:
                    return (i + 1, j + 1)
        return None

    def encrypt(self, text: str) -> str:
        """Шифрует текст методом Полибия."""
        encrypted = []
        for char in text.upper():
            coords = self.find_coordinates(char)
            if coords:
                encrypted.append(f"{coords[0]}{coords[1]}")
            else:
                encrypted.append(char)
        return ''.join(encrypted)

    def decrypt(self, text: str) -> str:
        """Дешифрует текст методом Полибия."""
        decrypted = []
        i = 0
        while i < len(text):
            if text[i].isdigit() and i + 1 < len(text) and text[i + 1].isdigit():
                row, col = int(text[i]) - 1, int(text[i + 1]) - 1
                if 0 <= row < self.matrixHeight and 0 <= col < self.matrixWidth:
                    decrypted.append(self.b[row][col])
                i += 2
            else:
                decrypted.append(text[i])
                i += 1
        return ''.join(decrypted) 