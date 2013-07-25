class Content():
    def __init__(self, text):
        self.text = text
        self.words = self.text.split()

        self.clean_text = self.text.replace(':', '')
        self.clean_text = self.clean_text.replace(',', '')
        self.clean_text = self.clean_text.replace('.', '')
        self.clean_text = self.clean_text.lower()
        self.clean_words = self.clean_text.split()

        self.sentence_text = self.text.replace(':', '.')
        self.sentences = self.sentence_text.split('. ')

    def contains(self, *args):
        for arg in args:
            if self.clean_text.find(arg) != -1:
                return True
        return False

    def locate(self, term, forward=False, tag=False, plural=False):
        value = ''
        sentences = self.sentences
        for sentence in sentences:
            sentence = Content(sentence)

            if term in sentence.clean_words:
                index = sentence.clean_words.index(term)
                if not forward and self.is_proper(index - 1):
                    if plural:
                        value = sentence.read_plural(index - 1, forward=False)
                    value = sentence.read_element(index - 1, forward=False)
                elif(
                    len(sentence.clean_words) > index + 1 and
                    sentence.clean_words[index + 1] == 'of' and
                    not forward
                ):
                    if plural:
                        value = sentence.read_plural(index + 2)
                    value = sentence.read_element(index + 2)
                else:
                    if plural:
                        value = sentence.read_plural(index + 1)
                    value = sentence.read_element(index + 1)
            if tag:
                if value:
                    value = value + ' ' + term.capitalize()
        return value

    def is_proper(self, index):
        if self.words[index][0].isupper():
            return True
        if self.words[index][:2].lower() == 'al':
            return True
        return False

    def read_element(self, index, forward=True):
        terms = []
        while True:
            if len(self.words) > index >= 0:
                if self.is_proper(index):
                    term = self.words[index]
                    if term[-1] == ',':
                        term = term[:-1]
                    terms.append(term)
                else:
                    break
            else:
                break

            if forward:
                index += 1
            else:
                index -= 1

        if not forward:
            terms.reverse()

        element = ''
        for term in terms:
            element += term + ' '
        if len(element) > 0:
            element = element[:-1]

        return element

    def read_plural(self, index, forward=True):
        locations = []
        if self.words[index + 1] == 'of':
            while True:
                index = self.words[index + 2]

                if self.is_proper(index):
                    bounds = self.read_plural_element(index)
                elif(
                    self.words[index + 1] == 'and' and
                    self.is_proper(index + 2)
                ):
                    bounds = self.read_plural_element(index + 2)

                locations += bounds
                index = bounds[1] + 1

    def read_plural_element(self, index):
        start = index
        while True:
            word = self.words[index]
            if self.is_proper(word):
                if word[-1] == ',':
                    break
            else:
                break
            index += 1
        return [start, index]
