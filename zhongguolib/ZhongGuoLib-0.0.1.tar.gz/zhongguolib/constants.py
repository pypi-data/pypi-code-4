# -*- coding: utf8 -*-
NO_INITIAL = ''

HSK_LEVEL_RANGE = [1, 2, 3, 4, 5, 6]

LATIN_ALPHABET = u'abcdefghijklmnopqrstuvwxyz'
ALLOWED_PININ_CHARACTERS = u'aeiouüāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ'
CYLLIRIC_ALPHABET = u'абвгдежзийклмнопрстуфхцчшщъьюя'

HEX_BASE = 16

CJK   = range(int('4E00',  HEX_BASE), int('9FFF',  HEX_BASE) + 1)
CJK_A = range(int('3400',  HEX_BASE), int('4DBF',  HEX_BASE) + 1)
CJK_B = range(int('20000', HEX_BASE), int('2A6DF', HEX_BASE) + 1)
CJK_C = range(int('2A700', HEX_BASE), int('2B73F', HEX_BASE) + 1)
CJK_D = range(int('2B840', HEX_BASE), int('2B81F', HEX_BASE) + 1)

NEUTRAL_TONE = 0
FIRST_TONE = 1
SECOND_TONE = 2
THIRD_TONE = 3
FOURTH_TONE = 4
CHINESE_TONES = [NEUTRAL_TONE, FIRST_TONE, SECOND_TONE, THIRD_TONE, FOURTH_TONE]

TONES = {
         u'a': [u'a', u'ā', u'á', u'ǎ', u'à'],
         u'e': [u'e', u'ē', u'é', u'ě', u'è'],
         u'i': [u'i', u'ī', u'í', u'ǐ', u'ì'],
         u'u': [u'u', u'ū', u'ú', u'ǔ', u'ù'],
         u'ü': [u'ü', u'ǖ', u'ǘ', u'ǚ', u'ǜ'],
         u'o': [u'o', u'ō', u'ó', u'ǒ', u'ò'],
}

VOWELS = [ u'a', u'e', u'i', u'u', u'ü', u'o' ]


INITIALS = [
            u'b', u'p', u'm', u'f', u'd', u't', u'n', u'l', u'g', u'k', u'h', u'j',
            u'q', u'x', u'zh', u'ch', u'sh', u'r', u'z', u'c', u's', u'w', u'y'
]

FINALS = [
          u'a', u'ai', u'an', u'ang', u'ao', u'e', u'ei', u'en', u'eng', u'er', u'i',
          u'ia', u'iao', u'ian', u'iang', u'ie', u'in', u'ing', u'iong', u'iu', u'o',
          u'ong', u'ou', u'u', u'ua', u'uai', u'uan', u'uang', u'ui', u'un', u'uo', u'ue',
          u'ü', u'üan', u'üe', u'ün'
]

FINALS_TONES = {
    u'a':       (u'a', u'ā', u'á', u'ǎ', u'à'),
    u'ai':      (u'ai', u'āi', u'ái', u'ǎi', u'ài'),
    u'ao':      (u'ao', u'āo', u'áo', u'ǎo', u'ào'),
    u'an':      (u'an', u'ān', u'án', u'ǎn', u'àn'),
    u'ang':     (u'ang', u'āng', u'áng', u'ǎng', u'àng'),
    u'e':       (u'e', u'ē', u'é', u'ě', u'è'),
    u'ei':      (u'ei', u'ēi', u'éi', u'ěi', u'èi'),
    u'en':      (u'en', u'ēn', u'én', u'ěn', u'èn'),
    u'eng':     (u'eng', u'ēng', u'éng', u'ěng', u'èng'),
    u'er':      (u'er', u'ēr', u'ér', u'ěr', u'èr'),
    u'i':       (u'i', u'ī', u'í', u'ǐ', u'ì'),
    u'ia':      (u'ia', u'iā', u'iá', u'iǎ', u'ià'),
    u'iao':     (u'iao', u'iāo', u'iáo', u'iǎo', u'iào'),
    u'ian':     (u'ian', u'iān', u'ián', u'iǎn', u'iàn'),
    u'iang':    (u'iang', u'iāng', u'iáng', u'iǎng', u'iàng'),
    u'ie':      (u'ie', u'iē', u'ié', u'iě', u'iè'),
    u'in':      (u'in', u'īn', u'ín', u'ǐn', u'ìn'),
    u'ing':     (u'ing', u'īng', u'íng', u'ǐng', u'ìng'),
    u'iong':    (u'iong', u'iōng', u'ióng', u'iǒng', u'iòng'),
    u'iu':      (u'iu', u'iū', u'iú', u'iǔ', u'iù'),
    u'o':       (u'o', u'ō', u'ó', u'ǒ', u'ò'),
    u'ong':     (u'ong', u'ōng', u'óng', u'ǒng', u'òng'),
    u'ou':      (u'ou', u'ōu', u'óu', u'ǒu', u'òu'),
    u'u':       (u'u', u'ū', u'ú', u'ǔ', u'ù'),
    u'ua':      (u'ua', u'uā', u'uá', u'uǎ', u'uà'),
    u'uai':     (u'uai', u'uāi', u'uái', u'uǎi', u'uài'),
    u'ue':      (u'ue', u'uē', u'ué', u'uě', u'uè'),
    u'uan':     (u'uan', u'uān', u'uán', u'uǎn', u'uàn'),
    u'uang':    (u'uang', u'uāng', u'uáng', u'uǎng', u'uàng'),
    u'wang':    (u'wang', u'wāng', u'wáng', u'wǎng', u'wàng'),
    u'ui':      (u'ui', u'uī', u'uí', u'uǐ', u'uì'),
    u'un':      (u'un', u'ūn', u'ún', u'ǔn', u'ùn'),
    u'uo':      (u'uo', u'uō', u'uó', u'uǒ', u'uò'),
    u'ü':       (u'ü', u'ǖ', u'ǘ', u'ǚ', u'ǜ'),
    u'üan':     (u'üan', u'üān', u'üán', u'üǎn', u'üàn'),
    u'üe':      (u'üe', u'üē', u'üé', u'üě', u'üè'),
    u'ün':      (u'ün', u'ǖn', u'ǘn', u'ǚn', u'ǜn'),
    u'y':       (u'yu', u'yū', u'yú', u'yǔ', u'yù'),
    u'yue':     (u'yue', u'yuē', u'yué', u'yuě', u'yuè'),
    u'yuan':    (u'yuan', u'yuān', u'yuán', u'yuǎn', u'yuàn'),
    u'yun':     (u'yun', u'yūn', u'yún', u'yǔn', u'yùn'),
}

NO_FINALS = [ u'ai', u'an', u'ang', u'ao', u'e', u'en', u'eng', u'er' ]


SYLLABLES = {
                NO_INITIAL: [u'a', u'ai', u'ao', u'an', u'ang', u'e', u'ei', u'en', u'eng', u'er', u'o', u'ou'],
                
                u'b':  [u'ba', u'bai', u'ban', u'bang', u'bao', u'bei', u'ben', u'beng',
                        u'bi', u'biao', u'bian', u'bie', u'bin', u'bing', u'bo', u'bu'],

                u'p':  [u'pa', u'pai', u'pan', u'pang', u'pao', u'pei', u'pen', u'peng',
                        u'pi', u'piao', u'pian', u'pie', u'pin', u'ping', u'po', u'pou', u'pu'],

                u'm':  [u'ma', u'mai', u'man', u'mang', u'mao', u'mei', u'men', u'meng', u'mi',
                        u'miao', u'mian', u'mie', u'min', u'ming', u'miu', u'mo', u'mou', u'mu'],

                u'f':  [u'fa', u'fan', u'fang', u'fei', u'fen', u'feng', u'fo', u'fou', u'fu'],

                u'd':  [u'da', u'dai', u'dan', u'dang', u'dao', u'de', u'dei', u'den', u'deng',
                        u'di', u'dia', u'diao', u'dian', u'die', u'ding', u'diu', u'dong', u'dou',
                        u'du', u'duan', u'dui', u'dun', u'duo'],

                u't':  [u'ta', u'tai', u'tan', u'tang', u'tao', u'te', u'teng', u'ti', u'tiao',
                        u'tian', u'tie', u'ting', u'tong', u'tou', u'tu', u'tuan', u'tui', u'tun', u'tuo'],

                u'n':  [u'na', u'nai', u'nan', u'nang', u'nao', u'ne', u'nei', u'nen', u'neng', u'ni',
                        u'niao', u'nian', u'niang', u'nie', u'nin', u'ning', u'niu', u'nong', u'nou',
                        u'nu', u'nuan', u'nun', u'nuo', u'nü', u'nüe'],

                u'l':  [u'la', u'lai', u'lan', u'lang', u'lao', u'le', u'lei', u'leng', u'li', u'lia',
                        u'liao', u'lian', u'liang', u'lie', u'lin', u'ling', u'liu', u'long', u'lou',
                        u'lu', u'luan', u'lun', u'luo', u'lü', u'lüe'],

                u'g':  [u'ga', u'gai', u'gan', u'gang', u'gao', u'ge', u'gei', u'gen', u'geng', u'gong',
                        u'gou', u'gu', u'gua', u'guai', u'guan', u'guang', u'gui', u'gun', u'guo'],

                u'k':  [u'ka', u'kai', u'kan', u'kang', u'kao', u'ke', u'ken', u'keng', u'kong', u'kou',
                        u'ku', u'kua', u'kuai', u'kuan', u'kuang', u'kui', u'kun', u'kuo'],

                u'h':  [u'ha', u'hai', u'han', u'hang', u'hao', u'he', u'hei', u'hen', u'heng', u'hong',
                        u'hou', u'hu', u'hua', u'huai', u'huan', u'huang', u'hui', u'hun', u'huo'],

                u'j':  [u'ji', u'jia', u'jiao', u'jian', u'jiang', u'jie', u'jin', u'jing', u'jiong',
                        u'jiu', u'ju', u'juan', u'jue', u'jun'],

                u'q':  [u'qi', u'qia', u'qiao', u'qian', u'qiang', u'qie', u'qin', u'qing', u'qiong',
                        u'qiu', u'qu', u'quan', u'que', u'qun'],

                u'x':  [u'xi', u'xia', u'xiao', u'xian', u'xiang', u'xie', u'xin', u'xing', u'xiong',
                        u'xiu', u'xu', u'xuan', u'xue', u'xun'],

                u'zh': [u'zha', u'zhan', u'zhang', u'zhao', u'zhe', u'zhei', u'zhen', u'zheng',
                        u'zhi', u'zhong', u'zhou', u'zhu', u'zhua', u'zhuai', u'zhuan', u'zhuang',
                        u'zhui', u'zhun', u'zhuo'],

                u'ch': [u'cha', u'chan', u'chang', u'chao', u'che', u'chen', u'cheng', u'chi',
                        u'chong', u'chou', u'chu', u'chua', u'chuai', u'chuan', u'chuang', u'chui', u'chun', u'chuo'],

                u'sh': [u'sha', u'shan', u'shang', u'shao', u'she', u'shei', u'shen', u'sheng',
                        u'shi', u'shou', u'shu', u'shua', u'shuai', u'shuan', u'shuang', u'shui', u'shun', u'shuo'],

                u'r':  [u'ran', u'rang', u'rao', u're', u'ren', u'reng', u'ri', u'rong', u'rou', u'ru',
                        u'ruan', u'rui', u'run', u'ruo'],

                u'z':  [u'za', u'zai', u'zan', u'zang', u'zao', u'ze', u'zei', u'zen', u'zeng',
                        u'zi', u'zong', u'zou', u'zu', u'zuan', u'zui', u'zun', u'zuo'],

                u'c':  [u'ca', u'cai', u'can', u'cang', u'cao', u'ce', u'cen', u'ceng', u'ci',
                        u'cong', u'cou', u'cu', u'cuan', u'cui', u'cun', u'cuo'],

                u's':  [u'sa', u'sai', u'san', u'sang', u'sao', u'se', u'sen', u'seng', u'si',
                        u'song', u'sou', u'su', u'suan', u'sui', u'sun', u'suo'],

                u'w':  [u'wa', u'wai', u'wan', u'wang', u'wei', u'wen', u'weng', u'wo', u'wu'],

                u'y':  [u'ya', u'yan', u'yang', u'yao', u'ye', u'yi', u'yin', u'ying', u'yong',
                        u'you', u'yu', u'yuan', u'yue', u'yun'],
}

all_syllables = reduce(lambda x, y: x+y, [v for k, v in SYLLABLES.iteritems()])
ALL_SYLLABLES_SORTED = sorted(all_syllables, lambda x, y: cmp(len(x),len(y)), reverse=True)