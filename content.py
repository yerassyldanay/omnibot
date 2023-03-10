KAZ = 'kk'
RUS = 'ru'

START = 'Тілді таңдаңыз / Выберите язык'

HELLO: dict = {
    KAZ: '''Сәлем. Мен кезкелген сұраққа жауап беретін Omni ботпын. 

<b>Сұрақты таза әрі толық нұсқада сұрасаңыз, жақсырақ жауап беремін.</b> Мысалдарды төмендегі батырма арқылы біле аласыздар 

Сұраңыз: қай тақырыпта жазайын?''',
    RUS: '''Привет. Я Omni бот, который отвечает на любые вопросы.

<b>Чтобы получить конкретный и точный ответ, вы должны задать вопрос с контекстом.</b> Вы можете найти примеры, нажав кнопку ниже.

Спросите: на какую тему мне писать?''',
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

<pre>Кездесетін қызыма туған күніне қандай сыйлық сыйласам болады? Креативті ойлар айт.</pre>''',
        RUS: '''<s>Предлагай подарок моей девушке</s>

<pre>Что подарить девушке на день рождения? Придумывайте креативные идеи.</pre>'''
    },
    {
        KAZ: '''<s>Кванттық физика</s>

<pre>Кванттық физиканы оңай түсіндіріп бер. Мені бастауыш сынып оқушысы деп ойла. Барынша қысқа етіп жаз.</pre>''',
        RUS: '''<s>Квантовая физика</s>

<pre>Объясните квантовую физику легко. Считайте меня учеником начальной школы. Пишите как можно короче.</pre>'''
    },
    {
        KAZ: '''<s>Абай жолы туралы айт</s>

<pre>Мұхтар Әуезовтың Абай Жолы романына рецензия жазып бер. Қысқа етіп жаз.</pre>''',
        RUS: '''<s>Расскажи про путь Абая</s>
        
<pre>Напишите рецензию на роман Мухтара Ауэзова «Путь Абая». Держать его коротким.</pre>'''
    },
    {
        KAZ: '''<s>Туристерге арналған видеоролик</s>
        
<pre>Қазақстанға шетелден туристерді шақыратын видео-роликке текст жазып бер. Қазақстанның ерекше тұстарына жарнама болу керек.</pre>''',
        RUS: '''<s>Видеоролик для туристов</s>
        
<pre>Напишите текст для видеоролика, приглашающего иностранных туристов в Казахстан. Должна быть реклама про особенностей Казахстана.</pre>'''
    },
    {
        KAZ: '''<s>Хәрри Поттер</s>
        
<pre>Хәрри Поттер стилінде өте қысқа әңгіме жазып бер.</pre>''',
        RUS: '''<s>Гарри Поттер</s>
        
<pre>Напишите очень короткий рассказ в стиле Гарри Поттер.</pre>'''
    },
    {
        KAZ: '''<s>Платформаға жарнама жаз</s>
        
<pre>Ағылшын тілін онлайн оқыту платформасы үшін ақпараттық және әзіл мазмұнында әлеуметтік желілерге жарнама жазыңыз. Мұны жастар стилінде жасаңыз, өйткені менің клиенттерім жастардан тұрады. Қысқа етіп жазыңыз.</pre>''',
        RUS: '''<s>Реклама для платформы</s>
        
<pre>Напишите рекламу в социальных сетях с информативным и юмористическим содержанием для онлайн-платформы для изучения английского языка. Делайте это в молодежном стиле, потому что мои клиенты — молодые люди. Держать его коротким.</pre>'''
    },
    {
        KAZ: '''<s>Инстаграм пост жаз</s>
        
<pre>Таудың басында отырып, алысқа қарап тұрған суретімнің астына Instagram пост жазу керек. Оны философиялық етіп жасаңыз.</pre>''',
        RUS: '''<s>Напиши Инстаграм пост</s>
        
<pre>Напишите пост в Instagram под фотографией, на которой я сижу на вершине горы и смотрю вдаль. Сделайте это философским.</pre>'''
    },
]

PROCESS_RUNNING = {
    KAZ: 'Жақсы сұрақ! Бомба жауап дайындап жатырмын...',
    RUS: 'О, интересный вопрос! Думаю, сейчас будет бомба ответ...'
}
