from openai import OpenAI, RateLimitError, Timeout
from dotenv import load_dotenv
import backoff
import os
import json

class LLM:
    """Abstract, parent class the children classes of which will be in charge of the system-LLM interaction.
    -2 functions are implemented by the children classes, namely build_prompt (prompt formatting according to the LLm format) and generate_stream_response
    (feed the prompt to the LLM, return its response while streaming the response)
    """
    def __init__(self) -> None:
        pass
    
    def build_prompt(system_prompt, examples, inst_prompt, images_encoded):
        pass
    
    def generate_stream_response(self, prompt, temperature, max_new_tokens, additional_sampling_parameters) -> str:
        pass

    def generate_structured_response(self, prompt, temperature, max_new_tokens, additional_sampling_parameters) -> str:
        pass

    
    def clean_tokens(self, token):        
        return token.replace("\n", "  \n").replace("```json", "").replace("```", "")
 
class OpenAI_Generic(LLM):
    def __init__(self, client, model, sampling_parameters = None) -> None:
        self.client = client
        self.model = model        
        self.sampling_parameters = sampling_parameters
    
    def build_prompt(self, system_prompt, examples, inst_prompt):
        """Prompt builder for OpenAI. It can take previous messages to enable in-context learning. It can also take images (if the underlying LLM supports it).

        Args:
            system_prompt (str): system prompt
            examples (list of dicts): previous messages, enabling in-context learning
            inst_prompt (str): instruction/user prompt
            image_encoded (str, optional): base64-encoded image. Defaults to None.

        Returns:
            str: formatted prompt
        """
        prompt_messages = []
        # IF ANY, WE ADD THE SYSTEM PROMPT
        if system_prompt != "" and system_prompt is not None:
            prompt_messages.append({"role":"system","content": [{
                    'type': 'text',
                    'text': system_prompt,
                }]})
        # IF ANY HISTORIC/FEW-SHOT PROMPTING, WE ITERATE OVER A LIST OF DICTS WITH INPUT-OUTPUT AND FORMAT THEM AS USER-ASSISTANT INTER.
        if examples is not None and len(examples) > 0:
            for i, example in enumerate(examples):
                prompt_messages.append({"role":"user","content": [{
                    'type': 'text',
                    'text': example["input"],
                }]})
                prompt_messages.append({"role":"assistant","content": [{
                    'type': 'text',
                    'text': example["output"],
                }]})

        # WE ADD THE TEXTUAL USER PROMPT AS AN USER MESSAGE
        prompt_messages.append({"role":"user","content": [{
                    'type': 'text',
                    'text': inst_prompt,
                }]})
                
        return prompt_messages
    
    @backoff.on_exception(backoff.expo, RateLimitError, max_tries=10)
    def generate_stream_response(self, prompt, temperature, max_new_tokens, additional_sampling_parameters = None, clean_code_tags_markdown = True):
        """Feeds the LLM with a fully-formatted prompt, streams its generation and returns the LLM response

        The inherent LLM's sampling parameters setted up (if any) will be taken into account, and the additional ones optionally
        passed will be also used, combining those with the LLM specific ones

        Args:
            prompt (str): fully-formatted prompt
            temperature (float): LLM temperature to use
            max_new_tokens (int): max new tokens to generate by the LLM
            additional_sampling_parameters (dict, optional): dict of additional sampling parameters to use when generating. Defaults to None.                

        Returns:
            str: LLM response

        Yields:
            Iterator[str]: LLM streamed response
        """        
        full_response = ''
        model_args = {
            "model": self.model,
            "messages": prompt,
            "temperature": temperature,
            "max_tokens": max_new_tokens,            
            "stream": True,
        }
        if self.sampling_parameters:
            model_args.update(self.sampling_parameters)
        if additional_sampling_parameters:
            for k, v in additional_sampling_parameters.items():
                if k in model_args.keys():
                    model_args[k] += v
                else:
                    model_args[k] = v
        for chunk in self.client.chat.completions.create(**model_args):
            if len(chunk.choices) > 0:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    if content is not None:                        
                        full_response += content                        
                        yield f'%s' % (self.clean_tokens(content) if clean_code_tags_markdown else content)
        return full_response
    
    @backoff.on_exception(backoff.expo, RateLimitError, max_tries=10)
    def generate_response(self, prompt, temperature, max_new_tokens, additional_sampling_parameters = None):
        """Feeds the LLM with a fully-formatted prompt, and returns the LLM response

        The inherent LLM's sampling parameters setted up (if any) will be taken into account, and the additional ones optionally
        passed will be also used, combining those with the LLM specific ones

        Args:
            prompt (str): fully-formatted prompt
            temperature (float): LLM temperature to use
            max_new_tokens (int): max new tokens to generate by the LLM
            additional_sampling_parameters (dict, optional): dict of additional sampling parameters to use when generating. Defaults to None.                

        Returns:
            str: LLM response        
        """
        model_args = {
            "model": self.model,
            "messages": prompt,
            "temperature": temperature,
            "max_tokens": max_new_tokens,  
        }
        if self.sampling_parameters:
            model_args.update(self.sampling_parameters)
        if additional_sampling_parameters:
            for k, v in additional_sampling_parameters.items():
                if k in model_args.keys():
                    model_args[k] += v
                else:
                    model_args[k] = v
                
        return self.clean_tokens(self.client.chat.completions.create(**model_args).choices[0].message.content)
    
    @backoff.on_exception(backoff.expo, RateLimitError, max_tries=10)
    def generate_structured_response(self, prompt, response_schema, temperature, max_new_tokens, additional_sampling_parameters = None):
        """Feeds the LLM with a fully-formatted prompt, and returns the LLM response

        The inherent LLM's sampling parameters setted up (if any) will be taken into account, and the additional ones optionally
        passed will be also used, combining those with the LLM specific ones

        Args:
            prompt (str): fully-formatted prompt
            temperature (float): LLM temperature to use
            max_new_tokens (int): max new tokens to generate by the LLM
            additional_sampling_parameters (dict, optional): dict of additional sampling parameters to use when generating. Defaults to None.                

        Returns:
            str: LLM response        
        """
        model_args = {
            "model": self.model,
            "messages": prompt,
            "temperature": temperature,
            "max_tokens": max_new_tokens,
            "response_format": response_schema
        }
        if self.sampling_parameters:
            model_args.update(self.sampling_parameters)
        if additional_sampling_parameters:
            for k, v in additional_sampling_parameters.items():
                if k in model_args.keys():
                    model_args[k] += v
                else:
                    model_args[k] = v
                
        return json.loads(self.client.beta.chat.completions.parse(**model_args).choices[0].message.content)
    
class GenericLLM(OpenAI_Generic):
    def __init__(self) -> None:
        """The constructor gets the backend LLM serving's endpoint from the .env file       

        Raises:
            ValueError: If the LLM is not deployed
        """
        load_dotenv()
        base_url=os.getenv("LLM_ENDPOINT")        

        if base_url is not None and base_url != "":        
            client = OpenAI(
                base_url=base_url,
                api_key=os.getenv("LLM_API_KEY"),
                timeout=Timeout(120.0, connect=10.0),
                max_retries=10
            )
            model = os.getenv("LLM_MODEL_NAME")
            sampling_parameters = None
            OpenAI_Generic.__init__(self, client, model, sampling_parameters)
        else:
            raise ValueError("The selected model is not deployed.")