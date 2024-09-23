from abc import abstractmethod

from langchain_core.documents import BaseDocumentTransformer
from langchain_text_splitters import TextSplitter

from langflow.base.document_transformers.model import LCDocumentTransformerComponent


class LCTextSplitterComponent(LCDocumentTransformerComponent):
    trace_type = "text_splitter"

    def _validate_outputs(self):
        required_output_methods = ["text_splitter"]
        output_names = [output.name for output in self.outputs]
        for method_name in required_output_methods:
            if method_name not in output_names:
                raise ValueError(f"Output with name '{method_name}' must be defined.")
            elif not hasattr(self, method_name):
                raise ValueError(f"Method '{method_name}' must be defined.")

    def build_document_transformer(self) -> BaseDocumentTransformer:
        return self.build_text_splitter()

    @abstractmethod
    def build_text_splitter(self) -> TextSplitter:
        """
        Build the text splitter.
        """
        pass