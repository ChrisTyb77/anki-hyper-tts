import io
from hypertts_addon import service, voice, languages, logging_utils, constants, errors
from typing import List
import requests
logger = logging_utils.get_child_logger(__name__)

# 🇺🇸 'a' => American English 
# 🇬🇧 'b' => British English
# 🇪🇸 'e' => Spanish es
# 🇫🇷 'f' => French fr-fr
# 🇮🇳 'h' => Hindi hi
# 🇮🇹 'i' => Italian it
# 🇯🇵 'j' => Japanese
# 🇧🇷 'p' => Brazilian Portuguese pt-br
# 🇨🇳 'z' => Mandarin Chinese

AMERICAN_ENGLISH_VOICES = [
    "af_heart",
    "af_bella",
    "af_nicole"
]

BRITISH_ENGLISH_VOICES = [
    "bf_emma"
]

LangId = languages.AudioLanguage
LANGUAGE_MAP ={
    LangId.en_US: "a",
    LangId.en_GB: "b"
}


class KokoroTTS(service.ServiceBase):
    CONFIG_API_URL = 'api_url'

    def __init__(self):
        service.ServiceBase.__init__(self)
    
    def cloudlanguagetools_enabled(self):
        return True

    def configuration_options(self):
        return {
            self.CONFIG_API_URL: str
        }

    @property
    def service_type(self) -> constants.ServiceType:
        return constants.ServiceType.tts

    @property
    def service_fee(self) -> constants.ServiceFee:
        return constants.ServiceFee.free
    
    def voice_list(self) -> List[voice.TtsVoice_v3]:
        voices = []
        
        # American English voices
        for voice_key in AMERICAN_ENGLISH_VOICES:
            voices.append(voice.build_voice_v3(
                    name=voice_key,
                    gender=constants.Gender.Any,
                    language=LangId.en_US,
                    service=self,
                    voice_key=voice_key,
                    options={}
                ))
            
        # British English voices
        for voice_key in BRITISH_ENGLISH_VOICES:
            voices.append(voice.build_voice_v3(
                    name=voice_key,
                    gender=constants.Gender.Any,
                    language=LangId.en_GB,
                    service=self,
                    voice_key=voice_key,
                    options={}
                ))

        return voices
    

    def get_tts_audio(self, source_text, voice: voice.TtsVoice_v3, options):
        try:
            api_url = self.get_configuration_value_mandatory(self.CONFIG_API_URL)
            endpoint = f"{api_url}/v1/audio/speech"

            lang_key = LANGUAGE_MAP.get(voice.languages[0], "a")

            response = requests.post(
                endpoint,
                json={
                    "model": "kokoro",  
                    "input": source_text,
                    "voice": voice.voice_key,
                    "lang_code": lang_key,
                    "response_format": "mp3",
                    "speed": 1.0
                }
            )
            response.raise_for_status()

            return response.content
        except Exception as e:
            logger.warning(f'exception while retrieving sound for {source_text}: {e}')
            raise errors.RequestError(source_text, voice, str(e))