'''
Author       : bughero jinxinhou@tuputech.com
Date         : 2023-12-06 10:24:30
LastEditors  : bughero jinxinhou@tuputech.com
LastEditTime : 2023-12-06 10:29:28
FilePath     : /DeepLearning/python/DeepLearningPython/langchain/test_vertexai.py
Description  : 

Copyright (c) 2023 by Antyme, All Rights Reserved. 
'''
import vertexai
from vertexai.language_models import TextGenerationModel


def interview(
    temperature: float,
    project_id: str,
) -> str:
    """Ideation example with a Large Language Model"""

    # vertexai.init(project=project_id, location=location)
    vertexai.init(project=project_id)
    # TODO developer - override these parameters as needed:
    parameters = {
        # Temperature controls the degree of randomness in token selection.
        "temperature": temperature,
        # Token limit determines the maximum amount of text output.
        "max_output_tokens": 256,
        # Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value.
        "top_p": 0.8,
        # A top_k of 1 means the selected token is the most probable among all tokens.
        "top_k": 40,
    }

    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict(
        "Give me ten interview questions for the role of program manager.",
        **parameters,
    )
    print(f"Response from Model: {response.text}")

    return response.text


if __name__ == "__main__":
    interview(0.1, "630514417281")
