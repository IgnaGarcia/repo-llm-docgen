"""
analisis de codigo estatico para obtener datos estructurados sobre el codigo

TARGET:
{
    "content": [
        {
            "object-type": "class | struct | function | attribute | param | return",
            "name": "LLMService",
            "content": [
                {
                    "type": "attribute",
                    "name": "model_name",
                    "content": "string"
                },
                {
                    "type": "attribute",
                    "name": "model_large",
                    "content": "int"
                },
                {
                    "type": "function",
                    "name": "__init__",
                    "content": [
                        {
                            "type": "param",
                            "name": "bla",
                            "content": "str"
                        },
                        {
                            "type": "return",
                            "name": "some",
                            "content": "any"
                        }
                    ]
                }
            ]
        }
    ]
}
"""
