from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from langchain_community.utilities.searchapi import SearchApiAPIWrapper
from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.inputs import SecretStrInput, MultilineInput, DictInput, MessageTextInput, IntInput
from langflow.schema import Data
from langflow.field_typing import Tool
from langchain.tools import StructuredTool


class SearchAPIComponent(LCToolComponent):
    display_name: str = "Search API"
    description: str = "Call the searchapi.io API with result limiting"
    name = "SearchAPI"
    documentation: str = "https://www.searchapi.io/docs/google"

    inputs = [
        MessageTextInput(name="engine", display_name="Engine", value="google"),
        SecretStrInput(name="api_key", display_name="SearchAPI API Key", required=True),
        MultilineInput(
            name="input_value",
            display_name="Input",
        ),
        DictInput(name="search_params", display_name="Search parameters", advanced=True, is_list=True),
        IntInput(name="max_results", display_name="Max Results", value=5, advanced=True),
        IntInput(name="max_snippet_length", display_name="Max Snippet Length", value=100, advanced=True),
    ]

    class SearchAPISchema(BaseModel):
        query: str = Field(..., description="The search query")
        params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional search parameters")
        max_results: int = Field(5, description="Maximum number of results to return")
        max_snippet_length: int = Field(100, description="Maximum length of each result snippet")

    def _build_wrapper(self):
        return SearchApiAPIWrapper(engine=self.engine, searchapi_api_key=self.api_key)

    def build_tool(self) -> Tool:
        wrapper = self._build_wrapper()

        def search_func(
            query: str, params: Optional[Dict[str, Any]] = None, max_results: int = 5, max_snippet_length: int = 100
        ) -> List[Dict[str, Any]]:
            params = params or {}
            full_results = wrapper.results(query=query, **params)
            organic_results = full_results.get("organic_results", [])[:max_results]

            limited_results = []
            for result in organic_results:
                limited_result = {
                    "title": result.get("title", "")[:max_snippet_length],
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", "")[:max_snippet_length],
                }
                limited_results.append(limited_result)

            return limited_results

        tool = StructuredTool.from_function(
            name="search_api",
            description="Search for recent results using searchapi.io with result limiting",
            func=search_func,
            args_schema=self.SearchAPISchema,
        )

        self.status = f"Search API Tool created with engine: {self.engine}"
        return tool

    def run_model(self) -> List[Data]:
        tool = self.build_tool()
        results = tool.run(
            {
                "query": self.input_value,
                "params": self.search_params or {},
                "max_results": self.max_results,
                "max_snippet_length": self.max_snippet_length,
            }
        )

        data_list = [Data(data=result, text=result.get("snippet", "")) for result in results]

        self.status = data_list
        return data_list