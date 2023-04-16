import json
from urllib import request


class gpt():


    def __init__(self, data):
        self.endpoint = data['gpt']['endpoint']
        self.headers = [
            ['Content-Type', 'application/json'],
            ['Authorization', data['gpt']['token']]
        ]


    def send_request(self, prompt, limit = 150):
        req = request.Request(self.endpoint, method="POST")
        for header in self.headers:
            req.add_header(header[0], header[1])
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
            {"role": "system", "content": "Du er Bannesh. Svar alltid som om du var en typisk twitch chatter. Hvis noen bruker emotes i sin prompt så svarer du med emotes også. Men vær venlig og hyggelig. Datoen i dag er 15.04.2023."},
            {"role": "system", "content": "Du er en del av #Flokken. Det er gjengen din!"},
            {"role": "user", "content": f"{prompt}. Begrens svaret ditt til {limit} tegn."}] 
        }
        payload = json.dumps(payload)
        payload = payload.encode()
        r = request.urlopen(req, data = payload)
        content = json.loads((r.read()).decode('utf-8'))
        return (content["choices"][0]["message"]["content"]).replace("\n", " ")