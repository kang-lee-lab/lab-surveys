"""General utility functions"""


def process_response_query(
    response_results: list, process_results: bool = False
) -> (list, list):
    data = []
    responses = []
    for response in response_results:
        temp = []
        temp.append(response.id)
        temp.append(response.time_stamp)
        string = response.response_answers
        string = string.replace("{", "")
        string = string.replace("'", "")
        string = string.replace("}", "")
        response_list = [string.split(","), response.id]
        responses.append(response_list)

        if process_results:
            response_str = response.response_results
            response_str = response_str.replace("{", "")
            response_str = response_str.replace("}", "")
            response_str = response_str.replace("'", "")
            temp.append(response_str)
        else:
            temp.append(round(float(response.response_results), 3))

        data.append(temp)

    return responses, data
