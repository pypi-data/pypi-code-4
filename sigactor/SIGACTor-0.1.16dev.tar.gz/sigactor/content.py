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

    def locate(self, term, forward=False, tag=False):
        value = ''
        sentences = self.sentences
        for sentence in sentences:
            sentence = Content(sentence)

            if term in sentence.clean_words:
                index = sentence.clean_words.index(term)
                if(
                    len(sentence.clean_words) > index + 1 and
                    sentence.clean_words[index + 1] == 'of' and
                    not forward
                ):
                    value = sentence.read_element(index + 2)
                elif not forward:
                    value = sentence.read_element(index - 1, False)
                else:
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
                    terms.append(self.words[index])
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
