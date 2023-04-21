from deep_translator import GoogleTranslator

def translate_en_to_kz(text):
    """
    Бұл код ағылшын тіліндегі мәтінді қазақ тіліне аудару үшін.

    Функцияның ішінде deep_translator бумасындағы GoogleTranslator сыныбы мәтінді
    бастапқы тілден (авто, яғни енгізілген мәтіннің тілі автоматты түрде анықталады)
    мақсатты тілге (kk, бұл) аударатын дананы инициализациялау үшін пайдаланылады.

    Бұл код Python ортасында орнатылған deep_translator бумасын, сондай-ақ аударма
    үшін Google Translate API пайдалану үшін интернет байланысын қажет ететінін ескеріңіз.
    """
    translated = GoogleTranslator(source='auto', target='kk').translate(text)
    return translated
