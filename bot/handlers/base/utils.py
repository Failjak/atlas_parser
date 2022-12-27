from parser.dto import ParserDto


def generate_final_route(parser_dto: ParserDto):
    return f"{parser_dto.departure_place.capitalize()} --> {parser_dto.arrival_place.capitalize()}"
