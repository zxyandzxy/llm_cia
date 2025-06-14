from openai import OpenAI
from dotenv import load_dotenv
from abc import ABC

class OpenAIEngine(ABC):
    def __init__(self, model_type="qwen-plus"):
        load_dotenv()
        self._client = OpenAI(
            api_key="",  # YOUR-API-KEY
            base_url=""
        )
        self.FUNCTION_FUNC1_DESCRIPTIONS = [
            {
                "type": "function",
                "function": {
                    "name": "get_co_change_relationship",
                    "description": "This function takes a target entity as a parameter, and applies data mining to the project's version history to get the recommended synchronised changes, i.e. based on the fact that ‘the programmer who modified this entity in the past also modified ....’. The function will return an array where each element is (the entity name,  the number of supports, the confidence). The explanation of the number of supports and confidence is as follows: if the target entity is A.java, in the version history of A.java has been modified 8 times, at the same time in these 8 modifications of B.java appeared 7 times, then the number of supports is 7, the confidence is 7/8 = 0.875",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "File name of the target entity",
                            }
                        },
                        "required": ["entity"]
                    },
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "description": "{the entity name,  the number of supports, the confidence}",
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_conceptual_coupling",
                    "description": "This function calculates the semantic similarity of the code of two entities through natural language processing techniques, specified by the cosine similarity, and returns the semantic similarity probability of the two entities.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity1": {
                                "type": "string",
                                "description": "File name of the first entity",
                            },
                            "entity2": {
                                "type": "string",
                                "description": "File name of the second entity",
                            }
                        },
                        "required": ["entity1", "entity2"]
                    },
                    "return": {
                        "type": "double",
                        "description": "the semantic similarity probability of the two entities",
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_call_graph",
                    "description": "This function parses out the call information in the target entity, and if another entity is used by the target entity (either through a method call or a direct reference to a variable), then that entity is used as one of the elements of the result array.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "the file need to analysis",
                            },
                        },
                        "required": ["entity"],
                    },
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Name of the entity to be called in the target entity",
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_origin_code",
                    "description": "This function takes one parameter: the name of the entity to be analysed, and returns the source code information for this entity as a string (Remove comment information and extra blank lines)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "the file need to analysis",
                            }
                        },
                        "required": ["entity"]
                    },
                    "return": {
                        "type": "string",
                        "items": {
                            "type": "string",
                            "description": "the source code information for this entity",
                        }
                    }
                }
            }
        ]
        self.FUNCTION_FUNC3_DESCRIPTIONS = [
            {
                "type": "function",
                "function": {
                    "name": "get_coupling_dependencies",
                    "description": "This function takes two entities as input and returns the coupling dependencies that exist between the two entities. There are 18 types of coupling dependencies, including Inheritance(IH), Implementing Interface(II), Instanceof (IO), Return Type (RT), and Exception Throws (ET), etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity1": {
                                "type": "string",
                                "description": "File name of the first entity",
                            },
                            "entity2": {
                                "type": "string",
                                "description": "File name of the second entity",
                            }
                        },
                        "required": ["entity1", "entity2"]
                    },
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "the coupling relationship between two entity",
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_co_change_relationship",
                    "description": "This function takes a target entity as a parameter, and applies data mining to the project's version history to get the recommended synchronised changes, i.e. based on the fact that ‘the programmer who modified this entity in the past also modified ....’. The function will return an array where each element is (the entity name,  the number of supports, the confidence). The explanation of the number of supports and confidence is as follows: if the target entity is A.java, in the version history of A.java has been modified 8 times, at the same time in these 8 modifications of B.java appeared 7 times, then the number of supports is 7, the confidence is 7/8 = 0.875",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "File name of the target entity",
                            }
                        },
                        "required": ["entity"]
                    },
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "description": "{the entity name,  the number of supports, the confidence}",
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_call_graph",
                    "description": "This function parses out the call information in the target entity, and if another entity is used by the target entity (either through a method call or a direct reference to a variable), then that entity is used as one of the elements of the result array.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "the file need to analysis",
                            },
                        },
                        "required": ["entity"],
                    },
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Name of the entity to be called in the target entity",
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_origin_code",
                    "description": "This function takes one parameter: the name of the entity to be analysed, and returns the source code information for this entity as a string (Remove comment information and extra blank lines)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "the file need to analysis",
                            }
                        },
                        "required": ["entity"]
                    },
                    "return": {
                        "type": "string",
                        "items": {
                            "type": "string",
                            "description": "the source code information for this entity",
                        }
                    }
                }
            }]
        self.FUNCTION_FUNC4_DESCRIPTIONS = [
            {
                "type": "function",
                "function": {
                    "name": "get_coupling_dependencies",
                    "description": "This function takes two entities as input and returns the coupling dependencies that exist between the two entities. There are 18 types of coupling dependencies, including Inheritance(IH), Implementing Interface(II), Instanceof (IO), Return Type (RT), and Exception Throws (ET), etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity1": {
                                "type": "string",
                                "description": "File name of the first entity",
                            },
                            "entity2": {
                                "type": "string",
                                "description": "File name of the second entity",
                            }
                        },
                        "required": ["entity1", "entity2"]
                    },
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "the coupling relationship between two entity",
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_co_change_relationship",
                    "description": "This function takes a target entity as a parameter, and applies data mining to the project's version history to get the recommended synchronised changes, i.e. based on the fact that ‘the programmer who modified this entity in the past also modified ....’. The function will return an array where each element is (the entity name,  the number of supports, the confidence). The explanation of the number of supports and confidence is as follows: if the target entity is A.java, in the version history of A.java has been modified 8 times, at the same time in these 8 modifications of B.java appeared 7 times, then the number of supports is 7, the confidence is 7/8 = 0.875",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "File name of the target entity",
                            }
                        },
                        "required": ["entity"]
                    },
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "description": "{the entity name,  the number of supports, the confidence}",
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_conceptual_coupling",
                    "description": "This function calculates the semantic similarity of the code of two entities through natural language processing techniques, specified by the cosine similarity, and returns the semantic similarity probability of the two entities.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity1": {
                                "type": "string",
                                "description": "File name of the first entity",
                            },
                            "entity2": {
                                "type": "string",
                                "description": "File name of the second entity",
                            }
                        },
                        "required": ["entity1", "entity2"]
                    },
                    "return": {
                        "type": "double",
                        "description": "the semantic similarity probability of the two entities",
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_origin_code",
                    "description": "This function takes one parameter: the name of the entity to be analysed, and returns the source code information for this entity as a string (Remove comment information and extra blank lines)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "the file need to analysis",
                            }
                        },
                        "required": ["entity"]
                    },
                    "return": {
                        "type": "string",
                        "items": {
                            "type": "string",
                            "description": "the source code information for this entity",
                        }
                    }
                }
            }]
        self.FUNCTION_FUNC5_DESCRIPTIONS = [
            {
                "type": "function",
                "function": {
                    "name": "get_coupling_dependencies",
                    "description": "This function takes two entities as input and returns the coupling dependencies that exist between the two entities. There are 18 types of coupling dependencies, including Inheritance(IH), Implementing Interface(II), Instanceof (IO), Return Type (RT), and Exception Throws (ET), etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity1": {
                                "type": "string",
                                "description": "File name of the first entity",
                            },
                            "entity2": {
                                "type": "string",
                                "description": "File name of the second entity",
                            }
                        },
                        "required": ["entity1", "entity2"]
                    },
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "the coupling relationship between two entity",
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_co_change_relationship",
                    "description": "This function takes a target entity as a parameter, and applies data mining to the project's version history to get the recommended synchronised changes, i.e. based on the fact that ‘the programmer who modified this entity in the past also modified ....’. The function will return an array where each element is (the entity name,  the number of supports, the confidence). The explanation of the number of supports and confidence is as follows: if the target entity is A.java, in the version history of A.java has been modified 8 times, at the same time in these 8 modifications of B.java appeared 7 times, then the number of supports is 7, the confidence is 7/8 = 0.875",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "File name of the target entity",
                            }
                        },
                        "required": ["entity"]
                    },
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "description": "{the entity name,  the number of supports, the confidence}",
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_conceptual_coupling",
                    "description": "This function calculates the semantic similarity of the code of two entities through natural language processing techniques, specified by the cosine similarity, and returns the semantic similarity probability of the two entities.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity1": {
                                "type": "string",
                                "description": "File name of the first entity",
                            },
                            "entity2": {
                                "type": "string",
                                "description": "File name of the second entity",
                            }
                        },
                        "required": ["entity1", "entity2"]
                    },
                    "return": {
                        "type": "double",
                        "description": "the semantic similarity probability of the two entities",
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_call_graph",
                    "description": "This function parses out the call information in the target entity, and if another entity is used by the target entity (either through a method call or a direct reference to a variable), then that entity is used as one of the elements of the result array.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "the file need to analysis",
                            },
                        },
                        "required": ["entity"],
                    },
                    "return": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Name of the entity to be called in the target entity",
                        },
                    },
                },
            }
        ]
        self._model = model_type

    def get_response(self, messages, func_name):
        for _ in range(5):
            try:
                if func_name == "get_coupling_dependencies":
                    completion = self._client.chat.completions.create(
                        model=self._model,
                        messages=messages,
                        tools=self.FUNCTION_FUNC1_DESCRIPTIONS
                    )
                    return completion.model_dump()
                elif func_name == "get_conceptual_coupling":
                    completion = self._client.chat.completions.create(
                        model=self._model,
                        messages=messages,
                        tools=self.FUNCTION_FUNC3_DESCRIPTIONS
                    )
                    return completion.model_dump()
                elif func_name == "get_call_graph":
                    completion = self._client.chat.completions.create(
                        model=self._model,
                        messages=messages,
                        tools=self.FUNCTION_FUNC4_DESCRIPTIONS
                    )
                    return completion.model_dump()
                elif func_name == "get_origin_code":
                    completion = self._client.chat.completions.create(
                        model=self._model,
                        messages=messages,
                        tools=self.FUNCTION_FUNC5_DESCRIPTIONS
                    )
                    return completion.model_dump()
            except Exception as e:
                save_err = e
        raise save_err