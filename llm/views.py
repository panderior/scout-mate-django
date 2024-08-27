from django.shortcuts import render
from django.http import JsonResponse
from scout_mate.utils import saveFile, generate_unique_token
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from files.serializers import UploadedFileSerializer
from .serializers import JobRequirementSerializer, MatrixScoresSerializer, MatrixWeightsSerializer
from .constants import DOMAIN, EDUCATION, SKILL
from authenticate.serializers import UserSessionSerializer
import json
from .solar import ChatWithSolar

def hello(request):
    return render(request, "home.html")

def scout(request):
    return render(request, "scout.html")


def upload_view(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        for file in files:
            with open(os.path.join(BASE_DIR, 'users_data', file.name), 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        return JsonResponse({'success': True})
    return render(request, 'home.html')

class ScoutDataPersistingAPI(generics.GenericAPIView):
    @api_view(['POST'])
    def scout_data_upload(request, *args, **kwargs):
        result = {"success": True, "data": {}, "detail": {} }
        try:
            # create a session instance
            new_session_serializer = UserSessionSerializer(data={"token": generate_unique_token()})
            new_session_serializer.is_valid(raise_exception=True)
            new_session_instance = new_session_serializer.save()

            # save the list of files with the session instance
            files = request.FILES.getlist('files')
            for one_file in files:
                temp_file_path = saveFile(one_file)
                temp_file_serializer = UploadedFileSerializer(data={"file_path": temp_file_path})
                temp_file_serializer.is_valid(raise_exception=True)
                temp_file_instance = temp_file_serializer.save(session=new_session_instance)

            # save the job requirements data
            # Get the education requirement from the request
            education_requirement = request.POST.get('education_level', '')
            temp_education_req_serializer = JobRequirementSerializer(data={"value": education_requirement, "requirement_type": EDUCATION})
            temp_education_req_serializer.is_valid(raise_exception=True)
            temp_education_req_serializer.save(session=new_session_instance)
            
            # Get the domain_list from the request
            domains_list = json.loads(request.POST.get('domains_list', '[]'))
            for temp_domain_val in domains_list:
                temp_domain_serializer = JobRequirementSerializer(data={"value": temp_domain_val, "requirement_type": DOMAIN})
                temp_domain_serializer.is_valid(raise_exception=True)
                temp_domain_serializer.save(session=new_session_instance)

            # Get the skills_list from the request
            skills_list = json.loads(request.POST.get('skills_list', '[]'))
            for temp_skill_val in skills_list:
                temp_skill_serializer = JobRequirementSerializer(data={"value": temp_skill_val, "requirement_type": SKILL})
                temp_skill_serializer.is_valid(raise_exception=True)
                temp_skill_serializer.save(session=new_session_instance)
                
            # save the metrix weights
            experiance_weight = float(request.POST.get('experiance_weight', ''))
            relevance_weight = float(request.POST.get('relevance_weight', ''))
            education_weight = float(request.POST.get('education_weight', ''))
            skills_weight = float(request.POST.get('skills_weight', ''))
            temp_metrics_weights_data =  {'experiance_weight': experiance_weight, 'relevance_weight': relevance_weight, 'education_weight': education_weight, 'skill_weight': skills_weight}
            
            temp_metrics_weights_serializer = MatrixWeightsSerializer(data=temp_metrics_weights_data)
            temp_metrics_weights_serializer.is_valid(raise_exception=True)
            temp_metrics_weights_serializer.save(session=new_session_instance)


            # send response data with the session id
            result["data"]["session_id"] = new_session_instance.id
            return Response(result, status=status.HTTP_200_OK) 
        except Exception as exp:
            print(exp)
            result["success"] = False
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

def chat_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        answer = ChatWithSolar(user_message)

        return JsonResponse({"response": answer})

    return JsonResponse({"error": "Invalid request"}, status=400)