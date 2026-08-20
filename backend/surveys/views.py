import csv

from django.http import HttpResponse, JsonResponse
from surveys.survey_registry import build_survey_catalog, get_survey_file_path
from surveys.utils.asq.asq_survey import asq_calculate_results
from surveys.utils.child_bmi.child_bmi_survey import child_bmi_calculate_results
from surveys.utils.child_bmi.child_bmi_survey import MODEL_VERSION as CHILD_BMI_MODEL_VERSION
from surveys.utils.dass.dass_survey import dass_calculate_results
from surveys.utils.mmpi.mmpi_survey import mmpi_calculate_results
from surveys.utils.nafld.nafld_survey import nafld_calculate_results
from surveys.utils.dass_multiclass.dass_multiclass_survey import dass_multiclass_calculate_results
from surveys.utils.sample_survey.sample_survey import sample_survey_calculate_results
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Response
from datetime import datetime
from django.forms.models import model_to_dict
from datetime import timedelta

from typing import List, Any

import logging
import collections
if not hasattr(collections, 'Mapping'):
    import collections.abc
    collections.Mapping = collections.abc.Mapping


logger = logging.getLogger(__name__)

def post_to_db(response_type, response_answers, response_results, response_duration):
    time = datetime.now()
    date = time.date()
    # change response_duration to seconds
    duration_timedelta = timedelta(seconds=response_duration)
    
    r = Response(response_type=response_type, 
                 response_answers=response_answers, 
                 response_results=response_results, 
                 response_date=date,
                 response_time=time,
                 response_duration=duration_timedelta)
                
    r.save()
    
def call_from_db_all():
    return Response.objects.all()


def call_from_db_id(id):
    return Response.objects.all().filter(id=id)


def index(request):
    r = Response(2, "asq", "test1", "test2", datetime.now())
    r.save()
    return HttpResponse("Hello, world. You're at the survey.")


@csrf_exempt
def calculate_results(request):
    # throw error if it is not a POST request
    if request.method != "POST":
        data = {"message": "Only POST requests are allowed."}
        return JsonResponse(data, status=400)

    # else call appropriate survey to calculate the results
    request_body = json.loads(request.body.decode("utf-8"))

    data = {}
    try:
        response_type = request_body["survey"]
        
        if request_body["survey"] == "asq":
            results, metadata, asq_result, sq_result = asq_calculate_results(
                request_body["data"], "EN"
            )
            data["asq_result"] = asq_result
            data["sq_result"] = sq_result
            
            db_result = dict(sq_result)
            db_result["result"] = asq_result
            data["db_result"] = db_result

        elif request_body["survey"] == "child_bmi":
            (
                results,
                metadata,
                pred_height,
                pred_weight,
                pred_bmi,
            ) = child_bmi_calculate_results(request_body["data"], "EN")
            data["pred_height"] = pred_height
            data["pred_weight"] = pred_weight
            data["pred_bmi"] = pred_bmi
            data["age_to_predict"] = request_body["data"]["Age to predict"]
            # Reported so a stored prediction can be attributed to the model that
            # produced it; callers previously had to hardcode a version string.
            data["model_version"] = CHILD_BMI_MODEL_VERSION
            data["db_result"] = {"Predicted Height (cm)": pred_height, "Predicted Weight (kg)": pred_weight, "Predicted BMI (kg/m²)": pred_bmi}
        elif request_body["survey"] == "dass":
            results, metadata, positive = dass_calculate_results(
                request_body["data"], request_body["mode"], "EN"
            )
            data["positive"] = positive
            data["mode"] = request_body["mode"]
            response_type = request_body["mode"] + "_moderate"
            data["db_result"]  = {request_body["mode"] + " percentage": float(results)*100} 
        elif request_body["survey"] == "mmpi":
            results, metadata, positive_proba = mmpi_calculate_results(
                request_body["data"], "EN"
            )
            data["positive"] = positive_proba
            # Convert results string to a dictionary
            cleaned_results = results.strip('\"').replace('\\\"', '\"')
            result_dict = json.loads(cleaned_results)
            data["db_result"] = result_dict
        elif request_body["survey"] == "nafld":
            results, metadata, positive = nafld_calculate_results(
                request_body["data"], "EN"
            )
            data["positive"] = positive
            data["db_result"]  = {"Likelihood of NAFLD (%)":  float(results)*100}
        elif request_body["survey"] == "dass_multiclass":
            results, metadata, severity_level, rank = dass_multiclass_calculate_results(request_body["data"], request_body["mode"])
            response_type = request_body["mode"].replace("-", "_")
            data["db_result"] = results
            data["rank"] = rank
            data["severity_level"] = severity_level
        elif request_body["survey"] == "sample_survey":
            (
                results,
                metadata,
                scalar_score,
                likelihood,
                summary_text,
            ) = sample_survey_calculate_results(request_body["data"], "EN")
            data["scalar_score"] = scalar_score
            data["positive"] = likelihood
            data["likelihood"] = likelihood
            data["summary_text"] = summary_text
            data["db_result"] = {
                "Scalar score (sum)": scalar_score,
                "Experience rating (%)": likelihood * 100,
                "Summary": summary_text,
            }
                        
        else:
            data = {"message": "This survey type is invalid."}
            return JsonResponse(data, status=400)
        data["results"] = results
        data["metadata"] = metadata
        duration = request_body["duration"]
        # TODO: Uncomment this line to save the results to the database
        # post_to_db(response_type, json.dumps(request_body["data"]), json.dumps(data["db_result"]), duration)
    except Exception as e:
        logger.error(f"Error while calculating survey results: {e}")
        data = {"message": "There was an error while calculating the survey results."}
        return JsonResponse(data, status=500)
    return JsonResponse(data, status=200)


@csrf_exempt
def get_consent_file_path(survey_folder: str) -> str:
    if survey_folder == "manga_consent":
        return "surveys/static/survey_files/manga/manga-consent.json"


def get_survey(request, id):
    if request.method != "GET":
        data = {"message": "Only GET requests are allowed."}
        return JsonResponse(data, status=400)
    try:
        json_file_path = get_survey_file_path(id)
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {"message": f"Survey file not found for survey_folder: {id}"}
        return JsonResponse(data, status=500)
    except Exception as e:
        data = {"message": f"Error while processing the survey: {str(e)}"}
        return JsonResponse(data, status=500)

    return JsonResponse(data, status=200)


def list_surveys_catalog(request):
    """
    GET: Returns all surveys grouped by metadata survey_type (physical,
    psychological, physiological, other). Each entry includes route_id for
    GET /surveys/survey/<route_id> and submit hints for POST /surveys/results.
    """
    if request.method != "GET":
        data = {"message": "Only GET requests are allowed."}
        return JsonResponse(data, status=400)
    try:
        payload = build_survey_catalog()
    except Exception as e:
        logger.error(f"Error building survey catalog: {e}")
        data = {"message": "There was an error while loading the survey catalog."}
        return JsonResponse(data, status=500)
    return JsonResponse(payload, status=200)


def get_survey_questions(request, survey_folder: str) -> List[Any]:
    try:
        json_file_path = get_survey_file_path(survey_folder)
        with open(json_file_path, "r") as f:
            survey = json.load(f)
        questions = survey.get('pages', [])[0].get('questions', [])
    except FileNotFoundError:
        data = {"message": f"Survey file not found for survey_folder: {survey_folder}"}
        return JsonResponse(data, status=500)
    except Exception as e:
        data = {"message": f"Error while processing the survey: {str(e)}"}
        return JsonResponse(data, status=500)

    return questions


def get_history(request):
    data = Response.objects.all()
    serialized_data = [model_to_dict(item) for item in data]
    return JsonResponse(serialized_data, safe=False)

def history_view(request, response_type):
    # Filter data based on response_type
    filtered_responses = Response.objects.filter(response_type=response_type)
    response_data = []
    for response in filtered_responses:
        questions = get_survey_questions(request, response.response_type)
        response_data.append({
            'id': response.id,
            'response_type': response.response_type,
            'response_answers': response.response_answers,
            'response_results': response.response_results,
            'response_date': response.response_date.strftime("%Y-%m-%d"),
            'response_time': response.response_time.strftime("%H:%M:%S"),
            'response_duration': response.response_duration.total_seconds(),
            'questions': questions,
        })

    return JsonResponse(response_data, safe=False)

def download_csv(request):
    data = Response.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Response Answers', 'Response Results', 'Response Date', 'Response Time', 'Response Duration'])

    for row in data:
        writer.writerow([row.id, row.response_answers, row.response_results, row.response_date,row.response_time, row.response_duration])

    return response

def get_survey_consent(request, id):
    try:
        json_file_path = get_consent_file_path(id)
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {"message": f"Survey consent file not found for survey_folder: {id}"}
        return JsonResponse(data, status=500)
    except Exception as e:
        data = {"message": f"Error while processing the survey: {str(e)}"}
        return JsonResponse(data, status=500)

    return JsonResponse(data, status=200)
