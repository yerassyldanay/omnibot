KAZ = 'kk'
RUS = 'ru'

START = 'Тілді таңдаңыз / Выберите язык'

HELLO: dict = {
    KAZ: '''Сәлем. Мен әлеуметтік желілерге кез келген тақырыпта контент жазып беремін. 

Таза әрі толық нұсқада сұрасаңыз, жақсырақ жауап беремін. Мысалы, 

Ағылшын тілін онлайн оқыту платформасы үшін ақпараттық және әзіл мазмұнында әлеуметтік желілерге жарнама жазыңыз. Мұны жастар стилінде жасаңыз, өйткені менің клиенттерім жастардан тұрады. Қысқа етіп жазыңыз.

Таудың басында отырып, алысқа қарап тұрған суретімнің астына Instagram пост жазу керек. Оны философиялық етіп жасаңыз.

Сұраңыз: қай тақырыпта жазайын?''',
    RUS: '''Привет. Я пишу контент для социальных сетей на любую тему.

Я дам лучший ответ, если вы спросите простым языком и в полной версии. Например,

Пожалуйста, напишите информативный и юмористический рекламный контент в социальных сетях для платформы онлайн-обучения английскому языку. Сделайте это в молодежном стиле, так как мой клиентский сегмент в основном состоит из молодежи. Держать текст коротким.

Пожалуйста, напишите подпись к посту в Instagram под фотографией, на которой я сижу на вершине горы и смотрю вдаль. Сделайте это философским.

На какую тему мне писать?''',
}

ADD_CONTEXT: dict = {
    KAZ: 'Алдыңғы сұрағыңызға сәйкес басқа да мәлімет қоссаңыз',
    RUS: 'Пожалуйста добавьте больше информации к предыдущему посту',
}

HELP: dict = {
    KAZ: '''Посттың қандай болу керектігін сипаттап берсеңіз, соған сәйкес мәтін жазамын. 

Әр жауаптан кейін /add батырмасын басып, қосымша мәлімет берсеңіз, жаңа әрі мағыналы мәтін дайындап беремін. 

Мысалы, 
* жастар тілінде жаз
* ресми тілде жаз
* осы мәтінді қысқартып жаз
деген сияқты толықтырулар (қиялыңыздың ұшқырылығы керек болады)''',
    RUS: '''Если вы опишете, каким должен быть пост, я напишу текст соответственно.

Под каждым моим ответом по контенту, вы можете найти кнопку /add, которая добавляет доп данные для вашего контента и перегенерирует контент на основе добавленных данных.

Например,
* писать молодежным языком
* писать более официальным языком
* сократить этот текст
и так далее (зависит от вашей фантазией)''',
}

FEEDBACK: dict = {
    KAZ: '''Мен туралы пікір қалдырып кетіңіз
* қай жерін өзгертуге кеңес бересіз
* немесе жай ғана мақтап кетсеңіз де ризамын''',
    RUS: '''Оставьте отзыв обо мне
* что вы бы хотели видеть или изменить
* или можете меня просто похвалить''',
}

DID_NOT_UNDERSTAND: dict = {
    KAZ: 'Мен сізді түсінбедім, мәзірді немесе /help батырмасын басып мәлімет алыңыз',
    RUS: 'Я не понял вас, воспользуйтесь меню или /help чтобы узнать какие функционалы есть'
}

TO_ADD_CONTEXT: dict = {
    KAZ: 'Алдыңғы жазбаға қосымша ақпарат қосу үшін /add түймесін немесе жаңа жазба жасау үшін /new түймесін басыңыз',
    RUS: 'Нажмите /add - добавить доппольнительную информацию к предыдущему сообщению или /new - чтобы создать новый пост'
}

SEND_NEW_POST: dict = {
    KAZ: 'Маған жаңа мазмұнның сипаттамасын жібере аласыз ба',
    RUS: '''Вы можете мне отправить описание нового контента'''
}

HIT_LIMIT: dict = {
    KAZ: 'Сіз шекке жеттіңіз. Сіз боттан күніне 6 жауап ала аласыз (/add және /new командалар үшін)',
    RUS: '''Вы достигли лимита. Вы можете получить 6 ответов от бота за день (для команд /add и /new)'''
}

EXCEPTION: dict = {
    KAZ: 'Сорри, қателік орын алды. Бірақ менен емес ;)',
    RUS: 'Сорри, произошла ошибка. Но тут я ни при чем ;)'
}

THANKS_FOR_FEEDBACK = {
    KAZ: 'Фидбэк үшін көп-көп рақмет!!!',
    RUS: 'Cпасибо за фидбэк!!!'
}

# <s></s>
EXAMPLES = [
    {
        KAZ: '''<s>Қызыма сыйлық айт</s>

Кездесетін қызыма туған күніне қандай сыйлық сыйласам болады? Креативті ойлар айт.''',
        RUS: '''<s>Предлагай подарок моей девушке</s>

Что подарить девушке на день рождения? Придумывайте креативные идеи.'''
    },
    {
        KAZ: '''<s>Кванттық физика</s>

Кванттық физиканы оңай түсіндіріп бер. Мені бастауыш сынып оқушысы деп ойла. Барынша қысқа етіп жаз.''',
        RUS: '''<s>Квантовая физика</s>

Объясните квантовую физику легко. Считайте меня учеником начальной школы. Пишите как можно короче.'''
    },
    {
        KAZ: '''<s>Абай жолы туралы айт</s>

Мұхтар Әуезовтың Абай Жолы романына рецензия жазып бер. Қысқа етіп жаз.''',
        RUS: '''<s>Расскажи про путь Абая</s>
        
Напишите рецензию на роман Мухтара Ауэзова «Путь Абая». Держать его коротким.'''
    },
    {
        KAZ: '''<s>Туристерге арналған видеоролик</s>
        
Қазақстанға шетелден туристерді шақыратын видео-роликке текст жазып бер. Қазақстанның ерекше тұстарына жарнама болу керек.''',
        RUS: '''<s>Видеоролик для туристов</s>
        
Напишите текст для видеоролика, приглашающего иностранных туристов в Казахстан. Должна быть реклама про особенностей Казахстана.'''
    },
    {
        KAZ: '''<s>Хәрри Поттер</s>
        
Хәрри Поттер стилінде өте қысқа әңгіме жазып бер.''',
        RUS: '''<s>Гарри Поттер</s>
        
Напишите очень короткий рассказ в стиле Гарри Поттер.'''
    },
    {
        KAZ: '''<s>Платформаға жарнама жаз</s>
        
Ағылшын тілін онлайн оқыту платформасы үшін ақпараттық және әзіл мазмұнында әлеуметтік желілерге жарнама жазыңыз. Мұны жастар стилінде жасаңыз, өйткені менің клиенттерім жастардан тұрады. Қысқа етіп жазыңыз.''',
        RUS: '''<s>Реклама для платформы</s>
        
Напишите рекламу в социальных сетях с информативным и юмористическим содержанием для онлайн-платформы для изучения английского языка. Делайте это в молодежном стиле, потому что мои клиенты — молодые люди. Держать его коротким.'''
    },
    {
        KAZ: '''<s>Инстаграм пост жаз</s>
        
Таудың басында отырып, алысқа қарап тұрған суретімнің астына Instagram пост жазу керек. Оны философиялық етіп жасаңыз.''',
        RUS: '''<s>Напиши Инстаграм пост</s>
        
Напишите пост в Instagram под фотографией, на которой я сижу на вершине горы и смотрю вдаль. Сделайте это философским.'''
    },
]

PROCESS_RUNNING = {
    KAZ: 'Жақсы сұрақ! Бомба жауап дайындап жатырмын...',
    RUS: 'О, интерестный вопрос! Думаю, сейчас будет бомба ответ...'
}
