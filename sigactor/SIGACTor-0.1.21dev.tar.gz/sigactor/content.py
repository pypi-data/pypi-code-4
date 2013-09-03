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

        terms = term.split()
        length = len(terms)

        sentences = self.sentences
        for sentence in sentences:
            sentence = Content(sentence)
            words = sentence.clean_words
            start = ''
            end = ''

            for number in range(0, len(words) - (length - 1)):
                if words[number:number + length] == terms:
                    start = number
                    end = number + length - 1

            if start != '':
                if not forward and self.is_proper(start - 1):
                    if plural:
                        value = sentence.read_plural(start - 1, forward=False)
                    value = sentence.read_element(start - 1, forward=False)
                elif(
                    len(sentence.clean_words) > end + 1 and
                    sentence.clean_words[end + 1] == 'of' and
                    not forward
                ):
                    if plural:
                        value = sentence.read_plural(end + 2)
                    value = sentence.read_element(end + 2)
                else:
                    if plural:
                        value = sentence.read_plural(end + 1)
                    value = sentence.read_element(end + 1)
            if tag:
                if value:
                    if length > 1:
                        value = value + ' ' + term
                    else:
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
                term = self.words[index]
                if (not terms) and term.lower() == 'the':
                    return term
                if self.is_proper(index):
                    stop = False
                    if term[-1] == ',':
                        term = term[:-1]
                        stop = True
                    terms.append(term)
                    if stop:
                        break
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
