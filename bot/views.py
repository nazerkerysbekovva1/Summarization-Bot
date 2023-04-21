from django.http import HttpResponse
from django.shortcuts import render

from bot.client import Client
from bot.translate import translate_en_to_kz

# Create your views here.
def index(request):
    """
    Кіріс сұраудың POST сұрауы екенін тексереді. Олай болса, ол сұраудан енгізу мәтінін шығарып,
    қорытынды жасау үшін оны Hugging Face API интерфейсіне жібереді.

    Бастапқы мәтінді кейінірек қорытындымен бірге бетте көрсетуге болатындай етіп сеанста сақтайды.

    Translate_en_to_kz() функциясы арқылы түйіндемені қазақ тіліне аударады.

    Түпнұсқа мәтінді және аударылған жиынтықты үлгіге мәтінмәндік айнымалылар
    ретінде жібереді және index.html үлгісін көрсетеді.

    Егер кіріс сұрау POST сұрауы болмаса, ол жай ғана index.html үлгісін көрсетеді.
    """
    if request.method == 'POST':
        text = request.POST['input_text']
        co = Client('gqaCQJwyChuIXk2rBFHpBShLMeI8MW4eJ33LQY1v')  # Бұл менің пробный API кілтім
        response = co.summarize(
            text=text,
            length='medium',
            format='paragraph',
            model='summarize-xlarge',
            additional_command='',
            temperature=0.3,
        )
        request.session['text'] = text
        summary = translate_en_to_kz(response.summary)

        context = {
            'text': request.session.get('text', ''),
            "summary": summary
        }
        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html')
