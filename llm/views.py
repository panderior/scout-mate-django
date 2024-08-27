from django.shortcuts import render, redirect
from django.http import JsonResponse
from scout_mate.utils import saveFile, generate_unique_token
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from files.serializers import UploadedFileSerializer
from .serializers import JobRequirementSerializer, MatrixScoresSerializer, MatrixWeightsSerializer
from .constants import DOMAIN, EDUCATION, SKILL
from authenticate.serializers import UserSessionSerializer
from files.models import UploadedFileModel
from files.serializers import UploadedFileSerializer
from .models import JobRequirementModel, MatrixWeightsModel, MatrixScoresModel
from .serializers import JobRequirementSerializer, MatrixScoresSerializer, MatrixWeightsSerializer
from scout_mate.settings import BASE_DIR
from .utils import update_vector_db, get_mertics_llm, scouty_chat_llm
import json
from .solar import ChatWithSolar
from dotenv import load_dotenv
from tqdm import tqdm
import os
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_upstage import ChatUpstage
from langchain_upstage import UpstageEmbeddings 
import subprocess
from langchain.vectorstores import Chroma

load_dotenv()
api_key = os.environ.get("SOLAR_API_KEY")

persist_directory = os.path.join(BASE_DIR, 'docs', 'chroma')

filter_embedding = OllamaEmbeddings(model="EEVE-Korean-10.8B-FOR-FILTER:latest", base_url="https://dug-ollama.paz.works")
filter_llm = ChatOllama(model="EEVE-Korean-10.8B-FOR-FILTER:latest", base_url="https://dug-ollama.paz.works", temperature=0)

solar_embedding = UpstageEmbeddings(
    api_key=api_key,
    model="solar-embedding-1-large"
)

solar_llm = ChatUpstage(api_key=api_key, temperature=0)

chat_llm = ChatUpstage(api_key=api_key, temperature=0)

def chat_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        answer = ChatWithSolar(user_message)

        return JsonResponse({"response": answer})

    return JsonResponse({"error": "Invalid request"}, status=400)

class ScoutDataPersistingAPI(generics.GenericAPIView):
    @api_view(['GET'])
    def get_home_page(request, *args, **kwargs):
        return render(request, 'home.html')

    @api_view(['POST'])
    def scout_data_upload(request, *args, **kwargs):
        result = {"success": True, "data": {}, "detail": {} }
        try:
            # create a session instance
            new_session_serializer = UserSessionSerializer(data={"token": generate_unique_token()})
            new_session_serializer.is_valid(raise_exception=True)
            new_session_instance = new_session_serializer.save()

            # save the job requirements data
            # Get the education requirement from the request
            education_requirement = request.POST.get('education_level', '')
            temp_education_req_serializer = JobRequirementSerializer(data={"value": education_requirement, "requirement_type": EDUCATION})
            temp_education_req_serializer.is_valid(raise_exception=True)
            temp_education_req_serializer.save(session=new_session_instance)
            
            # Get the domain_list from the request
            # domains_list = json.loads(request.POST.get('domains_list', '[]'))
            # for temp_domain_val in domains_list:
            #     temp_domain_serializer = JobRequirementSerializer(data={"value": temp_domain_val, "requirement_type": DOMAIN})
            #     temp_domain_serializer.is_valid(raise_exception=True)
            #     temp_domain_serializer.save(session=new_session_instance)

            # # Get the skills_list from the request
            # skills_list = json.loads(request.POST.get('skills_list', '[]'))
            # for temp_skill_val in skills_list:
            #     temp_skill_serializer = JobRequirementSerializer(data={"value": temp_skill_val, "requirement_type": SKILL})
            #     temp_skill_serializer.is_valid(raise_exception=True)
            #     temp_skill_serializer.save(session=new_session_instance)

            # save the metrix weights
            experiance_weight = float(request.POST.get('experiance_weight', ''))
            relevance_weight = float(request.POST.get('relevance_weight', ''))
            education_weight = float(request.POST.get('education_weight', ''))
            skills_weight = float(request.POST.get('skills_weight', ''))
            temp_metrics_weights_data =  {'experiance_weight': experiance_weight, 'relevance_weight': relevance_weight, 'education_weight': education_weight, 'skill_weight': skills_weight}
            
            temp_metrics_weights_serializer = MatrixWeightsSerializer(data=temp_metrics_weights_data)
            temp_metrics_weights_serializer.is_valid(raise_exception=True)
            temp_metrics_weights_serializer.save(session=new_session_instance)

            # remove chroma db
            try:
                delete_cmd = f'rm -rf {persist_directory}'
                process_result = subprocess.run(delete_cmd, shell=True)
                print(process_result)
            except Exception as exp:
                print(exp)

            # save the list of files with the session instance
            applicants_metrics_data_dir = {}
            vectordb = None
            files = request.FILES.getlist('files')
            for i, one_file in tqdm(enumerate(files)):
                temp_file_path = saveFile(one_file)
                temp_file_serializer = UploadedFileSerializer(data={"file_path": temp_file_path})
                temp_file_serializer.is_valid(raise_exception=True)
                temp_file_instance = temp_file_serializer.save(session=new_session_instance)

                candidate_num = f"Candidate No.{i+1}"
                vectordb = update_vector_db(candidate_num=candidate_num, file_name=temp_file_path, 
                                            filter_embedding=filter_embedding, filter_llm=filter_llm,
                                            solar_embedding=solar_embedding, solar_llm=solar_llm)
                
                applicants_metrics_data_dir[candidate_num] = temp_file_instance
            
            print("**** Vectordb count: ", vectordb._collection.count())
            metrics_result_text = get_mertics_llm(vectordb, "senior", "data scientist")
            print(metrics_result_text)
            parsed_metrics_json = json.loads(metrics_result_text)
            for candidate, details in parsed_metrics_json.items():
                temp_file_instance = applicants_metrics_data_dir[candidate]
                temp_applicant_score_data = {
                    'candidate_name': candidate,
                    'experiance_score': details["experience"], 
                    'relevance_score': details["relevance"],
                    'education_score': details["education"],
                    'skill_score': details["skills"]
                }
                temp_applicant_score_serializer = MatrixScoresSerializer(data=temp_applicant_score_data)
                temp_applicant_score_serializer.is_valid(raise_exception=True)
                temp_applicant_score_serializer.save(uploaded_file=temp_file_instance)

            # send response data with the session id
            result["data"]["session_id"] = new_session_instance.id
            return Response(result, status=status.HTTP_200_OK) 
        except Exception as exp:
            print(exp)
            result["success"] = False
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

class ScoutResultsAPI(generics.GenericAPIView):
    @api_view(['GET'])
    def get_scout_page(request, *args, **kwargs):
        try:
            session_id = int(kwargs.get('id'))
            temp_metrics_weights_instance = MatrixWeightsModel.objects.get(session__id=session_id)
            temp_metrics_weights_data = MatrixWeightsSerializer(temp_metrics_weights_instance).data

            temp_applicants_score_instance = MatrixScoresModel.objects.filter(uploaded_file__session__id=session_id)
            temp_applicants_score_data = MatrixScoresSerializer(temp_applicants_score_instance, many=True).data
            
            
            context = {
                "metrics_weights": temp_metrics_weights_data,
                "applicant_scores": temp_applicants_score_data
            }
            
            return render(request, 'scout.html', context=context)
        except Exception as exp:
            print(exp)
            return redirect('home') 
        
    @api_view(['POST'])    
    def scouty_chat(request, *args, **kwargs):
        try:
            vectordb = Chroma.from_texts(
                texts=[" "],
                embedding=solar_embedding,
                persist_directory=persist_directory
            )
            print(vectordb._collection.count())

            data = json.loads(request.body)
            user_message = data.get("message", "")
            metrix_result = get_mertics_llm(vectordb, "senior", "data scientist")
            answer = scouty_chat_llm(vectordb, metrix_result, user_message)
            print(answer)

            return JsonResponse({"response": answer})
        except Exception as exp:
            print(exp)

        