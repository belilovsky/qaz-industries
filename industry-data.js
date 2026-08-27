const responsiveAssets = (prefix) => [480, 960, 1600].map((width) => ({ src: `${prefix}-${width}w.webp`, width }));

window.QAZ_INDUSTRIES = {
  energy: {
    id: 'energy',
    name: 'Энергетика',
    short: 'Энергия',
    code: '01 / ENERGY',
    sourceName: 'qz.energy',
    sourceUrl: 'https://qz.energy/',
    sourceReleaseId: 'qz-energy-newsroom-4100f6a1-20260826',
    release: 'Выпуск qz-energy-newsroom-4100f6a1-20260826 · данные на 6 августа',
    status: 'Действующий отраслевой продукт',
    summary: 'Производство энергии, сети, коридоры, объекты и события отрасли в едином публичном контуре.',
    illustration: {
      alt: 'Абстрактная редакционная иллюстрация: солнце, ветровые турбины, электростанция, линии электропередачи и городской силуэт.',
      disclosure: 'ИИ-иллюстрация для редакционного контекста; не документальная фотография.',
      sources: [
        { src: 'assets/editorial-media/profile-heroes/energy/derivatives/energy-480w.webp', width: 480 },
        { src: 'assets/editorial-media/profile-heroes/energy/derivatives/energy-960w.webp', width: 960 },
        { src: 'assets/editorial-media/profile-heroes/energy/derivatives/energy-1600w.webp', width: 1600 }
      ]
    },
    photo: {
      alt: 'Ветровые турбины Кордайской ВЭС на юго-востоке Казахстана.',
      caption: 'Кордайская ВЭС на юго-востоке Казахстана. Документальный контекст; кадр не является сводкой текущего состояния объекта.',
      creator: 'МаратД',
      sourceUrl: 'https://commons.wikimedia.org/wiki/File:Korday_wind_farm_in_the_south-_east_of_Kazakhstan.jpg',
      license: 'CC BY-SA 4.0',
      licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0',
      sources: responsiveAssets('assets/editorial-media/profile-context/energy/derivatives/energy-context')
    },
    about: 'Профиль связывает показатель с периодом, объектом на карте и материалом, который объясняет изменение. От национального значения можно перейти к инфраструктурному объекту и первоисточнику.',
    kpis: [
      { value: '173', label: 'показателей', period: 'публичный реестр' },
      { value: '18', label: 'объектов', period: 'карта и паспорта' },
      { value: '9', label: 'материалов', period: 'редакционный выпуск' },
      { value: '38', label: 'источников', period: 'реестр выпуска' }
    ],
    indicators: [
      { name: 'Выработка электроэнергии', value: '63,4', unit: 'млрд кВт·ч', period: 'I полугодие 2026', note: 'Национальный показатель', url: 'https://qz.energy/indicators.html' },
      { name: 'Выработка объектов ВИЭ', value: '5,1', unit: 'млрд кВт·ч', period: 'I полугодие 2026', note: 'Опубликованный срез ВИЭ', url: 'https://qz.energy/indicators.html' },
      { name: 'Рост выработки ВИЭ', value: '21,2', unit: '%', period: 'I полугодие 2026 к 2025', note: 'Сопоставление периодов', url: 'https://qz.energy/indicators.html' },
      { name: 'Введено проектов ВИЭ', value: '7', unit: 'проектов', period: '2026', note: 'На дату публикации', url: 'https://qz.energy/indicators.html' }
    ],
    chain: [
      { title: 'Ресурс', text: 'уголь, нефть, газ, вода, ветер и солнце' },
      { title: 'Производство', text: 'электростанции, добыча и переработка' },
      { title: 'Инфраструктура', text: 'сети, трубопроводы и коридоры' },
      { title: 'Потребление', text: 'промышленность, города и экспортные рынки' }
    ],
    geography: [
      { title: 'Запад', text: 'Нефтегазовая добыча, переработка и экспортные коридоры.' },
      { title: 'Север и центр', text: 'Крупная генерация и северо-центральный контур ЕЭС.' },
      { title: 'Восток', text: 'Гидроэнергетика, угольная генерация и сетевые связи.' },
      { title: 'Юг', text: 'Газификация, тепло, гидроэнергетика и ВИЭ.' }
    ],
    coverage: { 'Показатели': 'ready', 'Карта': 'ready', 'Паспорта объектов': 'ready', 'Редакция': 'ready', 'Машинные данные': 'partial', 'Практические сервисы': 'gap', 'Методика и источники': 'ready' },
    gaps: ['Занятость и профессии по отрасли', 'Добавленная стоимость и производительность', 'Полная цепочка межотраслевых входов и выходов', 'Сопоставление с соседними странами и мировыми рынками'],
    sources: [
      { label: 'Показатели', url: 'https://qz.energy/indicators.html' },
      { label: 'Карта', url: 'https://qz.energy/map.html' },
      { label: 'Объекты', url: 'https://qz.energy/objects.html' },
      { label: 'Источники', url: 'https://qz.energy/sources.html' }
    ]
  },
  space: {
    id: 'space',
    name: 'Космическая отрасль',
    short: 'Космос',
    code: '02 / SPACE',
    sourceName: 'Qazaqstan.Space',
    sourceUrl: 'https://qazaqstan.space/',
    sourceReleaseId: '2026-08-25.2',
    release: 'Выпуск 2026-08-25.2 · данные на 25 августа',
    status: 'Проверяемый отраслевой атлас',
    summary: 'Объекты, спутниковые программы, наземная инфраструктура, редакционные сигналы и первичные источники.',
    illustration: {
      alt: 'Абстрактная редакционная иллюстрация: спутник на орбите, наземные антенны и условные линии связи.',
      disclosure: 'ИИ-иллюстрация для редакционного контекста; не документальная фотография.',
      sources: [
        { src: 'assets/editorial-media/profile-heroes/space/derivatives/space-480w.webp', width: 480 },
        { src: 'assets/editorial-media/profile-heroes/space/derivatives/space-960w.webp', width: 960 },
        { src: 'assets/editorial-media/profile-heroes/space/derivatives/space-1600w.webp', width: 1600 }
      ]
    },
    photo: {
      alt: 'Корабль Soyuz TMA-09M на стартовой площадке космодрома Байконур.',
      caption: 'Корабль Soyuz TMA-09M на стартовой площадке Байконура. Документальный контекст, не оперативный статус программы.',
      creator: 'Bill Ingalls',
      sourceUrl: 'https://commons.wikimedia.org/wiki/File:Soyuz_TMA-09M_spacecraft_at_the_Baikonur_Cosmodrome_launch_pad_(4).jpg',
      license: 'Public domain',
      licenseUrl: 'https://commons.wikimedia.org/wiki/Commons:Copyright_tags#Public_domain',
      sources: responsiveAssets('assets/editorial-media/profile-context/space/derivatives/space-context')
    },
    about: 'Сильная сторона профиля — доказательная модель. Каждый вывод можно связать с объектом, фактом и источником, а карта выступает не украшением, а навигацией по инфраструктуре отрасли.',
    kpis: [
      { value: '32', label: 'объекта и системы', period: 'публичный атлас' },
      { value: '146', label: 'проверенных фактов', period: 'корпус выпуска' },
      { value: '26', label: 'материалов', period: 'редакционная лента' },
      { value: '151', label: 'источник', period: 'реестр доказательств' }
    ],
    indicators: [
      { name: 'Объекты и системы', value: '32', unit: 'ед.', period: 'выпуск 2026-08-25.2', note: 'Инфраструктура и программы', url: 'https://qazaqstan.space/infrastructure' },
      { name: 'Проверяемые утверждения', value: '146', unit: 'фактов', period: 'выпуск 2026-08-25.2', note: 'С типом, статусом и границей вывода', url: 'https://qazaqstan.space/data' },
      { name: 'Редакционные сигналы', value: '34', unit: 'сигнала', period: 'выпуск 2026-08-25.2', note: 'Датированные отраслевые события', url: 'https://qazaqstan.space/media' },
      { name: 'Проверенные источники', value: '151', unit: 'источник', period: '25 августа 2026', note: 'Государственные, официальные и исследовательские', url: 'https://qazaqstan.space/register' }
    ],
    chain: [
      { title: 'Инфраструктура', text: 'космодромы, центры управления и наземные комплексы' },
      { title: 'Аппараты', text: 'связь, дистанционное зондирование и пусковые системы' },
      { title: 'Данные', text: 'снимки, телеметрия и геопродукты' },
      { title: 'Применение', text: 'связь, картография, мониторинг и управление рисками' }
    ],
    geography: [
      { title: 'Байконур', text: 'Пусковой контур и связанная инфраструктура.' },
      { title: 'Астана', text: 'Национальный космический центр и инженерные функции.' },
      { title: 'Акколь', text: 'Наземная инфраструктура спутниковой связи.' },
      { title: 'Национальный охват', text: 'ДЗЗ и сервисы, работающие поверх географии всей страны.' }
    ],
    coverage: { 'Показатели': 'partial', 'Карта': 'ready', 'Паспорта объектов': 'ready', 'Редакция': 'ready', 'Машинные данные': 'ready', 'Практические сервисы': 'partial', 'Методика и источники': 'ready' },
    gaps: ['Экономический вклад отрасли', 'Занятость и инженерные компетенции', 'Цепочка поставщиков и локализация', 'Сравнение программ и стоимости с другими странами'],
    sources: [
      { label: 'Атлас', url: 'https://qazaqstan.space/atlas' },
      { label: 'Инфраструктура', url: 'https://qazaqstan.space/infrastructure' },
      { label: 'Данные', url: 'https://qazaqstan.space/data' },
      { label: 'Реестр', url: 'https://qazaqstan.space/register' }
    ]
  },
  farm: {
    id: 'farm',
    name: 'Сельское хозяйство',
    short: 'АПК',
    code: '03 / AGRICULTURE',
    sourceName: 'QAZ.FARM',
    sourceUrl: 'https://qaz.farm/',
    sourceReleaseId: '2026-08-21.1',
    release: 'Выпуск 2026-08-21.1 · данные на 24 августа',
    status: 'Сезонный отраслевой продукт',
    summary: 'Статистика производства, состояние сезона, региональные профили, сущности и официальные маршруты поддержки.',
    illustration: {
      alt: 'Абстрактная редакционная иллюстрация: поля, вода, колос, почва и условная инфраструктура хранения.',
      disclosure: 'ИИ-иллюстрация для редакционного контекста; не документальная фотография.',
      sources: [
        { src: 'assets/editorial-media/profile-heroes/farm/derivatives/farm-480w.webp', width: 480 },
        { src: 'assets/editorial-media/profile-heroes/farm/derivatives/farm-960w.webp', width: 960 },
        { src: 'assets/editorial-media/profile-heroes/farm/derivatives/farm-1600w.webp', width: 1600 }
      ]
    },
    photo: {
      alt: 'Спутниковый снимок сельскохозяйственных участков и долин в Казахстане.',
      caption: 'Спутниковый снимок NASA: сезонная структура сельскохозяйственных участков в Казахстане. Это документальный контекст дистанционного зондирования, не текущая статистика.',
      creator: 'NASA Goddard Space Flight Center',
      sourceUrl: 'https://commons.wikimedia.org/wiki/File:Fall_Harvest_in_Kazakhstan_(9936304204).jpg',
      license: 'Public domain',
      licenseUrl: 'https://commons.wikimedia.org/wiki/Commons:Copyright_tags#Public_domain',
      sources: responsiveAssets('assets/editorial-media/profile-context/farm/derivatives/farm-context')
    },
    about: 'Отрасль нельзя читать по одному периоду. Годовой выпуск, оперативные данные, сезонные наблюдения и сервисные маршруты здесь разделены; для каждого указаны границы применимости.',
    kpis: [
      { value: '6', label: 'временных рядов', period: '149 наблюдений' },
      { value: '20', label: 'регионов', period: 'публичные профили' },
      { value: '35', label: 'сущностей', period: 'общий реестр' },
      { value: '75', label: 'источников', period: 'проверенный выпуск' }
    ],
    indicators: [
      { name: 'Валовый выпуск', value: '9 771,5', unit: 'млрд ₸', period: '2025', note: 'Сельское, лесное и рыбное хозяйство', url: 'https://qaz.farm/data/' },
      { name: 'Индекс объёма', value: '105,9', unit: '%', period: '2025 к предыдущему году', note: 'Официальная статистика', url: 'https://qaz.farm/data/' },
      { name: 'Зерно в наличии', value: '6,99', unit: 'млн т', period: 'на 1 июля 2026', note: 'Зерновые и бобовые культуры', url: 'https://qaz.farm/data/' },
      { name: 'Коровье молоко', value: '1,89', unit: 'млн т', period: 'январь–июнь 2026', note: 'Произведено за шесть месяцев', url: 'https://qaz.farm/data/' },
      { name: 'Скот и птица на убой', value: '938,2', unit: 'тыс. т', period: 'январь–июнь 2026', note: 'В живом весе', url: 'https://qaz.farm/data/' },
      { name: 'Куриные яйца', value: '2,38', unit: 'млрд шт.', period: 'январь–июнь 2026', note: 'Произведено за шесть месяцев', url: 'https://qaz.farm/data/' }
    ],
    chain: [
      { title: 'Ресурсы', text: 'земля, вода, семена, корма и техника' },
      { title: 'Производство', text: 'растениеводство и животноводство' },
      { title: 'Переработка', text: 'хранение, пищевая промышленность и упаковка' },
      { title: 'Рынок', text: 'внутреннее потребление, логистика и экспорт' }
    ],
    geography: [
      { title: 'Север', text: 'Зерновые, масличные и крупный полевой сезон.' },
      { title: 'Юг и юго-восток', text: 'Орошаемое земледелие, сады, овощи и ранняя уборка.' },
      { title: 'Запад', text: 'Пастбищное животноводство и водный риск.' },
      { title: 'Центр и восток', text: 'Смешанный профиль и чувствительность к запасам влаги.' }
    ],
    coverage: { 'Показатели': 'ready', 'Карта': 'ready', 'Паспорта объектов': 'partial', 'Редакция': 'ready', 'Машинные данные': 'ready', 'Практические сервисы': 'ready', 'Методика и источники': 'ready' },
    gaps: ['Экономика переработки и маржинальность цепочки', 'Занятость и дефицит навыков', 'Экспортные рынки по продуктам', 'Инфраструктура хранения и логистические ограничения'],
    sources: [
      { label: 'Национальный срез JSON', url: 'https://qaz.farm/data/agri-snapshot.json' },
      { label: 'Карты', url: 'https://qaz.farm/maps/' },
      { label: 'Источники', url: 'https://qaz.farm/sources/' },
      { label: 'Карточка выпуска', url: 'https://qaz.farm/thematic-release.json' }
    ]
  },
  water: {
    id: 'water',
    name: 'Водоёмы и рыболовство',
    short: 'Вода',
    code: '04 / WATER',
    sourceName: 'QAZ.FISH',
    sourceUrl: 'https://qaz.fish/',
    sourceReleaseId: 'qazgeo-20260825T102556931z',
    release: 'Выпуск qazgeo-20260825T102556931z · данные на 25 августа',
    status: 'Географический сервис и база знаний',
    summary: 'Водоёмы, виды рыб, правила, сезонные условия, обучение и подготовка поездки на общей географической основе.',
    illustration: {
      alt: 'Абстрактная редакционная иллюстрация: слои воды, камыш, условный берег и силуэты рыб.',
      disclosure: 'ИИ-иллюстрация для редакционного контекста; не документальная фотография.',
      sources: [
        { src: 'assets/editorial-media/profile-heroes/water/derivatives/water-480w.webp', width: 480 },
        { src: 'assets/editorial-media/profile-heroes/water/derivatives/water-960w.webp', width: 960 },
        { src: 'assets/editorial-media/profile-heroes/water/derivatives/water-1600w.webp', width: 1600 }
      ]
    },
    photo: {
      alt: 'Берег озера Белое в Шортандинском районе Акмолинской области: удочка у воды и степной горизонт.',
      caption: 'Озеро Белое, Шортандинский район, Акмолинская область. Документальный контекст для темы водоёмов и рыболовства.',
      creator: 'Nurken',
      sourceUrl: 'https://commons.wikimedia.org/wiki/File:Beloye_Lake,_Şortandy_District,_Akmola_Region_2.jpg',
      license: 'CC BY 4.0',
      licenseUrl: 'https://creativecommons.org/licenses/by/4.0',
      sources: responsiveAssets('assets/editorial-media/profile-context/water/derivatives/water-context')
    },
    about: 'QAZ.FISH связывает задачу пользователя с каталогом, картой, правилами и материалами для подготовки поездки. Чувствительные точки и личный журнал не публикуются.',
    kpis: [
      { value: '20', label: 'регионов', period: 'география страны' },
      { value: '268', label: 'водных объектов', period: 'публичный каталог' },
      { value: '28', label: 'подробных профилей', period: 'проверенные карточки' },
      { value: '20', label: 'уроков', period: 'практическая академия' }
    ],
    indicators: [
      { name: 'Региональный охват', value: '20', unit: 'регионов', period: 'публичный срез', note: 'Карта Казахстана', url: 'https://qaz.fish/map' },
      { name: 'Каталог водных объектов', value: '268', unit: 'объектов', period: 'публичный срез', note: 'Озёра, реки и водохранилища', url: 'https://qaz.fish/waters' },
      { name: 'Подробные паспорта', value: '28', unit: 'профилей', period: 'публичный срез', note: 'Виды, доступ, сезонность и проверки', url: 'https://qaz.fish/waters' },
      { name: 'Практическая академия', value: '20', unit: 'уроков', period: 'август 2026', note: 'Безопасность, снасти и чтение воды', url: 'https://qaz.fish/learn' }
    ],
    chain: [
      { title: 'Экосистема', text: 'водный объект, режим и состояние среды' },
      { title: 'Ресурс', text: 'виды рыб, сезонность и допустимое использование' },
      { title: 'Доступ', text: 'правила, разрешения, инфраструктура и маршрут' },
      { title: 'Практика', text: 'поездка, безопасность, знания и ответственное поведение' }
    ],
    geography: [
      { title: 'Балхаш–Алаколь', text: 'Крупные озёрные системы и разнообразные сценарии доступа.' },
      { title: 'Иртышский бассейн', text: 'Реки и водохранилища востока страны.' },
      { title: 'Урал–Каспий', text: 'Западный речной и прикаспийский контур.' },
      { title: 'Север и центр', text: 'Степные озёра, водохранилища и сезонные ограничения.' }
    ],
    coverage: { 'Показатели': 'partial', 'Карта': 'ready', 'Паспорта объектов': 'ready', 'Редакция': 'ready', 'Машинные данные': 'ready', 'Практические сервисы': 'ready', 'Методика и источники': 'ready' },
    gaps: ['Промысловая экономика и официальный отраслевой выпуск', 'Состояние запасов по видам и бассейнам', 'Аквакультура и цепочка переработки', 'Занятость, предприятия и инфраструктура отрасли'],
    sources: [
      { label: 'Карта', url: 'https://qaz.fish/map' },
      { label: 'Каталог водоёмов', url: 'https://qaz.fish/waters' },
      { label: 'Правила', url: 'https://qaz.fish/rules' },
      { label: 'Данные и свежесть', url: 'https://qaz.fish/data' }
    ]
  }
};
