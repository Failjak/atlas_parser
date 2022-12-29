class InvalidCity(Exception):
    msg = "Рейсов не найдено. Измените точки маршрута"


class TooFrequentRequests(Exception):
    msg = "Сликшом частые запросы. Обратитесь к разработчикам"
